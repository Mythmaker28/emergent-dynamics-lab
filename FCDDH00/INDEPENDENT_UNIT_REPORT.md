# FCDDH00 — INDEPENDENT UNIT REPORT

## 1. The unit

The **only** independent unit in this programme is **one upstream ancestry block**. Within a
block, the four descendants, the two carriers, the two support channels, the sites and the ten
scored times are **repeated conditions**, not independent observations.

```
1 block = 1 upstream seed S
        = 1 byte-identical precursor  PRECURSOR(S) = seed_state(SPEC, TRACER, S, "random")
        -> 4 descendants   (NEAR, FAR) x (H3 member 0, H3 member 1)
        -> 8 active rows   4 descendants x {CARRIER_1, CARRIER_2}
        -> 8 sham rows     4 descendants x {SHAM_0, SHAM_1}
```

Everything downstream of the block is collapsed **before** any inference: the two carriers into
one carrier-differential `d`, the two allocation members into one averaged `x[b]` (or into one
worst-of-four `J[b]`), and the twenty coordinates into one scalar along a fixed axis. The
estimand therefore produces **exactly one number per independent unit**, which is the only level
at which any count, any sign tally or any randomization distribution is ever formed.

## 2. What was realised

| level | planned | realised |
|---|---|---|
| discovery independent units | 12 | **12 sealed** |
| discovery descendants | 48 | **48 sealed** |
| discovery sham rows | 96 | **59 acquired, 37 missing** |
| discovery active rows | 96 | **0** |
| hold-out independent units | 16 | **0** |
| hold-out descendants | 64 | **0** |
| hold-out active rows | 128 | **0** |

No inference of any kind was performed, because the discovery panel never reached a decodable
state. No `n` was ever formed.

## 3. Why the crossing matters for the unit

FSQBT00's twelve blocks carried **one descendant each**, with geometry and allocation tied to
`S mod 4`: the factors were confounded with the ancestry. FCDDH00's blocks carry **all four
cells inside one ancestry**, from byte-identical precursor bytes, with geometry and allocation set
by explicit arguments. That is what makes `x[b]` a *within-ancestry* contrast: the upstream draw
cancels exactly, and the block is the unit at which the geometry coin is applied — one fair
sign-flip unit per ancestry. This structural gain was fully realised and is committed: 12 blocks,
12 distinct precursor hashes, 4 cells each, verified field-by-field at construction time.

## 4. What may never be counted as independent

* the 4 descendants of a block (they share one precursor and one geometry coin);
* the 2 carriers of a descendant (they share one sham and one TAU);
* the 2 support channels, the sites, and the 10 scored times (they are the coordinates of one
  response vector, related by the frozen weights);
* the 4 cross-orbit allocation pairings of a block (they reuse the same four descendants);
* the 64 hold-out descendants as 64 Bernoulli trials — they are clustered within 16 ancestries.

## 5. Consequence for the closed programme

Because no response was decoded, there is no effect size, no p-value, no interval and no count in
this delivery. The only quantities reported are structural: charged starts, hashes, twin identity
at hash level, and panel completeness.
