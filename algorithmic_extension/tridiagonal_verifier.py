"""Outward Sturm-count verification for symmetric tridiagonal menu inputs.

Independent of ARPACK/menu solvers. Exact binary64 inputs; correctly rounded
elementary operations and nextafter are assumed, as in interval_verifier.py.
Every successful count certifies pivot signs of exact LDL^T by intervals.
Unresolved pivots reject a proposal. No full dense matrix is formed.
"""
import math
import numpy as np
from scipy import sparse
from scipy.linalg import eigh_tridiagonal
from interval_verifier import (IntervalVerifier,point,add,sub,mul,matmul,
                               sum_interval,norm_symmetric_upper)


def scalar_sub(a,b):
    return math.nextafter(a[0]-b[1],-math.inf),math.nextafter(a[1]-b[0],math.inf)


def scalar_mul(a,b):
    vals=[x*y for x in a for y in b]
    return math.nextafter(min(vals),-math.inf),math.nextafter(max(vals),math.inf)


def scalar_div(a,b):
    if b[0]<=0<=b[1]:
        raise ArithmeticError('Unresolved Sturm pivot')
    vals=[x/y for x in a for y in b]
    return math.nextafter(min(vals),-math.inf),math.nextafter(max(vals),math.inf)


class TridiagonalVerifier(IntervalVerifier):
    def __init__(self,a,c,d,rank,upper):
        matrices=[sparse.csr_matrix(x,dtype=float) for x in [a,*c]]
        self.n=matrices[0].shape[0]
        for x in matrices:
            if x.shape!=(self.n,self.n) or (x-x.T).nnz or not np.isfinite(x.data).all():
                raise ValueError('Exactly symmetric finite square inputs required')
            coo=x.tocoo()
            if np.any((abs(coo.row-coo.col)>1)&(coo.data!=0)):
                raise ValueError('Tridiagonal verifier cannot certify general sparse inputs')
        self.ad=matrices[0].diagonal();self.ae=matrices[0].diagonal(1)
        self.cd=[x.diagonal() for x in matrices[1:]]
        self.ce=[x.diagonal(1) for x in matrices[1:]]
        self.d=np.asarray(d,dtype=float);self.rank=int(rank);self.upper=float(upper)
        if not (1<=self.rank<=self.n and len(self.d)==len(self.cd)>0 and self.upper>0):
            raise ValueError('Invalid dimensions')
        if not np.isfinite(self.d).all():raise ValueError('Nonfinite overhead')
        self.eigen_cache={};self.f_cache={};self.sturm_counts=0

    def diagonals(self,p,site):
        return (sub(mul(point(p),point(self.cd[site])),point(self.ad)),
                sub(mul(point(p),point(self.ce[site])),point(self.ae)))

    def count(self,p,site,x):
        diagonal,off=self.diagonals(p,site)
        pivot=None;count=0
        for i in range(self.n):
            current=scalar_sub((float(diagonal[0][i]),float(diagonal[1][i])),(x,x))
            if i:
                e=(float(off[0][i-1]),float(off[1][i-1]))
                current=scalar_sub(current,scalar_div(scalar_mul(e,e),pivot))
            if not all(math.isfinite(v) for v in current) or current[0]<=0<=current[1]:
                raise ArithmeticError('Unresolved Sturm pivot')
            count += current[1]<0
            pivot=current
        self.sturm_counts+=1
        return int(count)

    def branch(self,p,site):
        key=(float(p),int(site))
        if key in self.eigen_cache:return self.eigen_cache[key]
        diag=-self.ad+p*self.cd[site];off=-self.ae+p*self.ce[site]
        proposed=eigh_tridiagonal(diag,off,eigvals_only=True,
                                   select='i',select_range=(0,self.rank-1))
        scale=max(1.,float(abs(diag).max())+2*float(abs(off).max(initial=0.)))
        intervals=[]
        for j,w in enumerate(proposed):
            radius=1e-12*scale
            for attempt in range(18):
                lo=math.nextafter(float(w)-radius,-math.inf)
                hi=math.nextafter(float(w)+radius,math.inf)
                try:
                    if self.count(p,site,lo)<=j and self.count(p,site,hi)>=j+1:
                        intervals.append((lo,hi));break
                except ArithmeticError:
                    pass
                radius*=4
            else:raise ArithmeticError('Cannot enclose ordered eigenvalue with Sturm counts')
        result=add(sum_interval((np.array([v[0] for v in intervals]),np.array([v[1] for v in intervals]))),
                   mul(point(p),point(self.d[site])))
        out=(float(result[0]),float(result[1]))
        self.eigen_cache[key]=out
        return out

    def objective(self,u,p,site):
        if u.shape!=(self.n,self.rank):raise ValueError('Invalid basis shape')
        gram=matmul(point(u.T),point(u))
        eta=norm_symmetric_upper(sub(gram,point(np.eye(self.rank))))
        if eta>=1:raise ArithmeticError('Cannot certify full-rank preset')
        diagonal,off=self.diagonals(p,site)
        rows=np.maximum(abs(diagonal[0]),abs(diagonal[1]))
        edges=np.maximum(abs(off[0]),abs(off[1]))
        # Outward accumulation of an absolute row-sum norm bound.
        rows[:-1]=np.nextafter(rows[:-1]+edges,np.inf)
        rows[1:]=np.nextafter(rows[1:]+edges,np.inf)
        norm=float(rows.max())
        value=point(0.)
        for col in u.T:
            value=add(value,sum_interval(mul(diagonal,mul(point(col),point(col)))))
            cross=mul(off,mul(point(col[:-1]),point(col[1:])))
            value=add(value,mul(point(2.),sum_interval(cross)))
        error=mul(mul(point(self.rank),point(norm)),point(eta))[1]
        return add(add(value,(-error,error)),mul(point(p),point(self.d[site])))
