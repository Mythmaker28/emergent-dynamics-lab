# DOTC01 — IS THE CURRENT ARCHITECTURE CAPABLE?

does the current state space and transition law admit ANY regime in which a daughter forms, stays nonempty, gains a constituent, loses a constituent, keeps producing X locally, and does not proliferate out of control?

## The answer does not need a feasibility bound

> the question does not need a feasibility argument at all, because the phenomenon has ALREADY OCCURRED. Four centres in the surviving PQEC01 B1 set complete a constituent turnover inside one continuous identity interval, and three of them keep producing X locally on both sides of the removal. An existence proof by observation supersedes any bound.

| Structural requirement | Status |
|---|---|
| a mechanism for local replenishment INSIDE an existing centre | **PRESENT** |
| co-located Y can form a persistent multi-constituent centre under the scheduler | **PRESENT** |
| a removal rate that produces turnover without forcing extinction first | **PRESENT AT B1** |
| a birth rate high enough for replacement without uncontrolled new centres | **PRESENT AT B1** |
| local X function survives the removal | **OBSERVED** |

- **PRESENT** — the Y birth branch of _react_core fires only at cells with nY > 0, so every newborn Y is co-located with an existing constituent and lands inside that centre by construction. The engine's replenishment mechanism is intrinsically intra-centre.
- **PRESENT** — observed max N_Y in one centre reached 3; single-linkage at CORE_R = 5.0 keeps co-located and near constituents in one component
- **PRESENT AT B1** — birth and death hazards at B1 are of the same order — mean local birth hazard 8.680e-05 per step against muY = 9.261e-05, ratio 0.9373 — so neither swamps the other. The exact chain gives P(complete turnover by horizon) = 0.11664 against P(extinct before turnover) = 0.25524.
- **PRESENT AT B1** — PREMATURE_THIRD_CENTRE accounts for 0.1591 of B1 stops, so proliferation is present but bounded, and 28 of 44 worlds never exceeded one centre.
- **OBSERVED** — 3 of 4 turnover centres record exact X births at their own cells on both sides of the removal

## The four canonical conflicts

- *birth rate high enough for replacement always causes uncontrolled new centres* → **REFUTED BY OBSERVATION — replacement occurred at B1 while 28 of 44 worlds never exceeded one centre**
- *death rate high enough to create turnover always causes extinction before replacement* → **REFUTED BY OBSERVATION — 4 centres completed turnover; 3 kept producing afterwards for 99, 217 and 5644 further steps**
- *co-located Y cannot form a persistent multi-constituent centre under the scheduler* → **REFUTED BY OBSERVATION — N_Y reached 2 and 3 inside single components**
- *the engine has no mechanism for local replenishment inside an existing centre* → **REFUTED STRUCTURALLY — Y birth is Y-gated and therefore intrinsically intra-centre**

```
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
```

the standard requires a PROOF that the current state variables and transition laws cannot support a continuously functioning centre through constituent turnover. The opposite has been observed. No architecture change is proposed, considered or implied.

`NEW_PARAMETER_DESIGN_REQUIRED = False`. §12 asks for a new design only if NO existing point can produce constituent turnover. B1 produces it. No sweep, no interpolation, no new point.
