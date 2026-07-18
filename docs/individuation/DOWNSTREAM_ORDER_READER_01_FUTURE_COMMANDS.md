# DOWNSTREAM-ORDER-READER-01 — exact future command templates

These commands contain placeholders only. The execution command remains prohibited until a human has reviewed this
package, audited a new namespace, inserted exactly 48 unique seeds, and changed the manifest to the separately
approved sealed state.

## Current authorized action: validate the seedless template

```powershell
$env:PYTHONUTF8='1'
$py='<PYTHON_EXE>'
$repo='<REPOSITORY_WORKTREE>'
Set-Location -LiteralPath $repo
& $py -m experiments.individuation.downstream_order_reader_prospective `
  --manifest 'docs/individuation/DOWNSTREAM_ORDER_READER_01_PROSPECTIVE_MANIFEST_TEMPLATE.json' `
  --validate-template
```

## Future only after explicit execution approval

```powershell
$env:PYTHONUTF8='1'
$py='<PYTHON_EXE>'
$repo='<REPOSITORY_WORKTREE>'
$manifest='<HUMAN_SEALED_MANIFEST_WITH_48_AUDITED_SEEDS>'
$raw='<NEW_EMPTY_RAW_OUTPUT_DIRECTORY>'
Set-Location -LiteralPath $repo
& $py -m experiments.individuation.downstream_order_reader_prospective `
  --manifest $manifest `
  --execute `
  --output-dir $raw
```

The runner refuses the supplied seedless template before it creates the output directory. Resume uses the exact
same manifest bytes and output directory; a changed manifest hash, duplicate seed, mismatched shard, or non-prefix
shard set is refused.

## Future independent raw reproduction

```powershell
$env:PYTHONUTF8='1'
$py='<PYTHON_EXE>'
$repo='<INDEPENDENT_REPRODUCTION_WORKTREE>'
$manifest='<EXACT_EXECUTED_MANIFEST>'
$raw='<READ_ONLY_RAW_OUTPUT_DIRECTORY>'
$out='<NEW_REPRODUCTION_JSON>'
Set-Location -LiteralPath $repo
& $py -m experiments.individuation.downstream_order_reader_reproduce `
  --manifest $manifest `
  --raw-dir $raw `
  --output $out
```

The reproducer reads JSON only and imports neither runner, scientific contract nor simulation engine.
