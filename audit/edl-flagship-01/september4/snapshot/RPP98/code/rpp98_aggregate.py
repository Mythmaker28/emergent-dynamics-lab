"""RPP98 — l'agrégation. Ce fichier est commité au même titre que la mesure : c'est le
manquement n°8 de RPP97, qui ne pouvait pas être régénérée depuis le dépôt.

Ne rapporte QUE les grandeurs fixées à la section 3 du pré-enregistrement. Tout ce qui n'y était
pas est marqué NON_PREENREGISTRE__CONTEXTE_SEUL et ne sert à rien conclure.
"""
from __future__ import annotations
import os, sys, json, glob, subprocess
import numpy as np

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02/code"))
sys.path.insert(0, os.path.join(REPO, "RPP98/code"))
import omldct02_hashes as H
import rpp98_episodes as E

HORIZON = 11000
ARMS = ("SHAM", "SELECTIVE", "DISPLACED")


def dist(v):
    """min, quartiles (numpy, interpolation linéaire), max — méthode nommée pour être refaite."""
    a = np.asarray([x for x in v if x is not None], dtype=np.float64)
    if a.size == 0:
        return {"n": 0}
    return {"n": int(a.size), "min": float(a.min()),
            "q1": float(np.percentile(a, 25, method="linear")),
            "median": float(np.percentile(a, 50, method="linear")),
            "q3": float(np.percentile(a, 75, method="linear")),
            "max": float(a.max()), "mean": float(a.mean())}


