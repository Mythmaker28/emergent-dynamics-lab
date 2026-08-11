# FCDDH01R start budget and lineage ledger

```
FCDDH00_HISTORICAL_CHARGED_STARTS      = 108   (permanently charged to the closed parent)
FCDDH00_UNUSED_PERMISSIONS             = expired with that authorization; neither transferred nor data
FCDDH01R_CHILD_MAXIMUM_CHARGED_STARTS  = 672
FCDDH00_PLUS_FCDDH01R_LINEAGE_MAXIMUM  = 780
```

Per-phase maxima, planning rules, setup accounting, raw-advance accounting and the "charge the
larger count" convention are inherited exactly: discovery 96/96/96, hold-out 128/128/128.

```
OTHER_REAL_ENGINE_STARTS_AUTHORIZED       = 0
DIAGNOSTIC_REAL_ENGINE_STARTS_AUTHORIZED  = 0
TIMING_REAL_ENGINE_STARTS_AUTHORIZED      = 0
SMOKE_TEST_REAL_ENGINE_STARTS_AUTHORIZED  = 0
PREFLIGHT_ENGINE_STARTS_AUTHORIZED        = 0
```

Every durability validation was dummy-only. Static runner audit (unchanged from the parent):
`C_PRECURSOR_ADVANCE = 0`, `C_BLOCK_MAX = 4`, `C_SETUP_D = C_SETUP_H = 0`,
`N_D_ATTEMPT = 24 >= 12`, `N_H_ATTEMPT = 32 >= 16`.

Namespace `N = 73000`; discovery candidates 73000–73023,
hold-out candidates 73024–73055.
smallest N >= 72000 divisible by 1000 whose whole 56-seed interval is absent from every used, reserved, generated, opened and exposed namespace. 72000 was REJECTED because the FCDDH00 closure report itself exposed 'N >= 72000' as the recommended next namespace; N was increased by exactly 1000 as the rule prescribes. 73000-73055 occurs in no seed-declaring context and in no filename across any branch tip.
