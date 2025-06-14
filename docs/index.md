---
layout: default
title: "Guide to this brms model recovery site"
---

Eventually, [do_all_model_recovery.html](../do_all_model_recovery.html)

[all_factors_but_not_multilevel](all_factors_but_not_multilevel.html) . Works for estimating a few factors but blows up to almost 5 hrs when estimating all factors, and at least with limited runs (700 iterations, 2 chains), lab factor blew up. But reference group might be correct.

[lab_age_model_works](lab_age_model_works/lab_age_model_works_except_logSigma.html)

[basic_model_recovery.html](docs/basic_model_recovery.html)



[advanced_model_recovery.html](advanced_model_recovery.html)

## Why is estimate of logSigma so much larger (shallower) than actual value?

Discrepancy of 0.37 between my logSigma, -1.61 and what brms estimated, -1.24
Works in this seemingly super-simple case:
[logSigma_wrong](logSigma_wrong_minimal_example/logSigma_wrong.html)

Also works when simultaneously estimating alpha

I'm thinking that creating unmodeled dispersion by adding back in the target penalty will make sigma be estimated too shallow.

## Why do CIs for parameters whose true value is exactly zero never range below zero?

[CIs of estimates stop short at zero](why_do_CIs_not_range_below_zero/CIs_not_below_zero_advanced_model_recovery.html)


## Why does having numTargets be numeric make model recovery fail?

[FAIL version](break_brms_with_numeric_regressor/numTargets_recovery_FAIL_because_numeric.html)

[Success version, not numeric](break_brms_with_numeric_regressor/numTargets_recovery_SUCCEED_because_not_numeric.html)

## Reference group

[not_multilevel_model_recovery](docs/not_multilevel_model_recovery.html)

## Priors

Check out [visualize_and_select_priors.html](visualize_and_select_priors.html)

A remaining question is why lb and ub are not accepted for prior that applies only to eta_Intercept. If one sets lb and ub, one gets this error:

` Error : Prior argument 'coef' may not be specified when using boundaries. `

So I dropped lb and ub.

That yields a warning because the uniform prior I set does have bounds, and brms doesn't like that discrepancy.

` Warning :It appears as if you have specified a lower bounded prior on a parameter that has no natural lower bound.
If this is really what you want, please specify argument 'lb' of 'set_prior' appropriately.
Warning occurred for prior 
b_eta_Intercept ~ uniform(0, 2.5) `

 with "Error : Prior argument 'coef' may not be specified when using boundaries." make it difficult to have a uniform prior, should I go for a non-uniform prior even for effects of groups that I'm interested in estimating (as opposed to the Intercept)

Age_group estimate went crazy in not_multilevel_model_recovery.qmd, maybe by confining the prior to the intercept I no longer have a prior on the coefficient. 

# All the problems below were I think because prior bounded at zero also applied to coefficients



## Why did this stop working, estimating age and gender as having zero effect while others work?

[not_multilevel_model_recovery](not_multilevel_model_recovery.html) - why did this stop working for estimating effects of age and gender? Try make_stancode()

why are gender and ageGroup estimates zero

also looking at [what is happening during a chain](https://discourse.mc-stan.org/t/init-not-using-my-initial-values-and-seems-to-be-defaulting-to-0/39548):

, [goes straight to zero](why_age_estimated_as_zero/age_estimated_as_zero.html) almost. And posterior density is ridiculously peaked at zero.

More minimal yet [still](why_age_estimated_as_zero/age_estimated_as_zero_continue.html)

Save warm-ups and then do diagnostics too.

* Turning off init=0, back to default. Did not help

fit$fit@sim$samples[[1]] includes stepsize and
attr(,"sampler_params")$divergent

## Eta estimation by itself or in conjunction with lapse only (and no factors) seems ok

Although it's often off by maybe 0.16

I'm trying to get back to eta being so wrong when both lapse and logSigma estimated.

[eta_wrong](eta_wrong_minimal_example/eta_wrong.html)



At first I thought lapse biased high, but maybe that byproduct of high eta?

I upped the trials and even with lapse estimation on it seems ok.
With eta =1.1, 1.6 and 1.7 as well it does fine!

[eta_lapse_estimation_no_apparent_bias](eta_wrong_minimal_example/eta_lapse_estimation_no_apparent_bias.html)
 
## When add one factor, age, fails

Can't figure out why it always just splits the difference and gives zero for effect of age.

[eta_with_one_factor](eta_wrong_minimal_example/eta_with_one_factor.html)

Splitting the difference and assigning close to zero effect of age

Trying to work back down from not_multilevel_model_recovery but it also now isn't working for gender and age? It really seems like sometimes brms won't recover the effect of these factors.



