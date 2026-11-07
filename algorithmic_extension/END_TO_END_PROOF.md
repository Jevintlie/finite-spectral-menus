# Exact-real finite-menu characterization and checkable bounds

This document supplies complete arguments for the model-specific composition.
Two-objective spectral optimization and rank recovery are established in the
fair-PCA literature (Tantipongpipat et al., 2019; Shen et al., 2026). Greedy
interval covering and weak dual certificates are also established ideas. The
intended contribution is their constructive use for this finite-menu problem,
its implementation, and its measured and independently verified behavior.

## 1. Model and basic geometry

Let A,C_1,...,C_m be real symmetric n by n matrices, m>=1, 1<=r<=n,
B>0, and d_1,...,d_m be finite real numbers. Positive semidefinite matrices
and nonnegative overheads give the intended resource interpretation; the
following arguments do not need positivity of the matrices or overheads.
The price domain [0,B] and the shared task matrix A are essential assumptions.
Let G_r be the compact set of rank-r orthogonal projectors. Define

    a(P)=-tr(AP), c_L(P)=tr(C_L P)+d_L,
    c(P)=min_L c_L(P), J(P,p)=a(P)+p c(P),
    F_L(p)=sum_{j=1}^r lambda_j(-A+p C_L)+p d_L,
    F(p)=min_L F_L(p)=min_{P in G_r} J(P,p).

Eigenvalues are in increasing order. The last equality follows from the
minimum trace principle. For p>=0, min_L(a(P)+p c_L(P))=J(P,p); a site
minimizing c_L(P) works at every price. Thus J is affine in price, and F is
a finite-valued continuous concave function: it is the infimum of a compact
family of affine functions with bounded slopes. Define R(P,p)=J(P,p)-F(p).
It is nonnegative, continuous in (P,p), and convex in p.

For a menu Q=(P_1,...,P_K), let E(Q)=max_{p in [0,B]} min_i R(P_i,p).
The optimal value E_K=min_{Q in G_r^K} E(Q) exists by compactness and
continuity. Allowing repeated projectors makes this equivalent to at most K
presets. K counts projectors/subspaces, not r times K individual channels.

For any epsilon>=0 the acceptable set {p:R(P,p)<=epsilon} is a closed
interval, possibly empty or a singleton. Consequently one preset is
acceptable on [a,b] if and only if it is acceptable at a and b.

## 2. Endpoint oracle with recovery of an actual projector

For a<b, set f_a=F(a), f_b=F(b), s=(f_b-f_a)/(b-a). At one site define

    e_L(a,b)=min_{P in G_r} max(a(P)+a c_L(P)-f_a,
                              a(P)+b c_L(P)-f_b).

Then

    e_L(a,b)=max_{p in [a,b]} [F_L(p)-f_a-(p-a)s].             (1)

Proof. For any P and p in [a,b], the convex combination of the two endpoint
regrets with weights (b-p)/(b-a) and (p-a)/(b-a) is
a(P)+p c_L(P)-f_a-(p-a)s. It is at most their maximum. Minimizing over P
gives the right side of (1) as a lower bound.

To attain it, choose a maximizer p*. Let V_< span all eigenvectors of
H=-A+p*C_L whose eigenvalues are strictly below lambda_r(H), and V_= span
its cutoff eigenspace. Every trace-minimizing projector at p* contains V_<
and chooses k=r-dim(V_<) dimensions inside V_=; no other projector minimizes
the trace. If D=V_=^T C_L V_= has eigenvalues mu_1<=...<=mu_q, the minimum
and maximum c_L on this minimizing face are

    c_- = tr(V_<^T C_L V_<)+d_L+sum_{j=1}^k mu_j,
    c_+ = tr(V_<^T C_L V_<)+d_L+sum_{j=q-k+1}^q mu_j.

Every intermediate cost is realized by an actual projector. In a D-eigenbasis,
retain the common coordinates of the k-low and k-high index sets; pair the
remaining low and high coordinates. For each pair i,j use
sqrt(1-t)e_i+sqrt(t)e_j, with the same t in [0,1]. These columns have disjoint
supports, are orthonormal, and their total cost is (1-t)c_-+t c_+.

The right and left derivatives of F_L at p* are respectively c_- and c_+.
This follows by taking directional minima over its compact minimizing face
in the affine-envelope representation. At an interior maximum of the scalar
function in (1), c_-<=s<=c_+. Choose a face projector with c_L=s. Its
two endpoint regrets are equal to the dual value at p*, proving equality.
If p*=a, the right derivative is nonpositive, so c_-<=s. Choose the minimum
cost face projector. Its regret at b is its regret at a plus
(b-a)(c_--s), hence is no larger. Its regret at a equals the dual value.
If p*=b, the left derivative is nonnegative, so c_+>=s; choose the maximum
cost face projector and reverse the argument. This proves (1), including
ties, full rank, and boundary maximizers, without randomizing projectors.

The unrestricted common-preset endpoint loss is

    e(a,b)=min_L e_L(a,b).                                  (2)

