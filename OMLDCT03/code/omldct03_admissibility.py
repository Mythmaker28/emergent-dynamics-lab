"""OMLDCT03 — le compte d'admissibilite, sous les criteres GELES d'OMLDCT02.

Rien ici n'est choisi par moi. Les deux classificateurs sont ceux d'OMLDCT02, appeles et non
reimplementes ; la regle d'admissibilite est celle de la qualification gelee : une paire est
admissible si et seulement si les DEUX classificateurs rendent OK sur les DEUX bras et
s'accordent EXACTEMENT sur les deux criteres.

t_m et l'ensemble de cellules de la fille verrouillee sont des ENTREES, prises du registre gele de
TBRT02 et identiques dans les deux bras par construction — le prefixe s[0..t_m] est identique bit
a bit et l'intervention est appliquee apres la ligne t_m.

Ce fichier ecrit DEUX sorties separees :
  OMLDCT03_ADMISSIBILITY.json  — le compte, et rien d'autre
  work/omldct03_pairs.json     — les durees, qui ne sont PAS regardees tant que la porte des 41
                                 n'est pas franchie
"""
from __future__ import annotations
import os, sys, json, glob, subprocess

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
os.environ.setdefault("OMLDCT02_REPO", REPO)
os.environ.setdefault("LDFMA01_REPO", REPO)
sys.path.insert(0, os.path.join(REPO, "LDFMA01/code"))
sys.path.insert(0, os.path.join(REPO, "OMLDCT02/code"))
import numpy as np
import omldct02_e3_a as AA
import omldct02_e3_b as B
import omldct02_hashes as H

RAW = "/home/claude/TBRT02_raw"
ARMS = ("SELECTIVE", "SHAM")


def seeds():
    rows = [json.loads(l) for p in sorted(glob.glob(f"{REPO}/TBRT02/work/TBRT02_SEALED_LEDGER_*.jsonl"))
            for l in open(p) if l.strip()]
    return sorted([r for r in rows if r.get("ADMISSIBLE")], key=lambda x: x["index"])


def one_seed(r):
    out = {"index": int(r["index"]), "ARMS": {}}
    tms, dcs = set(), set()
    for a in ARMS:
        d = r["ARCHIVES"][a]
        path = os.path.join(RAW, os.path.basename(d["path"]))
        z = np.load(path, allow_pickle=True)
        meta = json.loads(str(z["meta"][0])); z.close()
        t_m = int(meta["t_m"])
        cells = [(int(c[0]), int(c[1])) for c in meta["intervention"]["daughter_cells"]]
        tms.add(t_m); dcs.add(tuple(sorted(cells)))
        ra = AA.e3(path, t_m, cells)
        rb = B.e3(path, t_m, cells)
        agree = (bool(ra.get("OK")) and bool(rb.get("OK"))
                 and ra.get("E3_DURATION") == rb.get("E3_DURATION")
                 and ra.get("E3_EXPOSURE") == rb.get("E3_EXPOSURE"))
        out["ARMS"][a] = {"t_m": t_m, "n_daughter_cells": len(cells),
                          "A_OK": bool(ra.get("OK")), "B_OK": bool(rb.get("OK")),
                          "A_REASON": ra.get("REASON"), "B_REASON": rb.get("REASON"),
                          "CLASSIFIERS_AGREE_EXACTLY": agree,
                          "_A": ra, "_B": rb}
    out["t_m_identical_across_arms"] = (len(tms) == 1)
    out["daughter_cells_identical_across_arms"] = (len(dcs) == 1)
    out["ADMISSIBLE_PAIR"] = bool(out["t_m_identical_across_arms"]
                                  and out["daughter_cells_identical_across_arms"]
                                  and all(out["ARMS"][a]["CLASSIFIERS_AGREE_EXACTLY"] for a in ARMS))
    return out


