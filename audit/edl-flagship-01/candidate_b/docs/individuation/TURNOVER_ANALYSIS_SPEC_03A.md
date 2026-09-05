# HISTORICAL CLAUDE 03A ANALYSIS — NON-AUTHORITATIVE

Superseded by the canonical specification in `PRESEAL_CANDIDATE_PROTOCOL.md` §6-7 and the frozen implementation
`turnover_statistics.py`. Do not execute or seal from this file.

# LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A — Repaired statistical-analysis specification (TASK 2 + access structure)

*Frozen before prospective data. Makes graded **own-history ownership** the co-primary gate; demotes the
interventional feeding effect to a mechanistic check (its null is the algebraic prediction D). No composite score,
no coordinate switching, no post-hoc decoder selection.*

## 1. Coordinates (frozen)

- **Primary coordinate: cumulative dose / m₊ only.** All primary gates use own cumulative dose.
- **Order / m₋: secondary, descriptive only.** No coordinate switching dose↔order. The closed V4 **h2** program is
  **not** reopened.

## 2. Decoders and resampling (frozen; identical machinery to confirm-02)

- Ridge decoder, **world-grouped leave-one-world-out** (LOWO) cross-validation. Unit = world. The 3 droplets of a
  world are **not** independent; no row-level leakage (a world is entirely in train or test).
- **Within-world permutation null** (permute dose within each world) → null-95.
- **World-level bootstrap** CIs (resample worlds).
- **No post-hoc decoder selection**: regularization grid and feature set frozen here; the single frozen decoder is
  applied without tuning on prospective data.

## 3. PRIMARY gate G3-OWNERSHIP (co-primary with feasibility)

At the deep snapshot, decode own cumulative dose and require **own strictly more informative than neighbour AND
than global**:

```
own_dose_R2   > within-world null-95         (own carries own dose)
own_dose_R2   > neighbour_dose_R2            (not the neighbour's dose)
own_dose_R2   > global/world_dose_R2         (not a shared/global signal)
world-bootstrap lower CI of (own − max(neighbour, global)) > 0
```

A merely positive local field or feeding effect is **insufficient**. Baselines that must **fail** where own
succeeds: body size, mass, position, environment (N/c). If a baseline decodes own-dose as well as memory, the claim
is a geometric/environmental artefact, not memory.

## 4. Distributed-access ACCESS-STRUCTURE test (co-reported; frozen interpretations)

Decode own-dose from four **frozen readout scopes**, same worlds/folds/regularization/null:

- **L** target droplet only; **P** target + neighbouring droplets; **E** environment with **target memory masked**;
  **G** complete world/global state.

| pattern | interpretation (frozen) |
|---|---|
| L succeeds; P/E/G add little | predominantly **local** memory (compatible with individuation) |
| L and E both succeed similarly | **redundant droplet–environment** encoding; local ownership NOT established |
| L fails but P or G succeeds | **distributed/synergistic** access; individual-memory claim fails |
| E succeeds while L fails | **environmental trace**, not droplet memory |
| all scopes fail at deep | graded history **information lost** |

`up_ref := 0` is the mechanistic diagnostic of the known global channel; a null there does **not** prove no
distributed channel. At n_valid < ~18 do **not** fit a multivariate synergy/PID estimator — report the scope
comparison descriptively and treat ACCESS as **exploratory-becoming-primary** only at full power. (DEV n=4: no scope
beats null — unresolved.)

## 5. SECONDARY causal check (NOT a primary gate)

Interventional own/sham/neighbour/ablation/fixed-mask (confirm-02 battery) is reported, but its **null is the
algebraic direct-coupling prediction D**: it counts as independent evidence only if `own_observed ≫ own_predicted`.
Otherwise it is the coupling multiplier and does not, by itself, support individuation.

## 6. Retention (G5) — descriptive, no invented threshold

Report rest, deep, ratio, difference, paired world-CI. "Causal survival" = deep own lower-CI > 0. A "strong
retention" threshold is used **only** if a mechanistic justification is stated; otherwise retention stays
descriptive (no auto-0.50).

## 7. Frozen gate summary

- **G0 feasibility** (co-primary): ≥ pre-declared valid-world floor at the frozen cap (`TURNOVER_POWER_REPAIR_03A.md`).
- **G3-OWNERSHIP** (co-primary): §3 (own > neighbour AND global).
- **ACCESS** (co-reported): §4.
- **G1/G2 rest** replication as confirm-02.
- **G4 interventional** SECONDARY, null = D (§5).
- **G6** PASS only if G0 ∧ G1 ∧ **G3-OWNERSHIP** ∧ own separable from neighbour AND global AND not explained by a
  baseline; the interventional effect alone can **never** carry G6.
