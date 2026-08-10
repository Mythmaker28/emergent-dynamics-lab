# FSCMA00 -- parent provenance and bug audit

Parent programme: WARPED_SCALE_FIXED_SUPPORT_CAUSAL_RESPONSE_PILOT_00 (WSFSCRP00).
Device-chain parent commit: `e912a1004c5b9732d12a8fcc417002bfd1135622` (WSCCRP00).
Parent payload archive sha256: `141fe743274c0502ae1d9d06a2ef875988b16fbd5815d7aea02811b1d3d6fcf1` -- reproduced byte-for-byte in this session.

## 1. Integrity

* Archive sha256 recomputed from bytes: MATCHES the reported value exactly.
* `SHA256SUMS`: **49 of 49 entries verified from bytes**, zero failures.
* Parent engine-start ledger: 36 starts (12 GEN + 12 Q0 + 12 Q1), consistent
  with the parent's own log.

## 2. The `state_feats` bug, and why it provably cannot have touched Q2

The parent's `wsfscrp_q234.py` crashed with an `IndexError` in `state_feats` because `st.C` is
three-dimensional (a cohort tracer) and was indexed as if two-dimensional. Two source states are
preserved and separately hashed:

| state | sha256 |
|---|---|
| pre-fix `wsfscrp_q234_PREFIX.py` | `aff4b19937ef431e76420a824f2f888cb23c14364ca870090b872a726ba24521` |
| post-fix `wsfscrp_q234_POSTFIX.py` | `8261da7adbf32eb5f5110c7c6e900d4ec5b0b5adf22949edcec62337825a35f3` |

The minimal diff between them is 28 lines. The argument that Q2 is untouched is positional and
checkable, not a judgement call:

* Q2 is fully computed **and printed** by line 30.
* `state_feats` is first *defined* at line 61 and first *called* at line 90.
* Q0 and Q1 live in a different file (`wsfscrp_q01.py`) which the fix never opened.

A crash at line 90 cannot retroactively alter a value produced at line 30. The fix additionally
added a `time_template_only` nuisance baseline, which enters only as `min(...)` over baselines and
can therefore only **lower** `L_NUIS` -- it makes the Q3 gate strictly harder, never easier.

## 3. Independent recalculation of Q2 -- exact, with certificates

A separately coded verifier recomputed Q2 from the raw 12-row response matrix. It imports nothing
from the parent, re-derives the quadrature weights from the frozen physical grid, and decides both
gates in exact rational arithmetic with **no floating point in the decision path**.

The trick that makes exactness possible: the parent's design matrix carries `sqrt(w)`, which is
irrational, but the 12x12 Gram matrix `G = Xc Xc^T` carries `sqrt(w)*sqrt(w) = w` and is therefore
exactly rational. Singular values of `Xc` are square roots of eigenvalues of `G`. Eigenvalues are
counted exactly by Sylvester's law of inertia (exact LDL^T of `G - tI`).

| quantity | certified value | parent reported | relative difference |
|---|---|---|---|
| sigma2/sigma1 | 0.119621715387289415 | 0.1196217154 | 2.93e-16 |
| sigma2^2 / sum sigma^2 | 0.013975557890517347 | 0.0139755579 | 5.06e-16 |

Certified brackets are narrower than float64 resolution (relative width ~1e-30), so the meaningful
comparison is the relative error above: the parent's float64 answer is correct to a couple of ULP.

**Gate decisions confirmed exactly.** `sigma2/sigma1 > 0.10` PASSES (by a factor 1.196).
`sigma2^2/sum >= 0.05` FAILS (by a factor 3.578 -- not marginally). The second gate is decided by a
single exact inertia count: exactly **1** eigenvalue is at or above `trace/20`; two were required.

**The parent's arithmetic is vindicated. Its interpretation is not** -- see the mode arbitration
report, which shows the rank-one reading is an artefact of an ungauged channel label.

## 4. A defect the parent recorded and did not act on

`wsfscrp_q01.json` records `domain_ok = false` for **6 of its 12 TRAIN cells** -- every cell using
the S2 sentinel (intensive reflection). This audit determines what failed:

* C1 (`|Mf[0]| <= rho`) holds for intensive reflection on all six founders.
* C2 (`Mf[0] == 0` exactly on the dead gate `rho <= 1e-4`) is violated on 31-67 sites per founder,
  carrying between 8.4e-6 and 2.5e-5 of the total absolute carrier content.
* The engine repairs it within one step: the writer ends every step with
  `newm = clip(m,-1,1) * alive` and `Mf = rho * newm`, so `Mf` is exactly zero off the gate at the
  end of every step, unconditionally. It is not inert, though: during that first step the carrier
  transport reads `fM = Mf/max(rho,EPS)`, so off-gate carrier can be advected onto live neighbours
  before the gate re-applies.

This is a defect in the parent's domain declaration or in its choice of S2 instance. It is
**recorded, not repaired**: parent outputs are append-only.

## 5. Delivery defect inherited from the parent

WSFSCRP00 produced no commit: the device bridge was disconnected when it finished. That delivery
gap is closed by this programme's Git section. Reattachment is a delivery repair, not a science
change; no parent disposition is altered by it.
