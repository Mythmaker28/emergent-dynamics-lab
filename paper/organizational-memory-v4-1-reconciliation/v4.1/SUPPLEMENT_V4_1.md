# Supplement V4.1

## Original-world grouped statistical and artifact audit

This supplement accompanies **“Organizational-memory claims under
original-world grouped validation: a V4.1 reconciliation.”** It reports methods,
sample sizes, fold definitions, audit findings, and numerical dispositions in
greater detail. No new simulation was run.

## S1. Canonical-source chain

The exact V4.0 source is Git commit
`23b53aee4169deeda30aad2a9dba8587024f8d3d`, subject
`CANONICAL-REANALYSIS-V4: adopt committed reproducible headline numbers`.
The release manifest is
`v4.0/canonical/release/RELEASE_MANIFEST_V4.json`.

The canonical primary objects are:

| Object | Canonical path |
|---|---|
| Manuscript source | `docs/paper/full/ORGANIZATIONAL_MEMORY_FULL_MANUSCRIPT_V4.tex` |
| Manuscript PDF | `docs/paper/full/ORGANIZATIONAL_MEMORY_FULL_MANUSCRIPT_V4.pdf` |
| Supplement source | `docs/paper/full/SUPPLEMENT_V4.tex` |
| Supplement PDF | `docs/paper/full/SUPPLEMENT_V4.pdf` |
| Claim ledger | `docs/paper/full/CLAIM_LEDGER_V4.md` |
| Statistical re-audit | `docs/paper/full/STATISTICAL_REAUDIT_V4.md` |
| Reproduction package | `reproduction/` |
| Longitudinal raw data | `results/observer/tca_holdout_raw.pkl` |

All 37 release-manifest files verify byte-for-byte against their declared
SHA-256 hashes. V4.0 is not edited by V4.1.

## S2. Analysis units and sample sizes

### S2.1 Primary longitudinal artifact

- rows: n=36 at each checkpoint;
- original worlds: W=3, seeds 38502–38504;
- imposed histories: H=12;
- rows per world: 12;
- checkpoints: initial, moderate, deep-1, and deep;
- outer group: original world / simulation seed;
- response coordinates: cumulative drive h1 and order contrast h2;
- primary component rule: longitudinal tracker;
- sensitivity component rule: largest component at each frame.

### S2.2 Common-recipient transplant artifact

- rows: n=36;
- donor worlds: W=3, seeds 35001–35003;
- histories: H=12;
- recipient bodies: one fixed standardized recipient;
- response vector: the committed five-dimensional response;
- outer group: donor world.

The analysis therefore addresses donor-world generalization for one recipient,
not recipient-world generalization.

### S2.3 In-place response artifact

- rows: n=24;
- original worlds: W=2;
- histories: H=12;
- status: descriptive only because W=2.

### S2.4 Historical body-baseline artifact

- rows: n=48;
- original worlds: W=4, seeds 38501–38504;
- histories: H=12;
- component rule: largest-component reselection;
- compared feature sets: component-memory features and size-plus-mass.

## S3. V4.0 bootstrap audit

The V4.0 implementation draws H=12 history identifiers with replacement from
the same 12 histories. It copies the associated rows and assigns each draw a
fresh group identifier before leave-one-group-out fitting.

If a history is selected twice, its copied rows are exact duplicates, including
the same original-world observations. The fresh identifiers make the copies
appear independent to the cross-validation splitter. Consequently, one copy can
be in a training fold while another exact copy is in the corresponding test
fold.

The probability of no duplicate in one replicate is:

`P(all unique) = 12! / 12^12 = 0.0000537232`.

The probability of at least one duplicate is:

`P(duplicate) = 0.9999462768`.

Audit of the fixed V4.0 draws gives:

| Unique histories in replicate | Number of replicates |
|---:|---:|
| 4 | 3 |
| 5 | 43 |
| 6 | 291 |
| 7 | 854 |
| 8 | 1,081 |
| 9 | 593 |
| 10 | 122 |
| 11 | 13 |
| 12 | 0 |

Thus 3,000/3,000 realized replicates contained duplicates and 0/3,000 were
leakage-free under the intended original-observation interpretation.

## S4. Frozen V4.1 prediction algorithm

For response y, feature matrix X, and original-world vector g:

