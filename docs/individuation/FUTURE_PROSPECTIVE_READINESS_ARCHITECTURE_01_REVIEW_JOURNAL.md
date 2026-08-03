# FUTURE-PROSPECTIVE-READINESS-ARCHITECTURE-01 — review journal

Complete record of the independent adversarial review, per Part I §13 (R1–R7). Every finding is
recorded, including those judged invalid, with the reason for the judgement; every correction; every
withdrawal; and the exact package each verdict was issued against.

---

## 1. Packages and hashes

| Checkpoint | Commit | `REPORT.md` sha256 | Bytes |
|---|---|---|---|
| 1 — frozen Part I | `b7f43b25c5d7ee0f7e75f258ffc89406f4062aa9` | `8ba61ce306d03081dec335b8e5b14aea6696763ed148395c172adf56f1410972` | 41,772 |
| 2 — candidate routes + preliminary decision | `8cfdb2e5598555d2bd91a38da6bd020d7c78ee35` | `4789f8d4a32dfc90e0a9c9b4feb5316512a755c8627ce01d2f57976c947d5f33` | 88,370 |
| 3 — round-1 corrections (Part III) | not committed separately | `2aeb2b80f9b6104f45b7057fafc3ae3a127388643b2f7e8519305a837696d59c` | 121,410 |
| 4 — round-2 corrections (Part IV) — the round-3 review package | not committed separately | `1205bf159aeae8c3eede705fa337d8b3a7b40c40495d3bf04fb77aca66de5a80` | 150,988 |
| seal — Part V appended | *this commit* | recorded in `DECISION.json` | see `DECISION.json` |

Round 1 verdicts were issued against the checkpoint-2 package
(`4789f8d4a32dfc90e0a9c9b4feb5316512a755c8627ce01d2f57976c947d5f33`) and against no other. Round 2
verdicts were issued against the 121,410-byte package (`2aeb2b80…`) and against no other. Round 3
verdicts were issued against the 150,988-byte package (`1205bf15…`), the route-neutral roadmap
(`70555225eacea33f8fabc155186b59c1875c27ec66bed155e30581104f0edd5d`) and this journal as then drafted
(`15094a542daccf27260fd50a213b9d563372abb020f2f09a35ada95d77ffa3a7`) — and against no other.
`DECISION.json` was not part of any reviewed package; it records the round-3 verdicts and is written
afterwards. Part V is appended after the round-3 verdicts and is therefore not covered by them.

Part I is a byte-exact 41,772-byte prefix of every later version of the report. Verified at each
checkpoint.

## 2. Reviewer charters

- **Reviewer A — scientific design and falsifiability.** Attack estimands; power and MDE;
  denominators; equivalence claims; alternative hypotheses; the claim ladder; whether a negative
  result would truly be informative. Instructed to recompute every reported number independently and
  to report any arithmetic that does not reproduce. Instructed that a reviewer who finds nothing is
  presumed not to have read carefully, and that the preferred route may be rejected.
- **Reviewer B — selection bias and provenance.** Attack use of closed-family knowledge; hidden
  tuning; eligibility and replacement; survivorship; initial-condition dependence; symmetry leakage;
  niche and shared-field confounding; evidence-root anchoring; OP-L3; and whether the chosen route is
  genuinely executable. Given the accepted owned-pipeline source and instructed to check the claimed
  API against it.

The reviewers worked independently and concurrently. Neither saw the other's findings. Neither was
told the author's preferred outcome beyond what the package itself states.

## 3. Round 1 — findings

### 3.1 Reviewer A (21 findings: 7 BLOCKER, 11 MAJOR, 3 MINOR) — `VERDICT: FAIL`

