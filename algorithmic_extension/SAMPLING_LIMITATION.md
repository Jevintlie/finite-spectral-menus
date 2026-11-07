# A precise limitation of spectral sampling

Consider one site, rank one, price p in [0,1],

    A=diag(2,1), C=diag(2,0), d=0.

For a unit vector with x=v_1^2 in [0,1], the affine objective is

    ell_x(p)=-1-x+2px,
    F(p)=min(-2+2p,-1).

Endpoint regret is (1-x,x), so the one-preset minimax value is

    min_{0<=x<=1} max(1-x,x)=1/2,

attained at x=1/2. Away from p=1/2, the globally optimal line is uniquely a
coordinate axis. A library containing only these uniquely selected optima has
best one-preset error 1, regardless of sample density. A conventional diagonal
eigensolver also returns coordinate eigenvectors at the exact collision.

At p=1/2 every direction is optimal. A method explicitly generating suitable
mixtures inside that tied eigenspace can include the best preset and avoid the
failure. Thus it is false to claim that *all* possible price-optimal sampling
fails. The statement concerns libraries of unique branch optima and default
eigenbasis selection. It isolates why finite-K menu construction needs a
realizable endpoint-balancing oracle instead of assuming that sampling more
prices always resolves the problem.

This example is an explanatory constructed witness. Its general lesson is
consistent with established fair-PCA tie recovery and restricted versus
unrestricted tangent approximation; scientific priority is not established.
