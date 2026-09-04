"""FIMRCC02 — analyse de PUISSANCE, faite AVANT tout gel et sans ouvrir une seule archive.

FIMRCC01 a gele E3, E4 et E5 le 2026-08-25 comme contrastes APPARIES entre bras sur la meme
graine, puis ne les a pas autorises, pour une raison ecrite :

    « the inherited data contain no matched no-removal arm at LAW_C, anywhere in 512 worlds »

TBRT02 a construit ce bras : 41 graines, prefixe bit a bit identique jusqu'a t_m, puis SHAM sans
retrait contre SELECTIVE avec retrait. Le verrou nomme est tombe.

Mais FIMRCC01 note aussi, dans le meme fichier, que « their prospective power is therefore not
identified ». E1 et E2 sont morts de puissance. Avant de geler quoi que ce soit, on calcule donc
ce que 41 paires peuvent detecter — et ce qu'elles detecteraient a tort.

CE FICHIER N'OUVRE AUCUNE ARCHIVE. Il ne lit que le tableau de mortalite deja calcule et deja
publie dans RPP98/work (n_zero_steps par archive), et des lois binomiales exactes.
"""
from __future__ import annotations
import os, sys, json, glob, subprocess
from math import comb

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02/code"))
import omldct02_hashes as H


def binom_sf(k, n, p=0.5):
    """P(X >= k)"""
    return sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(k, n + 1))


def sign_test_two_sided(k, n):
    """p exact bilateral du test des signes : k succes sur n paires discordantes."""
    k = max(k, n - k)
    return min(1.0, 2 * binom_sf(k, n, 0.5))


