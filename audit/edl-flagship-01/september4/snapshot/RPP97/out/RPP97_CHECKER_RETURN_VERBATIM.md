# RPP97 — retour du checker adverse, VERBATIM

Retour intégral et non modifié du checker adverse lancé sur `RPP97/out/RPP97_RESULT.json` le
2026-08-29. Écrit et commité AVANT toute action, conformément à la règle. Rien n'y a été coupé,
résumé, reformulé ni corrigé. Ce qui suit la ligne de séparation est le texte tel qu'il a été rendu.

---

# ADVERSARIAL CHECK — RPP97_RESULT.json

**Checker scope:** read-only. Nothing in `/home/claude/edl` was modified; all scratch work in `/tmp/rpp97chk`. Recomputation was done independently against the 123 raw archives in `/home/claude/TBRT02_raw`, importing RPP97's own `rpp97_stats.py` where I wanted to test *their* statistic and hand-written code where I wanted to test the statistic itself.

---

## VERDICT

Every headline number in `RPP97_RESULT.json` reproduces exactly — 73434, 324, 73110, 0.99559, median 1, largest 4, 3 of 123, 123/123, 39/42, and all twelve FAR/PRE moments to the last decimal — and rerunning the committed `rpp97_measure.py` reproduces both work shards byte-for-byte. The arithmetic is clean. The science is not. Three defects are load-bearing and none of them is the one the mission self-reported. **First**, X is not the substrate: under the frozen kinetics (`kinetics.py:113-133`) X is never consumed — SX and SY are the feed species and X is autocatalytically *produced* wherever `nX·nY` is large, so S1 and S2 measure the Gray-Scott *autocatalyst*, not the depletable feed, and the parent mission's own bequest had named "the per-step component and **free-capacity** series" as the right instrument. **Second**, the "rise from FAR to PRE in 39/42" is a calendar artefact: a leave-one-world-out predictor that knows only the absolute step numbers of the two windows reproduces an *increase of +0.475* against the observed +0.375, and the scale-free enrichment ratio `16·k_xd/nX_total` **falls** from FAR to PRE in **14 of 14** worlds (14.90 → 6.44); the file's stated defence — "nX_total RISES, so the falling-denominator artefact is unavailable" — names the precise quantity that manufactures the effect, because S2 is an unnormalised density difference that scales linearly with `nX_total`. **Third**, the "precondition does not hold" claim is asserted at world scope but established only inside two windows that the frozen trigger's own definition (`t_m` = the 250th consecutive step at exactly two components) forces into the only epoch of the 11000-step horizon in which no extended body exists: in the same archives the largest component reaches ≥5 cells at median t=1183, ≥100 cells at median t=3606, and a median maximum of **248 cells** (max 303) — and where I *can* compute a core/rim contrast on those large bodies, S1 is null on X, on SY, on free capacity and on nY alike (median −0.005, 48.9% positive, n=2877 across 39 worlds). So the fair reading is not "the precondition does not hold" and not "the mechanism is refuted" but "the mechanism is absent where it is testable, and RPP97 did not look there." Two further material items: the file computed 324 S1 values whose median under its own code is **−0.500** with 60.2% negative — the refuting sign, and one of the statement's own §5 incompatibility conditions — and reported only the count; and `rpp97_stats.centroid_frozen` uses integer floor division (`soy // m`) where the frozen centroid is a true mean, so the statement's claim of bit-identity is false (6.1% of window component-steps affected, 64.6% over the horizon, 38% of S1 values change). The post-hoc disclaimer in §0 is honest and prominent, and the self-reported empty between-arm control is correct and verified. It does not cover these.

---

## FINDINGS

### 1. X is not the substrate. The whole mechanism translation is mis-specified.
**Severity: MATERIAL. LOAD-BEARING — claim 2 collapses; claim 1's framing collapses with it.**

`RPP97_STATEMENT.md` §2 asserts: *"**X joue le rôle du substrat.** Ce n'est pas une analogie choisie: la naissance de Y est autocatalytique et sa propension locale gelée vaut `kY · nX · nY` par cellule."*

The frozen kinetics say otherwise. `/home/claude/ORR01/code/kinetics.py:113-133` (verbatim in `/home/claude/edl/OBTC02/code/engine_obtc.py:158-174`):

