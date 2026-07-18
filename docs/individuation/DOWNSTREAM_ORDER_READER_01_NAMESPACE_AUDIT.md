# DOWNSTREAM-ORDER-READER-01 — semantic seed-namespace audit

Verdict: **PASS — select `58001-58048`**. This audit initialized zero scientific engines and zero worlds.

## Semantic rule

A genuine assignment is a bounded decimal integer used by a seed manifest, family declaration, execution command,
world record, or runner. Incidental hash substrings, decimal fragments, byte counts, timestamps, line numbers and
explicit rejection tests are not assignments. This distinction matters for `58001`: it occurred only in two tests
which deliberately pass an out-of-family seed and assert refusal. Neither occurrence reserves or opens a world.

## Excluded candidates

| 48-slot candidate | Disposition |
|---|---|
| `50001-50048` | reject: `50001-50010` already-open DEV |
| `51001-51048` | reject: `51001-51012` executed; durable records exclude `51000-54120` |
| `52001-52048` | reject: `52001-52024` assigned/executed |
| `53001-53048` | reject: `53001-53032` assigned/executed and `53033-53040` historically proposed/superseded |
| `54001-54048` | reject: wholly inside executed 03G primary `54001-54050` |
| `55001-55048` | reject: `55001-55024` assigned/opened |
| `56001-56048` | reject: prior audit found bounded historical integer `56023`; do not recycle |
| `57001-57048` | reject: `57001-57024` assigned/opened |

The adjacent 03G reserve `54051-54096` remains unavailable although unexecuted, and superseded `54097-54120`
remains contaminated. They are not candidates for this 48-slot family.

## Selected namespace and proof

The ordered family is every integer from `58001` through `58048`, exactly once. Before this seal there were zero
semantic assignments and zero world records for those integers. `58002-58048` had no bounded decimal occurrence.
`58001` had only these two rejection-test additions:

- commit `8349c5592c750bf077943480bd48b0aba67925e5`, `test_mminus_order_reader_dev.py`;
- commit `f831800c5e4f3e61fc5fe8b4ce224769765d407f`,
  `test_counterfactual_history_mechanism_reconciliation.py`.

The audit covered 39 valid unique ref tips, 207 reachable commits, every object in the local Git object database,
and all 10 registered worktrees. `refs/heads/probe/tmp01` was already malformed because its file contains a warning
line before the OID. It was not changed. Its final line is the valid commit
`c8a8b354f10e0988adff4264bf0b1fdffcdf19c9`, which was included explicitly.

## Exact audit commands

Run from the isolated worktree at accepted commit `5ae98861b00f62cde78858234dd03ef4a47f549c`:

```powershell
$common = git rev-parse --git-common-dir
$brokenTip = (Get-Content -LiteralPath (Join-Path $common 'refs\heads\probe\tmp01'))[-1].Trim()
$tips = @(git for-each-ref --format='%(objectname)' refs/heads refs/remotes refs/tags 2>$null) + $brokenTip |
  Where-Object { $_ -match '^[0-9a-f]{40}$' } | Sort-Object -Unique
git rev-list $tips | Sort-Object -Unique

$re = '(^|[^0-9A-Za-z.])580(0[1-9]|[1-3][0-9]|4[0-8])([^0-9A-Za-z.]|$)'
git log $tips --format='COMMIT %H %s' -G $re -- .
foreach ($tip in $tips) { git grep -n -I -E $re $tip -- 2>$null }
git cat-file --batch-all-objects --batch

$roots = git worktree list --porcelain |
  Where-Object { $_ -like 'worktree *' } | ForEach-Object { $_.Substring(9) }
foreach ($root in $roots) { rg -n -I -e $re -- $root }

rg -n -e '50001|51001|52001|53001|54001|55001|56001|57001' `
  docs experiments --glob '*.md' --glob '*MANIFEST*.json' --glob '*.py'
```

The machine-readable record freezes the counts, classification and complete selected list. Once the manifest is
committed, future appearances of `58001-58048` are expected seal assignments and cannot be used to claim the
pre-seal namespace was contaminated.
