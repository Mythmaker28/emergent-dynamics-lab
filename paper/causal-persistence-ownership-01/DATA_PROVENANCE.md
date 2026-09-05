# Data provenance and epistemic scope

This article is a same-data reconstruction of one recorded prospective family, followed by explicitly exploratory diagnostics. It contains no new simulated worlds and does not combine independent architectures into one sample.

## Primary family

| Artifact | Verified identity / purpose |
|---|---|
| Source snapshot | `06fd9524f5c7ffb329ee850a10bd9959f2f0bde5` |
| Prospective seal commit | `b5c0f02c02fde0bd15a288b961ffc24606199376` |
| Seal SHA-256 | `cdf7277a00e3017a1389e9334d983364b9aa0af88c646cdec2999e6ad88757fd` |
| Authorization | `c158bc0b848710edeafd425f31dfcbd5aefc0934` |
| Raw result | `9cb996bb891f9a618e593f2f5c302f30210458de`; authorization is its direct parent |
| Historical independent raw-only implementation | `a8d6446fade6dbeb984e269fab27ddd5ebf75286` |
| Raw family | `data/results/LCI-TURNOVER-PROSPECTIVE-03G/raw/seed_54001.json` through `seed_54050.json` |
| Raw manifest | `data/results/LCI-TURNOVER-PROSPECTIVE-03G/raw_manifest_03g.json` |

The 50 primary worlds yield 21 jointly valid original worlds with three targets each. There are no reserve observations. All 29 invalid worlds remain in the shipped raw files and accounting table: 17 initially ineligible, 11 split before the deep threshold, one lost before deep. None of the 21 deep-reaching worlds was then excluded for assay geometry.

The recorded order and bindings were checked against recovered Git objects. Git timestamps, author strings and an execution ledger are documentary evidence; they cannot demonstrate that an unrecorded run was impossible. The article does not make such a claim.

## Exact byte export

`INPUT_MANIFEST.json` contains 222 entries: 150 raw/protocol/provenance/historical-analysis files under `data/` and 72 files in the static and local-dynamic source import closure under `source_model/`. `scripts/prepare_inputs.py` is the one-time export recipe, using the recovered source revision. Ordinary reproduction uses only the committed export, without Git or that exporter.

Each entry gives the original repository path, source commit, byte length and SHA-256. The source closure includes all 37 files protected in the raw bindings. For 19 protected files, the historical Windows working-file hash corresponds to CRLF while the Git blob contains LF. Both relationships are verified: the source capsule keeps exact Git bytes, and the manifest explicitly records the deterministic LF-to-CRLF conversion needed to reproduce that separate working-file hash. It does not claim those two encodings have identical bytes.

Fonts have a separate `assets/fonts/MANIFEST.json` and `LICENSE_DEJAVU`. They are rendering assets, not scientific inputs. Their byte hashes and PDF glyph coverage are checked at build time.

## What “raw” means here

The JSON records contain the measured histories, feasibility fields, recorded tracer trajectories, exact deep fractions, seven scope feature matrices, and branch-specific uptake/geometry outputs. Those are sufficient to reconstruct the paper's numerical analyses. They are not a complete dump of all full-resolution spatial fields at every step. Consequently this work independently checks calculations from recorded measurements and statically documents the generating equations; it does not independently regenerate or compare every physical trajectory.

`M_i` is current mass carrying the target's own initial-mask label divided by current target mass. It is not the fraction of initial labelled mass still present, nor the fraction of all pre-existing world material. The unlabelled complement includes material initially outside the marked masks. Cross-target fractions in the sampled trajectory are not automatically measurements at the exact deep snapshot.

## Analytic independence

The historical 03M file is preserved and replayed unchanged except for a runtime input adapter from Git reads to verified local bytes. Its output retains historical wording for exact comparison; that wording is not a claim authority. The new primary script independently reconstructs causal contrasts and ridge predictions via augmented least squares. The statistician's matrix implementation and the editorial raw effect-scale check are separate calculations. They all analyze the same observations. They are not new-seed replication or independent validation of the model's constructs.

Internal agent reviews provide adversarial source and calculation checks. They share a workflow and are language-model-assisted, not external human peer review. The final ledger identifies which artifacts each reviewer actually read.

## September recovery and rejected synthesis

The user supplied `EDL_RECOVERY_20260904.bundle`, 1,106,003 bytes, with SHA-256 `8c43b31d9311fa2cb51bab9fd055c1286eafe0b091d96bcd3ec0e106d934d46f`. Git bundle verification passed. Its independent recovery root ends at `b391a73978f515e50738e8fade20c389cf131d8b`, with eight commits and a final snapshot of 263 files. It is preserved under repository `audit/edl-flagship-01/september4/` and the remote recovery ref `recovery/astra-edl-september4-verified`.

The separate adjudication recomputes CCRA01 as 17 lower, 24 higher, zero tied ordinal outcomes, one-sided exact p = 0.8944882011955997. It verifies the separate specification commit and capability examples; actual outcome blindness is unknown beyond an author declaration. Thirty of the 41 comparisons use duration to break rank ties. The ordinal test is a chosen retrospective sensitivity analysis, not a universal competing-risk repair or a mechanism-specific negative.

The 28 historical findings are individually traced to commits: 14 resolved, nine resolved with scoped limitations, F5 addressed without an exhaustive no-experiment proof, and four historical partial findings (F8 power provenance, F9 unconditional post-selection error-control wording, F24 abbreviated status strings, F28 inconsistent tree/payload byte scope). No omitted original power script or independent blindness evidence is manufactured. These residual historical claims are not adopted by this article. They remain visible in the separate adjudication and review ledger.

An error in the preceding Astra audit is explicitly corrected: two-arm runtime accounting had charged complete branches to 12 triggers that failed before any fork. Charging continuations only where archives exist yields crossing at index789 with38 pairs, total571.649363636; the earlier760/36 reproach to the checker was wrong. The corrected script and regenerated audit outputs are on this branch, with an erratum preserving the historical record.

FDFLT01 and the TBRT/OMLDCT/CCRA lineage are not the C1c memory-field population. Their endpoints do not fill the present local-access gap. The complete audit is retained in the repository but is not needed to rebuild the article's primary data or figures.

## Publication boundary

This package is for author and expert review. It has no new DOI, deposition, journal submission or acceptance. No license for the author's manuscript or data is invented here; the included DejaVu fonts retain their supplied license. The source history and exact file manifests remain the attribution/provenance record. Publication and submission decisions remain with Tommy Lepesteur.
