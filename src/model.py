## Note:  the following code was originally auto-generated.  Modificaitons/additions here are strongly discouraged.

import base64
import sys

from .fs import fs


class SamplingConfig(object):

    def __init__(self, sample_gen = None, num_ensembles = None, sample_size = None, bias = None, shape_slope = None, shape_intercept = None, constrained_c = None, seed = None):
        self.sample_gen = sample_gen or ''  # type String
        self.num_ensembles = num_ensembles or 1  # type Integer
        self.sample_size = sample_size or 50000  # type Integer
        self.bias = bias or "shape"  # type String
        self.shape_slope = shape_slope or 1.1  # type Real
        self.shape_intercept = shape_intercept or -0.3  # type Real
        self.constrained_c = constrained_c or 3.5  # type Real
        self.seed = seed or 1234  # type Integer

    @property
    def typeName(self):
        return "SamplingConfig"

    @property
    def fsType(self):
        return fs.SamplingConfig

    def defaultDict(self):
        return {
            'sample_gen' : self.sample_gen or '',
            'num_ensembles' : self.num_ensembles or 1,
            'sample_size' : self.sample_size or 50000,
            'bias' : self.bias or "shape",
            'shape_slope' : self.shape_slope or 1.1,
            'shape_intercept' : self.shape_intercept or -0.3,
            'constrained_c' : self.constrained_c or 3.5,
            'seed' : self.seed or 1234,
        }

    def __str__(self):
        return self._description()

    def _description(self):
        return "SamplingConfig: `{}`".format(", ".join([ "{}={}".format(k, v) for k, v in self.json(skipTypes = True, limit = 1).items() ]))

    def _newObjectOfSameType(self):
        return SamplingConfig()

    def clone(self):
        c = self._newObjectOfSameType()
        if hasattr(self, 'serialize'):
            c.deserialize(self.serialize())
        else:
            c.loadFromJson(self.json())
        return c


    def loadFromJson(self, json, skipNull = False):
        if not json:
            return self
        self.sample_gen = json.get('sample_gen', '')
        self.num_ensembles = json.get('num_ensembles', 1)
        self.sample_size = json.get('sample_size', 50000)
        self.bias = json.get('bias', "shape")
        self.shape_slope = json.get('shape_slope', 1.1)
        self.shape_intercept = json.get('shape_intercept', -0.3)
        self.constrained_c = json.get('constrained_c', 3.5)
        self.seed = json.get('seed', 1234)
        return self

    def json(self, skipTypes = False, minimal = False, limit = -1):
        if limit == 0:
            return "..."
        d = { }
        if not skipTypes:
            d["type"] = self.typeName
        if ((self.sample_gen is not None) if minimal else (self.sample_gen)): d['sample_gen'] = self.sample_gen
        if ((self.num_ensembles is not None) if minimal else (self.num_ensembles)): d['num_ensembles'] = self.num_ensembles
        if ((self.sample_size is not None) if minimal else (self.sample_size)): d['sample_size'] = self.sample_size
        if ((self.bias is not None) if minimal else (self.bias)): d['bias'] = self.bias
        if ((self.shape_slope is not None) if minimal else (self.shape_slope)): d['shape_slope'] = self.shape_slope
        if ((self.shape_intercept is not None) if minimal else (self.shape_intercept)): d['shape_intercept'] = self.shape_intercept
        if ((self.constrained_c is not None) if minimal else (self.constrained_c)): d['constrained_c'] = self.constrained_c
        if ((self.seed is not None) if minimal else (self.seed)): d['seed'] = self.seed
        return d

