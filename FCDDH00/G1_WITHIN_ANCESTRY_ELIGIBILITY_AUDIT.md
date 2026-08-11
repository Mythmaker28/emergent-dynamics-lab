# FCDDH00 — G1 WITHIN-ANCESTRY ELIGIBILITY AUDIT

**Verdict: `FCDDH00_G1_STATIC_ELIGIBILITY = PASS`.**
Proved **statically**, from committed source only. **No physics was instantiated for this proof.**

## 1. The common upstream precursor is a pure seeded draw

`edlab.experiments.exp_sc_00.seed_state(sp, tr, seed, internal)` — reached as
`edlab.experiments.sc_mcm.config.seed_state` through `sc_iom.config` and `sc_hmc.config` — draws
from `numpy.random.default_rng(seed)` and returns an `SCState`. AST audit of its body:

* calls: `['?.default_rng', 'SCState', 'np.arange', 'np.clip', 'np.full', 'np.ones', 'np.where', 'np.zeros', 'range', 'rng.standard_normal']`
* contains no `.step` call: `True`
* contains no `advance`: `True`
* reads no geometry symbol (`SITE_A`, `SITE_B`, `GEOMETRY`, `_blob`): `True`
* formal arguments: `['sp', 'tr', 'seed', 'internal']`

Therefore `PRECURSOR(S)` is a **pure function of `S` alone**, byte-identical for all four
descendants of a block, independent of geometry and of allocation, and it costs **zero engine
advances**. Each construction worker recomputes it in its own fresh process and reports its
SHA-256; the driver requires the four hashes of a block to be equal, and records the value in the
panel lock. A block whose four precursor hashes are not identical is rejected whole.

## 2. Geometry is an explicit argument applied to that identical precursor

`domc_core.set_geometry(name)` assigns only the two frozen site positions from an explicit name
(`GEOMETRY = {"FAR": ((32,16),(32,48)), "NEAR": ((32,24),(32,40))}`). `domc_core.found(S)` then
returns `SCState -> IOMState` with `rho, U, V, C` multiplied by the geometry blob `_blob()` and
`c, N, uptake` copied unchanged; it calls `['?.copy', 'C.seed_state', 'IOMState', '_blob', 'np.zeros']` and
contains no `.step`: `True`.

**Each worker re-verifies this identity numerically at run time, with zero advances**, by
asserting `found(S).rho == PRECURSOR(S).rho * blob`, and likewise for `U`, `V`, `C`, and
`c == PRECURSOR(S).c`, `N == PRECURSOR(S).N`. The result is reported as
`g1_precursor_mask_identity` on every descendant record, and a false value rejects the block.

## 3. Byte-for-byte reproduction of every historical parity-selected branch

Three routes exist in the committed tree:

| route | selection of `(hA, hB)` |
|---|---|
| `WSFSCRP00.wsfscrp_core.make_founder(seed, geom)` | `seed % 2 == 0` (**parity**) |
| `FSQBT00.fq_construct.construct(seed, geom, alloc)` | `alloc == 0` (**explicit**) |
| `FCDDH00.fh_cworker` | `ALLOC == 0` (**explicit**, `S` common to the four cells) |

All three execute the identical operation sequence:

```
domc_core.set_geometry(g)
e = wsfscrp_core.engine()
f0 = domc_core.found(S)                       # zero advances
f  = domc_core.advance(e, f0, domc_core.T_FOUND)      # 150 steps
(hA,hB) = (HIST_H,HIST_L) if a == 0 else (HIST_L,HIST_H)
st = domc_core.advance(e, domc_core.apply_dual_history(e,f,hA,hB), domc_core.SETTLE)  # 120+120
```

`identical_in_all_three_routes = True`.
The **only** difference is the guard that selects `(hA, hB)`. Under the substitution
`a := 0 if seed % 2 == 0 else 1` the two guards are the *same Boolean*, so the explicit form
reproduces every historical parity-selected branch **byte-for-byte**. The engine callable is the
same single function `wsfscrp_core.engine()` in all three routes.
`physics_instantiated_for_this_proof = False`.

## 4. Label blindness of admission, reader, gauge and threshold formulae

Every function below was parsed and its complete symbol set intersected with the label tokens
`SITE_A, SITE_B, GEOMETRY, set_geometry, geom, geometry, alloc, allocation, HIST_H, HIST_L, HIST,
role, NEAR, FAR`. Every intersection is empty:

