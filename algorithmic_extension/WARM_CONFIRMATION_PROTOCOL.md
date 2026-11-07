# Stronger-reference confirmation — fixed before execution

4 October 2026. Local hash-bound plan, not externally preregistered.

Development used seeds 5300–5302 and the mirror/collision controls. This study
uses new seeds 5400 and 5401 for each shape (n,r,sites)=(8,1,1),(16,4,3),
(32,8,6),(64,4,3),(64,16,3), plus the mirror control. K=2,4 for all cases;
three repetitions with method order cyclically rotated across repetitions.
This gives 198 runs and 66 saved first-repetition menus.

Compare reused slope bisection, cached-slope-bracket Brent, and hybrid Brent
with both cached bounds and brackets. All use the identical outer menu search,
full dense eigensolver, cache capacity, basis recovery, and tolerances
(loss=2e-6, price=2e-8, endpoint=1e-9). Warm references retain cache bounds in
the checked recovery fallback; that cost and fallback frequency are reported.
The hybrid tests whether the gain is erased when Brent receives the same
primal/dual cache decisions. These are our implementations, not the authors'
code, and no theoretical superiority of bisection over Brent is claimed.

Fresh model/cache each run; all algorithm work included; input generation and
artifact saving excluded. One BLAS thread, sequential timings. Do not run
other numerical jobs concurrently. Raw rows retained including failures.
Retained spectrum/sample storage is measured, not full process RSS.

Success checks: all paired numerical losses within 5e-6, saved orthonormality
and continuous maximum independently checked, all failures disclosed. Report
ratios of per-cell median seconds, not best runs. Primary summary excludes
the mirror development control and includes every new-seed cell. Report
minimum/median/maximum ratio and all losses. One-preset behavior is outside
this study; its development result favors Brent on smooth cases and must
remain explicit. Independent global certificates are a separate check.

This is confirmation of a narrow implementation benefit on a synthetic dense
family. It is not evidence of universal superiority, general bit complexity,
physical applicability, or priority over all previous algorithms.
