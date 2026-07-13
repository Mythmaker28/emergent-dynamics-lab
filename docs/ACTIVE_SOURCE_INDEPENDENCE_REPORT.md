# ACTIVE SOURCE INDEPENDENCE

Independence is not tabulated from a baseline. It is **sought**: the observer looks for a dissociating
intervention, and stops at the first one that works — further pulses would be waste.

> Identical time series are not proof of common source. Different time series are not proof of independence.
> Only a dissociation is proof.

| verdict | fires when | development evidence |
|---|---|---|
| `SAME_SOURCE_DIFFERENT_TAPS` | ancestries reach one root | `dup_same`: two duplicate taps. **Pulsing either leaves the other untouched** — they are siblings, not parent and child — so a tap-level intervention test calls them INDEPENDENT. Only ancestry sees the single cause. |
| `INDEPENDENT` | each moved while the other's history is preserved | `and3` / `sync3`: two registers with **byte-identical baseline series**, both causal, never merged |
| `COMMON_CAUSE` | ancestries overlap but are not equal | `cascade`: one tap is `AND(chan, reg)`, the other is `chan`; the first can never be 1 while the second is 0 |
| `DETERMINISTIC_TRANSFORM` | only one of the two can be moved alone | the write-enable and the register it loads |
| `OBSERVATIONALLY_EQUIVALENT` | no admissible intervention separates them | → `CONFOUNDED` |
| `UNRESOLVED` | ancestry reaches no root | fired on a synthetic deaf world |

**Prospective result: source identities 100 % (24/24)** against the privileged intervention-derived audit —
including the channels where the true second source is the **write-enable rail**, not the register.

The retired D-065 observer counted three boundary taps as three independent inputs. This one counts **causes**.
