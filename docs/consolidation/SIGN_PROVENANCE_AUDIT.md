# SIGN-CONTRACT PROVENANCE AUDIT

## Finding: all point identifications were contract-dependent, and the contracts were ORACLE-derived
In `bench.py` the `clean_anchor` and `sign` flags are set from case definitions that **know the true κ**. In the
synthetic benchmark these are therefore **oracle metadata**, not operationally established contracts.

## Rerun with contracts removed (dev + prospective, 20 cases)
| | WITH oracle contracts | WITHOUT any contract |
|---|---|---|
| point identifications | 8 / 20 | **0 / 20** |
| invalid sets | 0 | 0 |

Without contracts every case degrades to `NON_IDENTIFIABLE` (or `ILL_CONDITIONED`) — the instrument stays **safe**
but identifies nothing.

## Interpretation (claim-narrowing, load-bearing)
The benchmark validates that the instrument **uses** declared contracts correctly and refuses without them. It does
**not** demonstrate that such contracts are obtainable from passive data. They must come from **external domain
knowledge** — sensor physics, a calibration intervention with an independent scale, or a conservation law. Amplitude
scaling of the intervention does **not** reveal the sign (both `q` and `q(1−β)` scale identically).

**Any claim of point identification must be stated as conditional on an externally established sign/anchor
contract.** Unconditional point-recovery claims are withdrawn.
