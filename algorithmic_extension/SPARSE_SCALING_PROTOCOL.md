# Descriptive scaling screen

Declared 5 October 2026 before running this screen. The original protocol
already specifies paths n=1024,4096, rank=2, sites=2, K=2, seed=6300, with
CSR/ARPACK and tridiagonal LAPACK. Retain that comparison, one timed run
per method/size; it is descriptive, not a repeated confirmation study.

Additionally test grids n=1024 and 4096 with seed=6500, rank=2, sites=2,
K=2, using CSR/ARPACK. At n=1024 also time dense-partial LAPACK once.
These cases probe a larger generic sparse regime; they are not selected
after seeing their outcomes. Same tolerances as confirmation. Record failures.
All computations are sequential, with one BLAS thread. Setup and independent
verification are outside solver timings. No timeouts will be hidden.

Check path menus with independent ordered tridiagonal eigenvalues and
outward Sturm/polar witnesses. Check the n=1024 grid with full dense
eigenvalues at every menu-line intersection and interval endpoint. For
n=4096 grid use an independent banded LAPACK eigensolve, exploiting the
known bandwidth floor(sqrt(n)), for the same numerical continuous-price
check. The latter is not an outward general sparse certificate.

Do not infer universal speed, memory, or asymptotic complexity from this
screen. Report tridiagonal timings beside the path ARPACK timings, even if
the specialized solver wins. Report retained arrays rather than peak RSS.
