# EXP-SC-00B — QUALIFIES prospectively, then FAILS R8-B. Substrate RETIRED. R8-C never reached.

Protocol SHA `a6d301870b29b4ef046194b68466727dc6e4ddb6`, frozen before any run. Substrate **unchanged** throughout.
Entirely unseen seeds. **D-044's seeds (8001, 8101, 8102) were not reused and its result is not reinterpreted.**

## The qualification passed — and O2' was the right criterion
| gate | result |
|---|---|
| **O1** scaffold coheres with the internal network **off** | **PASS** (PR 0.126 / 0.116 / 0.116) |
| **O2'** viability of **every** internal state (localization, no invasion, no extinction, no catastrophic fragmentation, persistence ≥ 0.8, continued turnover) | **PASS at beta = 0.10** on all 3 internal states × 3 unseen seeds |
| **O3** internal fields alone create no entity | **PASS** |
| **O4'** internal state predicts **future** uptake **after controlling for mass, radius, density and size** | **PASS: r_partial = +0.521, permutation p < 0.0005, n = 96** |

`beta = 0.10` selected by the **frozen prospective rule** (smallest beta in the grid passing O1/O2'/O3/O4'; the rule
references no identity outcome). Body size **does** differ across internal states (u-state: 21–24 entities; v-state:
11–12) — **reported, not thresholded**. That is exactly what the old O2 wrongly penalised.

**O4' is the strongest single result this project has produced.** The internal state predicts a *future* behavioural
observable with a partial correlation of **+0.52** after the trivial morphology features are regressed out. Identity
is not a decorative label, and it is not a proxy for body size — the confound case is a must-fail unit test that the
metric provably rejects.

## R8 — and where it died
| gate | result |
|---|---|
| **R8-A diversity** | **PASS** — between-entity distance 0.836 vs within-entity drift 0.394 → **ratio 2.12** (frozen margin 2.0) |
| **R8-B predictive identity** | **FAIL** — 1-NN prototypes fitted on the **early half** re-identify entities in the **late half** with accuracy **0.286** against chance 0.083. Required: chance + 0.25 = **0.333**. |

**0.286 is 3.4x chance — a real signal — and it does not meet the preregistered bar. The bar is not moved.**

**Why it fails, and it is the same number twice:** within-entity temporal drift (0.394) is nearly half the
between-entity distance (0.836). The internal organizations are *diverse* (R8-A) but **not temporally stable**: the
toggle domains coarsen and rearrange, so an entity at late times no longer resembles its own early prototype more
than it resembles its neighbours'. R8-A barely passes (2.12) for exactly the same reason. **Identity exists here, but
it does not persist.**

## Verdict
**R8-B FAILS → substrate RETIRED for the current question. R8-C is not run** (it presupposes a temporally persistent
identity to recover). **No threshold changed, no mechanism added, no retuning after failure.**

## What this rules out, precisely — and what it does not
It does **not** show the scaffold+internal-network architecture is invalid. The architecture **worked**: cohesion was
scaffold-independent (O1), every identity state was viable (O2'), the internal fields could not fake an entity (O3),
and the internal state was **causally efficacious on future behaviour, independently of morphology** (O4', r = +0.52).
What failed is the **temporal stability of the internal organization** under continuous constituent turnover.

The next requirement is therefore sharp and specific: an internal organization whose configuration is **pinned**, not
merely multistable — one that does not coarsen while the material beneath it is replaced. Achieving that by lowering
`D_int` or strengthening bistability **after seeing this failure would be tuning-after-failure and is forbidden.**
It is a new substrate, preregistered from the outset, with the pinning mechanism declared in advance.
