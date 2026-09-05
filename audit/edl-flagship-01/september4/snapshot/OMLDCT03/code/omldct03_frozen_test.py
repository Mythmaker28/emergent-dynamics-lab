"""OMLDCT03 — l'execution du test GELE d'OMLDCT02 sur les 41 paires de TBRT02.

Rien dans ce fichier n'est un choix scientifique de ma part. La retention des paires, la
convention de signe, la difference des logs et la decision sont celles d'OMLDCT02, recopiees de
omldct02_c3_raw.analyse() et appelees, pour la decision, via omldct02_analysis.decide() INCHANGE.

La seule chose que ce fichier fait de neuf, c'est de pointer le pipeline vers les archives de
TBRT02 au lieu de celles d'OMLDCT02 — ce qui est exactement ce que l'autorisation humaine couvre.

REGLE DE RETENTION GELEE, verbatim d'omldct02_c3_raw.measure() :
    les deux classificateurs rendent OK, ET s'accordent sur E3_DURATION, E3_EXPOSURE
    ET sur identity_termination_type, dans LES DEUX bras.
Mon compte d'admissibilite (commite en 384333f) omettait le type de terminaison. Il est ajoute
ici, et s'il fait tomber le compte sous 41, le test NE S'EXECUTE PAS.
"""
from __future__ import annotations
import os, sys, json, math, subprocess

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02/code"))
import omldct02_analysis as AN          # decide(), midranks(), exact_two_sided_p() — INCHANGE
import omldct02_hashes as H

ARMS = ("SELECTIVE", "SHAM")


