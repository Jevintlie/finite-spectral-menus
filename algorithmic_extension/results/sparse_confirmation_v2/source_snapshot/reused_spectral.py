"""Reuse supporting subspaces and dual samples across endpoint queries.

Each cache entry supplies a valid primal line for any endpoint pair and a dual
sample if its price lies in that pair's interval. Cached subgradients bracket
the scalar concave maximum. This is an acceleration built from standard
supporting-line / cutting-plane principles, not a newly claimed principle.
"""
import numpy as np
from spectral_menu import SpectralModel, EndpointResult


class SampleStore:
    def __init__(self):
        self.array = np.empty((64, 4))
        self.bases = []
        self.count = 0

    def append(self, p, value, cost, intercept, basis):
        if self.count == len(self.array):
            new = np.empty((2*len(self.array), 4))
            new[:self.count] = self.array
            self.array = new
        self.array[self.count] = p, value, cost, intercept
        self.bases.append(basis)
        self.count += 1


class ReusedSpectralModel(SpectralModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.samples = [SampleStore() for _ in self.d]
        self.sample_keys = [set() for _ in self.d]
        self.reuse_decisions = 0

    def spectrum(self, p, site):
        w, v = super().spectrum(p, site)
        if p not in self.sample_keys[site]:
            basis = v[:, :self.rank].copy()
            intercept = -float(np.sum(basis*(self.A@basis)))
            cost = float(np.sum(basis*(self.C[site]@basis)))+self.d[site]
            value = float(w[:self.rank].sum()+p*self.d[site])
            self.samples[site].append(p, value, cost, intercept, basis)
            self.sample_keys[site].add(p)
        return w, v

    def _site_endpoint(self, a, b, fa, fb, site, tol, decision=None, maxiter=100):
        slope = (fb-fa)/(b-a)
        entries = self.samples[site]
        arr = entries.array[:entries.count]
        values = np.maximum(arr[:, 3]+a*arr[:, 2]-fa, arr[:, 3]+b*arr[:, 2]-fb)
        idx = int(np.argmin(values))
        valid = (arr[:, 0] >= a) & (arr[:, 0] <= b)
        lower = float(np.max(arr[valid, 1]-fa-(arr[valid, 0]-a)*slope))
        best = EndpointResult(lower, float(values[idx]), entries.bases[idx], site, arr[idx, 0], 0)
        if best.upper-lower <= tol or (decision is not None and
                                       (lower > decision or best.upper <= decision)):
            self.reuse_decisions += 1
            return best
        positive = arr[(arr[:, 2] > slope) & (arr[:, 0] <= b), 0]
        negative = arr[(arr[:, 2] < slope) & (arr[:, 0] >= a), 0]
        lo = max(a, float(positive.max())) if len(positive) else a
        hi = min(b, float(negative.min())) if len(negative) else b
        if lo > hi:  # numerical subgradient ordering; never trust inverted bounds
            lo, hi = a, b
        for it in range(maxiter):
            p = (lo+hi)/2
            value = self.branch(p, site)-fa-(p-a)*slope
            lower = max(lower, value)
            basis, cmin, cmax = self._face_basis(p, site, slope, tol)
            intercept = -float(np.sum(basis*(self.A@basis)))
            cost = float(np.sum(basis*(self.C[site]@basis)))+self.d[site]
            upper = max(intercept+a*cost-fa, intercept+b*cost-fb)
            if upper < best.upper:
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
                break
        if best.upper-lower > max(tol, 1e-11*max(1., abs(best.upper), abs(lower))):
            raise ArithmeticError(f'Cached endpoint gap unresolved: {best.upper-lower:g}')
        return best


def as_reused(model):
    return ReusedSpectralModel(model.A, model.C, model.d, model.rank, model.upper)
