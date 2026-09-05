# TBRT02 — retour du checker adverse, VERBATIM

Ce fichier est le retour intégral et non modifié du checker adverse lancé sur C4
(`TBRT02/out/TBRT02_C4_ANALYSIS.json`) le 2026-08-28. Il est écrit et commité AVANT toute
action, conformément à la règle : le retour d'un checker s'enregistre avant d'être exploité.
Rien n'y a été coupé, résumé, reformulé ni corrigé. Ce qui suit la ligne de séparation est le
texte tel qu'il a été rendu.

---

I have completed the audit. Here is the standalone report.

---

# ADVERSARIAL CHECK — TBRT02/out/TBRT02_C4_ANALYSIS.json

**Checker:** independent adversarial review. Read-only; nothing in `/home/claude/edl` was modified, no commit was made, all scratch work was done under `/tmp`.

## VERDICT

The central claim survives in substance but not in its stated generality, and its stated justification is the weaker of the two available. The induction in §7 is **valid** — I could not break it, and I strengthened it: the same argument extends to the mass level (R3), which the file records only as "not computable", so no re-run with a tagged-mass tracker could rescue the frozen condition either. Every number in the file reproduces exactly against an independent from-scratch re-implementation and against the raw archives; the content hash, the parent hashes, the methods hash and the sampled archive digests all verify; the mass-conservation audit of variant B is correct and genuinely parameter-free; the capability search is fair and is in fact *stronger* than the file claims. **But** the answer to the question the task called most important is yes: a fourth reading exists that keeps `CERTAIN` as the subject, is computable from these archives using the programme's *own frozen component rule* with no free parameter, is **not** vacuous, and **fires in 17 of 41 triples**. Its existence falsifies the headline phrase "the only reading its own words support" and makes §7's unqualified "the frozen refutation condition is VACUOUS" an overstatement — it is the *strict cell-membership* reading that is vacuous. This does **not** overturn the decision to withhold the sequential bound; it makes that decision more clearly correct, for a better reason than the one given: the statistic was never defined before the raw, and two defensible post-raw readings of the same frozen sentence disagree about whether the event occurred (0/41 vs 17/41). Secondary defects: the file's own data contradict one of its stated root causes, right-censoring is nowhere disclosed, and the competitor-viability block is an upper bound reported as a measurement.

---

## FINDINGS

### F1 — A defensible, non-vacuous reading of the frozen words exists, is computable from these archives, and fires in 17/41
**Severity: MATERIAL. LOAD-BEARING** for the wording of the central claim (the claim must be narrowed to R1); **not** load-bearing for the decision to withhold the bound.

The file declares the "DESC_definition" as the ANY-source closure and then proves that *any* set transported by one-step adjacency cannot enter `CERTAIN`. That proof is correct. But it forecloses only readings in which the absorbed object is a **cell** or a **quantum**. It does not touch the reading in which the absorbed object is a **body**.

This programme already has a frozen definition of a body. `FDOT01/code/fdot01_centres.py:38-56` defines `components()` as toroidal single-linkage over Y-occupied cells at Euclidean radius `CORE_R = 5.0`; `TLMR01/code/tlmr01_world.py:71-76` writes the resulting component id into `c_cid`, one value per Y-occupied cell per step, in every archive. So the reading

> **R5** — ∃t : some cell of `CERTAIN(daughter)(t)` and some cell of `DESC(competitor)(t)` carry the **same `c_cid`** at step t (they are the same organiser body)

is computable directly from the archives, uses only frozen primitives, and has no free parameter. It is at least as faithful to the freeze as R1: the freeze's own gloss (`TBRT02_MASTER_FREEZE.json`, `THE_QUESTION`) reads "in the presence of a matched competing Y source **it could wrongly absorb**" — where "it" is *an organisation issued from the daughter*, i.e. a body, not a set. "Absorb" is a body-level verb there.

I computed R5 on all 41 DISPLACED archives (`/tmp/.../r5.py`, independent code):

| reading | fires | first firing, steps after t_m (min / median / max) |
|---|---|---|
| R1 strict `CERTAIN ∩ DESC` | **0 / 41** | — |
| **R5 same frozen component (`c_cid`)** | **17 / 41** | **383 / 1076 / 1745** |
| R5′ `CERTAIN` Moore-1 adjacent to `DESC` | 17 / 41 | 562 / 1252 / 2371 |
| R2 `POSSIBLE ∩ DESC` (reported) | 17 / 41 | 562 / 1252 / 1983 |

