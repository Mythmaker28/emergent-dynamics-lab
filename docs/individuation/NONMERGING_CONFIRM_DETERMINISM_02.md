# NONMERGING_CONFIRM_DETERMINISM_02 — Phase 4 DEV determinism pilot (frozen pre-data)

*Full-pipeline determinism check on DEV, before the prospective run. No effect recalibration.*

## Result

Two independent full-pipeline runs of `nonmerging_confirm.py` over DEV seeds 50001–50010 (8 eligible) were
compared:

- **Raw JSON byte-identical** across the two runs (canonical `json.dumps(sort_keys=True)`):
  - run 1 sha256 = `a45a860e0a8418e72f7fe904001e971556ac420e34914a6f243a18523dac6edb`
  - run 2 sha256 = `a45a860e0a8418e72f7fe904001e971556ac420e34914a6f243a18523dac6edb`
- **Bijective-tracker statuses and censorship events identical** across runs for every branch
  (`intact`, `sham`, `ablate`) of every eligible seed (asserted equal).
- **G0 validity identical**: all 8 eligible DEV worlds G0-VALID both runs (max coverage 1.8–3.3 %, 3 distinct
  components throughout, 3 alive).
- **No mask overlap** between alive tracks at any step (one-to-one invariant; enforced by the tracker, tested
  10/10 in `test_bijective_tracker.py`).

## Scope / honesty

- Determinism is byte-identical on **this fixed platform** (py3.11.15 / numpy 2.2.6 / scipy 1.15.3), consistent
  with the sealed-platform determinism established for the prior confirmations. It is **not** claimed
  cross-platform (chaotic RD-PDE).
- The DEV effect magnitudes were **not** recalibrated by this pilot; DEV is used only to verify the pipeline and
  (separately, `power_explore.py`) to size the family. **No positive claim is drawn from DEV.**
- Analyses/nulls use the frozen bootstrap seed 20260715, so `nonmerging_analyze.py` is itself deterministic.

*main/V4/release intacts. Rien poussé/mergé/publié.*
