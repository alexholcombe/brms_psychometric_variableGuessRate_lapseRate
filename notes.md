Starting after Denison students left off, in May 2025

Why did it estimate exactly zero for all the moderators (used 3 chains and 1000 iterations)?
It wasn't because I modeled logSigma as function of age was it? Don't think I did that before. I upped the chains and interactions, didn't help. 

Try turning off logSigma modeling. That didn't help.
Try putting init =0
That didn't help either but obviously something is totally wrong because the confidence intervals have zero width.

Maybe it's my formula setting somehow??? Get rid of separate formula setting
Trying it also with only 'lab'

~/Documents/softwareStatsEquipment/programming_psychophysics/brms_psychometric_variableGuessRate_lapseRate/brms_psychometric_variableGuessRate_lapseRate/docs/visualize_and_select_priors.qmd

mv all_factors_but_not_multilevel.qmd whyDoesntThisWork.qmd

Going with strategy of checking out the whole repo.

_basic_model_
advanced working but it's actually basic WORKS!!
k DOES NOT WORK
"Added gender and lab, now can try to make it multilevel" WORKS!
"additional" WORKS

_docs/advanced_model_recovery.qmd_
"advanced working but it's actually basic" WORKS
"additional" WORKS!
k WORKS!

WTF, current advanced_model_recovery.qmd_ version estimates lab correctly but age and gender are estimated at exactly zero.
I guess I should check out K and gradually upgrade.

I've been doing that but then it went back to zero again, which seemed to be because of the new expand.grid version of the condition generation. But then I went back to the old version and it still gave exactly-zero estimates for gender and age (but not for lab). So I still don't know what triggers the problem.
I've now turned off the logSigma_age part of the equation.

logSigma_age doesn't seem to have been the problem.
Going back to non expand.grid. That didn't work.

Rolling back the commits a couple commits, with new branch retryFromWorkingPlace. This is all in the brms_rebuild directory

Made small changes. Still works.

retryFromWorkingPlace now working great, except for num_targets estimate.
So now changing to  a new fixNumTargetsEstimate branch

trial doesn't incorporate targets but it isn't used right?

Wow subbing for labs didn't work

Wow it worked. 
Now will try to add lab back in.

Everything worked until I changed numTargets back to numeric!!!

Implementing Rafe's things bout priors

Error : The following priors do not correspond to any model parameter: 
<lower=0,upper=2.5> Intercept_eta ~ uniform(0, 2.5)

yeah because it's supposed to be eta_Intercept?

## To-do

Check if logSigma still wrong.

Try to work out reference group again.