# LCI-CAUSAL-TURNOVER-PREREG-03 — Phase 8: Power analysis (DEV-derived; non-prospective)

*Each quantity dimensioned separately. DEV inputs from seeds 50001–50010 (`turnover_dev_certificate.json`). No
prospective family is opened.*

## Inputs (DEV, non-prospective)

| quantity | DEV value |
|---|---|
| eligibility (≥3 targets sep ≥24) | 8/10 = 0.80 (confirm-02 was 23/32 = 0.72) |
| feasibility of eligible (3 alive/distinct/non-fusing at M_i≤0.25) | 4/8 = 0.50 |
| net valid worlds / seed | 0.40 (0.32 under the conservative 0.72×0.45) |
| deep interventional own | mean 0.131, **world-SD 0.020** (tight) |
| deep own−neigh, own−sham | ≈ own (neighbour, sham ≈ 0) |
| deep/rest retention | 0.68 |
| deep graded own-dose decode | R²=0.135 < neighbour-dose 0.580 (n=4 worlds / 12 samples) |

## Feasibility (family sizing)

Smallest family N with P(Binom(N, p) ≥ 12) ≥ 0.90:

| eligibility | feas | net p/seed | N for ≥12 valid @90% |
|---|---|---|---|
| 0.72 | 0.45 | 0.324 | **49** |
| 0.72 | 0.50 | 0.360 | 44 |
| 0.80 | 0.45 | 0.360 | 44 |
| 0.80 | 0.50 | 0.400 | 39 |

**Recommend a fixed cap of 50 seeds** (`54001–54050`) to clear ≥12 valid worlds at ≥90 % even under the pessimistic
net rate. No post-hoc extension is permitted (frozen cap).

## Interventional causal own (G4) — well-powered

World-level bootstrap at mean 0.131, SD 0.020: P(lower-CI(own) > 0) = **1.000 at n_valid ≥ 6**. own−neigh and
own−sham identical (neighbour, sham ≈ 0). So G0-feasibility (≥12 valid) already over-powers the interventional
gates. **These gates will almost certainly PASS** — which is exactly why they are the *low* bar (coupled readout).

## Graded storage decode (G3) — the hard, at-risk rung

The graded own-dose decode is the informative rung and is **doubly threatened**:

1. **Underpowered** — prior graded-decode power on this project: n=9 worlds → 0.10, n=18 → 0.75. Storage decode
   needs **≥18 valid worlds** even for a real effect.
2. **Likely genuinely near-null** — DEV deep own-dose (0.135) does **not** beat neighbour-dose (0.580), and the deep
   memory homogenizes locally (m₊ spread 0.07→0.007, `GLOBAL_CHANNEL_AUDIT.md`). The graded own signature is being
   erased by forgetting/templating, so more worlds may not rescue it.

**G3 is designated PRIMARY-at-risk.** A confirmatory family sized for feasibility (50 seeds → ~14–20 valid) reaches
the ≥18-world storage-decode power only marginally, and only if the effect is real — which DEV suggests it is not.

## Retention (G5) — descriptive

deep/rest ≈ 0.68 (per world 0.60–0.79), deep − rest world-CI [−0.086, −0.046] (deep significantly below rest). No
0.50 threshold is invented; retention is reported descriptively.

## Bottom line

A confirmatory family would, on DEV evidence, most likely yield **G0 PASS** (with 50 seeds), **G4 PASS**
(interventional survives), **G3 INDETERMINATE/FAIL** (graded storage homogenizes). By G6's rule (needs G3) and the
règle finale, that is **not** a clean "individuation survives turnover" — it is "spatial-locality survives, graded
content does not," the outcome that would motivate (not confirm) ACTIVE-RECONSTRUCTION.
