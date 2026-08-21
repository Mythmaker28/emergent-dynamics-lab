# FMRT01 — FRESH MINIMAL REPRODUCTION TEST 01
## MASTER FREEZE — written and committed BEFORE the first scientific world

This document is the human-readable face of `FMRT01_MASTER_FREEZE.json`.
It is derived mechanically from the frozen JSON artefacts; it adds no number of its own.

| | |
|---|---|
| Program | FRESH-MINIMAL-REPRODUCTION-TEST-01 |
| Generated (UTC) | 2026-08-21T14:59:08.971274+00:00 |
| Parent tip | `a453e215f39150afe8a2e9c59a74150b9abecd63` |
| Methods hash | `ca6318d7ccd38cd6d4eb75b32a4d54d6de98265594204693c21a1680c5e7fd87` |
| Primary scientific worlds | 255 (cap 256) |
| Blocks x arms | 85 x 3 |
| Technical reserves permitted | 6 |
| Post-outcome scientific repairs permitted | 0 |

---

## 0. Container incident disclosed at the head of the freeze

> this mission began after the FIFTH container rollback. The repository was restored from RCD01_INCREMENT.bundle on Tommy's Windows disk. The SPOIQ01 capability module was never made durable and was destroyed; it is RECONSTRUCTED here and RE-QUALIFIED from scratch, and SPOIQ01's recorded hashes are NOT claimed.

The capability module is therefore re-qualified from scratch in this mission: `UNARMED_INERTNESS = PASS_88_OF_88`, fixtures `11/11`. No hash recorded by SPOIQ01 is reused or claimed.

---

## 1. The law under test is unchanged

The frozen engine is executed byte-for-byte. The intervention is a **subclass method** that the
autonomous law never calls; it is invoked only by the experiment harness, at one predeclared boundary.

| Component | SHA-256 |
|---|---|
| `OBTC02/code/engine_obtc.py` | `2172deae5bbabf37238cf7712cb17663c151494befcf85505c537a7cac0ded30` |
| `PQEC01/code/pqec01_observer.py` | `d8ff4b9da05c95641c7f69cef4c8b2ffe4c45f17975e8f348d5c5e0f2b6bba21` |
| `FMRT01/code/fmrt01_engine.py (capability)` | `6801081deb4726acd6eb6ddbaa037060e9f10a1fa205982fb6a8498128dcb95d` |

`engine_unchanged = True`. The complete transitive closure is 22 modules and 11 data inputs, hashed in
`FMRT01_METHODS_MANIFEST.json` and `FMRT01_METHODS_SHA256SUMS`.

### The frozen parameter point B1

```
kY  = 2.5118864315095822e-05
muY = 9.261187281287937e-05
```

Inherited frozen constants: `CAP = 16`, `S0 = 3`, `phi = 0.2`, `omega = 0.05`, `muX = 0.004`, `kX = 1.0`, `L = 36`, `X_SEED = 4`, `p_hop_X = 0.10263340389897246`, `p_hop_Y_mobile = 0.10263340389897246`, `T_HORIZON = 11000`, `T_WINDOW = 9000`, `BURN_IN = 2000`, `CORE_R = 5.0`, `TAU_SEP = 125.0`, `ALPHA_SURVIVAL = 0.5`, `N_STAR = 10.0`, `GAMMA_SEP = 0.5`, `MIN_EVENTS = 1.0`

No parameter point is created, retuned or re-selected by this mission (`NEW_PARAMETER_POINTS = 0`, `ADAPTIVE_RETUNING = forbidden`).

---

## 2. Design selection — decided mechanically, before any outcome exists

Two designs were costed exactly, with no normal approximation:

| Design | Causal contrast | Worlds to reach power 0.80 at q = 0.40 |
|---|---|---|
| A paired 3-arm common-seed blocks | matched — the three arms are bit-identical immediately before the intervention, by construction | 150 |
| B 2:1:1 independent allocation (SPOIQ01 proposal) | unmatched — arms differ by seed as well as by treatment | 256 |

**Selected: Design A.** A reaches the 0.80 power target at q = 0.40 with 150 primary worlds where B needs 256, and it delivers a strictly stronger causal contrast because the arms share the exact pre-intervention state. B was not retained merely because SPOIQ01 proposed it.

