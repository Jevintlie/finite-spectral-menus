# Focused proof and priority audit — 11 October 2026

This is a documented internal audit, not external peer review or a proof of
worldwide priority. It supersedes the literature-access limitation in
`STRUCTURAL_REVIEW.md`. The complete Diakonikolas thesis was obtained from
Columbia and its relevant definitions, algorithms, and proofs were inspected.
Benchmark expansion was frozen. No performance result is added by this audit.

## Decision and residual contribution

Proceed with a modest structural optimization submission, subject to the
author's final review and accurate submission declarations. The results checked
do not supply the precise combination of an all-subinterval missing-slope
criterion, explicit spectral face intervals, and an additive repair count by
exceptional prices. This is evidence for that narrowly stated contribution,
not evidence for a new general duality or representative-set principle.

The strongest hostile interpretation remains plausible: the geometric results
are elementary refinements of known exposed-face and approximation arguments.
The paper should be judged on the usefulness of this characterization for
spectral presets, its sharp model realizations, and its verifiable construction.
A referee may find that insufficiently significant for a particular journal.
No numerical score or acceptance probability is assigned.

The distinction between convex evaluation of a chosen menu and feasibility of
its chosen representatives is essential. For every fixed menu, minimizing a
linear functional over its convex hull equals minimizing it over the menu.
Thus saying that older work "allows mixtures" does NOT by itself distinguish
our problem. The revised Appendix D states this identity explicitly.

## Search and source coverage

Searches covered supported/unsupported bicriteria solutions, compact affine
families and lower envelopes, convex Pareto approximation, fixed-cardinality
regret sets, tangent replacement, finite adaptability, min–max–min robustness,
policy-count bounds, joint numerical ranges, and analytic spectral branches.
The search included work published through the session date, including Kurtz
(2026). Citation tracing was used in addition to searching our terminology.

Local research copies are in `resources/priority_20261011/`; they are excluded
from distributable archives. The distributable source manifest records their
URLs, hashes, and the passages checked in
`results/publication_audit_v6/literature_sources.json`. Downloading a source
does not mean every page was audited; the passage field states the actual scope.

