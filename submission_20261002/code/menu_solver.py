"""Continuous-angle, scalar-price menu solver for the recorded mirror example.

The greedy algorithm is exact with exact endpoint feasibility. This implementation
uses numerical bisection and must not be described as formal interval arithmetic.
All public computations use a first-quadrant reduction valid for positive task
cross-term and diagonal site costs. No price grid is used by the solver.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class MirrorModel:
    m: float = 1.5
    a: float = .5
    b: float = .6
    c: float = 1.6
    k: float = 1.4
    d: float = 1.
    upper: float = 2.

    def branch(self, price, site):
        x = (self.k*price-self.a) if site == 0 else (-self.k*price-self.a)
        radius = math.hypot(x, self.b)
        center = .5*math.atan2(self.b, x)
        value = -self.m+(self.c+site*self.d)*price-radius
        return value, 2*radius, center

    def optimum(self, price):
        return min(self.branch(price, s)[0] for s in (0, 1))

    def line(self, angle):
        # J=-m+a cos(2theta)-b sin(2theta)+lambda E(theta).
        q = math.cos(2*angle)
        intercept = -self.m+self.a*q-self.b*math.sin(2*angle)
        costs = (self.c-self.k*q, self.c+self.k*q+self.d)
        site = 0 if costs[0] <= costs[1] else 1
        return intercept, costs[site], site

    def acceptable_arc(self, price, epsilon, site):
        value, gap, center = self.branch(price, site)
        remaining = epsilon-(value-self.optimum(price))
        if remaining < 0:
            return None
        if remaining >= gap:
            return (0., math.pi/2)
        radius = math.asin(math.sqrt(remaining/gap))
        return max(0., center-radius), min(math.pi/2, center+radius)

    def endpoint_witness(self, left, right, epsilon):
        for site in (0, 1):
            arc0 = self.acceptable_arc(left, epsilon, site)
            arc1 = self.acceptable_arc(right, epsilon, site)
            if arc0 is None or arc1 is None:
                continue
            lo, hi = max(arc0[0], arc1[0]), min(arc0[1], arc1[1])
            if lo <= hi:
                return (lo+hi)/2, site
        return None

    def furthest(self, left, epsilon, iterations=58):
        witness = self.endpoint_witness(left, self.upper, epsilon)
        if witness is not None:
            return self.upper, witness
        lo, hi = left, self.upper
        witness = self.endpoint_witness(left, left, epsilon)
        if witness is None:
            raise ArithmeticError('A point must admit its own optimal direction.')
        for _ in range(iterations):
            mid = (lo+hi)/2
            trial = self.endpoint_witness(left, mid, epsilon)
            if trial is None:
                hi = mid
            else:
                lo, witness = mid, trial
        return lo, witness

    def cover(self, epsilon, max_size):
        current = 0.
        segments = []
        for _ in range(max_size):
            end, (angle, site) = self.furthest(current, epsilon)
            segments.append({'left': current, 'right': end, 'angle': angle, 'witness_site': site})
            if end == self.upper:
                return True, segments
            if end <= current:
                break
            current = end
        return False, segments

    def minimax(self, size, iterations=48):
        lo, hi = 0., 1.
        while not self.cover(hi, size)[0]:
            hi *= 2
        for _ in range(iterations):
            mid = (lo+hi)/2
            if self.cover(mid, size)[0]:
                hi = mid
            else:
                lo = mid
        feasible, segments = self.cover(hi, size)
        assert feasible
        return {'K': size, 'numerical_infeasible_epsilon': lo,
                'numerical_feasible_epsilon': hi, 'segments': segments,
                'angles': [s['angle'] for s in segments]}

    def continuous_max(self, angles):
        lines = [self.line(a) for a in angles]
        prices = [0., self.upper]
        for i, (ai, bi, _) in enumerate(lines):
            for aj, bj, _ in lines[i+1:]:
                if bi == bj:
                    continue
                cross = (aj-ai)/(bi-bj)
                if 0 <= cross <= self.upper:
                    prices.append(cross)
        values = [(min(a+p*b for a,b,_ in lines)-self.optimum(p), p) for p in prices]
        worst, where = max(values)
        return {'value': worst, 'price': where, 'candidate_prices': sorted(set(prices))}

    def packing_witness(self, epsilon, size, price_step=1e-7):
        # If successful, K+1 rational-grid prices have no jointly acceptable
        # direction at adjacent points. Interval convexity also excludes sharing
        # any non-adjacent pair. Incompatibility is checked again at high precision.
        points = [0.]
        for _ in range(size):
            end, _ = self.furthest(points[-1], epsilon)
            nxt = (math.floor(end/price_step)+1)*price_step
            if nxt > self.upper:
                return None
            if self.endpoint_witness(points[-1], nxt, epsilon) is not None:
                return None
            points.append(nxt)
        return points


if __name__ == '__main__':
    import json
    model = MirrorModel()
    for k in (1, 2, 3, 4, 8):
        result = model.minimax(k)
        result['continuous_max'] = model.continuous_max(result['angles'])
        print(json.dumps(result))
