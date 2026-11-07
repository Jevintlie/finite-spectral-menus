"""Stronger cached Brent references; leave the v1 timing sources unchanged.

WarmBrent brackets the scalar maximum using earlier supporting-line slopes.
HybridBrent additionally uses all cached primal/dual bounds to decide queries.
Both recover actual rank-r bases and check objective gaps, not just parameter
convergence. This is an implementation comparison, not a new Brent algorithm.
"""
import numpy as np
from scipy.optimize import minimize_scalar
from spectral_menu import EndpointResult
from reused_spectral import ReusedSpectralModel
from brent_reference import DecisionReached


class WarmBrentSpectralModel(ReusedSpectralModel):
    def __init__(self, *args, reuse_bounds=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.reuse_bounds = reuse_bounds
        self.brent_fallbacks = 0

    def _site_endpoint(self, a, b, fa, fb, site, tol, decision=None, maxiter=100):
        slope = (fb-fa)/(b-a)
        entries = self.samples[site]
        arr = entries.array[:entries.count]
        positive = arr[(arr[:, 2] > slope) & (arr[:, 0] <= b), 0]
        negative = arr[(arr[:, 2] < slope) & (arr[:, 0] >= a), 0]
        lo = max(a, float(positive.max())) if len(positive) else a
        hi = min(b, float(negative.min())) if len(negative) else b
        if lo > hi:
            lo, hi = a, b
        best, lower, evaluations = None, -np.inf, 0

        def reached():
            return (best.upper-lower <= tol or (decision is not None and
                    (lower > decision or best.upper <= decision)))

        if self.reuse_bounds:
            values = np.maximum(arr[:, 3]+a*arr[:, 2]-fa,
                                arr[:, 3]+b*arr[:, 2]-fb)
            idx = int(np.argmin(values))
            valid = (arr[:, 0] >= a) & (arr[:, 0] <= b)
            lower = float(np.max(arr[valid, 1]-fa-(arr[valid, 0]-a)*slope))
            best = EndpointResult(lower, float(values[idx]), entries.bases[idx],
                                  site, float(arr[idx, 0]), 0)
            if reached():
                self.reuse_decisions += 1
                return best

        def objective(t):
            nonlocal best, lower, evaluations
            p = lo+t*(hi-lo)
            dual = self.branch(p, site)-fa-(p-a)*slope
            lower = max(lower, dual)
            u, _, _ = self._face_basis(p, site, slope, tol)
            intercept = -float(np.sum(u*(self.A@u)))
            cost = float(np.sum(u*(self.C[site]@u)))+self.d[site]
            upper = max(intercept+a*cost-fa, intercept+b*cost-fb)
            evaluations += 1
            if best is None or upper < best.upper:
                best = EndpointResult(lower, upper, u, site, p, evaluations)
            best.lower, best.iterations = lower, evaluations
            if reached():
                raise DecisionReached
            return -dual

        try:
            objective(0.)
            objective(1.)
            minimize_scalar(objective, bounds=(0., 1.), method='bounded',
                            options={'xatol': 1e-13, 'maxiter': maxiter})
        except DecisionReached:
            return best
        # Retaining previous samples in the recovery fallback favors both
        # references. Its cost is charged and its frequency is reported.
        self.brent_fallbacks += 1
        return super()._site_endpoint(a, b, fa, fb, site, tol, decision, maxiter)


def as_warm_brent(model):
    return WarmBrentSpectralModel(model.A, model.C, model.d, model.rank, model.upper)


def as_hybrid_brent(model):
    return WarmBrentSpectralModel(model.A, model.C, model.d, model.rank, model.upper,
                                 reuse_bounds=True)
