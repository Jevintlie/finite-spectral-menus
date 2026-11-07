# Independent finite-menu bounds with outward rounding

Development derivation, 4 October 2026. The numerical solver and the verifier
have separate roles. A small solver stopping tolerance is not a certificate.

## Eigenvalue bounds without trusting eigensolver accuracy

Let H be the exact symmetric matrix defined by stored binary64 inputs and a
stored binary64 price. Let V and diagonal D be an approximate full eigensystem,
treated as exact floating-point entries. Interval products enclose

    G=V^T V, B=V^T H V.

Take eta>=||G-I||_2 and rho>=||B-D||_2, using symmetric absolute row-sum bounds.
If eta<1, V is invertible. For any nonzero x, the generalized Rayleigh quotient
x^T Bx/(x^T Gx) differs from x^T Dx/(x^T x) by at most

    delta=(rho+||D||_2 eta)/(1-eta).

This follows by writing B=D+(B-D), G=I+(G-I), bounding the denominator below
by (1-eta)||x||^2, and subtracting the two quotients. Generalized Courant-Fischer
then gives |lambda_j(H)-D_jj|<=delta for sorted D. The sum of r smallest
eigenvalues is enclosed by sum D_jj +/- r delta. Add the outward-rounded
overhead p*d_L. Taking the minimum of site lower endpoints and of site upper
endpoints encloses F(p).

All interval matrix products in `interval_verifier.py` are explicit scalar
product/addition stages with nextafter widening, independent of BLAS reductions.
The eigensolver's output is only a candidate congruence basis. Its accuracy is
checked by the above enclosures; insufficient accuracy yields wide bounds or
an invertibility failure, not an unchecked success.

## Actual realizable subspaces from saved bases

A stored n-by-r basis U need not be exactly orthonormal in real arithmetic.
Interpret it as the subspace with polar basis Q=U(U^TU)^(-1/2). If
eta_U>=||U^TU-I||_2 is below one, Q exists and is orthonormal. Singular values
show that

    ||UU^T-QQ^T||_* = sum_j |sigma_j(U)^2-1| <= r eta_U.

Consequently the interval trace of U^T H U, enlarged by
r*||H||_2*eta_U, encloses the actual objective of the realizable Q projection.
No eigendecomposition of the small Gram matrix is required by the verifier.

For every saved covering segment [a,b], evaluate the preset at both endpoints
and use a fixed site on the segment. J_L(Q,p)-F(p) is convex, so the larger
endpoint upper bound covers the complete segment. A contiguous partition of
[0,B] and at most K saved presets therefore certify a global upper bound.
This avoids having to certify numerically computed menu-line intersections.

## Global lower bound

For adjacent witness prices a<b and any p_L in [a,b], weak minimax duality gives

    e_L(a,b) >= F_L(p_L)
                  - (1-t_L) F(a) - t_L F(b),
    t_L=(p_L-a)/(b-a).

The verifier evaluates this expression with outward intervals for each site.
If all site lower bounds exceed epsilon, no preset covers both witness prices.
If there are K+1 ordered witnesses and every adjacent pair is excluded, convex
coverage means each preset covers at most one witness. Thus E_K>epsilon.
This lower certificate needs weak duality only, not exact recovery or convergence
of the solver. It requires the shared task reward and nonnegative prices that
make one cheapest site valid for each preset.

## Arithmetic contract and limitations

Each input binary64 number denotes its exact real value, not an interval for
physical measurement uncertainty. The implementation assumes IEEE-754 binary64
elementary arithmetic with correctly rounded operations and gradual underflow;
overflow or nonfinite intermediates cause failure. No formal proof assistant or
independent audit of the interval implementation has yet been completed.
Arithmetic enclosure tests against exact fractions, invariant tests, and the
complete saved-result verification must pass before advertising certified
global bounds. A successful certificate proves the declared mathematical
instance, not scientific relevance or novelty.
