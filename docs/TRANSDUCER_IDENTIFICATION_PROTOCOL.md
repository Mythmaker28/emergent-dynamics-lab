# TRANSDUCER IDENTIFICATION PROTOCOL  (frozen; RETIRED at D-067)

## Procedure

1. **Micro causal graph** — one-step pulses, under baseline and every discovered context, unioned. Whatever differs
   one step after a pulse is a *direct* child; an indirect effect needs two. Polarity is read off the pulse itself.
2. **Candidate regions** — conductor-bounded computing clusters. **Proposals only.** They define no input, no
   arity, no truth-table axis and no equivalence.
3. **Source tracing** — every boundary tap back to its roots, recording lag and polarity. Never geometry.
4. **Independence certificate** — see `SOURCE_INDEPENDENCE_CERTIFICATE.md`.
5. **Source lags** — at which lags does each source reach the output? A held source has **no history**: its lag set
   is a single number. A varying source may enter at several lags — the same cause, remembered for different times.
6. **Reachable manifold** — see `REACHABLE_MANIFOLD_SPEC.md`.
7. **Model selection** — the *smallest* class that is **consistent**, and consistency is the whole test: if one
   source-history row ever produced two different outputs, the class is too small and is rejected.

```
STATIC             one lag per source, one shared lag
DELAYED_STATIC     one lag per source, lags differ
FINITE_HISTORY(h)  a source enters at several lags: the output depends on its past
FINITE_STATE       no lag window up to MAX_HISTORY explains it: the module remembers something itself
INDETERMINATE      the sources, the boundary or the coverage are unresolved
```

A module that *contains* a register is not thereby a state machine. `reg_delay` builds its delay out of a latch
whose write-enable is derived internally, and its interface is a **static function with a delay**. The class is
read off the **behaviour**, never off the parts.

## Quotient — five verdicts, never composited

`MICRO_ARCHITECTURE` · `SOURCE_INTERFACE` · `UNTIMED_TRANSDUCER` · `TIMED_TRANSDUCER` · `G`.

Functions are compared **only where both were observed**. Agreement everywhere observed, with rows left uncovered,
is `INDETERMINATE` — not `SAME`. A measured difference is `DIFFERENT` — not `INDETERMINATE`. False abstention is
the mirror image of false certainty and is exactly as dishonest.
