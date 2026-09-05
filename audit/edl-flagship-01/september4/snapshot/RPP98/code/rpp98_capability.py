"""RPP98 — test de capacité. Exécuté AVANT l'ouverture de la moindre archive.

RPP97 a été retirée en partie parce que sa fenêtre de contrôle était vide par construction et
que personne ne l'avait vérifié avant. Ici le détecteur est exercé sur des séries dont la réponse
est connue par construction, y compris sur les cas où une erreur ne se verrait pas :

  frontières      un épisode qui touche le premier pas, un qui touche le dernier ;
  adjacence       deux plateaux séparés par UN SEUL pas à 1 doivent faire DEUX épisodes ;
  seuil           duree 249 n'est pas persistant, duree 250 l'est — l'inegalite est >= ;
  trous           un pas manquant dans t doit COUPER l'épisode, jamais le recoller ;
  extinction      n_components = 0 interrompt un épisode exactement comme 1 ;
  n_max           une valeur qui monte à 3 au milieu d'un plateau doit être relevée ;
  nullité         le détecteur doit pouvoir rendre ZÉRO épisode, et doit pouvoir rendre
                  BEAUCOUP d'épisodes dont AUCUN persistant — c'est la borne de trivialité de la
                  section 5 du pré-enregistrement. Un détecteur incapable de produire ce second
                  résultat ne pourrait pas rapporter le nul recevable de la section 6.

Si un seul cas échoue, MEASUREMENT_MAY_PROCEED est faux et la mesure ne se fait pas.
"""
from __future__ import annotations
import os, sys, json, subprocess

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "RPP98/code"))
import rpp98_episodes as E

CASES = []


def case(name, t, nc, expect, note=""):
    got = E.episodes(t, nc)
    got_c = [{"t_start": e["t_start"], "t_end": e["t_end"], "duree": e["duree"],
              "n_max": e["n_max"]} for e in got]
    CASES.append({"case": name, "note": note, "expected": expect, "got": got_c,
                  "PASS": got_c == expect})


