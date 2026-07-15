"""Central experiment: isolate the MEMORY's causal effect from history-induced physical-state changes.
Clean counterfactuals hold the body fixed and vary only memory:
  ERASE    : same body, memory -> 0  => memory's causal contribution to that body's response
  TRANSPLANT into a COMMON erased body B0 => pure history-written memory readout (snapshot-identical)
  SCRAMBLE : spatial memory permuted (same body)
  ABLATION : lam_m=0 -> the memory channel is off; effects must vanish (G14)
Memory (m) access is a privileged diagnostic; the causal claims rest on behaviour, not on reading m.
Resumable. Physics: frozen base + memory extension only.
"""
from __future__ import annotations

import os
import pickle
import sys
import time

import numpy as np

from . import config as C
from . import harness as H
from .engine import MemoryScaffoldEngine, MemParams
from ..sc_hmc.harness import PulseChaseTracer
from ..sc_hmc import interventions as INT

OUT = os.environ.get("SC_IOM_OUT", "/tmp/sc_iom")
BUDGET = float(os.environ.get("SC_BUDGET", "37"))
os.makedirs(OUT, exist_ok=True)
SCALE = np.array([5.0, 1.0, 0.01, 5.0])


def _load(p, d): return pickle.load(open(p, "rb")) if os.path.exists(p) else d
def _save(p, o):
    with open(p, "wb") as f: pickle.dump(o, f)


class _NoisyMemEngine(MemoryScaffoldEngine):
    def __init__(self, spec, mem, tracer, rng):
        super().__init__(spec, mem, tracer); self.rng = rng
    def step(self, st):
        out = super().step(st)
        out.N = out.N * np.exp(C.CLONE_NOISE_SIGMA * self.rng.standard_normal(out.N.shape))
        out.c = out.c * np.exp(C.CLONE_NOISE_SIGMA * self.rng.standard_normal(out.c.shape))
        return out


def noisy_engine(seed, k, mem=None):
    return _NoisyMemEngine(C.SPEC, mem or C.MEM, C.TRACER, np.random.default_rng(70000 + 101 * seed + k))


def settle(eng, st): return H.advance(eng, st, C.SETTLE)


def _feat(st):
    e = H.largest(st)
    return np.array([e.size, e.rg, e.specific_uptake, e.mass]) if e else np.zeros(4)


def probe_response(eng, st):
    field, op, amp, dur = C.PROBE
    cur = st.copy(); out = []
    for t in range(1, C.PROBE_HORIZON + 1):
        if t <= dur:
            cur = INT._perturb(cur, field, op, amp)
        cur = eng.step(cur)
        if t % C.PROBE_CADENCE == 0:
            out.append(_feat(cur))
    return np.asarray(out) / SCALE


def _D(a, b):
    m = min(len(a), len(b))
    return float(np.linalg.norm((a[:m] - b[:m]).ravel()) / np.sqrt(m)) if m else 0.0


def erase_memory(st):
    out = st.copy(); out.Mf = np.zeros_like(out.Mf); return out


def transplant_mean(recipient, donor_mem):
    """Set the recipient entity's memory to the donor's mean (m1,m2) uniformly (aligned, clean transplant)."""
    out = recipient.copy(); e = H.largest(out)
    if e is None:
        return out
    ys, xs = e.cells[:, 0], e.cells[:, 1]
    for k in range(out.Mf.shape[0]):
        out.Mf[k, ys, xs] = out.rho[ys, xs] * donor_mem[k]
    return out


def scramble_memory(st):
    out = st.copy(); e = H.largest(out)
    if e is None: return out
    ys, xs = e.cells[:, 0], e.cells[:, 1]
    perm = np.random.default_rng(12345).permutation(len(ys))
    for k in range(out.Mf.shape[0]):
        v = out.Mf[k, ys, xs].copy(); out.Mf[k, ys, xs] = v[perm]
    return out


def relabel_pc(st):
    out = st.copy(); out.C = np.stack([out.rho.copy(), np.zeros_like(out.rho)]); return out


