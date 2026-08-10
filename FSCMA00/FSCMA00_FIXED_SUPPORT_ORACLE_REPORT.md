# FSCMA00 -- fixed-support oracle report

The reader, endpoint, grid, weights, detector and checkpoint time are inherited from WSFSCRP00
without a single change (`FIXED_SUPPORT_READER_CHANGE = false`).

## Oracle checks passed in this programme

* **Sham determinism re-verified in this container.** A replicate sham on the gauge founder
  reproduced the other sham bit-for-bit across the full horizon, including the terminal state
  hash: `True`.
* **Structural zero at h = 0.** Every one of the 30 scored
  intervention arms in this programme has `r(h=0) = (0, 0)` exactly, in rational arithmetic.
* **Touch sets.** Every environmental arm touched `['N']` and nothing else; every carrier arm
  touched `['Mf']` and nothing else.
* **Source immutability.** The founder checkpoint bytes were re-hashed after every operator
  application and were unchanged in every case.
* **Exact budget injection.** `sum(N)` changed by exactly 2048.0 for `+0.50*N0` and exactly 1024.0
  for `+0.25*N0` on a 64x64 lattice with `N0 = 1` -- i.e. `amp * N0 * L^2`, to the bit.

## Material signal

| arm | A_bu range | A/ETA range |
|---|---|---|
| carrier (BASIS, parent) | 4.750e-03 .. 9.700e-03 | 3.69 .. 8.26 |
| carrier (LOCKED, this programme) | 4.602e-03 .. 9.751e-03 | 3.38 .. 8.15 |
| environmental +0.25 (BASIS) | 5.876e-02 .. 6.324e-02 | 39.01 .. 50.41 |
| environmental +0.50 (BASIS) | 1.129e-01 .. 1.221e-01 | 75.35 .. 97.30 |

Every cell clears its own ETA. The environmental response is about
11.2x the carrier response in weighted amplitude.
