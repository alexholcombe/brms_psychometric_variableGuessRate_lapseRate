This is for trying brms data analysis of multiple object tracking, for now mainly model recovery, using single- and multi-level Baysian modeling.

The idea is to model:

Non-linear psychometric function in each participant. Sigmoidal but requiring a custom link function because goes from chance_rate to near 1 (affected by lapse rate), with lapse_rate, scale(slope), and location(threshold speed) parameters.

Within-participant factors:

*	numTargets (2 vs 3 for Holcombe data, 1,2,3 for Roudaia data)
*	numObjects (4 vs 8 for Holcombe data, 5 vs 10 for Roudaia data)

Between-participant factors

* gender
* ageGroup
* lab (ideally done in a multilevel way)
* individual differences

For an alternative to Bayesian, what library should I use?

*	There's the python implementation of psignifit.
*	Some

