# ACCESS-STRUCTURE-00 — Phase 0.7 CORE-SUFFICIENCY-00 DEV causal pilot

Status: **PHASE 0.7 COMPLETE — STOP-CORE-SUFFICIENCY — NO PROSPECTIVE-DESIGN-GO — DEV ONLY — NO SEED SELECTED —
HUMAN REVIEW REQUIRED**

Branch `claude/access-structure-noswap-design-06`, continuing from Phase 0.6B tip
`7deeb8e0bd4ac972e1dd133fc8992fcfc4f2fb2b`, parent `fa261734…`. The competing Phase 0.6A transplant line
(`codex/access-structure-boundary-repair-06`, tip `bf5901a…`) returned STOP-TRANSPLANT and was read, not merged. This
is a DEV-only causal pilot on the already-open seeds 50001–50010 (deep-feasible: 50002, 50004, 50005, 50007). No
prospective seed was opened, no confirmatory p-value or certification is claimed, and no endpoint, time point,
reference, or margin was selected by maximizing the DEV effect. Machine results:
`ACCESS_STRUCTURE_00_PHASE07_CORE_SUFFICIENCY_RESULTS.json` (sha256
`82e4bbc9becd91d5cb8a8453f067e9921052405d8d085caa63e0ab9affb5e7f0`).

## 1. Reframed question and scope

CORE-SUFFICIENCY-00: *does the history-bearing core state remain causally sufficient to alter future feeding when
environmental input is replaced by a fixed, history-independent boundary condition?* A positive, control-surviving,
reference-robust result could support only “local/core causal sufficiency under a standardized boundary.” It could
not establish unique local ownership, absence of environmental/redundant/relational access, individual identity, or
active reconstruction. **The DEV pilot does not deliver such a result** (Sections 5–9); it returns STOP for the
design as specified.

## 2. Predeclared estimands and statistical unit

Predeclared before executing the factorial (the same 2×2 for every arm, common frozen probe, deterministic paired
conditions — the substrate consumes no RNG in continuation, so pairing is exact):

- `tau_clamped = Y(M_OWN, K_CLAMPED) − Y(M_STD, K_CLAMPED)`
- `tau_coupled = Y(M_OWN, K_COUPLED) − Y(M_STD, K_COUPLED)`
- `interaction = tau_clamped − tau_coupled`

`Y` = integrated future feeding on the bijectively tracked target at the frozen horizon step 40 (CONFIRM-02 probe:
`N:=N0`, settle 40, uniform stimulus `0.25×5`, horizon 40). The **statistical unit is the original world**; the three
targets are aggregated within world (mean over valid targets) before any summary. Targets are not independent
replicates. Every eligible DEV world is reported, including sign reversals and near-degenerate targets. No
confirmatory inference is drawn from four DEV worlds.

## 3. Task 1 — audit of the memory standardization (M_STD)

M_STD is a **local memory-field intervention with body and geometry preserved** — not “the standardized complete
core.” It sets the target core’s intensive memory `m=(m1,m2)` to the translated same-seed no-history twin’s intensive
memory and rebuilds the extensive `Mf` on the target’s own `rho`. Audited on all 12 deep-feasible targets:

| Property | Finding |
|---|---|
| exact fields modified | **`Mf` only** (verified); `rho, U, V, c, N, C, uptake` bit-unchanged |
| spatial support | the radius-10 core disk; `Mf` outside the core bit-unchanged; body/geometry preserved |
| recipient-history-independence | yes — the twin is the same seed evolved without the two phase drives; independent of the recipient target’s history |
| on-manifold | the imposed `m` is the twin’s evolved (on-manifold) memory, but only ~0.76–0.80 of the target core body is covered by the translated twin body; uncovered cells receive `m≈0` |
| **information introduced** | **substantial** — the no-history twin is NOT memory-free: its ambient core `m_plus` (~0.19–0.34) is COMPARABLE to the history-laden target (~0.25–0.33). M_STD therefore *swaps* history for an on-manifold ambient baseline of similar magnitude rather than removing memory |
| immediate `m_plus` change (own→std, body mean) | **sign-variable**, range `−0.136 … +0.130` (max abs up to `0.507`) |
| conservation | extensive `Mf` core total changes by `0.47 … 5.90` (non-conservative in memory by construction); `rho` conserved |
| reference dependence | **material** — see Section 9 |

The decisive audit result is that the same-seed no-history reference carries comparable ambient memory. The
`M_OWN − M_STD` contrast is thus the *difference between the target’s experimental-history memory and the twin’s
ambient memory*, a small and sign-variable quantity — not a clean “history present vs absent” contrast.

