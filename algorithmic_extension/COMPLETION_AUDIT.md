# Current proof-and-priority release (v6)

Objective: keep the paper, freeze benchmark expansion, complete a focused
proof-and-priority audit, and prepare a LaTeX publication submission package.
This audit is separate from the historical algorithm-development objectives.

| Requirement | Current authoritative evidence | Completion condition |
|---|---|---|
| Preserve the paper and all existing evidence | v5 archives; current main.tex and all experiment inputs | All declared results and limitations retained; theory-first revision |
| Freeze benchmark expansion | `results/publication_audit_v6/frozen_evidence.json` | All 214 baseline hashes match, no new run/NPZ files |
| Audit central proofs and boundary cases | `PRIORITY_AUDIT_20261011.md`; actual statements in `manuscript/structural_theory.tex` and main.tex | Checked arguments, scopes and edge cases; no unresolved gap found in this internal audit |
| Compare closest predecessors by substance | Same audit, `manuscript/prior_art_comparison.tex`, `results/publication_audit_v6/literature_sources.json` | Full relevant primary passages compared; known principles attributed; narrow residual claim and remaining significance uncertainty stated |
| Produce reviewable LaTeX/PDF | main.tex, all inputs and main.pdf; rendering checks in completion_v6.json | 22 pages; clean build; no missing citations or layout warnings; visual review |
| Prepare a suitable submission route | SUBMISSION_NOTES.md; submission/cover_letter.tex and PDF; arxiv_metadata.json; author checklist | Current official instructions checked; target and fit limits stated; no fabricated author declarations |
| Reproduce released evidence | `releases/release_validation_v6.json` | Clean extracted hashes, saved-evidence replay, structural diagnostics, existing smoke test, research and arXiv builds all PASS |
| Validate journal source independently | `releases/journal_validation_v6.json` | Flat archive builds after extraction; PDF text matches working source |
| Preserve prior releases and requested placeholders | `releases/completion_v6.json`, author_info.tex and declarations | v5 hashes unchanged; intentional human finalization identified; no upload performed |

The final gate is `releases/completion_v6.json`. It must inspect actual reports
and archive hashes, not merely this list, and verify text equality across the
working, extracted research and arXiv PDFs. The journal validator checks its
own extracted PDF separately. Reports are external to the archive whose hash
they verify, avoiding a self-referential manifest.

PASS means completion of the scientific/technical preparation within the
requested placeholder scope. The files must not be uploaded with placeholder
identity or unconfirmed declarations. This is not a claim of guaranteed
acceptance, independent peer review, exhaustive priority, or completed public
publication. The remaining human factual/account actions are listed in
`submission/AUTHOR_FINALIZATION.md`.

---

Historical record follows; earlier release gates do not validate v6.

# Completion audit

## Banded verification extension (5 October 2026)

Current release gate: `releases/release_validation_v5.json` must report PASS.
Version 4 remains preserved. The new evidence is
`results/banded_certificates_v2/summary.json` and `standalone_verification.json`:
14 grid certificates, including both larger CSR scaling cases, with gaps
below 1.01e-5. `audit_banded_results.py` checks provenance, counts and the
retained v1 failure. `check_banded_verifier.py` compares both binary64 and
directed Decimal inertia with exact rational elimination in 144 cases each.
The proof and additional arithmetic contract are in `BANDED_VERIFICATION.md`.
Six CPU processes check independent branch-price pairs; isolated optimizer
timings remain unchanged. This is a bandwidth-dependent certification
extension, not a new eigensolver theorem or a validated physical application.

## Sparse extension (5 October 2026)

The new user request is to establish what efficient sparse computation can
actually deliver. Release v3 remains intact. The extension's completion gate
is `releases/release_validation_v4.json` reporting PASS after clean extraction.

- Paired backend study: `results/sparse_confirmation_v2/analysis.json`,
  72 timings and 24 independent continuous-price menu checks.
- Descriptive scaling screen: `results/sparse_scaling_v1/analysis.json`,
  seven solves/checks, including a tridiagonal reference and banded grid check.
- Outward global bounds: four selected grid menus and four path menus,
  with standalone replay records in `sparse_grid_certificates_v1` and
  `sparse_path_certificates_v1` under `results/`.
- Development correctness: `results/sparse_development_v2.json`, including
  exact-rational inertia comparisons and an avoided-crossing regression.
- Failure retention: stopped `sparse_confirmation_v1`, 18 runs including six
  failures, source snapshot and consumed seeds; fresh seeds for v2.
- Provenance and quantitative summary: `audit_sparse_results.py`,
  `results/sparse_audit.json`, and `results/sparse_summary.json`.
- Scientific interpretation: `SPARSE_REVIEW.md`; derivation and arithmetic
  scope: `SPARSE_VERIFICATION.md`. No universal sparse complexity or physical
  application claim follows from these checks.

The earlier audit below describes the preserved structural revision. Its v3
gate does not validate the sparse extension.

## Previous objective: complete Paper 2 and make it LaTeX ready (v3)

The user requested substantive research progress after questioning the
scientific significance of the earlier algorithmic paper. Completion must
therefore include a developed contribution and its limitations, as well as
a working source package. It cannot be inferred from benchmark counts alone.