def critical_k(n, alpha=0.05):
    """le plus petit k tel que le test bilateral soit significatif a alpha."""
    for k in range(n // 2, n + 1):
        if sign_test_two_sided(k, n) <= alpha:
            return k
    return None


def power_sign(n, p_true, alpha=0.05):
    """puissance du test des signes bilateral a n paires discordantes, sous P(paire favorable)=p."""
    k = critical_k(n, alpha)
    if k is None:
        return 0.0
    # rejet si X >= k ou X <= n-k
    return binom_sf(k, n, p_true) + (1 - binom_sf(n - k + 1, n, p_true))


def main():
    # --- la mortalite, lue et non supposee ---
    rec = []
    for p in sorted(glob.glob(f"{REPO}/RPP98/work/shard*.json")):
        rec.extend(json.load(open(p)))
    by = {}
    for r in rec:
        by.setdefault(r["index"], {})[r["arm"]] = r["INTEGRITY"]["n_zero_steps"]
    seeds = sorted(by)
    dead = {a: {s for s in seeds if by[s][a] > 0} for a in ("SHAM", "SELECTIVE", "DISPLACED")}
    S, SH = dead["SELECTIVE"], dead["SHAM"]
    sel_only, sham_only, both = len(S - SH), len(SH - S), len(S & SH)
    n_alive_pairs = len(seeds) - len(S | SH)

    # --- 1. le confondant : le test des signes sur la MORTALITE SEULE ---
    n_disc = sel_only + sham_only
    p_mortality_alone = sign_test_two_sided(sel_only, n_disc)

    out = {
        "MISSION": "FIMRCC02",
        "SECTION": "analyse de puissance, avant tout gel, AUCUNE ARCHIVE OUVERTE",
        "GENERATED_UTC": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%S+00:00"],
                                        capture_output=True, text=True).stdout.strip(),
        "LA_QUESTION_HERITEE": {
            "source": "FIMRCC01/out/FIMRCC01_ENDPOINT_PREREGISTRATION.json, 2026-08-25",
            "E3": ("le nombre de pas pendant lesquels l'intervalle d'identite de la fille survit "
                   "strictement apres t_m, compare ENTRE BRAS SUR LA MEME GRAINE"),
            "E4": ("le nombre de naissances Y et de morts Y attribuees a l'intervalle de la fille "
                   "apres t_m, compare ENTRE BRAS SUR LA MEME GRAINE"),
            "E5": ("le nombre d'intervalles satisfaisant le COMPLETE_TURNOVER gele n'importe ou "
                   "dans le monde apres t_m, compare ENTRE BRAS SUR LA MEME GRAINE"),
            "statut_en_2026_08_25": "FUTURE_QUESTION_RECORDED__NOT_AUTHORISED, sur les trois",
            "verrou_nomme": ("no matched no-removal arm at LAW_C, anywhere in 512 worlds"),
            "le_verrou_est_tombe": ("TBRT02 fournit 41 graines appariees, prefixe bit a bit "
                                    "identique jusqu'a t_m, SHAM sans retrait contre SELECTIVE"),
            "ce_que_FIMRCC01_notait_aussi": "their prospective power is therefore not identified",
        },

        "MORTALITE_PAR_BRAS": {
            "source": ("RPP98/work/shard*.json, champ INTEGRITY.n_zero_steps — deja calcule et "
                       "deja publie ; c'est une grandeur DEJA VUE et elle est declaree comme telle"),
            "n_graines": len(seeds),
            "Y_eteint_SHAM": sorted(SH), "Y_eteint_SELECTIVE": sorted(S),
            "Y_eteint_DISPLACED": sorted(dead["DISPLACED"]),
            "paires_SELECTIVE_mort_SHAM_vivant": sel_only,
            "paires_SHAM_mort_SELECTIVE_vivant": sham_only,
            "paires_les_deux_morts": both,
            "paires_les_deux_vivants": n_alive_pairs},

        "CONSTAT_1__LE_CONTRASTE_GELE_EST_SIGNIFICATIF_PAR_LA_SEULE_MORTALITE": {
            "raisonnement": ("dans un monde ou Y est eteint, les trois criteres valent leur "
                             "minimum par definition : l'intervalle de la fille ne survit pas, il "
                             "n'y a plus ni naissance ni mort de Y a lui attribuer, et aucun "
                             "intervalle ne peut satisfaire le turnover. La direction de la paire "
                             "est donc FORCEE, sans aucun effet sur la persistance de la fille."),
            "paires_discordantes_par_la_seule_mortalite": n_disc,
            "dont_en_faveur_de_SHAM": sel_only,
            "p_bilateral_du_test_des_signes": p_mortality_alone,
            "VERDICT": ("le contraste apparie SELECTIVE contre SHAM, tel que FIMRCC01 l'a gele, "
                        "retournerait « significatif » a p = %.4f sous l'hypothese nulle stricte "
                        "d'aucun effet sur la fille. Il ne distingue pas « la fille ne persiste "
                        "pas » de « retirer le parent tue le monde ». Ce sont deux affirmations "
                        "differentes et le critere gele les confond." % p_mortality_alone)},

        "CONSTAT_2__PUISSANCE_UNE_FOIS_LA_MORTALITE_CONDITIONNEE": {
            "design": ("restreindre aux paires ou les DEUX bras ont Y vivant apres t_m est la "
                       "seule facon de poser la question de la fille sans poser celle de la mort "
                       "du monde. Cela coute des paires et il faut le savoir avant de geler."),
            "n_paires_utilisables": n_alive_pairs,
            "test": "test des signes bilateral exact, alpha = 0.05",
        },
        "NO_ARCHIVE_WAS_OPENED_TO_PRODUCE_THIS_FILE": True,
    }

    # courbe de puissance sur les paires utilisables, en supposant toutes discordantes
    curve = {}
    for pt in (0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95):
        curve[f"{pt:.2f}"] = round(power_sign(n_alive_pairs, pt), 4)
    k = critical_k(n_alive_pairs)
    out["CONSTAT_2__PUISSANCE_UNE_FOIS_LA_MORTALITE_CONDITIONNEE"].update({
        "k_critique": k,
        "lecture_du_k_critique": (f"il faut {k} paires sur {n_alive_pairs} dans le meme sens, soit "
                                  f"{100*k/n_alive_pairs:.1f} pour cent, pour atteindre p <= 0.05"),
        "puissance_par_p_vrai_si_toutes_les_paires_sont_discordantes": curve,
        "p_vrai_minimal_pour_80_pourcent_de_puissance":
            next((float(x) for x, v in curve.items() if v >= 0.80), None),
    })
    # et si une fraction des paires est a egalite (comptes identiques), n discordantes baisse
    ties = {}
    for frac in (0.0, 0.25, 0.50):
        nd = int(round(n_alive_pairs * (1 - frac)))
        kk = critical_k(nd) if nd >= 6 else None
        ties[f"{int(frac*100)}_pourcent_d_egalites"] = {
            "n_discordantes": nd, "k_critique": kk,
            "puissance_a_p_vrai_0.80": round(power_sign(nd, 0.80), 4) if kk else None,
            "puissance_a_p_vrai_0.70": round(power_sign(nd, 0.70), 4) if kk else None}
    out["CONSTAT_3__SENSIBILITE_AUX_EGALITES"] = {
        "pourquoi": ("un contraste de COMPTES produit des egalites exactes, et le test des signes "
                     "les jette. Chaque egalite retire une paire. Voici le cout."),
        "table": ties}

    # --- E4 : sa loi marginale publiee borne deja son taux d'egalites ---
    out["CONSTAT_4__E4_EST_UN_COMPTE_TROP_ETROIT_POUR_UN_TEST_APPARIE"] = {
        "source": ("FIMRCC01/out/FIMRCC01_ENDPOINT_TABLE.json, publie le 2026-08-25 sur 22 mondes "
                   "— grandeur DEJA VUE, declaree comme telle"),
        "loi_marginale_publiee_de_E4": {"n_worlds": 22, "distinct_values": 6, "min": 0, "max": 5,
                                        "median": 1.0, "modal_value": 1,
                                        "fraction_at_the_modal_value": 0.3182},
        "l_argument": ("E4 prend six valeurs entieres entre 0 et 5, de mediane 1, avec 31,8 pour "
                       "cent de la masse sur la seule valeur 1. Deux tirages independants de cette "
                       "loi tombent a egalite avec une probabilite au moins egale a la somme des "
                       "carres des frequences, soit environ un quart. Or les deux bras d'une "
                       "graine ne sont PAS independants : ils partagent un prefixe bit a bit "
                       "identique jusqu'a t_m, ce qui ne peut qu'AUGMENTER le taux d'egalites."),
        "consequence": ("le taux d'egalites de E4 est donc superieur a 25 pour cent, "
                        "vraisemblablement bien au-dela. En lisant la table du constat 3 : a 25 "
                        "pour cent d'egalites la puissance a p_vrai = 0,70 tombe a 0,36 ; a 50 "
                        "pour cent elle tombe a 0,16."),
        "CE_N_EST_PAS_UNE_MESURE": ("c'est une borne deduite d'une loi marginale deja publiee. "
                                    "Aucune archive TBRT02 n'a ete ouverte pour l'obtenir, et la "
                                    "vraie valeur ne sera connue qu'en mesurant."),
        "E4_STATUT_PROSPECTIF": "SOUS_PUISSANT_SAUF_EFFET_TRES_LARGE",
        "E3_EST_DIFFERENT": ("E3 a 22 valeurs distinctes sur 22 mondes, min 31, mediane 230, max "
                             "1472 : c'est un compte large, ou les egalites exactes seront rares. "
                             "E3 est le seul des trois dont le test des signes ne perd pas ses "
                             "paires par egalite.")}

    out["CE_QUE_CETTE_ANALYSE_DECIDE"] = {
        "E3_E4_E5_TELS_QUE_GELES_SUR_SELECTIVE_CONTRE_SHAM":
            "NON_INTERPRETABLES__CONFONDUS_PAR_LA_MORTALITE_DIFFERENTIELLE",
        "LA_SEULE_VERSION_POSABLE": ("le meme contraste restreint aux paires ou les deux bras ont "
            f"Y vivant, soit {n_alive_pairs} paires, et alors seulement un effet tres large est "
            "detectable — ce qui doit etre ecrit au titre et non en note de bas de page"),
        "UNE_TROISIEME_VOIE_A_EXAMINER": ("le bras DISPLACED perd Y dans 5 graines contre 12 pour "
            "SELECTIVE ; le contraste DISPLACED contre SHAM est moins confondu, mais DISPLACED "
            "n'est pas le GLOBAL_OFF que le pre-enregistrement FIMRCC01 nommait, et cette "
            "substitution doit etre declaree avant tout gel, pas apres"),
        "CLASSEMENT_DES_TROIS": ("E3 est le seul candidat viable : compte large, egalites rares. "
            "E4 est sous-puissant par l'etroitesse de sa loi. E5 porte sur la population ambiante "
            "et E0 a montre que cette population sature — a verifier avant de le retenir."),
        "CE_QUI_SERAIT_MALHONNETE": ("geler E3/E4/E5 sur SELECTIVE contre SHAM, obtenir p < 0.01, "
            "et l'appeler un resultat sur la persistance de la fille. Le chiffre serait juste et "
            "la phrase serait fausse.")}

    out["STATUTS_INCHANGES"] = {
        "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
        "HEREDITY_STATUS": "NOT_TESTED", "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
        "X_LAWSPEC_BASELINE": "UNCHANGED", "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
        "COMPANION_PAPER_V1_1_STATUS": "UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
        "OMLDCT02_STATUS": "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED",
        "CLEA01_STATUS": "CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED",
        "TBRT02_STATUS": "CLOSED__RAW_COMPLETE__PRIMARY_ADJUDICATION_INCONCLUSIVE_BY_CONSTRUCTION",
        "RPP97_STATUS": "WITHDRAWN_AS_A_DESCRIPTION__ARITHMETIC_SOUND__SCIENCE_MIS_SPECIFIED",
        "RPP98_STATUS": ("WITHDRAWN__THE_QUESTION_WAS_ALREADY_ANSWERED_BY_TLMR01__"
                         "AND_THE_COUNTED_EVENT_IS_NOT_THE_CLAIMED_EVENT")}
    out["CODE_SHA256"] = {"FIMRCC02/code/fimrcc02_power.py":
                          H.file_sha256(os.path.join(REPO, "FIMRCC02/code/fimrcc02_power.py"))}
    out["POWER_CONTENT_HASH"] = H.content_digest(out, extra_excluded=("POWER_CONTENT_HASH",))
    return out


