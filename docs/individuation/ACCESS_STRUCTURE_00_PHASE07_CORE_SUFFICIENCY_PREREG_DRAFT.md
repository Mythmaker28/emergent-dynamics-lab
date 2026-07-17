# ACCESS-STRUCTURE-00 — Phase 0.7 CORE-SUFFICIENCY-00 prospective decision draft

**DRAFT v0.7 — STOP-CORE-SUFFICIENCY — NOT SEALED — NOT AUTHORISED — NO PROSPECTIVE SEED — DO NOT EXECUTE**

This draft records the prospective logic for CORE-SUFFICIENCY-00 and the reason it is **blocked**. It does not
authorise a family, does not select a seed, and does not seal any margin. See
`ACCESS_STRUCTURE_00_PHASE07_CORE_SUFFICIENCY_REPORT.md` (sha256 of results
`82e4bbc9becd91d5cb8a8453f067e9921052405d8d085caa63e0ab9affb5e7f0`).

## Question (restricted)

Does the history-bearing core state remain causally sufficient to alter future feeding when environmental input is
replaced by a fixed, history-independent boundary? A positive, control-surviving, reference-robust result may support
only “local/core causal sufficiency under a standardized boundary.” It may never support unique local ownership,
absence of environmental/redundant/relational access, identity, or active reconstruction.

## Design (as tested in DEV)

- Statistical unit: original world; targets aggregated within world.
- Estimands: `tau_clamped = Y(M_OWN,K_CLAMPED) − Y(M_STD,K_CLAMPED)`, `tau_coupled = Y(M_OWN,K_COUPLED) −
  Y(M_STD,K_COUPLED)`, `interaction = tau_clamped − tau_coupled`.
- Endpoint: integrated tracked uptake at the frozen horizon step 40 (CONFIRM-02 probe). Fixed-mask uptake is the
  tracker-independent convergent control.
- M_OWN: preserve the target core `Mf`. M_STD: same-seed no-history twin intensive core-memory standardization
  (body/geometry preserved). K_COUPLED: ordinary coupling. K_CLAMPED: qualified two-cell history-independent boundary
  clamp. Mechanistic controls: `lam_plus=0`, `up_ref=0`. No arm added after seeing results.

## Explicit prospective outcomes (predeclared, unsealed)

- **CORE_SUFFICIENCY_SUPPORTED** — `tau_clamped` exceeds a frozen practical margin, same sign as `tau_coupled`,
  survives `lam_plus`/`up_ref` and body/geometry/nutrient controls, and is **reference-robust** (does not reverse
  across valid standardization references).
- **CORE_SUFFICIENCY_NOT_ESTABLISHED** — `tau_clamped` within a frozen equivalence bound, or not reference-robust.
  Never “environmental ownership.”
- **MANIPULATION_INVALID** — any clamp/standardization/viability/seam/temporal-discontinuity gate fails.
- **UNRESOLVED** — wide intervals, failed equivalence, or patterns not uniquely classified.

## Why this draft is BLOCKED (DEV evidence)

1. **Reference reversal.** `tau_coupled` reverses sign between the same-seed twin reference (negative, ~−0.02) and the
   erase reference (positive, ~+0.15) in all four DEV worlds. The prospective outcome would depend on the null choice.
2. **Estimand/null flaw.** The same-seed no-history twin carries ambient core `m_plus` comparable to the target, so
   `M_OWN − M_STD` is a small, sign-variable experimental-history increment, largely a direct `m_plus→uptake` readout
   (collapses ~69% under `lam_plus=0`). The null must be redefined to isolate the history-bearing component
   reference-robustly before any seal (candidates in the report §13).
3. `BLOCKED`: practical/equivalence margins, simultaneous-interval/multiplicity method, and power — none may be set
   from DEV outcomes and none can be defensibly set while (1)–(2) stand.

## Semantic seed-namespace audit (no selection, no opening)

Recorded so a future phase does not silently recycle a namespace; **none is chosen here.**

- `50001–50010`: already-open DEV; used for design/pilot only.
- `51xxx / 52xxx / 53xxx`: historical families; read-only context.
- `54001–54050`: consumed certified 03G primary family.
- `54051–54096`: reserved by the 03G manifest — unavailable.
- `54097–54120`: superseded historical namespace — must not be recycled.
- apparent `55xxx` in text scans is contaminated by five-digit byte counts in raw indexes; the broken ref
  `refs/heads/probe/tmp01` must be disposed of (without deleting evidence) before any seed audit is trusted.

Any future prospective family requires a fresh, collision-free namespace chosen **only** after a corrected null
passes DEV reference-robustness and receives explicit human approval. This draft selects none.

Current recommendation: **STOP-CORE-SUFFICIENCY.** No family, seal, prospective execution, merge, V5 change, or
active-reconstruction claim is authorised.