def main():
    adm = json.load(open(f"{REPO}/OMLDCT03/out/OMLDCT03_ADMISSIBILITY.json"))
    assert adm["GATE_MAY_THE_FROZEN_TEST_RUN"], "la porte d'admissibilite n'est pas ouverte"
    pairs = json.load(open(f"{REPO}/OMLDCT03/work/omldct03_pairs.json"))

    retained, dropped = [], []
    for m in pairs:
        ok = True
        for a in ARMS:
            A_, B_ = m["ARMS"][a]["_A"], m["ARMS"][a]["_B"]
            if not (A_.get("OK") and B_.get("OK")
                    and A_["E3_DURATION"] == B_["E3_DURATION"]
                    and A_["E3_EXPOSURE"] == B_["E3_EXPOSURE"]
                    and A_["identity_termination_type"] == B_["identity_termination_type"]):
                ok = False
        (retained if ok else dropped).append(m)

    n = len(retained)
    dur, exp, table = [], [], []
    for m in retained:
        ds = m["ARMS"]["SELECTIVE"]["_A"]["E3_DURATION"]; dh = m["ARMS"]["SHAM"]["_A"]["E3_DURATION"]
        es = m["ARMS"]["SELECTIVE"]["_A"]["E3_EXPOSURE"]; eh = m["ARMS"]["SHAM"]["_A"]["E3_EXPOSURE"]
        dd = math.log(ds) - math.log(dh) if ds > 0 and dh > 0 else (0.0 if ds == dh else None)
        de = math.log(es) - math.log(eh) if es > 0 and eh > 0 else (0.0 if es == eh else None)
        dur.append(dd); exp.append(de)
        table.append({"index": m["index"], "t_m": m["ARMS"]["SELECTIVE"]["t_m"],
                      "SELECTIVE_duration": ds, "SHAM_duration": dh, "log_duration_difference": dd,
                      "SELECTIVE_exposure": es, "SHAM_exposure": eh, "log_exposure_difference": de,
                      "SELECTIVE_termination": m["ARMS"]["SELECTIVE"]["_A"]["identity_termination_type"],
                      "SHAM_termination": m["ARMS"]["SHAM"]["_A"]["identity_termination_type"]})

    undefined = [t["index"] for t in table
                 if t["log_duration_difference"] is None or t["log_exposure_difference"] is None]
    res = AN.decide(dur, exp, n) if (not undefined and n >= AN.MINIMUM_VALID_PAIR_COUNT) else None

    doc = {
     "MISSION": "OMLDCT03",
     "SECTION": "2 — execution du test GELE d'OMLDCT02 sur les 41 paires de TBRT02",
     "GENERATED_UTC": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%S+00:00"],
                                     capture_output=True, text=True).stdout.strip(),
     "AUTHORISATION": "OMLDCT03/out/OMLDCT03_HUMAN_AUTHORISATION.json",
     "ADMISSIBILITY_CONTENT_HASH": adm["ADMISSIBILITY_CONTENT_HASH"],
     "LE_GEL_APPLIQUE": {
       "source": "OMLDCT02/out/OMLDCT02_MASTER_FREEZE.json, 2026-08-25T22:30:05",
       "PRIMARY_ENDPOINT": "paired post-intervention duration of the same locked daughter identity",
       "COPRIMARY_ENDPOINT": "paired post-intervention locked-daughter particle-step exposure",
       "SIGN_CONVENTION": "SELECTIVE minus SHAM, on the paired log difference",
       "PAIRED_TEST": "two-sided exact Wilcoxon signed-rank with Pratt ranking",
       "ALPHA": AN.ALPHA, "MINIMUM_VALID_PAIR_COUNT": AN.MINIMUM_VALID_PAIR_COUNT,
       "decide_est_appele_INCHANGE": "OMLDCT02/code/omldct02_analysis.py:decide"},
     "REGLE_DE_RETENTION_COMPLETE_INCLUANT_LE_TYPE_DE_TERMINAISON": True,
     "N_PAIRS_MEASURED": len(pairs), "N_PAIRS_RETAINED": n,
     "DROPPED_INDICES": [m["index"] for m in dropped],
     "PAIRS_WITH_AN_UNDEFINED_LOG_DIFFERENCE": undefined,
     "PER_PAIR": table,
     "DECISION": res,
     "TERMINAL": (res["TERMINAL"] if res else "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS"),
     "NULL_RESULT_INTERPRETATION": "INCONCLUSIVE__NO_CLAIM_OF_EQUIVALENCE__NO_CLAIM_OF_NO_EFFECT",
     "CE_QUE_CE_TEST_NE_DIT_PAS": (
       "il ne porte pas sur la reproduction, ni sur l'heredite, ni sur ce que ces objets sont. Il "
       "compare la duree et l'exposition d'UNE identite nommee avant l'intervention, entre un bras "
       "ou son parent est retire et un bras ou rien n'est fait, sur la meme graine."),
     "STATUTS_INCHANGES": {
       "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
       "HEREDITY_STATUS": "NOT_TESTED", "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
       "X_LAWSPEC_BASELINE": "UNCHANGED", "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
       "COMPANION_PAPER_V1_1_STATUS": "UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
       "CLEA01_STATUS": "CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED",
       "TBRT02_STATUS": "CLOSED__RAW_COMPLETE__PRIMARY_ADJUDICATION_INCONCLUSIVE_BY_CONSTRUCTION",
       "RPP97_STATUS": "WITHDRAWN_AS_A_DESCRIPTION__ARITHMETIC_SOUND__SCIENCE_MIS_SPECIFIED",
       "RPP98_STATUS": "WITHDRAWN__THE_QUESTION_WAS_ALREADY_ANSWERED_BY_TLMR01__AND_THE_COUNTED_EVENT_IS_NOT_THE_CLAIMED_EVENT",
       "FIMRCC02_STATUS": "WITHDRAWN__A_PREREGISTERED_TEST_ALREADY_EXISTS__AND_THE_CENTRAL_PREMISE_IS_FALSE_BY_DEFINITION",
       "FIMRCC01_E3_E4_E5_STATUS": "FUTURE_QUESTION_RECORDED__NOT_AUTHORISED"},
     "VOCABULAIRE": "rien ici ne porte sur ce que ces objets sont.",
    }
    doc["RESULT_CONTENT_HASH"] = H.content_digest(doc, extra_excluded=("RESULT_CONTENT_HASH",))
    json.dump(doc, open(f"{REPO}/OMLDCT03/out/OMLDCT03_FROZEN_TEST_RESULT.json", "w"),
              indent=1, ensure_ascii=False)
    return doc


if __name__ == "__main__":
    d = main()
    print("paires retenues :", d["N_PAIRS_RETAINED"], "/ requis", AN.MINIMUM_VALID_PAIR_COUNT)
    print("ecartees        :", d["DROPPED_INDICES"])
    r = d["DECISION"]
    if r:
        for k in ("duration", "exposure"):
            v = r[k]
            print(f"{k:9s} p = {v['exact_two_sided_p']:.6f} | mediane = {v['median_difference']:+.4f} "
                  f"| HL = {v['hodges_lehmann']:+.4f} {tuple(round(x,4) for x in v['hl_interval'])} "
                  f"| zeros {v['n_zero']} | rejette {v['rejects']}")
        print("les deux rejettent :", r["both_reject"], "| directions concordantes :", r["direction_concordant"])
        print("REGLE ET          :", r["AND_RULE_PASSES"])
    print("TERMINAL          :", d["TERMINAL"])
    print("hash              :", d["RESULT_CONTENT_HASH"][:16])
