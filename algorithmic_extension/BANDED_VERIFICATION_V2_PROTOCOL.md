# Banded verification v2: higher precision for unresolved small cases

5 October 2026. Preserve the v1 proposal files, source snapshot, and rejected
verification attempt. Its interval elimination widened some rank-eight
eigenvalue brackets enough to lose an existing packing exclusion margin.
This is a failure to certify, not a failed numerical optimization result.

Use the same 14 menus and the same proposed witnesses. Verification is a
development/audit operation, not a held-out timing experiment. No solver
timing, seed, or objective tolerance changes.

Before widening an eigenvalue bracket, an unresolved binary64 count at
n<=512 may be retried with directed 50-digit Decimal interval arithmetic.
Convert every input float exactly with Decimal.from_float; round elementary
operations separately toward negative and positive infinity. Reject any
unresolved or nonfinite pivot and trap Decimal underflow. The proof is the
same interval LDL induction and inertia law, under the additional Decimal
correct-rounding contract. Check both arithmetic paths against exact rational
elimination. Automatic Decimal fallback is limited to n<=512; larger cases
continue to use binary64 outward arithmetic and may fail to certify.

Independent replay still imports no menu solver. Six CPU processes may
verify independent branch-price pairs. GPU arithmetic is not used for these
outward bounds. Report fallback counts and retain any further failures.