```
pair = nX * nY ; free0 = max(free, 0)
for prod, res, kk in (("X","SX",kX), ("Y","SY",kY)):
    p     = min(1.0, kk*pair)
    cand  = min(n[res], free0)
    births= binomial(cand, p)
    n[res] -= births ;  n[prod] += births
```

- X is **never** on the left of a reaction. Neither `_react` nor anything else consumes X except decay (`muX = 0.04`) and hopping.
- The species that are consumed — the fed reservoirs replenished toward `S0` at rate `phi` — are **SX and SY** (`lawspec_v2.py:131-146`, `kinetics.py:141-148`).
- X is **autocatalytic**: `SX → X` at probability `min(1, kX·nX·nY)` with `kX = 1.0`. X is produced fastest exactly where the mechanism predicts it should be depleted.
- The propensity quoted in §2 is incomplete. Expected Y births per cell per step = `min(nSY, free) × min(1, kY·nX·nY)`. The omitted factor `min(nSY, free)` **is** the substrate/capacity term — the one that carries depletion. Dropping it is what licenses the substitution of X for SX/SY.

`/home/claude/edl/TBRT02/out/TBRT02_C5_CLOSURE.json`, item `6_WHAT_A_SUCCESSOR_COULD_DO...[1]`, says the comparison is *"measurable on the per-step component and **free-capacity** series already archived."* RPP97 substituted X and does not mention the departure.

The correct fields were present and unused: `c_nSY` and `c_free` per Y-occupied cell, `s[:,3]`/`s[:,4]` for `nSY_total`/`nSX_total` (`tlmr01_world.py:53-55, 73-75, 90-91`). I computed the rim−core contrast on all of them (below, Finding 4): all null.

Consequence: "S2 runs opposite to the prediction" is not a surprising anti-mechanism observation. It is the expected sign for a locally-produced autocatalyst with decay length `ell_X = sqrt(D_X/muX) = 2.5` sitting inside a disc of radius 5.

### 2. The FAR→PRE rise is absolute time, and the file's own defence is the cause.
**Severity: MATERIAL. LOAD-BEARING — this is the entirety of claim 2's temporal evidence.**

`RPP97_RESULT.json` §2 reports `paired_change_FAR_to_PRE: {n:42, median:0.387924, archives_where_it_increases:39}` and defends it under `THE_TRIVIAL_EXPLANATION_THAT_IS_NOT_AVAILABLE`: *"a global collapse of X would inflate S2 mechanically. It did not happen: nX_total RISES."*

S2 is a difference of densities, not a ratio. Writing `C = (k_xd/81)/(nX_total/1296) = 16·k_xd/nX_total` (the scale-free enrichment ratio; the disc is exactly 1/16 of the lattice):

**S2 = (nX_total/1296)·(C − 1)**

With `C > 1` fixed, S2 rises *linearly* in `nX_total`. The rise in `nX_total` is therefore not the reason the artefact is unavailable — it is the artefact.

Measured across the 14 independent worlds that have any FAR data at all:

| | FAR | PRE | change |
|---|---|---|---|
| `nX_total` (median) | 36.2 | 200.5 | **+161.2, rises in 14/14** |
| `C` = enrichment ratio (median) | **14.90** | **6.44** | **−8.21, falls in 14/14** |
| `S2` (median) | 0.374 | 0.812 | +0.388, rises in 13/14 |

On the scale-free measure the neighbourhood becomes **relatively poorer** in X from FAR to PRE, unanimously — the opposite direction to the headline. In several worlds `C_FAR = 16.000` exactly, i.e. *every* X molecule in the world is inside the disc.

Leave-one-world-out confound test (`/tmp/rpp97chk/confound.py`): for each of the 14 worlds I pooled the *other 40* worlds' S2 at the *same absolute steps* as that world's FAR and PRE windows, using nothing about the world itself.

- observed FAR→PRE increase: n=14, median **+0.388**, mean +0.375, positive **13/14**
- time-only prediction: n=14, median **+0.482**, mean +0.475, positive **14/14**
- residual (observed − time-only): median **−0.126**, positive **3/14**

