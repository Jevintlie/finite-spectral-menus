# Public artifact and manuscript revision (v8)

The versioned research artifact is public:
https://github.com/Jevintlie/finite-spectral-menus/releases/tag/v7

V8 adds that verified URL to the manuscript and updates publication-status
metadata. Its proofs, algorithms and frozen experimental evidence are
unchanged. Use `paper2_publication_bundle_v8.zip` for the revised manuscript
and complete reports; use `paper2_algorithmic_arxiv_source_v8.zip` for arXiv.
These are available with the matching v8 GitHub release once published.

The author reports no prior publication or current submission as of
7 November 2026 and plans an arXiv posting. Final author approval of the PDF,
arXiv account/endorsement/upload, and independent human criticism remain
pending. The GitHub upload is not an arXiv submission or peer review.

The v6/v7 audits below describe their preserved historical archives.
`audit_public_artifact_v8.py` checks the v8 revision.

# Historical publication preparation (v7)

Updated 7 November 2026. Author: Jevint Felixciano, Independent researcher.
Author declarations are in the manuscript. Software is MIT licensed;
content/results are CC BY 4.0. Scientific proofs, algorithms and benchmark
evidence are unchanged from v6. V7 updates authorship and distribution.

Use `releases/paper2_publication_bundle_v7.zip` once built and validated.
It includes all three v7 ZIPs, the reports and logs certifying them, and an
integrity verifier. This outer bundle fixes the missing reports without
attempting to put a ZIP's own hash inside itself.

The review brief is `submission/independent_review/REVIEW_BRIEF.pdf`.
Independent criticism has been prepared but not obtained. Local draft
contact emails are excluded from public packages. See
`submission/PUBLICATION_PLAN.md` for the GitHub/arXiv plan and pending actions.
No public repository URL or arXiv identifier is claimed until it exists.

The following v6 record is historical; its hash-bound audit applies to
the unchanged v6 archives, not to edited v7 working files.

# Previous proof-and-priority release (v6)

Prepared 19 October 2026. Start with `manuscript/main.pdf` and
`PRIORITY_AUDIT_20261011.md`. The 22-page LaTeX manuscript is **Finite Menus of
Spectral Subspaces: Realizability and the Cost of Convexification**.
Its central contribution is the all-subinterval active-slope exactness
criterion and the exceptional-price bound on additional feasible presets.
The audit explicitly acknowledges the convex-Pareto and robust-policy
predecessors. All computational evidence is retained in Appendix A; no
performance benchmark was added or rerun for this revision.

The preparation target is Journal of Global Optimization. Scope fit is not
an acceptance prediction. This is a modest structural optimization submission,
not a claim of a new general scalarization, duality or covering theorem.

Read `SUBMISSION_NOTES.md` for file selection and
`submission/AUTHOR_FINALIZATION.md` for the deliberately retained author fields.
Author identity and declarations must be finalized before actual upload.
No submission, public repository, or license choice has been made.

The release gates are `releases/release_validation_v6.json`,
`releases/journal_validation_v6.json`, and `releases/completion_v6.json`.
All must report PASS and match the current archive hashes. Their reports live
alongside the archives they check. See `COMPLETION_AUDIT.md` for scope.
Existing v1-v5 releases and the paused Omega study are preserved.

---

Historical record follows; earlier release gates do not validate v6.

# Algorithmic extension of Paper 2

Revised 5 October 2026. The manuscript includes a slope-based
exactness criterion, sharp spectral examples, and a finite additional-preset
bound to the general algorithm and independently checked evidence. Read
`STRUCTURAL_REVIEW.md` for the proof and prior-art audit. The sparse extension
adds a separate CSR/dense-partial comparison, larger scaling checks, and
tridiagonal outward verification; read `SPARSE_REVIEW.md` for its limits.
Release v4 preserves the 18-page sparse-computation revision, v3 the
15-page structural revision, and v2 the earlier
11-page manuscript. The current release gate is
`releases/release_validation_v5.json` and is valid only when it reports PASS.

The artifact retains complete model-specific construction proofs,
402 repeated timing runs across three studies, and 54 independently replayed
certificate artifacts. Final release verification is recorded separately in
`COMPLETION_AUDIT.md`. The original `../submission_20261002` package is preserved.

Sparse evidence is separate: 72 confirmation timing runs, seven descriptive
scaling solves, 31 independently checked menus, and eight additional outward
certificate artifacts. The stopped sparse v1 attempt and its six failures
are retained. Numerical agreement does not imply a universal sparse speedup;
the tables report every declared size, including unfavorable cases.

The banded verification extension adds 14 outward certificate artifacts for
every CSR grid menu, including n=4096, with standalone replay. These include
the four small grids already checked by the dense verifier; counts are
certificate artifacts, not 14 additional independent problem instances.
Read `BANDED_VERIFICATION.md` for the proof, Decimal fallback, retained failed
attempt, and bandwidth limits. The optimizer timings are unchanged.

Start with `manuscript/main.pdf`, `STRUCTURAL_REVIEW.md`, and `REPRODUCIBILITY.md`.
The contribution is scoped structural and computational optimization; priority over every
possible predecessor and journal acceptance are not claimed.

## Objective and decision standard

Develop a defensible algorithmic contribution for finite measurement menus,
covering a meaningful problem class and demonstrating an advantage against
credible alternatives. A successful implementation, a rediscovered theorem,
or a favorable toy example alone does not complete this objective.

Current candidate: globally optimized menus of fixed-rank orthogonal measurement
subspaces, in arbitrary finite dimension, with arbitrary positive-semidefinite
site cost matrices and a shared quadratic task reward, over a scalar price
interval. Endpoint feasibility uses established two-objective spectral
optimization; interval covering then addresses the full menu.

Completion criteria (retained from the original research plan):

1. Correct reduction, assumptions, recovery of actual subspaces, and treatment
   of repeated eigenvalues; distinguish known ingredients from new results.
2. Reliable implementation with independent checks and explicit numerical
   upper/lower evidence for continuous-price menu loss.
3. Comparisons with strong applicable methods at matched objective accuracy;
   include small cases where the previous analytic solver is competitive.
4. Dimension, rank, site-count, conditioning, degeneracy, and budget tests;
   retain failures and runtime costs, not only favorable examples.
5. Literature comparison demonstrating the residual contribution's usefulness;
   no claim that lack of a search result proves priority.
6. Manuscript integration and reproducible artifact only once the contribution
   survives the preceding checks.

No Omega process is started or changed by this work. No public submission occurs.

## Files

- `THEORY.md`: derivation and scope, including attribution boundaries.
- `LITERATURE.md`: directly relevant predecessors and open comparison questions.
- `spectral_menu.py`: experimental general-rank spectral implementation.
- `screen.py`: initial correctness screen, not a final benchmark.
- `results/`: generated records with code hashes and environment metadata.

## Pre-outcome development screen

Use the old mirror model as an independent rank-one endpoint and menu reference.
For general instances compare endpoint objective with an independent convex
scalar optimization and, where available, an SDP relaxation. Explicit commuting
matrices must force an interior eigenvalue collision and require a mixed
subspace. Verify actual endpoint loss, orthonormality, and primal/dual gaps.
Random development seeds are 4100 onward; later confirmation seeds must be
separate. These checks develop and debug the method, not confirm a speed claim.
