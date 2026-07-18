# EXP-SC-MCM-00 — QUANTUM RELEVANCE AUDIT (bounded)

**QUANTUM HARDWARE NOT USED.** Bounded audit only; no circuit, no shots, no hardware.

The bottleneck is a classical STORAGE-CAPACITY / write-saturation limit: the scalar write signal
Psi = tanh(...) saturates, so the two-component memory holds ~one continuous dimension plus a sign-of-order
bit in viable regimes. Adding a second read-out channel made temporal order a distinct causal axis, but a
second independent continuous dimension is simply not stored. A QPU becomes relevant only when multiple
memory modes are already present AND measurement disturbance limits access AND a quantum protocol has a
defined information-per-disturbance advantage over the optimal classical read-out. None holds: the classical
read-out is not disturbance-limited (transplant + settle reads the memory directly), and there is no
second stored mode to interrogate. A quantum computer cannot add a stored dimension the substrate lacks.
The correct next step is classical: revise the WRITING (non-saturating storage) or add recurrent plasticity.