* `FCDDH00/fh_core.py:A_PAIR` — leaked tokens: `[]`
* `FCDDH00/fh_core.py:A_X_block` — leaked tokens: `[]`
* `FCDDH00/fh_core.py:differential_d` — leaked tokens: `[]`
* `FCDDH00/fh_core.py:gauge_sign` — leaked tokens: `[]`
* `FCDDH00/fh_core.py:gauge_statistic` — leaked tokens: `[]`
* `FCDDH00/fh_core.py:interaction_x` — leaked tokens: `[]`
* `FCDDH00/fh_core.py:residual_r` — leaked tokens: `[]`
* `FCDDH00/fh_core.py:tau_dynamic_sq` — leaked tokens: `[]`
* `FCDDH00/fh_core.py:tau_material_sq` — leaked tokens: `[]`
* `FCDDH00/fh_core.py:tau_site_sq` — leaked tokens: `[]`
* `WL2SMF00/wl2_prod.py:M2sq` — leaked tokens: `[]`
* `WL2SMF00/wl2_prod.py:X_channels` — leaked tokens: `[]`
* `WL2SMF00/wl2_prod.py:cell_verdict` — leaked tokens: `[]`
* `WL2SMF00/wl2_prod.py:normalizer` — leaked tokens: `[]`
* `WL2SMF00/wl2_prod.py:tau_dynamic_sq` — leaked tokens: `[]`
* `WL2SMF00/wl2_prod.py:tau_material_sq` — leaked tokens: `[]`
* `WL2SMF00/wl2_prod.py:tau_site_sq` — leaked tokens: `[]`
* `WL2SMF00/wl2_ref.py:M2sq` — leaked tokens: `[]`
* `WL2SMF00/wl2_ref.py:X_channels` — leaked tokens: `[]`
* `WL2SMF00/wl2_ref.py:normalizer` — leaked tokens: `[]`
* `WL2SMF00/wl2_ref.py:tau_dynamic_sq` — leaked tokens: `[]`
* `WL2SMF00/wl2_ref.py:tau_material_sq` — leaked tokens: `[]`
* `WL2SMF00/wl2_ref.py:tau_site_sq` — leaked tokens: `[]`
* `WSFSCRP00/wsfscrp_core.py:B_of` — leaked tokens: `[]`
* `WSFSCRP00/wsfscrp_core.py:q_channels` — leaked tokens: `[]`
* `WSFSCRP00/wsfscrp_core.py:reference_masks` — leaked tokens: `[]`
* `WSFSCRP00/wsfscrp_core.py:t0_masks` — leaked tokens: `[]`

The frozen **response reader** is parameterised by the *physical site positions*, which **are**
the geometry; that is the inherited physical readout, not a label leak. No admission rule, no
gauge selection rule and no threshold formula contains any `g` or `a` term whatsoever.
Descendant-specific sham values differ and remain bound to bytes.

## 5. The seven required conditions

1. **same_upstream_precursor_bytes_for_all_four_descendants** — PROVED_BY_CONSTRUCTION: PRECURSOR(S) = seed_state(SPEC,TRACER,S,'random') is a pure function of S with zero engine advances; each worker recomputes it and reports its sha256, and the driver requires the four to be equal.
2. **one_and_only_one_descendant_per_cell** — ENFORCED_BY_THE_CONSTRUCTOR_DRIVER
3. **geometry_independent_of_allocation_construction_order** — PROVED: geometry enters only through set_geometry -> _blob, before any history; allocation enters only through apply_dual_history, after the founding advance.
4. **reader_compatible_masks_and_support_in_every_cell** — ENFORCED_BY_ADMISSION_PER_DESCENDANT
5. **no_label_in_admission_reader_gauge_or_threshold_formula** — PROVED_BY_AST_ABOVE
6. **no_seed_parity_fallback** — The FCDDH00 route never reads seed bits; (g,a) are explicit arguments.
7. **no_G2_observational_substitute** — No observational route exists in the FCDDH00 code path.

## 6. Consequence

`WITHIN_ANCESTRY_G1_NOT_FREEZABLE__ZERO_STARTS` is **not** triggered. The G1 complete-factorial
route is freezable and no G2 observational substitute is used anywhere in the FCDDH00 code path.
