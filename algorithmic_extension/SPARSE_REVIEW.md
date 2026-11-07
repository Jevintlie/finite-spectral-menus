# Sparse extension: scientific interpretation and review boundaries

This extension addresses the user's request to investigate efficient sparse
computation for Paper 2. Final numeric results are generated in
`results/sparse_summary.json`; release completion requires a passing v4
clean-extraction validation for the v4 study, not merely this document.
The subsequent banded extension requires the v5 gate and is described in
`BANDED_VERIFICATION.md`.

## What this can establish

The declared paired study compares CSR/ARPACK with dense partial LAPACK,
using the same menu search, cache rules, tolerances, and recovery. It tests
the practical effect of the spectral backend inside the existing finite-menu
algorithm. All losses are independently evaluated using ordered spectral
methods at the finite candidates needed for the continuous price maximum.
Separate outward witnesses establish global optimality gaps for selected
grid cases and the structured path screen.

The tridiagonal verifier extends the existing independent certificate
framework without requiring a dense matrix. Its inertia recurrence and
polar correction are standard mathematics; the contribution is their
implementation and integration with the finite-menu witnesses. The proof
and arithmetic assumptions are in `SPARSE_VERIFICATION.md` and the manuscript.

The avoided-crossing failure is material: both original backends reached
machine resolution in price before the requested objective gap. The stopped
v1 study remains visible. The fix directly adjusts the preset in a small
subspace, accepts it only against the original criterion, and is shared by
both methods in a fresh-seed v2 study. This improves robustness; it is not
presented as a new minimax theorem.

## What this cannot establish

- A universal sparse speedup or a new Lanczos algorithm. Small dimensions,
  higher ranks, spectral clusters, dense fill, and different outer-query
  patterns can change the comparison.
- Statistical generality from three timing repetitions: these repeats
  measure the same model, not three independent problem instances. Each
  dimension/rank has only two model seeds. Larger scaling cases have one
  observation per method and are explicitly descriptive.
- A universally efficient sparse outward eigensolver. The banded extension
  independently certifies all 14 CSR grid menus through n=4096. Its cost
  depends on bandwidth, and unpivoted interval factorization can fail.
  It does not imply efficient verification for arbitrary sparse graphs.
  Residual checks alone still do not certify extremal ordering or multiplicity.
- Bounded total memory from a bounded spectrum cache. Saved primal bases
  grow with query count. Reported input/cache/sample bytes omit Python objects
  and temporary eigensolver allocations and are not measured peak RSS.
- A validated engineering application. Graph Laplacians supply sparse PSD
  test matrices, not a calibrated resource or measurement-design model.
- Guaranteed journal acceptance or scientific priority over every predecessor.

The paper's central research claim remains its structural analysis of
realizability, missing optimal slopes, and finite additional-preset bounds.
Sparse computation supplies broader computational evidence. Its significance
should be judged on the measured tradeoffs and verification scope, not on
whether the implementation can import a sparse eigensolver.

## Primary references checked

- SciPy's ARPACK interface and its restrictions:
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.eigsh.html
- Tridiagonal ordered eigenvalue interface:
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.eigh_tridiagonal.html
- Demmel, Heath and van der Vorst (1993), LAPACK Working Note 60,
  section 6.3.2, LDL/Sturm eigenvalue counting:
  https://www.netlib.org/lapack/lawnspdf/lawn60.pdf

These sources support the numerical-method attribution. They do not by
themselves establish novelty of the full menu construction.
