"""Independent outward-rounded verification for saved spectral-menu witnesses.

Inputs are interpreted as exact binary64 numbers. Elementary numpy operations
are widened with nextafter; matrix products use explicit interval sums, not
BLAS. Assumes IEEE-754 correctly rounded binary64 elementary +,-,*,/ operations
with gradual underflow. Eigensolvers only propose a basis/diagonal: the bounds
are checked independently by interval congruence and norm estimates.

This module is experimental until its proof and arithmetic tests are reviewed.
"""
import numpy as np


def point(x):
    x=np.asarray(x,dtype=np.float64)
    assert np.isfinite(x).all()
    return x,x


def down(x):
    return np.nextafter(x,-np.inf)


def up(x):
    return np.nextafter(x,np.inf)


def add(a,b):
    return down(a[0]+b[0]),up(a[1]+b[1])


def neg(a):
    return -a[1],-a[0]


def sub(a,b):
    return add(a,neg(b))


def mul(a,b):
    products=np.array([a[0]*b[0],a[0]*b[1],a[1]*b[0],a[1]*b[1]])
    return down(products.min(axis=0)),up(products.max(axis=0))


def divide_positive(a,b):
    assert np.all(b[0]>0)
    return mul(a,(down(1./b[1]),up(1./b[0])))


def transpose(a):
    return a[0].T,a[1].T


def matmul(a,b):
    assert a[0].ndim==b[0].ndim==2 and a[0].shape[1]==b[0].shape[0]
    out=point(np.zeros((a[0].shape[0],b[0].shape[1])))
    for k in range(a[0].shape[1]):
        out=add(out,mul((a[0][:,k,None],a[1][:,k,None]),
                        (b[0][None,k,:],b[1][None,k,:])))
    assert np.isfinite(out[0]).all() and np.isfinite(out[1]).all()
    return out


def sum_interval(a):
    out=point(0.)
    for lo,hi in zip(a[0].flat,a[1].flat):
        out=add(out,(lo,hi))
    return out


def norm_symmetric_upper(a):
    # The exact enclosed matrix must be symmetric. A row-sum bound then bounds
    # its spectral norm, even if the enclosing interval box is not symmetric.
    absolute=np.maximum(abs(a[0]),abs(a[1]))
    total=np.zeros(absolute.shape[0])
    for j in range(absolute.shape[1]):
        total=up(total+absolute[:,j])
    return float(total.max())


class IntervalVerifier:
    def __init__(self,a,c,d,rank,upper):
        self.a=np.asarray(a,dtype=float)
        self.c=np.asarray(c,dtype=float)
        self.d=np.asarray(d,dtype=float)
        self.rank=int(rank)
        self.upper=float(upper)
        self.n=len(self.a)
        assert np.array_equal(self.a,self.a.T),'Input must be exactly symmetric.'
        assert all(np.array_equal(x,x.T) for x in self.c)
        self.eigen_cache={}
        self.f_cache={}

    def matrix(self,p,site):
        return add(neg(point(self.a)),mul(point(p),point(self.c[site])))

    def branch(self,p,site):
        key=(float(p),int(site))
        if key in self.eigen_cache:
            return self.eigen_cache[key]
        h=self.matrix(p,site)
        w,v=np.linalg.eigh(-self.a+p*self.c[site])
        gram=matmul(point(v.T),point(v))
        eta=norm_symmetric_upper(sub(gram,point(np.eye(self.n))))
        assert eta<1.,'Congruence basis not certified invertible.'
        b=matmul(point(v.T),matmul(h,point(v)))
        rho=norm_symmetric_upper(sub(b,point(np.diag(w))))
        delta=divide_positive(add(point(rho),mul(point(abs(w).max()),point(eta))),
                              sub(point(1.),point(eta)))[1]
        center=sum_interval(point(w[:self.rank]))
        error=mul(point(self.rank),point(delta))[1]
        result=add(add(center,(-error,error)),mul(point(p),point(self.d[site])))
        out=(float(result[0]),float(result[1]))
        self.eigen_cache[key]=out
        return out

    def optimum(self,p):
        if p not in self.f_cache:
            values=[self.branch(p,s) for s in range(len(self.d))]
            self.f_cache[p]=min(x[0] for x in values),min(x[1] for x in values)
        return self.f_cache[p]

    def objective(self,u,p,site):
        # Interpret the stored basis as its exact polar orthonormalization Q.
        # ||UU^T-QQ^T||_* <= rank * ||U^T U-I||_2.
        assert u.shape==(self.n,self.rank)
        gram=matmul(point(u.T),point(u))
        eta=norm_symmetric_upper(sub(gram,point(np.eye(self.rank))))
        assert eta<1.,'Preset basis not certified full rank.'
        h=self.matrix(p,site)
        b=matmul(point(u.T),matmul(h,point(u)))
        center=sum_interval((np.diag(b[0]),np.diag(b[1])))
        error=mul(mul(point(self.rank),point(norm_symmetric_upper(h))),point(eta))[1]
        return add(add(center,(-error,error)),mul(point(p),point(self.d[site])))

    def menu_upper(self,bases,segments):
        assert len(bases)==len(segments)
        assert segments[0,0]==0. and segments[-1,1]==self.upper
        assert np.array_equal(segments[:-1,1],segments[1:,0])
        rows=[]
        for u,(a,b) in zip(bases,segments):
            assert 0<=a<=b<=self.upper
            bounds=[]
            for site in range(len(self.d)):
                values=[float(sub(self.objective(u,p,site),self.optimum(p))[1]) for p in (a,b)]
                bounds.append(max(values))
            # Choose one fixed site for this whole segment. Convex regret then
            # extends both endpoint bounds to the complete closed segment.
            rows.append({'left':float(a),'right':float(b),'upper':min(bounds),
                         'site':int(np.argmin(bounds))})
        return {'upper':max(x['upper'] for x in rows),'segments':rows}

    def pair_lower(self,a,b,prices):
        assert a<b and len(prices)==len(self.d)
        vals=[]
        for site,p in enumerate(prices):
            assert a<=p<=b
            t=divide_positive(sub(point(p),point(a)),sub(point(b),point(a)))
            chord=add(mul(sub(point(1.),t),self.optimum(a)),mul(t,self.optimum(b)))
            value=sub(self.branch(p,site),chord)
            vals.append(float(value[0]))
        return {'lower':min(vals),'site_lower_bounds':vals}