R5 fires **strictly earlier than R2 in all 17 worlds**, and selects exactly the same world set (indices 94, 279, 312, 321, 365, 391, 415, 491, 511, 545, 566, 573, 593, 595, 636, 724, 827 — identical to the repo's `R2_FIRED` set, which I also reproduced).

Consequence: under R5, the frozen rule "one absorption suffices" fires, and Model C would be **REFUTED**. I am **not** asserting R5 is the correct reading — R1 is the more literal rendering of "the set absorbs" — I am asserting that R1 is *not* "the only reading its own words support", which is what `THE_HEADLINE` and `tbrt02_c4_close.py:72-75` claim, and that §7's `CONCLUSION` (`tbrt02_c4_close.py:150-154`) must be qualified to "the strict cell-membership reading is vacuous". The reading that makes the test empty was selected from a menu that did not include the body-level reading, and the body-level reading is the one the freeze's own question phrases.

*Fairness note:* R5 was computed by me **after** the numbers were known. It carries no pre-registration and cannot be used to declare a refutation. That cuts both ways — see F2.

---

### F2 — The stated reason for withholding the sequential bound is reading-dependent; the robust reason is different and stronger
**Severity: MATERIAL. Not load-bearing** — the decision (withhold) is right; the argument for it is not.

§8 `WHY_IT_IS_WITHHELD` argues: "the statistic is identically zero by construction, so there is no parameter to bound." That premise is exactly the claim F1 narrows. If R1 is not the unique reading, the premise is conditional on a reading chosen after the raw.

The robust argument, which the file does not make, is a timing argument it already has the evidence for: the notes declaring R1/R2/R3 were committed at `2a78e68`, **after** the raw closed at `ec4f83b` (§2 says this plainly). So no operationalisation of the frozen sentence predates the data. Two post-raw readings of the same sentence give 0/41 and 17/41. A zero-event anytime-valid bound requires the *statistic*, not just the admissibility rule, to be fixed independently of the data; here it was not. Reporting `p_max(41) = 0.070461` would therefore be invalid even if R1 were not vacuous.

Answering the task's question 7 directly: **withholding is not an over-correction — it is under-argued.** Note also that the file does not actually suppress the number: §8 prints `0.070461` and quarantines it with an explanation. That is the right practice, and better than the word "withheld" suggests.

---

### F3 — The file's own data contradict the "root cause" it gives for variant B
**Severity: MINOR. Not load-bearing.**

§4 `root_cause` states: "the t_m row … still carries the parent's Y … **The second half affects the frozen Model C as applied here**: in SELECTIVE and DISPLACED the parent cell counts as a source at the first transition."

It does not, in any of these worlds:

- Variants A and B are **identical on every daughter-side quantity in all 123 world-arms**. Comparing `C4_LINEAGE_{0,1}.json` against `C4_LINEAGE_B_{0,1}.json` field by field: `CERTAIN_duration`, `POSSIBLE_duration`, `CERTAIN_exposure`, `POSSIBLE_exposure`, `CERTAIN_max_cells`, `CERTAIN_steps`, `POSSIBLE_steps`, `R1_rows`, `R2_rows` — **0 differences**. Only `DESC_duration`/`DESC_max_cells` (3 worlds: 85, 240, 347), `n_invariant_violations` (41 DISPLACED worlds) and `stopped_at` (2 worlds) differ.
- The mechanism cannot bite: over the 41 triples the **minimum Chebyshev distance from any parent cell to any daughter cell is 5** (min over worlds 5, max 17). A parent cell is never in the Moore-1 neighbourhood of a daughter cell, so it can never be a source of one.

Consequence for the report: §10 presents `VARIANT_A` and `VARIANT_B` as two full arm-summary blocks. They are byte-identical, necessarily. A reader takes that as independent corroboration; it is a duplicate. The honest statement is: *variant B changes nothing on the daughter side in any of the 123 world-arms; it changes only the competitor seeding, in 3 of 41 worlds.*

---

### F4 — Underclaim: R3 is not merely "not computable", it is provably vacuous — and that is the strongest support the central claim has
**Severity: MINOR (underclaim). Not load-bearing, but it closes the last escape route.**

§3 records R3 as "NOT COMPUTABLE from the archives: schema TLMR01-ARCHIVE-1 carries no hop ledger". True, but it leaves a reader believing that a re-run with instrumentation could make the frozen condition non-vacuous at the quantum level. It could not. From the frozen engine source:

- `OBTC02/code/engine_obtc.py:35` — `NEI = ((1,0),(-1,0),(1,1),(-1,1))`: exactly one +1 and one −1 sub-shift per axis per step, so a Y quantum's **net displacement per step is at most 1 in Chebyshev**.
- `OBTC02/code/engine_obtc.py:158-174` — Y birth is autocatalytic: `pair = nX*nY`, `p = min(1, kY*pair)`, so `p = 0` wherever `nY = 0`. **Y can never be born in a cell that holds no Y.** Grepping every write site of `n["Y"]` across `kinetics.py`, `engine_obtc.py`, `pqec01_observer.py`, `tlmr01_world.py`, `tbrt02_*.py` finds no other Y-creating channel besides seeding and the declared interventions.
- Therefore every Y quantum in cell d at row t+1 came from a cell in `S(d,t)` (Moore-1, Y-occupied at row t), under either genealogy convention (born-Y descends from the catalytic Y, or born-Y is new mass). If `d ∈ CERTAIN(t+1)` then `S(d,t) ⊆ CERTAIN(t)`, and by induction back to the daughter root.

Empirically confirmed: I scanned **all 123 archives over their full 11,000-step horizons** for cells appearing with no Moore-1 source. Total violations: **42**, of which **41 are the teleport itself** (one per DISPLACED archive, always exactly at t_m+1) and one archive (i0507) has 2 at t_m+1. **Zero violations anywhere else, in any arm, at any step.**

So R3 is vacuous too. Secondary precision point: the *mechanism* given for R3's non-computability is wrong. Even with a `pq_yhop` ledger, quantum identity would not be recoverable — `pq_yhop` records *counts* moved, and `pqec01_observer.py:107` shows only X is tracked (`if self.track and sname == "X": self.tracker.move(...)`). Y is an unlabelled integer field.

---

### F5 — Right-censoring is nowhere disclosed, and censoring rates differ by arm by a factor of 3.6
**Severity: MINOR→MATERIAL for §10 and §12. Not load-bearing.**

Every duration in §10 and every difference in §12 is `min(true duration, horizon − t_m)`. Computed from `C4_LINEAGE_B_*.json`, counting worlds where the set was still alive at the horizon:

| arm | CERTAIN right-censored | POSSIBLE right-censored |
|---|---|---|
| SHAM | 8 / 41 | 34 / 41 |
| SELECTIVE | **29 / 41** | 29 / 41 |
| DISPLACED | 16 / 41 | 33 / 41 |

**30 of the 41** `SELECTIVE − SHAM` paired differences and **21 of 41** `DISPLACED − SHAM` differences involve at least one censored duration. `SELECTIVE CERTAIN_duration median = 10093` is, in 29 worlds, simply "the horizon". The word "censored" appears nowhere in C4. Direction of bias is favourable — censoring is heavier in the arm with the longer durations, so the reported differences (median +7700, +875) are attenuated lower bounds — but reporting min/median/mean/max of a censored quantity as a duration, and differencing them, without saying so is a reporting defect. §12's `EXPLORATORY` label mitigates it; §10's arm summaries carry no such label.

---

### F6 — The competitor-viability block reports an upper bound as a measurement
**Severity: MINOR. Not load-bearing.**

`DESC` is a possible-descendant closure, so it certifies actual descent only while it is disjoint from `POSSIBLE(daughter)`. I proved and checked this: at t_m the entire Y population lies inside `parent_cells ∪ daughter_cells` in **41/41** worlds (2 components, total Y mass 2–5 quanta), so after the intervention the world has exactly two Y roots and `POSSIBLE ∪ DESC` = every occupied cell. Before first contact, every source of a DESC cell is itself in DESC, so DESC mass is exactly competitor-descended. **After** first contact, a DESC cell may hold daughter-descended mass.

Quantified: for the 17 contaminated worlds a median of **8,850** of the reported `DESC_duration` steps accrue **after** first contact. Truncating at first contact changes the pooled figures from the reported `median 2214 / mean 5279.8` to **`median 1023 / mean 1606.4`**. And `DESC_max_cells` is sharply bimodal — median **1** across the 24 uncontaminated worlds versus median **244** across the 17 contaminated ones; the reported pooled median of **4** conceals that in half the uncontaminated worlds the displaced quantum's descendant set never exceeded a single cell.

The specific claim `worlds_where_the_displaced_mass_left_no_descendant: 0` **is** sound: every world has DESC alive ≥ 49 steps, and first contact never occurs before step 562, so descent is certified in all 41. The word "viability" in the block label, and the pooled duration/extent figures, are not.

---

### F7 — Underclaim/framing: on its own metric the displacement performed *worse* than doing nothing
**Severity: MINOR. Not load-bearing.**

§11 frames the result as a "partial repair" of the CLEA01 degeneracy. That is true only against SELECTIVE. From the file's own numbers:

| arm | POSSIBLE ≡ CERTAIN (degenerate) | non-degenerate |
|---|---|---|
| SELECTIVE | 41 / 41 | **0 / 41** |
| DISPLACED | 24 / 41 | **17 / 41** |
| SHAM (untreated control) | 15 / 41 | **26 / 41** |

Leaving the parent in place yields a non-trivial lineage object in **26** of 41 worlds; teleporting it to the daughter's antipode yields one in **17**. The treatment moved the competing source 17–18 cells away (I measured competitor-to-daughter Chebyshev: min 17, max 18 across the 41 worlds), which is why contact is rarer. C4 reports both numbers and draws no comparison between them. The honest sentence is available and is not written: *relative to the untreated control the displacement reduced, rather than increased, the frequency of a non-degenerate lineage object.*

---

### F8 — Gap in the written proof: it cites the right constant for the wrong step
**Severity: MINOR. Not load-bearing — the proof is patchable and I patched it.**

§7's `proof` justifies base-case disjointness "at t_m … because the displacement enforces Chebyshev ≥ 2". At t_m only Chebyshev ≥ 1 is needed (the competitor cell merely must not *be* a daughter cell). The step where ≥ 2 is actually load-bearing is the one the written proof omits entirely: in **variant A**, DESC is injected **outside the recursion** at t_m+1 (`tbrt02_lineage_c4.py:119-123`, `nd |= {c for c in desc_pending if c in cur}`). The induction does not cover an injected set. The patch: `competitor_cell` has no daughter cell in its Moore-1 neighbourhood precisely because separation ≥ 2, so `S(competitor_cell, occ(t_m)) ∩ CERTAIN(t_m) = ∅`, and since a non-empty S is required (`tbrt02_lineage_c4.py:113-115`) it cannot be in `CERTAIN(t_m+1)`. With that added the proof is complete for both variants. As written it is not.

---

### F9 — Latent instrument gap: R1 and R2 are never evaluated at t = t_m itself
**Severity: COSMETIC. Not load-bearing.**

In `tbrt02_lineage_c4.py` the intersections `i1 = certain & desc` and `i2 = possible & desc` are computed at lines 126 and 132, i.e. only *after* the update at line 124. The initial state (variant B: `certain` = occupied daughter cells, `desc` = `{competitor_cell}`) is never tested. The enforced separation ≥ 2 (`tbrt02_displace.py:42, 89, 116-117`, and measured 17–18 in the data) makes this unreachable here. If the separation constraint were ever relaxed by a successor, a t_m-time firing would be silently missed.

---

### F10 — The capability search is fair, but its prose overstates one thing and understates another
**Severity: MINOR. Not load-bearing.**

Answering the task's question 3: the control is **not** structurally different in a way that invalidates it, and the search does explore the space that matters. But two corrections.

*Overstated:* §7 `reading` says "4000 synthetic worlds unconstrained by the engine's physics — **cells free to appear and vanish**". They are not free. `tbrt02_r1_capability.py:52-56` draws every cell of the next row inside the Moore-1 neighbourhood of the *current live sets*; no cell ever appears away from a live front. The code comments this honestly ("bias the draw towards the neighbourhoods of both live sets"); the C4 prose does not.

*Understated, and this matters more:* the file justifies capability only via the relaxed control's 1720 firings. That leaves open the obvious objection — "the frozen branch never fired because CERTAIN died at step 1". I instrumented the frozen branch over the same 4000 worlds (same seed, same generator):

- the daughter (`CERTAIN`) set survives a **median of 51 of 60** steps (mean 41.9), reaching a **median maximum size of 17 cells**;
- both sets are simultaneously alive on **136,895 rows**;
- the two live sets are **Moore-1 adjacent on 7,560 rows across 1,548 of the 4,000 worlds** — the search repeatedly placed `CERTAIN` in direct physical contact with `DESC`, and the intersection still never occurred.

That is far stronger evidence than the number reported, and it is not in the file. (Reproduction: running `tbrt02_r1_capability.py` verbatim reproduces `0 / 1720 / median 11` exactly.)

---

### F11 — Provenance: the analysis code that produced every number in C4 is hash-pinned nowhere
**Severity: MINOR. Not load-bearing.**

- `tbrt02_lineage_c4.py`, `tbrt02_r1_capability.py`, `tbrt02_c4_close.py` are **not** in `METHODS_FILES` and their digests appear nowhere in C4. C4 records `METHODS_HASH` (acquisition) and nothing about analysis.
- `CLEA01/code/clea01_lineage_i1.py` — the frozen Model C whose *definition* is the entire subject of the vacuity claim — is likewise not pinned in TBRT02's methods closure, and no artefact anywhere in the repo records its sha256 (`798a88e03567ba81eae82fcac06bfff596f8e6ee3e2b4d337d558b5b96518b6d`). Git covers it: one commit (`53bb912`, 2026-08-26), never touched since, verified by `git log ec4f83b..HEAD`.
- Concretely consequential: the **variant-A per-archive files were written at 04:41 by the pre-`ee7338e` build** of the enumerator — different bytes from the file now in the tree (`ee7338e` at 04:46 added the variant machinery; the A files even lack the `VARIANT` key). I verified by regeneration that the current `variant="A"` path reproduces them **exactly on 15 archives, 0 mismatches**, and inspected the diff to confirm it is purely additive on the A path. But C4 does not record this and a reader cannot check it.

---

### F12 — Inherited defect: the sequential addendum's own integrity hash does not verify
**Severity: MINOR. Not load-bearing — I recomputed the quoted value independently.**

C4 §8 sources `preregistered_value_at_n_41`, the formula, α and the validity condition from `TBRT02_SEQUENTIAL_ADDENDUM.json`. That file's `ADDENDUM_CONTENT_HASH` does **not** reproduce under `H.content_digest` — I searched every subset of its timestamp and hash fields (`DECLARED_AT_UTC`, `PARENT_FREEZE_SHA256`, `PARENT_FREEZE_CONTENT_HASH`, `ADDENDUM_CONTENT_HASH`) and none reproduces the stored value. By contrast `FREEZE_CONTENT_HASH`, `C3_CONTENT_HASH` and `C4_CONTENT_HASH` all verify. So the addendum's self-hash provides no integrity guarantee for the pre-registered readings C4 quotes. Git provenance is clean (added once at `672ccc1`, 2026-08-27 03:23, never modified). C4 cites the addendum as authority without flagging this. I independently confirmed `1 − 0.05^(1/41) = 0.070461`.

---

## CHECKED AND FOUND SOUND

1. **The induction proof, on its own terms (R1), is valid.** `d ∈ CERTAIN(t+1) ⟹ ∅ ≠ S(d,t) ⊆ CERTAIN(t)`; `d ∈ DESC(t+1) ⟹ S(d,t) ∩ DESC(t) ≠ ∅`; together they force `CERTAIN(t) ∩ DESC(t) ≠ ∅`. I could not construct a counterexample and the 4000-world search found none in 7,560 direct-contact rows.
2. **Every edge case the task named is handled.** Cells with no sources are excluded from *all three* sets before any membership test (`tbrt02_lineage_c4.py:113-115`), so a source-less cell can neither enter CERTAIN nor seed DESC. `certain` becoming empty does **not** make `S <= certain` return a vacuous True: the `if not S: continue` guard precedes it, and `and certain` (`clea01_lineage_i1.py:73`, `tbrt02_lineage_c4.py:116`) is a correct redundancy. Once CERTAIN is empty it stays empty — consistent with the proof. Roots never overlap: competitor-to-nearest-daughter Chebyshev is 17–18 in all 41 worlds against a required minimum of 2.
3. **Differential verification of the enumerator.** I wrote an independent re-implementation sharing no code with the repo (rows rebuilt from the `.npz` by hand, neighbourhood by hand, sets by hand) and ran it on 12 archives × both variants × 13 fields: **0 mismatches**. Separately, the current code's `variant="A"` path reproduces the committed pre-edit A files exactly on 15 archives.
4. **Every aggregate in C4 recomputed from the per-archive files: all match exactly** — §5 audit flags, §6 R1 counts and rows, §9 R2 counts, first-contact stats, DESC stats, the internal-consistency flag, §10 all 30 stat blocks across both variants and three arms, §11 counts, §12 both paired contrasts. `1 − 0.05^(1/41) = 0.070461`.
5. **Hashes.** `C4_CONTENT_HASH` verifies. `PARENT_C3_CONTENT_HASH` matches `C3_CONTENT_HASH`. `METHODS_HASH` matches the freeze and all **17** methods files are byte-unchanged today (my first attempt reported a mismatch — that was my own path-format error, corrected: `canonical_digest(METHODS_FILES)` reproduces).
6. **Archive integrity.** 9 of 123 archives spot-checked: sha256 matches the sealed ledger in all 9. The ledger holds 41 admissible triples; 123 archives; every admissible triple has three arms.
7. **The variant-B mass-conservation audit, verified against the raw rather than against the repo's own audit field.** In **41/41** worlds the Y mass at `parent_cells` in the recorded t_m row equals `meta.intervention.competitor_mass`; in **41/41** the competitor cell is unoccupied at t_m; in 37/41 the competitor cell carries exactly that mass at t_m+1 (the other 4 are the documented first-step hops). The reconstruction removes exactly the Y the intervention removes (`parent_emptied` is asserted at `tbrt02_fork.py:103,108`) and places exactly the mass it places — **genuinely no free parameter**, as claimed. Variant B is not merely an alternative; it is the correct initial condition for the post-fork trajectory.
8. **The selection-bias condition of the bound, verified from source.** `tbrt02_fork.py`: non-admissible return at 60-66, fork at 70, DISPLACED intervention at 89, no arm stepped before 119-120. Admissibility is settled from the common prefix alone.
9. **The "never operationalised in code" claim (§2).** Grepping every file under `TBRT02/code` **as of commit `ec4f83b`** for `absorb|refut|descendant`: hits occur only in prose and in the freeze's own quoted text, never as a procedure. Claim stands.
10. **The `POSSIBLE ≡ CERTAIN` proxy is valid.** The file tests equality of duration *and* exposure rather than of the sets. On 10 sampled worlds spanning all three arms and both outcomes, the proxy agrees with true per-step set identity: **0 disagreements**.
11. **The §11 SELECTIVE claim is verified, not just asserted.** "Removing the parent leaves the daughter as the only Y source" — at t_m the entire Y population lies in `parent_cells ∪ daughter_cells` in 41/41 worlds, in exactly 2 components.
12. **The capability search reproduces bit-for-bit** (0 / 1720 / median 11) and its control is a fair one (see F10 for the two prose corrections).
13. **No claim about lineage, heredity, reproduction or life is smuggled in.** All status fields are carried verbatim from the parent artefacts; `MODEL_C_STATUS` refuses both refutation and corroboration; the file states outright that its own primary adjudication cannot discriminate and that the falsifiability claimed in `tbrt02_displace.py:20` is not established. The biological vocabulary that remains ("descends from her", "viability") names computed objects, not world facts — with the one exception noted in F6.

---

## WHAT I DID NOT CHECK

Stated explicitly so nothing here is implied to have been verified.

- **I did not re-run the engine.** The archives were not shown to be the deterministic output of the recorded seeds; `rng_hash_before`/`rng_hash_after` were not verified. Archive bytes were checked against the sealed ledger for **9 of 123** archives only.
- **R3 was not measured.** My claim that R3 is vacuous is a proof from the engine source plus the full-horizon locality scan, not a direct observation of quantum identity. I did not attempt a re-run with a tagged-Y tracker.
- **The addendum's own verification claims were not reproduced** — neither the 200,000-run Monte-Carlo coverage nor the 200-step bisection cross-check. I verified only the closed form at n = 41.
- **Scope of my recomputations:** the full-horizon locality scan covered all 123 archives; my independent lineage oracle covered 12 archives; the R5 computation covered the 41 DISPLACED archives; the set-identity proxy check covered 10 world-arms. The remaining per-archive numbers were verified only through the repo's own `C4_LINEAGE_*` files, which I did not independently regenerate in full.
- **I did not audit** the seed manifest, the forbidden-seed set, the ceiling arithmetic, the EVCS01 sizing, or anything in C1–C3 beyond the hashes and the fork/admissibility source path.
- **I did not evaluate** whether `CORE_R = 5.0` single-linkage is a good definition of a body. I took it as given because this programme froze it, and R5's status as "defensible" rests on that inheritance, not on my endorsement.
