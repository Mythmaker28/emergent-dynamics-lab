# AUTO-20261107-1942-PRIMARYREPRO — journal

role: auto-backlog agent `claude` (Claude Code cloud session), started by the scheduled
Routine Sweeper of `ai-credit-sweeper` (slot T_MINUS_90M); CI-only change

run ID: `AUTO-20261107-1942-PRIMARYREPRO`

start/end: 2026-11-07 19:42Z / 2026-11-07 20:27Z (journal finalized; the commit, the push, the CI check
on the new head, the PR description update and the lock release follow, in that order)

starting Git state: `main` at `3e0e13b71c976d6dcf9602310084c908b8885541`, clean

ending Git state: `auto/primary-repro-ci` = `3e0e13b` + `3f19431` (the job) + the commit that
adds this journal and the `docs/RUN_INDEX.md` row; PR #41 open, not merged

assigned scope: the `ai-credit-sweeper` auto-backlog task, verbatim: "Ajouter à
.github/workflows/nasi-ci.yml un job « primary-repro » (Python 3.10, versions Node 24 de
checkout et setup-python, pip install -r requirements-lock.txt, REPRO_OUT=$RUNNER_TEMP/repro
python -m reproduction.primary --check, python -m reproduction.test_canonical, puis test -z
"$(git status --porcelain)") : aucun job ne lance aujourd'hui la reproduction phare (≈ 30 s et
arbre propre en local le 17/10 sur f382dbf ; dépôt public) — fini quand : job vert sur la PR
et son journal contient « PRIMARY REPRODUCTION: OK » et « CANONICAL TEST: PASS »". No code,
data, parameter, experiment, decision or scientific result changes.

## Authority

Step 4 of the Routine Sweeper task: do one task of the `ai-credit-sweeper` auto-backlog under
its `AUTONOMOUS_MODE.md` rules. The routine's runner step ended `BLOCKED`, not
`REFUSED_BY_PLATFORM`, which is the only outcome that skips step 4. The task (`BACKLOG.md`
line 34 on `auto-backlog`) was reserved in `eb9ee39`, pushed 19:39:09Z. `AUTONOMOUS_MODE.md`
allows a self-merge of a CI-only change only when the test suite is green. It is not (8 known
failures, `docs/TEST_STATUS.md`), so PR #41 is left for the owner's review.

## Lock

`AGENTS.md` requires the scheduled-run lock before a scheduled run changes files. Acquired at
19:43:44Z, before the workflow edit (file mtime 19:46:52Z):

```bash
python -m edlab.runtime_lock acquire --run-id AUTO-20261107-1942-PRIMARYREPRO \
  --task-identity auto-backlog-claude-primary-repro-ci \
  --starting-head 3e0e13b71c976d6dcf9602310084c908b8885541
```

`--experiment` was left at its default, `NONE`. The lock file is git-ignored (`.gitignore:10`)
and local to this ephemeral clone, so it does not guard the owner's working copy; a
concurrent push is rejected by GitHub as non-fast-forward, not overwritten. It is released
with `python -m edlab.runtime_lock release --run-id AUTO-20261107-1942-PRIMARYREPRO` after
the push of this journal.

## Actions