## 4. Manipulation-validity and probe reproduction

An independent second path validates the probe machinery: `nm.measure` intact-vs-region-erase reproduces the
established own effect, own-fraction ≈ 0.05 (50002 `[−0.0, 0.051, 0.052]`, 50004 `[0.052, 0.047, 0.039]`, 50005
`[0.051, 0.066, 0.046]`, 50007 `[−0.0, 0.054, 0.074]`; two near-degenerate targets carry ~0 own effect and are
retained, not excluded). All **144/144 arms are viable** (three distinct bijective tracks, coverage < 0.15, uptake
endpoint present every step) across all conditions. Exact bit-level isolation of the two-cell clamp was established in
Phase 0.6B and is unchanged here.

## 5. DEV factorial (world-level, twin-referenced M_STD, tracked endpoint)

| Condition | seed | `tau_coupled` | `tau_clamped` | `interaction` |
|---|---|---:|---:|---:|
| normal | 50002 | −0.00312 | −0.00012 | +0.00300 |
| normal | 50004 | −0.02043 | −0.02053 | −0.00009 |
| normal | 50005 | −0.01019 | −0.00931 | +0.00088 |
| normal | 50007 | −0.05159 | −0.04697 | +0.00462 |
| **normal — world summary** | | mean **−0.0213**, all 4 negative | mean **−0.0192**, all 4 negative | mean **+0.0021** |
| lam_plus=0 | 50002/04/05/07 | +0.0043 / −0.0038 / +0.0028 / −0.0155 | +0.0073 / −0.0029 / +0.0017 / −0.0050 | small |
| up_ref=0 | 50002/04/05/07 | identical to normal (to 5 dp) | identical to normal | identical |

`Y` values are ~1.5–2.2 integrated uptake, so `|tau| ≈ 0.02` is ~1% of feeding. The twin-referenced effect is small,
**consistently negative** (M_OWN feeds slightly *less* than the same-seed ambient baseline — the experimental history
left the core with slightly lower feeding-relevant `m_plus` than ambient), and largely unchanged by the clamp.

## 6. Task 2 — direct-readout and global-channel controls (secondary)

Evaluated on the *history-dependent contrasts*, not merely endpoint presence.

- **lam_plus=0**: `|tau_coupled|` collapses to **31%** of its normal value (mean `0.0066` vs `0.0213`) and becomes
  mixed-sign. Interpretation: the (already small) twin-referenced effect is **predominantly mediated by the direct
  `m_plus → uptake` pathway**. A residual ~31% under lam_plus=0 reflects the indirect `m_minus → attractant`
  pathway and dynamics; it does not by itself locate storage.
- **up_ref=0**: absolute feeding shifts slightly (e.g. `1.939968 → 1.939977`, control genuinely applied) but every
  `tau` is unchanged to five decimals. The global channel is **common-mode** in this contrast and does not mediate
  it. Consistent with the DEV prior that `up_ref` barely moves `m_plus`. This is not evidence *against* an
  environmental/global role for storage; it only shows the global channel does not carry *this* contrast.

The frozen normal probe remains primary; these ablations are secondary and mechanistic.

## 7. Task 4 — time-horizon discipline

The frozen 40-step horizon is the primary endpoint; earlier points are diagnostic only. The core `m_plus` contrast
`|mean(m_plus_OWN) − mean(m_plus_STD)|` on the body is retained to step 40 at fractions **0.59–0.87** (coupled) and
**0.59–0.87** (clamped) across worlds — the core stays in an interpretable regime through the primary endpoint; the
standardized boundary does **not** overwrite core memory before step 40 (memory diffusion `D_m=0.01` and templating
`eta_t=0.01` are slow, and the barrier sits in near-empty space outside the body). No earlier, more favourable
endpoint was substituted. Horizon discipline is satisfied — this is not the reason for STOP.

## 8. Task 3 — interaction, evaluated (not asserted)

Per the explicit instruction, common-mode cancellation is **not asserted**; the interaction was computed. World-level
`interaction` is `[+0.0030, −0.0001, +0.0009, +0.0046]`, mean `+0.0021`, i.e. ≈ **10% of `|tau_coupled|`**. The clamp
therefore does **not** create or dominate the memory effect (the effect is present, and of the same sign, under
ordinary coupling), but it is **not exactly common-mode either** — it modestly amplifies `|tau|` for two worlds. The
primary contrast is not a pure clamp artefact; equally, the clamp is not proven neutral.

## 9. Reference sensitivity — the decisive result

