# EXP-GT-CONTINUOUS-FINGERPRINT-01 — PROTOCOL (PREREGISTERED)

**Tail-Aware Continuous Causal Fingerprint.**

Written and committed **before the v01 instrument exists**. Version 00 is `FAIL — RETIRED`; its hold-out is
**burned**; nothing here inherits its PASS.

---

## 1. The claim

> A fixed continuous-response fingerprint can **distinguish sufficiently observed slow relaxation from genuinely
> unresolved in-flight response**, while preserving continuity, difference, abstention, and repertoire-relative
> equivalence under a frozen continuous measurement contract.

**Not claimed:** identity · lineage · life · autonomy · **droplet transfer** · material-turnover continuity ·
universal tail modelling · universal system identification.

## 2. The exact defect being attacked

Version 00 conflated two different questions:

| the question it asked | the question it should have asked |
|---|---|
| **Is the signal still moving?** | **Is the unobserved remainder large enough to change the verdict?** |

`P_cascade`: distance **64.15** against a separation radius of **23.36** — strongly separated — and v00 returned
`INDETERMINATE`, because its tail was moving by 5.3% of peak against a frozen 5% threshold. Its true settling time
was **108** inside a **160**-sample window. **The window was long enough and the system was decidable.**

**Merely raising the 5% threshold is forbidden.** That is tuning on the failed hold-out and it would get control
**T4** wrong, by construction.

## 3. The three-way distinction (required)

| status | meaning |
|---|---|
| `DECIDABLE_SETTLED` | the remainder is at or below the noise floor; the fingerprint is a faithful summary |
| `DECIDABLE_SLOW_TAIL` | the signal is **still changing**, but the bounded remainder **cannot cross the decision boundary** |
| `INDETERMINATE_IN_FLIGHT` | the unseen remainder **could** change the verdict, or is unbounded |

## 4. The tail-uncertainty method — bound the *eventual* distance, do not model the tail

The fingerprint is an RMS over an observation window. The question "would a longer window change the verdict?" is
answered by **bracketing the distance on an extended window**, not by fitting a curve to the tail.

For each probe block, on the difference trace `delta(t) = z_A(t) - lambda * z_B(t)`:

1. **The tail region begins at `T_TAIL0 = D_HOLD + D_MAX`.** No causal component may arrive later than the probe's
   end plus the declared delay horizon, so **settling may not even be assessed before then.** This is what defeats
   the delayed-second-component trap (**T5**), on which a local-derivative guard stops in the plateau.
2. Split the tail region into **three** equal sub-blocks; take their means `mu1, mu2, mu3`.
3. Geometric (Aitken) extrapolation of the level: `rho = (mu3-mu2)/(mu2-mu1)`; remaining movement
   `R = (mu3-mu2)*rho/(1-rho)`; asymptote `delta_inf = mu3 + R`.
4. **Envelope bound** on any future value: `|delta(u) - delta_inf| <= B := |R| + ripple3` for all `u >= W`, where
   `ripple3 = max|delta - mu3|` inside the last sub-block (this is what carries an *underdamped* tail, whose level
   is flat while the signal rings).
5. **Refuse rather than extrapolate** when the tail is not a bounded relaxation:
   * `|rho| >= RHO_MAX` -> not converging -> **UNBOUNDED**;
   * implied `tau = -L/ln|rho| > TAU_MAX` -> **out of the declared contract** -> **UNBOUNDED**;
   * the extension needed to bury the remainder exceeds `L_MAX` -> **UNBOUNDED**.
6. **Bracket the extended distance.** With `K` further samples of remainder whose RMS lies in
   `[rho_lo, rho_hi] = [max(0,|delta_inf|-B), |delta_inf|+B]`:

   ```
   d_ext = sqrt( (W*d_obs^2 + K*rho^2) / (W+K) )   is monotone in rho, so
   d_lo  = sqrt( (W*d_obs^2 + K*rho_lo^2)/(W+K) )     d_hi = sqrt( (W*d_obs^2 + K*rho_hi^2)/(W+K) )
   ```
   Aggregate across blocks with the **max** (preserved from v00: a FOR-ALL is certified by its worst case).
   `D_lo = max_b d_lo,b` and `D_hi = max_b d_hi,b` bracket the aggregate.

