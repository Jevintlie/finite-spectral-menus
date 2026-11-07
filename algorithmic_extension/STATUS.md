# Current proof-and-priority release (v6)

19 October 2026. The manuscript has been reorganized around realizability,
with the complete experiments moved to an appendix and an added comparison
with convex-Pareto and robust-policy results. The exactness and repair results
are now Theorems 4 and 6. The title is **Finite Menus of Spectral Subspaces:
Realizability and the Cost of Convexification** (22 pages).

The focused audit found substantial established antecedents and no unresolved
proof gap in the statements it checked. The residual claim is deliberately
narrow. This is an internal assessment, not an independent mathematical review
or proof of worldwide novelty. Significance remains for editors and referees.

The six core solver/verifier files and all saved run/NPZ evidence match the
214-file pre-revision hash snapshot; see
`results/publication_audit_v6/frozen_evidence.json`. Benchmark expansion is frozen.
Only saved-evidence replay, structural checks, and the existing fresh-problem
smoke test are used in release validation.

Prepared deliverables include LaTeX/PDF, a cover-letter draft, arXiv metadata,
a flat journal source ZIP, an arXiv source ZIP, and a research/evidence ZIP.
Current completion requires PASS in all three v6 release reports named in
README.md. Placeholder names and author-specific declarations remain by request.
The package has not been uploaded. See `submission/AUTHOR_FINALIZATION.md`.

---

Historical record follows; earlier release gates do not validate v6.

# Research status - 5 October 2026

## Current banded verification extension

The working manuscript extends the preserved v4 sparse study with outward
certificates for all 14 CSR grid menus, including n=1024 and 4096. Each has
passed standalone replay with a global gap below 1.01e-5. The banded interval
LDL verifier uses classical inertia and a directed 50-digit Decimal retry
for unresolved counts at n<=512; the larger cases use binary64 only.
Both arithmetic paths pass 144 exact-rational count checks. The failed first
attempt remains under results/banded_certificates_v1.

This addresses the previous large-grid verification gap, while retaining
bandwidth, pivot, memory, and synthetic-model limits. It changes no frozen
solver or optimization timing. See BANDED_VERIFICATION.md and the v5 release
gate: releases/release_validation_v5.json must report PASS. Earlier releases
and the paused Omega work remain preserved.

## Historical structural revision (v3)

The current manuscript is **Finite Menus of Spectral Subspaces: Exactness,
Approximation, and Verifiable Construction**, 15 pages. Its additional
theory is in `manuscript/structural_theory.tex`; proof and prior-art boundaries
are audited in `STRUCTURAL_REVIEW.md`. New results characterize exactness
on every price subinterval and bound the number of extra globally optimal
presets needed to realize a relaxed menu's tolerance. The factor-two
scalarization principle is attributed as standard, with sharp spectral
examples provided here.

`results/structural_theory_v1.json` passes 12 outward-bound cases and 54
numerical endpoint checks, plus the recorded tie and multi-gap controls.
The evidence audit also passes for the unchanged historical solver studies.
Clean packaging of this revision requires a PASS in
`releases/release_validation_v3.json`. The v2 release remains unchanged.

The material below records the earlier algorithmic release and its evidence.

## Prior algorithmic release

Objective: a defensible algorithmic contribution for Paper 2. The general
construction, proofs, experiments, independent verification, and eleven-page
manuscript are prepared. Final archive validation is recorded separately in
`releases/release_validation_v2.json`; see `COMPLETION_AUDIT.md` for all gates.
The original submission package and paused Omega experiment are preserved.

## Evidence now available

- General-dimensional, fixed-rank, multi-site endpoint construction implemented.
  Two-objective spectral minimax and tied-eigenspace recovery are explicitly
  attributed to prior fair-PCA research; they are not claimed as new.
- END_TO_END_PROOF.md gives the exact-real endpoint, recovery, greedy covering,
  cache-bound, and finite certificate arguments. Numerical stopping tolerances
  are distinguished from independently verified upper/lower bounds.
