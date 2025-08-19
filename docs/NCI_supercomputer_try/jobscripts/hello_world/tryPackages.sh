#!/bin/bash

#PBS -P ew49
#PBS -q normal
#PBS -l ncpus=4
#PBS -l mem=16gb
#PBS -l walltime=00:10:00

echo "Current directory is $(pwd)"

module load R/4.5.0

Rscript -e "library(ggplot2)"
#Rscript brms_model_recovery_MOT/hello_packages/hello_packages.R
