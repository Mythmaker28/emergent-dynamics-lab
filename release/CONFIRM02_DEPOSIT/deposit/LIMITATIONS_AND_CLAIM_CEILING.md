# Limitations and claim ceiling — LCI-CAUSAL-NONMERGING-CONFIRM-02

*Publication document 4 of 4. This document is binding on the other three: nothing in
`MANUSCRIPT.md`, `DEPOSIT_METADATA.json` or `PROVENANCE_LEDGER.md` may exceed the ceiling below.*

---

## 1. The ceiling, verbatim

The maximal authorised claim for this work is, word for word:

> **Local interventional causal individuation in non-merging droplets.**

Nothing stronger may be written, said, tweeted, put in a title, put in an abstract, or implied by
omission.

## 2. Claims that are FORBIDDEN

| Forbidden claim | Why it is forbidden here |
|---|---|
| **Distal behaviour** | The readout is uptake, and uptake is multiplicatively coupled to m₊ in the engine. Nothing was measured away from the coupling. |
| **Graded metrology** | Graded decoding of dose from behaviour is **INDETERMINATE** (secondary, non-gating; world-level corr = +0.174). There is no measuring instrument here. |
| **Global identity** | The design establishes local, own-specific interventional effects. It says nothing about identity of the droplet as a global or persistent-through-turnover object. |
| **Bounded entity established** | Not tested. G0 establishes that three connected components stay distinct under a fusion cap; that is a geometric fact about the run, not a demonstration of a bounded entity. |
| **Turing behaviour** | Not tested, not approached, not implied. |
| **Life, agency, cognition, memory in the biological sense** | Not tested. The "memory" is an engineered scalar field in a PDE. |
| **Physical / chemical / biological result** | This is a **computational model** end to end. |
| **Independent replication** | One family, one run, one platform, one pipeline. |
| **Cross-platform result** | Determinism is byte-identical on the sealed platform only; the PDE is chaotic. |

## 3. The coupling — the single most important limitation

The behavioural readout is **not** an emergent behaviour. In the sealed engine
(`edlab/experiments/sc_mcm/engine.py`, blob `2a2aaf47`), uptake is computed as

```
g = dt · g0 · ρ · N · qq · (1 + β·σ) · (1 + λ₊ · m₊)      with λ₊ = 0.25
```

which the frozen protocol states in shorthand as **`uptake ∝ N·ρ·(1 + λ₊·m₊)`**.

Therefore: **erasing m₊ must change uptake.** That is arithmetic, not discovery. This is disclosed in
the manuscript **abstract**, in the metadata `mandatory_disclosures` block, and here.

What is *not* arithmetic, and what the frozen paired design actually tests:

- that the effect is confined to the **own** droplet (neighbour ≈ 0, sham ≈ 0 — perfect locality),
- that it survives on droplets that provably **never merge** (0 fusion, coverage ≤ 5.64 % vs a 15 %
  cap), refuting the "fusion artefact" hypothesis raised by the prior merge-incident audit,
- that it survives a **tracker-free** convergent readout (fixed mask, ratio 1.08× rather than the
  4.80× inflation seen in the fused, non-bijective regime).

The ablation control (λ → 0 → effect exactly 0.000) is a **manipulation check**: it confirms the
intervention machinery is wired as declared. Because the coupling is by construction, this control
carries **no independent evidential weight** for the causal claim and must never be presented as if
it did.

## 4. Statistical unit — the nesting, stated plainly

- 32 seeds run → **23 eligible worlds** → **23 G0-valid worlds** → **69 droplet-targets**
  (3 per world).
- **The 69 targets are nested within the 23 worlds. They are NOT 69 independent replications.**
- Every gate, every confidence interval and every p-value in this work is computed at the **world**
  level, n = 23, by world bootstrap (5000 resamples, seed 20260715).
