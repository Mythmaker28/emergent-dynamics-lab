# DOWNSTREAM-ORDER-READER-01 — code-only instrumentation qualification

Status: **PASS — INSTRUMENTATION ONLY — ZERO SCIENTIFIC WORLDS OR SEEDS**

## Implemented scope

`experiments/individuation/downstream_order_reader_instrumentation.py` adds a passive logger mixin for the frozen
diagnostic engine and qualified no-swap clamp. The override calls the inherited `_face_flux`, returns the original
live array unchanged, and retains only a separate read-only copy. It also provides pure construction and diagnostic
functions for the matched ramp, internal +x face mask, mass-specific internal face-flux sum, boundary partition and
closed-fixture first-moment identity.

No history runner, seed constant, family manifest, outcome analyzer, feeding endpoint or decision classifier was
added. No physics equation was changed.

## Revised schedule qualification

The synthetic schedule test executes:

1. one common 40-step settle at `lam_minus=0.15`;
2. two exact clones of the settled state;
3. one source-expression update at `lam_minus=0.15` versus `lam_minus=0`;
4. verification that only source-output `c` differs;
5. matched `-1/0/+1` ramps applied after source expression;
6. one common response update at `lam_minus=0.15` with exact flux logging.

This test evaluates only construction identities on a hand-built synthetic state. It does not compute a history
contrast or scientific endpoint.

## Synthetic evidence

| Fixture | Result |
|---|---|
| Base logger passivity | logged and unlogged hash both `39537c88c00a339c2d9e47f33b4578807e58f211abe90907cd1a0dda77c0128f` |
| Recorded engine axes | exact order `(-2,-1)`; arrays equal direct `_face_flux`; copies read-only |
| Qualified no-swap clamp passivity | terminal hashes identical |
| Radius-10 ramp | 317 cells; 296 internal +x faces; total addition `3.17` in each arm |
| Closed first moment | internal integral `0.49500000000000011`; moment increment `0.49500000000000005`; residual `-5.55e-17` |
| Boundary flux | internal endpoint unchanged while synthetic incoming/outgoing flux changes core mass |
| Ordinary synthetic response | paired internal response `+2.6175406501143461e-4` |
| Saturated synthetic response | paired internal response `-2.024053728781291e-6` |

The sign reversal is an expected qualification result: it proves that saturation and state can reverse the
downstream response. Positive EARLY-minus-LATE attenuation is therefore a preregistered directional hypothesis, not
a mechanical validity theorem.

## Endpoint wording

The code and documents use **mass-specific internal +x face-flux sum**:

```text
J = dt/M * sum(F_x on faces with both endpoints in K).
```

The closed fixture proves its first-moment identity only when the scored domain has zero boundary flux. The actual
radius-10 endpoint excludes boundary faces and is not called whole-body displacement or net movement. Boundary
partition values are validity diagnostics, not additional scientific endpoints.

## Margin rationale

`m_A` and `m_0` are unsealed. The superseded tentative numbers are not used by code, tests or classification.
Synthetic fixtures establish numerical fidelity but cannot determine practical scientific relevance. Any later
margin must be justified independently before scientific outcomes; `m_0` remains a secondary specificity
diagnostic and cannot invalidate the primary source-condition-by-order interaction by precedence.

## Qualification command

```powershell
$env:PYTHONUTF8='1'
$py='C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe'
& $py -m pytest experiments/individuation/test_downstream_order_reader_instrumentation.py -q
```

Focused result after the clamp-schedule revision: `7 passed in 0.82s`. The final combined instrument,
source-calibration-reader and no-swap regression is `27 passed in 5.95s`; both new files also pass `py_compile`.

## Disposition

**Instrument `QUALIFIED`; scientific preregistration `REVISE`.** No 570xx outcome, new seed, prospective family,
`BODY-EQUALIZATION`, feeding endpoint or reader battery is authorized.