The time-only predictor *over*-explains the rise. After removing absolute time, the world-specific component runs the other way in 11 of 14 worlds — mildly *toward* the mechanism's prediction. The S2 vs absolute-t curve is universal: median +0.555 at t∈[0,250), rising to +0.979 at t≈1250, then falling to ≈0 by t=4000. Both windows sit on the rising limb of that curve.

Within PRE there is no rise toward `t_m` either: 25-step bins run 0.890, 0.801, 0.766, 0.747, 0.760, 0.757, 0.768, 0.763, 0.776, 0.796 — flat with a slight *fall* at the start.

And the sign carries no information at all: **S2 > 0 in 41/41 worlds at t = 0**, at the seeded initial condition, before a single reaction has been recorded (median +0.081; the single organiser cell carries the seed X, so `k_xd = nX_total`). "Positive in 123/123 in PRE" is a property of the initial condition of every world, not of the approach to anything.

### 3. The FAR window is truncated in 41/41 triples, empty in 27, and is the startup transient — not a temporal control.
**Severity: MATERIAL. LOAD-BEARING for the paired comparison. This is a design defect the mission did not find.**

`t_m` across the 41 triples: min **370**, median **713**, max **1673**. **No triple has `t_m ≥ 2000`.** The nominal FAR window `[t_m−2000, t_m−1000]` therefore extends before t=0 in **41 of 41** cases.

- 27 triples (81 archives) have `t_m < 1000` → FAR is **entirely empty**. `RPP97_RESULT.json` reports `FAR n=14` against `PRE n=41` with **no explanation anywhere in the file**.
- For the 14 remaining triples, the surviving FAR window is exactly `[0, t_m−1000]`, i.e. **7, 24, 42, 61, 74, 109, 109, 240, 248, 553, 569, 628, 642, 674** steps out of a nominal 1001. It **always begins at t = 0**.
- `nX_total` at t=0 is 4–8 in every world. The reported `FAR min = 0.092593` is exactly `8/81 − 8/1296` — one archive's initial condition with all eight X molecules in the disc.
- Component-count composition inside the windows, pooled over the 41 triples: **FAR = 3941 steps at 1 component, 39 at 2**; **PRE = 41 steps at 1 component, 10209 at 2**.

So the comparison labelled "far from division vs just before division" is in fact "the single-organiser startup transient at t≈0, of wildly varying length, vs a 250-step window in which the world has exactly two components by construction." The 14 FAR windows are not comparable to each other, let alone to PRE.

### 4. "The precondition does not hold" is stated at a scope the evidence cannot reach; the same archives grow 248-cell bodies, and where the contrast is computable it is null.
**Severity: MATERIAL. LOAD-BEARING for claim 1's stated reading (not for its arithmetic).**

`RPP97_RESULT.json` §1 READING: *"the bodies that divide in these worlds are one to four cells across … at the scale where division happens in these worlds there is no interior to starve."* §4: *"the division events in these worlds are not the division of an extended spot with a depleted core."*

The window arithmetic is right. The scope is not. Over the whole horizon, in the *same* 123 archives:

| quantity | min | median | max |
|---|---|---|---|
| max component `ncells` ever, per archive | 2 | **248** | **303** |
| max component `ncells`, t ≥ 10000 (n=104) | 207 | 245 | 289 |
| **median** component `ncells`, t ≥ 10000 | 194 | 225 | 268 |
| max `ncells` inside the PRE window | 2 | 2 | 4 |
| max `ncells` inside the FAR window (n=42) | 1 | 1 | 3 |

104 of 123 archives reach ≥100 cells. First step at which the largest component reaches N cells, median over the 39 SHAM worlds that grow at all: **≥5 at t=1183, ≥10 at t=1809, ≥25 at t=2398, ≥50 at t=2787, ≥100 at t=3606, ≥200 at t=5877.** Median `t_m` is 713; the last RPP97 window closes at `t_m−1 ≤ 1672`. **Both windows close, in every world, before any extended body exists.**

