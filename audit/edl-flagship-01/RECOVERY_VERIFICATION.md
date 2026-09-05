# Recovery verification

> **Statut historique, remplacé pour la livraison PAPER-01.** Le bundle du 4 septembre a depuis été récupéré, vérifié et adjudiqué. Voir [le rapport de septembre](september4_adjudication/SEPTEMBER4_ADJUDICATION_FR.md) et [l’article livré](../../paper/causal-persistence-ownership-01/README.md). Les demandes de bundle et états non vérifiés ci-dessous ne décrivent plus le dossier courant.

Status: **RECOVERY_VERIFIED for the recovered August history and named raw evidence; SEPTEMBER_4_PACKAGE_NOT_LOCATED**.

Source repository `C:\Users\tommy\Documents\ising-v3-recovery\ising v3` was inspected and left untouched. Its main was `f3921a4d`, with 19 historical Windows-invalid missing cache paths and untracked recovery/experiment residue. No dirty sibling was repaired, reset, cleaned, or merged. The current audit uses owned bare repository `C:\Users\tommy\Documents\edl-astra-flagship-audit-01-repository.git` and isolated worktree `C:\Users\tommy\Documents\edl-astra-flagship-audit-01`.

The new recovery history branch `recovery/astra-edl-history-20260905` publishes `5372fd86ba98b5b21a50143ca9c36b25d191daac` unchanged. The recovery-with-raw branch `recovery/astra-edl-tbrt02-20260905` publishes `2422492d13fa5e333d4d3111e9ca95de2d7cc9b7`. The audit branch descends from that checkpoint. No main, PR34, persistence branch, or historical freeze is modified. The recovery history was published before analysis changes; transfer of the additional raw checkpoint completed while independent, non-mutating analyses were prepared. The initial 503 MiB push timed out HTTP 408; retry using HTTP/1.1 and a 1 GiB request buffer succeeded. Both remote tips were read back.

## Search boundary and missing source

Searched local Downloads, Desktop, Documents, then filenames under the user profile with large dependency/cache directories excluded; searched targeted attachment and download contents, inventoried 129 local bundle headers, remote branches, reachable source objects, the preceding Codex task “Audit terrain Codex”, and connected Drive queries. No `EDL_STATE.b64.txt`, announced September-4 bundle, CCRA01 files, nonexchangeability manuscript, or September-4 findings document was located. The preceding task quotes the report but contains no accessible binary attachment or download URL for these files. This establishes **not located in searched sources**, not global nonexistence. No Claude native app control was available.

One requested source remains: `Edl recovery 20260904.bundle`, announced SHA-256 `8c43b31d9311fa2cb51bab9fd055c1286eafe0b091d96bcd3ec0e106d934d46f`, branch `recovery/edl-state-20260904`, abbreviated tip `b391a739`. Its claimed strict base64/gzip/tar, 246-file completeness and 28 findings cannot be verified without the bytes.

## Actually recovered input

| Input | SHA-256 / binding | Verification |
|---|---|---|
| TBRT02_INCREMENT.bundle, 3,187,496 bytes | `7199a4603e8e387ca50326e5e270f852b6e291a8d182d6c65ee5a844f31c2541` | Hash before import; Git bundle verify; tip 5372fd86, prerequisite 06c5923. This is not the Sept-4 bundle. |
| 41 TRIPLE tar archives | each outer/member hash in EXTRACTION_MANIFEST.json | 123 NPZ, 41 unique admissible seeds, all sealed ledger hashes match. |
| FDFLT01_RAW_CORE.tar.zst, 92,229,211 bytes | `936fac7c7d61df1a1bedf2d94e5e933930aa55f66de2e057e41202b467f04467` | Outer hash matches historical durability/sidecar; 192 result-bearing NPZ; member hashes preserved. |
| FDFLT01 pre-run capsule | `ec550be75428dbc5d257cfc980a33fe3d55887b6ab811992d717738a1bd1859b` | Matches sidecar and all 28 module/data hashes. The durability JSON contains a different, erroneous hash. |
| FDFLT01_PRE_RUN_FULL.bundle | `af4f9d6c799eb412160495c06b80f9ffac6cb22974afe0e81feb364ac6426b3b` | Local file hashed; pre-run freeze/source already present in recovered ancestry. |
| Candidate B snapshot | 06fd9524f5c7ffb329ee850a10bd9959f2f0bde5 | 191 exact Git-source files with per-file manifest; 50 raw records match their historical hashes. |

