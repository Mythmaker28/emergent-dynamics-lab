# FUTURE-PROSPECTIVE-READINESS-ARCHITECTURE-01 — roadmap

Terminal disposition of Architecture 01: **`ARCHITECTURE_REVISE`**. **No route selected. No backup.**

This roadmap is deliberately **route-neutral**. An earlier draft named Route E in four of its steps and
was rejected by both reviewers for carrying forward, as the plan of record, a route that fails the gate
set — which §10.1 forbids as a trade and §10.7 forbids as a conditioned backup. No route name appears
in any step before the step that re-runs the §10 comparison.

**Nothing here is authorised.** The only authorised next action is step 0.

---

## Step 0 — HUMAN REVIEW — FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_01

| | |
|---|---|
| **Purpose** | Accept, defer or reject the `ARCHITECTURE_REVISE` disposition, the twenty-seven round-1 withdrawals (W1–W27), the twenty round-2 corrections (X1–X20), the eleven round-3 seal corrections (Y1–Y11), the complete binary gate table as corrected by Y1, and the three declared Part I deviations |
| **Type** | human review — no code, no execution |
| **Inputs** | this branch's four documents; both reviewers' round-1, round-2 and round-3 registers (79 findings, none judged invalid) |
| **Outputs** | one decision record; authorisation (or not) of step 1 |
| **Stop condition** | a withdrawal is judged incomplete, the gate adjudication is judged wrong, or a declared Part I deviation is judged unacceptable |
| **New family or seed?** | no |
| **Authorised now?** | **YES — the only authorised next action** |

Three governance questions the review must settle, because step 1 cannot start without them:

1. **The allowlist.** Every remaining specification blocker sits behind an exact read of
   `edlab/substrates/lattice_bond/engine.py` and the law parameterisation. Without that extension,
   step 1 will return `ARCHITECTURE_REVISE` for the same reason Architecture 01 did.
2. **The deferral standard.** Architecture 01 applied one standard to Route E and another to Route G,
   and both reviewers caught it. The successor brief must state **once** whether an engine-dependent
   definition may be deferred to a later allowlisted mission, and the answer must bind every route
   equally.
3. **The three declared Part I deviations.** §IV.5 declares that the lifecycle-01R and tracker-repair
   primary records cannot be re-cited by exact path without a filename search the firewall forbids,
   and that byte ranges are given only where they were tracked; §V.3 Y11 declares that the read ledger
   sits in Part IV rather than Part II, because R3/R4 forbid rewriting a reviewed part. The review must
   decide whether to supply the missing paths explicitly or to accept the deviations.

---

## Step 1 — FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_02

| | |
|---|---|
| **Purpose** | **1a** resolve the route-common items 1–2 of Part IV §IV.4 (allowlist, law frame, initial-condition classes, validator semantics); **1b** re-run the §10 route comparison from the beginning over Q-E, Q-G and Q-F on equal terms; **1c** resolve the remaining items of §IV.4 **applicable to the route selected at 1b** |
| **Type** | document-only architecture, to preregistration-grade precision |
| **Inputs** | Architecture 01 (four documents); the step-0 decision; the extended allowlist; the single deferral standard |
| **Outputs** | a specification precise enough to preregister without further design work, for **whichever** route the re-run comparison selects; a complete binary gate table; two independent adversarial reviews |
| **Stop condition** | items 1–2 remain unresolvable **with** the extended allowlist → `ARCHITECTURE_REVISE` again. A route-specific item that cannot be resolved is a stop for **that route**, not for the mission; if every prospective route stops that way, `STOP_PROSPECTIVE_READINESS` follows only if the affirmative case for stopping is by then established |
| **New family or seed?** | no |

**The order 1a → 1b → 1c is mandatory.** An earlier draft of this roadmap required fifteen
route-shaped items to be resolved *before* the comparison. That fixes design parameters before the
route and population are chosen — the same inversion this package condemns — and it structurally
privileges a prospective outcome, because Route F needs none of those items. Items 3–21 are entered
only after 1b has selected a route, and only to the extent they apply to it.

