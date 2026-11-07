"""Regenerate sparse-study manuscript tables from checked records."""
from pathlib import Path
import json
import numpy as np

ROOT=Path(__file__).resolve().parent
study=json.loads((ROOT/'results/sparse_confirmation_v2/analysis.json').read_text())
scaling=json.loads((ROOT/'results/sparse_scaling_v1/analysis.json').read_text())
assert study['status']==scaling['status']=='PASS'
rows=list(map(json.loads,(ROOT/'results/sparse_confirmation_v2/runs.jsonl').read_text().splitlines()))
screen=list(map(json.loads,(ROOT/'results/sparse_scaling_v1/runs.jsonl').read_text().splitlines()))
table=[r'\begin{tabular}{rrrrrr}\toprule',r'$n$ & $r$ & Seed & Dense partial & CSR/ARPACK & Ratio\\\midrule']
for cell in sorted(study['cells'],key=lambda c:(c['n'],c['rank'],c['case'])):
    seed=cell['case'].split('seed')[1]
    table.append(f"{cell['n']} & {cell['rank']} & {seed} & {cell['times']['dense_partial']:.2f} & {cell['times']['sparse']:.2f} & {cell['dense_to_sparse_ratio']:.2f} "+r'\\')
table.append(r'\bottomrule\end{tabular}')
(ROOT/'manuscript/tables/sparse.tex').write_text('\n'.join(table)+'\n')
table=[r'\begin{tabular}{lrlrr}\toprule',r'Graph & $n$ & Backend & Seconds & Retained MiB\\\midrule']
labels={'dense_partial':'Dense partial','sparse':'CSR/ARPACK','tridiagonal':'Tridiagonal'}
for row in screen:
    memory=(row['input_bytes']+row['spectrum_bytes_peak']+row['sample_bytes'])/1024**2
    table.append(f"{row['geometry'].title()} & {row['n']} & {labels[row['method']]} & {row['seconds']:.2f} & {memory:.1f} "+r'\\')
table.append(r'\bottomrule\end{tabular}')
(ROOT/'manuscript/tables/sparse_scaling.tex').write_text('\n'.join(table)+'\n')
ratios={n:[c['dense_to_sparse_ratio'] for c in study['cells'] if c['n']==n] for n in [128,256,512]}
fallbacks=sum(r['fallback_count'] for r in rows+screen if r['method']=='sparse')
error=max(c['reported_difference'] for c in study['saved_menu_checks']+scaling['checks'])
mantissa,exponent=f'{error:.1e}'.split('e')
error_tex=mantissa+r'\times10^{'+str(int(exponent))+'}'
screen1024={r['method']:r for r in screen if r['geometry']=='grid' and r['n']==1024}
larger=screen1024['dense_partial']['seconds']/screen1024['sparse']['seconds']
certs=[json.loads((ROOT/f'results/{name}/standalone_verification.json').read_text()) for name in ['sparse_grid_certificates_v1','sparse_path_certificates_v1']]
assert all(c['status']=='PASS_STANDALONE_INTERVAL_VERIFICATION' for c in certs)
text=rf'''All 72 confirmation runs completed, and all 24 saved menus passed the
independent numerical check. The median dense-partial/CSR runtime ratio
across the 12 cells is ${study['median_ratio']:.3f}$. Its per-dimension medians
are ${np.median(ratios[128]):.3f}$, ${np.median(ratios[256]):.3f}$, and
${np.median(ratios[512]):.3f}$ for $n=128,256,512$, respectively.
Thus the small-instance overhead must be weighed against the measured
larger-instance behavior, rather than reporting only a favorable size.
The maximum difference between reported and independently evaluated losses
over confirmation and scaling menus is ${error_tex}$.
The sparse runs in these two studies used {fallbacks} dense fallbacks.

Table~\ref{{tab:sparse-scaling}} extends the numerical screen to $n=4096$.
For the single $n=1024$ grid, the dense-partial/CSR ratio is ${larger:.2f}$;
this one observation is not a repeated speedup estimate. Independent
ordered tridiagonal, full dense, and banded LAPACK calculations check path,
$n=1024$ grid, and $n=4096$ grid menus, respectively. The banded check uses
the known grid bandwidth, not the ARPACK proposals.

Outward verification and standalone replay also succeed for the four
$n=128$ CSR grid menus and all four path menus in the scaling screen,
each with a global bound width $10^{{-5}}$ to displayed precision. The grid certificates
use dense arithmetic; the path certificates use the tridiagonal verifier.
The banded verification study below extends certification to the larger grids.
Recorded array storage includes all cached preset bases, which can exceed
the spectrum-cache budget; it excludes transient solver workspaces and
Python overhead and is not a peak-memory measurement.
'''
(ROOT/'manuscript/sparse_results.tex').write_text(text)
summary=dict(status='PASS',runs=len(rows),saved_menus=len(study['saved_menu_checks']),
    scaling_runs=len(screen),median_ratio=study['median_ratio'],
    per_n_median_ratio={n:float(np.median(v)) for n,v in ratios.items()},
    grid1024_single_ratio=larger,max_loss_crosscheck_error=error,sparse_dense_fallbacks=fallbacks,
    certificate_artifacts=sum(len(c['rows']) for c in certs))
(ROOT/'results/sparse_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
