# FSCMA00 -- environmental probe report

19 engine starts (plus 1 discarded pre-outcome), against a cap of 24. Two predictions were frozen
to disk **before** the first environmental start, both derived from static structure alone.

## The mechanism that generated the predictions

* Every carrier operator leaves N bit-identical, so it changes the total nutrient budget by exactly zero, and by the one-step dependency matrix it cannot reach rho at all within one step. It acts as a multiplicative transport-coefficient perturbation.
* The environmental operator adds +amp*N0 at all 4096 sites, changing the nutrient budget by exactly amp*N0*L^2, and reaches rho within one step through the growth term. It acts as an additive source perturbation that INJECTS matter into both scored windows.

## P1 -- common mode

Prediction: the environmental response loads on `s = dA + dB` more heavily than *any* carrier cell.
Threshold, fixed in advance from the 12 carrier cells: **0.1457**.

| set | sum-mode share |
|---|---|
| carrier, 12 cells | 0.0358 .. 0.1457 |
| environmental, 12 cells | 0.9687 .. 0.9933 |

**P1_CONFIRMED**, with no overlap and a separation factor of
6.6. Carrier operators redistribute between the two
windows; the environmental operator fills both.

## P2 -- off-family

Prediction: environmental cells fall outside the affine family fitted on the carrier BASIS, at the
same 0.10 threshold the carrier cells must satisfy from the inside.

| k | carrier OFF max (tube valid?) | environmental OFF range |
|---|---|---|
| 1 | 0.5252 (False) | 0.9991 .. 1.0000 |
| 2 | 0.1895 (False) | 0.9026 .. 0.9223 |
| 3 | 0.1195 (False) | 0.8181 .. 0.8307 |
| 4 | 0.0319 (True) | 0.1456 .. 0.1654 |

At k = 1 the environmental response is essentially **orthogonal** to the carrier family
(OFF ~ 0.999). Even at k = 4, the smallest dimension at which the carrier tube closes at all, the
environmental cells remain at OFF ~ 0.15. **P2_CONFIRMED**.

## Dose

`|r(+0.50)| / |r(+0.25)| = 1.9218` with cosine
`>= 0.999216`. The environmental response is a one-dimensional amplitude
family, close to linear in dose (slightly sublinear -- mild saturation), along a direction the
carrier repertoire cannot reach.

**Branch: H2_SECOND_MODE_CANDIDATE.**
