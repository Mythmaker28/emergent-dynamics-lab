# DOTC01 — DAUGHTER-ORGANISER-TURNOVER-CRITERION-01
## FINAL REPORT

A zero-run derivation. MRFA01 named two missing objects; this mission derives both, and then finds
that the phenomenon they describe **has already happened** in data that survived on Tommy's disk.

`NEW_SCIENTIFIC_RUNS_USED = 0`. No seed, no world, no trajectory was created, and no replay was needed.

---

## 0. The result in one paragraph

A daughter organising centre is redefined as a **continuously matched component of Y-occupied cells**
whose identity survives material change — not as a molecule. The event that proves it is a
**complete constituent turnover**: at least one Y birth and at least one Y removal inside one
continuous identity interval that is never empty. Applying that criterion to the 128 surviving PQEC01
worlds finds **4 centres in 4 of 44 B1 worlds** that complete a turnover, and **3 of the 4** keep
producing X at their own cells on both sides of the removal, persisting 99, 217 and 5644 further steps.
B2 is structurally incapable — zero Y deaths in 44 worlds — and A0 has no Y dynamics at all. The
architecture needs no change, B1 needs no replacement, and one clean prospectively frozen experiment
of 128 worlds exists.

Terminal disposition: `ORGANISER_TURNOVER_CRITERION_DERIVED__ONE_EXISTING_POINT_DIRECT_TEST_ELIGIBLE`.

---

## 1. Binding

Parent `MINIMAL-REPRODUCTION-FAILURE-AUTOPSY-01`, tip `bec963d5851389fc5dcd430c0df33d6a9eafcdeb`.

> the launcher names 9bc79c1 (MRFA01 C2). The actual tip is one commit later, bec963d5851389fc5dcd430c0df33d6a9eafcdeb (MRFA01 C3), which recorded the re-probed remote-write gate. Resolved from the repository rather than assumed from the prompt.

No container rollback this mission — HEAD is at the MRFA01 tip and MRFA01/, FMRT01/ and PQEC01/raw are all present; no restoration was needed.

| Programme | SHA256SUMS verified | bad |
|---|---|---|
| ORR01 | 0 | 0 |
| OBTC02 | — | — |
| OBFOR01 | 54 | 0 |
| PQEC01 | 32 | 0 |
| FLCR01 | 36 | 0 |
| FTCTR01 | — | — |
| FLRS02 | 28 | 0 |
| FDFLT01 | 33 | 0 |
| RCD01 | 32 | 0 |
| FMRT01 | 129 | 0 |
| MRFA01 | 57 | 0 |

401 files verified, 0 bad. Engine byte-unchanged: True.

### Where each executable object actually lives

| Object | Status |
|---|---|
| `Y_BIRTH_LAW` | EXACT, event-aligned, from PQEC01 raw `ybirth` = (step, y, x, n_born) |
| `Y_DEATH_LAW` | EXACT, event-aligned, from PQEC01 raw `ydeath` = (step, y, x, n_died) |
| `Y_DIFFUSION` | EXACT from PQEC01 raw `yhop` = (step, sub, shift, ax, y_from, x_from, n_accepted) |
| `CENTRE_CLASSIFIER` | EXACT per step from PQEC01 raw `ycells` (step,y,x,...) which lists every Y-occupied cell |
| `LOCAL_X_SOURCE_LAW` | world totals per step from PQEC01 raw `xevent` = (step, n_X_born, n_X_died); per-cell X births are NOT stored by PQEC01 and are recoverable only by replay |
| `PERSISTENT_CENTRE_TRACKER` | DOES NOT EXIST AS A STORED OBJECT |
| `Y_BIRTH_DEATH_LEDGERS` | PRESENT AND EXACT in PQEC01 raw |
| `X_BIRTH_LEDGER` | WORLD-TOTAL ONLY in PQEC01 (`xevent`); per-cell X birth positions are not stored |

> PQEC01 recorded the exact event-aligned Y ledgers and the per-step local environment at every Y-occupied cell. Everything DOTC01 needs about the organiser process is in those bytes. No world is constructed and no trajectory is run.

`CLOC02` and `RSLOC03` are not used as numerical evidence anywhere.

---

## 2. The old object, stated without dismissing it

Recomputed from raw FMRT01 bytes: **22** triggered blocks, **every one** with exactly two Y-occupied
cells at maturation, one per centre. Selective removal takes [1] Y, global removal takes [2].
A single constituent survives the old 250-step window with probability **0.977112**.

