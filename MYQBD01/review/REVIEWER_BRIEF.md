# MYQBD01 — INDEPENDENT ADVERSARIAL REVIEW BRIEF (the single authorized review of this seal)

You are an **independent adversarial reviewer**. Your job is to **refute**, not to praise.
Uncertainty is not evidence. Never write the bare word `REFUTED` (ambiguous): use only
`DEFECT_CONFIRMED`, `DEFECT_PLAUSIBLE`, `ATTACK_REFUTED` (= the attack failed, the claim stands).

## HARD CONSTRAINTS
- **Do NOT modify** the candidate branch, its source files, its outputs, or its Git history.
  You may read anything and you may write ONLY under `/home/claude/MYQBD01/review/`.
- **Do NOT replay a World.** Do not construct `kinetics.World`, do not call `_one_step`, do not
  import and run the engine on scientific parameters. `SCIENTIFIC_RUNS_USED` must remain 0.
  Reading `.npz` archives, reading source, exact arithmetic, enumeration and PGF algebra are fine.
- Do not run `git push`, `git commit`, `git checkout`, `git reset`, or any history-mutating command.

## THE CANDIDATE, BOUND BY BYTES
```
repo              /home/claude/edl
branch            codex/minority-y-q-bound-derivation-01
ACTUAL_TIP        f88147a3b5603aa2c301061c495fdd87200b3b55
parent tip        8c2afa32e1e19ecf7ee5ff6e803dbb50cf2f0367 (repaired PMCR01)
candidate outputs /home/claude/edl/MYQBD01/out/   (authoritative; 30/30 SHA256SUMS verify)
candidate sources /home/claude/edl/MYQBD01/code/
raw archives      /home/claude/OBFOR01/raw/*.npz  (28 arms: S__* static, M__* mobile)
engine source     /home/claude/ORR01/code/kinetics.py   (frozen; `_react`, `_one_step`)
observer source   /home/claude/ORR01/code/observe.py    (Q written in `pre_react`)
protocol          /home/claude/OBTC02/code/protocol_obtc02.py, obtc02_protocol.yaml
binding record    /home/claude/MYQBD01/seal/out/SEAL01_CANDIDATE_BINDING.json
```

## THREE PROVENANCE FACTS YOU MUST CARRY INTO YOUR FINDINGS (do not smooth them over)
1. The seal launcher's `CANDIDATE_REPORTED_TIP = decfda5` is **stale**: it is a true ancestor but
   one commit precedes the actual tip `f88147a…`. You review the ACTUAL tip.
2. `MYQBD01_MASTER_FREEZE.{md,json}` was **committed in the same commit** (`decfda5`) as
   `MYQBD01_ARM_LEVEL_Q_SUMMARIES.{csv,json}` and `MYQBD01_TEMPORAL_DEPENDENCE.json`. There is
   **no independent Git checkpoint** proving the freeze predates the detailed statistical access.
   Judge for yourself whether any surviving claim depends on that ordering.
3. MYQBD01's own §19 **already consumed one adversarial review** inside the candidate
   (`MYQBD01_REVIEW_AND_REPAIR.json`: concurring, 0 load-bearing, 3 cosmetic repaired). Yours is
   the **second** review overall. Read that record and state, per attack, whether you are
   repeating it, deepening it, or contradicting it.

## THE CANDIDATE'S DISPOSITION UNDER ATTACK
`FINAL_DISPOSITION = EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED`
with `ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED`, `SCIENTIFIC_RUNS_USED = 0`.

## THE 12 ATTACKS — run every one
**A1 — Q event phase.** The candidate claims `Q_LEDGER_EVENT_EXACT`: `Q` written in
`Recorder.pre_react` is exactly the binomial `n` parameter of the Y birth draw at that step.
Attack: verify the scheduler order in `kinetics.World._one_step` and that `free0` in `_react` is
computed ONCE before both the X and Y loop iterations. Find any step, sub-step, diffusion or
occupancy update that occurs between the `pre_react` write and the Y `cand` computation and that
could change `min(nSY, free)`. An off-by-one-phase `Q` would invalidate every downstream number.

**A2 — temporal dependence and unit of replication.** The candidate claims IAT ≈ 7 (static) / 9
(mobile) and that the unit is the ARM (14/branch), never the 9000 frames. Attack the IAT
estimator itself (Geyer initial-positive-sequence): recompute independently, try block-means and
a spectral estimate, and test whether IAT is stable across arms or heavy-tailed. If IAT is
badly underestimated, even the 14-arm claim may be optimistic. Also check: are the 14 arms within
a branch truly independent (distinct seeds), or do any share a seed / a parent state?

**A3 — branch separation.** The candidate reports static mean-of-arm-means E[Q] = 2.369048
(sd 0.130602) and mobile = 3.169730 (sd 0.162990). Recompute from raw. **List every arm ID and
its per-arm mean explicitly** — no aggregate may be reported without the arm list. Check whether
the separation is driven by one or two arms; check the burn-in choice (2000) by recomputing at
several burn-ins; check that arm→branch assignment matches `p_hop_Y` in each archive's own spec
rather than the filename prefix.

**A4 — DESCENDANT SPATIAL EXPOSURE. THIS IS THE MOST LOAD-BEARING ITEM.** The candidate claims
`Q_POSITION(x,t)` for a separated mobile descendant is **not recoverable** from the archives, and
the whole calibration disposition rests on that. **Try hard to refute it.** Open an `.npz` and
enumerate **every key**: for each, report exact `shape`, `dtype`, the meaning of each column, the
cadence (per step? per sub-step? per event?), and whether it is invertible. In particular attack
`birth_offsets (…,4)`, `hop_ledger (44000,4)`, `source_substep_ledger (44000,6)`,
`birth_substep_ledger (11000,6)`, `frames (220,)`, and the terminal `n*_final (36,36)` grids.
Ask: can the per-step full lattice occupancy be **deterministically reconstructed** by running the
recorded hop ledger backwards from the terminal grids, or forwards from an initial condition?
If yes, `Q_POSITION` IS recoverable and the candidate is **too conservative**. Give an explicit
reconstruction argument or an explicit information-theoretic obstruction (e.g. which species'
motion is unrecorded, whether hops are per-particle or aggregate, whether `frames` are lattice
snapshots and at what stride). Do NOT settle this by assertion in either direction.

