"""CSR and dense-partial spectral backends for the existing menu construction.

ARPACK eigenpairs and residual tests are numerical proposals, NOT certificates
that all lower eigenvalues or a whole multiple eigenspace were found. Final
verification must be performed independently. Dense recovery is explicit and
counted, never silently described as sparse work. Frozen v3 solvers unchanged.
"""
from collections import OrderedDict
import numpy as np
from scipy import sparse
from scipy.linalg import eigh, eigh_tridiagonal
from scipy.sparse.linalg import eigsh, ArpackNoConvergence
from reused_spectral import ReusedSpectralModel, SampleStore


class PartialSpectralModel(ReusedSpectralModel):
    def __init__(self, task, costs, overheads, rank=1, upper=2.,
                 backend='sparse', cache_bytes=32*1024**2, dense_limit=1024):
        if backend not in ['sparse','dense_partial','dense_full','tridiagonal']:
            raise ValueError('Unknown backend')
        self.backend = backend
        matrices = [sparse.csr_matrix(x,dtype=float) for x in [task,*costs]]
        for x in matrices:
            x.sum_duplicates(); x.eliminate_zeros(); x.sort_indices()
            if x.shape[0] != x.shape[1] or not np.isfinite(x.data).all():
                raise ValueError('Finite square matrices required')
            if (x-x.T).nnz:
                raise ValueError('Exactly symmetric inputs required')
        self.n = matrices[0].shape[0]
        if any(x.shape != (self.n,self.n) for x in matrices):
            raise ValueError('Inconsistent dimensions')
        self.A, self.C = matrices[0], matrices[1:]
        if backend in ['dense_partial','dense_full']:
            self.A = self.A.toarray(); self.C = [x.toarray() for x in self.C]
        self.d = np.asarray(overheads,dtype=float)
        self.rank, self.upper = int(rank), float(upper)
        if not (1 <= self.rank <= self.n and self.upper > 0 and
                len(self.C)==len(self.d)>0 and np.isfinite(self.d).all()):
            raise ValueError('Invalid model dimensions or parameters')
        self.cache = OrderedDict()
        self.cache_budget = int(cache_bytes)
        self.cache_bytes = self.cache_bytes_peak = self.cache_peak = 0
        self.eigen_calls = self.endpoint_calls = self.reuse_decisions = 0
        self.samples = [SampleStore() for _ in self.d]
        self.sample_keys = [set() for _ in self.d]
        self.dense_limit = int(dense_limit)
        self.fallbacks = []
        self.guard_expansions = 0
        self.max_scaled_residual = self.max_orthogonality_error = 0.
        self.max_returned_vectors = 0
        self.rng = np.random.default_rng(6173)

    def _solve(self, h, k, p, site):
        self.eigen_calls += 1
        if self.backend == 'tridiagonal':
            coo=h.tocoo()
            if np.any((abs(coo.row-coo.col)>1)&(coo.data!=0)):
                raise ValueError('Tridiagonal backend requires tridiagonal inputs')
            return eigh_tridiagonal(h.diagonal(),h.diagonal(1),
                                    select='i',select_range=(0,k-1))
        if self.backend == 'dense_full':
            return eigh(h,check_finite=False)
        if self.backend == 'dense_partial':
            return eigh(h,subset_by_index=[0,k-1],driver='evr',check_finite=False)
        if self.n <= 24 or k >= self.n-1:
            if self.n > self.dense_limit:
                raise ArithmeticError('Full cutoff face requires dense work above declared limit')
            self.fallbacks.append(dict(price=float(p),site=site,reason='small_or_full_face'))
            return eigh(h.toarray(),check_finite=False)
        try:
            w,v = eigsh(h,k=k,which='SA',tol=1e-13,
                         ncv=min(self.n,max(2*k+1,32)),
                         maxiter=max(1000,20*self.n),v0=self.rng.normal(size=self.n))
        except ArpackNoConvergence:
            if self.n > self.dense_limit:
                raise
            self.fallbacks.append(dict(price=float(p),site=site,reason='arpack_no_convergence'))
            return eigh(h.toarray(),check_finite=False)
        order=np.argsort(w)
        w,v=w[order],v[:,order]
        # Rayleigh-Ritz refinement in a QR-orthonormalized returned subspace.
        q,_=np.linalg.qr(v,mode='reduced')
        wr,z=eigh(q.T@(h@q),check_finite=False)
        return wr,q@z

    def spectrum(self,p,site):
        key=(float(p),int(site))
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        h=-self.A+p*self.C[site]
        scale=max(1.,float(np.asarray(abs(h).sum(axis=1)).max()))
        k=min(self.n,max(self.rank+8,2*self.rank))
        while True:
            w,v=self._solve(h,k,p,site)
            residual=np.linalg.norm(h@v-v*w,axis=0).max()/scale
            orth=np.linalg.norm(v.T@v-np.eye(v.shape[1]),ord=np.inf)
            self.max_scaled_residual=max(self.max_scaled_residual,float(residual))
            self.max_orthogonality_error=max(self.max_orthogonality_error,float(orth))
            if residual > 2e-10 or orth > 1e-9:
                raise ArithmeticError('Partial eigensystem residual/orthogonality check failed')
            # Include guard vectors beyond the cutoff cluster. This guards a
            # detected cluster, but is NOT a rigorous multiplicity count.
            if len(w)==self.n or w[-1]-w[self.rank-1] > 1e-7*scale:
                break
            k=min(self.n,max(k+8,2*k))
            self.guard_expansions += 1
        self.max_returned_vectors=max(self.max_returned_vectors,len(w))
        size=w.nbytes+v.nbytes
        while self.cache and self.cache_bytes+size > self.cache_budget:
            _,(oldw,oldv)=self.cache.popitem(last=False)
            self.cache_bytes-=oldw.nbytes+oldv.nbytes
        self.cache[key]=(w,v)
        self.cache_bytes+=size
        self.cache_bytes_peak=max(self.cache_bytes_peak,self.cache_bytes)
        self.cache_peak=max(self.cache_peak,len(self.cache))
        if p not in self.sample_keys[site]:
            u=v[:,:self.rank].copy()
            intercept=-float(np.sum(u*(self.A@u)))
            cost=float(np.sum(u*(self.C[site]@u)))+self.d[site]
            value=float(w[:self.rank].sum()+p*self.d[site])
            self.samples[site].append(p,value,cost,intercept,u)
            self.sample_keys[site].add(p)
        return w,v

    def storage(self):
        def size(x):
            return x.data.nbytes+x.indices.nbytes+x.indptr.nbytes if sparse.issparse(x) else x.nbytes
        return dict(input_bytes=sum(size(x) for x in [self.A,*self.C]),
                    spectrum_bytes_peak=self.cache_bytes_peak,
                    sample_bytes=sum(s.array.nbytes+sum(x.nbytes for x in s.bases) for s in self.samples),
                    eigensolver_calls=self.eigen_calls,guard_expansions=self.guard_expansions,
                    fallback_count=len(self.fallbacks),max_returned_vectors=self.max_returned_vectors,
                    max_scaled_residual=self.max_scaled_residual,
                    max_orthogonality_error=self.max_orthogonality_error)