| Primary source and passages inspected | Consequence for this paper |
|---|---|
| Diakonikolas (2011), Chapter 4 definitions and Remark 4.3.2; Chapter 5 §§5.1–5.3, particularly §5.2.2, Theorems 5.3.2–5.3.5, Remark 5.3.6. [Columbia thesis](https://academiccommons.columbia.edu/doi/10.7916/D80K2GR9) | The distinction between feasible and convexified representatives, usefulness of non-extreme/unsupported points, cardinality factors, and recovery limitations are established. Do not claim the general phenomenon in Proposition 1 as new. The read results concern multiplicative approximation and oracle/cardinality complexity, not our explicit all-interval equality criterion or exceptional-price count. |
| Bazgan et al. (2022), Proposition 1, Theorem 2 and its sharpness discussion; Helfrich et al. (2024), Definitions 2.13–2.15 and Theorems 4.4, 5.5. [Bazgan](https://doi.org/10.1007/s00224-021-10066-5), [Helfrich](https://doi.org/10.1007/s00186-023-00823-2) | Weighted-sum approximation and the distinction between all supported solutions and a chosen optimizer per weight are prior art. The factor-two endpoint bound is an elementary specialization. Retain spectral sharpness, not a general scalarization novelty claim. |
| Magnanti–Stratila (2012), §2.1, Lemma 2 and proof. [Preprint](https://arxiv.org/abs/1201.3148) | Tangent replacement with bounded cardinality is prior art. Our refinement charges only missing-slope prices and preserves the additive tolerance. Changing the metric alone is not sufficient originality. |
| Hanasusanto–Kuhn–Wiesemann (2015), Theorem 1 and electronic-companion proof; Buchheim–Kurtz (2017), §2, Lemma 1, Corollary 1, §3. [Hanasusanto](https://doi.org/10.1287/opre.2015.1392), [Buchheim](https://doi.org/10.1007/s10107-016-1053-z) | Convex combinations, minimax swaps, and finite-policy recovery already underlie robust optimization. Their convex uncertainty assumptions do not hold after the regret lift in general. Appendix D gives an explicit countercheck rather than asserting disjointness from titles alone. |
| Kurtz (2026), definitions and §§3–4, especially Theorems 2, 7 and recourse-stability assumptions. [Publisher full text](https://doi.org/10.1007/s10107-026-02329-1) | The objective-uncertainty results require concavity in uncertainty; our regret is convex. The constraint-uncertainty framework uses bounded integer recourse and stability regions, not the continuum of projectors. The policy-count problem is relevant prior work but these stated results do not directly imply the missing-slope repair. |
| Cardinal–Goaoc–Wajsbrot (2025), §§1–4, especially §4.2, Lemmas 4.2–4.3 in the arXiv version. [Full text](https://arxiv.org/html/2504.16642v1) | The farthest-reach greedy characterization has a direct predecessor. It is explicitly attributed next to our theorem; their polyhedral-input complexity is not claimed for spectral input. |
| Tantipongpipat et al. (2019), Theorems 1.2–1.3; Shen et al. (2026), Theorem 4.1 and Appendix A.3. [Tantipongpipat](https://arxiv.org/abs/1902.11281), [Shen](https://doi.org/10.1007/s10543-026-01109-9) | Two-criterion subspace optimization, scalar spectral search, and tied-eigenspace recovery are prior art. Our direct face proof specifies the exact oracle and real-projector recovery, including low dimensions. |
| Barbarino–Noferini, published 2023 version, Theorem 1.1. [Article](https://doi.org/10.1016/j.laa.2023.04.022) | Rellich's analytic parameterization is an established input, not a new finiteness theorem of perturbation theory. The reference was updated from preprint metadata. |

The thesis's extreme convex-Pareto representatives and our set of ALL tied
globally optimal presets must not be conflated. Our separation checks the
larger latter set. The cited sources are compared by their assumptions and
conclusions; absence of our exact wording in search results is not the test.

## Proof audit

The statements below use stable LaTeX labels because the theory-first
reorganization changes theorem numbers (v5 exactness/repair 6/8 become 4/6).
All were checked against the actual source, not only the feedback summary.

| Statement | Adversarial check and outcome |
|---|---|
| Affine reduction (`eq:regret`) | Sharing A and restricting p to nonnegative values permits one cheapest site for a fixed projector. This would fail with general site-dependent rewards or negative prices. The exclusions remain explicit. |
| Compactness and attainment | Rank-r real projectors form a compact set; min of finitely many continuous costs is continuous. The globally optimal relation in projector × price space is closed and compact. Its projection, the coefficient image, and its finite-dimensional convex hull are compact. All three finite-K optima are attained. |
| Separation (`prop:separation`) | Re-derived the piecewise objectives in t. Model S gives 1/2; M gives 3/4. At its tie, M has only the two coordinate optima, so allowing every tied optimizer does not remove the example. This is a spectral realization, not a new abstract information-loss principle. |
| Relaxed oracle (`lem:relaxation`) | Chord error bounds every dominating affine line from below. Interior derivative bounds permit two active slopes with the required convex combination. At each domain boundary, the one-sided derivative chooses the correct extreme slope. If the chord error is zero the argument still applies. |
| Factor two (`thm:factor`) | At a segment midpoint the two nonnegative endpoint regrets sum to twice its chord error. Neither endpoint can exceed this sum. An interval cover can be chained with at most K positive-length pieces; redundant singleton pieces can be discarded by closedness and finite coverage. No division by zero regret is used. |
| Sharp family (`eq:kappa`) | For kappa>2 the minimum endpoint loss is 1−1/kappa and restricted loss is 1. The limiting ratios use opposite ends of kappa's range. At kappa=2 the tied feasible family changes; no false continuity assertion is made. |
| Exactness, sufficiency (`thm:exactness`) | A complete active slope interval supplies a pure preset at the chord slope. Endpoints already need only one preset. Applying the construction on each relaxed covering segment proves equality for every budget. Values from F alone do not identify projector matrices. |
| Exactness, necessity | A missing slope lies strictly between finite left/right derivatives, since the active slope set is compact and contains its extremes. Secant continuity constructs an interval straddling that price with exactly this chord slope. Positive endpoint weights force equality and the forbidden active slope if actual error equaled relaxed error. Compact attainment upgrades nonattainment of equality to a strict gap. Quantifier: every subinterval, not one chosen budget/domain. |
| Spectral face union (`eq:unionfaces`) | The low eigenspace is fixed; rotating disjoint low/high compression eigenvectors realizes every intermediate cutoff trace with a real orthogonal projector. At p>0 an active-site minimizer cannot have a cheaper site. At p=0 that last argument is invalid; the union formula remains restricted to interior prices. |
| Repair (`thm:repair`) | The minimum of two actual affine lines lies below their convex combination pointwise. A two-line repair is charged to a missing-slope price strictly inside the served segment. Disjoint interiors charge each price at most once, even if a price has several missing slope intervals. Deterministic selection after price observation is sufficient. |
| Finiteness | Rellich applies on an open neighborhood of the whole compact price interval. Each rank-r sum is one of finitely many analytic branch sums. Remove identical functions before using isolated zeros; this handles persistent ties. Pairwise nonidentical analytic differences have finitely many zeros on that compact interval. Differentiable prices cannot have missing slopes. No computable small or polynomial q bound follows from this proof alone. |
| Cardinality/asymptotics | Positive tolerance admits a finite cover by compactness or the uniform slope bound. Apply repair with K−q and repeat presets if necessary. A fixed integer shift preserves an already-established positive c K^(−alpha) law. No universal exponent, finite-K relative closeness, or finite-zero-regret limit by division is inferred. |
| Endpoint oracle (`thm:endpoint`) | Re-derived weak duality, cutoff cost extremes, real rotations, both boundary cases, and interchange with finite site choice. Coincident eigenvalues and r=n do not break recovery. This remains attributed prior methodology. |
| Covering (`thm:greedy`) | Compactness attains the farthest reachable endpoint; monotonicity plus a finite interval chain proves equivalence, including zero tolerance and repeated presets. A real-arithmetic characterization does not imply a finite-precision or bit-complexity guarantee. |
| Certificate (`prop:certificate`) | Convex regret extends endpoint upper bounds. Every adjacent witness pair has all-site weak-dual lower bounds. Interval acceptability then excludes all nonadjacent pairs too, so K+1 witnesses cannot be served by K presets. |
| Interval appendices | Congruence Rayleigh-quotient bound requires Gram deviation <1; polar correction bounds the actual projector. Unpivoted band/Sturm inertia accepts only nonzero enclosed pivots, rejects uncertain signs, and checks ordered eigenvalue counts rather than trusting partial Ritz ordering. The IEEE arithmetic assumptions and lack of formal software verification remain stated. |

No mathematical counterexample or unresolved logical gap was found in these
checks. That statement reports this audit's outcome; it is not an independent
certification of every proof. Existing exact examples and saved outward
certificates supplement the reasoning. Numerical agreement is not substituted
for any proof.

## Changes made because of the audit

- Put structural theory before construction and define e(a,b) before first use.
- Explicitly identify the compact-affine scope and the model-specific content.
- State the distinction between curve-only values and actual projector recovery.
- Attribute the broader convex-Pareto obstruction and robust-policy precedents.
- Add the same-menu convex-hull identity and a concrete failed uncertainty lift.
- State necessity of one extra preset in the q=K=1 case without claiming
  unproved sharpness for every q and K.
- Retain all numerical evidence in an appendix, with a concise main-text account
  that includes slowdowns and limits. No extra performance experiments.
- Update bibliographic metadata and show persistent links in the PDF.

## Submission decision

Journal of Global Optimization is the selected preparation target: its official
scope includes global, robust, multiobjective optimization and computational
geometry. This is a scope match, not an assurance that the editors will judge
the residual contribution sufficiently significant. The pitch is an exact
realizability characterization and exceptional-price cardinality refinement,
supported by reproducible global certificates. It is not a superior universal
optimizer, a hardware study, or a cognitive theory.

The release must still pass its current build, clean-extraction, evidence,
rendering, and packaging gates; see the v6 completion record for those outcomes.
Author placeholders are retained by explicit request. Actual upload requires
the human author to replace identity/declaration fields, review the work, and
make the license/account choices. No external submission is made by this audit.
