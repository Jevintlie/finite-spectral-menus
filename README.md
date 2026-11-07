# Finite Menus of Spectral Subspaces

**Realizability and the Cost of Convexification**

Jevint Felixciano — Independent researcher

This paper studies when convexified finite menus can be realized by rank-r
orthogonal subspaces, and bounds the additional presets needed when some
optimal slopes are missing. It combines structural results with synthetic
computational evidence and independently replayable numerical certificates.
It does not establish a validated physical application or a new general eigensolver.

- [Read the 22-page paper](algorithmic_extension/manuscript/main.pdf)
- [LaTeX source](algorithmic_extension/manuscript/main.tex)
- [Download v8: complete bundle and arXiv source](https://github.com/Jevintlie/finite-spectral-menus/releases/tag/v8)
- [Reproduction instructions](algorithmic_extension/REPRODUCIBILITY.md)
- [Validation summary](algorithmic_extension/releases/completion_v8.json)
- [Focused independent-review brief](algorithmic_extension/submission/independent_review/REVIEW_BRIEF.pdf)
- [License scope](LICENSE.md)

V8 inserts the public artifact link and updates publication-status metadata.
Proofs, algorithms and frozen benchmark evidence are unchanged from v7/v6.
All 11 clean-extraction checks passed. This is internal technical validation,
not independent human peer review or a certificate of novelty. Substantial
AI assistance is disclosed in the manuscript. Independent human criticism
and arXiv submission remain pending.

## Verify and reproduce

Use Python 3.12 and the pinned requirements. From algorithmic_extension/:

```text
python verify_distribution.py
python -m pip install -r requirements.txt
python reproduce.py --mode verify
python reproduce.py --mode smoke
```

The first command checks the research artifact manifest. Additional repository
files and validation reports are covered by PUBLIC_SNAPSHOT_MANIFEST.json.
The evidence replays and smoke solve create new outputs, preserving stored
results. Building the paper requires LaTeX. See REPRODUCIBILITY.md for details.
The complete release bundle also includes a standard-library integrity verifier.

## Versions and citation

The manuscript cites the fixed [v7 artifact](https://github.com/Jevintlie/finite-spectral-menus/releases/tag/v7),
whose scientific evidence is unchanged. V8 supplies the manuscript containing
that public link. Cite the exact release or commit used; no arXiv ID or DOI
has been assigned by this workflow. GitHub hosting is not a DOI archive.

Software is MIT licensed. Manuscript, documentation and generated results are
CC BY 4.0. Third-party works and dependencies retain their own rights.
