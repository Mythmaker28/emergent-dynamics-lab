# EXP-GT-CONTINUOUS-FINGERPRINT-02 — PROTOCOL (PREREGISTERED)

**Resolution-Certified Tail-Aware Continuous Fingerprint.**

Committed **before the horizon sweep is run** and before any v02 instrument code exists. v00 and v01 are
`FAIL — RETIRED`; neither is rewritten, repaired or rerun. v01's prospective split is **sealed** (audited: no `Q_*`
acquisition has ever existed on disk or in git history) and may be used **exactly once**.

---

## 1. The claim

> Under a frozen continuous measurement contract **whose temporal resolution is certified against its noise
> floor**, a causal-response fingerprint can classify decidable slow tails, abstain when the unseen remainder could
> change the verdict, and preserve continuity/difference discrimination on unseen continuous systems.

**Not claimed:** identity · individuality · lineage · life · autonomy · universal system identification ·
**droplet transfer** · material-turnover continuity · substrate-independent equivalence.

## 2. Why v01 died, in one line

Its tail bound's **noise floor (7.40)** exceeded the **real remainder it had to detect (8.25)** on the decisive
T4 case. The instrument confidently classified a pair whose unseen future could still change the answer.

**v02 is not a threshold patch.** The window is not raised to a convenient number. It is *derived* from an explicit
resolution contract and *certified* against the noise floor before the instrument may freeze.

## 3. THE RESOLUTION CONTRACT — the whole point of this version

The tail bound's remaining-envelope statistic is

```
B = (d2 + BOUND_K*sd) * rho_max/(1 - rho_max)  +  max(0, rip3 - RIP_NOISE_K*sig)
     rho_max = exp(-L/TAU_MAX)      L = (W - T_TAIL0)/3      sd = sig*sqrt(2/L)
```

Both of its terms depend on the horizon `W`, and **they pull in opposite directions**:

* the **noise floor** `B_noise(W)` falls as `W` grows — `L` grows, `sd` shrinks as `1/sqrt(L)`, and the
  amplification `rho_max/(1-rho_max)` collapses;
* the **signal** `B_signal(W)` — the true remaining envelope of a tail with time constant `tau` — **also** falls,
  as `exp(-W/tau)`, because a longer window leaves less outside it.

**A longer window is therefore NOT automatically better, and asserting that it is would be the same unexamined
reflex that produced v00 and v01.** The ratio can peak and then degrade. This protocol measures the ratio rather
than assuming its sign.

### Preregistered definitions (fixed here, before any sweep)

| symbol | definition |
|---|---|
| `B_noise(W)` | the **maximum** of the raw `B` statistic over NOISE-ONLY development blocks (systems that cannot respond). No label consulted. |
| `TAIL_NOISE(W)` | `1.2 * B_noise(W)` — the settled/slow-tail gate |
| **decision-relevant remainder** | a pair is *decision-relevant at `W`* iff, on the **noise-free privileged** traces, `d(W)` and `d(settled)` fall on **opposite sides** of `r_continuity` or `r_separation`. Instrument-independent. |
| `B_critical(W)` | the **smallest** measured `B` among development pairs that are decision-relevant at `W` |

### THE ADMISSIBILITY GATE — `k` is fixed NOW, at 3.0

```
        A battery at horizon W is ADMISSIBLE only if     B_critical(W)  >=  k * B_noise(W),     k = 3.0
```

**`k = 3.0` is frozen here and is not revisited after any distribution is seen.**

**Declared answer to the mandated question** — *what is the smallest decision-relevant unseen remainder this
battery can reliably detect?* — is `k * B_noise(W) = 3 * B_noise(W)`, reported in the resolution certificate for
every horizon on the grid.

## 4. PREREGISTERED HORIZON GRID

```
        W  in  { 160, 240, 320, 480, 640 }
```

Committed before the sweep. **The smallest horizon satisfying every development gate is selected** — not the one
with the prettiest separation. If none satisfies them, v02 **fails at development** and the sealed split is not
touched.

`T_TAIL0 = D_HOLD + D_MAX = 24 + 60 = 84` and `TAU_MAX = 80` are unchanged from v01. The episode length grows with
`W`; nothing else in the battery does.

## 5. Development gates (all must pass to freeze)

**D1** burned v00 cascade -> `DECIDABLE_SLOW_TAIL` · **D2** the v01 T4 case decided **only** by a valid bound, never
by exception · **D3** a decision-relevant unseen tail -> `INDETERMINATE_IN_FLIGHT` · **D4** a harmless slow tail ->
classifies · **D5** non-settling -> abstains/out of scope · **D6** window-extension stability · **D7** resolution
monotonicity within tolerance · **D8** noise/drift is not an unresolved tail · **D9** gain, sign, hidden state,
latency, feedback still detectable · **D10** continuity protected (units, solver, equivalent implementations) ·
**D11** limited-access collisions -> `EQUIVALENCE_CLASS_ONLY` · **D12** construction truth and the independent
privileged evaluator agree on every scored case.

## 6. Controls rebuilt properly (v01's T5/T7/T8 were crude and their verdicts meant nothing)

**T5** delayed second component: a purely local derivative guard must be *shown* to fail; the frozen guard is
protected by the declared delay horizon. **T7 / T8** are evaluated on **NESTED PREFIXES OF A SINGLE LONG
ACQUISITION** — same noise realization, same interventions, only the window truncated. Comparing separately
simulated noisy episodes as though they differed only in length, as v01 did, tests nothing.

Must-fail: exact float inequality · integer collapse · guard removed · v00's guard restored · window shorter than
the certified horizon · discriminating probe removed · hidden label leakage · unequal valid windows · **stale-cache
reuse must be caught by parameter/hash-keyed cache validation.**

## 7. Preserved core (unchanged unless the longer window demonstrably invalidates it)

fixed probe battery structure · NSRC representation · max-over-probes aggregation · the `lambda`-quotient · unit
invariance · gain and sign sensitivity · hidden-state detection · repertoire-relative equivalence · coverage and
responsiveness · exclusion of labels and tracker IDs. **The observation horizon changes; that is declared, and it
makes v02 a broader instrument.**

## 8. Stop rules

* T4's remainder still below the honest noise floor at the **largest** grid horizon ->
  `EXP-GT-CONTINUOUS-FINGERPRINT-02: FAIL AT DEVELOPMENT`. **No more flexible estimator may be invented after
  seeing that failure.**
* The certified horizon cannot plausibly transfer to the droplet sampling regime ->
  `SCOPE FAILURE — REQUIRED TEMPORAL RESOLUTION NOT TRANSFERABLE`. **An instrument that cannot later be mapped
  physically is not qualified.**
* Any prospective gate fails -> v02 retired, hold-out burned.

`SC-PILOT-CAUSAL-FINGERPRINT` remains **BLOCKED**. `EXP-SC-01` remains **BLOCKED**. No droplet experiment.