1. enumerate each unique world w;
2. define test rows as g=w and training rows as g≠w;
3. identify nonconstant columns using training rows only;
4. estimate feature mean and standard deviation using training rows only;
5. standardize training and test rows with those training estimates;
6. fit ridge regression with λ=1 and an intercept;
7. predict all rows in world w once;
8. concatenate all held-out predictions in original row order.

No original world appears in both training and test within an outer fold.
Preprocessing is nested inside the fold. No hyperparameter is selected after
outcomes are inspected.

The primary pooled score is:

`R² = 1 - sum_i (y_i - yhat_i)^2 / sum_i (y_i - mean(y))^2`.

For uncertainty display, each fold score uses a normalized held-out loss with a
common outcome scale, so the mean fold score equals the pooled score.

## S5. Crossed world-and-history exclusion

The primary estimator tests generalization to a new world while retaining other
worlds’ observations of the same imposed history in training. A stricter
sensitivity removes both:

- every row from the held-out world; and
- every training row with the test row’s history identifier.

This produces one prediction per test row from other worlds and other
histories. It is a sensitivity analysis because its training set differs by
test history.

| Checkpoint | h1 primary | h1 crossed | h2 primary | h2 crossed |
|---|---:|---:|---:|---:|
| Initial | 0.7382 | 0.6021 | 0.7631 | 0.6618 |
| Moderate | 0.9020 | 0.8842 | -0.5102 | -0.9873 |
| Deep-1 | 0.8432 | 0.8041 | -0.1315 | -0.4677 |
| Deep | 0.6947 | 0.6420 | -1.1183 | -1.4230 |

## S6. Original-world fold scores and uncertainty

### S6.1 Cumulative-drive coordinate h1

| Checkpoint | World 38502 | World 38503 | World 38504 | Mean / pooled |
|---|---:|---:|---:|---:|
| Initial | 0.7735 | 0.5479 | 0.8933 | 0.7382 |
| Moderate | 0.9006 | 0.8557 | 0.9498 | 0.9020 |
| Deep-1 | 0.8845 | 0.7079 | 0.9373 | 0.8432 |
| Deep | 0.7454 | 0.4141 | 0.9246 | 0.6947 |

### S6.2 Order-contrast coordinate h2

| Checkpoint | World 38502 | World 38503 | World 38504 | Mean / pooled |
|---|---:|---:|---:|---:|
| Initial | 0.7488 | 0.6936 | 0.8470 | 0.7631 |
| Moderate | -0.0162 | -1.2059 | -0.3085 | -0.5102 |
| Deep-1 | 0.2850 | -0.9119 | 0.2324 | -0.1315 |
| Deep | -0.0982 | -3.2362 | -0.0206 | -1.1183 |

### S6.3 Descriptive intervals

| Quantity | World-fold t interval | Fixed-fold block percentiles |
|---|---:|---:|
| h1 initial | [0.3026, 1.1738] | [0.5968, 0.8673] |
| h1 moderate | [0.7851, 1.0189] | [0.8654, 0.9391] |
| h1 deep-1 | [0.5448, 1.1416] | [0.7462, 0.9258] |
| h1 deep | [0.0513, 1.3381] | [0.4859, 0.8858] |
| h2 initial | [0.5701, 0.9561] | [0.7056, 0.8257] |
| h2 moderate | [-2.0503, 1.0299] | [-1.0115, -0.0796] |
| h2 deep-1 | [-1.8117, 1.5487] | [-0.6640, 0.2736] |
| h2 deep | [-5.6757, 3.4390] | [-2.5563, -0.0374] |

With W=3, neither interval family is a reliable nominal 95% confidence
interval. The fold values are the primary uncertainty report.

## S7. Tracker and event-evidence audit

The longitudinal raw summary directly contains:

| Count or quantity | Reproduced value |
|---|---:|
| total records | 36 |
| recorded surviving | 36 |
| recorded lost | 0 |
| recorded switches | 0 |
| mean deep M | 0.190203 |
| deep M≤0.25 | 34/36 |

The deep h1 tracker comparison is:

| World | Longitudinal | Largest each frame | Difference |
|---|---:|---:|---:|
| 38502 | 0.7454 | 0.7928 | -0.0474 |
| 38503 | 0.4141 | 0.3722 | 0.0419 |
| 38504 | 0.9246 | 0.8470 | 0.0777 |
| Mean | 0.6947 | 0.6706 | 0.0241 |

The paired descriptive t interval for the mean difference is
[-0.1360, 0.1841].

The persisted artifact does **not** contain:

