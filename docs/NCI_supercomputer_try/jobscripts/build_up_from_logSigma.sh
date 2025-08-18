#!/bin/bash

#PBS -P ew49
#PBS -q normal
#PBS -l ncpus=4
#PBS -l mem=16gb
#PBS -l walltime=00:10:00

echo "Current directory is $(pwd)"

module load R/4.5.0

echo "Contents of current directory are: $(ls)"
echo "End of directory listing."
echo "ls of brms_model_recovery_MOT/brms_psychometric_variableGuessRate_lapseRate/docs/NCI_supercomputer_try/jobscripts is $(ls brms_model_recovery_MOT/brms_psychometric_variableGuessRate_lapseRate/docs/NCI_supercomputer_try/jobscripts)"
Rscript brms_model_recovery_MOT/brms_psychometric_variableGuessRate_lapseRate/docs/NCI_supercomputer_try/jobscripts/build_up_from_logSigma.R
