# Sparse computation and verification: derivation and limits

## Partial spectra and recovery

`sparse_spectral.py` uses SciPy's ARPACK interface for lowest Ritz pairs,
QR and Rayleigh--Ritz refinement, residual checks, and extra vectors beyond
the rank cutoff. These are established numerical techniques. A small
residual locates an eigenvalue near a Ritz value; it does not count missing
lower eigenvalues or prove that a repeated eigenspace was fully recovered.
Consequently a general CSR solve remains a proposal until independently
checked. Dense fallbacks are counted and disabled above n=1024.

Near an avoided crossing, scalar-price bisection may reach machine resolution
without resolving the endpoint objective. Fix the first r-1 vectors and
rotate the two adjacent cutoff vectors by (cos(theta), sin(theta)). If their
compressed cost matrix is M, the resulting cost is

    fixed_cost + tr(M)/2 + (M11-M22)/2 cos(2 theta) + M12 sin(2 theta).

Solve this scalar equation for the required chord slope, test both roots,
and evaluate the actual original endpoint costs. Accept only against the
unchanged endpoint gap/decision criterion. No exact tie is assumed; a poor
subspace or an unattainable cost fails the test. This is a floating-point
primal recovery, not a rigorous lower-bound certificate.

## A structured sparse certificate

`tridiagonal_verifier.py` supports exactly symmetric tridiagonal A and C.
It does not support general CSR matrices. It inherits the exact-binary64
input and elementary IEEE-754 outward-arithmetic contract in
`CERTIFICATE_DERIVATION.md`. No dense n by n array is required.

For a real shift x, let H-xI have diagonal a_i-x and off-diagonal b_i.
If the recurrence

    t_1 = a_1-x,  t_i = a_i-x - b_(i-1)^2/t_(i-1)

has no zero pivot, H-xI = L diag(t_i) L^T with invertible unit lower
bidiagonal L. Sylvester's inertia law therefore says that the number of
negative t_i equals the number of eigenvalues of H strictly below x.
Interval arithmetic encloses each exact recurrence value by induction.
Only finite pivot intervals excluding zero are accepted. A pivot containing
zero causes rejection, never a guessed sign or an unverified replacement.

If certified counts at l and h satisfy count(l)<=j and count(h)>=j+1
(j starts at zero), then lambda_(j+1)(H) lies between l and h. LAPACK
eigenvalues merely propose centers; expanding intervals and independently
rechecking the counts establishes ordered eigenvalue enclosures. Summing
the first r intervals and adding p*d encloses F_L(p). Multiplicities are
allowed; no residual-based ordering assumption enters this argument.

For a saved n by r basis U, outward products bound ||U^T U-I|| by eta<1.
The exact polar basis Q exists, with ||UU^T-QQ^T||_* <= r*eta. Compute
tr(U^T H U) from diagonal and neighboring entries only, then enlarge by
r*eta times an outward absolute-row-sum bound for ||H||. This encloses the
objective of an actual orthogonal projector. The existing segment-endpoint
upper argument and K+1 packing-point lower argument then certify a global
continuous-price optimization gap.

For fixed rank, a successful Sturm count uses O(n) work/storage and the
preset check uses O(n*r^2) elementary interval operations. The number of
bracket attempts and the solver's iteration count are not given a worst-case
bit-complexity bound. Basis sample storage can grow with oracle calls.

## Attribution and checks

The LDL/Sturm recurrence and ordered eigenvalue bisection are classical;
see Demmel, Heath and van der Vorst, *Parallel numerical linear algebra*,
LAPACK Working Note 60 (1993), section 6.3.2, Algorithm 17:
https://www.netlib.org/lapack/lawnspdf/lawn60.pdf

SciPy interfaces:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.eigsh.html
https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.eigh_tridiagonal.html

Development checks compare 27 interval counts with exact rational LDL
counts, including mixed inertia; compare enclosures with the separate dense
verifier; test cutoff multiplicity/high rank; and retain the avoided-crossing
regression from the stopped v1 study. These tests are not an external audit
or a proof-assistant verification.
