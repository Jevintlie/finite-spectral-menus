"""Fresh unseen-seed menu, then generation and independent replay of its bounds."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import subprocess
import sys
import numpy as np
from spectral_menu import random_model
from reused_spectral import as_reused

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results/smoke_run'
OUT.mkdir(parents=True,exist_ok=False)
model=as_reused(random_model(5600,8,2,2))
result=model.minimax(2,loss_tol=2e-6,price_tol=2e-8,oracle_tol=1e-9)
np.savez_compressed(OUT/'n8_r2_s2_seed5600_K2_reused.npz',A=model.A,C=model.C,d=model.d,
    rank=model.rank,upper=model.upper,bases=[x['basis'] for x in result['segments']],
    segments=[[x['left'],x['right']] for x in result['segments']])
subprocess.run([sys.executable,'certify_artifacts.py','--source','results/smoke_run',
                '--output','results/smoke_certificates'],cwd=ROOT,check=True)
subprocess.run([sys.executable,'check_certificates.py','--source','results/smoke_run',
                '--certificates','results/smoke_certificates'],cwd=ROOT,check=True)
