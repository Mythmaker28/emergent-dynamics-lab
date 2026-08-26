# EVCS01 — FINAL REPORT

```
FINAL_DISPOSITION = E3_ENDPOINT_COMPOSITION_MEASURED__DECISION_REFERRED_TO_THE_OWNER
LOAD_BEARING_DEFECT_COUNT = 0
NEW_SCIENTIFIC_WORLDS_USED = 0
LAUNCHER = SELF_ISSUED
```

## What this mission was for

CLEA01 closed with a finding aimed at its parent: the qualified OMLDCT02 E3 component contains Y
mass with no causal path to the daughter. `E3_DURATION` and `E3_EXPOSURE` are not OMLDCT02's
endpoints alone — they are the programme's measuring instrument, and any successor reuses them.
This mission measured what that instrument actually contains, and turned the accrual arithmetic
into committed code. Zero worlds, zero seeds.

## The launcher was mine, and that is the first thing to distrust

The owner authorised the choice of mission, not its content. An operator who writes his own mandate
can write one he is guaranteed to pass. Three guards were declared in advance:

| guard | outcome |
|---|---|
| method committed before any measurement | **HELD** — verified from git by the checker, not from my prose |
| an inconvenient result named in advance | **HELD** — and it did **not** occur, and that was reported |
| no threshold, no verdict on the science | **HELD in the code, BREACHED in my C2 commit prose** |

The third breach is real and the checker was right to press it. My C2 subject line said *"the
endpoint is clean in 64 arms and materially foreign in one"* — a magnitude verdict I had
pre-committed not to render, on a tally that folded in the 33 arms I had myself declared
uninformative. Retracted at C3. The commit is immutable and stands wrong.

## Gate 0

Model A reconstructed from LDFMA01's frozen classifier reproduces the parent's own `E3_DURATION`,
`E3_EXPOSURE` and interval row count **exactly in 66 of 66 arms**. The checker did not take that on
trust: it rebuilt Model A with a different component algorithm, integer centroids, forward-only
identity tracking and coordinate sets, and reproduced all four quantities in all 66. That
independent verification is the checker's, not mine.

## What E3_EXPOSURE is made of

```
SHAM        16765 units    CERTAIN 15505 (0.9248)   POSSIBLE_ONLY 525 (0.0313)   NO_CAUSAL_PATH 735 (0.0438)
SELECTIVE   18204 units    CERTAIN 18204 (1.0000)   POSSIBLE_ONLY   0            NO_CAUSAL_PATH   0
```

**The SELECTIVE column is uninformative by construction and is evidence of nothing.** After the
intervention the daughter is the world's only Y source, so everything descends from it. The launcher
said so before the number existed; the checker verified the mechanism independently (33 of 33 arms
are exactly one component at `t_m+1`, and the 23 that later split stay CERTAIN).

In the control arm, the foreign mass concentrates:

```
402 SHAM   2080 = 859 CERTAIN + 525 POSSIBLE_ONLY + 696 NO_CAUSAL_PATH    33.5% of that arm
518 SHAM   1669 = 1630 + 0 + 39                                            2.3%
31 of 33 SHAM arms carry no non-CERTAIN mass at all
13 interval rows counted in E3_DURATION contain no daughter-descended mass whatever
```

Whether that is acceptable in an endpoint a successor would reuse is **not decided here**. No
threshold separates acceptable from unacceptable, this mission does not supply one, and a
self-issued mandate has no standing to decide it. It is referred to the owner.

## A correction to a closed parent mission

CLEA01 states that every cell Model A carries and Model C does not was *"never CERTAIN and never
POSSIBLE at any row. Not ambiguous origin — no causal path at all."*

My own measurement refutes that for 402 SHAM. **525 of that arm's 1221 non-CERTAIN units — 43 %,
across 81 of 238 interval rows — are POSSIBLE.** They do have a causal path to the daughter; it is
simply not exclusive. CLEA01's sentence held only on the three rows it republished. 518 SHAM is
unaffected, the G4 verdict of 64 of 66 is unaffected, CLEA01's terminal is unaffected, and no
OMLDCT02 number moves. No CLEA01 file is modified — the correction is recorded in the mission that
measured it.

I held this in hand and did not report it. The reason is instructive rather than exculpating: the
`EXAMPLE_ROWS` cap fires only on rows carrying NO_CAUSAL_PATH mass, so no POSSIBLE_ONLY row ever
reached the published artefact. The cap was frozen at C1 before I knew POSSIBLE_ONLY mass would
exist — honest, and still one-sided in exactly the direction I was looking.

## The sizing instrument, and the diagnosis I got wrong

I wrote, in C2 and to the owner in conversation, that two campaigns failed because *"a pair target
and a cost ceiling were frozen independently and never checked against each other."* **That is false
of both, and their own committed records say so.** FIMRCC01 ran **zero** worlds — its 0.0165 is the
number that *stopped* it at the precondition gate, and its pre-registration carried an explicit 80 %
power criterion. OMLDCT02's pre-run design file records `P_reaching_target = 0.9999` against the 512
ceiling. Both checked.

The real common cause is narrower and sharper: **the rate the check was performed at.** OMLDCT02
checked its 41-pair target against its 512-instance ceiling at 22/256 and got 0.9999. At the
realised 33/805 the identical check gives 0.075. The fragile input is the yield estimate, and a
check conditioned on a point estimate inherits that estimate's bias.

Which is exactly the error the checker then found in my own instrument. `REQUIRED_CEILING` was the
95th percentile **conditional on the rate being exactly 33/805**. Propagating the rate's own
posterior, a campaign freezing that value attains about **85 %**, not 95 — I reproduced the
checker's number independently at 0.8537. Fixed in code, not merely disclosed:

```
41 pairs at 95%, rate treated as known    785.1     <- what C1/C2 returned; optimistic
41 pairs at 95%, rate uncertain           887.1     <- freeze this one
OMLDCT02's frozen ceiling                 512       <- the instrument REFUSES it
```

The non-exchangeability of the TLMR01 developmental sizing set survives, but its evidence was
overstated by about 2.1e4: the published binomial tail of 4.16e-07 treated a 256-sample estimate as
a known parameter. The correct two-sample comparison gives **Fisher exact p = 0.008710**.

## The checker

One checker, no cascade. Verbatim return hashed before any finding was acted on. **28 findings, 9
MATERIAL, 6 MINOR, zero load-bearing** — and every MATERIAL one is prose or framing attached to a
right number. Its own summary of the pattern is the fairest description of this mission: *more
careful in its instruments than in its narration.* Ten corrections made, three of them to my own
immutable commit message, one to a closed parent mission, one to what the owner was told before this
mission existed.

## Claim ceiling

```
CLEA01_STATUS                 = CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED
OMLDCT02_STATUS               = INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED
OMLDCT02_PAIRED_STATISTICS    = DESCRIPTIVE_ONLY__NO_INFERENTIAL_WEIGHT
H3_STATUS                     = NOT_TESTED
REPRODUCTION_STATUS           = NOT_TESTED
HEREDITY_STATUS               = NOT_TESTED
AUTONOMOUS_COHESION_STATUS    = NOT_ESTABLISHED
X_LAWSPEC_BASELINE            = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
COMPANION_PAPER_V1_1_STATUS   = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED
```

Nothing measured here establishes anything about reproduction, authorises a successor campaign, or
reopens CLEA01.