| Requirement | Current authoritative evidence | Completion gate |
|---|---|---|
| Strengthen the scientific argument beyond the single example and modest timing gain | Theorems 5, 6, and 8 in the current manuscript; exact active-face slope formula; proof audit in STRUCTURAL_REVIEW.md | Complete proofs and clearly delimited contribution; no claim of breakthrough or guaranteed acceptance |
| Distinguish established principles from the proposed refinement | Primary-source comparison in STRUCTURAL_REVIEW.md and citations to weighted scalarization, convex Pareto approximation, tangent replacement, and Rellich | General ingredients attributed; incomplete full-text access disclosed; universal priority not asserted |
| Check new formulas and boundary distinctions | results/structural_theory_v1.json, regenerated by check_structural_theory.py | PASS, 12 exact-rational/outward examples, 54 numerical endpoints, active-face/tie/gap controls |
| Retain valid earlier computational evidence | audit_results.py plus extracted-package reproduce.py --mode verify | Unchanged frozen solver hashes; 134 saved menu checks and 54 certificate replays |
| Supply complete LaTeX source and readable PDF | manuscript/main.tex, structural_theory.tex, references.bib, main.bbl, figure and table inputs | Current build, no unresolved references/overflow; rendered structural pages inspected |
| Package and verify portable artifacts | releases/package_v3.json and release_validation_v3.json | PASS from clean extraction, matching hashes, fresh smoke solve/certificate, research and arXiv PDF builds |
| Preserve requested author placeholders and prior work | Current author fields; previous release v2 and original submission folder | Placeholders retained; no submission performed; Omega unchanged |

The release gate is checked after packaging. A missing or failing v3 report
means this revision is not complete. The report is external to the archive
whose hash it checks. The earlier v2 report is not evidence for the revision.
Scientific significance remains a matter for reviewers; technical completion
does not promise acceptance or imply an independent peer review.

## Historical audit against the original algorithmic objective

Objective: develop a defensible algorithmic contribution for Paper 2, with a
meaningful finite-menu class, credible comparisons, an explanation of the
advantage and its limits, and a reviewable research manuscript/artifact.
This audit retains the six requirements in README.md; it does not replace the
objective with merely getting a prototype or a favorable example to run.

| Original requirement | Authoritative evidence inspected | Finding |
|---|---|---|
| 1. Correct reduction, actual subspaces, repeated eigenvalues, prior-art boundary | Manuscript Theorems 2–3; END_TO_END_PROOF.md; exact face interpolation; LITERATURE.md; independent SDP/rotation and tie tests | Constructive proof and implementation agree. Fair-PCA endpoint duality/recovery and greedy interval covering are explicitly prior art. |
| 2. Reliable implementation and continuous-price upper/lower evidence | interval_verifier.py; CERTIFICATE_DERIVATION.md; exact/high-precision arithmetic checks; 54 saved upper/lower witness artifacts; optimizer-free replay | Bounds of width 1e-5 pass for every primary proposed menu. The arithmetic contract is explicit. Float search estimates are not promoted to certificates. |
| 3. Strong accuracy-matched alternatives, including old analytic solver | 132 cold-Brent runs; 198 warm/hybrid-Brent runs; ten all-site dictionary cases; 18 specialized-solver timing runs | The strongest general reference takes 1.367 times the proposed method's time at the median. Losses agree within 5e-6. The specialized old solver wins and is reported. |
| 4. Dimension, rank, site count, conditioning/degeneracy, budgets, failures, cost | Five dense shapes through n=64, ranks through 16, one/three/six sites, K=1/2/4 across studies; 20 analytic scale/near-tie/full-rank cases; independent SDP/rotation checks; retained failure directories and memory/timing records | Declared tests pass, with failures retained and corrected transparently. Results do not establish arbitrary-conditioning, sparse, or large-scale performance. |
| 5. Useful residual contribution and literature comparison | Exact identical-F/different-menu example; complete finite-menu algorithm; standalone witnesses; scoped 1.37 strongest-reference ratio; 72-run reuse ablation; primary-source ledger | A narrow computational optimization contribution is supported. It is not a new general minimax theorem, interval greedy rule, or proof of priority over all literature. Scientific significance remains a referee judgment. |
| 6. Manuscript integration and reproducible artifact | Eleven-page manuscript, generated figure/tables, source/bibliography, frozen raw evidence, pinned dependencies, reproduce.py, release archives | Manuscript builds without unresolved references or layout overflow. Local isolated verification and fresh-problem smoke runs pass. Final archive readiness is determined by release_validation_v2.json as described below. |

## Numerical and release gates

`results/completion_evidence.json` audits source hashes, all 402 main timing
runs, all 134 saved menu checks, the 54 certificate artifacts, dictionary
target counts, the special-case comparison inputs, and the manuscript build.
It is a count/provenance audit, not a replacement for the mathematical proofs.

The local isolated verification report is
`reproductions/20261004T055848351605Z/reproduction_report.json` (PASS), and
the fresh-problem report is
`reproductions/20261004T055916894718Z/reproduction_report.json` (PASS).
These are local working directories, not bundled dependencies.

Archive validation is deliberately performed **after** packaging. Its
authoritative report is `releases/release_validation_v2.json`. Final readiness
requires that report to say PASS and match the archive hashes in
`releases/package_v2.json`. It checks every archived file hash, replays all
saved analyses and certificates from the extracted package, solves and
certifies a new problem, and builds both the research-package manuscript and
the arXiv source package without access to this working tree's manuscript.
The report is supplied alongside the archives rather than inside an archive
whose own hash it checks.

## What completion does and does not mean

The research objective is the algorithmic extension and its reviewable
evidence, not guaranteed peer-review acceptance, a proof that no predecessor
exists, or an actual public submission. Author identity and declarations are
intentionally placeholders. The original submission directory and paused
Omega study were not modified. A prospective venue and its fit limitations
are documented in SUBMISSION_NOTES.md.
