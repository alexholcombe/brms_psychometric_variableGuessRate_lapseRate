---
layout: default
title: "Guide to this brms model recovery site"
---

[basic_model_recovery.html](docs/basic_model_recovery.html)

[all_factors_but_not_multilevel](all_factors_but_not_multilevel.html)

[advanced_model_recovery.html](advanced_model_recovery.html)

Check out [visualize_and_select_priors.html](visualize_and_select_priors.html)

[do_all_model_recovery.html](../do_all_model_recovery.html)

## Why is estimate of eta smaller by 0.16 than actual value?

It's not the numTargets difference

[eta_wrong.qmd](eta_wrong_minimal_example/eta_wrong.html)


## Why is estimate of logSigma so much larger (shallower) than actual value?

Discrepancy of 0.37 between my logSigma, -1.61 and what brms estimated, -1.24

[logSigma_wrong.qmd](logSigma_wrong_minimal_example/logSigma_wrong.html)

## Why do CIs for parameters whose true value is exactly zero never range below zero?

[CIs of estimates stop short at zero](why_do_CIs_not_range_below_zero/CIs_not_below_zero_advanced_model_recovery.html)


## Why does having numTargets be numeric make model recovery fail?

[FAIL version](break_brms_with_numeric_regressor/numTargets_recovery_FAIL_because_numeric.html)

[Success version, not numeric](break_brms_with_numeric_regressor/numTargets_recovery_SUCCEED_because_not_numeric.html)