def sparse_graph_model(seed,n,rank,sites=2,geometry='path',backend='sparse'):
    """Synthetic PSD graph-plus-diagonal family; no physical calibration."""
    rng=np.random.default_rng(seed)
    if geometry=='path':
        edges=np.column_stack([np.arange(n-1),np.arange(1,n)])
    elif geometry=='grid':
        width=int(np.sqrt(n))
        edges=np.array([(i,j) for i in range(n) for j in [i+1,i+width]
                        if j<n and (j!=i+1 or i//width==j//width)],dtype=int)
    else:
        raise ValueError('Unknown graph family')
    def laplacian():
        weights=rng.uniform(.05,.25,len(edges))
        rows=np.concatenate([edges[:,0],edges[:,1]])
        cols=np.concatenate([edges[:,1],edges[:,0]])
        graph=sparse.csr_matrix((np.tile(weights,2),(rows,cols)),shape=(n,n))
        return sparse.diags(np.asarray(graph.sum(axis=1)).ravel())-graph
    task=laplacian()+sparse.diags(rng.uniform(.2,2.,n))
    costs=[laplacian()+sparse.diags(rng.uniform(.1,1.5,n)) for _ in range(sites)]
    return PartialSpectralModel(task,costs,rng.uniform(0.,.15,sites),rank,
                                backend=backend)
