# Finite Menus of Spectral Subspaces

**Realizability and the Cost of Convexification**

Jevint Felixciano — Independent researcher

This repository is prepared for public release; this local snapshot has not
yet been uploaded. The manuscript studies exactness of convexified finite
menus and the additional realizable presets needed to repair missing slopes.
It is a structural optimization paper with synthetic computational evidence,
not a validated physical application or a claim of a new general eigensolver.

- [Read the paper](algorithmic_extension/manuscript/main.pdf)
- [LaTeX sources](algorithmic_extension/manuscript/main.tex)
- [Reproduction instructions](algorithmic_extension/REPRODUCIBILITY.md)
- [Focused review brief](algorithmic_extension/submission/independent_review/REVIEW_BRIEF.pdf)
- [Release validation](algorithmic_extension/releases/completion_v7.json)
- [Licenses](LICENSE.md)

V7 supplies the author's declarations and licenses and closes the missing
validation-report handoff gap. Proofs and benchmark evidence are unchanged
from v6. Independent human review and public arXiv submission are pending.
Internal validation is not peer review or a novelty certificate.

## Verify and reproduce

Use Python 3.12 and the pinned requirements. From algorithmic_extension/:

```text
python verify_distribution.py
python -m pip install -r requirements.txt
python reproduce.py --mode verify
python reproduce.py --mode smoke
```

The first command checks the archived source/evidence manifest. Added
repository landing files and release reports are listed in
PUBLIC_SNAPSHOT_MANIFEST.json. The verification workflow creates new output
folders and does not overwrite frozen results. Building the manuscript needs
a LaTeX installation. Read REPRODUCIBILITY.md for complete assumptions.

## Versioning and citation

Cite the manuscript and the exact published release/commit you use. No DOI,
arXiv ID or live repository address is invented in this snapshot. The author
will insert the actual public release address into a subsequent manuscript
build. Software is MIT; manuscript, documentation and generated results are
CC BY 4.0. Third-party works/dependencies retain their own rights.
