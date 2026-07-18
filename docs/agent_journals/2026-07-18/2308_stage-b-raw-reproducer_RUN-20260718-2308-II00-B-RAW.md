# Stage-B independent raw-only reproducer journal

- Role: independent Stage-B raw-only reproducer
- Run ID: `RUN-20260718-2308-II00-B-RAW`
- Start time: `2026-07-18 23:08:01 +02:00`
- End time: `2026-07-18 23:08:58 +02:00` (preregistration turn complete; reproduction not started)
- Starting Git branch: `codex/interventional-individuality-00-stage-b`
- Starting Git state: no short-status entries observed at journal creation
- Assigned scope: preregister an independent raw-only reproduction contract before any Stage-B DEV output exists; do not implement or inspect/init a world until the committed B1 manifest and raw schema are sealed and supplied.

## Immutable source firewall

Before raw reproduction begins, the reproducer may read only:

1. the exact committed B1 manifest named by the parent agent;
2. the exact committed raw schema named by that manifest; and
3. every raw world shard enrolled by that manifest, plus the manifest-declared hash inventory needed to verify them.

The reproducer must not read or import:

- `engine.py`;
- `instrumentation.py`;
- `stage_b.py` or any production/online runner;
- online classification code or generated online classifications;
- the Stage-B report or atlas;
- any candidate, picked-world, shortlist, representative-world, or visualization list;
- historical checkpoints, scientific result files, prior DEV worlds, seeds, or source worlds;
- any file outside the committed B1 manifest/schema/raw-shard allowlist except this journal and the reproducer implementation/output paths explicitly added to the allowlist before execution.

This firewall is semantic as well as path-based: copied extracts, cached values, summaries, screenshots, logs, comments, or messages conveying forbidden online outcomes are also forbidden. The parent may provide only the sealed commit identifiers and exact allowed paths/hashes, not scientific signs or candidate hints.

## Frozen independent algorithm obligations

The reproducer will be implemented independently from the raw schema and mathematical definitions frozen in the B1 manifest. It will not copy, import, dynamically call, or translate the production classifier implementation.

It must:

1. reject any manifest or schema whose committed bytes or declared hashes do not match the supplied seal;
2. enumerate the complete enrolled world set from the manifest, never from directory discovery or a selected list;
3. verify that every enrolled shard exists exactly once, has the declared byte hash, carries the declared world identity and neutral initial-condition class, and contains the complete declared frame/horizon coverage;
4. reject duplicate, missing, extra, truncated, non-finite, malformed, out-of-order, or schema-incompatible raw records;
5. derive per-track and per-world quantities only from raw numerical records using the frozen thresholds, chronology, boundary conventions, tolerances, and precedence encoded in the committed B1 manifest/schema;
6. reproduce all nine regime classes literally and exhaustively: the class identifiers, precedence, gates, and tie handling will be read from the sealed manifest and may not be renamed, merged, split, reordered, or inferred from online output;
7. assign exactly one of the nine classes to each enrolled world or fail closed;
8. reproduce complete region aggregation from the manifest-declared law-family coordinates and region bins, including counts for all nine classes, denominators, neutral-initial-condition strata, and any manifest-required marginal totals; no post hoc binning, smoothing, dropping, or empty-bin suppression is permitted;
9. preserve exact non-candidate and failed-world records and never select surviving subsets;
10. emit a machine-readable reproduction result containing input hashes, complete world-level classifications, complete region aggregates, invariant-check results, and deterministic serialization metadata.

No intervention, cut, conductance response, memory test, reproduction test, parameter adaptation, threshold relaxation, or scientific-world initialization is permitted in this task.

## Determinism and two-run byte identity

After implementation, the independent reproducer must be executed twice from the same sealed inputs in fresh output locations/processes. Canonical machine-readable outputs must be byte-identical. Ordering, numeric formatting, newline convention, and serialization must be explicitly fixed before the first run. The two output SHA-256 hashes and byte counts must be recorded here. A mismatch is binding and cannot be resolved by choosing one run.

## Preregistered kill switches

Stop reproduction and return a failed independent-qualification disposition to the parent if any of the following occurs:

- the committed B1 manifest or raw schema was not sealed before the first DEV world was initialized;
- any allowed input hash differs from its committed/declarative hash;
- the parent cannot provide an exact finite allowlist of manifest, schema, raw shards, reproducer paths, and output paths;
- any forbidden file or forbidden outcome-bearing information is opened, imported, received, or cached;
- the reproducer requires production engine, instrumentation, runner, classifier, report, atlas, or picked-world logic to compute a result;
- enrolled-world enumeration depends on filesystem discovery, online success, a shortlist, a visualization, or survival filtering;
- an enrolled raw shard is missing, extra, duplicated, truncated, malformed, non-finite, out of order, hash-mismatched, or inconsistent with declared identity/IC/horizon metadata;
- the raw schema is insufficient to reconstruct any mandatory gate, one of the exact nine regime classes, or the complete declared region aggregation without assumptions;
- a threshold, precedence rule, tolerance, coordinate, region boundary, empty-bin rule, or class identifier is ambiguous after sealing;
- the independent algorithm cannot assign exactly one frozen class to every enrolled world;
- any result requires post hoc threshold changes, fixture tuning, parameter-region changes, subset selection, or preferred-sign reasoning;
- raw-derived conservation, boundary-work, tracker, chronology, or accounting identities required by the manifest fail;
- the two fresh executions are not byte-identical;
- the independent world-level or region-level result disagrees with the sealed production result when comparison is finally authorized, with neither implementation privileged to resolve the discrepancy.

No disagreement or kill switch authorizes inspecting scientific outcomes to repair the method, replacing failed worlds, expanding the family, or continuing to a later scientific stage.

## Actions and evidence so far

- OBSERVED: this journal was preregistered before the reproducer received a B1 manifest, raw schema, or any DEV output.
- OBSERVED: only repository identity/status and wall-clock time were queried before this journal was written.
- INFERRED: no raw reproduction can begin until the parent supplies a committed seal and exact allowlist.
- HYPOTHESIS: the sealed raw schema will be sufficient for a genuinely independent reconstruction of every gate and all nine classes.
- WHAT WOULD FALSIFY THIS?: any mandatory derived quantity, class decision, or region aggregate requiring forbidden implementation knowledge or an unstated convention.
- Failures/dead ends: none yet.
- Decisions: fail closed on incomplete enrollment, insufficient raw observability, ambiguity, firewall breach, nondeterminism, or disagreement.
- Unresolved risks: the B1 manifest/schema and permitted reproducer paths do not yet exist in the information available to this role.

## Files read or changed

- Read: no scientific source, manifest, schema, result, raw shard, report, or atlas.
- Changed: this journal only.

## Reproducible commands executed

```powershell
$pwd.Path
git branch --show-current
git rev-parse --show-toplevel
git status --short
Get-Date -Format 'yyyy-MM-dd HH:mm:ss K'
Get-Date -Format 'HHmm'
```

## Handoff

Await the exact committed B1 manifest/schema seal and a finite source allowlist. Until then, do not implement the reproducer, inspect any raw output, or initialize any world.

- Ending Git branch: `codex/interventional-individuality-00-stage-b`
- Ending Git state for assigned scope: this journal is the sole new file created by this role; parent-owned concurrent changes were not inspected.