45 local archives were safely listed/extracted into new quarantine directories, producing 375 files. Absolute/parent traversal, drive-qualified/backslash names, duplicate case-folded paths, links and special member types were rejected by the extraction helper. For zstd archives, Windows bsdtar listing/type inspection preceded extraction; this was not a strict base64/gzip check. See session-specific helper and complete manifests under `recovery`. Two pyc files in a historical capsule are preserved as archive evidence and are never executed.

## Exact methods formulas

TBRT02 uses a **dictionary**, not `methods_hash()`'s generic ordered-list helper:

```python
files = {relative_posix_path: sha256(file_bytes) for each of 17 METHOD paths}
METHODS_HASH = sha256(json.dumps(files, sort_keys=True,
    separators=(',', ':'), ensure_ascii=True).encode('utf-8'))
```

No appended newline. Result: `21571fb4cb1df9ac2e9089924e9d6ee5d4d63c920a007e188bdc24e0d94d1f99`. Verified first from recovered method files, then independently from the exact 5372fd86 Git blobs, bypassing sparse-checkout/EOL effects. All seven TBRT02/out sidecar hashes pass. Connectivity is 1,186 bytes but zero records and zero covered triples; it cannot support an exposure finding.

FDFLT01 hashes the newline-joined `sha256 absolute_path` module list sorted by absolute path, then a newline and the similarly sorted data list, then `\npython=<frozen version>\n` plus `json.dumps(frozen_packages, sort_keys=True)`. Frozen runtime metadata are inputs to this historic hash, not a claim that the current runtime is identical. Result: `d403ccd3976be5ceabd167bfe21750ce08782a52aa0dc6e7019a226fcef24759`; all 20 modules and 8 data files match in the capsule.

## Provenance limits

- 114 TBRT02 archives are documented as transferred originals. Nine archives at indices 793, 827, 866 were historically reconstructed from the same already-counted seeds and accepted against pre-existing sealed hashes. Current verification confirms the matching bytes; it does not independently witness that historical execution or create independent-seed replication.
- FDFLT01 core retains all endpoint arrays, X at every recorded step and final fields. Five non-X intermediate field planes are not recovered. The original full 192-file manifest totals 1,166,057,316 bytes; its hashes are not hashes of the reduced core. Do not mark that full package recovered.
- Git ancestry/timestamps and matching runtime bindings support the recorded prospective sequence. They do not establish an agent's cognitive blinding or prove that no unrecorded analysis occurred elsewhere.
- Reanalysis of a fixed sample, deterministic reconstruction of the same seeds, independent-seed experimental replication, and external validation are four different claims. Only the first two historical categories are relevant here. Current audit ran zero new worlds.

## Divergent histories

See `results/SOURCE_VERIFICATION.json` for full hashes. Relative to recovered 5372fd86: main has 199 unique commits versus 266 recovered; B has 51 versus 266; PR34 has 4 versus 161, sharing 06c5923; 99b8044 is an ancestor with 117 later recovered commits. These counts describe Git history, not scientific merit. No mechanical merge was performed.

The owned Windows sparse checkout produced a stale zero-byte sparse-checkout lock during materialization; it was inventoried and moved to external staging only after confirming no sparse-checkout process existed. Subsequent canonical source checks use Git blobs. Original repository malformed refs and invalid paths remain preserved.
