import os
import re
import multiprocessing as mp
import random
import time

from .logging import LoggingClass
from .util import ensure_folder_exists, json_at_path, write_json_to_path
from . import model as M   # auto-generated code, modification strongly discouraged


# Notes:
# - spats v1/v2 and R2D2 v1 both use python 2.7, but R2D2 v2 uses python 3.*.
#   spats v3 should be done in python 3.*.
# - both MemeRna and RNAstructure require some specific environment variables to be set first before running this.

class R2D2(LoggingClass):

    def __init__(self, base_path = None, config_path = None, run_now = True):
        LoggingClass.__init__(self)
        self._config = None
        self._base_path = base_path or os.path.abspath(".")
        config_json = json_at_path(config_path or os.path.join(self._base_path, "r2d2.json"))
        self._load_config(config_json)
        if run_now:
            self.run()

    @property
    def config(self):
        return self._config

    def _load_config(self, config_json):
        self._config = M.R2D2Config().loadFromJson(config_json)
        self._config.json = config_json   # in case there are custom fields within the json too
        assert self._config.run_name, f"run_name field is required in config json:  {config_json}"
        self._config.base_path = self._config.base_path or "."
        for ev in self._config.env_vars:
            os.environ[ev.variable] = ev.value if ev.replace_existing else ":".join([os.environ.get(ev.variable, ""), ev.value])
        assert self._config.sampling_config.num_ensembles > 0
        assert self._config.sampling_config.sample_size > 0
        assert self._config.distance_config.scaling_fn in ('D', 'U', 'K')
        random.seed(self._config.sampling_config.seed)

    def _get_field_ind(self, fields, name, name2 = None):
        try:
            return fields.index(name)
        except ValueError:
            if name2:
                try:
                    return self._get_field_ind(fields, name2)
                except:
                    pass
            self.error(f"invalid spats run file at {self._config.reactivity_file}:  '{name}' column not found")
            raise

    def parse_reactivity(self):
        nt_seqs = dict()       # length -> nt sequence (string)
        rho_seqs = dict()      # length -> rho sequence
        thetas = dict()
        with open(self._config.reactivity_file, 'r') as SRF:
            header = SRF.readline()
            fields = re.split(",|\s+", header)
            nt_ind = self._get_field_ind(fields, "nt", "nucleotide")
            l_ind = self._get_field_ind(fields, "L", "rt_start")
            # XXX: 'r' field in old spats files has different semantics than new spats files.
            # XXX: If there was an adapter/linker/endcut in the experiment which wasn't stripped
            # XXX: in the old results file, then things will be incorrect.  In that case, we need
            # XXX: to (re)calculate the rho values.
            try:
                theta_ind = -1
                reactivity_ind = self._get_field_ind(fields, "rho", "r")
            except ValueError:
                self.info(f"assuming old SPATS output, computing rhos from thetas (with endcut={self._config.endcut})")
                reactivity_ind = -1
                theta_ind = self._get_field_ind(fields, "theta")

            for line in SRF:
                fields = re.split(",|\s+", line)
                nt = fields[nt_ind]
                if nt == '*':
                    continue
                l = int(fields[l_ind])
                nt_seqs[l] = nt_seqs.get(l, "") + nt.upper()
                if reactivity_ind >= 0:
                    rho = float(fields[reactivity_ind])
                else:
                    theta = float(fields[theta_ind])
                    if self._config.endcut > 0:
                        thetas.setdefault(l, []).append(theta)
                    rho = l * theta
                rho_seqs.setdefault(l, []).append(rho)

            if self._config.endcut > 0:
                cut_nt_seqs = dict()
                cut_rho_seqs = dict()
                for l in nt_seqs.keys():
                    self.debug(f"cutting {self._config.endcut} nts for length={l}")
                    newl = len(nt_seqs[l]) - self._config.endcut
                    if newl <= 0:
                        self.warn(f"cut away entire sequence for length={l} with endcut = {self._config.endcut}")
                        continue
                    cut_nt_seqs[newl] = nt_seqs[l][:-self._config.endcut]
                    cut_rho_seqs[newl] = rho_seqs[l][:-self._config.endcut]
                    if reactivity_ind < 0:
                        self.info(f"recalculating rhos for old SPATS output for cut length={newl}")
                        cut_thetas = thetas[l][:-self._config.endcut]
                        theta_sum = sum(cut_thetas)
                        if theta_sum == 0:
                            theta_sum = 1    # just in case
                        cut_rho_seqs[newl] = [ newl * (t / theta_sum) for t in cut_thetas ]
                nt_seqs = cut_nt_seqs
                rho_seqs = cut_rho_seqs

        return nt_seqs, rho_seqs

    def _do_pool_work(self, seg):
        return seg[0], _R2D2Worker(self._config, self._run_dir, True).find_best_structs(seg[1], seg[2])

    def run(self, run_dir_suffix = "", nt_seqs = None, rho_seqs = None):
        key = f"{self._config.run_name}{run_dir_suffix}"
        self._run_dir = os.path.join(self._base_path, f"r2d2_{key}")
        ensure_folder_exists(self._run_dir)
        out_dir = os.path.join(self._run_dir, "results")
        ensure_folder_exists(out_dir)
        pool_size = max(os.cpu_count() - 1, 1)

        # note: we don't use time.process_time_ns() since we'll have
        # subprocesses and a multiprocessing pool (either here or in the worker).
        # further, we really do care about how long this takes for the *user*,
        # independent of how much processing time it may use on various CPUs.
        start_time = time.perf_counter_ns()

        if self._config.reactivity_file:
            nt_seqs, rho_seqs = self.parse_reactivity()
        if not nt_seqs or not rho_seqs:
            self.error("missing nt sequence or reactivities")
            return False
        lengths = sorted(nt_seqs.keys())

        if  len(lengths) == 1  or  pool_size == 1:
            worker = _R2D2Worker(self._config, self._run_dir, False)
            for l in lengths:
                results = worker.find_best_structs(nt_seqs[l], rho_seqs[l])
                self._write_results(results, l, out_dir)
        else:
            self.activity(f"spawning {pool_size} length workers")
            mp_ctx = mp.get_context('spawn')
            with mp_ctx.Pool(pool_size) as pool:
                for results in pool.imap_unordered(self._do_pool_work, ((l, nt_seqs[l], rho_seqs[l]) for l in lengths)):
                    self._write_results(results[1], results[0], out_dir)

        run_time = time.perf_counter_ns() - start_time
        time_out = os.path.join(out_dir, "run_time_ns")
        with open(time_out, 'w') as OTF:
            OTF.write(f"{run_time}\n")
        return True

    def _results_to_ctfile(self, results, ct_path):
        def write_struct(name_base, s, nt_seg):
            assert len(nt_seg) == len(s.pairings)
            name = f"{name_base}:DG={round(s.free_energy,4)}:RD={round(s.rho_dist,4)}"
            CTF.write(f"{len(nt_seg)} {name}\n")
            for i, p in enumerate(s.pairings):
                # indices in ct files are 1-based
                CTF.write(f"{i + 1}\t{nt_seg[i]}\t{i}\t{i + 2}\t{p}\t{i + 1}\n")
        with open(ct_path, 'w') as CTF:
            if self._config.free_energy_config.report_mfe:
                write_struct(f"MFE", results.mfe_struct, results.nt_seg)
            for i, ens in enumerate(results.ensembles):
                write_struct(f"ensemble{i}", ens.best_struct, results.nt_seg)

    def _write_results(self, results, length, out_dir):
        out_path = os.path.join(out_dir, f"len{length}")
        json = results.json()
        if self._config.save_ensembles:
            import pickle
            rdf = f"{out_path}.pkl"
            with open(rdf, "wb") as TMPP:
                pickle.dump(json['ensembles'], TMPP)
            self.activity(f"saved all ensembles w/ structs to {rdf}")
            for e in json['ensembles']:
                e['structs'] = {}    # don't write json below for all struct in ensemble too!
        write_json_to_path(json, f"{out_path}.json", pretty = True)
        self._results_to_ctfile(results, f"{out_path}.ct")
        # TAI:  also write the config options used to out_dir for future ref?
        self.activity(f"wrote results to {out_path}.json and {out_path}.ct")



