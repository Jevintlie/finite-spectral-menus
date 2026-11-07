# Banded verification extension: declared before the new checks

5 October 2026. Continue the sparse study by attempting outward certificates
for the existing grid menus. Preserve all v4 solvers, timings, witnesses,
and archives. This is a verification extension, not a new speed benchmark.

Implement interval, unpivoted LDL elimination in symmetric band storage.
Reject nonfinite or unresolved pivot intervals. A successful factorization
certifies inertia by congruence; numerical banded eigenvalues propose
brackets only. Extend the polar-basis trace check to all stored bands.
No new eigenvalue theorem or unconditional certification success is claimed.

First compare successful counts with exact rational elimination on small
integer band matrices, including indefinite cases, disconnected blocks,
repeated eigenvalues, and deliberately unresolved zero pivots. Compare
spectral/objective enclosures with the existing dense and tridiagonal
verifiers. Record failures rather than infer eigenvalue ordering from
residuals. No changes to a previously frozen solver are needed.

Then attempt certificates for every CSR grid menu in sparse_confirmation_v2
(12 cases, n=128,256,512) and the two CSR grid scaling menus (n=1024,4096).
Reuse the four existing n=128 packing witnesses where possible. Generate
new numerical witness proposals for other cases, separately from checking.
Require independently replayed global gaps below 1.01e-5, with displayed
widths rounded appropriately. Record certificate failures as failures.

CPU processes may run independent certificate cases concurrently; no timings
from these jobs will be compared with the isolated solver benchmark. The
user authorized CPU and GPU use. Outward verification remains on the CPU
under the existing documented elementary-arithmetic contract. GPU work is
optional for numerical proposals and must not replace independent checking.

Report half-bandwidth, storage, successful/rejected counts, and runtime.
The O(n*b^2) elimination and O(n*b) matrix storage depend on bandwidth b,
not just the number of original nonzeros. This does not establish efficient
verification for arbitrary sparse graphs or a bounded-memory menu solver.
