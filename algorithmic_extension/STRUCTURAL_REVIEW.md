# Structural revision: proof and contribution audit

4 October 2026. Current manuscript: **Finite Menus of Spectral Subspaces:
Exactness, Approximation, and Verifiable Construction**. The 11-page v2
release is preserved. The new structural section is `manuscript/structural_theory.tex`.
This is an internal audit, not an independent referee report.

## What changed scientifically

The earlier same-curve counterexample is now part of a quantitative account:

1. Convexification gives a curve-only lower bound. Midpoint scalarization
   bounds the regret of a supported menu by twice that lower bound.
2. One spectral family with unchanged F realizes every one-preset regret
   between 1/2 and 1. It makes both derived factor-two comparisons sharp
   uniformly over budgets (already at K=1).
3. Equality of actual and relaxed endpoint values on EVERY subinterval is
   equivalent to completeness of the available globally optimal slopes.
   In this model, those slopes are a finite union of cost intervals of
   active spectral faces. Single-site instances always pass the criterion.
4. A relaxed K-menu can be repaired using at most K+min(K,q) globally optimal
   presets, where q counts prices with missing slopes. Analytic spectral
   parameterization proves q finite for every fixed instance.
5. The same finite cardinality shift transfers an established positive
   power-law leading asymptotic. No new inverse-square law is claimed.

The contribution is the combined structural characterization and its spectral
specialization. Factor-two scalarization, convexification, two-point exposed-face
representation, and interval covering are standard ingredients. No fundamental
new convex-duality principle or established physical application is asserted.

## Proof audit

| Statement | Key check | Outcome |
|---|---|---|
| Compact optima | Continuous coefficient map on compact rank-projector set; compact convex hull in R^2; globally optimal set is projection of closed relation on compact product | Attainment justified, including restricted and relaxed menus |
| Relaxed endpoint oracle | Any relaxed line dominates F; at a dual optimum mix two active slopes, or take an extreme slope at a boundary | Primal and dual values agree; boundary prices handled |
| Factor two | Nonnegative endpoint regrets of midpoint optimum sum to twice midpoint chord error | Applies also when relaxed error is zero |
| Sharpness | Piecewise endpoint objective in t; optimizer t=1/kappa; global optimal set contains only coordinate projectors for kappa>2 | Exact algebra; tie-set discontinuity at kappa=2 explicitly noted |
| Necessity of slope completeness | A missing slope lies strictly between one-sided derivatives; secant continuity constructs arbitrarily short intervals with that chord slope | Positive endpoint weights force a forbidden active slope if equality held |
| Spectral slope union | Fixed low eigenspace plus cost-compression rank completion; active-site projector must use a cheapest site when p>0 | Actual pure projectors fill each interval; raw-site union not asserted at p=0 |
| Additional-preset bound | Lower envelope of two active lines lies below their mixture; each two-preset repair has a bad price in the segment interior | Disjoint interiors permit charging each price only once |
| Finite q | Rellich gives analytic eigenvalue branches on a neighborhood of the whole compact interval; finitely many r-fold sums; distinct analytic functions have finitely many intersections there | No assertion of an efficient enumeration or polynomial bound |
| Asymptotic transfer | bar(E)_K <= E_K <= E_K^G <= bar(E)_(K-q) | Valid for a separately established c K^(-alpha), c>0, alpha>0; not for zero-error finite menus via division |

Important logical boundary: absence of slope gaps is equivalent to endpoint
relaxation exactness on every subinterval. It is NOT necessary for equality
of a fixed-domain one-menu problem or for supported presets alone to be
optimal. Explicit counterchecks protect both distinctions.

## Primary-source comparison

- Bazgan, Ruzika, Thielen, Vanderpooten (2022), *The Power of the Weighted
  Sum Scalarization for Approximating Multiobjective Optimization Problems*,
  DOI https://doi.org/10.1007/s00224-021-10066-5.
  Publisher text and author/arXiv version inspected. Their positive-objective
  Pareto approximation results establish the relevance of supported-solution
  bounds. Our elementary two-endpoint factor is not positioned as a new
  general scalarization principle. The manuscript's specific quantity is
  additive regret with a fixed menu budget over a restricted weight interval.
- Magnanti and Stratila (2012), *Separable Concave Optimization Approximately
  Equals Piecewise-Linear Optimization*, https://arxiv.org/abs/1201.3148.
  Full HTML inspected, especially Lemma 2: arbitrary multiplicative
  approximating pieces can be replaced with tangents at a bounded cardinality
  cost. This precedes the general replacement idea. Here the repair counts
  missing-slope prices and retains the same additive regret tolerance.
- Diakonikolas and Yannakakis (2008), *Succinct Approximate Convex Pareto
  Curves*, https://www.cs.columbia.edu/~ilias/papers/convex-pareto.html.
  Author abstract and university publication record inspected. Exact Comb
  yields minimum size in the convex case and a factor-two cardinality
  approximation in the discrete case. This is explicitly cited as prior
  representative-set work. Full conference PDF and thesis retrieval returned
  access errors; no claim of exhaustive theorem-by-theorem exclusion is made.
- Barbarino and Noferini (2022), https://arxiv.org/abs/2211.15539.
  Full PDF inspected at Theorem 1.1, which states Rellich's analytic
  diagonalization on an open real interval. This supplies the established
  regularity theorem used for finiteness; the paper does not invent it.
- The earlier fair-PCA, greedy-cover, verified-spectrum, and scalar-asymptotic
  comparisons remain in `LITERATURE.md` and the manuscript.

Targeted searches did not identify the manuscript's precise slope-completeness
equivalence and additive missing-price count as a stated result in the sources
inspected. This is limited evidence for positioning, not proof of worldwide
priority. A referee may regard the characterization as an elementary
consequence of known geometry. The text therefore states and proves the
result directly without claiming a breakthrough or first-ever principle.

## Numerical evidence

`python check_structural_theory.py` writes `results/structural_theory_v1.json`.
It checks 12 kappa cases with outward bounds and exact rational comparison,
54 numerical endpoint cases, a one-site complete corner, two multi-site
active-face configurations, three local counterchecks, and a two-gap example.
The 54 diagnostics are not interval certificates and are not added to the
54 historical saved-menu certificate artifacts. These checks support the
proof audit; numerical agreement alone cannot establish a theorem.

One initial development run failed on treating a result dictionary as a scalar;
the checker was corrected to read its `value` field. This did not change any
solver or benchmark result. Solver/core files used by frozen timing studies
remain unchanged, as checked by `audit_results.py`.

## Remaining completion gates

The mathematics and manuscript are integrated. Before completing this revision,
rebuild and inspect the current PDF, run the evidence audit, update the reader
documentation, package a new release, and validate it from clean extraction.
The v2 validation report does not validate this new manuscript. Author and
affiliation placeholders remain as explicitly requested by the user.
