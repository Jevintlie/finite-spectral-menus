# Reuse ablation — fixed before execution

Compare identical slope-bisection endpoint solvers with and without reuse of
supporting subspaces, dual samples, and subgradient brackets. Both retain the
same bounded full-spectrum cache for exactly repeated spectral requests.
This isolates the combined reuse mechanism from the change from Brent to
bisection; it does not isolate each individual kind of cached bound.

Use seed 5500 (not previously used) in each of the five shapes from the warm
confirmation, K=2,4, three fresh-cache repetitions with alternating order.
Include the mirror model as a separate control: 72 total runs, 24 saved menus.
All tolerances and timing boundaries match CONFIRMATION_PROTOCOL.md. One BLAS
thread, no simultaneous numerical work. Retain all rows/failures and report
median-time ratios over all ten new-seed cells. Confirm numerical agreement
within 5e-6 and independently check saved continuous maxima/orthogonality.

This is a secondary mechanism ablation, not a stronger competitor than the
already completed hybrid-Brent comparison. Source hashes freeze the run.