if __name__ == "__main__":
    d = main()
    json.dump(d, open(f"{REPO}/FIMRCC02/out/FIMRCC02_POWER.json", "w"), indent=1, ensure_ascii=False)
    c1 = d["CONSTAT_1__LE_CONTRASTE_GELE_EST_SIGNIFICATIF_PAR_LA_SEULE_MORTALITE"]
    c2 = d["CONSTAT_2__PUISSANCE_UNE_FOIS_LA_MORTALITE_CONDITIONNEE"]
    print("paires discordantes par la seule mortalite :", c1["paires_discordantes_par_la_seule_mortalite"],
          "dont", c1["dont_en_faveur_de_SHAM"], "en faveur de SHAM")
    print("p bilateral sous H0 stricte               :", round(c1["p_bilateral_du_test_des_signes"], 6))
    print()
    print("paires utilisables (deux bras vivants)     :", c2["n_paires_utilisables"])
    print("k critique                                 :", c2["k_critique"], "->", c2["lecture_du_k_critique"])
    print("puissance :", json.dumps(c2["puissance_par_p_vrai_si_toutes_les_paires_sont_discordantes"]))
    print("p vrai minimal pour 80 % de puissance      :", c2["p_vrai_minimal_pour_80_pourcent_de_puissance"])
    print()
    print("egalites :", json.dumps(d["CONSTAT_3__SENSIBILITE_AUX_EGALITES"]["table"], indent=1))
    print()
    print("DECISION :", d["CE_QUE_CETTE_ANALYSE_DECIDE"]["E3_E4_E5_TELS_QUE_GELES_SUR_SELECTIVE_CONTRE_SHAM"])