Unconditional exact power at 85 blocks (integrating over the random number of trigger-eligible worlds):

| true q | power |
|---|---|
| 0.40 | 0.9699905737 |
| 0.30 | 0.8663466405 |
| 0.20 | 0.5768922790 |
| 0.15 | 0.3585751293 |
| 0.10 | 0.1477913941 |

Planning trigger probability: `0.21411676535655655` — the exact 95% lower confidence bound from FDFLT01 (point estimate `0.2760416666666667`), because planning on a point estimate would understate the worlds needed.
Source of that input: FDFLT01, developmental; not confirmatory evidence.
Late-trigger loss: 0 of 53 FDFLT01 maturation events fell after step 10750 (max observed t_m = 9464), so the latest-allowed-trigger rule costs nothing.
Expected trigger-eligible worlds at 85 blocks: `18.199925055307308`.
Conservative planning alternative: `q = 0.4`. the comparison criterion is which DESIGN needs fewer worlds; within the chosen design the budget is then spent on power against a more conservative alternative

---

## 3. The null hypothesis is the criterion's own false-positive rate

```
H0 : q <= 0.05
H1 : q > 0.05
alpha: one-sided 0.05
```

> the frozen R2 material criterion D compares the daughter's post-intervention local X against the exact 95 per cent binomial upper bound on how much pre-intervention X could survive T_HOLD steps with no new production. Under NO_NEW_DAUGHTER_X_PRODUCTION the false-positive probability of criterion D is therefore bounded by 0.05 by construction. The null is the criterion's own false-positive rate, not a chosen number.

Decision function: `critical(M) = smallest k with P[Binomial(M,0.05) >= k] <= 0.05`. Worked values:

| M eligible worlds | k required |
|---|---|
| 5 | 2 |
| 10 | 3 |
| 15 | 3 |
| 18 | 4 |
| 20 | 4 |
| 25 | 4 |
| 30 | 5 |

---

## 4. The primary endpoint, frozen in full

### Trigger (the maturation event)

- the FIRST step at which an episode of exactly two spatial centres reaches its frozen FDFLT01 maturation event
- Evaluated at **run_start + 250 - 1, evaluated at EXACTLY that step and not at later steps of the same run**
- Requires: no third centre inside the episode window
- Requires: the weaker centre's local X mass at the event is at least f_primary of the stronger's
- Does **not** require: R1. R1 is classified separately at t_m so the intervention can never be delayed until a favourable provenance state appears.
- `f_primary = 0.6321205588285577`, `NEED = 250`

### Intervention boundary

> after the completed end-of-step observation at t_m and before the first transport of t_m + 1. The engine never detects maturation and never invokes the intervention.

`TOTAL_HORIZON = 11000`, `T_HOLD = 250`, `LATEST_ALLOWED_TRIGGER = 10750`.

> a functional daughter appearing after the latest allowed trigger is a population-level FAILURE and is NOT intervention-eligible; the count is reported explicitly. No world is extended adaptively.

### R1 — provenance, classified at t_m and threshold-free

- Basis: molecule identity from the engine's inert tracker
- Criterion: inherited_mass_in_daughter_disc < f_primary * parent_disc_mass — the counterfactual F5 asks, restricted to material that existed before the daughter did
- `no_majority_cutoff = True`, `not_retuned_from_fresh_worlds = True`

### R2 — independent maintenance, evaluated at t_m + 250

- **A.** the daughter Y centre still exists
- **B.** the daughter remains spatially identifiable
- **C.** X/source integrity has held
- **D.** daughter-local X mass exceeds Q_0.95[Binomial(N_X_world_at_intervention, (1-muX)^250)]
- **E.** the tracker shows post-intervention X births inside the surviving daughter disc

- Per-molecule survival over the hold: `0.3671424535662421`
- criterion E converts the test from 'old stock survived' to 'the daughter maintained production'

> a third spatial centre appearing before R2 completion is a PRIMARY_REPRODUCTION_FAILURE, frozen before runs, because the causal source of maintained X would otherwise be ambiguous

> exactly T_HOLD steps with NO early stop. Extinction and third-centre events are recorded as OUTCOMES, not used as stops, because the GLOBAL arm removes all Y by design and must still be observed decaying. Frozen here, before any world exists.

**Minimal reproduction = R0 and R1 and R2 in the predeclared temporal order**

