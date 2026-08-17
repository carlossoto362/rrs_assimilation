contact: carlos.soto362@gmail.com

## Description

Files required to reproduce the remote sensing reflectance
(RRS) assimilation experiments as a function of constant
inflation, as well as with an online noise estimation
method, for both an indirect assimilation and a direct one.
The configuration files and forcings were downloaded from
[zenodo](https://doi.org/10.5281/zenodo.10067424)

A GOTM-FABM-BFM setup to run 1D simulations at the
Boussole site used in [Álvarez et al. (2023)](https://doi.org/10.5194/bg-20-4591-2023). Since the experiments were
performed on a cluster, we only share the configuration
files needed to run the experiments.

The remote sensing reflectance assimilation experiments are
done using the Ensemble and Assimilation Tool [EAT](https://doi.org/10.5194/gmd-17-5619-2024), a Python 3 tool
which uses the Parallel Data Assimilation Framework [PDAF](https://pdaf.awi.de/trac/wiki), a Fortran-based software
environment to perform data assimilation. EAT works by
running an ensemble of the physico-biogeochemical model in
parallel; every time there is an observation available, it
stops the simulation, performs an analysis step, and then
continues the simulation.

The interaction between the biogeochemical model, in our
case the Biogeochemical Flux Model (BFM), and the physical
component, the General Ocean Turbulence Model (GOTM),
is handled by the Framework for Aquatic Biogeochemical
Models (FABM). In addition, [Álvarez et al. (2023)](https://doi.org/10.5194/bg-20-4591-2023) included
the bio-optical component in the model, making possible
the direct assimilation of rrs.

##Requirements for reproducing the results

- **CMAKE**
- **EAT:** The EAT tool can be installed with Anaconda;
see [link](https://github.com/BoldingBruggeman/eat/wiki/).
It installs GOTM and FABM with their default configurations.
It can be downloaded from GitHub at [link](https://github.com/BoldingBruggeman/eat)
or from Zenodo with [DOI](https://doi.org/10.5281/zenodo.20006284).

- **BFM:** In addition to the EAT tool, FABM, and GOTM, it will
be necessary to install the BFM model configured to work with
FABM. The original version is available on GitHub,
[link](https://github.com/inogs/bfmforfabm.git), or on Zenodo,
[link](https://doi.org/10.5281/zenodo.10075551), but the
version used was the one on GitHub, with a more recent commit.
We also modified one of the files from the GitHub repository,
for which we included the OASIM model for FABM that we used
for the assimilation, where we added the variables NAP and CDOM
as part of the outputs of the model in the
[modified light_spectral_OASIM.F90 file](reference/light_spectral_OASIM.F90).

- **Fortran compiler:** Both BFM and EAT are Fortran-based, so
it is necessary to have a Fortran compiler, while EAT also uses
Python version >= 3.8. To install EAT with the Anaconda method,
it is necessary to have installed Anaconda or Miniconda, and to
have mpi4py installed for the parallel computations.

- **OPTIONAL, Slurm:** The experiments were originally
performed on a cluster with the Slurm workload manager. While
it is not necessary to reproduce the experiments, the files
called jobParallelSlurm are scripts to schedule the
experiments on a cluster managed with Slurm.

##Installing the necessary software to reproduce the results


To reproduce the results, it is enough to install EAT, the BFM for
FABM, and the OASIM model for FABM.

###command lines to do so with GitHub, and Anaconda:
	
- Downloading fabm-spectral, model of the incoming irradiance,
	
	- commit: 259df5c4d6d377e2992da8164696d2961915175b
	- Date:   Wed Jul 10 08:29:14 2024 +0100

```console
$ git clone --recursive \
    https://github.com/pmlmodelling/fabm-spectral.git\
    ./extern/spectral
	
$ cd extern/spectral
	
$ git checkout\
    259df5c4d6d377e2992da8164696d2961915175b
	
$ cd ../../
```
		     
- Downloading bfm for fabm, branch neccton

	- commit: b5da7ecd4df375ab2e368dcf58731ff255990293
	- Date: Mon Apr 14 18:29:22 2025

```console
$ git clone --recursive\
https://github.com/inogs/bfmforfabm.git\
./extern/ogs

$ cd extern/ogs

$ git checkout\
b5da7ecd4df375ab2e368dcf58731ff255990293

$ cd ../../
```

- Modify the light_spectral_OASIM.F90 file for the one we used
(includes the definitions for NAP and CDOM)

```console
$ mv extern/ogs/light_spectral_OASIM.F90\
  extern/ogs/light_spectral_OASIM.F90_original

$ cp reference/light_spectral_OASIM.F90\
  extern/ogs/
```
- Downloading EAT, and installing it,

	- commit: cb6e2352c75f9962efed08f18b7f749dbe2a5c58
	- date: Mon Nov 18 17:00:53 2024 +0000
	
```console
$ git clone --recursive\
  https://github.com/BoldingBruggeman/eat.git\
  ./extern/eat

$ cd extern/eat

$ git checkout\
  cb6e2352c75f9962efed08f18b7f749dbe2a5c58

$ conda env create -f environment.yml

$ conda activate eat

$ source ./install\
  -DFABM_INSTITUTES="ogs;spectral"\
  -DFABM_OGS_BASE=../ogs\
  -DFABM_SPECTRAL_BASE=../spectral
```

- Installing the Python 3 module ruamel for managing yaml files.

```console
$ conda install ruamel.yaml
```
- Creating the experiment files:

```console
$ python3 create_forgeting_factors_experiments.py\
  -hp <path/to/home> -N <Number_of_ensemble_members>
```

where ***path/to/home*** is the path to the folder where you have
the folders gotms, fabms, reference, forcing, and observations,
and ***Number_of_ensemble_members*** is the number of
ensemble members per experiment, which has to be (number of
cores available - 1) if the simulation of ensemble members is
performed with one core each. 

##File description

###reference

The folder reference contains the baseline files needed to
simulate the biogeochemical properties at the Bouée pour
l’acquisition d’une Série  Optique à Long terme (BUOSSOLE)
site, located in the Ligurian Sea, a subbasin of the Western
Mediterranean Sea, approximately at the coordinates 7 degrees
54 minutes E, 43 degrees 22 minutes N, setup downloaded from
[Alvarez, 2023](https://doi.org/10.5281/zenodo.10067424).
The original FABM is called [fabm_original.yaml](reference/fabm_original.yaml),
and the one used with some modifications in the parameter values
is [fabm.yaml](reference/fabm.yaml).
Together with the folder ../forcing, running:

```console
$ eat-gotm
```

inside this folder should work as long as it contains the
files fabm.yaml, gotm.yaml, restart.nc, the folder bcs, and
the folder ../forcings, and the installation of EAT, with BFM
and the spectral component.

The output is a netcdf with all the variables called result.nc,
and a file restart.nc, with the value of the state variables
at the end of the simulation.

####reference/bcs

Contains the spectral absorption and total scattering
coefficients for water, chlorophyll, cdom, and particulate
organic carbon needed to run the bio-optical component of the
model implemented by [Álvarez et al. (2023)](https://doi.org/10.5194/bg-20-4591-2023).

###forcings

This folder has the forcings needed to run the BFM coupled
with GOTM and the bio-optical components. It has the same
forcings as the ones used by [Álvarez et al. (2023)](https://doi.org/10.5194/bg-20-4591-2023),
plus the eastward gradient of pressure (ugos.csv) and the
northward gradient of pressure (vgos.csv).

###observations

The ensemble and assimilation tool (EAT) runs the model and
simultaneously checks text files with observations. Every time
an observation is encountered, EAT stops the simulation,
executes an assimilation step with the new observation,
changing the state of the system, and initializes the
simulation with the new states. The observations needed for
the assimilation are in this folder. 
For my work, I used three types of observations:

- **log transform of the buoy sea surface chlorophyll:**
  - chla_std.txt
  
- **log transform of the remote sensing reflectance:**
  - rrs_425.txt
  - rrs_450.txt
  - rrs_500.txt
  - rrs_525.txt
  - rrs_550.txt
  
- **log transform of the remote sensing sea surface
chlorophyll, nap and cdom:**
  - chla_inverted.txt
  - nap_inverted.txt
  - cdom_inverted.txt
  
###fabms

The goal of the work was to analyse the performance of an
ensemble-based data assimilation. For this end, we created an
ensemble of simulations with different initial conditions and
parameterizations. To ensure reproducibility, the
parameterizations corresponding to the biogeochemical and
bio-optical model used during our work are in the different
[fabm_#.yaml](fabms/fabm_0001.yaml) files. 

###gotms

The goal of the work was to analyse the performance of an
ensemble-based data assimilation. For this end, we created an
ensemble of simulations with different initial conditions and
parameterizations. To ensure reproducibility, the
parameterizations corresponding to the physical model used
during our work are in the different [gotm_#.yaml](gotms/fabm_0001.yaml) files. 

###initializations

The goal of the work was to analyse the performance of an
ensemble-based data assimilation. For this end, we created an
ensemble of simulations with different initial conditions and
parameterizations. To ensure reproducibility, the
initial conditions for the model used during our work are in
the different [restart_#.nc](initializations/restart_0001.yaml) files. 

###plugins

Two main plugins were used during the assimilation steps, in
addition to the main plugins already available in the EAT
tool.
	
- **transform_clean.py:** Log transform the state variables,
and force the output values to be between the ranges:

```python
x > max(gamma_min,gamma_minus)
x < max(gamma_max,gamma_plus)
```

where gamma_minus = 1E-9, gamma_plus = 4, and gamma_min and
gamma_max are the minimum and maximum values of the variables
during a simulation without assimilation. This procedure
helped to avoid divergences, hoping it didn't have a
strong effect on the final results. We also add noise with
zero mean, uniformly distributed between −0.1E−9 and 0.1E−9 to
variables with zero variance.

- **online_noise.py:** This plugin adds noise and, every time
an observation is available, adjusts the amplitude of the noise
added according to an online-noise estimation scheme.
				 
We also included the plugin used to store the average
statistics of an ensemble simulation without data
assimilation.

###da_chla_assimilation, da_chla_buoy_assimilation, da_cha_nap_cdom_assimilation, da_rrs_assimilation, da_no_assimilation

Folders where the experiments with constant inflation, and the
experiments with online-noise estimation, will be stored with
the default settings by running

```console
$ python3 create_forgeting_factors_experiments.py\
  -hp <path/to/home>\
  -N <Number_of_ensemble_members>
```

where ***path/to/home*** is the path to the folder where you have
the folders gotms, fabms, reference, forcing, and observations,
and ***Number_of_ensemble_members*** is the number of ensemble
members per experiment, which has to be equal to the number of
cores available - 1 if the simulation of ensemble
members is performed with one core each.

the folder da_no_assimilation/factor_00001 has the
[run.py](da_no_assimilation/factor_00001/run.py) script to
perform an ensemble simulation without data assimilation. 

###extern

Intended as the folder where the software EAT, BFM (ogs), and
the OASIM for FABM (Spectral) will be stored if the steps in
the section [command lines to do so with GitHub, and Anaconda](#command-lines-to-do-so-with-GitHub,-and-Anaconda).

###validation
Contains a copy of the dataset [MedBGCins-v1](https://doi.org/10.5281/zenodo.15489967),
and a netCDF4 file with the bathymetry used to assess when a
datapoint was deep water or not. For space availability, we
don't share the outputs of all the experiments.

##Reproducing the experiments:

If EAT has been installed correctly, then using 148
ensemble members would lead to the same results as our
experiments. There are two kinds of experiments:

###Constant inflation experiments

We perform a 10-year simulation plus assimilation with the
ESTKF from 2001 to 2010 with different inflation values.
Running the script

```console
$ python3 create_forgeting_factors_experiments.py\
  -hp <path/to/home>\
  -N <Number_of_ensemble_members>
```

where ***path/to/home*** is the path to the folder where you have
the folders gotms, fabms, reference, forcing, and observations,
and ***Number_of_ensemble_members*** is the number of ensemble
members per experiment, will create the necessary setup to
run the experiments.

The script will create the setup for 10 experiments with
different inflation values, for each of the following kinds of
assimilations:

- assimilating chlorophyll data from the BUOSSOLE buoy,
experiments stored in ./da_chla_buoy_assimilation/factor_<#>/

- assimilation of remote sensing chlorophyll, experiments
stored in ./da_chla_assimilation/factor_<#>/

- assimilation of remote sensing chlorophyll, nap and cdom,
experiments stored in ./da_chla_nap_cdom_assimilation/factor_<#>/

- assimilation of remote sensing reflectance, experiments
stored in ./da_rrs_assimilation/factor_<#>/

where factor_<#> represents a different folder with the
corresponding constant inflation factor for the given
constant-inflation experiment.

Inside each folder, you would be able to run

```bash
$mpirun -n 1 python3 run.py : \
-n <number_ensemble_members> eat-gotm \
--separate_restart_file --separate_gotm_yaml
```

and the ensemble simulation plus assimilation will be
performed, with outputs stored in the given folder, in
netCDF4 files called `result_<ensemble_member>.nc`.

Running the simulation with 148 ensemble members will need
sufficient computational power, for which we used a cluster
with Slurm. If you have access to it, the script

```console
$ sbatch jobParallelSlurm <path_with_experiments_to_run>
```

This will run the experiments sequentially in `<path_with_experiments_to_run>`
(e.g., `./da_chla_assimilation`) with 148 ensemble members (in which case you
would need to create the setup for the experiments using 148 ensemble members).

**NOTE:** It is possible to set a different path for the experiments. In case you
need to create them in a different path (useful when working in a cluster where
different paths have different memory availability), check:

```console
$ python3 create_forgeting_factors_experiments.py -h
```

In that case, `<path_with_experiments_to_run>` will need to point to the path
selected when creating the experiment setups.


### Online noise estimation experiments

Since these are fewer experiments, we already share the folder with the
respective `run.py` script. To run the experiments, it will still be necessary
to copy the gotm, fabm, and initialization files from the folders `./gotms`,
`./fabms`, and `./initializations`, and then go to the corresponding folder to
run the command:

```console
$ mpirun -n 1 python3 run.py : \
  -n <number_ensemble_members> eat-gotm \
  --separate_restart_file --separate_gotm_yaml
```