def main():
    rec = []
    for p in sorted(glob.glob(f"{REPO}/RPP98/work/shard*.json")):
        rec.extend(json.load(open(p)))
    rec.sort(key=lambda r: (r["index"], r["arm"]))
    assert len({(r["index"], r["arm"]) for r in rec}) == len(rec), "doublon archive"

    integ = {"n_archives": len(rec),
             "all_contiguous": all(r["INTEGRITY"]["contiguous"] for r in rec),
             "all_11000_steps": all(r["INTEGRITY"]["n_steps_is_horizon"] for r in rec),
             "n_archives_with_a_zero_step": sum(1 for r in rec if r["INTEGRITY"]["n_zero_steps"] > 0),
             "t_first_zero_dist": dist([r["INTEGRITY"]["t_first_zero"] for r in rec
                                        if r["INTEGRITY"]["t_first_zero"] is not None])}

    all_eps = [e for r in rec for e in r["EPISODES"]]
    late_eps = [e for r in rec for e in r["EPISODES"] if e["t_start"] > r["t_m"]]

    out = {
        "MISSION": "RPP98",
        "PREREGISTRATION": "RPP98/out/RPP98_PREREGISTRATION.md",
        "CAPABILITY": "RPP98/out/RPP98_CAPABILITY.json",
        "GENERATED_UTC": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%S+00:00"],
                                        capture_output=True, text=True).stdout.strip(),
        "QUESTION": ("les transitions vers deux composantes ou plus se produisent-elles ailleurs "
                     "que dans la fenetre selectionnee par le declencheur gele, et si oui : "
                     "combien, quand, et combien de temps la separation tient-elle"),
        "DEFINITIONS": {"MULTI_MIN": E.MULTI_MIN, "PERSISTENT_MIN_DUREE": E.PERSISTENT_MIN_DUREE,
                        "n_components": ("nombre de composantes de simple liaison toroidale des "
                                         "cellules Y-occupees, adjacence <= CORE_R = 5.0, "
                                         "FDOT01/code/fdot01_centres.components, ecrit dans s[:,7]"),
                        "n_components_zero": "Y eteint : aucune cellule occupee"},
        "INTEGRITE_DES_SERIES": integ,

        # --- section 3, dans l'ordre ou elle les a fixees ---
        "N_EPISODES_PAR_ARCHIVE": dist([r["n_episodes"] for r in rec]),
        "FRACTION_PERSISTANTS_PAR_ARCHIVE": dist(
            [r["n_persistants"] / r["n_episodes"] for r in rec if r["n_episodes"] > 0]),
        "DUREE_TOUS_EPISODES": dist([e["duree"] for e in all_eps]),
        "MASSE_PARENT_TOUS_EPISODES": dist([e["masse_parent"] for e in all_eps]),
        "N_EPISODES_TARDIFS_PAR_ARCHIVE": dist([r["n_tardifs"] for r in rec]),
        "MASSE_PARENT_EPISODES_TARDIFS": dist([e["masse_parent"] for e in late_eps]),
        "FRACTION_DU_TEMPS_PAR_ARCHIVE": dist([r["fraction_du_temps"] for r in rec]),

        "TOTAUX": {"n_episodes": len(all_eps),
                   "n_persistants": sum(1 for e in all_eps if e["persistant"]),
                   "n_tardifs": len(late_eps),
                   "n_tardifs_persistants": sum(1 for e in late_eps if e["persistant"]),
                   "n_chevauchant_t_m": sum(1 for e in all_eps if e["chevauche_t_m"]),
                   "n_archives_sans_episode": sum(1 for r in rec if r["n_episodes"] == 0),
                   "n_archives_sans_tardif": sum(1 for r in rec if r["n_tardifs"] == 0),
                   "n_archives_avec_tardif_persistant":
                       sum(1 for r in rec if r["n_tardifs_persistants"] > 0),
                   "n_max_global": max(r["n_max_global"] for r in rec)},
    }

    # --- par bras, APRES t_m uniquement (section 3, derniere puce) ---
    par_bras = {}
    for a in ARMS:
        sub = [r for r in rec if r["arm"] == a]
        eps_a = [e for r in sub for e in r["EPISODES"] if e["t_start"] > r["t_m"]]
        par_bras[a] = {
            "n_archives": len(sub),
            "N_EPISODES_TARDIFS_PAR_ARCHIVE": dist([r["n_tardifs"] for r in sub]),
            "N_TARDIFS_PERSISTANTS_PAR_ARCHIVE": dist([r["n_tardifs_persistants"] for r in sub]),
            "DUREE_EPISODES_TARDIFS": dist([e["duree"] for e in eps_a]),
            "MASSE_PARENT_EPISODES_TARDIFS": dist([e["masse_parent"] for e in eps_a]),
            "n_archives_avec_au_moins_un_tardif_persistant":
                sum(1 for r in sub if r["n_tardifs_persistants"] > 0)}
    out["PAR_BRAS_APRES_t_m"] = par_bras

    # --- section 5 : la borne de trivialite, lue et non affirmee ---
    dur = np.asarray([e["duree"] for e in all_eps], dtype=np.int64)
    out["BORNE_DE_TRIVIALITE"] = {
        "definition": ("si les episodes sont innombrables et longs de un ou deux pas, ils ne "
                       "decrivent qu'un scintillement du critere de liaison"),
        "n_episodes_duree_1": int((dur == 1).sum()),
        "n_episodes_duree_le_2": int((dur <= 2).sum()),
        "fraction_duree_le_2": float((dur <= 2).mean()) if dur.size else None,
        "n_episodes_duree_ge_250": int((dur >= 250).sum()),
        "fraction_des_pas_a_deux_ou_plus_passes_dans_un_episode_persistant":
            float(dur[dur >= 250].sum() / dur.sum()) if dur.sum() else None}

    # --- section 6 : lequel des deux nuls, si l'un des deux ---
    out["SECTION_6_NUL_1_aucun_persistant_tardif"] = bool(out["TOTAUX"]["n_tardifs_persistants"] == 0)
    out["SECTION_6_NUL_2_indistinguable_du_scintillement"] = bool(
        out["BORNE_DE_TRIVIALITE"]["n_episodes_duree_ge_250"] == 0)

    # --- contexte, hors pre-enregistrement : ne sert a rien conclure ---
    out["NON_PREENREGISTRE__CONTEXTE_SEUL"] = {
        "avertissement": ("ces chiffres n'etaient pas enumeres a la section 3 ; ils sont donnes "
                          "pour que le lecteur voie le denominateur et la chronologie, et sont "
                          "signales comme tels plutot que fondus dans les grandeurs gelees"),
        "fraction_du_temps_denominateur_11000_inclut_les_pas_ou_Y_est_eteint": True,
        "n_archives_ou_Y_s_eteint": integ["n_archives_with_a_zero_step"],
        "OMISSION_DE_LA_SECTION_3": ("la question de la section 1 demande COMBIEN, QUAND et "
                                     "COMBIEN DE TEMPS ; la section 3 a enumere le combien et le "
                                     "combien de temps mais a oublie d'enumerer le quand. "
                                     "t_start et n_max sont des attributs definis a la section 2 ; "
                                     "ils sont rapportes ici, sous cette etiquette, plutot que "
                                     "passes sous silence."),
        "t_start_TOUS_EPISODES": dist([e["t_start"] for e in all_eps]),
        "t_start_EPISODES_TARDIFS": dist([e["t_start"] for e in late_eps]),
        "t_start_EPISODES_TARDIFS_PERSISTANTS": dist([e["t_start"] for e in late_eps
                                                      if e["persistant"]]),
        "duree_EPISODES_TARDIFS_PERSISTANTS": dist([e["duree"] for e in late_eps
                                                    if e["persistant"]]),
        "n_max_TOUS_EPISODES": dist([e["n_max"] for e in all_eps]),
        "n_episodes_avec_n_max_ge_3": int(sum(1 for e in all_eps if e["n_max"] >= 3))}

    out["STATUTS_INCHANGES"] = {
        "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
        "HEREDITY_STATUS": "NOT_TESTED", "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
        "X_LAWSPEC_BASELINE": "UNCHANGED", "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
        "COMPANION_PAPER_V1_1_STATUS": "UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
        "OMLDCT02_STATUS": "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED",
        "CLEA01_STATUS": "CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED",
        "TBRT02_STATUS": "CLOSED__RAW_COMPLETE__PRIMARY_ADJUDICATION_INCONCLUSIVE_BY_CONSTRUCTION",
        "RPP97_STATUS": "WITHDRAWN_AS_A_DESCRIPTION__ARITHMETIC_SOUND__SCIENCE_MIS_SPECIFIED"}
    out["VOCABULAIRE"] = ("episode multi-composantes ; transition vers deux composantes. Jamais "
                          "division, ni corps qui se divise : rien ici ne distingue un objet qui "
                          "se scinde de deux amas qui derivent au-dela du rayon de liaison.")

    out["CODE_SHA256"] = {p: H.file_sha256(os.path.join(REPO, p)) for p in
                          ("RPP98/code/rpp98_episodes.py", "RPP98/code/rpp98_capability.py",
                           "RPP98/code/rpp98_measure.py", "RPP98/code/rpp98_aggregate.py")}
    out["CAPABILITY_CONTENT_HASH"] = json.load(
        open(f"{REPO}/RPP98/out/RPP98_CAPABILITY.json"))["CAPABILITY_CONTENT_HASH"]
    out["RESULT_CONTENT_HASH"] = H.content_digest(out, extra_excluded=("RESULT_CONTENT_HASH",))
    return out


if __name__ == "__main__":
    d = main()
    json.dump(d, open(f"{REPO}/RPP98/out/RPP98_RESULT.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in d.items() if k not in ("PAR_BRAS_APRES_t_m",)},
                     indent=1, ensure_ascii=False))
