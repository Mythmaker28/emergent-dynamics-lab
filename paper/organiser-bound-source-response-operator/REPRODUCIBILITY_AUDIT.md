# Reproducibility audit — manuscript V2, 4 September 2026

This is an executed reconstruction of an English manuscript and its figures, not a proposal for later auditing. Its review status is calculated in provenance/PAPER_SUBMISSION_READINESS.json after the checks below. Audit and editing were conducted in the same Astra task; no independent reviewer is claimed.

## Source recovery

The source-response programmes are recovered at FLCR01 tip 06c592313df96601de8d2a89676d5a5cf79fc414 from ISING_LIFE_AUTHORITATIVE_FULL.bundle. The older, dirty ising-life-lab checkout is a different 2025 line and was preserved. The delivered LRCPS01 paper was committed before revision at 0a872ac. No later V2 was located. The separate EXP-SC-IOM-00 report, erratum and freeze manifest were copied from 4282fc6ead915639711f5096c7825d3880a640d4; no data were pooled across architectures.

The isolated task checkout uses sparse materialization because 19 historical cache paths contain Windows-invalid vertical bars. It retains the original scientific Git tree, 4c18778b2f352c6eca2a8e73a07576b1c2ffd0db. Raw arrays and programme methods were materialized from exact Git bytes, including their original line endings. SOURCE_MANIFEST.json pins 482 inputs by size, SHA-256 and Git blob. The audit verifies rather than rewrites this input manifest.

The existing remote is Mythmaker28/emergent-dynamics-lab. Its inspected current branch is not a descendant of the recovered FLCR01 tip. A separate archive base at that exact tip keeps the draft PR's diff confined to manuscript restoration/revision and the task records. Neither remote main nor another dirty checkout is changed.

## Executed checks

| Check | Executed result | Evidence |
|---|---|---|
| Pinned inputs | 482 files: size and SHA-256 match | SOURCE_MANIFEST.json; AUDIT_RESULTS.json |
| Freeze chronology | Freeze 050e666 precedes first raw commit 0148acc; fourteen method blobs unchanged at recovered tip | GIT_FREEZE_VERIFICATION.json |
| Fresh allocation | 28 archives; 14 static + 14 mobile; unique disjoint seeds, no retired seed reused | audit_final.py; FRESH_ARM_RECOMPUTATION.csv |
| Array structure | Each series 11000 x 29; hop ledger 44000 x 4; source ledger 44000 x 6; birth ledger 11000 x 6; final lattices 36 x 36 | audit_final.py |
| Frames | 220 ordered frames per arm; 180 post-burn frames each, 5040 in analysis | AUDIT_RESULTS.json |
| Arm results | Medians, means, within-arm SD, mean population, rejected-hop fractions agree; no excluded fresh arm | FRESH_ARM_RECOMPUTATION.csv |
| Final states | All six species' final-state digests checked for 28 arms; final source count and final radius independently recomputed | audit_final.py |
| Historical selection | 147 archives read; nested mobile counts 116 / 126 / 129 and their residuals/SE agree | HISTORICAL_ARM_RECOMPUTATION.csv; AUDIT_RESULTS.json |
| Historical baseline | Static n=3, mobile n=41; means, ratio and all three fresh relative errors recomputed | AUDIT_RESULTS.json |
| Predictor diagnostics | Four stored arrays of 16 replica means checked; empirical-minus-Poisson difference and SE agree | AUDIT_RESULTS.json |
| PQEC external raw | 128 files; 1,004,089,434 bytes; all original sizes, hashes and key sets verified; array shapes inventoried | PQEC01_EXTERNAL_RAW_AUDIT.json |
| Claims and numbers | 36 major claim bindings; 48 source-bound numerical rows; four figure source/hash bindings; three cited references | PAPER_CLAIM_LINT.json |
| Tests | Four tests passed: missing, resized and same-size-corrupt source rejection; discrete periodic quantile at translated seam | TEST_RESULTS.xml; code/test_audit.py |
| PDF build and QA | Both documents compile; text/log checks and all-page visual inspection bind to exact PDFs | PDF_QA.json; VISUAL_QA.json |
| Portability | Extracted review tree builds without Git; regenerated deterministic assets match original hashes; four tests pass there | STANDALONE_REBUILD.json |

Paths in this table without a directory prefix are under provenance. Exact commands are in README.md and COMMANDS_EXECUTED.md. No simulation engine, new predictor sampler, paid API or campaign was invoked.

## Recomputed primary results

| Endpoint | Frozen prediction | Fresh observation | Relative deviation |
|---|---:|---:|---:|
| Static radius | 6.007630361527475 | 5.999119238860436 | -0.1416718765113% |
| Mobile radius | 8.057449850229872 | 8.077146148389195 | +0.2444482873047% |
| Mobile/static | 1.3412026648359268 | 1.3463886658674735 | +0.3866679635759% |

All three pass the frozen +/-2.9% point rule. The historical-copy baseline also passes, so agreement alone has limited mechanistic discrimination. The literal sealed label is CONDITIONAL_FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED; the paper explains its bounded meaning and does not claim full-capacity exactness.

## Corrections made in V2

The measured historical birth flux is now explicit conditioning information. The shared source path is simulated by the predictor before fresh runs, not copied from a fresh run. Greater Poisson prediction distance is no longer treated as rejection: that variant passes the same tolerance. The prior large birth-flux-shape attribution and factorial decomposition are withdrawn; existing replicated estimates reverse its sign and reduce its magnitude (difference +0.414424 percentage points, SE 0.196296).

The historical residual is reported with outcome-dependent inclusion and all three nested sensitivity levels. The widest row still requires a final source and a finite radius; the historical key claiming no outcome-dependent threshold at all is explicitly corrected in prose. A first-crossing statistic does not supply a general proof of downward bias.

Interval rules and t-based equivalence diagnostics remain post-freeze, not newly claimed confirmatory successes. Predictor MC dispersion is displayed separately. A small diagnostic ratio-SE scale error is corrected by retaining the observed/predicted factor (about 0.863% instead of 0.859%); no frozen point conclusion changes.

The original 213-row numerical inventory is replaced by 48 current bindings. Its unused assertions, strategy documents and legacy paper build scripts are removed from the current package, preserving their bytes in Git 0a872ac. The replacement scripts share the original entry point names where useful. This avoids exposing stale positive claims as current submission guidance.

## Limits and status boundaries

This verifies stored raw summaries and reconstructs each final-lattice radius. Full intermediate lattice states are absent, so per-frame radii cannot all be independently reconstructed from occupancy. The archived 1500-step observer-inertness fixture is source-bound, not rerun or generalized. The historical reference kernel reproduces its frozen implementation; no new exactness theorem is asserted.

PQEC provenance does not restore a lost holdout: all 128 worlds retain post-outcome developmental status. FLCR01 supports a lineage criterion while leaving the operator unidentified; founder rejection is not reproduction. MYQBD01 still lacks the full descendant environment. EXP-SC-IOM-00 remains documentary context with INDIVIDUATION FAIL and its high-dimensional-storage interpretation reduced by the erratum. Reproduction/heredity are NOT TESTED here; autonomous cohesion and biological individuality are NOT ESTABLISHED.

The governing historical run-budget authorization remains UNKNOWN from the delivered evidence. The current mission explicitly authorizes this zero-campaign revision. Closed scientific routes remain closed. No independent full-engine replication, parameter generalization, originality/plagiarism certification, peer review, journal formatting, publication, deposition, DOI or merge is claimed. No external scientific communication is performed other than the explicitly authorized Git branch/draft-PR workflow.