```
OLD_DAUGHTER_OBJECT = SINGLE_Y_PARTICLE_WITH_LOCAL_X_FUNCTION
VALID_LOCAL_SOURCE__INSUFFICIENT_ORGANISER_LEVEL_IDENTITY
```

> the old object is a real, causally efficacious local X source: FMRT01's GLOBAL_OFF arm produced exactly zero X births in the daughter disc while the SELECTIVE arm produced a median of 110. What it does not carry is an identity that could survive replacement of its material, because it has only one constituent.

One caveat is recorded rather than glossed: FMRT01 stored N_Y only every 25 steps, so a birth and a death inside one 25-step gap would be invisible. This is why the organiser question is answered from PQEC01's exact event ledgers and not from FMRT01's sampled series.

---

## 3. The new object

**FUNCTIONAL_CONTINUITY_ACROSS_CONSTITUENT_TURNOVER.**

1. C remains spatially coherent under the frozen centre rule at every step in [t0,t1]
2. N_Y_C(t) >= 1 at every step in [t0,t1] — the component never becomes empty
3. at least one constituent-Y REMOVAL event is recorded inside C during [t0,t1]
4. at least one accepted constituent-Y BIRTH is recorded inside C during [t0,t1]
5. centre identity survives those material changes under the persistent spatial matching above
6. the local X organising function remains active across the turnover (see §5)

no parent-child assignment between Y molecules is invented, asserted or required. The engine keeps no Y tracker and DOTC01 does not create one.

> a static two-particle centre has more material but has demonstrated no organisational persistence through turnover; a single Y that survives a long time has demonstrated no material replacement. The criterion is the EVENT PAIR inside one continuous identity interval, not a count.

**Birth is inside the centre by construction, not by assumption.** a structural consequence of the frozen law, not an assumption: the Y birth branch of _react_core draws births with probability min(1, kY*nX*nY), which is zero at any cell with nY = 0. Every Y birth is therefore co-located with an existing constituent and is inside that constituent's component by construction.

### A theorem about the orderings

if N_Y_C = 1 and that constituent decays then N_Y_C = 0 and condition 2 fails at that step, ending the identity interval. A centre that begins the interval with one constituent can therefore reach COMPLETE_TURNOVER only through BIRTH_THEN_DEATH. This is a theorem about the frozen law and the definition, not an empirical claim.

The data confirms it rather than contradicting it: the single observed `DEATH_THEN_BIRTH` case had
`N_Y = 2` at the removal step.

---

## 4. The organiser timescale

| | B1 | B2 |
|---|---|---|
| muY | 9.261187281287937e-05 | 1e-08 |
| constituent e-folding, steps | 10797.3 | 1e+08 |
| exact discrete median lifetime | 7484 | 69314717 |
| P(one constituent decays by 11000) | 0.638964 | 0.000109994 |
| local Y-birth hazard, mean per step | 8.6805e-05 | 7.0632e-05 |
| birth-to-death hazard ratio | 0.9373 | 7.06e+03 |
| P(complete turnover by 1000) | 0.00575 | 0.00000 |
| P(complete turnover by 2500) | 0.02629 | 0.00000 |
| P(complete turnover by 5000) | 0.06495 | 0.00001 |
| P(complete turnover by 11000) | 0.11664 | 0.00006 |
| median / q80 / q90 | None / None / None | None / None / None |
| P(extinct before turnover) | 0.25524 | 0.00008 |

`None` means the quantile is not reached inside the horizon. The chain is driven step by step by each
world's realised hazard sequence; no mean is substituted for a time-dependent hazard, and the single
approximation is stated in `DOTC01_ORGANISER_TIMESCALE.md`.

**The hold is an event, not a clock.** The centre must carry its local X function through at least one
complete turnover. The horizon only bounds the observation, and it is not lengthened past 11000.

---

## 5. The audit: it already happened

| | B1 | B2 | A0 |
|---|---|---|---|
| worlds | 44 | 44 | 40 |
| identity intervals | 244 | 261 | 40 |
| worlds with partial turnover | 43 | 18 | 0 |
| worlds with COMPLETE turnover | 4 | 0 | 0 |
| centres with COMPLETE turnover | 4 | 0 | 0 |
| Y molecules born | 31 | 25 | 0 |
| Y molecules died | 40 | 0 | 0 |

Orderings at B1: {'BIRTH_THEN_DEATH': 3, 'DEATH_THEN_BIRTH': 1}.

### The four candidates, each scrutinised

