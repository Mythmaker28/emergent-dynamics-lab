# OMLDCT02 — FINAL REPORT

```
FINAL_DISPOSITION = INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS
```

One of the four frozen strings. No fifth was invented.

## What was asked, and what came back

One matched-control experiment, frozen before world 1: fork each admissible world at the trigger
step `t_m` into a `SELECTIVE_PARENT_REMOVAL` arm and a bit-exact `SHAM_NO_REMOVAL` arm, and compare
the locked daughter's post-intervention identity duration and particle-step exposure across the
pair.

```
BASE_SEEDS_ATTEMPTED       805 of 1024, strict frozen index order from 0
VALID_PAIRED_BLOCKS         33   (frozen minimum 41)
HARD_ARM_INSTANCE_COUNT    510.56902 of 512
CAMPAIGN_STOPPED           HARD_ARM_INSTANCE_CEILING
TECHNICAL_FAILURES           0
```

| endpoint | W+ | non-zero / zero | exact two-sided *p* | median log difference | Hodges–Lehmann | rejects |
|---|---|---|---|---|---|---|
| duration | 328.0 | 32 / 1 | **0.400946** | +0.128555 | +0.195665 | no |
| exposure | 348.0 | 32 / 1 | **0.231106** | +0.476476 | +0.307665 | no |

Sign convention SELECTIVE minus SHAM. The AND rule fails on two of its six conditions, and the
first of those — 33 pairs against a frozen minimum of 41 — settles the disposition on its own.

**These statistics are descriptive only.** The campaign under-accrued, so the owner's rule applies:
fewer than 41 pairs may not be interpreted using the paired *p*-values, even though the frozen
analysis computed them. They are recorded because bound code produced them and hiding them would
misrepresent what the pipeline did. They carry no inferential weight — not for an effect, not
against one, not for equivalence, and not for what a larger sample would have shown.

An earlier version of this report and the C4 commit message argued from those *p*-values in both
directions. Both arguments are retracted; see `OMLDCT02_UNDER_ACCRUAL_INTERPRETATION_RULE.json`.
The C4 commit message is immutable and stands wrong.

```
NULL_RESULT_INTERPRETATION = INCONCLUSIVE__NO_CLAIM_OF_EQUIVALENCE__NO_CLAIM_OF_NO_EFFECT
```

No causal effect is established. No absence of one is established either. There is no equivalence
margin and none was invented. The reason is the pair count, not the arithmetic.

## Why it under-accrued

The observed admissible yield is 33/805 = **4.10 %**. The design was sized on the parent's
22/256 = **8.59 %**. Fisher exact on the two samples gives *p* = 0.0087 — real, and modest.

The checker put this more precisely than I had. My pre-run disclosure `P(reaching 41 pairs) = 0.9999`
was computed by plugging the point estimate into the simulator with **no propagation of that
estimate's own sampling error**, from 22 events. Re-run at the lower 95 % bound of the same estimate
the frozen simulator returns **0.64**; at the observed rate, **0.076**. The failure that ended this
campaign sat inside the sizing estimate's own confidence interval before world 1. I framed a
foreseeable weakness as a surprise, and that framing was wrong.

Nothing was changed in response. No extra seeds, no raised ceiling, no replaced or reordered seed.

## What held

- **C2 preceded world 1**, proved from git topology, the pre-C2 guard record and mtime forensics.
  The guard refused four scientific-scale constructions before the freeze existed, and that refusal
  is in the record.
- **All five digests are reproducible** from committed generators, in a fresh clone, under a
  different Python. Four distinct labels; the checker audited fourteen hash keys and found no
  collision. OMLDCT01's one-label-two-quantities defect does not recur.
- **The seeds are provably fresh.** The checker regenerated all 1030 from the prose alone, field for
  field including every nonce, and found zero overlap with any OMLDCT01 seed, the four pilots, or
  anything else in the repository.
- **Zero classifier disagreements** across 132 endpoint computations — both arms, all 33 pairs.
- **Fork and intervention fidelity replicated independently** for all 33 pairs from the frozen
  seeds: identical physical and RNG state at the fork, parent emptied, daughter untouched,
  occupancy conserved, no random number consumed, sham inert, arms diverged afterwards.
- **The exact Pratt test is correct.** An independent brute-force enumerator with exact rational
  arithmetic agreed on 194 cases, and 120 further cases matched scipy's exact Wilcoxon. The scipy
  sentinel recorded zero calls across 805 worlds.
- **Sixty-six archives durable on Windows** in five verified batches, each reopened on the device
  and checked on seed, index, arm, schema, horizon, steps, sha256, law, integrity, `t_m` and the
  intervention flag.

## What did not hold, and is recorded rather than repaired

The single checker found **no load-bearing defect** and four MATERIAL ones. I accept all four.

1. `FREEZE_CONTENT_HASH` does not cover `METHODS_HASH` or `SEED_SET_HASH` — they are stripped as
   self-referential. My C1 claim that *"a freeze edited after C2 closes the gate again"* is **false
   for those two fields**.
2. The guard reads git for the token and the freeze but the **working tree** for the seed manifest,
   and a deleted freeze or a deleted seed manifest opens it. My claim that it *"reads git, not the
   working tree"* is two-thirds true. No fixture covers that path.
3. `omldct02_c3_raw.py` **contains a decision rule** — the undefined-log policy — and it fired at
   index 664, where both arms have duration 0. I said it *"chooses nothing"*. That was wrong. The
   branch taken is the one `PRATT_EXACT_SIGN_FLIP` requires, and dropping the pair entirely gives
   *p* = 0.3999 and 0.2240 and the same terminal.
4. The power disclosure, above.

Plus one prose error: the C2 commit message says the methods hash is over **36** files. It is over
**39**. The commit is immutable and stands wrong.

**Nothing was repaired.** Two of these are bugs I could fix in minutes. Fixing them would change a
file inside `METHODS_HASH` after world 1, which section 11 makes campaign-level invalidity, and
`MAX_POST_OUTCOME_SCIENTIFIC_REPAIRS = 0`. They are handed forward instead.

## The predecessor

OMLDCT01 was closed `OMLDCT01_TECHNICALLY_INVALID` on the owner's adjudication: four full-scale
trajectories on frozen candidate seeds preceded its master freeze, and those four seeds were then
retired on the strength of their own outcomes. Its pilot results survive only as
`DEVELOPMENTAL_PILOT_DIAGNOSTIC` and entered nothing here.

## The claim ceiling, unchanged

```
H3_STATUS                     = NOT_TESTED
REPRODUCTION_STATUS           = NOT_TESTED
HEREDITY_STATUS               = NOT_TESTED
AUTONOMOUS_COHESION_STATUS    = NOT_ESTABLISHED
X_LAWSPEC_BASELINE            = UNCHANGED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
COMPANION_PAPER_V1_1_STATUS   = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED
```

No constituent turnover, no minimal reproduction, no strong self-reproduction, no heredity, no
multigeneration, no living status, no architecture necessity.

## What is authorised next

Nothing. A second clean restart is forbidden, a second targeted measurement campaign is forbidden,
and this disposition authorises no successor. Any further experiment requires an explicit human
decision.