Indeed each P has one cost-minimizing site valid at both endpoints, so its
effective maximum endpoint regret equals the minimum over L of its site
maximum. The two minima over P and finite L commute. Convexifying across
different sites before solving (1) would not be justified; the structural
example in STRUCTURAL_EXAMPLE.md exhibits a strict relaxation gap.
For a=b, e(a,a)=0, realized by a globally optimal projector at a.

## 3. Exact-real greedy covering

For epsilon>=0 and x in [0,B], let

    T_epsilon(x)=max{y in [x,B]:e(x,y)<=epsilon}.

The maximum exists: the feasible pairs (P,y) form a nonempty compact set,
because a price-optimal P is feasible at y=x. For x<=x', T(x')>=T(x):
if T(x)>=x', the preset witnessing [x,T(x)] witnesses [x',T(x)]; otherwise
T(x')>=x'>T(x).

Set g_0=0 and g_j=T(g_{j-1}), taking T(B)=B. Then E_K<=epsilon if and
only if g_K=B. The forward construction immediately supplies a covering menu
when g_K=B. Conversely, acceptable intervals of any feasible K-menu cover
[0,B]. From this finite interval cover one can extract a chain of at most K
intervals with consecutive intervals overlapping, starting at zero and
ending at B. Its reachable endpoints x_j obey x_j<=T(x_{j-1}). By induction
and monotonicity of T, x_j<=g_j, so g_K=B. A singleton can be discarded
unless the entire domain is a singleton, excluded by B>0; finite closed
intervals cannot cover a nonempty gap between chain members.

For epsilon>0 progress is uniformly positive away from B. All c(P) lie in
a bounded interval [c_min,c_max]; F is Lipschitz with slopes in that interval.
A preset optimal at x has regret at y at most
(c_max-c_min)|y-x|. Thus T(x)>=min(B,x+epsilon/(c_max-c_min)) when the
denominator is positive. If it is zero, any price-optimal preset is globally
optimal and one preset suffices. This ensures a finite cover for positive
tolerance; it is not a bit-complexity bound for nested numerical root solves.

This gives the exact-real minimum cardinality and a monotone decision
characterization of E_K. The supplied floating implementation uses finite
price and objective tolerances: its outer search lower estimate is not an
outward-rounded bound. Finite-precision global claims require Section 5.

## 4. Reusing supporting lines and spectral samples

A stored projector with line alpha+p c_L provides, for every [a,b], the
valid primal upper bound max(alpha+a c_L-F(a),alpha+b c_L-F(b)) on e_L.
A stored branch value F_L(q) with q in [a,b] supplies the weak-dual lower
bound F_L(q)-F(a)-(q-a)s. Minimize cached primal bounds and maximize eligible
dual bounds. If the upper is <=epsilon or the lower is >epsilon, that site's
decision needs no further spectral evaluations. For the minimum over sites,
one feasible site suffices; exclusion requires every site's lower bound.

A minimizing projector at q provides a supergradient c_L of concave F_L.
If c_L>s, no maximizer of F_L(p)-sp lies strictly to the left of q; if
c_L<s, none lies strictly to the right. To see the first claim, for p<q
the supergradient inequality gives F_L(p)-sp <= F_L(q)-sq+(c_L-s)(p-q),
which is strictly smaller. The second is symmetric. Intersect these half
intervals with [a,b] to bracket subsequent searches. These are standard
supporting-line bounds; their use here is an acceleration, not new duality.
In floating point, inverted brackets are discarded and actual objective
gaps are checked. Those checks alone are numerical, not interval certificates.

## 5. Independent finite certificates

An upper certificate consists of K actual projectors and a partition
0=a_0<=a_1<=...<=a_K=B such that the i-th projector's regret is <=U at
a_{i-1},a_i. Convexity proves E_K<=E(Q)<=U.

A lower certificate consists of K+1 increasing prices x_0<...<x_K in
[0,B]. For each adjacent pair and every site give any q_L in that pair.
By the lower-bound part of (1),

    min_L {F_L(q_L)-chord[F(x_i),F(x_{i+1})](q_L)} > ell

implies that no preset has regret <=ell at both adjacent prices. By interval
convexity no preset can serve any two of the K+1 prices: serving a nonadjacent
pair would also serve the intervening adjacent pair. The pigeonhole principle
therefore excludes every menu of K presets, so E_K>ell. Together these give
ell<E_K<=U. This argument does not trust the optimizer that proposed the menu
or the witness prices, and it does not assume that the search found an optimum.

For binary64 matrices, the separate verifier interprets a stored full-rank
basis U as its exact polar-normalized projector, encloses its traces and all
needed spectral sums with outward interval arithmetic, and checks the above
inequalities. Its arithmetic contract and eigenvalue/trace enclosure proofs
are in CERTIFICATE_DERIVATION.md. These are mathematical certificates under
that contract; neither software formal verification nor external auditing is
claimed. Certificate generation may fail even when a numerical menu is good.

For ordinary numerical evaluation of an actual menu, each preset contributes
one effective affine line. Partition [0,B] at all their pairwise crossings.
On every resulting interval the minimum line is fixed, so the regret is
convex there. Evaluating the domain endpoints and crossings therefore gives
the continuous maximum; an arbitrary price grid is unnecessary.
