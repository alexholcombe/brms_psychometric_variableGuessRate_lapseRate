---
layout: default
title: "Guide to this brms model recovery site"
---

Eventually, [do_all_model_recovery.html](../do_all_model_recovery.html)


[basic_model_recovery.html](docs/basic_model_recovery.html)

[all_factors_but_not_multilevel](all_factors_but_not_multilevel.html)

[advanced_model_recovery.html](advanced_model_recovery.html)

## Why did this stop working, estimating age and gender as having zero effect while others work?

[not_multilevel_model_recovery](not_multilevel_model_recovery.html) - why did this stop working for estimating effects of age and gender? Try make_stancode()

why are gender and ageGroup estimates zero

also looking at [what is happening during a chain](https://discourse.mc-stan.org/t/init-not-using-my-initial-values-and-seems-to-be-defaulting-to-0/39548):

, [goes straight to zero](why_age_estimated_as_zero/age_estimated_as_zero.html) almost. And posterior density is ridiculously peaked at zero.


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

## Why is estimate of logSigma so much larger (shallower) than actual value?

Discrepancy of 0.37 between my logSigma, -1.61 and what brms estimated, -1.24

[logSigma_wrong](logSigma_wrong_minimal_example/logSigma_wrong.html)

## Why do CIs for parameters whose true value is exactly zero never range below zero?

[CIs of estimates stop short at zero](why_do_CIs_not_range_below_zero/CIs_not_below_zero_advanced_model_recovery.html)


## Why does having numTargets be numeric make model recovery fail?

[FAIL version](break_brms_with_numeric_regressor/numTargets_recovery_FAIL_because_numeric.html)

[Success version, not numeric](break_brms_with_numeric_regressor/numTargets_recovery_SUCCEED_because_not_numeric.html)

## Priors

Check out [visualize_and_select_priors.html](visualize_and_select_priors.html)