| ID | Sev | Location | Finding | Disposition |
|---|---|---|---|---|
| A1 | BLOCKER | §II.1.4 | "Two free constants only" is false: `matter_threshold=0.45`, `min_cells=3`, `max_centroid_displacement=3.0`, `max_area_ratio=3.0`, `dilation_radius=1`, `unique_score_margin=1e-12` all determine the primary outcome | **ACCEPTED** → W1; G3, G16 → FAIL |
| A2 | BLOCKER | §II.1.4 E-2 | `ε` does not exist in `advance_passive_tracer`'s API; it is an undeclared empirical threshold that scales `T_complete`, `H` and `Δ` | **ACCEPTED** → W2; G13 → FAIL |
| A3 | BLOCKER | §II.1.8 | NEGATIVE arm reaches 80% power only at `Δ ≈ 0.0138`, 7× below `Δ₀`; indifference region collapsed to a point; `L = 231` needed for 80% at `Δ = 0.05` | **ACCEPTED** (recomputed and confirmed) → W3; G18 → FAIL |
| A4 | BLOCKER | §II.1.10 | At 49% horizon censoring — one point under the discriminator — a frame with `q = 0.70` flips from certain POSITIVE to 76%-probable NEGATIVE | **ACCEPTED** → W16; G26 → FAIL |
| A5 | BLOCKER | §II.1.2 vs §II.2.4 | Asymmetric deferral: Route E defers its population (needs `engine.py`) while Route G is failed for needing `engine.py` | **ACCEPTED** → W22; standard applied symmetrically; G13 → FAIL for Route E |
| A6 | BLOCKER | §II.1.4, G6 cell | Turnover and persistence share the tracker's component identity; an identity swap produces exactly the POSITIVE signature; onset-`SPLIT`/`MERGE` tracks admit lineage survival | **ACCEPTED** → W4, W25; G6 → FAIL |
| A7 | BLOCKER | §II.1.14 | The tracer is a per-engine-step operator requiring pre/post matter and flows; tracks exist only after acquisition; the prerequisite is not one bounded channel | **ACCEPTED** → W5; G27, G28 → FAIL |
| A8 | MAJOR | §II.1.9 | Rung 3 refers to *the state* of rungs 1–2; Route E measures no state variable | **ACCEPTED** → W8; ceiling corrected to below rung 3 |
| A9 | MAJOR | §II.1.4 E-1 | `percolates` is a derived property (`wraps_y or wraps_x`), not an independent field; "does not wrap" is not entity-likeness | **ACCEPTED** → W10 |
| A10 | MAJOR | §II.1.7 | `Δ₀` justification has two undeclared free constants spanning 0.056–0.206; `(0.95, 30)` chosen to land on 0.10 | **ACCEPTED** → W11; G17 → FAIL |
| A11 | MAJOR | §II.1.8 | MDE 0.240 is an output presented as a justified target; `L = 60`, `R = 6`, `C = 2` unjustified | **ACCEPTED** → W12; G23 → FAIL |
| A12 | MAJOR | §II.1.5 | Attenuation table assumes `p₁ = p₂`; the cross-class conjunction attenuates more than `R` does | **ACCEPTED** → W19 |
| A13 | MAJOR | §II.4.2 | Tally says 8 fatal failures, list and table contain 10; non-binary verdicts violate §6/§10.1; Route F `N-A` unexplained | **ACCEPTED** → W19, W20; corrected to 7 after W23 |
| A14 | MAJOR | §II.2.2 | TOST size wrong: `n ≈ 271` for 90% power, not 214 (achieved power at 214 is 0.800); H2's unit should be the pair | **ACCEPTED** (recomputed: 270.55; power at 214 = 0.7998) → W19 |
| A15 | MAJOR | §II.1.13 | At `L₂ = 20` a NEGATIVE can never be reproduced (CP upper at `k=0` is 0.168); "consistent with" undefined | **ACCEPTED** → W13 |
| A16 | MAJOR | §II.1.11 | Calibration is not endpoint-blind (`T_complete` *is* E-2); `q₉₀` is survivor-conditioned on an undeclared `H_cal` | **ACCEPTED** → W6; G21 → FAIL |
| A17 | MAJOR | §II.4.1 vs §II.1.10 | Four alternative explanations declared, three discriminated; "detector artefacts" has none | **ACCEPTED** → W17 |
| A18 | MAJOR | §II.4.2 G5 | "PASS by declination" untenable: E-1 is named "Entity-like" and the ceiling claims the substrate can supply entities; environmentally-pinned structures are unconfronted | **ACCEPTED** → W9; G5 not credited |
| A19 | MINOR | §II.1.8 | Worst-case CP half-width at `L = 60` is 0.132, not 0.163 (0.163 is the unselected `L = 40` row) | **ACCEPTED** (recomputed: 0.13194) → W19 |
| A20 | MINOR | §II.2.4 | Enrolment table divides 30.354 while the text says 31 | **ACCEPTED** → W19 |
| A21 | MINOR | §II.1.2, §II.1.7 | Attribute 3 declared "None"; attribute 5 declared as two strategies; "lost" unmapped; α, direction and the negative boundary rate undeclared | **ACCEPTED** → W27 |