class DistanceConfig(object):

    def __init__(self, weight_paired = None, scale_rho_max = None, cap_rhos = None, scaling_fn = None):
        self.weight_paired = weight_paired or 0.8  # type Real
        self.scale_rho_max = scale_rho_max or 1.0  # type Real
        self.cap_rhos = cap_rhos or True  # type Boolean
        self.scaling_fn = scaling_fn or 'K'  # type String

    @property
    def typeName(self):
        return "DistanceConfig"

    @property
    def fsType(self):
        return fs.DistanceConfig

    def defaultDict(self):
        return {
            'weight_paired' : self.weight_paired or 0.8,
            'scale_rho_max' : self.scale_rho_max or 1.0,
            'cap_rhos' : self.cap_rhos or True,
            'scaling_fn' : self.scaling_fn or 'K',
        }

    def __str__(self):
        return self._description()

    def _description(self):
        return "DistanceConfig: `{}`".format(", ".join([ "{}={}".format(k, v) for k, v in self.json(skipTypes = True, limit = 1).items() ]))

    def _newObjectOfSameType(self):
        return DistanceConfig()

    def clone(self):
        c = self._newObjectOfSameType()
        if hasattr(self, 'serialize'):
            c.deserialize(self.serialize())
        else:
            c.loadFromJson(self.json())
        return c


    def loadFromJson(self, json, skipNull = False):
        if not json:
            return self
        self.weight_paired = json.get('weight_paired', 0.8)
        self.scale_rho_max = json.get('scale_rho_max', 1.0)
        self.cap_rhos = json.get('cap_rhos', True)
        self.scaling_fn = json.get('scaling_fn', 'K')
        return self

    def json(self, skipTypes = False, minimal = False, limit = -1):
        if limit == 0:
            return "..."
        d = { }
        if not skipTypes:
            d["type"] = self.typeName
        if ((self.weight_paired is not None) if minimal else (self.weight_paired)): d['weight_paired'] = self.weight_paired
        if ((self.scale_rho_max is not None) if minimal else (self.scale_rho_max)): d['scale_rho_max'] = self.scale_rho_max
        if ((self.cap_rhos is not None) if minimal else (self.cap_rhos)): d['cap_rhos'] = self.cap_rhos
        if ((self.scaling_fn is not None) if minimal else (self.scaling_fn)): d['scaling_fn'] = self.scaling_fn
        return d

class FreeEnergyConfig(object):

    def __init__(self, free_energy_fn = None, report_mfe = None):
        self.free_energy_fn = free_energy_fn or ''  # type String
        self.report_mfe = report_mfe or True  # type Boolean

    @property
    def typeName(self):
        return "FreeEnergyConfig"

    @property
    def fsType(self):
        return fs.FreeEnergyConfig

    def defaultDict(self):
        return {
            'free_energy_fn' : self.free_energy_fn or '',
            'report_mfe' : self.report_mfe or True,
        }

    def __str__(self):
        return self._description()

    def _description(self):
        return "FreeEnergyConfig: `{}`".format(", ".join([ "{}={}".format(k, v) for k, v in self.json(skipTypes = True, limit = 1).items() ]))

    def _newObjectOfSameType(self):
        return FreeEnergyConfig()

    def clone(self):
        c = self._newObjectOfSameType()
        if hasattr(self, 'serialize'):
            c.deserialize(self.serialize())
        else:
            c.loadFromJson(self.json())
        return c


    def loadFromJson(self, json, skipNull = False):
        if not json:
            return self
        self.free_energy_fn = json.get('free_energy_fn', '')
        self.report_mfe = json.get('report_mfe', True)
        return self

    def json(self, skipTypes = False, minimal = False, limit = -1):
        if limit == 0:
            return "..."
        d = { }
        if not skipTypes:
            d["type"] = self.typeName
        if ((self.free_energy_fn is not None) if minimal else (self.free_energy_fn)): d['free_energy_fn'] = self.free_energy_fn
        if ((self.report_mfe is not None) if minimal else (self.report_mfe)): d['report_mfe'] = self.report_mfe
        return d

class EnvVar(object):

    def __init__(self, variable = None, value = None, replace_existing = None):
        self.variable = variable or ''  # type String
        self.value = value or ''  # type String
        self.replace_existing = replace_existing or False  # type Boolean

    @property
    def typeName(self):
        return "EnvVar"

    @property
    def fsType(self):
        return fs.EnvVar

    def defaultDict(self):
        return {
            'variable' : self.variable or '',
            'value' : self.value or '',
            'replace_existing' : self.replace_existing or False,
        }

    def __str__(self):
        return self._description()

    def _description(self):
        return "EnvVar: `{}`".format(", ".join([ "{}={}".format(k, v) for k, v in self.json(skipTypes = True, limit = 1).items() ]))

    def _newObjectOfSameType(self):
        return EnvVar()

    def clone(self):
        c = self._newObjectOfSameType()
        if hasattr(self, 'serialize'):
            c.deserialize(self.serialize())
        else:
            c.loadFromJson(self.json())
        return c


    def loadFromJson(self, json, skipNull = False):
        if not json:
            return self
        self.variable = json.get('variable', '')
        self.value = json.get('value', '')
        self.replace_existing = json.get('replace_existing', False)
        return self

    def json(self, skipTypes = False, minimal = False, limit = -1):
        if limit == 0:
            return "..."
        d = { }
        if not skipTypes:
            d["type"] = self.typeName
        if ((self.variable is not None) if minimal else (self.variable)): d['variable'] = self.variable
        if ((self.value is not None) if minimal else (self.value)): d['value'] = self.value
        if ((self.replace_existing is not None) if minimal else (self.replace_existing)): d['replace_existing'] = self.replace_existing
        return d