The same contrast under the two candidate standardization references (world means, `tau_coupled`, normal probe):

| seed | twin-referenced (primary) | erase-referenced (m→0) | sign reversed? |
|---|---:|---:|---|
| 50002 | −0.00312 | +0.15423 | **yes** |
| 50004 | −0.02043 | +0.15320 | **yes** |
| 50005 | −0.01019 | +0.19822 | **yes** |
| 50007 | −0.05159 | +0.14108 | **yes** |

The **reference choice reverses the sign of the result in all four worlds**. The erase reference (off-manifold `m→0`)
gives a large positive effect — this is the already-established 03G total-memory finding (own memory raises feeding
vs no memory), and it survives the clamp. The same-seed on-manifold twin reference gives a small negative effect. The
two references measure genuinely different estimands (total core memory vs the experimental-history increment above a
comparable ambient baseline), and they disagree in sign. This is an explicit STOP condition.

## 10. Task 5 — halo claim, corrected

The Phase 0.6B “comoving halo ≈ 4 cells” is renamed and rescoped: it is a **DEV perturbation-propagation /
influence-decay radius under the specified `Mf` perturbation and horizon (~4 cells)**, a substrate interaction length —
**not a causal ownership boundary**. A genuine H_HALO test would require a prospective causal contrast across
predeclared boundary radii; that is **not** launched here. Radius sensitivity is reported only as secondary DEV
engineering information, and no radius was or will be chosen from a feeding contrast.

## 11. Task 6 — phase claim, corrected

H_PHASE is **not** dismissed on the ground that the engine is Markov. The correct statement: *no hidden update
buffer or velocity state was identified beyond the complete Markov snapshot, but relational phase information may
remain encoded in that snapshot* — spatial correlations, gradients, and joint field configuration. Assessment of the
interventions: the **clamp preserves** the core’s internal correlations (it replaces only the barrier; the core
evolves under the true engine), whereas **M_STD does not** — it overwrites the core memory field, imposing the twin’s
correlation structure and destroying the target’s relational memory phase on the core. Any prospective phase claim
would therefore be confounded by M_STD itself; no separate phase experiment is proposed.

## 12. Verdict — STOP-CORE-SUFFICIENCY

Returned per the predeclared Task-8 logic. Triggering conditions, from the data:

- **Reference choice reverses the result** — yes, 4/4 worlds (Section 9). *[explicit STOP condition]*
- **M_STD substantially manufactures the endpoint contrast** — the twin-referenced `tau` is small, sign-variable at
  the target level, collapses ~69% under `lam_plus=0`, and is essentially a direct readout of the imposed `m_plus`
  difference; because the twin carries comparable ambient memory, the sign is set by whether ambient exceeds the
  target’s own `m_plus`. *[explicit STOP condition, substantially met]*

Conditions that did **not** trigger STOP (reported for completeness): the clamp is mechanically valid and bit-exact;
the clamp/core interaction is small (~10%), not artefact-dominated; the core stays interpretable through step 40. So
the obstruction is specifically the **estimand/null**, not the clamp.

What STOP does and does not mean:
- It stops the prospective test **as designed** (twin-referenced M_STD): that contrast is not reference-robust and is
  a small direct-readout quantity, so a prospective sample could not defensibly establish “core sufficiency.”
- It is **not** evidence for environmental, redundant, or relational ownership. A negative/reference-fragile DEV
  result does not prove environmental storage. The core memory *does* causally alter feeding under the standardized
  boundary (`tau_clamped ≠ 0`, ~−0.02, retained to step 40), but the alteration is small, direct-readout-mediated,
  and its sign depends on the null.
- The established 03G total-memory effect (erase-referenced) survives the clamp; that is informative but is a
  different, already-certified estimand with an off-manifold null and cannot stand in for a core-sufficiency claim.

## 13. Bounded correction a future phase would require (not pursued now)

The single fixable obstruction is the null: a same-seed on-manifold “no-history” reference intrinsically carries
ambient memory comparable to the target’s, so the experimental-history increment is small and sign-variable. A future
phase — only if a human authorises it — would need to redefine the estimand/null so it isolates the history-bearing
component cleanly and reference-robustly (candidates: a within-target memory-scramble null that preserves the ambient
magnitude while destroying the written pattern; a matched-magnitude ambient null; or an explicit reframing to
total-memory sufficiency with an on-manifold justification for the `m→0` limit), then re-audit reference robustness
before any preregistration. No such arm is added here (no flattering arms after seeing results), and no seed is
selected.

Exact next authorized action: human review of this STOP verdict and the accompanying unsealed prereg/power drafts.