---

## 5. Controls

| Arm | Operation |
|---|---|
| `A_SELECTIVE_PARENT_OFF` | remove only parent-centre Y, exactly to WY; daughter untouched; no RNG |
| `B_SHAM` | the identical experimental branch and audit record with an empty mask; controls the trigger and intervention machinery |
| `C_GLOBAL_ORGANISER_OFF` | the historical global Y->WY transformation, applied at the identical boundary through the same three-line operation with an all-true mask; a frozen fixture proves state-identity with the historical organiser_off_at path |

- the all-true mask reproduces the historical transformation exactly; applying it at the same boundary as A and B is what makes the paired comparison valid, and the equivalence is proven by fixture rather than asserted
- Pairing: all three arms of a block share one seed and are forked from one bit-identical pre-intervention state
- Matching gate: physical state hash and RNG fingerprint must be identical across the three arms before the intervention; any mismatch is a technical failure of the design and is not repaired after outcomes
- Not required: SELECTIVE need not equal SHAM; parent removal is supposed to be a perturbation

---

## 6. Qualification gates, both green before any world

- `UNARMED_INERTNESS = PASS_88_OF_88`, with 0 intervention calls made by the unarmed law.
- Intervention fixtures: all pass, including the global-off equivalence proof against
  `engine_obtc.py` lines 226-228 and the RCD01 tie case resolving at identity level 4.

---

## 7. Seeds — published before the first world

```
seed = 940000000 + int(SHA256(parent_tip|FMRT01|B1|BLOCK|index + 10000*bump)[:12],16) mod 50000000
```

`N_BLOCKS = 85`, `PRIMARY_SCIENTIFIC_WORLDS = 255`, `DISJOINT_FROM_KNOWN = True` against a registry of 341 known seeds, `ALL_UNIQUE = True`, `TOTAL_BUMPS = 0`.

> every block supplies all three arms from the SAME seed. Assignment is therefore complete and fixed before any world exists; there is no post-outcome allocation to make.

First five seeds: `945575213, 986782284, 970615247, 988835594, 968027991` ... last three: `957595937, 956882268, 955782649`.

---

## 8. Outcome firewall

During execution the operator may see only: `opaque block token`, `completed`, `technical failure`, `checksum written`.

Withheld until every block has completed: `condition`, `seed`, `trigger occurrence`, `R0`, `R1`, `R2`, `runtime`, `file size`, `stop step`, `centre count`, `X response`.

`NO_SCIENTIFIC_FAILURE_MAY_TRIGGER_REPLACEMENT = True`. A reserve may be spent only on a technical failure.

---

## 9. The four terminal dispositions, fixed in advance

- `MINIMAL_REPRODUCTION_CAUSALLY_QUALIFIED`
- `MINIMAL_REPRODUCTION_NOT_QUALIFIED__DAUGHTER_INDEPENDENCE_NOT_ESTABLISHED`
- `MINIMAL_REPRODUCTION_NOT_QUALIFIED__PRE_INTERVENTION_MULTIPLICATION_TOO_RARE`
- `MINIMAL_REPRODUCTION_TEST_TECHNICALLY_INVALID`

---

## 10. Claim ceiling

> minimal reproduction under R0+R1+R2 at the frozen B1 law. Not strong self-reproduction, not second-generation competence, not heredity, not evolution, not life.

Unconditionally, whatever this experiment returns:

```
H3_STATUS = NOT_TESTED
REPRODUCTION_STATUS = NOT_TESTED
HEREDITY_STATUS = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED
X_LAWSPEC_BASELINE = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
```

---

## 11. Durability of this freeze

`WINDOWS_PRE_RUN_DURABILITY` is recorded in the JSON as `PENDING`: that is its true value at the instant
this freeze is committed, because the freeze must be committed before it can be bundled and shipped.
**The committed freeze is never rewritten.** The outcome of the pre-run durability operation is written
to a separate file, `FMRT01_PRE_RUN_DURABILITY.json`, together with the SHA-256 of every artefact placed
on external storage and the result of an independent read-back verification. No scientific world is
started until that separate file records a `PASS`, or records an explicit user-confirmed download.

This rule exists because of a documented FDFLT01 incident: a freeze that is silently rewritten is
worthless even when its content matches.
