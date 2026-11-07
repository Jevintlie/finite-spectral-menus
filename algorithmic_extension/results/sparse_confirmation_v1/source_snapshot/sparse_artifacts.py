"""Compact CSR input and menu serialization; no solver imports."""
import numpy as np
from scipy import sparse


def save(path,model,result):
    data=dict(n=model.n,rank=model.rank,upper=model.upper,d=model.d,
              bases=np.array([s['basis'] for s in result['segments']]),
              segments=np.array([[s['left'],s['right']] for s in result['segments']]))
    for index,matrix in enumerate([model.A,*model.C]):
        x=sparse.csr_matrix(matrix)
        data.update({f'x{index}_data':x.data,f'x{index}_indices':x.indices,
                     f'x{index}_indptr':x.indptr})
    np.savez_compressed(path,**data)


def load(path):
    with np.load(path) as z:
        n=int(z['n']);d=z['d']
        matrices=[sparse.csr_matrix((z[f'x{i}_data'],z[f'x{i}_indices'],z[f'x{i}_indptr']),
                                   shape=(n,n)) for i in range(len(d)+1)]
        return dict(task=matrices[0],costs=matrices[1:],overheads=d,rank=int(z['rank']),
                    upper=float(z['upper'])),z['bases'],z['segments']
