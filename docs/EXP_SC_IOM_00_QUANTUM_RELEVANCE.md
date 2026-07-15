# EXP-SC-IOM-00 — QUANTUM RELEVANCE AUDIT (bounded)

**Result: QUANTUM HARDWARE NOT USED.** Bounded relevance audit only; no circuit, no shots, no hardware.

A QPU would be relevant only if the mechanism produced a precise task involving coherent-vs-incoherent
history encoding, information-per-disturbance advantage, quantum channel discrimination, or a provable
adaptive-interrogation advantage. None arises:
- The memory is a bounded classical field with an explicit, auditable write/decay/template/diffuse rule
  and a scalar classical read-out. Its causal effect is fully captured by a low-dimensional classical model
  (net-dose read-out R2 ~ 0.95-0.97).
- There is no coherent history superposition to distinguish: the failure mode is a CLASSICAL read-out
  bottleneck (one scalar coupling), not a measurement-limited quantum encoding. The fix is classical
  physics design (more couplings), which a QPU cannot supply.
- Information-per-disturbance is already near-saturated classically by the bounded nutrient probe; no
  adaptive-measurement advantage is implied.

A quantum computer cannot manufacture individual memory absent from the substrate. Next step is classical.