class R2D2Config(object):

    def __init__(self, run_name = None, base_path = None, reactivity_file = None, save_ensembles = None, env_vars = None, sampling_config = None, free_energy_config = None, distance_config = None):
        self.run_name = run_name or ''  # type String
        self.base_path = base_path or ''  # type String
        self.reactivity_file = reactivity_file or ''  # type String
        self.save_ensembles = save_ensembles or False  # type Boolean
        self.env_vars = env_vars or []  # type [EnvVar]
        self.sampling_config = sampling_config or None  # type SamplingConfig
        self.free_energy_config = free_energy_config or None  # type FreeEnergyConfig
        self.distance_config = distance_config or None  # type DistanceConfig

    @property
    def typeName(self):
        return "R2D2Config"

    @property
    def fsType(self):
        return fs.R2D2Config

    def defaultDict(self):
        return {
            'run_name' : self.run_name or '',
            'base_path' : self.base_path or '',
            'reactivity_file' : self.reactivity_file or '',
            'save_ensembles' : self.save_ensembles or False,
            'env_vars' : self.env_vars or [],
            'sampling_config' : self.sampling_config or None,
            'free_energy_config' : self.free_energy_config or None,
            'distance_config' : self.distance_config or None,
        }

    def __str__(self):
        return self._description()

    def _description(self):
        return "R2D2Config: `{}`".format(", ".join([ "{}={}".format(k, v) for k, v in self.json(skipTypes = True, limit = 1).items() ]))

    def _newObjectOfSameType(self):
        return R2D2Config()

    def clone(self):
        c = self._newObjectOfSameType()
        if hasattr(self, 'serialize'):
            c.deserialize(self.serialize())
        else:
            c.loadFromJson(self.json())
        return c


    def loadFromJson(self, json, skipNull = False):
        if not json:
            return self
        self.run_name = json.get('run_name', '')
        self.base_path = json.get('base_path', '')
        self.reactivity_file = json.get('reactivity_file', '')
        self.save_ensembles = json.get('save_ensembles', False)
        self.env_vars = [ EnvVar().loadFromJson(x, skipNull = skipNull) for x in json.get('env_vars') or [] ]
        self.sampling_config = SamplingConfig().loadFromJson(json.get('sampling_config'), skipNull = skipNull) if ((not skipNull) or json.get('sampling_config')) else None
        self.free_energy_config = FreeEnergyConfig().loadFromJson(json.get('free_energy_config'), skipNull = skipNull) if ((not skipNull) or json.get('free_energy_config')) else None
        self.distance_config = DistanceConfig().loadFromJson(json.get('distance_config'), skipNull = skipNull) if ((not skipNull) or json.get('distance_config')) else None
        return self

    def json(self, skipTypes = False, minimal = False, limit = -1):
        if limit == 0:
            return "..."
        d = { }
        if not skipTypes:
            d["type"] = self.typeName
        if ((self.run_name is not None) if minimal else (self.run_name)): d['run_name'] = self.run_name
        if ((self.base_path is not None) if minimal else (self.base_path)): d['base_path'] = self.base_path
        if ((self.reactivity_file is not None) if minimal else (self.reactivity_file)): d['reactivity_file'] = self.reactivity_file
        if ((self.save_ensembles is not None) if minimal else (self.save_ensembles)): d['save_ensembles'] = self.save_ensembles
        if ((self.env_vars is not None) if minimal else (self.env_vars)): d['env_vars'] = [ x.json(skipTypes = skipTypes, minimal = minimal, limit = limit - 1) for x in self.env_vars ]
        if ((self.sampling_config is not None) if minimal else (self.sampling_config)): d['sampling_config'] = self.sampling_config.json(skipTypes = skipTypes, minimal = minimal, limit = limit - 1) if hasattr(self.sampling_config, 'json') else id(self.sampling_config)
        if ((self.free_energy_config is not None) if minimal else (self.free_energy_config)): d['free_energy_config'] = self.free_energy_config.json(skipTypes = skipTypes, minimal = minimal, limit = limit - 1) if hasattr(self.free_energy_config, 'json') else id(self.free_energy_config)
        if ((self.distance_config is not None) if minimal else (self.distance_config)): d['distance_config'] = self.distance_config.json(skipTypes = skipTypes, minimal = minimal, limit = limit - 1) if hasattr(self.distance_config, 'json') else id(self.distance_config)
        return d

