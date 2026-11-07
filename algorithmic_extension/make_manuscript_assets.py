"""Generate manuscript tables/figure only from saved evidence and exact formulas."""
from pathlib import Path
import json
import statistics
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'manuscript'
(OUT/'tables').mkdir(exist_ok=True)
(OUT/'figures').mkdir(exist_ok=True)
warm=json.loads((ROOT/'results/warm_confirmation_v1/analysis.json').read_text())
assert warm['status']=='PASS' and warm['runs']==198
lines=[r'\begin{tabular}{rrrrrr}',r'\toprule',
       r'$n$ & $r$ & Sites & Warm Brent & Hybrid Brent & Max. MiB\\',r'\midrule']
for n,r,s in [(8,1,1),(16,4,3),(32,8,6),(64,4,3),(64,16,3)]:
    cells=[x for x in warm['paired_cells'] if x['case'].startswith(f'n{n}_r{r}_s{s}_')]
    first=[x['reference_over_reused'] for x in cells if x['reference']=='warm_brent']
    second=[x['reference_over_reused'] for x in cells if x['reference']=='hybrid_brent']
    assert len(first)==len(second)==4
    mem=max(x['reused_retained_bytes'] for x in cells)/2**20
    lines.append(f'{n} & {r} & {s} & {statistics.median(first):.3f} & {statistics.median(second):.3f} & {mem:.1f}'+r'\\')
lines.extend([r'\bottomrule',r'\end{tabular}'])
(OUT/'tables/warm.tex').write_text('\n'.join(lines)+'\n')

rows=[json.loads(x) for x in (ROOT/'results/dictionary_comparison_v2/runs.jsonl').read_text().splitlines()]
lines=[r'\begin{tabular}{lrrrrrr}',r'\toprule',
       r'Case & $K$ & Reuse (s) & Uniform (s) & Met? & Adaptive (s) & Met?\\',r'\midrule']
counts={'uniform':0,'adaptive':0}
for ref in (x for x in rows if x['method']=='reused'):
    name,k=ref['case'],ref['K']
    display={'mirror':'Mirror','commuting_collision':'Collision'}.get(name,
        name.replace('_seed5200','').replace('_',r'\,'))
    values=[]
    for method in ('uniform','adaptive'):
        selected=[x for x in rows if x['case']==name and x['K']==k and x['method']==method]
        stage=selected[-2]; final=selected[-1]
        assert final['stage']=='final_verification'
        counts[method]+=int(final['target_met'])
        values += [f"{stage['cumulative_seconds']:.3f}", 'Yes' if final['target_met'] else 'No']
    lines.append(f"{display} & {k} & {ref['seconds']:.3f} & "+' & '.join(values)+r'\\')
lines.extend([r'\bottomrule',r'\end{tabular}'])
assert counts=={'uniform':1,'adaptive':6},counts
(OUT/'tables/dictionary.tex').write_text('\n'.join(lines)+'\n')

special=json.loads((ROOT/'results/special_case_comparison.json').read_text())
lines=[r'\begin{tabular}{rrr}',r'\toprule',r'$K$ & Analytic (s) & General reuse (s)\\',r'\midrule']
for row in special['pairs']:
    lines.append(f"{row['K']} & {row['analytic_seconds']:.4f} & {row['reused_seconds']:.4f}"+r'\\')
lines.extend([r'\bottomrule',r'\end{tabular}'])
(OUT/'tables/special.tex').write_text('\n'.join(lines)+'\n')

plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(9.4,3.25),layout='constrained')
p=np.linspace(0,1,501)
axes[0].plot(p,np.minimum(-1+2*p,0),color='black',lw=2,label='Shared adaptive value F')
axes[0].plot(p,p-.5,color='#0072B2',label='Model S optimal preset')
axes[0].plot(p,p-.25,color='#D55E00',ls='--',label='Model M optimal preset')
axes[0].set(xlabel='Price p',ylabel='Objective',xlim=(0,1))
axes[0].legend(frameon=False,fontsize=8)
t=np.linspace(0,1,501)
axes[1].plot(t,np.maximum(1-t,t),color='#0072B2',label='Model S')
axes[1].plot(t,np.maximum(1-t,np.minimum(2-t,3*t)),color='#D55E00',ls='--',label='Model M')
axes[1].scatter([.5,.25],[.5,.75],color=['#0072B2','#D55E00'],s=30,zorder=5)
axes[1].annotate('(1/2, 1/2)',(.5,.5),xytext=(7,8),textcoords='offset points')
axes[1].annotate('(1/4, 3/4)',(.25,.75),xytext=(-50,-20),textcoords='offset points')
axes[1].set(xlabel='Preset coordinate weight t',ylabel='Worst regret',xlim=(0,1),ylim=(.4,1.6))
axes[1].legend(frameon=False,fontsize=8)
fig.savefig(OUT/'figures/structural.pdf')
fig.savefig(OUT/'figures/structural.png',dpi=170)
plt.close(fig)
report={'status':'PASS','dictionary_target_counts':counts,
        'warm_summary':warm['new_seed_summaries'],'special_case':special['pairs']}
(OUT/'asset_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
