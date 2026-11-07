# Scientific claim audit

## Current structural revision

The current title is **Finite Menus of Spectral Subspaces: Exactness,
Approximation, and Verifiable Construction**. `STRUCTURAL_REVIEW.md`
audits the added claims: sharp spectral realizations of factor-two bounds,
the equivalence between endpoint relaxation exactness on every subinterval
and completeness of optimal slopes, and an additive preset budget bounded
by the finite number of missing-slope prices. The proofs are included in
the manuscript. These are model-specific refinements of standard convex
geometry; no general scalarization or spectral-duality discovery is claimed.

The historical runtime and certificate claims below remain unchanged.
The new 12 interval examples and 54 numerical endpoint diagnostics are
separate from the 54 saved-menu certificates described below.

## Earlier algorithmic contribution and retained evidence

The paper is **Finite Menus of Spectral Subspaces: Construction, Reuse, and
Verifiable Bounds**. This is a scoped computational optimization contribution,
not a claim of a fundamental new spectral theorem or proven journal acceptance.

| Claim | Evidence and boundary |
|---|---|
| The adaptive curve does not determine the finite menu | Exact two-model construction in Proposition 1 and STRUCTURAL_EXAMPLE.md; identical F, E1=1/2 versus 3/4. Strictly positive definite shifts preserve it. Four outward checks agree. |
| All globally optimal presets can be an insufficient dictionary | Exact proof for Model M: the complete set contains only coordinate projectors; best one-preset loss is 1 versus 3/4. This allows every tie choice and is stronger than the separate library-basis collision control. |
| Arbitrary finite dimension, rank, and site count are covered mathematically | Theorems 2–3 and END_TO_END_PROOF.md. Shared A, real symmetric matrices, fixed rank, scalar nonnegative price, finite site set. No multi-resource or site-dependent-task extension is claimed. |
| The endpoint oracle is exact in real arithmetic | Explicit weak-dual argument and pure-projector recovery, including boundaries and cutoff ties. Direct predecessors are Tantipongpipat et al. (2019) and Shen et al. (2026). This identity and recovery are NOT new claims. |
| The full menu characterization is globally optimal | Compactness, convex acceptable intervals, monotone farthest extension, and interval-cover exchange proof. This composes established ingredients for the present model. Floating outer-search lower estimates are not certificates. |
| Reuse reduces work in the tested regime | A 72-run fresh-seed ablation keeps slope bisection fixed; median plain/reuse time ratio 4.220 on ten new cells. Three repetitions, same spectrum cache. It isolates the combined reuse mechanism, not each bound type. |
| An advantage survives stronger alternatives | 198-run study: median hybrid-Brent/reuse ratio 1.367 on 20 new cells, range 1.255–1.866. Both use cached bounds and brackets. Own implementations; not prior authors' runtime results, a hardware-independent bound, or universal solver dominance. |
| Existing specialized formulas can be better | Three-repeat mirror comparison: the analytic solver is much faster for K=1,2,4 at matched stopping resolution. Smooth K=1 development cases also favor Brent. These negative scope findings are in the manuscript. |
| Dictionary competitors are accurately compared | All-site candidates; continuous-price selection; cumulative preprocessing/refinement costs; external accuracy target favors competitors. Uniform 1/10 and adaptive 6/10 attain the target within declared caps. Single-run screen; not all possible dictionaries or a replication of a published adaptive method. |
| Computed menus have global numerical evidence | 22 + 22 + 10 saved certificate artifacts, including repeated controls, have standalone outward bounds of width 1e-5. Exact binary64-input/IEEE-754 contract; independent optimizer-free replay. No claim of formally verified software or physical uncertainty bounds. |
| A genuine resource application has been established | NOT CLAIMED. Data are synthetic. An actual measurement-design application would require separate validation of A, C, d and practical consequences. |
| No one on the internet has ever known these facts | NOT CLAIMED. Targeted primary-source review establishes attribution and distinctions, not exhaustive priority. |

## Residual contribution and significance

The defensible contribution is the explicit finite-menu treatment of a
multi-site spectral feasible family, its structural distinction from the
fully adaptive curve, and a reproducible implementation that returns
independently checkable near-optimal menus and beats the tested general
references in the stated regime. The 1.37 ratio against the strongest
reference is modest. The exact separation and verifiable construction carry
more of the scientific argument than a large headline speedup would.

This is materially stronger than a two-dimensional worked example plus an
already-known approximation law. It remains a narrow paper: a referee may
judge the synthesis insufficiently significant for a particular journal.
That uncertainty cannot be removed by polishing prose or relabeling known
ingredients as discoveries. An original-research submission is reasonable to
consider on this scoped basis; acceptance and priority are not certified here.

The paper does not need a fabricated application to support this algorithmic
route. It does need its assumptions, comparative limits, retained failures,
and prior-art attribution to stay explicit in any venue-specific revision.
