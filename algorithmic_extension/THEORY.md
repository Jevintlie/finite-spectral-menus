# Historical derivation notes

The completed arguments are in `END_TO_END_PROOF.md` and the new manuscript.
These initial notes are preserved as development history; numerical global
bounds are now checked by `interval_verifier.py` and saved witness files.

# Candidate general-rank menu reduction

This is a research derivation, not yet an independently refereed theorem.
The two-objective spectral ingredient is established in fair-PCA literature.

Let P=UU^T, U^TU=I_r, with 1<=r<=n. At site L set

    J_L(P,p) = tr((-A+p C_L)P) + p d_L,
    F_L(p) = sum_{j=1}^r lambda_j(-A+p C_L) + p d_L,
    F(p) = min_L F_L(p).

A and C_L are symmetric; the measurement interpretation assumes A,C_L PSD
and d_L>=0. Prices p are nonnegative. The task matrix A is shared by sites.
A preset counts a subspace, not each basis vector within it.

For fixed P, the cheapest site minimizes tr(C_L P)+d_L independently of p.
The effective objective is affine and its regret relative to F is convex.
Thus endpoint sufficiency and the existing interval-covering proof remain valid.

## Endpoint minimax

For a<b define chord slope s=(F(b)-F(a))/(b-a), and

    e_L(a,b) = max_{p in [a,b]} [F_L(p)-F(a)-(p-a)s].

Claim: e_L is the minimum, over actual rank-r orthogonal projections, of the
larger endpoint regret at site L. Then the best common-preset endpoint loss is
min_L e_L(a,b). Site independence is required for this last minimum identity.

Proof route: relax P to the fantope {0<=P<=I, tr P=r}. Convex minimax gives
the displayed maximum of the sum of r smallest eigenvalues. At its maximizing
p, all strict low eigenvectors are fixed, and only a possible eigenvalue tie
at the rank cutoff remains. On that tied eigenspace, the attainable trace of
C_L over rank-k projections fills the interval between the sums of its k
smallest and k largest eigenvalues. At an interior optimum s-d_L belongs to
this interval after subtracting the fixed contribution. Choose a projection
with that trace: its endpoint regrets are equal and attain the dual value.
At a boundary maximum choose the appropriate extreme trace, giving an
endpoint-optimal projection with no larger regret at the other endpoint.
This constructs a pure projection, rather than a randomized mixture.

Explicit interpolation: diagonalize C_L in the tied eigenspace. The k-low
and k-high coordinate subspaces share some columns. Pair their nonshared
columns and replace each low column e_i with sqrt(1-t)e_i+sqrt(t)e_j.
All columns remain orthonormal; their total cost interpolates linearly.
Any intermediate cost is attained for one t in [0,1].

For a=b select any globally optimal subspace at a, giving zero regret.

## Consequence and limits

For positive tolerance, the farthest feasible endpoint and greedy interval
cover determine the minimum menu cardinality, by the existing compactness and
exchange proof. Outer tolerance search determines the finite-K minimax value.
This is an exact-real characterization, not a finite-precision certificate or
a claim of polynomial bit complexity near arbitrary eigenvalue collisions.

For a given numerical menu, eliminate sites once per subspace. Its objective
is a finite lower envelope of affine lines. Checking domain endpoints and
line-envelope breakpoints gives its continuous maximum regret. For a lower
bound, K+1 ordered prices with each adjacent pair incompatible suffice; scalar
dual evaluations can support the incompatibility without recovering a preset.

Numerical implementation must record primal upper versus dual lower gaps,
detect failure to close them, and not silently treat near ties as exact ties.
Rayleigh residuals/interval eigenvalue bounds would be needed for formal
floating-point certification. Initial development uses double precision and
explicitly labels its bounds as numerical.

Unresolved contribution question: this composes established ingredients. Its
practical utility and difference from existing continuum minimax approximation
algorithms must be established by the planned comparisons before promotion.
