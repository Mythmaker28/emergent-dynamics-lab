# FCDDH00 — P2 GAUGE AND CO-OPTIMALITY SPECIFICATION

## 1. The inherited physical gauge

The parent representation carries one **linked A/B exchange per complete descendant**. Exchanging
the two support channels swaps `delta_A` and `delta_B`, which leaves the common half `u`
unchanged and flips the sign of the differential half `v`. The gauge is therefore a single sign
`s in {+1,-1}` per descendant, **shared across both carriers and every scored time**:

```
z(s) = ( u , s*v )        ||z(s)||^2 = M2^2 for either s
```

## 2. The immutable parent-P2 residual selection rule

With `Q = I - P2_parent`, `a_o = u_o - mu_parent`, `b_o = v_o`, the descendant's total outside-P2
residual at gauge `s` is

```
sum_o ( a_o^T Q a_o + b_o^T Q b_o )  +  2 s  sum_o a_o^T Q b_o
```

Only the second term depends on `s`, so the minimiser is determined by the single statistic

```
D_desc = sum_{o in {CARRIER_1, CARRIER_2}} ( u_o - mu )^T Q v_o
s = -1  if D_desc > 0 ;   s = +1  if D_desc < 0 ;   BOTH co-optimal if D_desc = 0
```

This is exactly the parent rule (`FSQBT00/fq_analysis.py`, gate B). It reads **only** that
descendant's own two carrier rows and the immutable parent objects `mu`, `P2`. It is blind to
geometry, to allocation, to the discovery/hold-out role and to any candidate-axis score.

## 3. Block separability

`D_desc` depends on one descendant alone. The gauge is therefore **descendant separable**, hence
a fortiori **block separable**: no descendant's gauge can depend on any other descendant, on any
other ancestry, or on panel membership. Consequences, all required by the protocol:

* every leave-one-ancestry-out fold rebuilds each retained **and** omitted descendant gauge from
  that descendant's own response, by the same label-blind, axis-blind criterion; a full-panel
  gauge is never reused;
* the fold gauges are numerically identical to the full-panel gauges, which is a *consequence* of
  separability, not an assumption: the folds recompute them;
* no globally coupled discovery optimisation is ever substituted.

If separability could not be proved from the parent rule the axis would be declared `UNRESOLVED`.

## 4. Co-optimality

`D_desc` is carried as a certified rational interval. Three cases:

| case | verdict |
|---|---|
| `D_desc` interval strictly positive | unique gauge `s = -1` |
| `D_desc` interval strictly negative | unique gauge `s = +1` |
| interval contains 0 (exact zero, or not certifiably signed) | **co-optimal orbit `{+1,-1}`** |

A co-optimal descendant is **enumerated, never averaged away**. Every co-optimal combination is
expanded and the categorical verdict (cell materiality, direct contrast, `J`, the fixed axis
score sign, and every gate) must be identical across the entire orbit. If any verdict differs
across the orbit, the affected field is reported as `UNRESOLVED` — never silently resolved and
never averaged. Gates D9 (discovery) and H3 (hold-out) carry this requirement.

The number of co-optimal descendants is reported explicitly in
`DISCOVERY_COOPTIMAL_GAUGE_REPORT.json`; the enumeration cap is 12 descendants (4096 combinations),
above which the affected panel is declared `NUMERICALLY_OR_GAUGE_UNRESOLVED` rather than sampled.

## 5. What the gauge may never do

* it may never be chosen to make a score, a margin, a verdict or an axis look better;
* it may never see a geometry label, an allocation label, a role label or the candidate axis;
* it may never be applied to one carrier of a descendant and not the other;
* it may never be re-selected after any response has been decoded on the hold-out — on the
  hold-out path the linked A/B enumeration under this same immutable criterion is the **only**
  finite search permitted, and it cannot fit, orient or rescale `v_D`.

## 6. Independent reference

`fh_ref.gauge_sign` chooses the gauge by evaluating the descendant's **total residual at both
signs and taking the argmin**, rather than by the sign of the cross statistic `D_desc`. The two
routes must agree on every descendant (or the descendant must be flagged co-optimal). This is a
genuine second path to the same answer, not a restatement of the first.