### 3.2 Reviewer B (19 findings: 10 BLOCKER, 6 MAJOR, 3 MINOR — per the severity column below) — `VERDICT: FAIL`

| ID | Sev | Location | Finding | Disposition |
|---|---|---|---|---|
| B1 | BLOCKER | §II.1.4, G3/G16 | Same six undeclared constants as A1, plus: `matter_threshold` is an *absolute* cut while `F` varies matter scale, so `Δ` partly measures proximity to 0.45 | **ACCEPTED** → W1 |
| B2 | BLOCKER | §II.1.3–4 | The sampling cadence is never declared, yet it determines E-1, E-3 and E-4 through the 3.0-cell association window | **ACCEPTED** → W14; G24 → FAIL |
| B3 | BLOCKER | §II.1.4 E-4 | Rule and gloss are different endpoints; under the rule the endpoint is survival to `~4·q₉₀`, i.e. survivorship promoted into the outcome definition | **ACCEPTED** → W15 |
| B4 | BLOCKER | §II.1.11 | `H` is a data-dependent scalar that Δ is monotone in; no P8 sensitivity; no `H`-too-long discriminator; blindness unenforceable | **ACCEPTED** → W6, W16 |
| B5 | BLOCKER | §II.1.7 | The document declares 60 + 20 laws, so a 30-law screen is not "the largest bounded budget"; `1 − 0.05^(1/60) = 0.0487` | **ACCEPTED** → W11 |
| B6 | BLOCKER | §II.1.2–3 | `F` and the IC classes deferred while every parameter is fixed; eligibility blindness asserted about unread `engine.py` | **ACCEPTED** → W22, W26 |
| B7 | BLOCKER | §II.1.14, §II.4.3 | At least five prerequisites, not one; the accepted module runs no engine and persists boolean masks only; an accepted cohort field inverts the produce-never-accept property | **ACCEPTED** → W5; G28 → FAIL |
| B8 | BLOCKER | §II.1.11–12 | Calibration sets `H` *and* measures cost feeding the authorisation decision — a dual-role family | **ACCEPTED** → W6; G21 → FAIL |
| B9 | BLOCKER | §II.1.10 | McNemar tests marginal homogeneity and is null exactly where symmetric IC dependence is strongest; no numeric threshold attached | **ACCEPTED** → W7; G26 → FAIL |
| B10 | BLOCKER | §II.2.4, §II.4.2 | Route G's adjudication is not honest: asymmetric deferral (a), fabricated G16 charge (b), composite rescue withheld (c), hedged verdicts and a miscount (d) | **ACCEPTED** → W22, W23, W24, W20; Route G's count corrected to 7 |
| B11 | MAJOR | §II.1.3, §II.1.5 | `L`, `C`, `R`, `k_cell`, `L₂` unjustified; `C = 2` with a conjunctive both-class rule reproduces the closed family's design shape | **ACCEPTED** → W12 |
| B12 | MAJOR | §II.1.13 | The reproduction family cannot fail: CP intervals at `L₂ = 20` are consistent with almost anything | **ACCEPTED** → W13 |
| B13 | MAJOR | §II.5 | V1.2 (root omits component mass and the calibration record), V1.5 (a push credential is a secret; tags are force-updatable), V1.7 (enforcement deferred to a non-existent runner) all unmet | **ACCEPTED** → W18; G30, G31 → FAIL |
| B14 | MAJOR | §II.0 | Read ledger understates entries 9, 11, 12 and lacks the ranges §11.6 requires | **ACCEPTED** → W21 |
| B15 | MAJOR | §II.1.10 | The two 50% floors are round numbers with a discontinuous, uncalibrated effect on the terminal call | **ACCEPTED** → W16 |
| B16 | MAJOR | §II.1.4 | Late-born tracks have `H − t_birth` to satisfy E-3/E-4 — an immortal-time asymmetry; cohort inheritance across `SPLIT`/`MERGE` undeclared | **ACCEPTED** → W25 |
| B17 | MINOR | §II.1.4 E-1 | `percolates` is a property, not a field (duplicate of A9, independently found) | **ACCEPTED** → W10 |
| B18 | MINOR | §II.1.8 | Worst-case half-width is 0.132 (duplicate of A19, independently found); every other figure reproduces exactly | **ACCEPTED** → W19 |
| B19 | MINOR | §II.1.4, §II.6 | No rounding convention for `2·T_complete`; the frozen import pins one module while the endpoint depends on `instrumentation.py` too | **ACCEPTED** → W27 |