class Structure(object):

    def __init__(self, skey = None, pairings = None, free_energy = None, rho_dist = None):
        self.skey = skey or 0  # type Integer
        self.pairings = pairings or []  # type [Integer]
        self.free_energy = free_energy or 0.0  # type Real
        self.rho_dist = rho_dist or -1  # type Real

    @property
    def typeName(self):
        return "Structure"

    @property
    def fsType(self):
        return fs.Structure

    def defaultDict(self):
        return {
            'skey' : self.skey or 0,
            'pairings' : self.pairings or [],
            'free_energy' : self.free_energy or 0.0,
            'rho_dist' : self.rho_dist or -1,
        }

    def __str__(self):
        return self._description()

    def _description(self):
        return "Structure: `{}`".format(", ".join([ "{}={}".format(k, v) for k, v in self.json(skipTypes = True, limit = 1).items() ]))

    def _newObjectOfSameType(self):
        return Structure()

    def clone(self):
        c = self._newObjectOfSameType()
        if hasattr(self, 'serialize'):
            c.deserialize(self.serialize())
        else:
            c.loadFromJson(self.json())
        return c


    def loadFromJson(self, json, skipNull = False):
        if not json:
            return self
        self.skey = json.get('skey', 0)
        self.pairings = list(json.get('pairings', []))
        self.free_energy = json.get('free_energy', 0.0)
        self.rho_dist = json.get('rho_dist', -1)
        return self

    def json(self, skipTypes = False, minimal = False, limit = -1):
        if limit == 0:
            return "..."
        d = { }
        if not skipTypes:
            d["type"] = self.typeName
        if ((self.skey is not None) if minimal else (self.skey)): d['skey'] = self.skey
        if ((self.pairings is not None) if minimal else (self.pairings)): d['pairings'] = self.pairings
        if ((self.free_energy is not None) if minimal else (self.free_energy)): d['free_energy'] = self.free_energy
        if ((self.rho_dist is not None) if minimal else (self.rho_dist)): d['rho_dist'] = self.rho_dist
        return d

class Ensemble(object):

    def __init__(self, best_struct = None, mean_rho_dist = None, structs = None):
        self.best_struct = best_struct or None  # type Structure
        self.mean_rho_dist = mean_rho_dist or 0.0  # type Real
        self.structs = structs or []  # type [Structure]

    @property
    def typeName(self):
        return "Ensemble"

    @property
    def fsType(self):
        return fs.Ensemble

    def defaultDict(self):
        return {
            'best_struct' : self.best_struct or None,
            'mean_rho_dist' : self.mean_rho_dist or 0.0,
            'structs' : self.structs or [],
        }

    def __str__(self):
        return self._description()

    def _description(self):
        return "Ensemble: `{}`".format(", ".join([ "{}={}".format(k, v) for k, v in self.json(skipTypes = True, limit = 1).items() ]))

    def _newObjectOfSameType(self):
        return Ensemble()

    def clone(self):
        c = self._newObjectOfSameType()
        if hasattr(self, 'serialize'):
            c.deserialize(self.serialize())
        else:
            c.loadFromJson(self.json())
        return c


    def loadFromJson(self, json, skipNull = False):
        if not json:
            return self
        self.best_struct = Structure().loadFromJson(json.get('best_struct'), skipNull = skipNull) if ((not skipNull) or json.get('best_struct')) else None
        self.mean_rho_dist = json.get('mean_rho_dist', 0.0)
        self.structs = [ Structure().loadFromJson(x, skipNull = skipNull) for x in json.get('structs') or [] ]
        return self

    def json(self, skipTypes = False, minimal = False, limit = -1):
        if limit == 0:
            return "..."
        d = { }
        if not skipTypes:
            d["type"] = self.typeName
        if ((self.best_struct is not None) if minimal else (self.best_struct)): d['best_struct'] = self.best_struct.json(skipTypes = skipTypes, minimal = minimal, limit = limit - 1) if hasattr(self.best_struct, 'json') else id(self.best_struct)
        if ((self.mean_rho_dist is not None) if minimal else (self.mean_rho_dist)): d['mean_rho_dist'] = self.mean_rho_dist
        if ((self.structs is not None) if minimal else (self.structs)): d['structs'] = [ x.json(skipTypes = skipTypes, minimal = minimal, limit = limit - 1) for x in self.structs ]
        return d

