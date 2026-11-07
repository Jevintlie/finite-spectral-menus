# Sparse confirmation v2: declared before fresh-seed runs

5 October 2026. Supersedes the confirmation portion of
SPARSE_STUDY_PROTOCOL.md; all scope limits and measurement rules remain.

The v1 run stopped after 18 of 72 planned runs. Six runs failed (both
backends, three repetitions) on seed 6201, n=128, rank=2. Price bisection
reached binary64 resolution near an avoided eigenvalue crossing before
the primal-dual gap met 1e-9. All rows and the original source snapshot
are retained under results/sparse_confirmation_v1. Seeds 6200 and 6201
are now development data and will not be called fresh confirmation.

Both backends now have the same two-vector recovery: if bisection fails,
rotate within the adjacent cutoff eigenvector plane to match the chord
slope, then evaluate the original endpoint objective. Accept only if
the original gap tolerance or original threshold decision is satisfied.
This is a numerical recovery, not an assumption of an exact eigenvalue tie.

Fresh seeds **6400 and 6401**, grid n=128,256,512, ranks 2 and 8, two sites,
K=2, three repetitions, alternating method order: 72 runs in 12 paired
cells. Same tolerances 2e-6 (loss), 2e-8 (price), 1e-9 (oracle), one BLAS
thread. Methods: dense partial LAPACK and CSR/ARPACK. Same outer search
and recovery. Frozen source hashes accompany the results.

Independent dense full-spectrum continuous-price checks for every saved
menu and paired loss spread below 5e-6 are required. Record all failures;
do not relax tolerances or change methods after looking at these results.
Report per-cell ratios and the median, including slower sparse cases.
Retained array counts are not peak process memory. Final outward
certificates, if generated, are reported separately from these checks.
