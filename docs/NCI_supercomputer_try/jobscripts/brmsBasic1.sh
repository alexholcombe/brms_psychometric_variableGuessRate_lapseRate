#!/bin/bash

#PBS -P ew49
#PBS -q normal
#PBS -l ncpus=4
#PBS -l mem=16gb
#PBS -l walltime=00:10:00

echo "Current directory is $(pwd)"
echo "Path is $PATH"

module load R/4.5.0

echo "Pwd is $(pwd)"

my_NCI_scripts_dir=~/brms_model_recovery_MOT/brms_psychometric_variableGuessRate_lapseRate/docs/NCI_supercomputer_try

echo "ls of my_NCI_scripts_dir is $(ls "$my_NCI_scripts_dir")"

echo "About to run quartoBasic"

#Make sure quartoBasic works
~/bin/quarto render brms_model_recovery_MOT/brms_psychometric_variableGuessRate_lapseRate/docs/NCI_supercomputer_try/quartoBasicTry/quartoBasic.qmd --to html

echo "Now about to run brmsBasic.qmd"

#Try brms
~/bin/quarto render brms_model_recovery_MOT/brms_psychometric_variableGuessRate_lapseRate/docs/NCI_supercomputer_try/brmsBasic.qmd --to html
