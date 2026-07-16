# Prospective authorization blocker — turnover 03G

## Status

**NOT READY — REPAIR REQUIRED.**

On 2026-07-16, the human operator supplied:

```text
I AUTHORIZE ONE PROSPECTIVE EXECUTION OF LCI-CAUSAL-TURNOVER-PRESEAL-03G FINAL_SEAL_SHA256=536cf0351bd65e6fc7efafb2d4a5acc86b99e244abe69c1bbcd8baad04022f62
```

No permission record was created, no prospective directory was created, and no seed was instantiated or executed.

## Reproduced blocker

The frozen execution manifest contains:

```text
I AUTHORIZE ONE PROSPECTIVE EXECUTION OF LCI-CAUSAL-TURNOVER-PRESEAL-03G FINAL_SEAL_SHA256=<FINAL_SEAL_SHA256>
```

`turnover_runner_03g.validate_authorization` compares `approval_phrase` to that manifest value as an exact string.
Consequently:

- the exact human phrase containing the real final-seal SHA-256 is refused with
  `authorization binding mismatch: approval_phrase`;
- the literal placeholder phrase is accepted by the validator.

Substituting the placeholder would not reproduce the operator's authorization and is therefore prohibited.

## Consequence

The current final seal cannot be used for the intended seal-hash-bound human authorization flow. The prospective
execution must remain unopened.

Repair requires a new protected manifest/runner contract that deterministically derives or expands the required
phrase using the verified final-seal SHA-256, followed by a new independent audit and new final seal. The scientific
protocol, thresholds, seed family, features, statistics, and A–F decision rules need not change.

The supplied authorization cannot be silently transferred to a repaired seal because its SHA-256 will differ. A
fresh human authorization phrase bound to the repaired final-seal SHA-256 will be required.
