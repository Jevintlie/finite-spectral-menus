"""Generate checked banded-certificate results and table for the manuscript."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
source=ROOT/'results/banded_certificates_v2'
summary=json.loads((source/'summary.json').read_text())
replay=json.loads((source/'standalone_verification.json').read_text())
assert summary['status']=='PASS' and replay['status']=='PASS_STANDALONE_BANDED_VERIFICATION'
assert len(summary['rows'])==14
assert max(r['gap'] for r in summary['rows'])<1.01e-5
rows=summary['rows'];dec=sum(r['decimal_counts'] for r in rows)
table=[r'\begin{tabular}{rrrrr}\toprule',r'$n$ & Menus & Half-bandwidth & Decimal counts & Max. gap / $10^{-5}$\\\midrule']
for n in sorted({r['n'] for r in rows}):
    group=[r for r in rows if r['n']==n]
    table.append(f"{n} & {len(group)} & {group[0]['half_bandwidth']} & {sum(r['decimal_counts'] for r in group)} & {max(r['gap'] for r in group)*1e5:.6f} "+r'\\')
table.append(r'\bottomrule\end{tabular}')
(ROOT/'manuscript/tables/banded.tex').write_text('\n'.join(table)+'\n')
text=rf'''\paragraph{{Outward verification of every CSR grid menu.}}
A further verification study certifies all 12 CSR confirmation menus and
both CSR grid scaling menus, through $n=4096$, using interval $LDL^T$
elimination in band storage. All 14 certificates pass standalone replay,
with global gaps below $1.01\times10^{{-5}}$ (Table~\ref{{tab:banded}}).
This strengthens the preceding numerical checks without changing any
optimizer, saved menu, or isolated runtime measurement.

An initial binary64 interval implementation rejected a rank-eight witness
because its eigenvalue brackets became too wide to prove exclusion. That
attempt is retained. The revised verifier retries unresolved counts at
$n\le512$ with directed 50-digit decimal intervals; {dec} counts use this
path. Both larger grid cases need only outward binary64 arithmetic.
The final checker independently encloses ordered eigenvalue sums and actual
polar-orthonormalized projectors; it imports no menu solver. Six CPU
processes check independent price/site pairs. These parallel verification
times are separate from the isolated optimization study.

For half-bandwidth $b$, each unpivoted inertia count uses $O(nb^2)$ work
and $O(nb+b^2)$ storage. The grid has $b=\lfloor\sqrt n\rfloor$;
at $n=4096$, packed input bands occupy about 6.1 MiB and an interval factor
about 4.1 MiB per worker, excluding temporary arrays and process overhead.
This is an advantage of band structure, not a guarantee for arbitrary
sparse graphs. Ambiguous pivots cause rejection; high bandwidth can erase
the storage benefit. Appendix~\ref{{app:sturm}} gives the factorization
argument and arithmetic assumptions.

\begin{{table}}[t]\centering\small
\caption{{Independently replayed outward certificates for CSR grid menus.
Decimal counts record successful higher-precision inertia retries;
the displayed gap column is rounded. All unrounded gaps are below
$1.01\times10^{{-5}}$.}}
\label{{tab:banded}}\input{{tables/banded.tex}}
\end{{table}}
'''
(ROOT/'manuscript/banded_results.tex').write_text(text)
print('Generated banded results and certificate table')
