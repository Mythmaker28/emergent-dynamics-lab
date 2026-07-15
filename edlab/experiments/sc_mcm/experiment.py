"""Central multi-channel experiment. Isolates the MEMORY read-out by transplanting memory into a COMMON
erased body B0 and settling in a neutral environment: the two channels then re-express the memory as a
resting multi-axis signature R=[size,rg,uptake,mass,mean_c]. m_plus drives uptake; m_minus drives
attractant production (mean_c). Channel-specific ablation (lam_plus / lam_minus -> 0) removes only the
associated axis. Erase, transplant, turnover, clone-ceiling as regressions. Resumable."""
from __future__ import annotations

import os, pickle, sys, time
import numpy as np

from . import config as C
from . import harness as H
from .engine import MultiChannelMemoryEngine, MCParams
from ..sc_iom import harness as IH
from ..sc_hmc.harness import PulseChaseTracer

OUT = os.environ.get("SC_MCM_OUT", "/tmp/sc_mcm")
BUDGET = float(os.environ.get("SC_BUDGET", "37"))
os.makedirs(OUT, exist_ok=True)
RS = np.array(C.RESP_SCALE)


def _load(p, d): return pickle.load(open(p, "rb")) if os.path.exists(p) else d
def _save(p, o):
    with open(p, "wb") as f: pickle.dump(o, f)


class _NoisyMC(MultiChannelMemoryEngine):
    def __init__(self, spec, mem, tracer, rng):
        super().__init__(spec, mem, tracer); self.rng = rng
    def step(self, st):
        out = super().step(st)
        out.N = out.N * np.exp(C.CLONE_NOISE_SIGMA * self.rng.standard_normal(out.N.shape))
        out.c = out.c * np.exp(C.CLONE_NOISE_SIGMA * self.rng.standard_normal(out.c.shape))
        return out


def transplant_mean(recipient, donor_mem):
    out = recipient.copy(); e = H.largest(out)
    if e is None: return out
    ys, xs = e.cells[:, 0], e.cells[:, 1]
    for k in range(out.Mf.shape[0]):
        out.Mf[k, ys, xs] = out.rho[ys, xs] * donor_mem[k]
    return out


def _feat5(st):
    return H._feat(st) / RS


def read_signature(eng, B0, donor_mem, settle=80):
    b = transplant_mean(B0, donor_mem)
    b = H.advance(eng, b, settle)
    return _feat5(b)


def central(seed) -> dict:
    eng = H.mc_engine()
    eng_min0 = H.mc_engine(MCParams(lam_plus=C.MC.lam_plus, lam_minus=0.0))   # ablate order channel
    eng_all0 = H.mc_engine(MCParams(lam_plus=0.0, lam_minus=0.0))              # ablate both channels
    S = H.warmup(seed)
    r = {"seed": seed}
    states = {h: H.advance(eng, IH.apply_history(eng, S, hist), C.SETTLE) for h, hist in C.HISTORIES.items()}
    if any(H.largest(s) is None for s in states.values()):
        r["valid"] = False; return r
    r["valid"] = True
    mem = {h: H.entity_memory(states[h]) for h in states}
    r["mem"] = {h: mem[h].tolist() for h in states}
    r["pm"] = {h: H.entity_pm(states[h]).tolist() for h in states}
    r["sizes"] = {h: int(H.largest(states[h]).size) for h in states}

    B0 = H.erase_memory(states["H4"])       # common neutral body
    Rv = {h: read_signature(eng, B0, mem[h]) for h in states}
    Rbase = read_signature(eng, B0, np.zeros(2))
    clones = [read_signature(_NoisyMC(C.SPEC, C.MC, C.TRACER, np.random.default_rng(80000 + 101 * seed + k)),
                             B0, mem["H1"]) for k in range(C.N_CLONE)]
    r["D_clone"] = float(np.median([H.D(Rv["H1"], ck) for ck in clones]))
    r["D_clone_caxis"] = float(np.median([abs(Rv["H1"][4] - ck[4]) for ck in clones]))
    # readouts
    r["dose_readout"] = H.D(Rv["H1"], Rv["H4"])              # m_plus channel (dose vs neutral)
    r["order_readout"] = H.D(Rv["H1"], Rv["H2"])             # full-vector order (A->B vs B->A)
    r["order_readout_caxis"] = abs(Rv["H1"][4] - Rv["H2"][4])  # m_minus channel (attractant axis)
    r["order_readout_uaxis"] = abs(Rv["H1"][2] - Rv["H2"][2])  # m_plus channel (uptake axis)
    r["erase_baseline_dist"] = H.D(Rv["H1"], Rbase)          # erased memory -> baseline (erase effect)
    # channel ablation
    Rv_min0 = {h: read_signature(eng_min0, B0, mem[h]) for h in ("H1", "H2")}
    r["order_caxis_ablate_minus"] = abs(Rv_min0["H1"][4] - Rv_min0["H2"][4])   # should collapse
    r["order_uaxis_ablate_minus"] = abs(Rv_min0["H1"][2] - Rv_min0["H2"][2])   # uptake axis should remain
    Rv_all0 = {h: read_signature(eng_all0, B0, mem[h]) for h in ("H1", "H2")}
    r["order_readout_ablate_all"] = H.D(Rv_all0["H1"], Rv_all0["H2"])          # ~0 (no memory channel)
    # turnover: apply H1/H4, replace material, read order signature via transplant of turned-over memory
    pc = MultiChannelMemoryEngine(C.SPEC, C.MC, PulseChaseTracer())
    def turned(h):
        stt = H.advance(pc, _relabel(IH.apply_history(eng, S, C.HISTORIES[h])), C.TURNOVER_STEPS)
        e = H.largest(stt)
        M = float(np.asarray(e.cohort_mass)[0] / np.asarray(e.cohort_mass).sum()) if e else 1.0
        return (H.entity_memory(stt), M)
    (m1t, Mt) = turned("H1"); (m2t, _) = turned("H2")
    r["turnover_M"] = Mt
    r["turnover_order_caxis"] = abs(read_signature(eng, B0, m1t)[4] - read_signature(eng, B0, m2t)[4])
    return r


def _relabel(st):
    out = st.copy(); out.C = np.stack([out.rho.copy(), np.zeros_like(out.rho)]); return out


def run(split="dev"):
    t0 = time.time()
    seeds = C.DEV_TRAJ if split == "dev" else C.PROSP_TRAJ
    p = f"{OUT}/central_{split}.pkl"; done = _load(p, []); seen = {d["seed"] for d in done}
    for s in seeds:
        if s in seen: continue
        if time.time() - t0 > BUDGET:
            print(f"BUDGET {len(done)}/{len(seeds)}; rerun", flush=True); return
        done.append(central(s)); _save(p, done)
    print((f"COMPLETE {split} " if len(done) >= len(seeds) else "PROGRESS ") + f"{len(done)}/{len(seeds)}", flush=True)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "dev")