### 3.3 Findings judged invalid

**None.** Every finding from both reviewers was accepted. Where the two reviewers differed on the
*charge* rather than the *defect* — B10(b) argued that Route G's G16 failure was an over-charge that
should have been G14 — the reviewer's correction was applied against the author's own earlier
adjudication (W23), reducing Route G's failure count from ten to seven.

### 3.4 Independent convergence

Three defects were found independently by both reviewers, from different charters:

| Defect | Reviewer A | Reviewer B |
|---|---|---|
| The primitive rests on six undeclared numeric constants | A1 | B1 |
| Asymmetric deferral standard between Route E and Route G | A5 | B6, B10(a) |
| "One bounded engineering prerequisite" is false | A7 | B7 |

Blind convergence on the three load-bearing claims was treated as dispositive rather than as
duplication.

## 4. Corrections applied

Twenty-seven corrections, W1–W27, recorded in Part III §III.2. Per R3 they were applied **additively**;
per R4 every false claim was **withdrawn** with its original text left standing in Part II rather than
rewritten. No limitation was deleted in order to pass. Two corrections went **against** the author's
own earlier position and in favour of the rejected route (W23, W24).

The corrections did not rescue Route E. They were not intended to: the author's judgement, recorded
here, is that repairing Route E inside this mission would have meant designing under review pressure
with the specific inputs (`engine.py`, the law space, the detector scale, the tracer semantics) that
this mission's firewall forbids. Attempting it would have reproduced the exact defect the reviewers
identified — fixing parameters before the population is defined.

## 5. Round 2 — targeted re-review of the corrected package

Both reviewers were returned the corrected package — Parts I + II + III of the report plus this
journal and the then-current roadmap — and asked a narrow question: is the corrected adjudication and
the `ARCHITECTURE_REVISE` disposition sound, are the withdrawals complete and honest, and is anything
still overclaimed. The reviewed report's Parts I+II were byte-identical to the checkpoint-2 package
(`4789f8d4a32dfc90e0a9c9b4feb5316512a755c8627ce01d2f57976c947d5f33`, verified independently by
Reviewer B); the reviewed report including Part III was 121,410 bytes, sha256
`2aeb2b80f9b6104f45b7057fafc3ae3a127388643b2f7e8519305a837696d59c`.

Both reviewers returned `VERDICT: FAIL`. **Both explicitly confirmed the terminal disposition.**
Reviewer A: *"`ARCHITECTURE_REVISE` is the right one, and it is overdetermined … `STOP_PROSPECTIVE_READINESS`
would be wrong."* Reviewer B: *"Honest, and doubly grounded … it buys no authorisation … so it is not
a way of avoiding a stop."* Both `FAIL` verdicts were directed at the corrective apparatus.

### 5.1 Reviewer A round 2 (A22–A33: twelve findings — 4 BLOCKER, 6 MAJOR, 2 MINOR) — `VERDICT: FAIL`

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| A22 | BLOCKER | §III.4's corrective gate table reproduces the non-binary defect it withdraws ("at issue", "pass or not reached"); G5 must be FAIL; §III.8 item 14 defers to Architecture 02 a requirement §6 imposed on this table | **ACCEPTED** → X1, X2; superseded by §IV.3 |
| A23 | MAJOR | Route G's corrected count of 7 is not derivable — G9 was dropped undisclosed | **ACCEPTED** → X3; G9 restored for both routes |
| A24 | BLOCKER | §III.7 item 3's "none of these was faulted" is false: W26, W15/W25 and W3 fault three of the four | **ACCEPTED** → X4; claim withdrawn |
| A25 | MAJOR | §III.7 items 1, 4, 5 overclaim: reviewer silence is not establishment; "confirmed"; a universal from two routes | **ACCEPTED** → X5 |
| A26 | MAJOR | §III.7 item 2's "genuinely closed" contradicts the document's own G11/G24 FAIL on cadence | **ACCEPTED** → X5 |
| A27 | BLOCKER | §III.8 omits W15, W17 and W27 while §III.11 claims fourteen items is complete | **ACCEPTED** → X6; superseded by the eighteen-item list at §IV.4 |
| A28 | BLOCKER | The roadmap re-selects Route E after "primary route: none" | **ACCEPTED** → X10; roadmap replaced with a route-neutral one |
| A29 | MAJOR | Item 3's sensitivity remedy leaves the absolute-cut defect intact | **ACCEPTED** → X7 |
| A30 | MAJOR | Item 5's "or an identity-swap discriminator" branch does not clear G6 | **ACCEPTED** → X8; branch removed |
| A31 | MAJOR | §III.9 narrates a completed re-review that had not occurred; `DECISION.json` absent; no round-2 package hash | **ACCEPTED** → X9; superseded by §IV.1 and this section |
| A32 | MINOR | §III.6's R5 reasoning is wrong — the disqualifier is the gate failures | **ACCEPTED** → X14 |
| A33 | MINOR | §III.1 overstates reviewer conduct | **ACCEPTED** → X15 |

