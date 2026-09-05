"""RPP98 — la mesure. Refuse de tourner si le test de capacité ne l'a pas autorisée.

Lit les 123 archives scellées de TBRT02. N'en lance aucun monde. Pour chaque archive :

    s[:,0] = t              s[:,7] = n_components   (les deux colonnes, sur les 11 000 pas)
    k_t, k_ncells           pour masse_parent = max des k_ncells au pas t_start - 1
    meta.t_m, meta.arm, meta.index

Ce que le fichier de sortie contient et que RPP97 n'avait pas : la vérification, archive par
archive, que la série est bien complète et contiguë. Si elle ne l'est pas, ce n'est pas corrigé
en silence — c'est écrit dans le résultat.
"""
from __future__ import annotations
import os, sys, json, glob
import numpy as np

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "RPP98/code"))
import rpp98_episodes as E

RAW = "/home/claude/TBRT02_raw"
HORIZON_EXPECTED = 11000


def one(path):
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["meta"][0]))
    t_m = int(meta["t_m"])
    srow = z["s"].astype(np.int64)
    kt = z["k_t"].astype(np.int64)
    knc = z["k_ncells"].astype(np.int64)
    z.close()

    t = srow[:, 0].tolist()
    nc = srow[:, 7].tolist()

    # intégrité de la série, écrite et non supposée
    contiguous = all(t[i] == t[i - 1] + 1 for i in range(1, len(t)))
    integ = {"n_steps": len(t), "t_first": t[0] if t else None, "t_last": t[-1] if t else None,
             "contiguous": bool(contiguous),
             "n_steps_is_horizon": bool(len(t) == HORIZON_EXPECTED),
             "steps_executed_meta": int(meta.get("steps_executed", -1)),
             "n_zero_steps": int(sum(1 for v in nc if v == 0)),
             "t_first_zero": next((tt for tt, v in zip(t, nc) if v == 0), None)}

    # masse_parent : le plus grand k_ncells à chaque pas
    mass = {}
    for tt, ncl in zip(kt.tolist(), knc.tolist()):
        if ncl > mass.get(tt, -1):
            mass[tt] = ncl

    eps = E.annotate(E.episodes(t, nc), t_m=t_m, mass_by_step=mass)
    after = [e for e in eps if e["t_start"] > t_m]
    return {"index": int(meta["index"]), "arm": meta["arm"], "t_m": t_m,
            "seed": int(meta.get("seed", -1)),
            "INTEGRITY": integ,
            "n_episodes": len(eps),
            "n_persistants": sum(1 for e in eps if e["persistant"]),
            "n_tardifs": len(after),
            "n_tardifs_persistants": sum(1 for e in after if e["persistant"]),
            "pas_a_deux_ou_plus": sum(e["duree"] for e in eps),
            "fraction_du_temps": sum(e["duree"] for e in eps) / float(HORIZON_EXPECTED),
            "n_max_global": max((e["n_max"] for e in eps), default=0),
            "EPISODES": eps}


def main(out_path, shard, nshards):
    rows = [json.loads(l) for p in sorted(glob.glob(f"{REPO}/TBRT02/work/TBRT02_SEALED_LEDGER_*.jsonl"))
            for l in open(p) if l.strip()]
    adm = sorted([r for r in rows if r.get("ADMISSIBLE")], key=lambda x: x["index"])
    jobs = [(r["index"], a, os.path.join(RAW, os.path.basename(d["path"])))
            for r in adm for a, d in sorted(r["ARCHIVES"].items())]
    jobs = [j for i, j in enumerate(jobs) if i % nshards == shard]
    res = []
    for idx, arm, path in jobs:
        res.append(one(path))
        r = res[-1]
        print(json.dumps({"index": idx, "arm": arm, "n_ep": r["n_episodes"],
                          "pers": r["n_persistants"], "tard": r["n_tardifs"],
                          "tard_pers": r["n_tardifs_persistants"],
                          "frac": round(r["fraction_du_temps"], 4),
                          "ok": r["INTEGRITY"]["contiguous"] and r["INTEGRITY"]["n_steps_is_horizon"]}),
              flush=True)
        json.dump(res, open(out_path, "w"))


if __name__ == "__main__":
    cap = json.load(open(f"{REPO}/RPP98/out/RPP98_CAPABILITY.json"))
    assert cap["MEASUREMENT_MAY_PROCEED"], "le test de capacite n'a pas autorise la mesure"
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