1. Read `AGENTS.md`, the heads of `docs/RESEARCH_CHARTER.md` and `docs/PROJECT_STATE.md`,
   `docs/RUN_INDEX.md`, the journal of `AUTO-20261028-0300-PRMERGES` and `ROADMAP.md` §4.
   `docs/DECISION_LOG.md` and `docs/EXPERIMENT_INDEX.md` were searched for CI only at the end,
   out of the required order. The only hit, `docs/DECISION_LOG.md:2439` ("Docker/CI never
   built"), is in D-085, a verdict on the theorem package and the large hold-out; it is not
   a decision about this workflow.
2. Read `.github/workflows/nasi-ci.yml`, `requirements-lock.txt`,
   `release/README_RELEASE.md`, `reproduction/primary.py`, `reproduction/test_canonical.py`
   and `reproduction/EXPECTED.json`.
3. Built a Python 3.10 venv with the lockfile, ran the reproduction and the canonical test in
   a local clone of `3e0e13b`, then the four job steps in a second, fresh clone with
   `RUNNER_TEMP` pointing at a scratch directory.
4. In the first clone: two negative controls and one in-place run without `REPRO_OUT`, each
   restored afterwards.
5. Added the `primary-repro` job (`.github/workflows/nasi-ci.yml:41-59`), commit `3f19431`
   (19:53:48Z), pushed `auto/primary-repro-ci`, opened PR #41.
6. Read both `primary-repro` job logs on `3f19431`.
7. Traced the in-place output drift of action 4 to its two causes (OBSERVED), in the second
   clone with outputs outside the tree; for this, searched `reproduction/figures.py` and
   `reproduction/primary.py` for font and `savefig` settings and read
   `release/ENVIRONMENT.md`.
8. Wrote this journal and one `docs/RUN_INDEX.md` row.

Important files read: those in actions 1 and 2, `docs/TEST_STATUS.md`,
`docs/paper/full/HEADLINE_NUMBER_ERRATUM.md`, `pyproject.toml`.

Changed: `.github/workflows/nasi-ci.yml` (new job only), `docs/RUN_INDEX.md`, this journal.
No code, data, experiment, state, decision, parameter or scientific result changed.

## Reproducible commands

Environment here: Ubuntu 24.04.5 LTS, Intel Xeon @ 2.10GHz, 4 vCPU with AVX2 and AVX-512F,
CPython 3.10.20 (installed with uv; the image has no `python3.10`). `pip install -r
requirements-lock.txt` installs 13 packages: contourpy 1.3.2, cycler 0.12.1, fonttools
4.65.0, kiwisolver 1.5.1, matplotlib 3.10.9, numpy 2.2.6, packaging 26.3, pillow 12.3.0,
pyparsing 3.3.3, python-dateutil 3.0.0, scipy 1.15.3, six 1.17.0, tzdata 2026.6. The runner
installed the same 13 versions, and its wheel file names carry the same platform tags as the
wheels installed here. The runner: image ubuntu-24.04 20261101.360.1 (Ubuntu 24.04.5),
runner 2.338.2, CPython 3.10.22, pip 26.3, steps in `bash -e`; its log does not name the CPU.

```bash
S="$(mktemp -d)"                 # scratch directory outside the repository (here: the session scratchpad)
uv python install 3.10
"$(uv python find 3.10)" -m venv "$S/venv310"; export PATH="$S/venv310/bin:$PATH"
git clone /home/user/emergent-dynamics-lab "$S/sim" && cd "$S/sim" && git checkout 3e0e13b
export RUNNER_TEMP="$S/runner_temp"            # the four job steps, as in the workflow
python -m pip install -r requirements-lock.txt
REPRO_OUT="$RUNNER_TEMP/repro" python -m reproduction.primary --check
python -m reproduction.test_canonical
git status --porcelain ; test -z "$(git status --porcelain)"
```

In-place run (first clone, `git clone /home/user/emergent-dynamics-lab "$S/clone"` at
`3e0e13b`, same venv): `python -m reproduction.primary --check`, then
`git status --porcelain reproduction/outputs`, then `python "$S/ulpdiff.py"
reproduction/outputs/primary_results.json reproduction/outputs/primary_manifest.json`, then
`git checkout -- reproduction/outputs`. `$S/ulpdiff.py` (scratch, not committed):

```python
import json, math, subprocess, sys
def floats(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from floats(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from floats(v, p + "/" + str(i))
    elif isinstance(o, float): yield p, o
for f in sys.argv[1:]:
    old = json.loads(subprocess.check_output(["git", "show", "HEAD:" + f]))
    new = json.load(open(f))
    a, b = dict(floats(old)), dict(floats(new))
    assert a.keys() == b.keys(), f
    d = [(abs(a[k] - b[k]) / math.ulp(a[k]), abs(a[k] - b[k])) for k in a if a[k] != b[k]]
    print(f, "floats", len(a), "changed", len(d), "max_ulp", max(x for x, _ in d) if d else 0, "max_abs", max(y for _, y in d) if d else 0)
```

Negative controls (first clone, restored with `git checkout --`): the deep h1 point in
`reproduction/EXPECTED.json` raised by 0.2, then `python -m reproduction.primary --check`;
`CANONICAL["h1_deep_point"]` set to `(0.50, 0.06)`, then `python -m
reproduction.test_canonical`.

Drift isolation (second clone, outputs outside the tree; `matplotlib.rcdefaults()` restores
matplotlib's built-in settings before the module runs):

```bash
run() { out="$1"; shift; env "$@" REPRO_OUT="$out" python -c "import sys, runpy, matplotlib; \
  matplotlib.rcdefaults(); sys.argv=['primary', '--check']; \
  runpy.run_module('reproduction.primary', run_name='__main__', alter_sys=True)"; }
DIS="AVX512F AVX512CD AVX512_SKX AVX512_CLX AVX512_CNL AVX512_ICL AVX512_SPR"
run "$S/repro_rcdefault"                                   # matplotlib defaults only
run "$S/repro_blas" OPENBLAS_CORETYPE=Haswell              # + OpenBLAS Haswell kernels
run "$S/repro_npy" NPY_DISABLE_CPU_FEATURES="$DIS"         # + numpy AVX-512 dispatch off
run "$S/repro_both" OPENBLAS_CORETYPE=Haswell NPY_DISABLE_CPU_FEATURES="$DIS"
# compare: sha256sum "$out/<file>" against git show HEAD:reproduction/outputs/<file> | sha256sum
```

The OpenBLAS core in use was read with `scipy_openblas_get_corename64_` from the
`libscipy_openblas64_` library bundled with numpy, and numpy's dispatch state from
`numpy._core._multiarray_umath.__cpu_features__`. The decoded pixels of the committed and
local PNGs were compared with Pillow and numpy.

CI logs: job 128511028984 (push run 42408409047) and job 128511157620 (pull_request run
42408450764), both on `3f19431`.

## OBSERVED

- Local, `3e0e13b` (same code as `3f19431`, which adds only the job):
  `python -m reproduction.primary --check` exits 0 in 23–24 s and `python -m
  reproduction.test_canonical` exits 0 in about 6 s. The input is
  `results/observer/tca_holdout_raw.pkl` (sha256 `dbb5a2bb3017dbe6…`): 36 records, seeds
  38502–38504, 12 histories; survival 36/36, 0 switches, 0 lost.
- Decoding R² with 95% CI, the same here and in both CI logs:

  | checkpoint | mean M | h1 | h2 |
  |---|---|---|---|
  | init | 1.000 | +0.785 [+0.557, +0.944] | +0.801 [+0.532, +0.922] |
  | moderate | 0.387 | +0.933 [+0.889, +0.979] | −0.032 [−0.679, +0.573] |
  | deep-1 | 0.245 | +0.897 [+0.860, +0.974] | −0.053 [−0.528, +0.460] |
  | deep | 0.190 | +0.888 [+0.837, +0.958] | −0.239 [−0.785, +0.318] |

  "GATE h1 deep-turnover CERTIFIED (CI lower bound > 0.50): True (lo=0.837)" and "GATE h2
  deep-turnover NOT ESTABLISHED (CI does not clear 0.50): True (point=-0.239, hi=0.318)".
  `test_canonical`: h1 0.8878 [0.8366, 0.9581], h2 −0.2394 [−0.7850, 0.3182], survival 36,
  switches 0.
- The four job steps pass in the fresh clone, and `git status --porcelain` stays empty.
- Negative controls: the raised `EXPECTED.json` value gives exit 4 and "REPRODUCTION FAILURE:
  --check FAILED (outside tolerance): deep/h1 point 0.888 vs 1.088"; the changed `CANONICAL`
  entry gives exit 1 and "CANONICAL TEST: FAIL h1_deep_point = 0.8878, expected 0.5000 ±
  0.0600".
- In-place run without `REPRO_OUT`: still "--check: OK", but 7 of the 10 tracked files in
  `reproduction/outputs/` change. The five PNGs grow by 8.1–15.3 %
  (`primary_figure.png` 60,032 → 64,880 bytes, `fig_longitudinal_v4.png` 72,847 → 80,546,
  `fig_h1_certification_v4.png` 39,483 → 44,939, `fig_h2_deepturnover_v4.png` 47,855 →
  53,000, `fig_gate_summary_v4.png` 54,032 → 62,289). In `primary_results.json`, 22 of 42
  floats differ, by at most 64 ULP (|Δ| ≤ 7.8e-16). In `primary_manifest.json`, 4 floats
  (at most 8 ULP) and 6 hashes differ. The CSV, NPZ and TEX files are byte-identical.
- CI on `3f19431`: all 8 jobs of the two runs succeeded. `primary-repro` took 76 s on push
  (19:53:54–19:55:10Z; reproduction step about 33 s, canonical step about 8 s) and 82 s on
  pull_request (19:54:27–19:55:49Z). Both logs contain "--check: OK (all values within
  tolerance point=0.06 ci=0.08).", "PRIMARY REPRODUCTION: OK (conclusions reproduced)." and
  "CANONICAL TEST: PASS (4 frozen numbers within tolerance).", write the outputs to
  `../../_temp/repro`, and print nothing at the `git status --porcelain` step. Actions:
  `actions/checkout@v5` at `fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09`,
  `actions/setup-python@v6` at `ece7cb06caefa5fff74198d8649806c4678c61a1`.
- The runner prints sha256 prefixes for 9 outputs, and all 9 equal the committed files:
  `primary_table.csv` 8cac07a6eb3d7b31, `primary_arrays.npz` b7e97a19b1968f22,
  `primary_figure.png` 1ff9e41e7a59d362, `primary_results.json` b9fb6d75b75702f4,
  `fig_longitudinal_v4.png` 2f49866701fb0b61, `fig_h1_certification_v4.png`
  4588d407833aeef8, `fig_h2_deepturnover_v4.png` eec40ea080c45d14,
  `fig_gate_summary_v4.png` cf4fff836a76c6ea, `synthesis_table.tex` 832e3fab70999c3c. The
  manifest hash is not printed.
- Here, matplotlib reads the system file `/etc/matplotlib/matplotlibrc`, which sets
  `font.family: Inter, sans-serif, DejaVu Sans` and `text.hinting: no_hinting`; Inter is
  installed (18 files in `/usr/share/fonts/opentype/inter/`). Matplotlib's built-in default
  is `font.family: sans-serif`, which resolves to its bundled DejaVu Sans. The local PNGs
  differ from the committed ones in their decoded pixels, and four of them in size:
  1633×634 instead of 1632×633 (`primary_figure.png`, `fig_longitudinal_v4.png`) and 883×610
  instead of 882×607 (`fig_h1_certification_v4.png`, `fig_h2_deepturnover_v4.png`);
  `fig_gate_summary_v4.png` keeps 1076×360, with 30,617 differing pixels.
- Here, the OpenBLAS bundled with numpy uses the SkylakeX core, and numpy's AVX-512F and
  AVX512_SKX dispatch is on; with `OPENBLAS_CORETYPE=Haswell` the core is Haswell, and with
  `NPY_DISABLE_CPU_FEATURES` set as above both numpy flags are off.
- The four drift-isolation runs each exit 0 with "--check: OK" and "PRIMARY REPRODUCTION:
  OK" (the first, timed, took 25 s) and leave the clone clean:
  - matplotlib defaults only: the five PNGs and the CSV, NPZ and TEX files are byte-identical
    to the committed ones; `primary_results.json` (`8c02e08599794731`, the same bytes as the
    in-place run) and `primary_manifest.json` differ;
  - plus `OPENBLAS_CORETYPE=Haswell`: all 10 files are byte-identical to the committed ones;
  - plus numpy's AVX-512 dispatch off, OpenBLAS left on SkylakeX: `primary_results.json` is
    still `8c02e08599794731`;
  - both settings: `primary_results.json` and `primary_manifest.json` equal the committed
    files (`b9fb6d75b75702f4`, `3b16550aa3026905`).

## INFERRED

- The job fails when a reproduced value leaves the tolerance of `reproduction/EXPECTED.json`
  or of `CANONICAL`, and when a step writes into the checkout: the two checks exit non-zero
  on such values (negative controls), each step runs under `bash -e`, and `test -z` fails on
  any `git status --porcelain` output.
- The in-place drift has two causes, both outside the repository: this container's
  `/etc/matplotlib/matplotlibrc` changes the figures, and OpenBLAS's runtime kernel choice
  (SkylakeX here) changes the JSON floats; the manifest records hashes of the other outputs
  and follows both. It comes neither from package versions, nor from the Python patch level
  (3.10.20 here reproduces the committed bytes with the two settings), nor from numpy's own
  SIMD dispatch.
- The machine that produced the committed outputs and the CI runner both render with
  matplotlib's built-in settings and get the same floats as the Haswell kernels.
- The job's verdict does not depend on either cause: the SkylakeX and Inter run here passes
  `--check`, its floats differ from the committed ones by at most 7.8e-16, about 14 orders
  of magnitude below the tolerances (0.06 and 0.08), and `REPRO_OUT` keeps all outputs out of
  the checkout.

## HYPOTHESIS

The runner's CPU has no AVX-512, so its OpenBLAS uses Haswell-class kernels. On a runner
where OpenBLAS selects SkylakeX, the job would print this container's hashes and still pass.

## WHAT WOULD FALSIFY THIS?

- A rerun of the job on `3f19431`, or on a later commit that does not touch `reproduction/`,
  `results/observer/`, `requirements-lock.txt` or the job, that fails or prints other values.
- A green job after a value in `reproduction/EXPECTED.json` or `CANONICAL` is moved outside
  its tolerance.
- For the drift causes: a rerun here of the run with both matplotlib defaults and
  `OPENBLAS_CORETYPE=Haswell` that does not give the committed bytes.
- For the hypothesis: a runner whose OpenBLAS reports the SkylakeX core and prints the
  committed hashes, or a failed `primary-repro` job on such a runner.

## Failures and dead ends

- The first `runtime_lock acquire`, run with the system `python3`, failed on `import numpy`
  and left no lock; it was rerun with the venv interpreter.
- The image has no `python3.10` and no `/usr/bin/time`: `uv python install 3.10` and
  `date +%s` were used instead.
- `git fetch origin main auto/primary-repro-ci` failed with "couldn't find remote ref" before
  the branch existed on the remote; remote state was then read with `git ls-remote`.
- The first local simulation of the steps used `bash -eo pipefail`, while the runner uses
  `bash -e`. The steps contain no pipe, so the outcome is the same.
- The first PR #41 description implied that the committed PNGs no longer reproduce. They do:
  the runner prints their exact hashes, and the drift is specific to this container
  (OBSERVED). The description is corrected after this push.

## Decisions

- `actions/checkout@v5` and `actions/setup-python@v6` only in the new job, as the task asks;
  the `tests` and `container` jobs keep v4 and v5. Their upgrade is left as a follow-up
  backlog task.
- `timeout-minutes: 15` for a job that takes 76–82 s.
- The trigger `on: [push, pull_request]` is unchanged: it is the owner's decision (ROADMAP §4
  H4, audit in PR #33). The job therefore runs twice for each push to a PR branch.
- `REPRO_OUT="$RUNNER_TEMP/repro"`, as the task asks: the clean-tree step then checks that the
  job writes nothing into the checkout, whatever the output bytes are on a given machine (the
  in-place run rewrote 7 of 10 tracked files).
- No `OPENBLAS_CORETYPE` or matplotlib setting in the job: the tolerance checks do not need
  them, and they would only make the bytes match where they are set.
- No change to `reproduction/`, `release/`, the manuscript, `EXPECTED.json` or `CANONICAL`.
  The deep-h2 lower bound reads −0.785 here and −0.79 in `CANONICAL` (tolerance 0.10); the
  rounding is already explained in `docs/paper/full/HEADLINE_NUMBER_ERRATUM.md:46-48`.
- No self-merge (Authority). `docs/PROJECT_STATE.md`, `docs/EXPERIMENT_INDEX.md` and
  `docs/DECISION_LOG.md` are not updated: no experiment ran and no scientific state changed.

## Unresolved risks

- ROADMAP §4 H4 still holds: CI does not run `pytest tests/`. The H4 text, a dated snapshot,
  does not mention this job.
- The `tests` and `container` jobs still use `actions/checkout@v4` (`nasi-ci.yml:11`, `:36`)
  and `actions/setup-python@v5` (`:12`). That v5 and v6 run on Node 24 comes from the task
  text; this run did not check it.
- `requirements-lock.txt` pins 3 of the 13 installed packages, and `setup-python` takes the
  latest 3.10 patch (3.10.22 on the runner; the lockfile comment and `release/ENVIRONMENT.md`
  name 3.10.12). A release of a transitive dependency can change the installed set.
- `pyproject.toml:9` requires Python >= 3.11, while this job and the release reproduction run
  on 3.10; the job does not install the package.
- `reproduction/test_canonical.py` prints "4 frozen numbers" while it checks 8 entries.
- `release/ENVIRONMENT.md` states byte-identical CSV/JSON "on the same numpy build". Here the
  same numpy wheel gives different JSON bytes (CSV identical) when OpenBLAS selects SkylakeX,
  and `release/README_RELEASE.md` tells readers to run in place, so a reader with an AVX-512
  CPU, or with a site matplotlibrc, sees tracked outputs change while every value stays within
  tolerance. Whether to document this is the owner's call.
- Draft PR #40 also adds a top row to `docs/RUN_INDEX.md`: whichever of #40 and #41 merges
  second will conflict there (keep both rows, newest first).

## Handoff

Run tests: the four job steps pass locally on `3e0e13b` and in both CI runs on `3f19431`.
pytest was not run in this session; its last records, on the same code, are 1,487 passed, 8
failed, 22 skipped at `c81ea31` and in the PR #40 baseline on `3e0e13b`, the two commits
differing only by a journal. The CI result on the final head of `auto/primary-repro-ci` is in
the PR #41 description.

Next authorized action: after the owner merges PR #41, the follow-up backlog task: move the
`tests` and `container` jobs of `nasi-ci.yml` to `actions/checkout@v5` (lines 11 and 36) and
`actions/setup-python@v6` (line 12) without changing their steps; done when every `uses:` in
the file is v5 or v6 and the four jobs are green on the PR.
