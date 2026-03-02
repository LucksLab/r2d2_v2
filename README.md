
# R2D2 Version 2

R2D2 stands for "Reconstructing RNA Dynamics from Data".
This is a rewrite of the original R2D2 code (which is [here](https://github.com/LucksLab/R2D2)) to slightly
simplify it, use the updated [SPATS tool](https://github.com/LucksLab/spats) file formats for reactivity inputs,
and add the ability to use/compare different RNA folding tools
([RNAstructure](https://rna.urmc.rochester.edu/RNAstructure.html) and [MemeRNA](https://github.com/Edgeworth/memerna), in particular).


## Environment Notes

- Spats v1/v2 and R2D2 v1 both use Python 2.7, but R2D2 v2 uses Python 3;
    - It is expected that Spats v3 will be done in Python 3 and potentially be more tightly integrated with R2D2.
- Both MemeRNA and RNAstructure require some specific environment variables to be set first before running R2D2.  [TODO]


## Configuration

R2D2 v2 uses a JSON input file for configuration.  An example `r2d2.json` file looks like:
```json
{
    "run_name": "119nt_memerna_eq_shape2",
    "reactivity_file":  "~/SRP_data/SRP_EQ/SRP_IDT2_mod_119nt_138_reactivities.txt",
    "endcut": 18,
    "save_ensembles": true,
    "free_energy_config": { "report_mfe": true },
    "sampling_config": { "sample_gen": "Memerna", "bias": "shape", "shape_slope": 3.5, "shape_intercept": -0.9 }
}
```

There are various options, many of which are optional (i.e., have default values), including:

### R2D2Config

The main configuration object.

| Key | Type | Default Value | Description |
| --- | ---- | ------------- | ----------- |
| `run_name` | String |     | name/tag to use to label R2D2 run outputs |
| `base_path` | String | "." | folder into which to put working and results files |
| `reactivity_file` | String | "`{run_name}.csv`" | `spats_tool` run output file |
| `save_ensembles` | Boolean | `false` | if `true`, save the entire ensemble |
| `endcut` | Integer | 0 | number of nucleotides to be removed from the 3' end (for adapters, linkers, primers, etc.); if positive, and if reactivities file is from an old spats run, theta/rho values will be re-calculated based on post-cut length |
| `sampling_config` | JSON object | | see [SamplingConfig](#SamplingConfig) |
| `free_energy_config` | JSON object | | see [FreeEnergyConfig](#FreeEnergyConfig) |
| `distance_config` | JSON object | | see [DistanceConfig](#DistanceConfig) |
| `env_vars` | JSON array of objects | | see [[EnvVar](#EnvVar)] |


### SamplingConfig

Configuration for how RNA structures ("samples") will be generated.

| Key | Type | Default Value | Description |
| --- | ---- | ------------- | ----------- |
| `sample_gen` | String | "MemeRNA" | either "RNAstructure" or "MemeRNA". generator to produce samples (defaults to use MemeRNA's subopt tool) |
| `num_ensembles` | Integer | 1 | number of structures to find at each length |
| `sample_size` | Integer | 50000 | number of samples to search through in an ensemble per method |
| `bias` | String | "shape" | options are:  "shape", "vanilla", "constrained", or "pooled" (which only works for RNAstructure sampling) |
| `shape_slope` | Real | 1.1 | Slope used to convert SHAPE reactivities to `pf` energy biases:  `pf = m * ln[rho] + b` |
| `shape_intercept` | Real | -0.3 | Intercept used to convert SHAPE reactivities to `pf` energy biases:  `pf = m * ln[rho] + b` |
| `constrained_c` | Real | 3.5 | Any rho value greater than or equal to this value will be forced as unpaired when sampling with hard constraints |
| `seed` | Integer | 1234 | pseudorandom numbers seed |
| `no_bulge_states` | Boolean | `true` | when `true`, disable bulge loop states computation |


### FreeEnergyConfig

Configuration options for how the Free Energy of a structure will be calculated.

| Key | Type | Default Value | Description |
| --- | ---- | ------------- | ----------- |
| `free_energy_fn` | String | "MemeRNA" | either "RNAstructure" or "MemeRNA" (defaults to use MemeRNA's efn or subopt tool) |
| `report_mfe` | Boolean  | `true` | if `true`, report the MFE struct in addition to the "best" struct; `false` saves time by not running efn or efn2 for every struct |


### DistanceConfig

Configuration for how the "distance" between an RNA structure and a reactivity (rho) vector will be defined/computed.

| Key | Type | Default Value | Description |
| --- | ---- | ------------- | ----------- |
| `weight_paired` | Real | 0.8 | Weight given to paired regions in distance calculations |
| `scale_rho_max` | Real | 1.0 | If `cap_rhos` is `true` or the "D" distance is used, this value is the max value and all values greater than it are set to this max value |
| `cap_rhos` | Boolean | `true` | Flag to use `scale_rho_max` as a cutoff for reactivities when calculating distances for choosing the best structure |
| `scaling_fn` | String | "K" | Scaling to use when choosing the best structure: <ul><li>D: Bound reactivity to be between `[0,1]`</li><li>U: Rescale sampled structures to average to `1`</li><li>K: Keep sampled structures and reactivities values. If `cap_rhos` is `true`, then reactivities will be capped.</li></ul> |
| `bases` | String | (all) | Bases for which to compute distance (e.g., "AC" would just compute distances at nucleotides with Adenine and Cytosine bases) |


### EnvVar

Environment variables to set. (Deprecated - should not be needed.)

| Key | Type | Default Value | Description |
| --- | ---- | ------------- | ----------- |
| `variable` |String | | name of an environment variable to set |
| `value` | String | | value of environment variable |
| `replace_existing` | Boolean | `false` | if `false`, will append to existing variable using ':' as the separator |



## Output

The best and MFE structures that were found in each ensemble at a particular length are written
in both JSON and CT formats (e.g., `len119.json` and `len119.ct` files respectively for an RNA of 119 nts).
The JSON object types are described below.

If the `save_ensembles` config option was specified as `true`, then all of the structures generated in
each ensemble are saved in a [Python Pickle](https://docs.python.org/3/library/pickle.html) file as well.


### LengthResult

Results for all ensembles generated for a nucleotide sequence of a specific length (`L`). Saved in
a file called "len{L}.json".

| Key | Type | Description |
| --- | ---- | ----------- |
| `nt_seg` | String |nucleotide sequence of length L for which all structures here apply |
| `ensembles` | [[Ensemble](#Ensemble)] | JSON array of all ensembles generated for this length |
| `mfe_struct` | [Structure](#Structure) | minimum free energy structure found across all ensembles of this length |
| `max_free_energy` | Real | maximum free energy found across all structures in all ensemble of this length |


### Ensemble

Results for a single set ("ensemble") of samples generated at a given length (`L`).

| Key | Type | Description |
| --- | ---- | ----------- |
| `best_struct` | [Structure](#Structure) | the best structure (i.e., with minimum `rho_dist`) within the structs of this ensemble |
| `mean_rho_dist` | Real | the mean distance of structures in this ensemble from the reactivity (rho) vector |
| `structs` | [[Structure](#Structure)] | all unique structures in the ensemble (but only if `save_ensembles` is true in the main config, otherwise empty) |


### Structure

Represents a possible structure of an RNA sequence of length `L`.

| Key | Type | Description |
| --- | ---- | ----------- |
| `skey` | Integer | key that uniquely identifies this structure |
| `pairings` | [Integer] | array of length `L` where value at an index specifies the (1-based) index of nt base that this index is paired with (or 0) |
| `free_energy` | Real | computed free energy for this secondary structure (as computed w/ [FreeEnergyConfig](#FreeEnergyConfig) params) |
| `probability` | Real | if the sampling/partitioning tool supports it, the probability of the structure (-1 if not) |
| `rho_dist` | Real | R2D2 "distance" from reactivity (rho) vector (as computed w/ [DistanceConfig](#DistanceConfig) params) |

