
import os
import random
import re
import subprocess
from tempfile import NamedTemporaryFile

from .logging import LoggingClass
from . import model as M   # auto-generated code, modification strongly discouraged


class RNAstructure(LoggingClass):

    def __init__(self, work_dir = None, use_smp = True):
        LoggingClass.__init__(self)
        #self.setLevelDebug()
        self._use_smp = use_smp
        self._work_dir = work_dir
        self._to_cleanup = []
        self.reset_sampling()

    @property
    def work_dir(self):
        return self._work_dir

    def _create_shapefile(self, rhos):
        SHF = NamedTemporaryFile(dir = self._work_dir, mode = "w+", suffix = ".rho")
        for i, rho in enumerate(rhos):
            SHF.write(f"{i}\t{rho}\n")
        SHF.flush()
        return SHF

    def _create_confile(self, constraints):
        CF = NamedTemporaryFile(dir = self._work_dir, mode = "w+", suffix = ".con")
        con = f" --constraint {CF.name}"
        CF.write("DS:\n-1\n")
        CF.write("SS:\n")
        for c in constraints:
            CF.write(f"{c}\n")
        CF.write("-1\n")
        CF.write("Mod:\n-1\n")
        CF.write("Pairs:\n-1 -1\n")
        CF.write("FMN:\n-1\n")
        CF.write("Forbids:\n-1 -1\n")
        CF.flush()
        return CF

    def partition(self, nt_seq, pfsfile, bias, config,
                  rhos = None, constraints = None):
        try:
            SHF, sh = None, ""
            CF, con = None, ""
            if rhos:
                SHF = self._create_shapefile(rhos)
                sh = f" -sh {SHF.name}"
            if constraints:
                CF = self._create_confile(constraints)
                con = f" --constraint {CF.name}"
            smp = "-smp" if self._use_smp else ""
            with NamedTemporaryFile(dir = self._work_dir, mode = "w+", suffix = ".fasta") as SF:
                SF.write("> partition\n")
                SF.write(f"{nt_seq}\n")
                SF.flush()
                cmd = f"partition{smp} {SF.name} {pfsfile} -si {config.shape_intercept} -sm {config.shape_slope}{sh}{con}"
                subprocess.check_call(cmd.split(' '), stdout = subprocess.DEVNULL, env = os.environ)
        finally:
            if SHF:
                SHF.close()
            if CF:
                CF.close()


    # The output .ct file can be huge, so we make this a generator.
    def stochastic(self, config, pfsfile):
        smp = "-smp" if self._use_smp else ""
        seed = random.randint(1, 100000000)
        struct = []
        # XXX: stochastic creates all samples first before writing ANY to stdout! (...and/or doesn't flush stdout)
        cmd = f"stochastic{smp} {pfsfile} - -e {config.sample_size} --seed {seed}"
        p = subprocess.Popen(cmd.split(' '), env = os.environ, text = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        try:
            while True:
                line = p.stdout.readline()
                if not line:
                    break
                if line[0] not in " \t\n":
                    continue
                line = line.strip()
                if not line:
                    continue
                fields = re.split('\s+', line)
                if len(fields) == 6:
                    struct.append(int(fields[4]))
                elif struct:
                    yield struct
                    struct = []
            if struct:
                yield struct
        finally:
            p.poll()
            if p.returncode:
                raise Exception(p.stderr.read())

    def efn2(self, struct, seg, config):
        assert len(seg) == len(struct)
        smp = "-smp" if self._use_smp else ""
        with NamedTemporaryFile(dir = self._work_dir, mode = "w+", suffix = ".ct") as CTF:
            # TODO:  rewrite efn2 so we don't need to dump struct(s) into a ctfile every time
            CTF.write(f"{len(struct)} EFNCT\n")
            for i, s in enumerate(struct):
                # indices in ct files are 1-based
                CTF.write(f"{i + 1}\t{seg[i]}\t{i}\t{i + 2}\t{s}\t{i + 1}\n")
            CTF.flush()
            cmd = f"efn2{smp} --ne {CTF.name} -"
            p = subprocess.Popen(cmd.split(' '), env = os.environ, text = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            try:
                while True:
                    line = p.stdout.readline()
                    if not line:
                        break
                    fields = line.strip().split("Energy = ")
                    if len(fields) > 1:
                        return float(fields[-1])
            finally:
                p.wait()
                if p.returncode:
                    raise Exception(p.stderr.read())
            assert False, f"bad efn2 file for seg={seg} and struct={struct}"

    def reset_sampling(self):
        self._last_seg = None
        self._last_partition = dict()
        for file in self._to_cleanup:
            if os.path.exists(file):
                os.remove(file)
        self._to_cleanup = []

    # TAI:  pass in hasher (hash(tuple(.)) lambda) or make part of config
    def sample_gen(self, nt_seq, rho_seq, config):
        all_biases = [ "shape", "constrained", "vanilla" ]
        if self._last_seg != nt_seq:
            for bias in all_biases:
                pfsfile = os.path.join(self._work_dir, f"{bias}.pfs")
                rhos = rho_seq if bias == "shape" else None
                constraints = None
                if bias == "constrained":
                    constraints = [i+1 for i, r in enumerate(rho_seq) if r > config.constrained_c]
                self.partition(nt_seq, pfsfile, bias, config,
                               rhos = rhos, constraints = constraints)
                self._last_partition[bias] = pfsfile
                self._to_cleanup.append(pfsfile)
            self._last_seg = nt_seq
        biases = all_biases
        if config.bias != "pooled":
            assert config.bias in all_biases
            biases = [ config.bias ]
        for bias in biases:
            for struct in self.stochastic(config, self._last_partition[bias]):
                yield M.Structure(hash(tuple(struct)), struct)
