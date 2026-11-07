# Accuracy-matched dictionary comparison v1

4 October 2026; specified after the Brent confirmation and before these runs.
This is a development/competitor assessment, not an untouched confirmation of
the final full method. All cases and unsuccessful stages will be retained.

Cases: mirror K=1,2,4; random PSD instances (n,r,sites,seed)=(16,4,3,5200),
(32,8,6,5200),(64,4,3,5200), each K=2,4; one commuting rank-one collision K=1.

Methods: reused continuous solver; all-site uniform dictionaries at nested sizes
129,513,2049,8193; adaptive dictionaries starting at 3 prices/site, refining
neighbors of selected presets and adding all site optima at the exact worst
price, for at most 20 rounds. Both dictionary methods optimize selection over
the continuous price interval. Include preprocessing, refinement, and all
selection solves in cumulative time. Fresh model per method; one BLAS thread.

Compute the reused solver's feasible loss, then seek a lower packing witness
within 1e-5. The externally supplied accuracy target for all competitors is
that reference upper +1e-5. This is a generous, oracle-assisted stop rule for
the baselines, not a deployable stopping guarantee. Record all stages until the
target is reached or the declared cap is exhausted. Refinement must not use
the reference's preset directions, active partition, or optimal sample prices.

Verify attained upper bounds separately with the interval verifier. Verification
cost is separate from construction time for all methods. Only with a verified
lower witness can this be described as globally accuracy-matched. If the
adaptive competitor erases the practical advantage, record that result and
revise the contribution rather than omitting the competitor.