- STRUCTURAL_EXAMPLE.md proves that identical fully adaptive curves can have
  optimal one-preset losses 1/2 and 3/4. In the latter model even the dictionary
  of every globally optimal preset has loss 1. This is independent of grid
  resolution and eigenbasis choices. Four outward numerical checks, including
  strictly positive definite shifts, confirm the algebraic construction.
- Independent SDP checks: 24 site solves; all within 2e-7, with solver statuses
  retained, including optimal_inaccurate warnings. Twelve rotation checks pass.
- First timing confirmation: 132 runs, 44 independently checked menus. Median
  cold-Brent/reuse ratio 2.810 on 20 new-seed case/budget cells. This is a
  weaker reference than the following comparison and is not the headline gain.
- Stronger timing confirmation: 198 runs, 66 independently checked menus,
  fresh seeds 5400/5401, three repetitions. On 20 new-seed cells, median
  bracket-warmed-Brent/reuse ratio 1.630 (range 1.375?2.033); hybrid Brent with
  the same cached primal/dual decisions/reuse ratio 1.367 (1.255?1.866).
  Numerical losses agree within 5e-6. No failed runs or slower reuse cells in
  that declared K=2,4 study. These are own dense implementations, not prior
  authors' code or a universal speed claim.
- One-preset development tests favor Brent on several smooth instances. The
  specialized two-dimensional analytic solver also wins: about 0.0015/0.0067/
  0.0128 seconds versus 0.0042/0.165/0.377 for K=1/2/4, at matched stopping
  resolution, three repetitions. Generality has a real cost in small cases.
- Uniform and adaptive all-site dictionaries are compared with continuous-price
  selection and an oracle-assisted accuracy target. Uniform meets the target
  in 1/10 cases at its cap; adaptive in 6/10. This is a descriptive screen,
  not a universal rejection of sampling or of all adaptive competitors.
- Original 22 saved menus have standalone outward upper/lower certificates
  with width 1e-5. Ten dictionary-reference cases now have the same verified
  global bounds. All 22 stronger-reference menus also pass standalone certificate replay.
- Interval primitives were checked against exact fractions/high precision;
  20 analytic scaling, near-crossing, high-multiplicity, and full-rank cases pass.
  Certification assumes the documented IEEE-754/exact-binary64-input contract;
  no proof-assistant verification or independent external code audit is claimed.

## Retained failures and limits

Certificate v1 rejected an out-of-range dual proposal in 1/22 cases; v2 uses
separate in-range dual-price proposals and passes all cases. The old failure
and generator snapshot remain. Dictionary v1 stopped on NumPy-bool JSON
serialization; v2 fixes serialization only and retains the incident.

## Completed research deliverables and final release gate

- The new eleven-page manuscript includes the exact structural example,
  complete constructive proofs, all comparison tables, attribution, AI-use
  disclosure, and explicit limits. Author-specific fields remain placeholders.
- A separate 72-run fresh-seed ablation isolates reuse while holding slope
  bisection fixed: median plain/reuse ratio 4.220 over ten new cells, with all
  numerical accuracy checks passing. The stronger hybrid comparison remains
  the appropriate headline: 1.367, not 4.220 or the cold-reference 2.810.
- Overall evidence: 402 main timed runs, 134 independently checked saved menus,
  54 certificate artifacts including repeated controls, and an additional
  fresh two-preset solve/certificate in an isolated smoke run.
- Local isolated evidence replay and smoke reproduction pass. Source hashes,
  counts, budget labels, numerical agreements, and manuscript build are checked
  in results/completion_evidence.json. Claim boundaries are in CLAIM_AUDIT.md.
- The release builder and clean-extraction validator produce separate research
  and arXiv-source archives. Their final authoritative readiness result is
  releases/release_validation_v2.json; it must say PASS before completion.

The contribution supports a scoped computational optimization submission.
Priority over all literature, real-world application validity, and journal
acceptance are not claimed. Optimization Letters is a plausible scope match,
with the significance caveat documented in SUBMISSION_NOTES.md. No public
submission has been made.
