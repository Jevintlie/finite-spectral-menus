"""Independent outward LDL inertia and polar traces in symmetric band storage.

Exact binary64 inputs; elementary IEEE-754 arithmetic with gradual underflow.
No pivoting: ambiguous/nonfinite pivots fail closed. LAPACK only proposes
eigenvalue brackets. Cost depends on bandwidth, not original sparsity alone.
"""
import numpy as np
from decimal import Decimal,Context,ROUND_FLOOR,ROUND_CEILING,Underflow
from scipy import sparse
from scipy.linalg import eigvals_banded
from interval_verifier import (IntervalVerifier,point,add,sub,mul,
                               norm_symmetric_upper)


def tree_sum(a):
    """Outward pairwise reduction, using only elementary additions."""
    lo=np.asarray(a[0],dtype=float).ravel().copy()
    hi=np.asarray(a[1],dtype=float).ravel().copy()
    if not len(lo):return point(0.)
    while len(lo)>1:
        if len(lo)%2:
            lo=np.append(lo,0.);hi=np.append(hi,0.)
        lo=np.nextafter(lo[::2]+lo[1::2],-np.inf)
        hi=np.nextafter(hi[::2]+hi[1::2],np.inf)
    if not np.isfinite([lo[0],hi[0]]).all():raise ArithmeticError('Nonfinite interval sum')
    return float(lo[0]),float(hi[0])


def signed_div(a,pivot):
    if not np.isfinite(pivot).all() or pivot[0]<=0<=pivot[1]:
        raise ArithmeticError('Unresolved LDL pivot')
    vals=np.array([a[0]/pivot[0],a[0]/pivot[1],a[1]/pivot[0],a[1]/pivot[1]])
    return np.nextafter(vals.min(axis=0),-np.inf),np.nextafter(vals.max(axis=0),np.inf)


