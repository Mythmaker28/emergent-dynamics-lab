# FCDDH00 — VERIFICATION REPORT

## 1. Parent binding

| check | result |
|---|---|
| owner-reported prefixes resolve uniquely | yes, all five |
| `334b7c2b` → | `334b7c2ba6d97dadb403c7a1ea9700a1c61ad512`, tree `b36f821850a970c6cbb6a29ca539b3a99bbd5d8c` |
| `334b7c2b:FCRA00` → | `b43e04983e6a3cbf31b6ccc84b5267fbe17b1ad2` (matches reported `b43e0498`) |
| `FCRA00_tip_334b7c2b.bundle` sha256 | `95ef451164d31bea9b16b94e6d86aadad40c696a308e007e9955b1e506ae2e3b` (matches reported `95ef4511`) |
| chain by `merge-base --is-ancestor` | `96c7d295 ≺ 16717582 ≺ b3f45ac7 ≺ 334b7c2b` |
| execution tree vs parent tree object | **1392 / 1392** paths byte-identical, 0 mismatches, 0 absent |
| git blob ids | recomputed in-process as `sha1(b"blob <len>\0" + content)`, no subprocess |
| `main` | `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`, re-read at every phase boundary, unchanged |

The 19 files that `.gitattributes` marks `text eol=crlf` were taken as **raw blob bytes**
(`git cat-file blob`) rather than eol-converted working-tree bytes, so every consumed path matches
the committed object exactly. Line-ending form has no effect on Python semantics or on any
numerical result.

## 2. Owner-reported FCRA00 facts, re-derived from committed bytes

| fact | reported | from bytes | agrees |
|---|---|---|---|
| FSQBT00 cell materiality | 24/24 | `PASS_24_OF_24`, n_pass 24 | yes |
| FSQBT00 direct carrier contrast | 12/12 | 12 | yes |
| FSQBT00 parent-e2 sign concordance | 10/12 | 10 | yes |
| frozen P2 transfer | NOT_TRANSFERRED | `NOT_TRANSFERRED` | yes |
| blocks over the frozen tube | 3 | 3 | yes |

`TUBE_P2_LOBO = 1.2166510017869535e-07`. No parent artefact was edited, amended or overwritten.

## 3. Parent basis certificate

`P2` symmetric to 0.0, idempotent to 8.33e-17, complementary (`P2(I−P2)` ≤ 5.9e-17), rank 2;
`P1` rank 1 and **nested inside** `P2` (`P2P1 − P1` ≤ 1e-16, `P2 − P1 − e2e2ᵀ` ≤ 1.4e-17);
`e1·e2` = −8.5e-17; `P2e1 = e1`, `P2e2 = e2` to 1.1e-16. The parent's own declared coordinate
layout (`u` ×10 then `v` ×10) and its declared weights match the frozen FCDDH00 estimand exactly,
so **no rescaling isometry was required**.

## 4. Pre-execution oracle

23 groups Q0A–Q0W, all non-vacuous, all passing, 61 required-to-fail mutations, **0 engine
starts**. The ten separate perturbations demanded by the authorization — a weight, a scored time,
a reader coefficient, a mask byte, a P2 coefficient, a carrier label, a geometry label, an
ancestry role, a TAU and a raw hash — are individually recorded, together with the unpaired
allocation-membership control, and a vacuous self-comparison is itself rejected as a control.

Two of the oracle's first-draft expectations were **wrong and were corrected against committed
bytes before any engine start**: the nested basis structure (§3), and the analytic K-tail of the
enumerable fixture (16/65536, not 1/65536).

## 5. Lock read-back

The committed tree was read back by an **independent path** — `git cat-file -p <branch>:FCDDH00/<f>`
piped to `sha256sum` under device git 2.34.1 — and compared against the sha256 of the execution
copy computed in the cloud container by Python `hashlib`. **23 of 23 files identical**, including
every executable, the master freeze, the oracle report, the randomization seed and the canonical
field schema. Neither side read the other's working file.

## 6. Construction

12 candidates attempted, **12 accepted, 0 rejected**. Per accepted block: 4 descendants, one per
`(geometry × allocation)` cell; 1 precursor hash shared by all four (12 distinct across blocks);
`g1_precursor_mask_identity` true 48/48; production/reference mask agreement 48/48; `B > 0` and
finite `ρ` 48/48; 390 engine steps per descendant; one fresh process and one raw advance sequence
per descendant. 48 charged of 96 authorized.

## 7. Acquisition and the process-control failure

59 of 96 sham rows completed and published. Row `SHAM_1_71007_FAR_a1` was terminated in flight by
an executor-side tool-call wall limit that killed the process group. Its `INTENDED` record was
written and fsynced, its `ACK` and `ADVANCE` markers exist, its output does not. Under the frozen
contract it is **charged and may never be replayed**. 60 charged of 96 authorized leaves 36; 37
rows are missing; **37 > 36**, so the complete twin-sham panel is unreachable within the frozen
budget independently of the replay rule. See `PROTOCOL_DEVIATIONS.md` D2.

**All 29 descendants with both twins acquired are bit-identical over the full horizon** — identical
per-time state hashes, identical terminal hashes, identical full-field output digests, empty touch
set at `t0`, input checkpoint unchanged, identical masks and normalizers.

## 8. What does not exist in this tree

No TAU, no `FCDDH00_DISCOVERY_THRESHOLD_LOCK.json`, no active row, no decoded reader series, no
`z`/`d`/`x`, no axis, no score, no p-value, no hold-out state of any kind. The manifest records 32
artefacts as `NOT_GENERATED_BY_PREDECLARED_STOP` and **no placeholder was created for any of
them**.

## 9. Integrity of this delivery

`SHA256SUMS_SCOPE.json` is non-self-referential: it covers every delivered FCDDH00 file except
`SHA256SUMS` itself, the `_marks/` idempotency-token directory, `__pycache__`, and the out-of-tree
final git bundle. `SHA256SUMS` is built from that scope and is verified twice:

1. against the working tree in the execution container;
2. against an **independent object extraction** from the committed tree on the device
   (`git cat-file -p <tip>:FCDDH00/<path>` per file, no working-file read).

The final subtree id is reproduced with the two available Git implementations (device 2.34.1 and
cloud 2.43.0) where possible. The final Git bundle is built only after the final tip exists, and
**its digest is reported out of band** — in the closing message to the owner — so that no later
closure commit can stale it.

## 10. Git discipline

Branch created from the exact FCRA00 tip and advanced by lock-free plumbing only (scratch
`GIT_INDEX_FILE`, `write-tree`, `commit-tree`, direct ref write), because the working copy sits on
a create-only mount with a stale `.git/index.lock` that cannot be unlinked. No amend, no rebase,
no reset, no force update, no history replacement, no merge into main, no push, no PR, no workflow
trigger. Nothing was deleted, hidden or rewritten. `main` untouched. No Git action was delegated
to Tommy.