| World | ordering | interval | first birth | first death | N_Y at removal | steps persisted after | X production before / after | functional |
|---|---|---|---|---|---|---|---|---|
| `B_B1_i010_s954932320` | BIRTH_THEN_DEATH | [2399, 2699] | 2550 | 2600 | 3 | 99 | True / True | **True** |
| `B_B1_i022_s960856267` | BIRTH_THEN_DEATH | [3202, 10282] | 9991 | 10065 | 3 | 217 | True / True | **True** |
| `B_B1_i031_s984994512` | BIRTH_THEN_DEATH | [0, 1694] | 1316 | 1694 | 2 | 0 | True / False | **False** |
| `B_B1_i037_s966307960` | DEATH_THEN_BIRTH | [1890, 7616] | 7230 | 1972 | 2 | 5644 | True / True | **True** |

`FUNCTIONAL_CONTINUITY_ACROSS_TURNOVER` in **3 of 4**. The one rejection is honest: in that world the removal fell on the last step of
the identity interval, so the centre never carried its function *through* the turnover.

> kX = 1.0, so p = min(1, kX*nX*nY) = 1 at any Y-occupied cell holding at least one X. X births there are then exactly min(nSX, free), a DETERMINISTIC count, so local X production is read off the reconstructed planes without any stochastic inference.

`STATUS = POST_OUTCOME_DEVELOPMENTAL_DIAGNOSTIC`. These are found in data that already existed, by a criterion written before the search.
They are a diagnostic, not a result, and the successor exists to fix that.

### Turnover is not creation

a fission ends the identity interval and starts new ones, so centre CREATION can never be counted as centre TURNOVER. §9 is enforced structurally, not by inspection.

In the same 44 worlds, `P(daughter formation AND functional turnover)` = **3/44 = 0.06818**, exact 95 % [0.01429, 0.18656].
counted directly in the same 44 worlds; no independence assumption is used every world with a complete turnover also had a two-centre episode. That is structural, not coincidental: a local Y birth is the SAME event that supplies a second constituent and, if the newborn later separates beyond CORE_R, a second centre.

---

## 6. Which point, and whether the architecture is the problem

| | B1 | B2 |
|---|---|---|
| candidate | **True** | **False** |
| extinction share | 0.6364 | 0.0000 |
| third-centre share | 0.1591 | 0.1591 |
| X integrity failures | 0 | 0 |

**B2 is excluded structurally, not statistically.** muY = 1e-08 makes a constituent removal essentially impossible: P(one constituent decays within the whole 11000-step horizon) = 0.000109994. The ledgers confirm it exactly — ZERO Y deaths across 44 worlds and 11000 steps each. A removal event is a NECESSARY part of the turnover definition, so B2 cannot produce one. This is a structural exclusion, not a sampling result.

**B1 agrees with its own model**: the exact chain predicts 0.11664 and the ledger gives 4/44 = 0.09091, which lies inside the exact 95 % interval [0.02533, 0.21669].

### The architecture question

> the question does not need a feasibility argument at all, because the phenomenon has ALREADY OCCURRED. Four centres in the surviving PQEC01 B1 set complete a constituent turnover inside one continuous identity interval, and three of them keep producing X locally on both sides of the removal. An existence proof by observation supersedes any bound.

- *birth rate high enough for replacement always causes uncontrolled new centres* → **REFUTED BY OBSERVATION — replacement occurred at B1 while 28 of 44 worlds never exceeded one centre**
- *death rate high enough to create turnover always causes extinction before replacement* → **REFUTED BY OBSERVATION — 4 centres completed turnover; 3 kept producing afterwards for 99, 217 and 5644 further steps**
- *co-located Y cannot form a persistent multi-constituent centre under the scheduler* → **REFUTED BY OBSERVATION — N_Y reached 2 and 3 inside single components**
- *the engine has no mechanism for local replenishment inside an existing centre* → **REFUTED STRUCTURALLY — Y birth is Y-gated and therefore intrinsically intra-centre**

```
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
```

the standard requires a PROOF that the current state variables and transition laws cannot support a continuously functioning centre through constituent turnover. The opposite has been observed. No architecture change is proposed, considered or implied.

`NEW_PARAMETER_DESIGN_REQUIRED = False`. §12 asks for a new design only if NO existing point can produce constituent turnover. B1 produces it. No sweep, no interpolation, no new point.

---

## 7. Is one clean experiment available?

Primary endpoint: per seeded world: does at least one continuously matched centre satisfy FUNCTIONAL_CONTINUITY_ACROSS_CONSTITUENT_TURNOVER, judged by the criterion frozen in DOTC01 before any world is run

