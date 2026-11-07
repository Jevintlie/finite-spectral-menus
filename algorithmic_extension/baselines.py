"""Strong finite-dictionary and adaptive-tangent reference methods.

The dictionary optimizer covers the continuous price interval, not a price grid.
Only its supplied preset candidates are discretized. Its greedy minimax search
is optimal within that dictionary in exact arithmetic. This prevents conflating
bad preset selection with limits of sampling the preset family.
"""
import numpy as np


class DictionarySolver:
    def __init__(self, model, bases):
        self.model = model
        self.bases = bases
        self.lines = np.array([model.line(u)[:2] for u in bases])

    def cover(self, epsilon, size, price_tol=1e-9):
        a, selected = 0., []
        self.last_segments=[]
        for _ in range(size):
            at_a = self.lines[:, 0]+a*self.lines[:, 1]-self.model.optimum(a)
            allowed = np.flatnonzero(at_a <= epsilon)
            if not len(allowed):
                return False, selected
            lines = self.lines[allowed]
            lo, hi = a, self.model.upper
            values = lines[:, 0]+hi*lines[:, 1]-self.model.optimum(hi)
            if values.min() <= epsilon:
                selected.append(int(allowed[np.argmin(values)]))
                self.last_segments.append((a,self.model.upper))
                return True, selected
            best = int(allowed[np.argmin(at_a[allowed])])
            while hi-lo > price_tol:
                mid = (lo+hi)/2
                values = lines[:, 0]+mid*lines[:, 1]-self.model.optimum(mid)
                if values.min() <= epsilon:
                    lo, best = mid, int(allowed[np.argmin(values)])
                else:
                    hi = mid
            selected.append(best)
            self.last_segments.append((a,lo))
            if lo <= a:
                break
            a = lo
        return False, selected

    def minimax(self, size, loss_tol=2e-6):
        vals0 = self.lines[:, 0]-self.model.optimum(0.)
        vals1 = self.lines[:, 0]+self.model.upper*self.lines[:, 1]-self.model.optimum(self.model.upper)
        hi = float(np.maximum(vals0, vals1).min()+loss_tol)
        if size == 1:
            best = int(np.argmin(np.maximum(vals0, vals1)))
            bases = [self.bases[best]]
            return {'continuous_max':self.model.continuous_max(bases),
                    'bases':bases, 'indices':[best], 'segments':[(0.,self.model.upper)],
                    'candidate_count':len(self.bases)}
        lo, best, best_segments = 0., None, None
        while hi-lo > loss_tol:
            mid = (lo+hi)/2
            ok, selected = self.cover(mid, size)
            if ok:
                hi, best = mid, selected
                best_segments=list(self.last_segments)
            else:
                lo = mid
        if best is None:
            ok, best = self.cover(hi, size)
            assert ok
            best_segments=list(self.last_segments)
        bases = [self.bases[i] for i in best]
        return {'continuous_max': self.model.continuous_max(bases),
                'bases': bases, 'indices':best, 'segments':best_segments,
                'candidate_count': len(self.bases)}


def sampled_dictionary(model, count, all_sites=True):
    bases = []
    for p in np.linspace(0., model.upper, count):
        if all_sites:
            for s in range(len(model.d)):
                bases.append(model.spectrum(p, s)[1][:, :model.rank].copy())
        else:
            bases.append(model.optimal_basis(p))
    return DictionarySolver(model, bases)


def adaptive_tangents(model, size):
    # Stronger than a single arbitrary start: use the better of both endpoints
    # and midpoint, charge all candidate evaluation work, then insert a global
    # optimum at the current menu's exact continuous worst price.
    choices = [[model.optimal_basis(p)] for p in (0., model.upper/2, model.upper)]
    bases = min(choices, key=lambda us: model.continuous_max(us)['value'])
    while len(bases) < size:
        check = model.continuous_max(bases)
        bases.append(model.optimal_basis(check['price']))
    return {'bases': bases, 'continuous_max': model.continuous_max(bases)}


class AdaptiveDictionary:
    """Heuristic local refinement with exact continuous dictionary selection.

    Refine both neighbors of each selected site/price sample and add all site
    optima at the menu's worst price. This is a deliberately stronger comparator
    than uniformly sampling an increasingly huge dictionary. No global
    convergence or novel adaptive-sampling mechanism is claimed.
    """
    def __init__(self,model):
        self.model=model
        self.entries=[]
        self.keys=set()
        for site in range(len(model.d)):
            for p in (0.,model.upper/2,model.upper):
                self.insert(site,p)

    def insert(self,site,p):
        if (site,p) not in self.keys:
            self.entries.append((site,p,self.model.spectrum(p,site)[1][:,:self.model.rank].copy()))
            self.keys.add((site,p))

    def step(self,size):
        solver=DictionarySolver(self.model,[e[2] for e in self.entries])
        result=solver.minimax(size)
        new=[]
        for i in result['indices']:
            site,p,_=self.entries[i]
            grid=sorted(q for s,q in self.keys if s==site)
            j=grid.index(p)
            if j>0:
                new.append((site,(grid[j-1]+p)/2))
            if j<len(grid)-1:
                new.append((site,(grid[j+1]+p)/2))
        for site in range(len(self.model.d)):
            new.append((site,result['continuous_max']['price']))
        for site,p in new:
            self.insert(site,p)
        return result