**The comparison must be genuinely re-run.** Both Q-E and Q-G currently fail G1/G13 on the *same*
ground — a definition that requires the engine read. Extending the allowlist changes the input to that
gate for **both**. Carrying Architecture 01's ranking forward would be exactly the error §10.8 lists
among the non-criteria ("the desire for forward motion"). Route F must again be evaluated
affirmatively, not as a residue.

**Derivation order is mandatory**, because Architecture 01 inverted it and that inversion is what the
reviewers destroyed:

> population → initial-condition classes → sampling schedule → detector and tracker constants →
> precision target → `L` → `Δ₀` and `Δ₁` → MDE (reported as a *consequence*, never as a justification)

---

## Step 2 — HUMAN REVIEW — ARCHITECTURE_02 *(combined with engineering authorisation)*

| | |
|---|---|
| **Purpose** | Accept the specification **and**, in the same decision, authorise step 3 with its exact frozen scope |
| **Type** | human review |
| **Inputs** | the Architecture 02 package |
| **Outputs** | one decision record; the frozen scope of step 3 |
| **Stop condition** | the specification still contains an undeclared outcome-determining parameter, or the selected route's gate table is not fully binary |
| **New family or seed?** | no |

Acceptance and engineering authorisation are combined because they are **one decision for one
decision-maker**: the scope of step 3 is determined entirely by what step 1 specified, so a separate
authorisation would add a signature without adding a judgement. Mission-count economy is **not** the
justification — fewer human gates means fewer opportunities to stop, which is not something a
governance document should optimise. Independence is preserved because the reviewers of step 1 are
not the authorisers of step 3.

---

## Step 3 — SCIENTIFIC_ACQUISITION_CAPABILITY_00

| | |
|---|---|
| **Purpose** | Close the infrastructure gap named in Part III §III.7 item 5. Extend the pipeline so that it **produces** — never accepts — (a) a float matter channel, (b) a labelled-cohort channel integrated per engine step, and (c) an engine-driven acquisition source; and so that analysis access is gated fail-closed on an external anchor |
| **Type** | code + tests + qualification, **plus a mechanical execution family** — an engine-driven acquisition path cannot be qualified without running the engine, and that is a new family under G8/G20 |
| **Inputs** | the accepted owned pipeline; the frozen scope from step 2 |
| **Outputs** | a qualified module; its test suite; a qualification record; a limitation register; the pinned source hashes of the **full** source-binding set |
| **Stop condition** | the produce-never-accept property cannot be preserved for the cohort channel; or per-step tracer integration cannot be reconciled with the persisted-and-re-read contract; or the engine-driven path cannot be qualified without contaminating a scientific family |
| **New family or seed?** | **yes — a mechanical qualification family that runs the engine.** It produces no scientific claim, and its worlds may never be enrolled in any later scientific family |

This is the largest remaining piece of work. Architecture 01 named one prerequisite where there are at
least five, and described the step as "synthetic qualification only" when it necessarily runs the
engine. It must not be split into ergonomic sub-missions.

---

## Step 4 — HUMAN REVIEW — SCIENTIFIC_ACQUISITION_CAPABILITY_00 *(combined with anchoring acceptance)*

| | |
|---|---|
| **Purpose** | Accept the capability, the anchoring venue and its in-code fail-closed enforcement, in one decision |
| **Type** | human review |
| **Inputs** | the step-3 package |
| **Outputs** | one decision record; the pinned hashes for the preregistration |
| **Stop condition** | the anchoring venue still requires a local secret, or is not genuinely append-only, or the root does not cover every morphology-dependent input |
| **New family or seed?** | no |

---

## Step 5 — PREREGISTRATION_00 *(named for the route selected at step 1)*

| | |
|---|---|
| **Purpose** | Freeze the executable preregistration: the estimand's six attributes; the enrolled denominator; the numeric decision rule with both arms' thresholds and both boundary error rates; the power analysis derived from a declared precision target; every constant with its sensitivity range; the committed PRNG seed; the pinned source hashes; and the analysis code |
| **Type** | document + analysis code; **no scientific execution** |
| **Inputs** | the step-1 specification; the step-4 pinned hashes |
| **Outputs** | the preregistration, sealed and externally anchored before any run |
| **Stop condition** | any design parameter still lacks a justification independent of the closed family, or the operating characteristics have not been evaluated under censoring and mechanical ineligibility |
| **New family or seed?** | the seed is **committed, not consumed** |

