# Current proof-and-priority release (v6)

This revision changes scientific positioning, attribution, organization and
submission preparation. It does not change the frozen solver, benchmark
measurements, saved menus or interval witness payloads.

- Title and abstract foreground the realizability criterion and the
  exceptional-price repair bound. Main theory comes before construction.
- All experiments and unfavorable comparisons remain in Appendix A.
- Appendix D compares the actual assumptions of convex-Pareto approximation,
  scalarization, tangent replacement and robust policy-count results. It
  includes an explicit example showing why convexifying lifted uncertainty
  changes this regret objective.
- Theorem 4 is the all-subinterval exactness result; Theorem 6 is repair and
  spectral finiteness. No universal sharpness of the q bound is claimed.
- The bibliography includes the full thesis comparison and recent policy-count
  work; published metadata and visible DOI links have been checked.
- Journal of Global Optimization is the preparation target; a flat source
  archive respects its no-subfolder instruction. A cover-letter draft and
  author-finalization checklist accompany the research archive.
- Eleven inspected primary-source records and a 214-file frozen-evidence
  manifest are distributable. Third-party full-text PDFs remain excluded.

The manuscript has 22 pages, compared with v5's 19. The added space documents
the priority boundary and complete evidence; it is not new benchmark volume.
All earlier archives are preserved. Final technical outcomes are recorded in
`releases/release_validation_v6.json`, `releases/journal_validation_v6.json`,
and `releases/completion_v6.json`; older green reports do not validate this
revision.

---

Historical record follows; earlier release gates do not validate v6.

# Release versions

Research/arXiv source v1 passed distribution hashes but its extracted research
package failed when the reproduction wrapper created paths longer than the
Windows legacy limit. The failed archive and `release_validation_v1.json` are
preserved. This was a scratch-copy path failure before numerical verification,
not a changed research result.

Version v2 changes the reproduction wrapper to select a shorter temporary
output directory automatically when needed on Windows. The numerical solver,
frozen benchmarks, witness files, manuscript, and scientific claims are
unchanged. Documentation points to v2 validation as the final release gate.
The authoritative outcome is `releases/release_validation_v2.json`.
