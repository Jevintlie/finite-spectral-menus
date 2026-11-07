"""Fair-PCA-style Brent scalar oracle within the identical menu search.

Independent implementation of the published scalar optimization strategy, not
the authors' code or a claim about their measured performance. Endpoint-aware
early exits and a checked recovery fallback avoid disadvantaging the reference.
"""
import numpy as np
from scipy.optimize import minimize_scalar
from spectral_menu import SpectralModel, EndpointResult


class DecisionReached(Exception):
    pass


class BrentSpectralModel(SpectralModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.brent_fallbacks = 0

    def _site_endpoint(self, a, b, fa, fb, site, tol, decision=None, maxiter=100):
        slope = (fb-fa)/(b-a)
        best, lower = None, -np.inf

        def objective(t):
            nonlocal best, lower
            p = a+t*(b-a)
            dual = self.branch(p, site)-fa-(p-a)*slope
            lower = max(lower, dual)
            u, _, _ = self._face_basis(p, site, slope, tol)
            intercept = -float(np.sum(u*(self.A@u)))
            cost = float(np.sum(u*(self.C[site]@u)))+self.d[site]
            upper = max(intercept+a*cost-fa, intercept+b*cost-fb)
            if best is None or upper < best.upper:
                best = EndpointResult(lower, upper, u, site, p, 0)
            best.lower = lower
            if best.upper-lower <= tol or (decision is not None and
                                           (lower > decision or best.upper <= decision)):
                raise DecisionReached
            return -dual
        try:
            objective(0.)
            objective(1.)
            minimize_scalar(objective, bounds=(0.,1.), method='bounded',
                            options={'xatol':1e-13,'maxiter':maxiter})
        except DecisionReached:
            return best
        if best.upper-lower > tol:
            self.brent_fallbacks += 1
            # Brent's parameter stopping rule alone is insufficient to certify
            # a recovered primal basis, particularly at a rank-cutoff collision.
            return super()._site_endpoint(a,b,fa,fb,site,tol,decision,maxiter)
        return best


def as_brent(model):
    return BrentSpectralModel(model.A,model.C,model.d,model.rank,model.upper)
