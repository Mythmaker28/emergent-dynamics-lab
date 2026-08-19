# FTCTR01 — EXECUTABLE BYTE AUDIT

**Program:** FUNCTIONAL-TWO-CENTRE-TIMESCALE-REDERIVATION-01 (FTCTR01)
**Owner:** Tommy Lepesteur · **Date (UTC):** 2026-08-19
**Authoritative repository:** `C:\Users\tommy\Documents\ising v3` (device only; the cloud container is **not** authoritative)
**Result:** the critical executable objects are **ABSENT**. Disposition `STOP__CRITICAL_EXECUTABLE_BYTES_MISSING`.

This document has three parts: (1) the independent checker's report, preserved verbatim; (2) a
**naming-independent physics-level re-audit** run by the primary operator, because the continuation
warns — correctly — that *"the old mission name is absent"* must not be confused with *"the physics
is absent"*; (3) the decision.

---

## PART 1 — Independent checker report, VERBATIM

> ## VERDICTS (repo: `C:\Users\tommy\Documents\ising v3`, device mount `$HOME/mnt/ising v3`)
>
> | # | Item | Verdict | Evidence |
> |---|---|---|---|
> | **A** | `TAU_SEP` / `tau_sep`, value 125 as separation time | **ABSENT** | 0 occurrences in any of 10,005 git blobs, 199 refs, 421 commit objects, full `--all` reflog, 9,695 worktree files, 5,792 gitignored files, 46 bundles, 81 tar payloads. Near-miss only: 40+ distinct `tau_*`/`TAU_*` symbols exist (`TAU`, `TAU_MAX`, `tau_sq`, `tau_iv`, `tau_feed`, `tau_on/off`, `TAU_CONTRAST`, `TAU_SLOW`…) — none is `tau_sep`. No `…= 125` bound to any separation concept anywhere. |
> | **B** | `p_hop_Y` (per-step hop probability) | **ABSENT** | 0 hits for `p_hop`, `p_hop_*`, `hop_prob`, `pHop`, "hop probab", "per-step hop" in every substrate scanned. Only `hop`-family tokens in repo: `hops` in `edlab/experiments/exp_ch_00.py:57` (Euclidean displacement of a continuum-field **centroid** between snapshots) and `"one hop"` prose in `_to_delete_ppai/_staging_ppai/PPAI/ppai_audit.py:30`. |
> | **C** | `muX` / `mu_X` (decay rate of X) | **ABSENT** | Case-sensitive `\bmuX\b`/`\bmu_X\b`: 0 real hits. The ~16 apparent hits were random bytes inside compressed binary blobs (npz/PDF), confirmed by inspection. One genuine **lowercase** near-miss, different meaning: blob `6e11da62c613487f4fc18359afb5196a85c6b9f2` — `J_xy^q = K_q(b_xy)*(mu_x^q - mu_y^q) = -J_yx^q`, a face-flux/chemical-potential transport identity, not a species decay rate. |
> | **D** | `kY`/`k_Y` and `muY`/`mu_Y` (birth/death of Y) | **ABSENT** | All `kY`/`kX` hits localise to one blob, `833e92225f42c4668fd496bb17c98e91ad93ce2b`, which is ASCII85/PostScript-encoded binary — false positives. Repo's actual birth/death rate names are `g0` (growth) and `k` (homogeneous removal), e.g. `edlab/substrates/motile_polar/engine.py` ("created by local growth `g0*rho*R` … destroyed by homogeneous removal `k*rho`"). No species-suffixed rate constants exist. |
> | **E** | `nSY` / `n_SY` | **ABSENT** | 17 raw-byte matches, all inside binary blobs (float64 arrays / zlib streams); 0 in any text blob or source file. |
> | **F** | Discrete-lattice engine: co-located Y, 4 ordered sub-shifts, binomial mover count, destination-capacity blocking, X birth/decay | **ABSENT** | See enumeration below. Decisive structural fact: **there is no random binomial draw anywhere in the repository.** All 69 `binomial` occurrences across all blobs are statistical inference (Clopper–Pearson tails via `math.comb`, Beta-Binomial power analysis, exact McNemar). `np.random.binomial` / `rng.binomial`: **0 occurrences**, worktree and history. |
> | **G** | Centre-classification rule → ONE_CENTRE vs TWO_CENTRES | **ABSENT** | 0 hits for `ONE_CENT*`, `TWO_CENT*`, `one_centre/center`, `two_centre(s)/center(s)`, `n_centres`, `centre_count`, `centre_class`/`center_class` — across git objects, worktree, ignored files, bundles and tar payloads. |
> | **H** | OBFOR01, PQEC01, FVLCR01, CLOC02, RSLOC03, FTCTR01 (and long forms) | **ABSENT** | 0 hits in 199 ref names, 397 commit messages, full reflog, 9,528 historical paths, 9,695 worktree paths, all blob contents, all 46 bundle ref-name headers and pack bodies, all 81 archives. **One exclusion declared:** `_ftctr01_src_py_md.tgz` exists at repo root but is `mtime 2026-08-19 21:52`, i.e. a staging artifact created by another agent in this same session ~18 min before I started; it is not repository content. Repo's real acronym families are FCDDH00/FCDDH01R, FSQBT00, FSCMA00, FCRA00, GIMB00, WSCPL00, WSFSCRP00, SQDT00, EEFCA, ETCMNFC, ETNBFC, DCL01T, AXMAT00, CFP01, CRD00-03. |
> | **I** | Threshold "101 accepted X births per centre over 250 steps" | **ABSENT** | 0 hits for `101 accepted`, `accepted_births`, `births per`, `\b101\b`↔birth/accept co-occurrence, `250 steps`. Sole near-miss: `edlab/substrates/reaction_diffusion/engine.py:93` → `tau_feed: int = 250  # steps per temporal cohort` — a feed-cohort period, unrelated to births or centres. |
>
> ## Item F — every simulation substrate/engine actually found (auditable enumeration)
>
> 1. `edlab/substrates/life/engine.py` — Conway Game of Life B3/S23, binary cells, bounded grid, deterministic.
> 2. `edlab/substrates/life/fast.py` — bit-exact fast GoL step, differentially verified against (1).
> 3. `edlab/substrates/boolnet/engine.py` — spatially embedded Boolean network.
> 4. `edlab/substrates/chemotaxis/engine.py` — continuum PDE: density `rho` + attractant `c`, saturating chemotaxis, volume exclusion.
> 5. `edlab/substrates/reaction_diffusion/engine.py` — Gray–Scott PDE `(U,V)` + passive origin cohorts.
> 6. `edlab/substrates/motile_polar/engine.py` — continuum `rho` + internal polarity vector field `p` + nutrient `R`.
> 7. `edlab/substrates/multistable/engine.py` — two continuum catalytic species A/B + shared attractant, demixing.
> 8. `edlab/substrates/scaffold/engine.py` — continuum scaffold `rho` + confined internal bistable `(u,v)` network.
> 9. `edlab/substrates/flow_lenia/engine.py` — mass-conservative Flow-Lenia continuum, FFT convolution, reintegration transport.
> 10. `edlab/substrates/flow_lenia/engine_throughput.py` — Flow-Lenia + latent reservoir `R` exchange.
> 11. `edlab/substrates/ctrans/engine.py` — 1-D chain of continuous sites, float observable ~1e-3, noise/drift/integer transport delays.
> 12. `edlab/substrates/lattice_bond/engine.py` *(history-only, not in worktree)* — periodic square lattice, three **continuous** fields: matter `m`, resource `n`, face bond-fraction `b`. Closest thing to "lattice" in the repo; still a bounded-continuum field model, no particle counts.
> 13. `edlab/substrates/particle_dynamics/engine.py` — off-lattice deterministic Newtonian particles on a 2-D torus (CORE V0).
> 14. `edlab/substrates/particle_dynamics/engine_density.py` — CORE V0 + density-preference force.
> 15. `edlab/substrates/particle_dynamics/engine_orbital.py` — CORE V0 + transverse/orbital force.
> 16. `edlab/substrates/particle_dynamics/engine_combined.py` — CORE V0 + both.
> 17. `edlab/experiments/sc_iom/engine.py` — scaffold + organizational-memory field `m=(m1,m2)`.
> 18. `edlab/experiments/sc_mcm/engine.py` — `MultiChannelMemoryEngine`, orthogonal two-channel readout of (17).
> 19. `independent_replication/substrate_fhn.py` — FitzHugh–Nagumo excitable network.
> 20. Harness/wrapper layers with **no new physics** (all import a frozen engine above, or are exact-arithmetic audit cores): `CHMR/chmr_core.py`, `DOMC/domc_core.py`, `PPAI/ppai_core.py`, `PPAI/ppai_engine.py`, `P07/p07_core.py`, `P08/p08_core.py`, `results/ROUTE_E_DYNAMIC_SOURCE_CAPTURE_04/dsc_core.py`, `WSFSCRP00/wsfscrp_core.py`, `ETCMNFC/etcmnfc_core.py`, `ETPC/etpc_core.py`, `FCDDH00/fh_core.py`, `edlab/experiments/sc_hsi/core.py`, `experiments/individuation/turnover_engine_03g.py`.
>
> Not one of these has integer per-cell particle counts, ordered sub-shift diffusion, a stochastic mover count, destination-capacity refusal, or an accept/reject birth process. "Occupied" in this repo always means a continuum threshold (`occupied = state.m >= spec.matter_threshold`, `edlab/substrates/lattice_bond/instrumentation.py:103`); "capacity" always means channel/throughput capacity in the P07/P08 analyses.
>
> ## Positive controls (same methods, same call paths)
>
> - **Working-tree chunked `xargs|grep`:** `FCDDH01R|Clopper-Pearson` → **151 hits** in `wtpart_07` alone (e.g. `_to_delete/fcddh01r_xcheck/SHA256SUMS:1506`).
> - **Gitignored-file chunk:** `sha256|seed` → **1,125 matching files** in `igp_00`.
> - **Git-object blob scanner (`scan2.py`):** returned real, verifiable text hits — 69 `binomial` (statistical), 6 `co-located` (`docs/CRD01_FINAL_REPORT.md:90`, `docs/CRD02_TRANSFER_AUDIT.md:11,26`) — proving it reads blob content correctly.
> - **Bundle zlib pack-walker:** control `import |def |Clopper|binomial` matched in **every one of 46 bundles** (585 matches in the 586 MB self-contained bundle, 35 in the orphan bundle), and each walk terminated exactly at `filesize − 20` (the pack trailer), proving 100 % traversal.
> - **1.4 GB escrow tar stream:** control `sha256|seed|.json|.npz` → **16,391 matching lines** over the full 1,553,920,000-byte decompressed stream.
> - **Symbol-family control:** `tau_*` grep returned 20+ distinct real symbols — so the absence of `tau_sep` is a true negative, not a broken pattern.
>
> ## Coverage — what was searched, and what was NOT
>
> **Searched (byte-level):**
> - **100 % of git objects**: 12,817 unique objects enumerated independently from 6 pack `.idx` files + all 256 loose object dirs (8,247 loose + 4,614 packed). Of these, **all 10,005 blobs** had their full decompressed content regex-scanned (9,845 ≤1 MB and all 160 >1 MB). Includes the **258 unreachable/dangling objects**.
> - All 199 refs (heads, tags, `refs/archive/*`, `refs/codex/turn-diffs/checkpoints/*`), 397 reachable commits, all commit messages+bodies, full `git reflog --all` (92 KB), 9,528 distinct historical paths.
> - Working tree: 1,203 tracked + 8,492 untracked files; 8,129 text-type files content-grepped. Plus 5,792 non-`.venv` gitignored files (4,528 text-type) grepped.
> - **All 46 `.bundle` files** byte-walked via direct zlib inflation of the packfile — including the one **orphan history** (tip `4dc575ea1e4939700ddaa52f70e7baf8f8deb459` = `refs/heads/agent/mpm-execution-recovery-02` / `refs/tags/DCL01T_R_AUTHENTIC`) whose base commit `f382dbf077699aa65c80328b6519035d1cda4a57` is absent from `.git`, so it is unreachable by any `git grep`.
> - **All 81 tar/tgz/tar payloads** (~1.6 GB compressed, incl. `ROUTE_E_RAW_EVIDENCE_ESCROW_00.tar.gz` at 1.55 GB decompressed) stream-decompressed and grepped end-to-end.
> - 9 registered worktrees: all their HEAD commits verified present in `.git` and thus already scanned. No stash entries.
>
> **NOT covered (honest bounds on the negative):**
> 1. `.venv/` — 7,696 gitignored third-party virtualenv files (numpy/scipy/dateutil). Excluded by design; a project symbol would not be defined there.
> 2. **Second-level compression**: binary blobs (`.npz`, `.pkl`, `.png`, PDF streams) were scanned as raw bytes but their *inner* zlib/zip members were not individually inflated. A token existing **only** inside a compressed numeric array payload would be missed. (Mitigation: `.npz` member names and all JSON sidecars are plaintext and were scanned.)
> 3. **Delta reconstruction inside bundles**: I inflated each pack object's stream, so literal text in delta-insert sections is caught, but text carried only by a copy-from-base instruction is not reconstructed. This matters only for the single orphan bundle pair; 42 of 43 bundle tips are already in `.git`, whose objects were fully materialised via `git cat-file`.
> 4. Worktree directories `/tmp/wt-*` and `/sessions/rcw-01maeqjjwxrbgthsjysxdmur/*` do not exist on this device (other machines/sessions) — but their commits are in `.git` and were scanned.
> 5. **Deliberately excluded**: `_ftctr01_src_py_md.tgz` (repo root), created 2026-08-19 21:52 by another agent in this session — not repository content.
> 6. `.git` was never written to; all fetch/clone attempts were redirected to device-local `/tmp`.
>
> ## OVERALL VERDICT
>
> **No "two-centre Y/X developmental timing architecture" exists in this repository, in any form, at any point in its recorded history.** Not a single one of the nine named objects is present; there is no discrete-particle lattice engine at all (the repo's 19 substrates are Game of Life, Boolean networks, continuum PDE fields, and off-lattice Newtonian particles); there is no stochastic binomial draw anywhere in the codebase; and no "centre" concept, X-birth acceptance counter, or separation-time parameter is defined anywhere. This repository is an emergent-dynamics/individuation metrology project ("edlab"), structurally unrelated to the described architecture.

*(End of verbatim checker report.)*

---

## PART 2 — Naming-independent physics-level re-audit (primary operator)

The checker's evidence is not internally contradictory, so the broad search was **not** repeated. What
follows is a different question, asked deliberately: *forget every name — is the mechanism there?*
A discrete stochastic hopping model has fingerprints that survive any renaming.

### 2.1 Fingerprint 1 — the mover draw

A binomial mover count over co-located particles cannot be implemented without a binomial (or an
equivalent sum of Bernoullis). Inventory of **every** stochastic draw call-site in the current tree
(ref `axmat/a-x-materiality-audit-00`, 610 Python files):

| draw | call-sites |
|---|---|
| `rng.uniform` | 144 |
| `rng.normal` | 82 |
| `rng.choice` | 61 |
| `rng.integers` | 42 |
| `rng.random` | 37 |
| `rng.permutation` | 21 |
| `rng.standard_normal` | 19 |
| `rng.randint` | 6 |
| `rng.shuffle` | 4 |
| `_rng.random` | 3 |
| `_rng.integers` | 1 |
| **`binomial` (any receiver)** | **0** |
| `poisson`, `multinomial`, `hypergeometric`, `geometric`, `exponential`, `bernoulli` | **0 each** |

There is no sum-of-Bernoullis substitute either: the single per-cell Bernoulli pattern in the whole
repository, `rng.random(shape) < p`, occurs once inside a lattice engine —
`edlab/substrates/life/fast.py:57`, which generates a **random initial soup** for Game of Life, not a
movement decision.

### 2.2 Fingerprint 2 — integer per-cell occupancy

Co-location, capacity blocking and candidate pools all require an integer count per cell. Every
integer-dtype array declared inside `edlab/substrates/` was inspected: they are component **labels**
(`flow_lenia/observables.py:36`), Boolean-circuit **opcodes and states**
(`boolnet/circuits.py:63-65`, `boolnet/engine.py:62`), **index sets** (`ctrans/engine.py:151-154`),
**delay matrices** (`ctrans/systems.py:61`), and serialisation **byte buffers**
(`lattice_bond/future_lifecycle_owned_pipeline.py:443`). **None is an occupancy count of a mobile
species.**

### 2.3 Fingerprint 3 — where the randomness actually lives

Only five engine modules touch an RNG at all, and in each case the draw is confined to
**initialisation**, never to dynamics:

* `particle_dynamics/engine.py` — lines 46-50 only: `default_rng(seed)`, initial positions
  (`rng.uniform`), initial velocities (`rng.normal`), initial types (`rng.integers`). The step
  function is deterministic Newtonian integration.
* `boolnet/engine.py` — lines 158-165 only: random circuit opcodes, sources and initial states.
* `life/fast.py` — initial soup.
* `ctrans/*` — measurement noise and acquisition jitter on a continuous chain.

Every remaining RNG use in the repository is experiment generation, statistical resampling, or
oracle/fixture construction (`noise_aware/`, `point_cert/`, `WL2SMF00/`, `FWL2CF00/`,
`consolidation/`). The three files that combine toroidal wrapping with an RNG are a **tracker
assignment test** with hand-supplied masks (`experiments/individuation/test_bijective_tracker.py`,
docstring: *"Masks are supplied directly … so the tests exercise the ASSIGNMENT / CENSORSHIP logic
(not the detector)"*), a parameter-sweep harness, and a statistical oracle.

### 2.4 Fingerprint 4 — the "co-located" lead, run down

The checker's only genuine textual hits for `co-located` are in `docs/CRD01_FINAL_REPORT.md:90` and
`docs/CRD02_TRANSFER_AUDIT.md:11,26`. Read in context, both refer to a **co-located reference
sensor** in the Causal Response Decomposition metrology programme
(`docs/CRD00_PROTOCOL.md`: *"EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-00"*), i.e. an instrument channel
sharing environmental drift. Nothing to do with two particles sharing a lattice cell. Lead closed.

### 2.5 Conclusion of Part 2

The physics is absent, not merely the vocabulary. A model whose diffusion is *defined* by a binomial
mover count, over integer per-cell occupancies, with destination-capacity refusal, leaves four
independent traces in a codebase. **Zero of the four are present.**

---

## PART 3 — Decision

### Critical executable objects (continuation §1) — all ABSENT

| critical object | verdict | searched in |
|---|---|---|
| actual discrete Y diffusion implementation | **ABSENT** | worktree, all 199 refs, remote-tracking refs, reachable **and** unreachable objects, 46 bundles, 81 archives |
| ordered four-sub-shift semantics | **ABSENT** | idem |
| Y hop probability path | **ABSENT** | idem |
| X decay path | **ABSENT** | idem |
| Y birth and death paths | **ABSENT** | idem |
| `nSY` / candidate-pool semantics | **ABSENT** | idem |
| capacity-blocking semantics (destination occupancy) | **ABSENT** | idem |
| actual centre-classification rule | **ABSENT** | idem |
| exact scheduler event order | **ABSENT** | idem |

### Non-critical objects — correctly not decisive

Per the continuation's own distinction, the absence of `TAU_SEP`, of the literal `125`, of the prior
mission names, and of the `101/250` threshold is **not** what stops this mission. FTCTR01 exists to
*derive* the clock, not retrieve it — and it would have derived it happily from an unnamed engine.
The mission stops because the engine itself, the centre rule, and the scheduler are absent.

### Named missing executable object (single, exact)

> **The discrete two-species lattice engine implementing sequential Y diffusion — four ordered
> sub-shifts, a binomial mover count over integer co-located Y occupancies, sequential state update
> between sub-shifts, toroidal wrap, and destination-capacity refusal — together with its centre
> classifier and its scheduler event order.**

No fragment of it exists in `Mythmaker28/emergent-dynamics-lab` at any point in its recorded history.

### Disposition

```
STOP__CRITICAL_EXECUTABLE_BYTES_MISSING
```

`TIMING_CRITERION_NOT_IDENTIFIABLE__EXACT_MISSING_OBJECT_NAMED` was considered and rejected: the
continuation reserves it for the case where *the engine survives* and a secondary object is missing.
Here the engine is the missing object.
