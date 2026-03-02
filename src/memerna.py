
import math
import os
import random
import subprocess

from .logging import LoggingClass
from . import model as M   # auto-generated code, modification strongly discouraged


class Memerna(LoggingClass):

    def __init__(self, work_dir = None):
        LoggingClass.__init__(self)
        #self.setLevelDebug()
        self._work_dir = work_dir
        self._last_Q = None
        R = 0.001987 # kcal mol-1 K-1
        T = 310  # K
        self._RT = R * T

    @property
    def work_dir(self):
        return self._work_dir

    def _parse_struct(self, line):
        fields = line.split()
        if len(fields) != 2:
            return True, None, None
        delta_fe = float(fields[0])
        paren_pairs = fields[1]
        struct = []
        open_stack = []
        for i, p in enumerate(paren_pairs):
            if p == '(':
                open_stack.append(i)
                struct.append(-1)
            elif p == ')':
                oi = open_stack.pop()
                assert struct[oi] == -1 , f"struct[oi] = {struct[oi]}"
                # note:  using 1-based indices for pairings (0 means unpaired)
                struct[oi] = i + 1
                struct.append(oi + 1)
            else:
                struct.append(0)
        assert not open_stack, f"open_stack = {open_stack}"
        probability = math.exp(-delta_fe / self._RT) / self._last_Q
        assert(0. <= probability <= 1.)
        return (False, False,
                M.Structure(skey = hash(tuple(struct)),
                            pairings = struct,
                            free_energy = delta_fe,
                            probability = probability))

    def _find_Q(self, line):
        try:
            qm = re.match("^\s*q:\s*((\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)\s*$", line)
            if qm:
                return False, True, float(qm.group(1))
        except ValueError:
            pass
        return True, False, None

    def _run_cmd(self, cmd, handle_line):
        self.debug(f"executing:  {cmd}")
        # TAI:  use cwd = self._work_dir ?
        p = subprocess.Popen(cmd.split(' '), env = os.environ, text = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        val = None
        try:
            while True:
                line = p.stdout.readline()
                if not line:
                    return val
                line = line.strip()
                if not line:
                    return val
                cont, ret, val = handle_line(line)
                if cont:
                    continue
                yield val
                if ret:
                    return val
        finally:
            p.poll()
            if p.returncode:
                raise Exception(p.stderr.read())
            p.kill()
            p = None

    def _pf_paired(self, config, rho_seq):
        if config.bias == "shape":
            def reactivity_to_dG(rho):
                # see https://doi.org/10.1073/pnas.0806929106
                # default parameters initially chosen to match RNAstructure
                dG = config.shape_slope * math.log(rho + 1.0) + config.shape_intercept
                return "{0:.2f}".format(dG)
            return " --pf-paired " + ",".join(map(reactivity_to_dG, rho_seq))
        elif config.bias == "constrained":
            # when rho is above threshold, try to prevent any pairing with a very high energy penalty
            max_dG = len(rho_seq) * 10
            def constrained_dG(rho):
                return "{0:.2f}".format(max_dG) if rho > config.constrained_c else "0.00"
            return " --pf-paired " + ",".join(map(constrained_dG, rho_seq))
        assert not config.bias  or  config.bias == "vanilla"
        return ""

    # TAI:  make energy_model and subopt_alg part of memerna-specific config
    # TAI:  pass in hasher (hash(tuple(.)) lambda) or make part of config
    def sample_gen(self, nt_seq, rho_seq, config, energy_model = "t04", subopt_alg = "iterative"):
        # TAI:  we should probably pin our repo to a specific version of memerna.
        bin_dir = os.environ.get("MRNA_DIST", "")
        data_dir = os.environ.get("MRNA_DATA")
        md_opt = f"--memerna-data {data_dir}" if data_dir else ""
        hacked_nt_seq = nt_seq.replace('T', 'U')
        pf_paired = self._pf_paired(config, rho_seq)
        base_args = f" -em {energy_model} --ctd none {md_opt} --backend base {hacked_nt_seq}{pf_paired}"

        cmd = os.path.join(bin_dir, "partition")
        cmdline = f"{cmd}{base_args}"
        self._last_Q = next(self._run_cmd(cmdline, self._find_Q))

        cmd = os.path.join(bin_dir, "subopt")
        subopt_opts = f" --subopt-alg {subopt_alg} --subopt-strucs {config.sample_size}"
        if config.no_bulge_states:
            subopt_opts += " --no-bulge-states"
        cmdline = f"{cmd}{subopt_opts}{base_args}"
        yield from self._run_cmd(cmdline, self._parse_struct)

