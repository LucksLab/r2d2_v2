
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

    @property
    def work_dir(self):
        return self._work_dir

    def _parse_struct(self, delta_fe, paren_pairs):
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
        return M.Structure(hash(tuple(struct)), struct, float(delta_fe))

    def _gen_sample(self, cmd):
        self.debug(f"executing:  {cmd}")
        # TAI:  use cwd = self._work_dir ?
        p = subprocess.Popen(cmd.split(' '), env = os.environ, text = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        try:
            while True:
                line = p.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                fields = line.split()
                if len(fields) != 2:
                    continue
                yield self._parse_struct(fields[0], fields[1])
        finally:
            p.poll()
            if p.returncode:
                raise Exception(p.stderr.read())

    # TAI:  make energy_model and alg part of memerna-specific config
    # TAI:  pass in hasher (hash(tuple(.)) lambda) or make part of config
    def sample_gen(self, nt_seq, rho_seq, config, energy_model = "t04p2full", alg = "iterative"):
        hacked_nt_seq = nt_seq.replace('T', 'U')
        bin_path = os.path.join(os.environ.get("MRNA_DIST", ""), "subopt")
        data_dir = os.environ.get("MRNA_DATA")
        # XXX:  newer versions of memerna seemed to have changed (at least the semantics of) the command line options.
        # TAI:  we should probably pin our repo to a specific version of memerna.
        md_opt = f"--memerna-data {data_dir}" if data_dir else ""
        base_cmd = f"{bin_path} --subopt-alg {alg} --energy-model {energy_model} --subopt-strucs {config.sample_size} --ctd none {md_opt} {hacked_nt_seq}"
        if config.bias == "shape":
            def reactivity_to_dG(rho):
                # see https://doi.org/10.1073/pnas.0806929106
                # default parameters initially chosen to match RNAstructure
                dG = config.shape_slope * math.log(rho + 1.0) + config.shape_intercept
                return "{0:.2f}".format(dG)
            pf_paired = " --pf-paired " + ",".join(map(reactivity_to_dG, rho_seq))
        elif config.bias == "constrained":
            # when rho is above threshold, try to prevent any pairing with a very high energy penalty
            max_dG = len(rho_seq) * 10
            def constrained_dG(rho):
                return "{0:.2f}".format(max_dG) if rho > config.constrained_c else "0.00"
            pf_paired = " --pf-paired " + ",".join(map(constrained_dG, rho_seq))
        else:
            assert not config.bias  or  config.bias == "vanilla"
            pf_paired = ""
        for s in self._gen_sample(base_cmd + pf_paired):
            yield s

