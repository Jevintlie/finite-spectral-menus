# Literature ledger

Checked 4 October 2026, primary sources. This is a developing comparison.

1. Shen, Davis, Lu, Bai (2026), *Fair principal component analysis via eigenvalue
   optimization*, BIT 66:17, DOI 10.1007/s10543-026-01109-9.
   https://web.cs.ucdavis.edu/~bai/publications/ShenDLB26.pdf
   Direct predecessor for the two-objective rank-constrained trace minimax
   reduction to scalar eigenvalue optimization and subspace recovery. Do not
   claim that subroutine as a new discovery. Need to inspect collision handling
   and compare its practical solver as a strong baseline.
   Full paper inspected locally: Section 4 uses Brent's scalar optimization;
   Appendix A.3 explicitly treats repeated eigenvalues and selects a basis
   within the tied space. Thus collision recovery is also prior art. Our
   implementation uses explicit orthogonal eigenvector-pair rotations instead
   of its suggested Grassmann path/root search; this alone is not a substantial
   novelty claim. `brent_reference.py` independently implements the scalar
   strategy with checked primal recovery, within the same outer menu search.
2. Tantipongpipat et al., *Multi-Criteria Dimensionality Reduction with
   Applications to Fairness*.
   https://papers.nips.cc/paper_files/paper/2019/hash/2201611d7a08ffda97e3e8c6b667a1bc-Abstract.html
   NeurIPS 32 (2019), Uthaipon Tantipongpipat, Samira Samadi, Mohit Singh,
   Jamie Morgenstern, Santosh Vempala. Primary proceedings page confirms exact
   polynomial-time two-criterion dimensionality reduction and multi-group
   approximation results. Earlier exactness and low-rank SDP precedent.
3. Imamoto and Tang (2008), *Optimal Piecewise Linear Approximation of Convex
   Functions*, WCECS, pp.1191-1194.
   https://iaeng.org/publication/WCECS2008/WCECS2008_pp1191-1194.pdf
   Direct competing finite-segment minimax approach. Unrestricted affine
   approximants need not be realizable by a spectral preset across site
   switches. STRUCTURAL_EXAMPLE.md now demonstrates this distinction: two models have
   the same F but different E_1, so F alone cannot determine the answer. The
   comparison concerns input/feasibility, not a speed claim against their code.
4. Rote (1992), Computing 48, 337?361, DOI 10.1007/BF02238642,
   *The convergence rate of the Sandwich algorithm for approximating
   convex functions*.
   https://page.mi.fu-berlin.de/rote/Papers/abstract/The%2Bconvergence%2Brate%2Bof%2Bthe%2BSandwich%2Balgorithm%2Bfor%2Bapproximating%2Bconvex%2Bfunctions.html
   Adaptive tangent sampling is a relevant baseline; its mechanism is prior art.
5. *Uniform Approximation of Eigenproblems of a Large-Scale Parameter-Dependent
   Hermitian Matrix*, arXiv:2409.05791.
   https://arxiv.org/abs/2409.05791
   Continuum parameter optimization and spectral reduced spaces. A reduced
   linear space allows combinations, unlike a selectable preset menu. Potential
   accelerator or comparator with that distinction made explicit.
6. Gaubert, McEneaney, Qu (2011), Theorem III.2.
   https://arxiv.org/html/1109.5241v1
   Already attributed in Paper 2; asymptotic law is not the new target.
7. Cardinal, Goaoc, Wajsbrot (2025), *Hitting and Covering Affine Families of
   Convex Polyhedra, with Applications to Robust Optimization*, MFCS 2025:33.
   https://drops.dagstuhl.de/storage/00lipics/lipics-vol345-mfcs2025/html/LIPIcs.MFCS.2025.33/LIPIcs.MFCS.2025.33.html
   Continuous hitting/covering and one-parameter finite adaptability are already
   studied. Their stated class is affine polyhedra with fixed-dimension
   complexity assumptions; the current rank-constrained spectral feasible set
   is different. Need explicit comparison, not a claim that continuous covering
   or finite adaptability originates here.
8. Rump (2022), *Verified Error Bounds for All Eigenvalues and Eigenvectors of
   a Matrix*, SIAM J. Matrix Anal. Appl., DOI 10.1137/21M1451440.
   https://www.tuhh.de/ti3/paper/rump/Ru22a.pdf
   Verified eigenvalue/subspace bounds and interval numerical linear algebra
   are established fields. Our elementary congruence verifier is a component
   for finite-menu certificates, not a claim to invent eigenvalue validation.

Working novelty boundary: the candidate is an end-to-end continuous-price
finite-menu algorithm with practical finite-budget evidence, not a new minimax
identity, interval greedy rule, fair-PCA solver, or approximation rate.

## Prior representative-set literature retained from the earlier draft

Cao et al. (2017), k-Regret Minimizing Set: Efficient Algorithms and Hardness,
ICDT 68:11, DOI 10.4230/LIPIcs.ICDT.2017.11, studies finite database tuples and
includes two-dimensional decision methods with interval-covering precedent.
https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICDT.2017.11

Diakonikolas and Yannakakis (2008), Succinct Approximate Convex Pareto Curves,
SODA pp.74?83, studies small representative convex Pareto approximations.
https://www.cs.columbia.edu/~ilias/papers/convex-pareto.html

The manuscript retains these precedents: neither finite-menu regret nor
interval-covering decision algorithms originate in this extension. The
structural example illustrates nonconvex realizability within this spectral
model; it is not advertised as a first general observation about scalar value
functions and feasible sets.

Tottori and Kobayashi (2026), Phys. Rev. Lett. 137:058401, DOI
10.1103/5ynb-7k4v, provides motivation through resource-induced strategy
transitions. Its dynamical memory-control model is explicitly distinguished
from the present static quadratic site costs.