- component masks by frame;
- candidate association edges;
- individual geometry/size gate terms;
- alternative compatible matches;
- split or merge adjudication records;
- a dedicated fusion flag.

Accordingly, the recorded survival and switch fields are reproducible, but
fusion-free continuity is not independently reconstructable.

## S8. Secondary results

### S8.1 Common-recipient transplant

| Response | Grouped R² | World folds | Crossed result |
|---|---:|---|---:|
| full h1 | 0.6468 | 0.6568, 0.6972, 0.5863 | 0.4807 |
| inert h1 | 0.0000 | 0, 0, 0 | -0.1901 |
| erased h1 | 0.0000 | 0, 0, 0 | -0.1901 |
| full h2 | 0.3537 | 0.4008, 0.4318, 0.2284 | 0.1002 |

The grouped constant-control score is zero because the held-out predictions
equal the no-information mean under the primary fold normalization. The crossed
row-wise sensitivity retains the historical negative value because its training
means differ by excluded history. Neither representation contains positive
information.

### S8.2 In-place response

| Response | Grouped R² | Worlds | Disposition |
|---|---:|---:|---|
| h1 difference | 0.7039 | 2 | descriptive only |
| h2 difference | 0.1939 | 2 | descriptive only |

### S8.3 Component-memory versus body baseline

| Checkpoint | Memory features | Size plus mass | Paired difference |
|---|---:|---:|---:|
| Initial | 0.8291 | -0.1078 | 0.9369 [0.4994, 1.3744] |
| Deep | 0.7692 | 0.4538 | 0.3154 [-0.2394, 0.8701] |

The intervals are descriptive t intervals over W=4 original worlds. The deep
comparison is not separated.

## S9. Global information versus local storage

The primary labels are functions of a drive history applied to the complete
world. Every large component in one world is therefore exposed to the same
label. A successful component-feature decoder can establish access to global
history-related information. It cannot, without additional frozen comparisons,
show that the information is uniquely or specifically stored inside the tracked
component.

The required but absent comparison would hold folds, preprocessing, labels, and
model fixed while varying access to:

- tracked-component features;
- nearby-component features;
- target-masked environmental features;
- whole-world aggregate features.

No such local/neighbour/environment/world access matrix is committed in V4.0.
The local-storage claim is withdrawn rather than inferred from tracker
agreement.

## S10. Figure-caption and sample-size audit

| Figure | Artifact family | n | W | H | Caption disposition |
|---|---|---:|---:|---:|---|
| Figure 1 | longitudinal | 36 per checkpoint | 3 | 12 | corrected; intervals labelled descriptive |
| Figure 2 | tracker sensitivity | 36 | 3 | 12 | corrected; event-evidence limitation stated |
| Figure 3 transplant | common recipient | 36 | 3 donor | 12 | corrected; one recipient stated |
| Figure 3 baseline | historical H2-CERT | 48 | 4 | 12 | corrected; different family and tracker stated |

No figure caption treats rows or histories as independent worlds. No caption
uses the withdrawn V4.0 bootstrap interval.

## S11. Claim dispositions

| ID | Short claim | V4.1 status |
|---|---|---|
| C01 | Initial h1 global informational content | SUPPORTED |
| C02 | Positive deep h1 point | SUPPORTED |
| C03 | Deep h1 lower bound clears 0.50 | NOT ESTABLISHED |
| C04 | Initial h2 information | SUPPORTED |
| C05 | Deep h2 information persists | NOT ESTABLISHED |
| C06 | Tracker points are descriptively comparable | OBSERVED |
| C07 | 36/36 surviving and zero switches are recorded | OBSERVED |
| C08 | Fusion-free continuity independently verified | WITHDRAWN |
| C09 | Common-recipient response carries h1 information | SUPPORTED |
| C10 | In-place response inferentially established | NOT ESTABLISHED |
| C11 | Deep memory features outperform size-plus-mass | NOT ESTABLISHED |
| C12 | Tracked component is the local storage site | WITHDRAWN |

The authoritative detailed wording is in `CLAIM_LEDGER_V4_1.md` and
`claim_ledger_v4_1.json`.

## S12. Reproduction boundary

The V4.1 analysis reads only four committed pickle artifacts. It does not
instantiate the simulation engine, execute a seed, replay a trajectory, or
reconstruct a frame. The exact commands are listed in `REPRODUCIBILITY.md`.

The unsealed turnover and active-reconstruction programme is outside this
paper. No result from that programme appears in the manuscript abstract,
results, or conclusion.
