# Submission preparation: v8

The current paper is **Finite Menus of Spectral Subspaces: Realizability and
the Cost of Convexification**, 22 pages. The main result is an exact
all-subinterval criterion for feasible realization of a convexified menu,
with a spectral active-face test and an additional-preset bound localized
to finitely many exceptional prices. The construction and all synthetic
experiments remain as supporting evidence.

## Venue and honest pitch

The author currently plans **arXiv** posting. **Journal of Global Optimization**
remains a possible later journal target, whose official
scope includes theoretical and computational global optimization, robust and
multiobjective optimization, and computational geometry. This provides a
plausible readership, not evidence that the paper meets its significance bar.
The paper is a modest structural refinement built on established geometry.
Do not pitch the 1.367 median timing ratio as a major algorithmic breakthrough
or the spectral example as discovery of the general convexification problem.

Official scope and instructions were checked again on 19 October 2026:

- https://link.springer.com/journal/10898/aims-and-scope
- https://link.springer.com/journal/10898/submission-guidelines

The manuscript has a 150-250 word abstract, five keywords, numbered references
with available DOI links, editable LaTeX sources, and a declarations section.
The journal recommends the Springer Nature template; it does not mandate it
in the inspected instructions. The current article-class source builds
without custom style dependencies. Author identity and declarations are supplied.
The manuscript cites the public v7 artifact. Final PDF approval and actual
arXiv submission remain pending.

## Files to use

| File | Purpose |
|---|---|
| `manuscript/main.pdf` | Manuscript for review after author finalization |
| `manuscript/main.tex` | Editable main source; all adjacent inputs are required |
| `releases/paper2_journal_source_v8.zip` | Flat source package for journal upload; table paths flattened and figure named Fig1.pdf |
| `releases/paper2_algorithmic_arxiv_source_v8.zip` | Minimal arXiv source package; entry point main.tex; bibliography source and bbl included |
| `releases/paper2_algorithmic_research_v8.zip` | Complete code, frozen results, proofs, audit and reproducibility artifact |
| `submission/cover_letter.pdf` and `.tex` | Cover-letter draft with an explicit final author-declaration paragraph to replace |
| `submission/arxiv_metadata.json` | Title and exact LaTeX abstract; suggested category math.OC |
| `submission/AUTHOR_FINALIZATION.md` | Required factual author, declaration, license and account actions |

The journal source has no subfolders as requested by its portal instructions.
Supply the manuscript PDF separately. The internal audits and author checklist
belong with the research preparation, not the article-source upload. Third-party
literature PDFs and local environments are excluded from all release archives.

The arXiv package contains TeX, bibliography sources, compiled bibliography,
table inputs and the vector figure. It omits the compiled manuscript PDF and
build auxiliaries. A reasonable primary category is math.OC; moderation and
endorsement remain arXiv decisions.

- https://info.arxiv.org/help/submit_tex.html
- https://arxiv.org/category_taxonomy

## Release and author gates

Require PASS in release_validation_v8.json, journal_validation_v8.json and
completion_v8.json with matching archive hashes. Reports and command logs travel with the ZIPs in
`paper2_publication_bundle_v8.zip`. Author identity, declarations, MIT code
and CC BY 4.0 content licenses are supplied. Final author review and the
arXiv account/endorsement/upload are still required. The author reports no
prior publication or current submission as of 7 November 2026. The v7 artifact
has been published on GitHub; the revised v8 package is prepared for a separate
release. No journal/arXiv submission, review email or editor contact has occurred.

After further edits, rebuild and create a new release tag. Preserve v6 as the
audited placeholder version. The proof/priority audit does not establish
worldwide novelty; a referee can still reasonably question the contribution's
depth or relevance. More hardware benchmarks would not settle that question.
