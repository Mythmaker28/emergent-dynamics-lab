# WD-01 Phase C — Independent Position (before selection)

## What Phase B established (I accept)
The frozen write is rank-1 in the viable regime (three agreeing estimators). The prior "two EMAs ⇒ 1-D"
mechanism was too strong; the true statement is regime/parameterization-bound (see erratum).

## The two live hypotheses
- **H1 (dynamic-range):** de-saturating the same Ψ and separating the two timescales lets m_fast≈recent and
  m_slow≈cumulative store two temporal features.
- **H2 (write-signal insufficiency):** even de-saturated, one scalar Ψ that saturates in the drive cannot
  carry two independent magnitudes; a second, physically distinct local signal is required.

## My prior (SPECULATIVE, to be tested — not to pre-empt the dev grid)
A single-seed design-probe (erase-then-write, band [0.003,0.02], settle 20) shows C1 variants still decode
h1 (cumulative) well (R²≈0.8–0.9) but **fail h2** (order/recent−early, R²≤0.17), with corr(m1,m2)≥0.96.
Root cause is not the clip alone but that **Ψ=tanh(k_exp(N−c)+…) saturates in the drive** (D2: 83% of cells
saturated at p=0.02), so the fast component sees a near-binary signal and cannot resolve *late-drive
magnitude*. This favors **H2**. But the probe is coarse (1 seed, unoptimized timescales); C1 gets a fair,
multi-seed, multi-band dev test before C2 is authorized (minimality rule).

## What would change my mind
If any C1 config reaches two grouped-decodable coordinates (each R²≥0.5) on a viable dev family, H1 wins and
C2 is unnecessary. If only C2 does, H2 wins. If neither does while viable, the honest verdict is FAIL —
writing effectively one-dimensional — and the escalation toward reproduction should halt.

## Falsifier for the whole direction
If neither a de-saturation nor a distinct-signal minimal change yields a second *causally expressed*,
prospectively-validated coordinate in a viable droplet, "multi-dimensional causal experience memory" is not
reachable by local writing on this substrate and the program should stop adding mechanism.