### 5.2 Reviewer B round 2 (B20–B30: 1 BLOCKER, 7 MAJOR, 3 MINOR) — `VERDICT: FAIL`

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| B20 | MAJOR | Undisclosed removal of the G9 charge against Route G, inside a correction whose purpose was to fix a miscount | **ACCEPTED** → X3 |
| B21 | BLOCKER | W20 asserted remedied and is not; journal §6 stated it as governance fact; Route G's hedged cells never resolved; Route F's `N-A` still unexplained | **ACCEPTED** → X1; §IV.3 is fully binary and states Route F's reason |
| B22 | MAJOR | The §11.6 read-ledger obligation was deferred to a successor instead of discharged, and the deviation was not declared as a §14 trigger | **ACCEPTED** → X17; ledger discharged at §IV.5, deviation declared |
| B23 | MAJOR | W26 withdrawn with no gate consequence | **ACCEPTED** → X12; G14 and G15 → FAIL |
| B24 | MAJOR | Roadmap step 3 understates its own scope — an engine-driven path cannot be qualified without running the engine, which is a new family; "factor of five" is a reverse-engineered magnitude | **ACCEPTED** → X11; step 3 rewritten |
| B25 | MAJOR | The roadmap installs Route E as the sole live path after "primary route: none", importing §10.8 non-criteria | **ACCEPTED** → X10 |
| B26 | MAJOR | Residual closed-family leakage: post-hoc "independent justification" of inherited instrumentation defaults is the `Δ₀` pattern | **ACCEPTED** → X7; provenance must be established or the values replaced |
| B27 | MAJOR | R7 unmet for round 2 — no package hash, `DECISION.json` absent, verdicts narrated but not recorded | **ACCEPTED** → X9; hashes recorded above |
| B28 | MINOR | §10.5's comparator silently changed from "admissible" to "corrected" | **ACCEPTED** → X16; substitution declared |
| B29 | MINOR | Residue location misstated | **ACCEPTED** → X18; corrected at §IV.7 |
| B30 | MINOR | `Δ₀` omitted from the corrected derivation ordering | **ACCEPTED** → X19; added at §IV.4 item 8 and in the roadmap |

### 5.3 Findings judged invalid — round 2

**None.** All twenty-three round-2 findings were accepted. Twenty corrections, X1–X20, follow in
Part IV §IV.2. Three of them (X3, X12, X13) **increase** the number of charged gate failures against
the author's own earlier adjudication; one (X3) restores a charge against Route G that the author had
silently dropped.

## 6. Round 3 — confirmatory re-review

Reviewed package: the report at 150,988 bytes (Parts I–IV),
sha256 `1205bf159aeae8c3eede705fa337d8b3a7b40c40495d3bf04fb77aca66de5a80`; the route-neutral roadmap,
sha256 `70555225eacea33f8fabc155186b59c1875c27ec66bed155e30581104f0edd5d`; and this journal as then
drafted, sha256 `15094a542daccf27260fd50a213b9d563372abb020f2f09a35ada95d77ffa3a7`. `DECISION.json`
was **not** in the reviewed package — it records these verdicts — and neither reviewer saw it.

| Reviewer | Verdict | New findings |
|---|---|---|
| A — scientific design and falsifiability | **PASS** | A34–A41 (0 BLOCKER, 3 MAJOR, 5 MINOR) |
| B — selection bias and provenance | **PASS** | B31–B38 (0 BLOCKER, 6 MAJOR, 2 MINOR) |