Why: `t_m` is not a size event. `fmrt01_endpoint.py:22-27, 46` + `fmrct01_track.py:89-95` define `t_m` as the 250th consecutive step of a maximal run in which `state_of` returns "S", i.e. **exactly two components** and `nY ≥ 2`, with an X-mass balance gate. So `PRE = [t_m−250, t_m−1] = [run_start−1, run_start+248]` **is the maturation run itself**. The trigger selects the window; the window's component count is the selection criterion, not an observation. This is confirmed exactly by the deterministic per-archive count in `work/rpp97_*.log`: `S1small = 499 = 1×1 + 249×2` for every archive with an empty FAR window, and `499 × 123 = 61377 = 83.6%` of the reported 73434.

At `t_m` the *entire world* holds 2–5 Y molecules. In **23 of 41** worlds it is two single molecules on two single cells; the full distribution of the `(ncells, ncells)` pair at `t_m` is `(1,1)×23, (1,2)×12, (2,2)×2, (2,3)×2, (1,3)×1, (1,4)×1`.

**And where the contrast can be computed, it is null.** I recomputed the rim−core split on the 39 worlds that grow, on a 100-step grid, using the *correct* frozen centroid, restricted to components of ≥100 cells (n = 2877 component-steps):

| field | median S1 | mean | fraction > 0 |
|---|---|---|---|
| X (RPP97's species) | −0.0052 | −0.0014 | 0.489 |
| SY (the actual feed) | +0.0008 | +0.0017 | 0.509 |
| free capacity | −0.0018 | −0.0022 | 0.497 |
| nY (body mass) | +0.0000 | +0.0012 | 0.496 |

No core/rim structure on any field. S2 on those same large bodies drops to median **+0.070** (58.5% positive) from +0.81 in PRE — the enrichment is a point-source halo effect, not a body effect.

**A caveat that partly rescues the conclusion but not the argument.** I measured compactness of the largest component at every 50th step in all 39 worlds: `compactness = r_equiv/(r_gyr·√2)`, where 1.0 = a uniformly filled disc. The maximum *ever* attained, per world: min 0.420, median 0.435, max 0.556; **zero worlds ever reach 0.7.** A 250-cell component has `r_gyr ≈ 14` where a filled disc of that mass would have `6.3`, with `r_max ≈ 24.8` against a torus maximum of 25.46 and 17% lattice coverage. The late "bodies" are percolating clouds spanning the whole torus, not spots. So there is indeed no extended spot with an interior anywhere in these worlds — **but RPP97 neither measured nor claimed that.** It offered cell count as the evidence, and cell count stops supporting the claim after t≈1200. The right conclusion was available and was not reached.

`RPP97_RESULT.json` §5 lists four things a real test would need. None of them is "look after `t_m`, where the bodies are 200× larger." Item 2 asks for a post-`t_m` window motivated only by the arm contrast; item 4 asks for a precondition check but writes it as though the answer were settled.

### 5. 324 S1 values were computed, run negative, and are not reported.
**Severity: MATERIAL. LOAD-BEARING for the READING sentence in §1.**

`RPP97_RESULT.json` reports `S1_defined: 324` and then: *"This is NOT evidence against the core-depletion mechanism."* It reports no S1 value, no median, no sign count.

All 324 come from one independent world (index 507, `t_m = 1552`), 108 per arm, all inside PRE. Under RPP97's own code:

- **median −0.500, mean −0.582, min −5.667, max +3.500; negative in 195/324 (60.2%), zero in 24, positive in 105.**

`RPP97_STATEMENT.md` §5 lists *"S1 ≤ 0 de façon soutenue en fenêtre PRE"* as one of the four things that **would count as incompatible with the mechanism**. It is met, in PRE, in the only world where it can be evaluated. The capability test (`RPP97_CAPABILITY.json`) exists precisely to prove S1 can express that sign. The measurement obtained it and the result file does not say so.

Fairness requires the other half: with the centroid corrected (Finding 6) the same 327 values give **median 0.000, mean −0.246, negative 47.7%** — null rather than refuting. Either way, n = 1 world of 4-cell objects and the value should have been printed with that caveat, not suppressed behind a count.

### 6. The centroid is floored, not averaged. The statement's bit-identity claim is false.
**Severity: MATERIAL. NOT load-bearing for the published numbers.**

`/home/claude/edl/RPP97/code/rpp97_stats.py:27-29`:
```python
def centroid_frozen(a0y, a0x, soy, sox, m):
    """The frozen centroid expression in the frozen order: (a0 + sum(offsets)//m) % L."""
    return ((a0y + soy // m) % L, (a0x + sox // m) % L)
```
The frozen centroid (`fdot01_centres.py:58-62`, `fmrt01_identity.py:30-34`) is `(a0 + sum(oy)/len(oy)) % L` — **true division**. `//` floors toward −∞; for `soy = −1, m = 3` the frozen value is `a0 − 0.333` and RPP97's is `a0 − 1`, a full cell.

`RPP97_STATEMENT.md` §3: *"le centroïde est recalculé par l'expression gelée … dans le même ordre, donc **bit-identique** à la valeur en ligne."* False. `tlmr01_world.py:56-59` explains that `(a0, soy, sox)` are stored precisely *so that* an offline reader can reproduce the float expression; RPP97 defeats that.

Measured: `soy // m ≠ soy / m` in **1495 of 24478** window component-steps (**6.1%**) and **460912 of 713163** over the whole horizon (**64.6%**). Effect on the statistic: **38.1%** of evaluable S1 values change; `S1_defined` moves 324 → **327**; `fraction_undefined` 0.99559 → 0.99555; the pooled S1 median moves −0.500 → 0.000. S2 is unaffected (`k_xd` was computed online at the true rounded centroid).

### 7. Threefold pseudo-replication in every reported n.
**Severity: MATERIAL. NOT load-bearing for the direction, load-bearing for any claim of weight.**

The three arms share a common prefix and both windows lie inside it (the mission's own §3, which I confirm: the `s` rows first differ at exactly `t_m + 1` in every archive I checked). So every per-archive number is identical across arms — verified: **41 of 41 triples give bit-identical FAR and PRE S2 medians across SHAM/SELECTIVE/DISPLACED.** Yet §2 still reports:

- `archives_with_S2_above_zero_in_PRE: 123 of 123` → really **41 of 41** worlds
- `archives_where_it_increases: 39 of 42` → really **13 of 14** worlds
- `component_steps_observed_in_the_windows: 73434` → **3 × 24478**

The file diagnoses the cause in §3 and then leaves the inflated denominators standing in §2 as headline evidence. There is a second inflation inside PRE: S2 is appended once **per component**, and PRE has exactly two components at 10209 of 10250 steps, so each step contributes two same-step, same-denominator values (centroid separation median 10.0 cells; the two 81-cell discs overlap at 51% of steps, median overlap 1 cell). Effective independent n for the PRE aggregate is **41 worlds**; for FAR, **14**.

### 8. The statement's fourth incompatibility condition was never evaluated — and it fires.
**Severity: MATERIAL. Under-claim.**

`RPP97_STATEMENT.md` §5 lists as incompatible: *"le contraste maximal survenant **après** t_m plutôt qu'avant."* `rpp97_measure.py:19-20, 35, 51` reads only `[t_m−2000, t_m−1]`; nothing at or after `t_m` is ever loaded. The condition is not evaluated and the result file does not say it went unevaluated.

I evaluated it. S2 binned by `t − t_m` over the 41 SHAM worlds:

```
 -750 +0.727 | -500 +0.905 | -250 +0.783 |    0 +0.862
 +250 +0.993 | +500 +0.999 | +750 +1.050 | +1000 +0.933
+1250 +0.724 | +1500 +0.597 | +1750 +0.426 | +2000 +0.212
```

The maximum contrast occurs at **t − t_m ≈ +750 to +1000**, not before `t_m`. By the file's own pre-declared criterion this is an incompatible observation, and it is absent from the result.

### 9. The aggregation code is not committed. The headline file cannot be regenerated from the repository.
**Severity: MATERIAL for reproducibility. NOT load-bearing.**

`git ls-files RPP97` returns six files plus two work shards and two logs. `rpp97_measure.py` produces `work/RPP97_{0,1}.json` (per archive) and stops. **No script anywhere in `/home/claude/edl` produces `RPP97_RESULT.json`** — I grepped for every headline constant and every field name. The by-arm/by-window table, the 123/123 and 39/42 counts, `median_size_when_undefined` and `largest_component_ever_seen_in_the_windows` were produced by uncommitted ad-hoc code. Note also that `median_size_when_undefined: 1` is *not* derivable from the committed work files (they carry only per-archive min/med/max); it happens to be correct because every per-archive median is 1, but a median-of-medians is not a pooled median in general. In a programme whose bequest is "operationalise in code before the first world," an uncommitted aggregation step is not a footnote.

Mitigating: `RPP97_CONTENT_HASH` **verifies** under the repository's canonical rule (`omldct02_hashes.content_digest`, excluding `GENERATED_UTC` and the hash field itself), and rerunning `rpp97_measure.py` reproduces both committed shards exactly.

### 10. The cited nX_total numbers contradict the sentence they support, and are a sample of one.
**Severity: MINOR.**

§2: *"nX_total RISES over these windows (7 at t=0, 272 at t_m−250, **252** at t_m−1 in the archive checked)."* The three quoted numbers reproduce (index 85), but 272 → 252 is a **fall** across the PRE window, not a rise. Across the 41 independent worlds `nX_total` rises over PRE in 38 and falls in 3 (median +69), so the sentence is defensible in general — but it is supported by one archive whose own numbers contradict it.

### 11. §2 misdescribes what `c_cand` is.
**Severity: MINOR.**

*"sa propension locale gelée vaut `kY · nX · nY` par cellule, archivée **telle quelle** dans `c_cand`."* `tlmr01_world.py:75` stores `int(round(1e6 * min(1.0, kY·nX·nY)))` — a capped, ×10⁶-scaled, rounded **probability**, verified exactly on 200k rows. Not "telle quelle", and — the substantive part — not the propensity for the number of births, which is `Binomial(min(nSY, free), p)`. The dropped `min(nSY, free)` factor is Finding 1's root.

### 12. "Bodies that divide" / "division events" is an unlicensed characterisation.
**Severity: MINOR, but it is exactly the class of language the programme forbids.**

`RPP97_RESULT.json` sets `REPRODUCTION_STATUS: NOT_TESTED`, `HEREDITY_STATUS: NOT_TESTED` and `NOTHING_HERE_SAYS_ANYTHING_ABOUT_WHAT_THESE_OBJECTS_ARE: true`, and in the same file writes *"the bodies that divide in these worlds"* and *"the division events in these worlds"*. What `t_m` actually marks is: the world has held exactly two single-linkage components (linkage radius 5) for 250 consecutive steps, with a local-X mass ratio ≥ 1−1/e. In 23 of 41 worlds that is two lone Y molecules on two lone cells; in all 41 the world's total Y at `t_m` is between 2 and 5. Nothing establishes that anything divided rather than that two molecules diffused more than five cells apart. The statement's framing (Gray-Scott *spot replication*) imports morphology the data does not carry. `NO_QUANTITATIVE_COMPARISON_TO_PUBLISHED_GRAY_SCOTT_PROFILES_WAS_ATTEMPTED: true` guards the numbers; nothing guards the nouns.

### 13. The named alternative is the weaker of the two available, and the stronger one is not named.
**Severity: MINOR. Under-claim.**

§2 names co-location: *"bodies sit where X is abundant … rather than making them rich."* The kinetics supply a stronger and different alternative: the body **makes** X where it sits — `SX → X` at `p = min(1, kX·nX·nY)` with `kX = 1.0`, decay length `ell_X = 2.5` inside a disc of radius 5. That is production, not co-location, and it predicts S2 > 0 deterministically. It is not named. Its signature is visible: S2 > 0 in 41/41 worlds at t=0 with `C = 16` (all X in the disc), and S2 collapsing to +0.07 once the body stops being a point.

### 14. The remedy §5 prescribes is not computable from this raw at all.
**Severity: MINOR. Under-statement.**

§2 says control discs "would be post-hoc on top of post-hoc"; §5 lists them as a requirement. Stronger: they are **impossible** from these archives. `c_nX` exists only on Y-occupied cells; the only off-support reading is `k_xd` at component centroids; `xbirth` records X births but there is no X-death and no X-hop ledger, and `p_hop_X = 1.0`, so the X field is not reconstructible at any other location. Separating production from co-location requires **new worlds**, not a further analysis of this raw. §5's third bullet should say so.

### 15. Aggregation labels and the unexamined gap.
**Severity: COSMETIC.**

`by_arm_and_window[...]["mean"]` is the **mean of per-archive medians**, not the mean of S2 values; unlabelled. And `rpp97_measure.py:35-36` loads the full span `[t_m−2000, t_m−1]` — including the 750-step gap `[t_m−1000, t_m−250]` — then discards it at line 51 without comment. That gap is the only stretch of the pre-`t_m` trajectory that is neither the startup transient nor the trigger's own selection window; it is the one window in the design that was not selected by construction, and it is thrown away.

---

## CHECKED AND FOUND SOUND

1. **Every headline number reproduces exactly**, recomputed independently over all 123 archives (`/tmp/rpp97chk/recompute.py`): `component_steps = 73434`; `S1_defined = 324`; `S1_undefined = 73110`; `fraction_undefined = 0.99559`; `median_size_when_undefined = 1`; `largest_component_ever_seen_in_the_windows = 4`; `archives_where_S1_could_be_computed = 3 of 123`; all twelve FAR/PRE moments to six decimals in all three arms; `123/123`; `n=42, median 0.387924, mean 0.375083, increases 39`. Nothing failed to reproduce.
2. **Rerunning the committed `rpp97_measure.py`** on both shards produces output `==` the committed `work/RPP97_{0,1}.json`. The measurement is deterministic and the work files are genuine.
3. **Shard coverage**: 62 + 61 = 123 archives, 123 unique tags, no duplicates, no omissions.
4. **`RPP97_CONTENT_HASH` verifies** under `omldct02_hashes.content_digest(doc, extra_excluded=("RPP97_CONTENT_HASH",))`.
5. **The 4-cell threshold does not manufacture the conclusion.** Window size histogram: `{1: 65142, 2: 6687, 3: 1266, 4: 339}`, nothing above 4. Threshold sensitivity: 2 → 8.29% defined; 3 → 1.59%; **4 → 0.44%**; 5 → 0.00%; 8 → 0.00%; 12 → 0.00%. Lowering to 3 leaves 98.4% undefined. This attack fails.
6. **The disc-in-ambient contamination cannot flip the sign and is conservative.** Algebraically exact for all `(k_xd, nX_total)` (verified on 2000 random pairs): `S2_excl = xd/81 − (N−xd)/1215 = (1296/1215)·S2_RPP97`. It is a pure positive scale factor of 1.06667 — the RPP97 form *understates* the positive contrast by 6.25%, i.e. biases toward the mechanism's prediction. Recomputed with the disc excluded: PRE median 0.866 (vs 0.812), positive 41/41; FAR median 0.399, positive 14/14; paired increase 13/14. **The sign survives.**
7. **The self-reported design defect is real and correctly diagnosed.** All three arms give bit-identical FAR and PRE medians in 41 of 41 triples, and the `s` rows first diverge at exactly `t_m + 1`. Both windows lie strictly inside the shared prefix. Confirmed.
8. **The capability test is genuine and does what it claims.** `rpp97_capability.py` runs before any archive is opened, exercises S1 on core-depleted / core-enriched / uniform synthetic discs at three radii, and the refuting negative is obtained at every radius (−66.67, −58.47, −52.89) with exact zeros on uniform bodies; S2 is shown two-signed. `DISC_AREA = 81` is read from `fmrt01_identity.disc_mask`, never assumed, and 81/1296 = 1/16 exactly. `MEASUREMENT_MAY_PROCEED` is asserted at `rpp97_measure.py:102`.
9. **`WORLDS_LAUNCHED: 0` and `ARCHIVES_READ: 123` are true.** No engine is instantiated anywhere in the RPP97 code.
10. **The §0 post-hoc disclaimer** is placed first, in both the statement and the result's `STATUS`/`WHY`, and is not walked back anywhere. `STATUS: POST_HOC__CANNOT_ADJUDICATE` is the correct status.
11. **The §7 limit is accurate**: `c_nX` exists only on Y-occupied cells (confirmed against the archive schema `cells_semantics`), so no radial profile outside the body is reconstructible, and no quantitative Gray-Scott comparison was attempted.
12. **`S1_defined + S1_undefined == component_steps_seen`** exactly (73434 = 324 + 73110) in my independent pass — no component-step is silently dropped by the `bycell.get((t,k))` lookup.
13. **All frozen-primitive imports are byte-unchanged** and the `L`/`CORE_R` cross-check between `fdot01_centres` (PQEC01 freeze) and `fmrt01_identity` (OBTC02 YAML) is asserted at `rpp97_stats.py:18-19`, not assumed.
14. **No `s`-row is missing** for any step inside either window in any archive checked.
15. **No lineage/heredity/reproduction/life *status* is asserted.** Every status field carries forward unchanged (`H3_STATUS`, `REPRODUCTION_STATUS`, `HEREDITY_STATUS`, `AUTONOMOUS_COHESION_STATUS`, `X_LAWSPEC_BASELINE`, `ARCHITECTURE_CHANGE_NECESSITY`, `COMPANION_PAPER_V1_1_STATUS`, `OMLDCT02_STATUS`, `CLEA01_STATUS`, `TBRT02_STATUS`) and matches the values in `TBRT02_C5_CLOSURE.json`. The objection in Finding 12 is to prose, not to a status field.

---

## WHAT I DID NOT CHECK

1. **The sha256 seals of the 123 raw archives.** I read `/home/claude/TBRT02_raw/*.npz` as given and did not verify them against `TBRT02/work/TBRT02_SEALED_LEDGER_*.jsonl`. If the raw is not what TBRT02 sealed, every number here and in RPP97 is void.
2. **The `ADMISSIBLE` selection** in the sealed ledger. I confirmed 41 triples × 3 arms = 123 files exist and are consistent, but did not audit which seeds were admitted or why, nor the `TBRT02_FORBIDDEN_SEEDS` list.
3. **The correctness of the archives as a record of the simulation.** I did not re-run any world and did not verify that `k_xd`, `c_nX`, `c_nSY`, `c_free` or `s` faithfully reflect the engine state. I verified `c_cand` internally against `round(1e6·min(1, kY·nX·nY))` on 200k rows and nothing else.
4. **The historical claim in §0** — that a real preregistration existed at commit `ae9c9cb` and a capability test at `4978c12` before the rollback. Those commits are not in this repository's history and I made no attempt to recover them. §0's account is taken at face value; if it is wrong, it is wrong in the direction of *understating* the mission's standing, not overstating it.
5. **The `TBRT02` claim that "at t=11000 a world carries ~266 Y cells."** I could not locate that sentence anywhere in the repository (grepped `TBRT02/out`, all `*.md`/`*.json`). What I measured at the final recorded step across the 123 archives: `n_y_cells` min 0, median **224**, mean 192, max 271; `nY_total` median **246**; `n_components` median 1. So ~266 is above the median but inside the range. I could not check the claim as attributed because I could not find it.
6. **Whether Reynolds, Ponce-Dawson & Pearson (1997) is characterised correctly.** No literature access. I took the mechanism description in §1 as given and tested only its translation into these variables.
7. **The nineteen archives whose Y goes extinct** (`ncells_max_all < 10`: SELECTIVE 12, DISPLACED 5, SHAM 2). I noted the arm asymmetry — the parent removal kills the world in 12 of 41 SELECTIVE arms — but did not pursue it. It is a further reason a post-`t_m` window would have produced a real arm contrast.
8. **Statistical significance of anything.** I report medians, means and sign counts. No test, no interval, no correction. The FAR-window observations are autocorrelated within worlds and the PRE observations doubly so (two components per step); I did not model that beyond reducing to per-world summaries.
9. **The other frozen modules in the import chain** — `pqec01_observer`, `fdot01_world`, `fmrct01_world`, `mrci01_descent`, `fdflt01_endpoint` beyond the maturation state machine — were read only as far as needed to establish what `t_m` is and what the kinetics do.
10. **Compactness before t≈1000.** My compactness scan required ≥8 cells, which no window component reaches, so the "no compact spot ever" statement in Finding 4 is established for t ≳ 1200 and is trivially true (by cell count) before that.