def main():
    rs = seeds()
    res = [one_seed(r) for r in rs]
    n_adm = sum(1 for r in res if r["ADMISSIBLE_PAIR"])
    reasons = {}
    for r in res:
        if r["ADMISSIBLE_PAIR"]:
            continue
        for a in ARMS:
            v = r["ARMS"][a]
            if not v["CLASSIFIERS_AGREE_EXACTLY"]:
                key = f"{a}:{v['A_REASON'] or v['B_REASON'] or 'CLASSIFIERS_DISAGREE_ON_A_VALUE'}"
                reasons[key] = reasons.get(key, 0) + 1

    doc = {
     "MISSION": "OMLDCT03",
     "SECTION": "1 — compte d'admissibilite sous les criteres GELES d'OMLDCT02",
     "GENERATED_UTC": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%S+00:00"],
                                     capture_output=True, text=True).stdout.strip(),
     "AUTHORISATION": "OMLDCT03/out/OMLDCT03_HUMAN_AUTHORISATION.json",
     "LA_REGLE_APPLIQUEE_EST_CELLE_D_OMLDCT02_ET_N_EST_PAS_LA_MIENNE": {
       "MINIMUM_VALID_PAIR_COUNT": 41,
       "une_paire_est_admissible_si": ("les deux classificateurs geles rendent OK sur les DEUX "
         "bras et s'accordent EXACTEMENT sur E3_DURATION et E3_EXPOSURE"),
       "classificateur_A": "OMLDCT02/code/omldct02_e3_a.py, appele, non reimplemente",
       "classificateur_B": "OMLDCT02/code/omldct02_e3_b.py, appele, non reimplemente",
       "une_graine_donne_au_plus_une_paire": True},
     "N_BASE_SEEDS": len(res),
     "N_ADMISSIBLE_PAIRS": n_adm,
     "MINIMUM_VALID_PAIR_COUNT": 41,
     "GATE_MAY_THE_FROZEN_TEST_RUN": bool(n_adm >= 41),
     "RAISONS_DE_NON_ADMISSIBILITE": reasons,
     "PAR_GRAINE": [{"index": r["index"], "ADMISSIBLE_PAIR": r["ADMISSIBLE_PAIR"],
                     "t_m_identical": r["t_m_identical_across_arms"],
                     "daughter_cells_identical": r["daughter_cells_identical_across_arms"],
                     **{f"{a}_agree": r["ARMS"][a]["CLASSIFIERS_AGREE_EXACTLY"] for a in ARMS}}
                    for r in res],
     "AUCUNE_DUREE_N_EST_RAPPORTEE_DANS_CE_FICHIER": True,
     "POURQUOI": ("le compte d'admissibilite ne revele pas le resultat du test. Il est ecrit et "
                  "commite SEUL, avant que la moindre duree soit regardee."),
    }
    doc["ADMISSIBILITY_CONTENT_HASH"] = H.content_digest(
        doc, extra_excluded=("ADMISSIBILITY_CONTENT_HASH",))
    json.dump(doc, open(f"{REPO}/OMLDCT03/out/OMLDCT03_ADMISSIBILITY.json", "w"),
              indent=1, ensure_ascii=False)
    # les durees vont dans work/, non regardees tant que la porte n'est pas franchie
    json.dump(res, open(f"{REPO}/OMLDCT03/work/omldct03_pairs.json", "w"), indent=1)
    return doc


if __name__ == "__main__":
    d = main()
    print("graines           :", d["N_BASE_SEEDS"])
    print("paires admissibles:", d["N_ADMISSIBLE_PAIRS"], "/ requis", d["MINIMUM_VALID_PAIR_COUNT"])
    print("PORTE             :", "OUVERTE" if d["GATE_MAY_THE_FROZEN_TEST_RUN"] else "FERMEE")
    if d["RAISONS_DE_NON_ADMISSIBILITE"]:
        print("raisons           :", json.dumps(d["RAISONS_DE_NON_ADMISSIBILITE"], ensure_ascii=False))