- The statement "69/69 targets positive" is **descriptive consistency only**. It contributes zero
  additional degrees of freedom. Quoting it as if it were 69 independent successes would be a
  misrepresentation — this is precisely the error that the prior "39/39 droplets" claim committed and
  for which it was invalidated (only 24 unique final components; 17/39 survived under a bijective
  tracker).

## 5. Scope of the R* = 0.2575 addendum

**Post hoc. Additional sensitivity work. NOT part of the frozen prospective design.**

- It was produced in commit `9c8a62c`, *after* the design was sealed (`9b7580bc`) and *after* the
  prospective family had been run once (`830c2d0`).
- It uses **DEV worlds only** (50001–50009). No prospective 53xxx seed was opened for it.
- It consults **geometry only**; the causal effect size was never examined for it.
- **No headline result depends on it.** If this section were deleted, Section 4 of the manuscript
  would be unchanged.
- Its conclusion is negative about R*: 0.2575 has **no independent theoretical derivation**
  (fails anti-numerology criteria 3, 4, 5, 6; criteria 1 and 2 do not discriminate it from 0.24,
  0.25 or 0.26). The sealed 0.25×5 probe is kept.
- Its only positive reading is narrow: a +3 % perturbation of probe amplitude leaves the geometry
  unchanged (both 8/8 G0-valid, worst coverage 3.3203 % vs 3.3447 %, Δ +0.0244 pp), so the result
  does not hinge on fine-tuning the amplitude.

## 6. What "VERIFIED" means in this deposit

**VERIFIED = traced to an exact repository artefact** (exact path, exact commit, exact SHA-256,
exact JSON key or table cell). **It does NOT mean independently reproduced.**

- Only VERIFIED values appear as unqualified facts.
- NOT_FOUND values are either omitted or explicitly labelled NOT_FOUND. None is presented as a fact.
- DIFFERS values are labelled and **were not retained merely because a mission prompt asserted them**.
  A mission prompt is not scientific evidence. Where a prompt-supplied figure could not be matched
  digit-for-digit against an artefact, the artefact wins and the discrepancy is recorded.
- The one substantive DIFFERS in this pass: re-running the committed analysis script on the committed
  raw record reproduced every **gated** statistic exactly but was **not byte-identical** — five
  non-gating floats differ by 1–3 ULP (~10⁻¹⁵ relative). All manuscript figures are quoted at a
  precision at which both computations agree.

## 7. Reproduction status

- **Simulation stage: NOT re-run** in this pass. 32 seeds × 5 branch families of a chaotic RD-PDE
  with an 800-step warm-up is not cheap under this tooling budget.
- **Analysis stage: re-run** (33.7 s), from the committed raw record with the committed script.
  Output and diff are in `verification/`.
- **Seal integrity: re-checked.** All 8 SHA-256 entries in the PRESEAL's `sealed_file_sha256`
  manifest match the committed content exactly. No post-seal code drift.

## 8. Release blockers (hard stops)

1. ~~Literal `[COPYRIGHT HOLDER]` marker in the licence files.~~ **RESOLVED 2026-08-08** — the
   corresponding author declared the holder: `Copyright 2026 Tommy Lepesteur`.
2. ~~Author name placeholder.~~ **RESOLVED 2026-08-08** — `Tommy Lepesteur`.
   **Affiliation and ORCID remain undeclared** and were not invented (ledger N04, N05).
3. ~~CC-BY-4.0 is a proposal.~~ **RESOLVED 2026-08-08** — approved by the author. `license` is now
   `cc-by-4.0` for data/figures/text; code stays Apache-2.0.
4. **No DOI, funder or related identifier exists.** Still true. None was invented.
5. **Nothing has been submitted.** Still true, and unchanged by the licence approval: no Zenodo
   record, no preprint, no journal. Authorisation to deposit is a separate decision the author has
   not given.

*This deposit is a package for the author to review. It is not a submission and must not be treated
as one.*
