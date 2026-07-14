# FINGERPRINT DEVELOPMENT CERTIFICATE — **18/18**, both arms

| | case | result |
|---|---|---|
| | **[both arms] CONTINUITY: behaviourally equivalent systems are never called DIFFERENT** | 7 pairs, max distance **0.0000** |
| | **[both arms] DIFFERENCE: different function or hidden state SEPARATE** | rich min 0.0301 · droplet min 0.0602 |
| | **[both arms] the continuity and difference regions do not overlap** | a real gap in each arm |
| | **[both arms] a REDUNDANT TAP creates no fingerprint difference** (three taps, two causes) | 0.0000 |
| | **[both arms] hidden state is separated from a LATCH** — same parts, different behaviour | rich 0.3302 · droplet 0.4115 |
| | **[droplet] a SILENT system is INDETERMINATE, never matched** | a saturated gate: responsiveness 0.00 |
| | **[rich] RICH access RESCUES a system the droplet repertoire cannot interrogate at all** | responsiveness 0.00 → 0.08 |
| **C1** | systems distinguishable under RICH access are INDISTINGUISHABLE under the droplet repertoire | 4/4 |
| **C2** | **FALSE SAMENESS INCREASES as access gets poorer** — measured, not assumed | collisions: rich 0/4, droplet **4/4** |
| **E1** | function-preserving **replacement during one continuous trajectory**: behaviour uninterrupted | identical before the swap; bounded transient 14 steps |
| **E1** | the fingerprint **survives the replacement** | pre/post distance **0.0000** |
| **L1** | **MUST-FAIL:** re-adding the class label and lag set **RECREATES the false difference** (D-069) | clean 0.0000 → contaminated **0.0612** |
| **L2** | **MUST-FAIL:** removing the discriminating probe **COLLAPSES two different systems into one fingerprint** | with the register step 0.0347 → without it **0.0000** |

**L1 proves the exclusion of description-level quantities is load-bearing.** **L2 proves probe-repertoire adequacy
is load-bearing.** Neither is an assumption; both are demonstrated by making them fail on purpose.

## Four defects development caught, each of which would have been a false result

1. **Deviation-only fingerprints are blind to output inversion.** d(AND, XOR) = 0.0000 — a false sameness.
2. **Zero-padding made latency into a difference.** d = 0.0946 between a channel and its own lengthened twin.
3. **The rich battery's length depended on the system.** A machine with a second register got an extra probe — a
   coordinate system with a variable number of axes.
4. **A response still in flight was recorded as permanent.** The 32-step window was shorter than the far channel's
   own latency, so "still responding" was read as "changed forever" — the memory signature contaminated by
   impatience, which is D-067's error arriving from the other end of the trace.

## And one benchmark-label correction, made before the freeze

`xor3` (the D-069 redundant-lag system) and `fsm_gate` (a gated state machine) **are** separable under rich access:
`xor3`'s reconvergent paths **glitch** on a register step, and `fsm_gate` **freezes** where `toggle` does not.
These are measured responses, not labels. **The benchmark was wrong; the measurement was not.** The matrix was
corrected on development, before the freeze, with a stated principle: **equivalence is relative to a repertoire.**
