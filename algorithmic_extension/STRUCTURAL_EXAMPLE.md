# The fully adaptive value function does not determine a finite menu

This explicit example explains a structural distinction from approximating a
scalar concave curve. It is a proposition about this model, not a claim that
nonconvex implementability or the limitations of scalar value functions are
new general concepts.

Let n=2, r=1, p in [0,1], A=diag(1,0), and all overheads be zero. Write
t=u_1^2 in [0,1] for a unit preset u. Compare two resource models:

- Model S has one site with C=diag(2,0). Its preset line is -t+2pt.
- Model M has sites C_1=diag(2,2), C_2=diag(4,0). Its effective preset line is
  -t+p min(2,4t).

Both have exactly the same fully adaptive value

    F(p)=min(-1+2p,0).

For S this is immediate by minimizing an affine function of t. For M, the
first site's branch is -1+2p, the second is min(-1+4p,0), and minimizing the
two gives the stated F on the whole domain.

In Model S the endpoint regrets are 1-t and t. Hence E_1(S)=1/2 at t=1/2.
In Model M they are 1-t and min(2-t,3t). For 0<=t<=1/2 the maximum of
1-t and 3t is minimized at t=1/4 with value 3/4. For 1/2<=t<=1 the
maximum is 2-t, whose minimum is 1. Thus E_1(M)=3/4, achieved by
u=(1/2,sqrt(3)/2). Convexity of each preset's regret makes endpoint checking
sufficient. Both models have E_2=0 using the two coordinate presets.

There is a stronger limitation than missing an eigenbasis at a repeated
eigenvalue: **every globally optimal preset of Model M, at every price, is a
coordinate preset.** For p<1/2 the first coordinate is uniquely globally
optimal (including p=0). For p>1/2 the second coordinate is uniquely globally
optimal. At p=1/2 the value for t is min(1-t,t), which vanishes only for
t in {0,1}. Thus even the infinite dictionary of all globally optimal presets
has best one-preset loss 1, strictly worse than 3/4. This statement allows
all choices at ties; it is not a library eigenvector artifact.

The optimal t=1/4 preset is supported by the *second site's* spectral branch
at p=1/4, where that branch equals zero but F=-1/2. An all-site branch oracle
with suitable tied-space recovery finds it. Merely taking global optima as
candidate presets cannot. Our numerical dictionary baseline is deliberately
stronger: it samples every site, not only globally optimal sites.

Consequently an algorithm whose only input is F cannot solve this general
finite-menu problem: the same F would require two different correct E_1
outputs. Unrestricted upper affine approximation of F gives 1/2 in both
cases, but its optimal line p-1/2 is unattainable by any Model M preset.
The difference is site-constrained realizability, not numerical resolution.

The zero eigenvalues are not essential for positive definiteness: adding
alpha I to A and the same beta I to every C shifts every preset and F by
-alpha+beta p. Regrets, minimizing subspaces and both separations are
unchanged for any alpha,beta>0.