7. **The verdict is read off the bracket, not off the point estimate.**
   * `D_hi <= r_continuity` -> `INDISTINGUISHABLE_UNDER_REPERTOIRE`
   * `D_lo >= r_separation` -> `DIFFERENT`
   * otherwise the bracket **straddles a boundary** -> `INDETERMINATE_IN_FLIGHT`

   A block whose tail is UNBOUNDED gets `d_lo = 0, d_hi = inf` and therefore forces abstention. No separate
   fraction threshold is needed, and there is no knob to turn.

**If the remainder is below the noise floor it cannot change anything, and the block is `SETTLED`.** A tail below
the noise is not an unresolved cause; it is nothing (**T6**).

## 5. The DECLARED TAIL CONTRACT — properties of the domain, not of the system being judged

```
TAU_MAX = 80     the slowest ACCESSIBLE relaxation the instrument is qualified for
D_MAX   = 60     the longest ACCESSIBLE transport delay; nothing may arrive after (probe end + D_MAX)
L_MAX   = 240    the longest extension over which a remainder may be buried (3 * TAU_MAX)
```

Declared exactly as the noise scale is declared, and for the same reason: **these are properties of the domain,
not quantities the instrument may infer from the system it is currently judging.** A system outside them is
**OUT OF CONTRACT and refused** — an honest abstention, not a failure.

**`TAU_MAX = 80` against a `W = 160` window is deliberate.** With `TAU_MAX = 40` the window is four time constants
long, every admissible system has already settled by its end (measured remainder beyond `W`: cascade2 **0.02%**,
multi-strong **0.07%**, the burned cascade **0.13%**), `DECIDABLE_SLOW_TAIL` would never occur, and **the
three-way distinction this experiment exists to test would be vacuous** — passing loudly while testing nothing.

## 6. The preserved core (unchanged, and independently re-qualified on the new split)

continuous response blocks · noise calibration · the `lambda`-quotient for noise-scale estimator uncertainty ·
max-over-probes aggregation · the fixed intervention battery · unit invariance · gain sensitivity · sign
sensitivity · hidden-state detection · responsiveness · coverage · `EQUIVALENCE_CLASS_ONLY` · exclusion of labels,
topology IDs and tracker IDs.

**Only the in-flight guard and the verdict logic change.** v00's six frozen files are **not modified**: v01 is
additive, and v00's freeze manifest still verifies byte-for-byte.

## 7. Split

`docs/CFP01_SPLIT_MANIFEST.json`, committed **before** the instrument changes. Verified: **v01 prospective reuses
ZERO v00 systems** (dev or prospective). The burned pair (`P_cascade`/`P_leak`) appears **only** as v01
*development* regression `R_cascade_burned`/`R_leak_burned` — control **T1**. Reserved to prospective alone: a
**third-order cascade**, an order development never sees.

## 8. Controls — each must do what it says

**T1** burned-case regression: `R_cascade_burned` may be classified **only** if its bound proves the verdict cannot
change. **Hard-coded exception is forbidden.** · **T2** genuine in-flight -> must abstain · **T3** slow but harmless
tail -> must classify · **T4** slow tail near the boundary -> must abstain · **T5** misleading flat tail (delayed
second component) -> the naive derivative guard must fail, the frozen one must not · **T6** noise/drift must not be
read as unresolved response · **T7** window-extension invariance · **T8** short window -> abstentions must increase
· **T9** guard removed -> at least one premature false verdict must appear · **T10** v00's guard restored -> at
least one unnecessary abstention must reappear.

## 9. Prospective gates (predeclared, exact)

1 zero false difference on continuity cases · 2 zero false sameness on difference cases · 3 genuine in-flight
abstains · 4 decidable slow tails classify · 5 no verdict changes under valid window extension · 6 predeclared
separation gate holds · 7 unit invariance exact · 8 gain and sign detectable · 9 hidden state separates · 10
limited-access collisions return `EQUIVALENCE_CLASS_ONLY` · 11 truth paths agree on every scored case · 12 no
prospective tuning or relabelling.

**A required abstention counted as a classification is a failure. An unnecessary abstention on a predeclared
decidable case is equally a failure.**

## 10. Kill switch

Any prospective gate fails -> **v01 is RETIRED**. No repair, no rerun on the same hold-out. PASS authorizes **only**
`SC-PILOT-CONTINUOUS-FINGERPRINT-PREFLIGHT`, which is **not executed**.
`SC-PILOT-CAUSAL-FINGERPRINT` remains **BLOCKED**. `EXP-SC-01` remains **BLOCKED**.