```
p <= 0
```

under the hypothesis that a centre's identity CANNOT survive removal of a constituent, a removal necessarily ends the identity interval, so a birth and a removal can never lie inside one interval and the event probability is exactly zero. Zero is not a chosen threshold: it is what the negated hypothesis forces.

**Said plainly:** with p0 = 0 a single qualifying event rejects, so the statistical power of this test is not where its value lies. Its value is PROSPECTIVE FREEZING: the criterion is fixed before the worlds exist, so the events cannot be found by searching after the fact. The developmental 3 of 44 is a diagnostic; a frozen 1 of N is evidence.

| Worlds | power at the conservative lower bound 0.01884 | power at the point estimate 0.06818 |
|---|---|---|
| 44 | 0.5669 | 0.9553 |
| 64 | 0.7040 | 0.9891 |
| 85 | 0.8015 | 0.9975 |
| 128 | 0.9124 | 0.9999 |
| 170 | 0.9606 | 1.0000 |
| 256 | 0.9923 | 1.0000 |

Recommended **N = 128**. 128 seeded worlds give 0.9124 power at the conservative lower bound 0.01884 and 0.9999 at the point estimate, well inside the 256-world budget, and leave room for the three-arm structure to be added later without a second freeze.

No matched fork: §14 prefers a matched causal fork only if parent-removal causality is load-bearing. For establishing that a centre carries organiser-level identity through turnover it is not: the question is about the centre itself, not about its dependence on a parent. The fork belongs to the SUBSEQUENT question and is deliberately not spent here.

---

## 8. The independent check

One checker, zero worlds, importing nothing from the primary analysis: components — scipy.sparse.csgraph.connected_components vs union-find; identity_matching — explicit per-step python mutual-best vs the primary implementation; lifetime_arithmetic — 50-digit Decimal vs IEEE double; birth_survival — complementary Decimal survival product vs numpy log1p reduceat; imports_from_the_primary_analysis — none.

13 quantities checked, **0 disagreements**. `INDEPENDENT_DERIVATIONS_AGREE`.

| Quantity | primary | checker |
|---|---|---|
| Y lifetime e-folding B1 | 10797.251615563411 | 10797.25161555908 |
| P(one constituent decays by 11000) B1 | 0.6389640630003623 | 0.6389640630005098 |
| P(one constituent decays by 11000) B2 | 0.00010999395132438305 | 0.00010999395077176674 |
| P(>=1 local Y birth by 11000) B1 | 0.3238843779120071 | 0.32388437791196045 |
| P(>=1 local Y birth by 11000) B2 | 0.48850675123450693 | 0.4885067512345519 |
| worlds with complete turnover B1 | 4 | 4 |
| centres with complete turnover B1 | 4 | 4 |
| orderings B1 | {'BIRTH_THEN_DEATH': 3, 'DEATH_THEN_BIRTH': 1} | {'BIRTH_THEN_DEATH': 3, 'DEATH_THEN_BIRTH': 1} |
| worlds with complete turnover B2 | 0 | 0 |
| total Y births B1 | 31 | 31 |
| total Y deaths B1 | 40 | 40 |
| total Y deaths B2 | 0 | 0 |
| centres persisting after the removal B1 | 3 | 3 |

---

## 9. Terminal disposition

```
ORGANISER_TURNOVER_CRITERION_DERIVED__ONE_EXISTING_POINT_DIRECT_TEST_ELIGIBLE
```

One conditional handoff, created and **not** executed: `HANDOFF_FRESH_DAUGHTER_ORGANISER_TURNOVER_TEST_01.md`.

B1, unchanged. No sweep, no interpolation, no new point, no architecture change.

---

## 10. Status

```
MINIMAL_REPRODUCTION_STATUS = NOT_ESTABLISHED
STRONG_SELF_REPRODUCTION_STATUS = NOT_TESTED
HEREDITY_STATUS = NOT_TESTED
R3_STATUS = NOT_TESTED
H3_STATUS = NOT_TESTED
REPRODUCTION_STATUS = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED
X_LAWSPEC_BASELINE = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
NEW_SCIENTIFIC_RUNS_USED = 0
RETROACTIVE_REPRODUCTION_CLAIM = NOT_MADE
```

Nothing here re-scores FMRT01, and nothing here is a reproduction claim. What has been shown is that
an organising centre in this engine can lose a constituent, gain a constituent, and go on organising —
and that the experiment which would establish that prospectively costs 128 worlds at a point the
programme already owns.
