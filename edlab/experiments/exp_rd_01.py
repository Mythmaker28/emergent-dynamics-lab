"""EXP-RD-01: blind low-discrepancy map over (F,k,Du,Dv), MATCHED OPEN vs the EXACT CLOSED limit.

CLOSED = the exact controlled limit F=k=0 (same Du, Dv, same seed): no feed, no removal, U+V conserved. It is the
matched control for openness. Frozen tracer (8 spatial + 8 temporal feed cohorts, tau=250; D-029), frozen field
P/M and thresholds (P>0.8, M<0.5), no composite score, no visual selection.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from ..entities.tracking import LineageTracker
from ..specs import TrackerSpec
from ..substrates.reaction_diffusion.engine import GrayScottSpec, RDEngine, TracerSpec
from ..substrates.reaction_diffusion.observables import (
    RDDetectionSpec, RDPhenotypeSpec, detect_rd_entities, to_entity_observation,
    rd_material_retention, rd_phenotype_continuity,
)
from .baseline import halton_point
from .exp_rd_00 import rates
from .exp_rd_00b import rd_state_t

TRACER = TracerSpec()          # FROZEN (D-029)


@dataclass(frozen=True)
class EXPRD01Config:
    n_laws: int = 24
    seeds: tuple[int, ...] = (10001, 10002, 10003)
    conditions: tuple[str, ...] = ("CLOSED", "OPEN")
    size: int = 64
    steps: int = 1500
    cadence: int = 50
    lag_indices: tuple[int, ...] = (1, 3, 6)
    enroll_min_obs: int = 8

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        for k in ("seeds", "conditions", "lag_indices"):
            d[k] = list(d[k])
        d["tracer"] = TRACER.as_dict()
        return d


def rd_law_from_halton(law_index: int, size: int = 64) -> tuple[GrayScottSpec, GrayScottSpec]:
    """Blind Halton law -> (OPEN spec, matched EXACT-CLOSED spec with the same diffusion)."""
    p = halton_point(law_index + 32, 4)
    F = float(0.010 + 0.050 * p[0])
    k = float(0.040 + 0.030 * p[1])
    Du = float(0.10 + 0.10 * p[2])
    Dv = float(0.04 + 0.06 * p[3])
    open_spec = GrayScottSpec(size=size, Du=Du, Dv=Dv, F=F, k=k)
    closed_spec = GrayScottSpec(size=size, Du=Du, Dv=Dv, F=0.0, k=0.0)   # EXACT controlled limit
    return open_spec, closed_spec


def screen_one(cfg: EXPRD01Config, law_index: int, condition: str, seed: int) -> dict[str, Any]:
    open_spec, closed_spec = rd_law_from_halton(law_index, cfg.size)
    spec = open_spec if condition == "OPEN" else closed_spec
    eng = RDEngine(spec, TRACER)
    st = rd_state_t(spec, TRACER, seed)
    snaps = eng.simulate(st, cfg.steps, cfg.cadence)
    det = RDDetectionSpec(); phe = RDPhenotypeSpec()
    trk = LineageTracker(TrackerSpec(8.0, 0.25), box_size=spec.size)
    per: dict[int, list] = {}
    prod = []; act = []; n_ent = []
    for s in snaps:
        p, r, a = rates(spec, s)
        fes = detect_rd_entities(s.U, s.V, s.CV, p, r, a, snapshot_step=s.step, time=float(s.step),
                                 detection=det, phenotype_spec=phe)
        n_ent.append(len(fes))
        for e in fes:
            prod.append(e.phenotype.raw["production"]); act.append(abs(e.phenotype.raw["activity"]))
        tracked = trk.update([to_entity_observation(e) for e in fes], snapshot_step=s.step, time=float(s.step))
        by = {e.local_index: e for e in fes}
        for to in tracked:
            per.setdefault(to.track_id, []).append(by[to.entity.local_index])
    complex_tracks: set[int] = set()
    for e in trk.events:
        if e.kind in {"split", "merge", "ambiguous_association"}:
            complex_tracks |= set(e.parent_track_ids) | set(e.child_track_ids)
    n = 0; sP = 0.0; sM = 0.0; probe = 0; eligible = False; minM = 1.0
    for tid, fes in per.items():
        for lag in cfg.lag_indices:
            for i in range(len(fes) - lag):
                p_ = rd_phenotype_continuity(fes[i].phenotype, fes[i + lag].phenotype)
                m_ = rd_material_retention(fes[i].cohort_mass, fes[i + lag].cohort_mass)
                n += 1; sP += p_; sM += m_; minM = min(minM, m_)
                if p_ > 0.8 and m_ < 0.5:
                    probe += 1
                    if tid not in complex_tracks and len(fes) >= cfg.enroll_min_obs:
                        eligible = True
    tl = [len(v) for v in per.values()]
    return {"law_index": law_index, "condition": condition, "seed": seed, "n_meas": n,
            "mean_P": (sP / n) if n else None, "mean_M": (sM / n) if n else None, "min_M": minM,
            "probe_count": probe, "eligible_seed": eligible, "n_tracks": len(per),
            "max_track_obs": max(tl) if tl else 0,
            "long_tracks": int(sum(1 for L in tl if L >= cfg.enroll_min_obs)),
            "mean_production": float(np.mean(prod)) if prod else 0.0,
            "mean_activity": float(np.mean(act)) if act else 0.0,
            "mean_entities": float(np.mean(n_ent)) if n_ent else 0.0}


def screen_records(cfg: EXPRD01Config, law_indices) -> list[dict[str, Any]]:
    return [screen_one(cfg, li, c, s) for li in law_indices for c in cfg.conditions for s in cfg.seeds]


def assemble(cfg: EXPRD01Config, recs: list[dict[str, Any]]) -> dict[str, Any]:
    by = {}
    for cond in cfg.conditions:
        rs = [r for r in recs if r["condition"] == cond]
        elig = defaultdict(int)
        for r in rs:
            if r["eligible_seed"]:
                elig[r["law_index"]] += 1
        permitted = sorted(l for l, c in elig.items() if c >= 2)
        P = [r["mean_P"] for r in rs if r["mean_P"] is not None]
        M = [r["mean_M"] for r in rs if r["mean_M"] is not None]
        by[cond] = {"mean_P": float(np.mean(P)) if P else None, "mean_M": float(np.mean(M)) if M else None,
                    "median_min_M": float(np.median([r["min_M"] for r in rs])),
                    "frac_runs_minM_below_0p5": float(np.mean([r["min_M"] < 0.5 for r in rs])),
                    "total_probe": sum(r["probe_count"] for r in rs),
                    "n_eligible_seeds": sum(1 for r in rs if r["eligible_seed"]),
                    "screening_permitted_laws": permitted, "n_permitted": len(permitted),
                    "eligible_counts_by_law": {str(l): elig.get(l, 0) for l in sorted(elig)},
                    "mean_production": float(np.mean([r["mean_production"] for r in rs])),
                    "mean_activity": float(np.mean([r["mean_activity"] for r in rs])),
                    "mean_tracks": float(np.mean([r["n_tracks"] for r in rs]))}
    op, cl = by.get("OPEN", {}), by.get("CLOSED", {})
    decision = "EXP_RD_01_SCREEN_CANDIDATES" if op.get("n_permitted", 0) > 0 else "EXP_RD_01_SCREEN_NEGATIVE"
    return {"config": cfg.as_dict(), "by_condition": by, "decision": decision,
            "shift_OPEN_minus_CLOSED": {
                "d_mean_M": (op.get("mean_M") - cl.get("mean_M")) if op.get("mean_M") is not None and cl.get("mean_M") is not None else None,
                "d_median_min_M": op.get("median_min_M", 0) - cl.get("median_min_M", 0),
                "d_permitted": op.get("n_permitted", 0) - cl.get("n_permitted", 0),
                "d_mean_production": op.get("mean_production", 0) - cl.get("mean_production", 0)},
            "interpretation_levels": {"1_distributional_shift": "descriptive", "2_screening_signal": "permission, not candidate",
                                      "3_fresh_seed_recurrence": "next", "4_alias_rejection": "next",
                                      "5_causal_reestablishment": "next"},
            "boundary": ("P/M separate; no composite; thresholds frozen; CLOSED is the EXACT controlled limit. "
                         "Screening permission is NOT a candidate: it must pass fresh-seed hold-out, alias audit "
                         "(incl. imposed-pattern/occupancy), causal intervention WITH continued turnover, and "
                         "observer sensitivity.")}