def central(seed) -> dict:
    eng = H.mem_engine()
    S = H.warmup(seed)
    r = {"seed": seed}
    states = {h: settle(eng, H.apply_history(eng, S, hist)) for h, hist in C.HISTORIES.items()}
    if any(H.largest(s) is None for s in states.values()):
        r["valid"] = False; return r
    r["valid"] = True
    mem = {h: H.entity_memory(states[h]) for h in states}
    r["mem"] = {h: mem[h].tolist() for h in states}

    nat = {h: probe_response(eng, states[h]) for h in states}
    era = {h: probe_response(eng, erase_memory(states[h])) for h in ("H1", "H4")}
    clone = [probe_response(noisy_engine(seed, k), states["H1"]) for k in range(C.N_CLONE)]
    r["D_clone"] = float(np.median([_D(nat["H1"], ck) for ck in clone]))

    # memory causal effect on native bodies (erase, same snapshot): G6/G7
    r["E_erase_H1"] = _D(nat["H1"], era["H1"])
    r["E_erase_H4"] = _D(nat["H4"], era["H4"])

    # COMMON-body transplant (snapshot-identical B0): pure history-written memory readout
    B0 = erase_memory(states["H4"])
    resp_B0 = probe_response(eng, B0)
    tp = {h: probe_response(eng, transplant_mean(B0, mem[h])) for h in states}
    r["readout_H1"] = _D(tp["H1"], resp_B0)          # G6 causal readout (history memory vs empty, same body)
    r["readout_H4"] = _D(tp["H4"], resp_B0)
    r["order_sep"] = _D(tp["H1"], tp["H2"])          # G5 temporal order A->B vs B->A, common body
    r["mem_order_sep"] = float(np.linalg.norm(mem["H1"] - mem["H2"]))
    r["hist_disc"] = _D(tp["H1"], tp["H4"])          # history vs neutral memory, common body

    # transplant transfer onto a DIFFERENT native body (G8): H1 memory into H2's body
    tp_cross = probe_response(eng, transplant_mean(states["H2"], mem["H1"]))
    r["transplant_effect"] = _D(tp_cross, nat["H2"])
    r["transplant_shift_frac"] = float(1 - _D(tp_cross, tp["H1"]) / (_D(nat["H2"], tp["H1"]) + 1e-9))

    # scramble (spatial memory organization): same body
    r["scramble_effect"] = _D(probe_response(eng, scramble_memory(states["H1"])), nat["H1"])

    # ablation (G14): lam_m=0 -> erase effect must vanish
    eng0 = H.mem_engine(MemParams(lam_m=0.0, eta_w=C.MEM.eta_w))
    S0 = H.warmup(seed, MemParams(lam_m=0.0, eta_w=C.MEM.eta_w))
    st0 = settle(eng0, H.apply_history(eng0, S0, C.HISTORIES["H1"]))
    r["ablation_E_erase"] = _D(probe_response(eng0, st0), probe_response(eng0, erase_memory(st0)))

    # turnover (G9/G16): H1 body, material replaced (pulse-chase), memory dynamics active
    pc = MemoryScaffoldEngine(C.SPEC, C.MEM, PulseChaseTracer())
    stt = H.advance(pc, relabel_pc(H.apply_history(eng, S, C.HISTORIES["H1"])), C.TURNOVER_STEPS)
    et = H.largest(stt)
    if et is not None:
        cm = np.asarray(et.cohort_mass, float)
        r["turnover_M"] = float(cm[0] / cm.sum()) if cm.sum() > 0 else 1.0
        # memory-effect after turnover = erase on the turned-over body (holds body fixed)
        r["turnover_E_erase"] = _D(probe_response(pc, stt), probe_response(pc, erase_memory(stt)))
        r["turnover_mem"] = H.entity_memory(stt).tolist()
        r["turnover_keep_frac"] = float(r["turnover_E_erase"] / (r["E_erase_H1"] + 1e-9))
    return r


def run(split="dev"):
    t0 = time.time()
    seeds = (C.DEV_TRAJ[:16] if split == "dev" else C.PROSP_TRAJ[:8])
    p = f"{OUT}/central_{split}.pkl"
    done = _load(p, []); seen = {d["seed"] for d in done}
    for s in seeds:
        if s in seen: continue
        if time.time() - t0 > BUDGET:
            print(f"BUDGET {len(done)}/{len(seeds)}; rerun", flush=True); return
        done.append(central(s)); _save(p, done)
    print((f"COMPLETE {split} " if len(done) >= len(seeds) else f"PROGRESS ") + f"{len(done)}/{len(seeds)}", flush=True)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "dev")
