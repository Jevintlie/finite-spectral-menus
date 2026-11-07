# Structural theory beyond the single counterexample — working derivation

Historical derivation. The current proofs are integrated in
`manuscript/structural_theory.tex`; `STRUCTURAL_REVIEW.md` records the
subsequent audit, tests, attribution, and limitations. In particular,
finiteness of q is now proved using analytic spectral parameterization.
The open-check list below records the starting state, not the current status.

4 October 2026. New research phase after the significance critique. These
statements need literature comparison, proof audit, and manuscript integration.
They are not yet claims of priority. The earlier eleven-page release remains
preserved. Standard ingredients include convexification, two-objective weighted
scalarization, exposed faces, and interval covering.

## Definitions

Use the shared-A, scalar nonnegative-price spectral model from
END_TO_END_PROOF.md. Let L be its compact set of effective affine preset lines
ell_P(p)=alpha(P)+p c(P). Let G be the compact set of presets that minimize
the global objective at at least one price in [0,B], including all ties.

E_K is the optimum using K arbitrary presets. E_K^G restricts all presets to G.
bar(E)_K allows each preset line to be any convex combination of lines in L.
It is a mathematical convexification, not an implementable orthogonal preset.
All three optima exist. Convexifying the line family leaves F unchanged.

For [a,b], let D(a,b)=max_[a,b] (F(p)-chord_[a,b] F(p)). This is the exact
endpoint minimax value for the convexified line family. Weak minimax duality
gives the lower bound; the exposed-face slope construction below gives equality.
Therefore greedy interval covering with oracle D computes bar(E)_K in exact
real arithmetic, using F alone.

## A. A uniform factor-two sandwich

Candidate theorem, with a direct proof:

    bar(E)_K <= E_K <= E_K^G <= 2 bar(E)_K.                 (A)

Take an optimal relaxed K-menu and a partition into at most K intervals it
covers at tolerance bar(E)_K. Such a partition exists because each relaxed
line has convex regret and its acceptable set is an interval. On [a,b], pick
ANY globally optimal preset at the midpoint q=(a+b)/2. Its two nonnegative
endpoint regrets sum to 2F(q)-F(a)-F(b). A relaxed line covering both endpoints
at epsilon has average endpoint regret <=epsilon, so this sum is <=2epsilon.
Each endpoint regret is therefore <=2epsilon, and convexity covers the whole
interval. Do this once per segment. This proves the last inequality; the
first two are inclusions of feasible families. Zero-regret cases also work.

Consequences: all globally supported presets give a factor-two approximation
to the unrestricted optimum; the scalar curve gives a lower bound within a
factor of two of the true optimum. This two-endpoint rounding argument is an
elementary weighted-scalarization principle, not a new general principle.

## B. One family makes both ratios sharp

Let n=2, r=1, B=1, A=diag(1,0), d=0, and

    C_1=2 I, C_2=diag(kappa,0), kappa>2.

For every kappa, F(p)=min(-1+2p,0). With t=u_1^2, the effective line is
-t+p min(2,kappa t). The best one-preset endpoint maximum is

    E_1 = 1-1/kappa,   attained at t=1/kappa.

Proof: if t<=2/kappa, endpoint regrets are 1-t and (kappa-1)t, whose maximum
is minimized at 1/kappa. If t>=2/kappa, the second regret is 2-t and its
minimum on this region is 1. The first region's value is smaller than 1.

All global optima are the two coordinate projectors (including at p=1/2),
so E_1^G=1. The convexified optimum is bar(E)_1=1/2. Hence

    E_1 / bar(E)_1 = 2-2/kappa -> 2 as kappa -> infinity,
    E_1^G / E_1 = kappa/(kappa-1) -> 2 as kappa -> 2 from above.

Thus neither universal multiplicative factor in (A) can be improved. The
same F realizes every E_1 in (1/2,1), in addition to the single-site model
C=diag(2,0) which has E_1=1/2. Positive definite shifts preserve all regrets.
Sharpness here is for the universal constant across budgets (already K=1),
not a claim of a separate sharp example for every fixed K>1.

## C. When the curve relaxation is exact

For an interior price p define the set of slopes of globally optimal presets

    S(p) = {c(P): ell_P(p)=F(p)}.