**A5 — β = kY·E[Q].** The candidate says the scalar reduction is valid only for the first birth.
Attack both ways: (a) is it valid even for the first birth given clamping `p = min(1, kY·nX·nY)`
and the fact that `E[Q]` is an average over a correlated series? (b) is the candidate too
pessimistic — could a Jensen/martingale argument extend it further?

**A6 — two-Y independence.** The candidate proves two co-located Y draw ONE
`Binomial(c, min(1,kY·nX·2))` from a shared pool, hence not Galton–Watson. Verify against
`_react` source. Attack the counterexample's numbers (unclamped: support 4 vs 8, variance 0.84 vs
1.02; clamped kY=0.20: means 4.0 vs 4.8). Recompute them. Check whether the non-independence is
material at the *admissible* kY ≈ 4e-5 or only at the inflated demonstration kY.

**A7 — Y feedback.** Archives have `kY = 0`. The candidate bounds one birth's perturbation as
−1 SY locally, ≈100% of mean nSY ≈ 0.99, recovering at φ ≈ 0.20/step. Verify S0 and φ come from
the actually-loaded spec, not a class default. Attack: is a ~100% local depletion consistent with
calling the first-birth error "controlled"? Is the recovery model right (Binomial(S0−nSY, φ))?

**A8 — calibration vs structural preclusion. Argue BOTH sides.** The candidate says structural
preclusion is NOT proved, citing an in-box witness `c=3, kY=4e-5, muY=1.9511e-6` giving
`R = 1.000478 > 1` and a survival iteration. (a) Verify `R` and the survival fixed-point
arithmetic; check `stable_survival` converges and is not a numerically degenerate fixed point at
this tiny supercriticality. (b) Then argue the OPPOSITE: with `R − 1 ≈ 4.8e-4`, is the witness so
marginal that it is indistinguishable from criticality, and does the `Q10 = 0` fact (Q = 0 more
than half the time) make the sustained-`Q_MAX`/`c=3` premise inadmissible? If the witness is
vacuous, `STRUCTURAL_PRECLUSION_PROVED` may still not follow — say precisely what would.

**A9 — arm selection.** Verify all 28 delivered arms are used, none dropped, and no inclusion
rule is conditioned on an outcome. Check the code paths (`glob` patterns) for silent exclusions.

**A10 — target-derived input.** Verify no MYQBD01 computation consumes a quantity derived from
the target it is meant to predict (e.g. an `r80`-like statistic). The candidate claims an
AST-based check with zero data accesses. Re-derive independently; look for laundering through
intermediate files.

**A11 — developmental claim boundary.** The candidate labels all 28 arms
`POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC`. Attack any place in the outputs or reports where a
developmental quantity is nonetheless used as if confirmatory, or where a forbidden claim
(reproduction, heredity, autonomous cohesion, H3, a minority window, Kamimura–Kaneko) is implied.

**A12 — zero-run enforcement.** Verify the sentinel actually patches what it claims
(`World.__init__`, `World._one_step`, `seed_one_organiser`) in all three modules, that the
filesystem witness covers the real output roots, and that no MYQBD01 script could have started a
scientific world. Attack the sentinel's coverage, not just its report.

## OUTPUT — write exactly two files
`/home/claude/MYQBD01/review/MYQBD01_ADVERSARIAL_REVIEW.md` and `…/MYQBD01_ADVERSARIAL_REVIEW.json`

Every finding must carry ALL of these fields:
```
ID, ATTACK (A1..A12), SEVERITY (LOAD_BEARING | SUBSTANTIVE | COSMETIC),
STATUS (DEFECT_CONFIRMED | DEFECT_PLAUSIBLE | ATTACK_REFUTED),
CLAIM_ATTACKED, EXACT_FILE_AND_LINES, EXACT_NUMBERS,
WHY_IT_MATTERS, SETTLING_COMMAND_OR_CALCULATION, MINIMUM_REQUIRED_CHANGE,
RELATION_TO_PRIOR_INTERNAL_REVIEW (repeats | deepens | contradicts | new)
```
`LOAD_BEARING` means: if confirmed, the final disposition must change.

End the `.md` with exactly this block, one value each:
```
REVIEWER_VERDICT              = <one of: CANDIDATE_DISPOSITION_SUPPORTED |
                                 CANDIDATE_TOO_CONSERVATIVE__DISCOVERY_REGION_ALREADY_DERIVABLE |
                                 CANDIDATE_TOO_STRONG__EVEN_PROSPECTIVE_CALIBRATION_NOT_YET_JUSTIFIED |
                                 STRUCTURAL_PRECLUSION_PROVED |
                                 EVIDENCE_OR_PROVENANCE_INCOMPLETE>
LOAD_BEARING_DEFECTS          = <int>
SUBSTANTIVE_DEFECTS           = <int>
COSMETIC_DEFECTS              = <int>
ATTACKS_REFUTED               = <int of 12>
DESCENDANT_EXPOSURE_RECOVERABLE = <YES | NO | UNDETERMINED> (from A4)
SCIENTIFIC_RUNS_USED_BY_REVIEW  = 0
```
Be specific and numeric. A finding without exact file, lines and numbers is not a finding.
