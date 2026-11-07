# Reproducing and checking the algorithmic paper

Use Python 3.12 and the pinned `requirements.txt`. From this directory:

```text
python -m pip install -r requirements.txt
python reproduce.py --mode verify
python reproduce.py --mode smoke
```

Both commands create new timestamped directories under `reproductions/`, leave
distributed records unchanged, and write a JSON report plus command logs.
On Windows, an automatically chosen shorter directory under the system temp
folder is used when nested paths would approach the legacy path limit; its
full location is printed. Use `--output PATH` to choose a short new location.
`verify` independently reevaluates every saved menu in the three original timing
studies and replays all 54 original certificate artifacts. It additionally
checks 24 sparse-confirmation menus, seven scaling menus, the avoided-crossing
regression, eight sparse-extension certificates, and the 14 banded grid
certificates. Banded replay uses six CPU workers and no menu solver.
Both interval arithmetic paths are tested against exact rational inertia.
It also checks the
interval primitives and the structural example. Certificate replay does not
import or run the menu optimizer. The sparse extension also needs SciPy for
input storage and spectral proposals, independently checked by the verifier.
`smoke` constructs a new seed-5600 two-preset menu and checks a newly generated
global lower/upper certificate, as well as the exact structural examples.

Do not run Python with `-O` or `PYTHONOPTIMIZE`: validation uses assertions.
The wrapper rejects optimized mode. Read `CERTIFICATE_DERIVATION.md` for the
IEEE-754 and exact-binary64-input contract. Certificates are not statements
about physical parameter uncertainty, novelty, or journal acceptance.

To repeat the timed studies rather than just checking their saved results:

```text
python reproduce.py --mode full
```

This runs the original and stronger Brent comparisons, the slope-bisection
reuse ablation, the dictionary screen, the specialized mirror comparison,
the analytic stress checks, and certificate generation/replay in a new
directory. Run it without other numerical jobs for interpretable timings.
Timings depend on hardware, BLAS, and system load; the numerical checks and
bounds are the reproducibility targets. A full run can take several minutes
or longer, especially on slower hardware. The original run environment is in
the study manifests and `results/environment.json`.

The sparse extension has its own full-run command, also using a fresh
isolated directory:

```text
python reproduce.py --mode sparse-full
```

This reruns the 72 fresh-seed confirmation timings, seven descriptive
scaling solves, independent spectral checks, and eight certificate
generation/replay cases. Do not run competing numerical jobs during timings.
Read `SPARSE_CONFIRMATION_V2_PROTOCOL.md`, `SPARSE_SCALING_PROTOCOL.md`, and
`SPARSE_VERIFICATION.md` for the design and the distinction between numerical
checks, dense outward certificates, and tridiagonal outward certificates.
The stopped v1 attempt (18 runs, six failures) and its source snapshot are
retained; it is not silently rerun using the repaired code. Generate manuscript
tables from checked records with `python make_sparse_assets.py`.

The current sparse-full workflow also generates and replays all 14 banded
grid certificates. Existing witnesses can be replayed directly with
`python check_banded_certificates_v2.py --workers 6`; lower the worker count
to reduce simultaneous CPU/memory use. `python make_banded_assets.py`
regenerates the associated manuscript text/table. See
`BANDED_VERIFICATION.md` and `BANDED_VERIFICATION_V2_PROTOCOL.md` for the
additional directed-Decimal arithmetic contract and retained failed attempt.

Additional development scripts (`screen.py`, `check_reuse.py`,
`check_warm_brent.py`, and `verify_independent.py`) are included with their
saved records. The SDP cross-check uses the separate optional environment:

```text
python -m pip install -r requirements-sdp.txt
python verify_independent.py
```

Run development scripts only in a scratch copy if preserving their original
result files matters. The full wrapper does not rerun the historical SDP
study or failed development versions. Their inputs, statuses, failure records,
and generator snapshots remain available for inspection.

## Manuscript

The PDF and all figure/table inputs are included. With pdfLaTeX and BibTeX:

```text
python manuscript/build.py
```

The build disables shell escape. Regenerate assets from saved evidence with
`python make_manuscript_assets.py`; this needs Matplotlib but no network.
The arXiv source archive contains only TeX, bibliography, tables, and the
figure PDF. The separate research archive contains code and evidence.

## Evidence map

- `results/confirmation_v1`: 132 cold-reference timing runs; 44 saved menus.
- `results/warm_confirmation_v1`: 198 stronger-reference runs; 66 saved menus.
- `results/reuse_ablation_v1`: 72 slope-bisection ablation runs; 24 saved menus.
- `results/dictionary_comparison_v2`: all ten dictionary cases and stages.
- `results/certificates_v2`, `warm_certificates_v1`,
  `dictionary_certificates_v1`: 22 + 22 + 10 upper/lower certificates.
- `results/special_case_comparison.json`: all matched-tolerance mirror timings.
- `results/structural_example.json`: outward checks of the exact counterexample.
- `results/interval_arithmetic_checks.json`, `stress_oracle.json`,
  `independent_verification.json`: independent and analytic correctness evidence.
- `results/certificates_v1` and `dictionary_comparison_v1`: retained failures.

Protocol hashes identify the exact source used for each frozen study. The
artifact manifest additionally hashes the distribution. Source PDFs from other
authors and local Python environments are deliberately not redistributed.
The companion `submission_20261002/code/menu_solver.py` is the original
specialized solver used as an independent reference; its sibling location is
needed by the comparison and reproduction scripts.

Author and affiliation placeholders are intentional. No public upload has
been made and no license has been chosen on the author's behalf.
# Structural revision

The current manuscript adds `manuscript/structural_theory.tex`.
Run `python check_structural_theory.py` to regenerate its targeted diagnostics
and outward bounds. This command is included in `reproduce.py --mode verify`
and `--mode full`. It does not rerun or alter the historical timing studies.
The current source/evidence release is v3; v2 preserves the earlier paper.
See `STRUCTURAL_REVIEW.md` for exactly which new checks are certified and
which are floating-point diagnostics.