The superdifferential of F is [min S(p),max S(p)]. Call p a slope-gap price
when S(p) is not that complete interval. For the spectral model S(p) is a
finite union of closed intervals: for each active site L, compress C_L to
the cutoff eigenspace of -A+p C_L. Its attainable rank-completion costs fill
an interval I_L(p), and S(p) is the union of I_L over active sites. Since
p>0, any branch-minimizing projector at an active site also has that site as
a cheapest site; otherwise its effective objective would be below F.

Candidate exactness characterization:

    e(a,b)=D(a,b) for every subinterval [a,b] of [0,B]
    iff S(p) has no gaps at every interior p.               (C)

Sufficiency: maximize F(p)-sp for the chord slope s. At an interior maximizer,
s is in the superdifferential; completeness supplies a global preset of slope
s and both endpoint regrets D. At a boundary maximizer, a global extreme
slope supplies an endpoint-dominating preset. This handles ties and corners.

Necessity: choose a missing s strictly between the extreme slopes at a gap
price p*. Choose a<p*<b arbitrarily close so the chord slope is exactly s.
Existence follows from the one-sided derivatives and continuity of secants:
fix a=p*-h and vary b from p* to p*+R h for a sufficiently large fixed R,
then take h small. The chord slope starts above s and ends below s.
The strict derivative jump around s makes p* the unique scalar maximizer.
If some actual preset attained e=D, its weighted endpoint regrets at p*
would equal D; nonnegativity of the endpoint weights forces both endpoints
to equal D. That preset would be global at p* with slope s, a contradiction.
Compactness makes the inequality strict, rather than merely unattained.

This is an equivalence for exactness of the curve relaxation on EVERY
subinterval. Do NOT replace it by an equivalence for supported presets being
optimal: a slope gap can have e^G=e>D on short intervals. The original
two-site example on a short interval around 1/2 demonstrates that distinction.

Corollaries: a single site has no slope gaps, even at eigenvalue collisions;
if F is differentiable throughout the interior, there are no gaps either.
In both cases E_K=E_K^G=bar(E)_K for every K. More generally, tied active sites
are harmless when their cost intervals overlap enough to fill the global
superdifferential. A corner is not by itself an obstruction.

## D. Additive preset-budget repair

Assume there are q slope-gap prices in (0,B), with q finite. Then

    E_{K+min(K,q)}^G <= bar(E)_K <= E_K.                    (D)

At a relaxed endpoint optimizer with dual price p*, its supporting line is
realizable by one global preset unless its required slope lies in a gap of
S(p*). In that case bracket the slope by two members of S(p*). Their affine
lines agree with F at p*, and a convex combination has the required slope.
The lower envelope of these TWO globally supported lines is no greater than
their convex combination at any price, so the two presets cover the original
segment at the same tolerance. This is deterministic selection from a menu,
not randomized measurement.

Repair each interval of an optimal relaxed K-cover. A repair requires a
slope-gap price strictly inside its segment; endpoint maxima need one preset.
Disjoint segment interiors cannot charge the same price twice. Thus at most
min(K,q) repairs are needed. Without any finiteness assumption this still
gives E_{2K}^G<=bar(E)_K.

For minimal cardinalities at any positive tolerance, the corresponding claim
is N_rel <= N_actual <= N_G <= N_rel+min(N_rel,q). This provides a tolerance-
independent upper bound q on the excess size of a globally supported menu.

Finiteness of q for finite affine symmetric pencils should be justified
explicitly (e.g. semialgebraicity or analytic eigenvalue branches), not assumed
from a plot. No polynomial bound on q or its computation is claimed here.

If bar(E)_K is regularly varying as c K^(-alpha), c>0, alpha>0, fixed finite q
gives bar(E)_K <= E_K <= bar(E)_(K-q) for K>q, so E_K/bar(E)_K -> 1.
This transfers an ESTABLISHED asymptotic law; it is not a newly invented rate.

## Open research checks

1. Audit all compactness, endpoint, and exactness-necessity arguments.
2. Identify direct predecessors for two-objective scalarization bounds,
   supported/unsupported solution approximation, and menu-size repair.
3. Test the kappa family with existing optimizer and independent interval
   bounds; test single-site exactness, nonsmooth completeness, and slope-gap
   intervals where supported sufficiency and relaxation exactness differ.
4. Decide whether the combined sharp information-loss and finite-budget result
   adds a useful contribution beyond known general representative-set theory.
5. Only then integrate into LaTeX, retaining the original analytic/asymptotic
   material where it supports the new results instead of padding page count.
