# TEMPORAL PROVENANCE CERTIFICATE — `EXP-GT-PROV`, **20/20**

Written and passed BEFORE the observer that depends on it existed. D-067 died of exactly this.

**A feature is not a number. It is a claim:** *"at time t−d, in episode e, source s held value v."* Every claim is
recorded with its world, episode, source, source timestamp, output, output timestamp, lag, window bounds, context
and validity — and every recorded claim is **re-read from the episode and compared byte-for-byte**.

| | case | result |
|---|---|---|
| P1–P2 | `d < t` and `d = t` are valid | index 0 is the first sample, not the last |
| P3 | **`d = t+1` MUST RAISE** | this is the exact D-067 arithmetic |
| P4–P5 | very long delays; a sample from the future | both refused |
| P6 | numpy **does** silently wrap a negative index | `arr[10-11] = arr[-1] = 39`, not an error. This is what was trusted. |
| P7–P8 | valid rows extracted; **source samples re-read and compared** | 28 rows, all byte-equal |
| P9 | a **fabricated source value** is caught | the row claims a value the episode does not contain |
| P10 | **the D-067 defect injected** (t=3, lag=12) | the row is **excluded and counted**, not wrapped |
| P11 | a row carrying a **wrapped timestamp** | caught by the arithmetic check: `out_t − d ≠ ts` |
| P12 | short (lag 12) and **long (lag 47)** channels | the window is **extended to fit the lag**; sampling starts at `max(margin, lag)`; 0 excluded |
| P12b | starting before the history exists | excludes exactly `lag` rows, and counts them |
| P13 | a window shorter than the lag | **zero** rows, an honest count, never a fabricated one |
| P14 | a history landing exactly on the left boundary | valid, and kept |
| P15–P16 | rows may not cross **episodes** or **worlds** | concatenated storage is not a timeline |
| P17 | a clamp that **did not take** | is not evidence |

**The rule that replaced the constant.** The observation window is
`T = required_window(max_lag + MAX_HISTORY, period, settle_margin)` — sized to the widest hypothesis the observer
will **test**, not the lags it first measured. Sampling begins at `max(settle_margin, max_lag_tested)`. D-067 chose
`t ≥ 32` in advance while the far channel's lag was 47.

**Result in the prospective run: 0 fabricated rows, 0 excluded rows, on every channel, at lags up to 56.**
