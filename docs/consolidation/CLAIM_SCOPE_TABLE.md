# CLAIM-SCOPE TABLE (sign-safe consolidation)

| claim | assumptions | substrate | prospective | indep. impl | falsifier | status |
|---|---|---|---|---|---|---|
| With a clean anchor, \|q\| ∈ [min\|v\|,max\|v\|] (T6-C) | ≥1 uncontaminated reference; spread≥0.15 | synthetic + ctrans | fresh PASS | 20/20 | a clean-anchor case the bracket misses | **SOLID** |
| With a sign contract, point-identified at the sign's extreme | anchor + declared sign(α·κ) | synthetic | fresh PASS | agree | a signed case the point misses | **SOLID** |
| No anchor + attenuate → lower bound (max\|v\|≤\|q\|) (T6-A) | 0≤α_iκ_i<1 ∀i | synthetic | fresh PASS | agree | an attenuating case with max\|v\|>\|q\| | **SOLID** |
| No anchor + amplify → UPPER bound (min\|v\|≥\|q\|) (T6-B) | α_iκ_i≤0 ∀i | synthetic | fresh PASS | agree | an amplifying case with min\|v\|<\|q\| | **SOLID (corrects historical error)** |
| No anchor + no sign → NON-identifiable (T6-E) | none | synthetic | fresh PASS | agree | any recovery without sign/anchor | **SOLID (impossibility, proved)** |
| Historical "argmax gives a lower bound" | e_i≥0 AND g_i>0 (undeclared) | ctrans | historical only | falsified | amplifying contamination | **RETRACTED** |
| Point recovery E/E*≈1.00 | ctrans dynamics | ctrans only | 12/12 | — | any 2nd substrate | **ctrans-SPECIFIC (FHN 0.86)** |
| Structural identifiability transfers across substrates | rest pre-window, distinct couplings | ctrans + FHN | — | — | a substrate where the classes mis-fire | **STRUCTURAL PASS** |
| Passive droplet references common-mode contaminated | shared nutrient field | scaffold | POD | — | a clean far-field passive reference | SOLID (negative) |
| Droplet identity / continuity / life | — | — | — | — | — | **NEVER CLAIMED** |

Every retained claim has a falsifier. The retracted historical claim is replaced by T6-A/B/C.
