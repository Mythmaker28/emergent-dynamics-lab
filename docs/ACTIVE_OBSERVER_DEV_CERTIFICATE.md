# ACTIVE OBSERVER — DEVELOPMENT CERTIFICATE (`EXP-GT-ACTIVE`, **15/15**)

**45 transducers: 15 worlds × 3 channels. Exactly 15 per channel.** The certificate that missed D-067 inspected
channel 0 of three — the only channel where its defect could not fire. It was not a certificate; it was a
demonstration with a denominator problem.

| | case | result |
|---|---|---|
| A1 | the **D-067 failure does not recur** on any channel of a plain AND | ch0 (lag 12), ch1 (lag 26), ch2 (lag 40): all `IDENTIFIED / DELAYED_STATIC` |
| A2 | a **long path behaves identically to a short path** once adequate history is supplied | lag 12 vs 40, identical table and class, **0 rows excluded** |
| A3 | hidden state claimed **only** on the true state machine | `FINITE_STATE` on `toggle` ×3 and nowhere else |
| A4 | duplicated taps collapse to one source, on every channel | `dup_same`: 3 taps → 2 sources, ×3 |
| A5 | source identities match the **privileged audit** (which now counts the write-enable) | **45/45** |
| A6 | three sources on `and3`/`sync3`, incl. two registers with identical baseline series | 3, 3, 3, 3, 3, 3 |
| A7 | partial manifold → `EQUIVALENCE_CLASS_ONLY` | `lag8_*`: coverage 0.5 |
| A8 | the off-manifold twins have **identical observed tables** and are not separated | agreement, not identification |
| A9 | history recovered where it is required | `dup_lag`, `edge_xor`, `tri_tap` → `FINITE_HISTORY` |
| A10 | a module built **out of state** is not a state machine at its interface | `reg_delay` → `DELAYED_STATIC` |
| A11 | **no false certainty** | 36 identified with a table, 0 with wrong sources |
| A12 | the **plan is a function of the world** | 6 distinct exploration plans across 15 worlds |
| A13 | cost: fewer questions than exhaustive tomography | **150 / 306 episodes (49 %)** |
| A14 | coverage spans every channel, lag band, class, manifold type, source count | channels {0,1,2}; bands short/medium/**long**; classes DELAYED_STATIC / FINITE_HISTORY / FINITE_STATE; manifold full **and** partial; sources 1–3 |
| A15 | **no channel dominates qualification** | 45 transducers, **15 per channel** |

Prerequisite: `EXP-GT-PROV` (temporal provenance) **20/20**, passed before this observer existed.

**And it still failed prospectively** — on model minimality, a question no case above asks. A development
certificate can only refute the errors you have thought of.