class LengthResult(object):

    def __init__(self, nt_seg = None, ensembles = None, mfe_struct = None, max_free_energy = None):
        self.nt_seg = nt_seg or ''  # type String
        self.ensembles = ensembles or []  # type [Ensemble]
        self.mfe_struct = mfe_struct or None  # type Structure
        self.max_free_energy = max_free_energy or 0.0  # type Real

    @property
    def typeName(self):
        return "LengthResult"

    @property
    def fsType(self):
        return fs.LengthResult

    def defaultDict(self):
        return {
            'nt_seg' : self.nt_seg or '',
            'ensembles' : self.ensembles or [],
            'mfe_struct' : self.mfe_struct or None,
            'max_free_energy' : self.max_free_energy or 0.0,
        }

    def __str__(self):
        return self._description()

    def _description(self):
        return "LengthResult: `{}`".format(", ".join([ "{}={}".format(k, v) for k, v in self.json(skipTypes = True, limit = 1).items() ]))

    def _newObjectOfSameType(self):
        return LengthResult()

    def clone(self):
        c = self._newObjectOfSameType()
        if hasattr(self, 'serialize'):
            c.deserialize(self.serialize())
        else:
            c.loadFromJson(self.json())
        return c


    def loadFromJson(self, json, skipNull = False):
        if not json:
            return self
        self.nt_seg = json.get('nt_seg', '')
        self.ensembles = [ Ensemble().loadFromJson(x, skipNull = skipNull) for x in json.get('ensembles') or [] ]
        self.mfe_struct = Structure().loadFromJson(json.get('mfe_struct'), skipNull = skipNull) if ((not skipNull) or json.get('mfe_struct')) else None
        self.max_free_energy = json.get('max_free_energy', 0.0)
        return self

    def json(self, skipTypes = False, minimal = False, limit = -1):
        if limit == 0:
            return "..."
        d = { }
        if not skipTypes:
            d["type"] = self.typeName
        if ((self.nt_seg is not None) if minimal else (self.nt_seg)): d['nt_seg'] = self.nt_seg
        if ((self.ensembles is not None) if minimal else (self.ensembles)): d['ensembles'] = [ x.json(skipTypes = skipTypes, minimal = minimal, limit = limit - 1) for x in self.ensembles ]
        if ((self.mfe_struct is not None) if minimal else (self.mfe_struct)): d['mfe_struct'] = self.mfe_struct.json(skipTypes = skipTypes, minimal = minimal, limit = limit - 1) if hasattr(self.mfe_struct, 'json') else id(self.mfe_struct)
        if ((self.max_free_energy is not None) if minimal else (self.max_free_energy)): d['max_free_energy'] = self.max_free_energy
        return d


def newObjectOfType(type):
    return globals()[type]()

_g_fsMap = {
    fs.SamplingConfig : SamplingConfig,
    fs.DistanceConfig : DistanceConfig,
    fs.FreeEnergyConfig : FreeEnergyConfig,
    fs.EnvVar : EnvVar,
    fs.R2D2Config : R2D2Config,
    fs.Structure : Structure,
    fs.Ensemble : Ensemble,
    fs.LengthResult : LengthResult,
}

def newObjectOfFixedStringType(type):
    return _g_fsMap[type]()

def hasObjectOfFixedStringType(type):
    return type in _g_fsMap

def objectFromJson(j):
    return newObjectOfType(j['type']).loadFromJson(j)