def run():
    # 1. série constante à 1 -> zéro épisode
    case("constante_a_1", list(range(100)), [1] * 100, [],
         "le monde reste un seul amas : aucun épisode")

    # 2. un plateau de longueur exacte connue
    t = list(range(100)); nc = [1] * 100
    for i in range(30, 47): nc[i] = 2          # 17 pas
    case("un_plateau_de_17", t, nc, [{"t_start": 30, "t_end": 46, "duree": 17, "n_max": 2}],
         "longueur exacte, bornes exactes")

    # 3. deux plateaux séparés -> deux épisodes
    t = list(range(100)); nc = [1] * 100
    for i in range(10, 15): nc[i] = 2
    for i in range(60, 63): nc[i] = 2
    case("deux_plateaux_separes", t, nc,
         [{"t_start": 10, "t_end": 14, "duree": 5, "n_max": 2},
          {"t_start": 60, "t_end": 62, "duree": 3, "n_max": 2}], "deux, pas un")

    # 4. créneau d'un seul pas -> un épisode de durée 1
    t = list(range(50)); nc = [1] * 50; nc[20] = 2
    case("creneau_un_pas", t, nc, [{"t_start": 20, "t_end": 20, "duree": 1, "n_max": 2}],
         "durée 1, non persistant : vérifié plus bas")

    # 5. deux plateaux séparés par UN SEUL pas à 1 -> DEUX épisodes
    t = list(range(50)); nc = [1] * 50
    for i in range(10, 20): nc[i] = 2
    for i in range(21, 30): nc[i] = 2
    case("separes_par_un_seul_pas", t, nc,
         [{"t_start": 10, "t_end": 19, "duree": 10, "n_max": 2},
          {"t_start": 21, "t_end": 29, "duree": 9, "n_max": 2}],
         "l'erreur classique serait d'en faire un seul de 20")

    # 6. épisode qui touche le premier pas
    t = list(range(40)); nc = [1] * 40
    for i in range(0, 6): nc[i] = 2
    case("bord_gauche", t, nc, [{"t_start": 0, "t_end": 5, "duree": 6, "n_max": 2}],
         "commence au tout premier pas de la série")

    # 7. épisode qui touche le dernier pas
    t = list(range(40)); nc = [1] * 40
    for i in range(35, 40): nc[i] = 2
    case("bord_droit", t, nc, [{"t_start": 35, "t_end": 39, "duree": 5, "n_max": 2}],
         "un épisode encore ouvert à la fin doit être fermé et rapporté")

    # 8. n_max relevé au milieu d'un plateau
    t = list(range(40)); nc = [1] * 40
    for i in range(10, 20): nc[i] = 2
    nc[14] = 3; nc[15] = 4
    case("n_max_au_milieu", t, nc, [{"t_start": 10, "t_end": 19, "duree": 10, "n_max": 4}],
         "un seul épisode, n_max = 4")

    # 9. extinction : n_components = 0 coupe l'épisode
    t = list(range(40)); nc = [1] * 40
    for i in range(10, 15): nc[i] = 2
    nc[15] = 0
    for i in range(16, 19): nc[i] = 2
    case("zero_coupe", t, nc,
         [{"t_start": 10, "t_end": 14, "duree": 5, "n_max": 2},
          {"t_start": 16, "t_end": 18, "duree": 3, "n_max": 2}],
         "zéro n'est pas une absence de donnée, c'est Y éteint")

    # 10. trou dans t : l'épisode est coupé, jamais recollé
    t = [i for i in range(20)] + [i for i in range(25, 40)]
    nc = [2] * len(t)
    case("trou_dans_t", t, nc,
         [{"t_start": 0, "t_end": 19, "duree": 20, "n_max": 2},
          {"t_start": 25, "t_end": 39, "duree": 15, "n_max": 2}],
         "cinq pas manquants : deux épisodes, pas un de 40")

    out = {"MISSION": "RPP98",
           "SECTION": "test de capacité, exécuté avant l'ouverture de toute archive",
           "PREREGISTRATION": "RPP98/out/RPP98_PREREGISTRATION.md",
           "GENERATED_UTC": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%S+00:00"],
                                           capture_output=True, text=True).stdout.strip(),
           "MULTI_MIN": E.MULTI_MIN, "PERSISTENT_MIN_DUREE": E.PERSISTENT_MIN_DUREE,
           "CASES": CASES}

    # 11. le seuil de persistance, des deux côtés
    def dur(n):
        t = list(range(n + 10)); nc = [1] * (n + 10)
        for i in range(5, 5 + n): nc[i] = 2
        e = E.annotate(E.episodes(t, nc), t_m=10**9)
        return e[0]

    e249, e250, e251 = dur(249), dur(250), dur(251)
    out["SEUIL_DE_PERSISTANCE"] = {
        "duree_249": {"duree": e249["duree"], "persistant": e249["persistant"]},
        "duree_250": {"duree": e250["duree"], "persistant": e250["persistant"]},
        "duree_251": {"duree": e251["duree"], "persistant": e251["persistant"]}}
    out["SEUIL_EST_UN_SUPERIEUR_OU_EGAL"] = (e249["persistant"] is False
                                             and e250["persistant"] is True
                                             and e251["persistant"] is True)

    # 12. tardif / chevauche : bornes strictes autour de t_m
    t = list(range(100)); nc = [1] * 100
    for i in range(40, 50): nc[i] = 2
    a = E.annotate(E.episodes(t, nc), t_m=45)[0]     # t_m dedans
    b = E.annotate(E.episodes(t, nc), t_m=40)[0]     # commence EN t_m
    c = E.annotate(E.episodes(t, nc), t_m=39)[0]     # commence APRÈS t_m
    d = E.annotate(E.episodes(t, nc), t_m=60)[0]     # entièrement avant t_m
    out["TARDIF_ET_CHEVAUCHEMENT"] = {
        "t_m_au_milieu": {"chevauche": a["chevauche_t_m"], "tardif": a["tardif"]},
        "commence_exactement_en_t_m": {"chevauche": b["chevauche_t_m"], "tardif": b["tardif"]},
        "commence_un_pas_apres_t_m": {"chevauche": c["chevauche_t_m"], "tardif": c["tardif"]},
        "entierement_avant_t_m": {"chevauche": d["chevauche_t_m"], "tardif": d["tardif"]}}
    out["TARDIF_EST_STRICT"] = (a["chevauche_t_m"] and not a["tardif"]
                                and b["chevauche_t_m"] and not b["tardif"]
                                and c["tardif"] and not c["chevauche_t_m"]
                                and not d["tardif"] and not d["chevauche_t_m"])

    # 13. masse_parent : lue au pas t_start - 1, None si ce pas n'existe pas
    t = list(range(40)); nc = [1] * 40
    for i in range(0, 4): nc[i] = 2          # touche le premier pas -> pas de t_start-1
    for i in range(20, 24): nc[i] = 2
    mass = {19: 137, 3: 999}
    ann = E.annotate(E.episodes(t, nc), t_m=10, mass_by_step=mass)
    out["MASSE_PARENT"] = {"episode_au_premier_pas": ann[0]["masse_parent"],
                           "episode_a_t_start_20": ann[1]["masse_parent"],
                           "valeur_attendue_a_19": mass[19]}
    out["MASSE_PARENT_EST_LUE_AU_BON_PAS"] = (ann[0]["masse_parent"] is None
                                              and ann[1]["masse_parent"] == 137)

    # 14. le détecteur peut rendre le nul recevable de la section 6 :
    #     beaucoup d'épisodes, aucun persistant.
    t = list(range(1000)); nc = [2 if i % 2 == 0 else 1 for i in range(1000)]
    flick = E.annotate(E.episodes(t, nc), t_m=0)
    out["BORNE_DE_TRIVIALITE"] = {
        "serie": "alternance 2,1,2,1 sur 1000 pas",
        "n_episodes": len(flick),
        "duree_max": max(e["duree"] for e in flick),
        "n_persistants": sum(1 for e in flick if e["persistant"])}
    out["PEUT_RENDRE_BEAUCOUP_ET_AUCUN_PERSISTANT"] = (len(flick) == 500
                                                       and out["BORNE_DE_TRIVIALITE"]["n_persistants"] == 0)
    # ... et peut rendre un persistant tardif, l'autre issue de la section 6
    t = list(range(11000)); nc = [1] * 11000
    for i in range(5000, 5600): nc[i] = 2
    one = E.annotate(E.episodes(t, nc), t_m=1000)
    out["PEUT_RENDRE_UN_PERSISTANT_TARDIF"] = (len(one) == 1 and one[0]["persistant"]
                                               and one[0]["tardif"] and one[0]["duree"] == 600)

    out["ALL_CASES_PASS"] = all(c["PASS"] for c in CASES)
    out["MEASUREMENT_MAY_PROCEED"] = bool(
        out["ALL_CASES_PASS"] and out["SEUIL_EST_UN_SUPERIEUR_OU_EGAL"]
        and out["TARDIF_EST_STRICT"] and out["MASSE_PARENT_EST_LUE_AU_BON_PAS"]
        and out["PEUT_RENDRE_BEAUCOUP_ET_AUCUN_PERSISTANT"]
        and out["PEUT_RENDRE_UN_PERSISTANT_TARDIF"])
    out["NO_ARCHIVE_WAS_OPENED_TO_PRODUCE_THIS_FILE"] = True
    return out


def sealed():
    sys.path.insert(0, os.path.join(REPO, "OMLDCT02/code"))
    import omldct02_hashes as H
    d = run()
    d["CODE_SHA256"] = {p: H.file_sha256(os.path.join(REPO, p)) for p in
                        ("RPP98/code/rpp98_episodes.py", "RPP98/code/rpp98_capability.py")}
    d["CAPABILITY_CONTENT_HASH"] = H.content_digest(d, extra_excluded=("CAPABILITY_CONTENT_HASH",))
    return d


if __name__ == "__main__":
    print(json.dumps(sealed(), indent=1, ensure_ascii=False))
