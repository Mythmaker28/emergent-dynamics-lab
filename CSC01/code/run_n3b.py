"""CSC01 — evaluate N3b against the observation, from data already on disk. No replay."""
from __future__ import annotations

import json
import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/CSC01/code")

import observe as OBS            # noqa: E402
import protocol as P             # noqa: E402

import null_n3b as NB            # noqa: E402
import nulls as NU               # noqa: E402

OUT = "/home/claude/CSC01/out"
L = P.POINT["L"]
P_HOP = P.POINT["p_hop_X"]
MU = P.POINT["muX"]
ELL = 2.5
DRAWS = 200
METRICS = ("r50", "r80", "Rg_pairwise", "main_mass_fraction", "n_eff_components",
           "core_fraction_within_2ellX")


def main():
    d = json.load(open(f"{OUT}/_autopsy_repaired.json"))
    F = list(OBS.Recorder.FIELDS)
    out = []
    for a in d["arms"]:
        tag = a["tag"]
        npz = np.load("/home/claude/ORR01/raw/%s.npz" % tag.replace("/", "__"))
        births = npz["series"][:, F.index("accepted_births_X")]
        ft = a["frame_trace"]
        org_steps = np.array([f["step"] for f in ft], dtype=np.int64)
        org_traj = np.array([[f["organiser_y"], f["organiser_x"]] for f in ft], dtype=np.int64)
        keep = org_traj[:, 0] >= 0
        org_steps, org_traj = org_steps[keep], org_traj[keep]
        if len(org_steps) < 5:
            out.append({"tag": tag, "applicable": False, "reason": "no organiser trajectory"})
            continue
        idxs = np.linspace(0, len(ft) - 1, 9).astype(int)
        rows = []
        for j, i in enumerate(idxs):
            f = ft[i]
            t, N_X = int(f["step"]), int(f["N_X"])
            if N_X <= 0 or f["organiser_y"] < 0:
                continue
            dist = NB.n3b_distribution(DRAWS, a["seed"] * 7919 + j, L, ELL,
                                       N_X=N_X, t=t, births=births, org_traj=org_traj,
                                       org_steps=org_steps, p_hop=P_HOP, mu=MU)
            if not dist:
                continue
            rec = {"step": t, "N_X": N_X, "observed": {}, "null_q": {}, "position": {}}
            for m in METRICS:
                o = f.get(m if m != "Rg_pairwise" else "Rg_pairwise")
                if o is None or not np.isfinite(float(o)):
                    continue
                v = dist[m][np.isfinite(dist[m])]
                rec["observed"][m] = float(o)
                rec["null_q"][m] = NU.quantiles(v)
                rec["position"][m] = float((v <= float(o)).mean())
            rows.append(rec)
        summ = {m: {"mean_observed_quantile": float(np.mean([r["position"][m] for r in rows
                                                            if m in r["position"]])),
                    "n_instants": sum(1 for r in rows if m in r["position"])}
                for m in METRICS}
        out.append({"tag": tag, "seed": a["seed"], "applicable": True,
                    "per_instant": rows, "summary": summ})
    json.dump({"draws": DRAWS, "arms": out,
               "definition": NB.__doc__}, open(f"{OUT}/_null_n3b.json", "w"), indent=1)

    print(f"{'seed':<5s} {'r50':>7s} {'r80':>7s} {'Rg':>7s} {'mainF':>7s} {'Neff':>7s} {'core2l':>7s}")
    print("observed quantile inside N3b (0 = far more compact than the no-interaction null)")
    for o in out:
        if not o["applicable"]:
            continue
        s = o["summary"]
        print(f"{o['seed']:<5d} " + " ".join(f"{s[m]['mean_observed_quantile']:>7.3f}"
                                             for m in METRICS))
    print()
    for o in out:
        if not o["applicable"]:
            continue
        r = o["per_instant"][len(o["per_instant"]) // 2]
        print(f"seed {o['seed']} at step {r['step']}: observed r80={r['observed']['r80']:.2f} "
              f"Rg={r['observed']['Rg_pairwise']:.2f} | N3b r80 "
              f"[q05={r['null_q']['r80']['0.05']:.2f} q50={r['null_q']['r80']['0.5']:.2f} "
              f"q95={r['null_q']['r80']['0.95']:.2f}] Rg "
              f"[q05={r['null_q']['Rg_pairwise']['0.05']:.2f} "
              f"q50={r['null_q']['Rg_pairwise']['0.5']:.2f} "
              f"q95={r['null_q']['Rg_pairwise']['0.95']:.2f}]")


if __name__ == "__main__":
    main()
