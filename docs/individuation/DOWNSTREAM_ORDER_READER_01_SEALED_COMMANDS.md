# DOWNSTREAM-ORDER-READER-01 — exact sealed commands

These commands are bound to the immutable manifest. Only the verifier is authorized now. The prospective command
is recorded for review but must not be invoked until a new explicit human execution authorization has been saved
outside the repository at the exact path below.

## Authorized seal verification

```powershell
$env:PYTHONUTF8='1'
$repo='C:\Users\tommy\Documents\ising-v3-downstream-order-reader-seal-00'
$py='C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe'
Set-Location -LiteralPath $repo
& $py -m experiments.individuation.downstream_order_reader_verify_seal `
  --manifest 'docs/individuation/DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_MANIFEST.json'
```

## Prohibited until a new explicit human authorization

The external file must be exactly one JSON object with only these fields:

```json
{
  "approval_phrase": "AUTHORIZE DOWNSTREAM-ORDER-READER-01 PROSPECTIVE EXECUTION MANIFEST-SHA256={manifest_sha256}",
  "manifest_sha256": "the lowercase SHA-256 of the immutable manifest bytes",
  "schema": "DOWNSTREAM-ORDER-READER-01-EXECUTION-AUTHORIZATION-v1",
  "status": "APPROVED_FOR_EXECUTION"
}
```

`{manifest_sha256}` is a runtime format token, not an authorization and not a seed placeholder. It must be replaced
by the exact lowercase manifest hash in both fields only after the requested human decision.

```powershell
$env:PYTHONUTF8='1'
$repo='C:\Users\tommy\Documents\ising-v3-downstream-order-reader-seal-00'
$py='C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe'
$manifest='docs/individuation/DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_MANIFEST.json'
$authorization='C:\Users\tommy\Documents\DOWNSTREAM_ORDER_READER_01_EXECUTION_AUTHORIZATION.json'
$output='results/DOWNSTREAM-ORDER-READER-01-PROSPECTIVE-001'
Set-Location -LiteralPath $repo
& $py -m experiments.individuation.downstream_order_reader_prospective `
  --manifest $manifest `
  --authorization $authorization `
  --execute `
  --output-dir $output
```

The initial command refuses an existing output path. A crash-recovery resume, if operationally required, uses the
same manifest, authorization and output path plus `--resume`; it accepts only the exact ordered prefix and does not
extend, replace or duplicate a world. It is not an outcome-triggered scientific stop or extension.
