# FCDDH01R dependency firewall

21 python modules audited across the child root and `_work/`. Banned constructs (`eval`, `exec`, `compile`, `__import__`, `importlib`, `runpy`, `globals`, `locals`, `vars`, `setattr`, `delattr`): none, except the single inherited declared allowlist entry — one `setattr` inside an oracle negative control that REQUIRES a `PermissionError`.

Violations: **0**.

Direction of dependence is unchanged from the parent: `fh_ref` imports nothing from `fh_core`; the hold-out scorer imports neither the trainer nor any historical direction and contains no eig/svd/pca/lstsq/pinv; the trainer accepts only twelve ascending discovery ancestries and only paths under the **child** work root, so every FCDDH00 path is now rejected (DEX9). The engineering layer (`DURABLE_PHASE_SUPERVISOR`, `EXACT_ONCE_PHASE_STATE_MACHINE`, `fr_*`) contains no scientific formula, no estimand, no threshold and no reader, and the DEX dummy worker imports only hashlib, json, os, sys and time — no path to any project engine.

## Module hashes

* `DURABLE_PHASE_SUPERVISOR.py` — `138334612d4ce75b1794f36a775e5338f86ced75426c22b1e481f9f70285d1af`
* `EXACT_ONCE_PHASE_STATE_MACHINE.py` — `a9cd877a8468ea2167eb16712285c7ee13631f8570104cacb2721ddc9847788d`
* `_work/DISCOVERY_AXIS_TRAINER_V1.py` — `f92354ce608caab797e5899f20efb35e3c05990876951fe4191f985ff3d53310`
* `_work/EXACT_RANDOMIZATION_ENUMERATOR_V1.py` — `894cf81fd1fb75035e2cf4dd66f9648b5ea26e8caa6d7994e7b821ae5a73f0d1`
* `_work/HOLDOUT_FIXED_AXIS_SCORER_V1.py` — `3355378fe23517e8533763b4c66f32c0aa8417d049aad5f53af5cccf6e7cb4fe`
* `_work/fh_aworker.py` — `308d80bfdca331cdbd953db0ae7ba896df13942f0592810bb5ffb2bbea7c6d08`
* `_work/fh_core.py` — `fdc80f984689a01ecfac482bfa7b8efee1dc47c407918052dd4ff0849545f4e6`
* `_work/fh_cworker.py` — `226b7301548ab997d0576c5fe1bb43eb713567a94e47088a0fe1ac1a696f1a05`
* `_work/fh_decode.py` — `d2fe65b200f47d5eed8e9c24960075e853de7d739830026a7ecf18d1de704967`
* `_work/fh_disc.py` — `e2da7cbe9c8873c00932a5d2d8e6bd04c86c08e47af508006486c022f6887c3d`
* `_work/fh_hold.py` — `0d96888c0715f50b4a6f1aaa786a52981915323046453b9bd1f9c2981f9f2270`
* `_work/fh_oracle.py` — `e06bbbe784e8d4f89de676923010a2e9459a4e3f04b66014ba0b089fbc4f3615`
* `_work/fh_p0.py` — `7fe1c6bb59692122b584167e67813d26bbe24bae38a364d10f5914a16209433c`
* `_work/fh_rand.py` — `d3b031c8709f01a30024f11a373b3b78e6fb399a259fd0f38c6103625d2ff01f`
* `_work/fh_ref.py` — `a8eff74a6028b48ff0a0447ab0440406b3d3a7122211108c42c6605de12258e9`
* `_work/fh_runner.py` — `f1144e17c3dd4d2a5f55726b9cddb71430f17ccd51ae1155d588cc15b6e4a5b0`
* `fr_dex.py` — `fb93b168387cd06a672efe133a88fbe8c6f3f1a21b38cf6b608045c61143c03c`
* `fr_docs.py` — `8f5e4c25ec7669e1a0da23fbf7916ba9f6f5dabc862a55f04b175eeab2be31f4`
* `fr_dummy.py` — `e46279fae1935e3f96ac624dc8a2cc532a06dc1f1d47851b5b14f584310ab859`
* `fr_p0.py` — `a8e830cbb8f45b4714fa07af6db558b1ab2536382554c76b3404f0566ce75ff1`
* `fr_plan.py` — `d55c9ac83354962d8aecda27d6812c14ed2630b83e186aab138c3495f6e8553d`
