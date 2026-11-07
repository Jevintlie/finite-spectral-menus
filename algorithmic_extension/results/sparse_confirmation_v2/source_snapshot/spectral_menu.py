"""Experimental general-rank continuous-price menu solver.

Known ingredients: two-objective spectral minimax / fair PCA, interval greedy.
Reported primal/dual bounds use floating point, not outward-rounded arithmetic.
"""
from dataclasses import dataclass
from collections import OrderedDict
import numpy as np
from scipy.linalg import eigh


@dataclass
class EndpointResult:
    lower: float
    upper: float
    basis: np.ndarray
    site: int
    price: float
    iterations: int


class SpectralModel:
    def __init__(self, task, costs, overheads, rank=1, upper=2.):
        self.A = np.asarray(task, dtype=float)
        self.C = np.asarray(costs, dtype=float)
        self.d = np.asarray(overheads, dtype=float)
        self.n = self.A.shape[0]
        self.rank = int(rank)
        self.upper = float(upper)
        assert self.A.shape == (self.n, self.n)
        assert self.C.shape == (len(self.d), self.n, self.n)
        assert 1 <= self.rank <= self.n and self.upper > 0
        assert np.allclose(self.A, self.A.T)
        assert np.allclose(self.C, self.C.transpose(0, 2, 1))
        assert all(np.isfinite(x).all() for x in (self.A, self.C, self.d))
        self.cache = OrderedDict()
        self.cache_limit = max(4, (32*1024*1024)//(8*(self.n*self.n+self.n)))
        self.cache_peak = 0
        self.eigen_calls = 0
        self.endpoint_calls = 0

    def spectrum(self, p, site):
        key = (float(p), site)
        if key not in self.cache:
            w, v = eigh(-self.A+p*self.C[site], check_finite=False)
            self.cache[key] = w, v
            self.eigen_calls += 1
            if len(self.cache) > self.cache_limit:
                self.cache.popitem(last=False)
            self.cache_peak = max(self.cache_peak, len(self.cache))
        else:
            self.cache.move_to_end(key)
        return self.cache[key]

    def branch(self, p, site):
        w, _ = self.spectrum(p, site)
        return float(w[:self.rank].sum()+p*self.d[site])

    def optimum(self, p):
        return min(self.branch(p, i) for i in range(len(self.d)))

    def optimal_basis(self, p):
        site = min(range(len(self.d)), key=lambda i: self.branch(p, i))
        return self.spectrum(p, site)[1][:, :self.rank].copy()

    def line(self, basis):
        intercept = -float(np.sum(basis*(self.A@basis)))
        slopes = [float(np.sum(basis*(c@basis)))+d for c, d in zip(self.C, self.d)]
        site = int(np.argmin(slopes))
        return intercept, slopes[site], site

    def _face_basis(self, p, site, target, tol):
        """Recover an actual orthonormal basis near a spectral minimizing face.

        Near-eigenvalue grouping is only a numerical construction. Every returned
        basis is checked through its actual primal objective by the caller.
        """
        w, v = self.spectrum(p, site)
        band = max(32*np.finfo(float).eps*max(1., abs(w).max()),
                   tol/(8*self.rank))
        fixed = v[:, w < w[self.rank-1]-band]
        tied = v[:, abs(w-w[self.rank-1]) <= band]
        k = self.rank-fixed.shape[1]
        wc, vc = eigh(tied.T@self.C[site]@tied, check_finite=False)
        tied = tied@vc
        base = float(np.sum(fixed*(self.C[site]@fixed)))+self.d[site]
        cmin, cmax = base+wc[:k].sum(), base+wc[-k:].sum()
        if cmax-cmin <= np.finfo(float).eps*max(1., abs(cmax)):
            return np.column_stack((fixed, tied[:, :k])), float(cmin), float(cmax)
        fraction = float(np.clip((target-cmin)/(cmax-cmin), 0., 1.))
        low, high = set(range(k)), set(range(len(wc)-k, len(wc)))
        columns = [fixed[:, j] for j in range(fixed.shape[1])]
        columns += [tied[:, j] for j in sorted(low & high)]
        for i, j in zip(sorted(low-high), sorted(high-low)):
            columns.append(np.sqrt(1-fraction)*tied[:, i]+np.sqrt(fraction)*tied[:, j])
        return np.column_stack(columns), float(cmin), float(cmax)

    def _site_endpoint(self, a, b, fa, fb, site, tol, decision=None, maxiter=100):
        slope = (fb-fa)/(b-a)
        lower = -np.inf
        best = None
        lo, hi = a, b
        for it in range(maxiter):
            p = a if it == 0 else b if it == 1 else (lo+hi)/2
            value = self.branch(p, site)-fa-(p-a)*slope
            lower = max(lower, value)
            basis, cmin, cmax = self._face_basis(p, site, slope, tol)
            intercept = -float(np.sum(basis*(self.A@basis)))
            cost = float(np.sum(basis*(self.C[site]@basis)))+self.d[site]
            upper = max(intercept+a*cost-fa, intercept+b*cost-fb)
            if best is None or upper < best.upper:
                best = EndpointResult(lower, upper, basis, site, p, it+1)
            best.lower, best.iterations = lower, it+1
            if best.upper-lower <= tol:
                return best
            if decision is not None and (lower > decision or best.upper <= decision):
                return best
            if cmin > slope:
                lo = p
            elif cmax < slope:
                hi = p
            else:
                # A numerically grouped face should have closed the gap. If
                # cancellation precludes requested accuracy, don't claim success.
                break
        if best.upper-lower > max(tol, 1e-11*max(1., abs(best.upper), abs(lower))):
            raise ArithmeticError(f'Endpoint gap unresolved: {best.upper-lower:g}')
        return best

    def endpoint(self, a, b, tol=1e-9, decision=None):
        assert 0 <= a <= b <= self.upper
        self.endpoint_calls += 1
        fa, fb = self.optimum(a), self.optimum(b)
        if a == b:
            u = self.optimal_basis(a)
            return EndpointResult(0., 0., u, self.line(u)[2], a, 0)
        lower, best = np.inf, None
        for site in range(len(self.d)):
            out = self._site_endpoint(a, b, fa, fb, site, tol, decision)
            lower = min(lower, out.lower)
            if best is None or out.upper < best.upper:
                best = out
            if decision is not None and out.upper <= decision:
                # Sites not processed may improve the lower bound. Zero is
                # universally valid for endpoint regret in this model.
                out.lower = 0.
                return out
        best.lower = max(0., lower)
        return best

    def furthest(self, a, epsilon, price_tol=1e-9, oracle_tol=1e-10):
        trial = self.endpoint(a, self.upper, tol=oracle_tol, decision=epsilon)
        if trial.upper <= epsilon:
            return self.upper, trial
        lo, hi = a, self.upper
        best = self.endpoint(a, a, tol=oracle_tol)
        while hi-lo > price_tol:
            mid = (lo+hi)/2
            trial = self.endpoint(a, mid, tol=oracle_tol, decision=epsilon)
            if trial.upper <= epsilon:
                lo, best = mid, trial
            else:
                hi = mid
        return lo, best

    def cover(self, epsilon, size, price_tol=1e-9, oracle_tol=1e-10):
        a, segments = 0., []
        for _ in range(size):
            b, trial = self.furthest(a, epsilon, price_tol, oracle_tol)
            segments.append({'left': a, 'right': b, 'basis': trial.basis,
                             'site': trial.site, 'upper': trial.upper})
            if b == self.upper:
                return True, segments
            if b <= a:
                break
            a = b
        return False, segments

    def minimax(self, size, loss_tol=1e-6, price_tol=1e-9, oracle_tol=1e-10):
        assert size >= 1
        if size == 1:
            trial = self.endpoint(0., self.upper, tol=min(loss_tol, oracle_tol))
            segments = [{'left':0., 'right':self.upper, 'basis':trial.basis,
                         'site':trial.site, 'upper':trial.upper}]
            return {'K':1, 'search_lower_estimate':trial.lower, 'search_upper':trial.upper,
                    'segments':segments, 'continuous_max':self.continuous_max([trial.basis]),
                    'eigen_calls':self.eigen_calls, 'endpoint_calls':self.endpoint_calls}
        lo, hi = 0., self.continuous_max([self.optimal_basis(0.)])['value']+loss_tol
        best = None
        while hi-lo > loss_tol:
            mid = (lo+hi)/2
            feasible, segments = self.cover(mid, size, price_tol, oracle_tol)
            if feasible:
                hi, best = mid, segments
            else:
                lo = mid
        if best is None:
            feasible, best = self.cover(hi, size, price_tol, oracle_tol)
            assert feasible
        bases = [x['basis'] for x in best]
        check = self.continuous_max(bases)
        return {'K': size, 'search_lower_estimate': lo, 'search_upper': hi,
                'segments': best, 'continuous_max': check,
                'eigen_calls': self.eigen_calls, 'endpoint_calls': self.endpoint_calls}

    def continuous_max(self, bases):
        lines = [self.line(u) for u in bases]
        prices = [0., self.upper]
        for i, (ai, bi, _) in enumerate(lines):
            for aj, bj, _ in lines[i+1:]:
                if bi != bj:
                    p = (aj-ai)/(bi-bj)
                    if 0 < p < self.upper:
                        prices.append(p)
        values = [(min(a+p*b for a, b, _ in lines)-self.optimum(p), p) for p in prices]
        value, price = max(values)
        return {'value': value, 'price': price, 'candidates': len(prices)}

    def packing(self, epsilon, size, step=1e-6, oracle_tol=1e-10):
        """Numerical lower evidence; all adjacent pairs must have dual > epsilon."""
        points, margins = [0.], []
        for _ in range(size):
            end, _ = self.furthest(points[-1], epsilon, oracle_tol=oracle_tol)
            nxt = end+step
            if nxt > self.upper:
                return None
            trial = self.endpoint(points[-1], nxt, tol=oracle_tol)
            if trial.lower <= epsilon:
                return None
            margins.append(trial.lower-epsilon)
            points.append(nxt)
        return {'epsilon': epsilon, 'points': points, 'dual_margins': margins}


def mirror_model():
    return SpectralModel([[1., .6], [.6, 2.]],
                         [np.diag([.2, 3.]), np.diag([3., .2])], [0., 1.])


def random_model(seed, n, rank, sites=3, upper=2.):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(n, n))
    a = x@x.T/n+np.eye(n)*.1
    cs = []
    for _ in range(sites):
        x = rng.normal(size=(n, n))
        cs.append(x@x.T/n+np.eye(n)*.1)
    return SpectralModel(a, cs, rng.uniform(0., .5, sites), rank, upper)