class BandedVerifier(IntervalVerifier):
    def __init__(self,a,c,d,rank,upper,max_bandwidth=256):
        matrices=[sparse.csr_matrix(x,dtype=float) for x in [a,*c]]
        self.n=matrices[0].shape[0]
        width=0
        for x in matrices:
            x.sum_duplicates();x.eliminate_zeros();x.sort_indices()
            if x.shape!=(self.n,self.n) or (x-x.T).nnz or not np.isfinite(x.data).all():
                raise ValueError('Exactly symmetric finite square matrices required')
            coo=x.tocoo()
            width=max(width,int(np.max(abs(coo.row-coo.col),initial=0)))
        if width>max_bandwidth:raise ValueError('Half-bandwidth exceeds declared storage limit')
        self.width=width
        packed=[]
        for x in matrices:
            ab=np.zeros((width+1,self.n))
            for k in range(width+1):ab[k,:self.n-k]=x.diagonal(-k)
            packed.append(ab)
        self.ab,self.cb=packed[0],packed[1:]
        self.d=np.asarray(d,dtype=float);self.rank=int(rank);self.upper=float(upper)
        if not (1<=self.rank<=self.n and len(self.d)==len(self.cb)>0 and
                np.isfinite(self.d).all() and np.isfinite(self.upper) and self.upper>0):
            raise ValueError('Invalid dimensions or parameters')
        self.eigen_cache={};self.f_cache={}
        self.counts=self.rejected_counts=self.bracket_expansions=self.decimal_counts=0
        self.indices=np.tril_indices(width)

    def bands(self,p,site):
        return sub(mul(point(p),point(self.cb[site])),point(self.ab))

    def count(self,p,site,x):
        lo,hi=self.bands(p,site)
        lo[0],hi[0]=sub((lo[0],hi[0]),point(x))
        negative=0
        with np.errstate(over='ignore',invalid='ignore',divide='ignore'):
            for i in range(self.n):
                pivot=(float(lo[0,i]),float(hi[0,i]))
                if not np.isfinite(pivot).all() or pivot[0]<=0<=pivot[1]:
                    self.rejected_counts+=1
                    raise ArithmeticError(f'Unresolved band LDL pivot at {i}')
                negative+=pivot[1]<0
                m=min(self.width,self.n-i-1)
                if not m:continue
                rr,cc=self.indices if m==self.width else np.tril_indices(m)
                column=(lo[1:m+1,i],hi[1:m+1,i])
                product=mul((column[0][rr],column[1][rr]),(column[0][cc],column[1][cc]))
                update=signed_div(product,pivot)
                band,cols=rr-cc,i+1+cc
                lo[band,cols],hi[band,cols]=sub((lo[band,cols],hi[band,cols]),update)
        self.counts+=1
        return int(negative)

    def branch(self,p,site):
        key=(float(p),int(site))
        if key in self.eigen_cache:return self.eigen_cache[key]
        h=-self.ab+p*self.cb[site]
        proposed=eigvals_banded(h,lower=True,select='i',select_range=(0,self.rank-1))
        scale=max(1.,float(abs(h[0]).max())+2*float(abs(h[1:]).sum(axis=0).max(initial=0.)))
        intervals=[]
        for j,w in enumerate(proposed):
            radius=1e-11*scale
            for attempt in range(14):
                low=float(np.nextafter(w-radius,-np.inf));high=float(np.nextafter(w+radius,np.inf))
                try:
                    if self.certified_count(p,site,low)<=j and self.certified_count(p,site,high)>=j+1:
                        intervals.append((low,high));break
                except ArithmeticError:pass
                radius*=4.;self.bracket_expansions+=1
            else:raise ArithmeticError('Failed to certify an ordered band eigenvalue')
        result=add(tree_sum((np.array([x[0] for x in intervals]),np.array([x[1] for x in intervals]))),
                   mul(point(p),point(self.d[site])))
        out=(float(result[0]),float(result[1]));self.eigen_cache[key]=out
        return out

    def count_decimal(self,p,site,x):
        """Same band elimination with explicitly directed 50-digit arithmetic."""
        down=Context(prec=50,rounding=ROUND_FLOOR);up=Context(prec=50,rounding=ROUND_CEILING)
        down.traps[Underflow]=up.traps[Underflow]=True
        def minus(a,b):return down.subtract(a[0],b[1]),up.subtract(a[1],b[0])
        def times(a,b):
            return (min(down.multiply(v,w) for v in a for w in b),
                    max(up.multiply(v,w) for v in a for w in b))
        def divide(a,b):
            if b[0]<=0<=b[1]:raise ArithmeticError('Unresolved decimal pivot')
            return (min(down.divide(v,w) for v in a for w in b),
                    max(up.divide(v,w) for v in a for w in b))
        dp=Decimal.from_float(float(p));dx=Decimal.from_float(float(x))
        zero=Decimal(0);ab=[[(zero,zero) for _ in range(self.n)] for _ in range(self.width+1)]
        for k in range(self.width+1):
            for i in range(self.n-k):
                a=Decimal.from_float(float(self.ab[k,i]));c=Decimal.from_float(float(self.cb[site][k,i]))
                val=minus(times((dp,dp),(c,c)),(a,a))
                ab[k][i]=minus(val,(dx,dx)) if k==0 else val
        count=0
        for i in range(self.n):
            pivot=ab[0][i]
            if not all(v.is_finite() for v in pivot) or pivot[0]<=0<=pivot[1]:
                raise ArithmeticError(f'Unresolved decimal band pivot at {i}')
            count+=pivot[1]<0
            m=min(self.width,self.n-i-1)
            for rr in range(m):
                for cc in range(rr+1):
                    delta=divide(times(ab[rr+1][i],ab[cc+1][i]),pivot)
                    ab[rr-cc][i+1+cc]=minus(ab[rr-cc][i+1+cc],delta)
        self.counts+=1;self.decimal_counts+=1
        return int(count)

    def certified_count(self,p,site,x):
        try:return self.count(p,site,x)
        except ArithmeticError:
            if self.n>512:raise
            return self.count_decimal(p,site,x)

    def objective(self,u,p,site):
        if u.shape!=(self.n,self.rank) or not np.isfinite(u).all():raise ValueError('Invalid basis')
        gl=np.empty((self.rank,self.rank));gh=np.empty_like(gl)
        for i in range(self.rank):
            for j in range(self.rank):
                gl[i,j],gh[i,j]=tree_sum(mul(point(u[:,i]),point(u[:,j])))
        eta=norm_symmetric_upper(sub((gl,gh),point(np.eye(self.rank))))
        if eta>=1:raise ArithmeticError('Preset is not certified full rank')
        bands=self.bands(p,site)
        absolute=np.maximum(abs(bands[0]),abs(bands[1]))
        rows=absolute[0].copy()
        value=point(0.)
        for k in range(self.width+1):
            length=self.n-k
            if k:
                rows[:length]=np.nextafter(rows[:length]+absolute[k,:length],np.inf)
                rows[k:]=np.nextafter(rows[k:]+absolute[k,:length],np.inf)
            for col in u.T:
                term=mul((bands[0][k,:length],bands[1][k,:length]),mul(point(col[k:]),point(col[:length])))
                contribution=tree_sum(term)
                if k:contribution=mul(point(2.),contribution)
                value=add(value,contribution)
        error=mul(mul(point(self.rank),point(float(rows.max()))),point(eta))[1]
        result=add(add(value,(-error,error)),mul(point(p),point(self.d[site])))
        if not np.isfinite(result).all():raise ArithmeticError('Nonfinite objective enclosure')
        return result

    def storage(self):
        return dict(n=self.n,half_bandwidth=self.width,
                    input_band_bytes=self.ab.nbytes+sum(x.nbytes for x in self.cb),
                    factor_interval_bytes=2*self.ab.nbytes,
                    successful_counts=self.counts,rejected_counts=self.rejected_counts,
                    bracket_expansions=self.bracket_expansions,decimal_counts=self.decimal_counts)