`PASS` means what the charge defined: the sealed package and its `ARCHITECTURE_REVISE` disposition are
sound and honest — **not** that any route is admissible. Both reviewers stated that no BLOCKER-level
defect remains, that none of their residual findings disturbs any of the three grounds for the
disposition, and that none converts a `FAIL` into a `PASS` or brings any route near admissibility.

All fourteen round-3 findings were accepted and corrected in Part V §V.3 as Y1–Y11. The most
consequential, A34/B31, **increases** the charge against Route G — the route the author did not prefer
— from fifteen fatal failures to eighteen, by applying the channel-inheritance argument symmetrically
to G3, G16 and G24. Y2 adds three further successor requirements; Y5 and Y6 correct the roadmap; Y7
removes an operative number derived from a withdrawn value; Y11 declares a third Part I deviation.

## 7. Governance record

- No candidate document was edited after a reviewer verdict was issued against it; corrections were
  appended as Parts III, IV and V. The one exception is this journal and the roadmap, which are
  working records rather than sealed candidates and which are updated in place, with every hash each
  verdict was issued against recorded in §1.
- Part I was never modified. Byte-exact prefix verified at checkpoints 1, 2 and 4.
- No gate was averaged, weighted, scored or traded. Part III §III.4's attempt to resolve the
  checkpoint-2 table's hedged verdicts was itself incomplete — it used "at issue" and a composite
  "pass or not reached" bucket, and journal §6 previously asserted, falsely, that the resolution was
  complete. Both reviewers caught this (round-2 findings A22, B21). The complete binary adjudication is Part IV §IV.3, as corrected by Part V §V.3 Y1, which
  assigns exactly one of `PASS` / `FAIL` / `N-A` to all thirty-two gates for all three routes and
  states Route F's inapplicability reason once, as §6 requires.
- No backup route was named, because §10.7 requires a backup to pass all thirty-two gates
  independently and none does.
- The author's preliminary decision (`PROSPECTIVE_ROUTE_SELECTED`, Route E) was overturned by review.
  That is recorded as the outcome, not softened. Route E ends the mission with **25** fatal gate
  failures and Route G with **18** (fifteen in §IV.3, plus G3, G16 and G24 added by Y1).
- The first roadmap named Route E in four steps after the report had declared "primary route: none".
  Both reviewers rejected it. The roadmap is now route-neutral and requires Architecture 02 to re-run
  the §10 comparison from the beginning.
- A Part I deviation is declared, not glossed: the §11.6 read-ledger obligation is only partly
  discharged (Part IV §IV.5). Under §14 that is itself an `ARCHITECTURE_REVISE` trigger.

## 8. Round-3 verdicts

`PASS` / `PASS`, recorded in §6 above and in
`FUTURE_PROSPECTIVE_READINESS_ARCHITECTURE_01_DECISION.json` under `review.round_3`. The terminal
disposition `ARCHITECTURE_REVISE` does **not** require reviewer `PASS`; per Part I §13 R6, only
`PROSPECTIVE_ROUTE_SELECTED` does, and it is not claimed. The `PASS` verdicts are recorded because
they were obtained, not because the disposition rests on them.

## 9. Totals

| Round | A findings | B findings | Verdicts |
|---|---|---|---|
| 1 | A1–A21 (7 BLOCKER, 11 MAJOR, 3 MINOR) | B1–B19 (10 BLOCKER, 6 MAJOR, 3 MINOR) | FAIL / FAIL |
| 2 | A22–A33 (4 BLOCKER, 6 MAJOR, 2 MINOR) | B20–B30 (1 BLOCKER, 7 MAJOR, 3 MINOR) | FAIL / FAIL |
| 3 | A34–A41 (0 BLOCKER, 3 MAJOR, 5 MINOR) | B31–B38 (0 BLOCKER, 6 MAJOR, 2 MINOR) | PASS / PASS |
| **total** | **41** | **38** | — |

**Seventy-nine findings. Zero judged invalid.** Fifty-eight corrections: W1–W27 (round 1), X1–X20
(round 2), Y1–Y11 (round 3). Four of them — X3, X12, X13 and Y1 — increase the number of charged gate
failures against the author's own earlier adjudication; one (W23) withdraws an over-charge in favour of
the rejected route.
