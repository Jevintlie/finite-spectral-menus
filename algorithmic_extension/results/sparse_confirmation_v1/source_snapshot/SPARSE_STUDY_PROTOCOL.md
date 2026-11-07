# Sparse computation study - declared before confirmation results

5 October 2026. User requested establishing efficient sparse computation.
The v3 manuscript and frozen dense studies are preserved.

## Scope and decision standard

Implement a CSR backend for the existing finite-menu construction, using
partial symmetric eigensolves. Compare it with dense partial eigensolves,
not just the old full-spectrum implementation. This tests an established
sparse numerical method inside our menu construction, not a new Lanczos
algorithm. Accept no universal sparse efficiency or rigorous ordering claim
from residuals alone. Negative outcomes and fallbacks must be retained.

The mathematical endpoint/covering proofs remain unchanged. Iterative
eigenpairs are numerical proposals. Independent full-spectrum verification
on tractable instances and outward menu bounds are separate gates. Large
instances without outward witnesses must be labeled numerical only.

## Development

Seeds 6100-6199. Test path and 2D-grid Laplacian families with independent
diagonal terms and common sparse quadratic task reward. Costs and rewards
are PSD by construction. Include diagonal crossings, repeated cutoffs,
high ranks, and an intentionally difficult weak-gap case. Record guard
expansion, fallback, eigensolver calls, residuals, and storage.

Do not tune families on confirmation outcomes. No externally validated
physical measurement model is asserted by using graph matrices.

## Confirmation

Fresh seeds 6200 and 6201. Shapes n=128,256,512, rank=2 and 8,
two sites, K=2, three repetitions, one BLAS thread. Alternate method order.
The confirmation family is the 2D grid, fixed before any confirmation run.
The path family additionally has a tridiagonal LAPACK reference in the
development/scaling study, since a generic sparse-versus-dense comparison
alone would overlook that stronger structured method.
Compare the same cached slope-bisection outer method with dense-partial
and CSR/ARPACK spectral backends. This isolates the spectral backend;
the previous hybrid-Brent comparison is not replaced by a weaker claim.
Use loss_tol=2e-6, price_tol=2e-8, oracle_tol=1e-9 throughout.
Verify all saved menus with independent dense spectral evaluation at all
line crossings and segment endpoints, numerical agreement target 5e-6.
If a confirmation method fails, retain the failure rather than silently
retrying with another algorithm or seed. A changed protocol needs a new version.

For each method save separate input, spectrum-cache, and basis-cache bytes;
these are retained arrays, not total process peak RSS. Charge spectrum and
sample cache creation and all recovery/fallback time. Model generation and
final independent verification are outside timed solve sections.

An additional path scaling screen uses n=1024 and 4096, rank=2, two sites, K=2,
seed=6300, with CSR/ARPACK and tridiagonal LAPACK. This is descriptive,
not a paired repeated benchmark. Any
outward certification limit and dense reference cost must be explicit.

## Integration gate

Only update the manuscript after checking numerical correctness, saved
continuous-price menus, final witnesses where applicable, and measured
tradeoffs. A negative sparse result remains a valid report; do not promote
an eigsh substitution alone into a demonstrated scalability claim.
