# SOURCE INDEPENDENCE CERTIFICATE

Correlation is not dependence; synchronization is not identity. Two registers holding the same bit have
byte-identical series in every baseline and are **two** causes. A wire and its own buffer have identical series up
to a delay and are **one**. No amount of passive observation separates these cases. Only an intervention does.

## Verdicts, and the case on which each was shown to fire

| verdict | fires on | development evidence |
|---|---|---|
| `SAME_SOURCE_DIFFERENT_TAP` | two taps whose ancestries reach one root | `dup_same`: the two duplicate taps. **Pulsing either leaves the other untouched** — they are *siblings*, not parent and child — so an intervention test on the taps alone calls them INDEPENDENT. Only ancestry sees the single cause. |
| `INDEPENDENT_SOURCES` | disjoint ancestries; each moved while the other's history is preserved | `and3`: the clock and **two registers whose baseline series are byte-identical**. |
| `DEPENDENT_COMMON_CAUSE` | ancestries overlap but are not equal | `cascade`: one tap is `AND(chan, reg)`, the other is `chan`. The first can never be 1 while the second is 0. Clamping them independently asks for a forbidden state. |
| `UNRESOLVED` | no admissible intervention separated them | fired on a synthetic world whose clamps never take. |
| `CONTEXT_CONDITIONED` | separation only under a discovered context | edges carry the contexts in which they fire; a saturated gate masks a real edge. |
| `OUT_OF_SCOPE` | reserved | not exercised in this substrate. |

**Every verdict was shown able to fire.** A classifier whose negative branch cannot be reached is not a classifier.

## The rule

A delayed copy of X is merged with X as **one source carrying several lags**. Two independent registers that happen
to hold the same bit remain **distinct**. A hidden common clock driving two channels does not merge them when each
carries its own context (`two_en`: the clock is one source at two lags; the two enables are two more sources).

Geometric proximity is **never** evidence of common source. The register that opens a gate sits nowhere near it.