---

## Step 6 — HUMAN REVIEW — PREREGISTRATION *(the execution gate)*

| | |
|---|---|
| **Purpose** | The single decision that authorises scientific execution |
| **Type** | human review |
| **Inputs** | the sealed preregistration and its anchor evidence |
| **Outputs** | authorisation of steps 7–8, or refusal |
| **Stop condition** | the projected resource cost exceeds the declared ceiling → the family is **not** authorised and is **not** shrunk to fit |
| **New family or seed?** | no |

---

## Step 7 — NUISANCE_AND_COST_CALIBRATION_00 *(conditional)*

| | |
|---|---|
| **Purpose** | Fix any remaining nuisance parameter and the per-run cost |
| **Type** | scientific execution — mechanical and nuisance only |
| **Inputs** | the preregistration |
| **Outputs** | the nuisance values, the per-run cost, and the family's own censoring fraction; all anchored before the scientific family is drawn |
| **Stop condition** | the nuisance estimator is undefined on the calibration draw |
| **New family or seed?** | **yes** — a disjoint PRNG block; its units are discarded and may never be enrolled |

**This step must be split or eliminated.** Architecture 01's version failed G8, G20 and G21 by
combining nuisance calibration with feasibility measurement in one family. If step 1 adopts a
horizon rule containing no draw from the frame (§IV.4 item 9), this step reduces to a cost measurement
and the dual-role problem disappears. Otherwise nuisance calibration and cost measurement are two
separately authorised families.

---

## Step 8 — SCIENTIFIC_FAMILY_00

| | |
|---|---|
| **Purpose** | Execute the preregistered family; seal and anchor the evidence root; open analysis access fail-closed; compute the single preregistered analysis once |
| **Type** | scientific execution |
| **Inputs** | the preregistration; the step-7 values; the committed seed |
| **Outputs** | the primary estimate with its interval; the terminal call; the full competing-risk profile over the five lifecycle terminal states; every prespecified sensitivity and discriminator |
| **Stop condition** | the resource ceiling is reached with the endpoint indeterminate → report `INDETERMINATE` with the achieved precision; **do not extend the family** |
| **New family or seed?** | **yes** — the scientific family |

**This is the first interpretable prospective result**, on the path 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8
— but only if step 1b selects a prospective route. If it selects Q-F, the path ends at step 1 and
steps 2–9 do not exist. The step count is a description, not a target.

---

## Step 9 — INDEPENDENT_REPRODUCTION_00 *(conditional)*

Required before any downstream family relies on the step-8 estimate. A separately authorised family
from a third disjoint PRNG block, run at the same pinned hashes, against a **numeric** reproduction
criterion with its own declared power — not a vague "consistent with". The size criterion, stated
without a number because the number depends on a value Architecture 01 withdrew: `L₂` must be large
enough that the upper confidence bound at zero successes lies **below the re-derived negative-arm
floor**. (Under Architecture 01's withdrawn `Δ₀ = 0.10` that floor was 36; under `Δ₀ = 0.05` it is 72.)

---

## What is not in this roadmap

- **No route is selected, and none is presupposed.** Q-E, Q-G and Q-F all re-enter the §10 comparison
  at step 1 on equal terms.
- **Route G's structural position** — that its persistence-through-turnover endpoint presupposes
  entities that persist through turnover, that its enrolment arithmetic is Q-E's estimand, and that its
  null is uninterpretable until Q-E is answered — is the author's argument, recorded in Part II §II.2.5.
  It was not independently examined by either reviewer and it is **not** carried here as an established
  finding. Step 1 must test it, not inherit it.
- **Route F** must be evaluated affirmatively at step 1, on its own expected epistemic value. It is not
  a residue of the other routes failing, and Architecture 01's two rejections of it do not bind step 1.
- **Nothing beyond step 0 is authorised** by this document.
