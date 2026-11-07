# Confirmation v1 — fixed before execution

4 October 2026. This is a local hash-bound plan, not an externally timestamped
preregistration. Development outcomes have been inspected and informed the
implementation. Confirmation seeds have not been evaluated by this script.

## Question

Does reusing primal subspaces and spectral dual samples reduce work and elapsed
time for the same continuous-price finite-menu search, without changing its
loss accuracy, across several dimensions, ranks, and site counts?

Compare (i) reused spectral oracle and (ii) independently implemented
Brent/fair-PCA-style oracle. Both use identical outer menu construction,
epsilon tolerance 2e-6, price tolerance 2e-8, endpoint tolerance 1e-9.
The Brent reference has endpoint-aware early decisions and primal-recovery
fallback; it is not intentionally run to unnecessary full precision.

Cases: the old mirror example as a development control, and random PSD models
at (n,r,sites)=(8,1,1),(16,4,3),(32,8,6),(64,4,3),(64,16,3),
with fresh seeds 5100 and 5101 for each shape. Every model uses K=2 and K=4.
This gives 22 paired case/budget cells, 20 on new random instances. Three timing
repetitions, fresh model/cache per run, alternate method order. Model generation
excluded from timing, all algorithm preprocessing included. One BLAS thread.
No speed claim about other hardware, sparse matrices, very large n, or prior
authors' implementation. Dense full eigensolvers are used by both methods.

Store each row immediately in JSONL, with source/protocol hashes, timings,
eigenvalue-call counts, cache storage, continuous loss, and outcome/failure.
Do not delete failed cases. Resume only with identical hashed inputs, skipping
already recorded keys. Save first-repetition menus for independent verification.

Success evidence: numerical loss agreement within 5e-6 for every completed
pair, independent continuous-maximum evaluation, and no undisclosed failures.
Report paired time ratios by cell and regime, plus median and range; report
the cases where the reuse method loses. Any failure triggers diagnosis and a
new labeled protocol/version, not retroactive threshold or case edits.

This experiment addresses a reuse acceleration, not the entire contribution.
Separate tests must compare optimized sampled dictionaries at matched loss,
check degeneracy/near-degeneracy, verify global lower evidence, and complete
the literature and proof assessment. Passing this study alone does not justify
claiming the user's research goal is complete.
