# Banded outward verification: proof, arithmetic and limits

This extension verifies the saved finite-menu witnesses. It does not alter
the menu optimizer or the isolated v4 runtime studies. Classical inertia
counting and band storage are used; no new eigenvalue theorem is claimed.

## Congruence and storage

Let H be symmetric with half-bandwidth b. At shift x, initialize interval
lower-band storage enclosing every entry of H-xI. At elimination step k,
the exact Schur complement has pivot d and column v supported in the next
at most b rows. When the pivot interval excludes zero, update the trailing
band entries by enclosing S_ij - v_i*v_j/d. Induction encloses every exact
Schur complement. Updating only the lower triangle preserves exact
symmetry; the update introduces no entry outside the original full band.

If all pivot intervals are finite and exclude zero, the corresponding exact
unpivoted factorization is H-xI=L D L^T with invertible unit lower triangular
L. Sylvester's law of inertia makes the number of negative diagonal entries
of D equal to the number of eigenvalues of H strictly below x. Every accepted
interval has a definite sign, so the certified count is exact. A singular
leading principal submatrix may prevent this factorization even when H-xI
is nonsingular. The implementation rejects that case; it never guesses a
sign or silently substitutes a pivot.

For sorted eigenvalues, counts N(l)<=j-1 and N(h)>=j give
lambda_j(H) in [l,h]. LAPACK's banded eigenvalues only propose centers;
accepted counts establish ordering independently. Add the first r intervals
and the overhead p*d_L to enclose the branch value. Take minima of lower and
upper endpoints separately to enclose the adaptive value.

A count uses O(n*b^2) scalar arithmetic operations and O(n*b+b^2) storage,
including indexing/workspace. This depends on filled bandwidth, not only
input nonzeros. The default implementation rejects half-bandwidth above 256.
It supplies no worst-case bound on bracket expansions or required precision.

## Arithmetic paths

The primary path uses the existing exact-binary64 input and outward
elementary IEEE-754 contract. Products, signed divisions and subtractions
are separately widened with nextafter. It does not use BLAS reductions
to certify an inequality. A pairwise outward addition tree replaces a
sequential sum where useful; induction at each tree node encloses its exact
subsum, including non-power-of-two lengths padded with exact zeros.

The initial version failed to verify one rank-eight witness because
interval propagation led to excessively wide eigenvalue brackets. The
failed attempt and its source snapshot are retained under
results/banded_certificates_v1. Version 2 retries an unresolved count at
n<=512 using 50-digit Decimal intervals. Decimal.from_float converts the
binary64 inputs exactly. Separate Context objects round each operation with
ROUND_FLOOR or ROUND_CEILING. Underflow, invalid operations, division by zero,
and overflow are trapped; nonfinite/zero-containing pivots are rejected.
This adds the standard library Decimal correct-directed-rounding assumption
to the arithmetic contract. It is not a proof-assistant verification.

The higher-precision path uses the same exact-matrix interpretation and
factorization induction. It returns only an integer inertia count, avoiding
any lossy conversion of Decimal interval endpoints to binary64. Automatic
fallback is limited to n<=512; larger cases may still fail to certify.

## Actual projectors and global menu bounds

Compute every entry of U^T U by outward product/sum operations. With
eta >= ||U^T U-I||_2 < 1, the exact polar basis Q exists and
||UU^T-QQ^T||_* <= r*eta. For the stored bands h_(k,i)=H_(i+k,i),

    tr(U^T H U) = sum_j sum_i h_(0,i) U_(i,j)^2
                 + 2 sum_j sum_(k=1..b) sum_i h_(k,i) U_(i+k,j) U_(i,j).

Enclose this sum and enlarge by r*eta times an outward absolute-row-sum
bound on ||H||. The result encloses the objective of QQ^T, an actual rank-r
orthogonal projector. The existing segment-endpoint upper argument and
K+1 ordered packing-point lower argument then provide global bounds.
The new checker also outward-rounds subtraction of the final bounds when
testing that their width is below 1.01e-5.

Branch-price pairs are independent and can run in CPU processes. The final
checker imports no menu solver or ARPACK backend. Parallel verification
times are not compared with isolated optimization timings. GPU arithmetic
is not part of this certificate's arithmetic contract.

## Attribution and validation

The classical congruence/inertia method and band-storage conventions are
documented in LAPACK materials:
https://www.netlib.org/lapack/lawnspdf/lawn60.pdf
https://www.netlib.org/lapack/lug/node124.html

Directed Decimal rounding and exact float conversion are documented by
Python (the implementation environment uses Python 3.12):
https://docs.python.org/3.12/library/decimal.html

Development checks include 144 exact rational inertia comparisons for each
arithmetic path, seven exact-rational sum checks, 16 spectral/objective
cross-checks against independent dense/tridiagonal verification, repeated
eigenvalues, indefinite matrices, and deliberate unresolved pivots. The
retained failure illustrates why those tests alone cannot imply success
on every new matrix. Final claims require saved-witness replay.
