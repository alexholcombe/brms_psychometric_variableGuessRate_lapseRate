Brms data analysis, for now mainly model recovery of MOT data, using single- and multi-level Baysian modeling.

Github Pages [site](https://alexholcombe.github.io/brms_psychometric_variableGuessRate_lapseRate/) auto-generated from [docs/](https://github.com/alexholcombe/brms_psychometric_variableGuessRate_lapseRate/tree/main/docs)

In each participant, model data with non-linear psychometric function in each participant. Sigmoidal but requiring a custom link function because goes from chance_rate to near 1 (affected by lapse rate), with lapse_rate, scale(slope), and location(threshold speed) parameters.

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
*	lme4
	*	Widely used for frequentist multilevel models.
Allows custom link functions via the family argument, but not as flexible as brms for arbitrary nonlinear models.
*	glmmTMB
	* Supports a wide range of distributions and custom link functions.
	* Good for complex random effects structures.
	* Multilevel?