class _R2D2Worker(LoggingClass):

    def __init__(self, config, work_dir, in_pool):
        LoggingClass.__init__(self)
        #self.setLevelDebug()
        self._RNAstructure = None
        self._memerna = None
        self._config = config
        self._work_dir = work_dir
        self._in_pool = in_pool
        if in_pool:
            self._work_dir = os.path.join(self._work_dir, str(os.getpid()))
        ensure_folder_exists(self._work_dir)
        sample_gen = self._config.sampling_config.sample_gen
        if sample_gen.lower() == "rnastructure":
            self._sample_gen = self._find_fn("self.RNAstructure.sample_gen", "sample_gen")
        else:
            assert(not sample_gen or sample_gen.lower() == "memerna")
            self._sample_gen = self._find_fn("self.memerna.sample_gen", "sample_gen")
        free_energy_fn = self._config.free_energy_config.free_energy_fn
        if free_energy_fn.lower() == "rnastructure":
            self._free_energy_fn = self._find_fn("self.RNAstructure.efn2", "free_energy_fn")
        else:
            assert(not free_energy_fn or free_energy_fn.lower() == "memerna")
            self._free_energy_fn = self._find_fn("self.memerna.efn", "free_energy_fn")

    @property
    def RNAstructure(self):
        if not self._RNAstructure:
            from .RNAstructure import RNAstructure
            self._RNAstructure = RNAstructure(self._work_dir, use_smp = not self._in_pool)
        return self._RNAstructure

    @property
    def memerna(self):
        if not self._memerna:
            from .memerna import Memerna
            self._memerna = Memerna(self._work_dir)
        return self._memerna

    def _find_fn(self, fn_str, key):
        parts = fn_str.split('.')
        try:
            fn = self if parts[0] == 'self' else globals()[parts[0]]
            for i in range(1, len(parts)):
                fn = getattr(fn, parts[i])
            return fn
        except:
            self.warn(f"possible config issue?  unable to find function '{fn_str}' for {key}")
        return None

    def _sample_unique_structs(self, nt_seg, rho_seg):
        seen = set()  # note:  not using struct_cache for this b/c this could be in a pool
        for s in self._sample_gen(nt_seg, rho_seg, self._config.sampling_config):
            if s.skey not in seen:
                seen.add(s.skey)
                yield s
        self.debug(f"found {len(seen)} unique structs (l={len(nt_seg)})")

    @staticmethod
    def cap_vec(vec, max_v):
        return [max_v if v > max_v else v for v in vec]

    @staticmethod
    def scale_vec_avg1(vec, max_r = None):
        """Scales a vector such that the vector's mean is 1."""
        avg_v = sum(vec) / len(vec)
        return [r / avg_v for r in arr] if avg_v else [1.0] * len(vec)

    def _scale_rhos(self, rho_seg):
        dcfg = self._config.distance_config
        v = self.cap_vec(rho_seg, dcfg.scale_rho_max) if dcfg.cap_rhos else rho_seg
        if dcfg.scaling_fn == 'D':
            max_rho = max(v)
            return [0 if r >= max_rho else (1 - r / max_rho) for r in v]
        elif dcfg.scaling_fn == 'U':
            # note: in R2D2 v1, cap_vec() was applied *before* scaling,
            # so that's what we did here too, but it may make more sense
            # to apply it *after* scaling.
            return self.scale_vec_avg1(v)
        elif dcfg.scaling_fn == 'K':
            return v
        assert False, f"unknown scaling_fn: {dcfg.scaling_fn}"

    def _scale_struct(self, struct):
        dcfg = self._config.distance_config
        smax = dcfg.scale_rho_max if (dcfg.cap_rhos and dcfg.scale_rho_max < 1.0) else 1.0
        o, z = (smax, 0.0) if dcfg.scaling_fn == 'D' else (0.0, smax)
        binary_struct = [o if s > 0 else z for s in struct]
        if dcfg.scaling_fn == 'U':
            binary_struct = self.scale_vec_avg1(binary_struct)
        return binary_struct

    def _distance(self, rho_seg, struct, nt_seg):
        assert len(rho_seg) == len(struct)
        # rhos have already been scaled, so just need to do struct
        ss = self._scale_struct(struct)
        wp = self._config.distance_config.weight_paired
        bases = self._config.distance_config.bases.upper()
        dp = du = 0
        for i,s in enumerate(struct):
            if bases and nt_seg[i] not in bases:  # TAI:  if too slow, could pre-compute these indices (or the inverse)
                continue
            if s != 0:
                dp += abs(ss[i] - rho_seg[i])
            else:
                du += abs(ss[i] - rho_seg[i])
        return wp * dp + (1 - wp) * du

    def _do_struct(self, sample):
        struct, nt_seg, scaled_rho_seg = sample
        if struct.rho_dist >= 0.0:
            return struct, False
        if self._config.free_energy_config.report_mfe  and  self._free_energy_fn:
            struct.free_energy = self._free_energy_fn(struct.pairings, nt_seg, self._config.free_energy_config)
        struct.rho_dist = self._distance(scaled_rho_seg, struct.pairings, nt_seg)
        assert struct.rho_dist >= 0.0
        return struct, True

    def _caching_sample_gen(self, struct_cache, nt_seg, rho_seg, scaled_rho_seg):
        pool_size = max(os.cpu_count() - 1, 1)
        # note:  if saving structures in the ensemble, want them to be in the order for now, so can't pool in that case.
        if not self._in_pool  and  pool_size > 1  and  not self._config.save_ensembles:
            def sample_getter():
                for s in self._sample_unique_structs(nt_seg, rho_seg):
                    struct = struct_cache.get(s.skey, s)
                    yield struct, nt_seg, scaled_rho_seg
            self.activity(f"spawning {pool_size} free-energy workers")
            mp_ctx = mp.get_context('spawn')
            with mp_ctx.Pool(pool_size) as pool:
                for struct, new in pool.imap_unordered(self._do_struct, sample_getter()):
                    yield struct, new
        else:
            for s in self._sample_unique_structs(nt_seg, rho_seg):
                struct = struct_cache.get(s.skey, s)
                yield self._do_struct((struct, nt_seg, scaled_rho_seg))

    def find_best_structs(self, nt_seg, rho_seg):
        self.activity(f"finding length {len(nt_seg)} structs...")
        scaled_rho_seg = self._scale_rhos(rho_seg)
        struct_cache = dict()   # note:  cache is across all ensembles
        results = M.LengthResult(nt_seg)
        length = len(nt_seg)
        for t in range(self._config.sampling_config.num_ensembles):
            self.debug(f"sampling for ensemble #{t} (l={length})...")
            ensemble = M.Ensemble()
            structs_in_ensemble = 0
            for struct, news in self._caching_sample_gen(struct_cache, nt_seg, rho_seg, scaled_rho_seg):
                assert struct.skey
                if news:
                    struct_cache[struct.skey] = struct
                    # This is a new (unseen) struct across all ensembles.
                    # We keep track of max/min free energy for a length across all ensembles at a length only.
                    if self._config.free_energy_config.report_mfe:
                        if (not results.mfe_struct) or (struct.free_energy < results.mfe_struct.free_energy):
                            results.mfe_struct = struct
                        if (results.max_free_energy is None) or (struct.free_energy > results.max_free_energy):
                            results.max_free_energy = struct.free_energy
                if self._config.save_ensembles:
                    ensemble.structs.append(struct)
                ensemble.mean_rho_dist += struct.rho_dist
                structs_in_ensemble += 1
                if (not ensemble.best_struct) or (struct.rho_dist < ensemble.best_struct.rho_dist):
                    ensemble.best_struct = struct
                elif struct.rho_dist == ensemble.best_struct.rho_dist:
                    if not self._config.free_energy_config.report_mfe  and  self._free_energy_fn:
                        # we didn't calculcate this earlier, so we do it now...
                        struct.free_energy = self._free_energy_fn(struct.pairings, nt_seg, self._config.free_energy_config)
                    if struct.free_energy < ensemble.best_struct.free_energy:
                        ensemble.best_struct = struct
            assert ensemble.best_struct
            ensemble.mean_rho_dist /= structs_in_ensemble
            results.ensembles.append(ensemble)
            if self._config.free_energy_config.report_mfe:
                self.debug(f"best free energy for ensemble #{t} (l={length}): {ensemble.best_struct.free_energy}  (MFE so far: {results.mfe_struct.free_energy})")
        if self._RNAstructure:
            self._RNAstructure.reset_sampling()
        self.info(f"found {len(results.ensembles)} best structs of length {length}.")
        return results

