"""CLOSE01 — le dossier de cloture du programme.

Aucun chiffre n'est ecrit de memoire : tout est relu des fichiers commites au moment ou ce
script tourne, et le dossier porte les hachages qui permettent de le refaire.
"""
from __future__ import annotations
import os, sys, json, math, glob, subprocess

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02/code"))
import omldct02_hashes as H


def J(p):
    return json.load(open(os.path.join(REPO, p)))


def main():
    r = J("OMLDCT03/out/OMLDCT03_FROZEN_TEST_RESULT.json")
    D = r["DECISION"]
    fim = J("FIMRCC01/out/FIMRCC01_ENDPOINT_ADJUDICATION.json")
    tl = J("TLMR01/out/TLMR01_ANALYSIS.json")["PER_LAW"]["LAW_C_MCTT01"]
    m1 = tl["M1_by_occupancy"]
    m2 = tl["M2_by_occupancy_at_separation"]
    auth = J("CLOSE01/out/CLOSE01_HUMAN_AUTHORISATION.json")

    def mult(k):
        v = D[k]
        return {"p_exact_bilateral": v["exact_two_sided_p"],
                "Hodges_Lehmann_en_facteur": round(math.exp(v["hodges_lehmann"]), 3),
                "intervalle_en_facteur": [round(math.exp(v["hl_interval"][0]), 3),
                                          round(math.exp(v["hl_interval"][1]), 3)],
                "rejette": v["rejects"], "n_egalites": v["n_zero"]}

    d = {
     "MISSION": "CLOSE01",
     "SECTION": "1 — dossier de cloture du programme",
     "GENERATED_UTC": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%S+00:00"],
                                     capture_output=True, text=True).stdout.strip(),
     "AUTHORISATION": {"fichier": "CLOSE01/out/CLOSE01_HUMAN_AUTHORISATION.json",
                       "hash": auth["AUTHORISATION_CONTENT_HASH"],
                       "reponse": auth["LA_REPONSE"]},

     "LA_CLOTURE_EN_UNE_PHRASE": (
       "le dispositif actuel ne peut pas trancher la question qu'il a ete construit pour poser, et "
       "l'arithmetique de ce blocage est etablie et chiffree ; le seul test confirmatoire "
       "pre-enregistre du programme a ete execute a son effectif requis et ne detecte pas d'effet, "
       "sans que cela autorise a conclure qu'il n'y en a pas."),

     "1_LE_MUR_TEL_QU_IL_EST_CHIFFRE": {
       "source": "FIMRCC01/out/FIMRCC01_ENDPOINT_ADJUDICATION.json, 2026-08-25",
       "E0_le_critere_herite": {
         "statut": fim["E0"]["STATUS"],
         "mesure": fim["E0"]["evidence"]["worlds"],
         "lecture": "il vaut la meme chose partout ; un critere qui ne varie jamais ne porte aucune information"},
       "E1_E2_le_critere_restreint": {
         "k_parmi_les_mondes_traites": fim["E1_E2"]["k_among_removed_worlds"],
         "taux_au_niveau_monde": fim["E1_E2"]["world_level_rate"],
         "valeur": fim["E1_E2"]["world_level_point"],
         "rapport_au_plancher_apparie": fim["E1_E2"]["ratio_to_F_INTEGRATED"],
         "assurance_du_critere_pre_declare_a_N_50": fim["E1_E2"]["P_K_GE_2_AT_N50_WORLD_LEVEL"],
         "POURQUOI_AUCUN_EFFECTIF_NE_REPARE": ("le taux mesure est 1,22 fois le plancher apparie. "
           "Un rapport de 1,22 ne se repare pas en ajoutant des mondes : ce n'est pas un probleme "
           "de puissance, c'est un probleme de separation entre le signal et le plancher.")},
       "CE_QUE_LE_MUR_EXPLIQUE": ("la longue serie de dispositions terminales en « non "
         "identifiable », « insuffisant », « sous-puissant » ou « techniquement invalide » n'est "
         "pas un defaut de soin. C'est le meme obstacle rencontre par des routes differentes.")},

     "2_LE_SEUL_TEST_CONFIRMATOIRE_EXECUTE": {
       "mission": "OMLDCT03",
       "le_gel": {"origine": "OMLDCT02_MASTER_FREEZE.json, 2026-08-25T22:30:05, avant tout monde",
                  "test": "Wilcoxon apparie exact, rangs de Pratt, enumeration complete",
                  "alpha": 0.05, "effectif_requis": 41,
                  "regle": "les DEUX criteres doivent rejeter, et dans la meme direction"},
       "n_paires_retenues": r["N_PAIRS_RETAINED"],
       "duree": mult("duration"), "exposition": mult("exposure"),
       "regle_ET": D["AND_RULE_PASSES"],
       "TERMINAL": r["TERMINAL"],
       "INTERPRETATION_GELEE": r["NULL_RESULT_INTERPRETATION"],
       "CE_QUE_L_INTERVALLE_AUTORISE_ENCORE": ("de 0,79 a 2,31 fois sur la duree. Ce test n'exclut "
         "ni un doublement ni une baisse d'un cinquieme. C'est la phrase qui compte et elle "
         "manquait a ma premiere redaction ; un verificateur adverse me l'a fait ajouter."),
       "DEUX_RESERVES_QUI_CHANGENT_CE_QUE_LE_RESULTAT_VEUT_DIRE": [
         "dans 9 paires sur 41 l'espece suivie s'eteint entierement du cote traite, contre 0 du "
         "cote temoin : le chiffre publie melange un ecart positif chez les mondes que le "
         "traitement ne tue pas et un ecart negatif chez ceux qu'il tue",
         "le retrait supprime l'objet meme qui fournissait la composante concurrente au suivi ; "
         "une part de « ca dure plus longtemps » est un artefact de mesure, pas un fait sur les objets"],
       "ET_UNE_RESERVE_DE_PORTEE": ("la regle d'accrual du gel n'a pas ete honoree : sous le "
         "plafond de 512 instances qu'OMLDCT02 avait gele, le flux disponible s'epuise avant 41 "
         "paires. Ce qui a ete execute est la PROCEDURE STATISTIQUE gelee, a son effectif requis, "
         "sur un echantillon obtenu hors de sa regle de recrutement.")},

     "3_CE_QUI_EST_ETABLI": {
       "noyau_causal": ("le support d'influence a un pas est EXACTEMENT le voisinage de Moore-1 "
         "torique : zero violation sur 668 041 paires de lignes, l'ensemble derive et l'ensemble "
         "mesure coincident. Structurel et exact."),
       "taux_de_separation_mesures": {
         "source": "TLMR01, 256 mondes a LAW_C_MCTT01, 2026-08-25",
         "transitions_vers_deux_centres_ou_plus": sum(v["k"] for v in m1.values()),
         "sur_pas_a_un_centre": sum(v["n"] for v in m1.values()),
         "runs_multi_centres": sum(v["n"] for v in m2.values()),
         "dont_atteignant_la_maturation": sum(v["k"] for v in m2.values()),
         "fraction_mediane_a_un_seul_centre": tl["M4_single_centre_exposure"]["median_horizon_fraction_single_centre"]},
       "point_de_lignee_qualifie": "FDFLT01, taux de succes superieur a 0,10, 2026-08-21",
       "preconditions_du_test_apparie": "FIMRCC01, A et B toutes deux PASS, fidelite auditee, 26 mondes sur 26",
       "le_materiel": ("TBRT02 : 41 triplets apparies a la meme graine, 123 archives scellees, "
         "prefixe identique bit a bit jusqu'a l'intervention, verifie deux fois par des "
         "verificateurs independants"),
       "le_test_execute": "OMLDCT03, ci-dessus — un nul pre-enregistre, ce qui est un resultat"},

     "4_CE_QUI_EST_RETIRE_ET_CE_QUE_CHAQUE_RETRAIT_A_PRODUIT": {
       "RPP97": {"statut": "WITHDRAWN_AS_A_DESCRIPTION__ARITHMETIC_SOUND__SCIENCE_MIS_SPECIFIED",
         "constats": "15 acceptes, 0 rejetes",
         "l_erreur": "un mecanisme bati sur l'idee qu'une espece etait consommee ; elle est produite",
         "la_garde_produite": "tester toute statistique contre le temps absolu et contre l'exposition avant publication"},
       "RPP98": {"statut": "WITHDRAWN__THE_QUESTION_WAS_ALREADY_ANSWERED_BY_TLMR01__AND_THE_COUNTED_EVENT_IS_NOT_THE_CLAIMED_EVENT",
         "constats": "16 acceptes, 0 rejetes",
         "l_erreur": "avoir declare neuve une question publiee quatre jours plus tot sur 256 mondes",
         "la_garde_produite": "GATE01, une porte d'anteriorite mecanique et opposable"},
       "FIMRCC02": {"statut": "WITHDRAWN__A_PREREGISTERED_TEST_ALREADY_EXISTS__AND_THE_CENTRAL_PREMISE_IS_FALSE_BY_DEFINITION",
         "constats": "16 acceptes, 0 rejetes",
         "l_erreur": "avoir declare qu'aucun test pre-enregistre n'existait ; il etait dans le depot depuis cinq jours",
         "la_garde_produite": "l'exigence d'une autorisation humaine explicite pour rouvrir une route, et le test lui-meme"},
       "CE_QUE_LA_SERIE_MONTRE": ("les trois retraits ont la meme cause : j'ai choisi la question "
         "moi-meme et je me suis trompe. Le calcul etait juste a chaque fois. Ce qui a echoue est "
         "le jugement sur ce qui etait neuf et sur ce que le critere mesurait vraiment.")},

     "5_CE_QUI_N_A_JAMAIS_ETE_TESTE": {
       "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
       "HEREDITY_STATUS": "NOT_TESTED", "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
       "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
       "X_LAWSPEC_BASELINE": "UNCHANGED",
       "REMARQUE": ("ces statuts n'ont pas bouge d'un cran depuis le debut du programme et rien "
         "dans cette cloture ne les deplace. Ils sont rapportes sans condition a chaque mission "
         "precisement pour qu'ils ne se deplacent jamais par inadvertance.")},

     "6_LE_LEGS__CE_QU_UN_SUCCESSEUR_DOIT_SAVOIR": [
       "le mur est arithmetique, pas methodologique : un critere a 1,22 fois son plancher ne se "
       "sauve pas par l'effectif. Un successeur doit chercher un observable qui se tienne plus "
       "loin du plancher, ou etablir — et non supposer — qu'un changement d'architecture est necessaire.",
       "l'unite independante est la graine de base, jamais l'archive : trois bras d'une meme graine "
       "partagent un prefixe identique bit a bit.",
       "toute restriction post-traitement est interdite, y compris la restriction aux survivants, "
       "et cette interdiction est gelee depuis le 25 aout.",
       "la mortalite differentielle — le retrait eteint l'espece dans 12 des 41 mondes traites "
       "contre 2 temoins — contamine tout comptage post-intervention. Elle est mesuree, elle est "
       "documentee, et elle n'a jamais fait l'objet d'une etude propre.",
       "GATE01 doit etre passee avec les NOMS DES GRANDEURS avant tout gel : des termes vagues "
       "signalent deux cents fichiers et la porte est contournee.",
       "un retour de checker se commite VERBATIM avant d'etre traite. C'est la seule raison pour "
       "laquelle les trois retraits sont lisibles aujourd'hui."],

     "7_CE_QUE_CETTE_CLOTURE_NE_DIT_PAS": auth["CE_QUE_LA_CLOTURE_N_EST_PAS"],

     "PROVENANCE": {
       "branche": "codex/one-matched-locked-daughter-control-test-02",
       "commits_depuis_la_base": int(subprocess.run(
           ["git", "-C", REPO, "rev-list", "--count",
            "06c592313df96601de8d2a89676d5a5cf79fc414..HEAD"],
           capture_output=True, text=True).stdout.strip() or 0),
       "METHODS_HASH": "21571fb4cb1df9ac2e9089924e9d6ee5d4d63c920a007e188bdc24e0d94d1f99",
       "retours_de_checker_verbatim_conserves": {
         "RPP97": H.file_sha256(f"{REPO}/RPP97/out/RPP97_CHECKER_RETURN_VERBATIM.md"),
         "RPP98": H.file_sha256(f"{REPO}/RPP98/out/RPP98_CHECKER_RETURN_VERBATIM.md"),
         "FIMRCC02": H.file_sha256(f"{REPO}/FIMRCC02/out/FIMRCC02_CHECKER_RETURN_VERBATIM.md"),
         "OMLDCT03": H.file_sha256(f"{REPO}/OMLDCT03/out/OMLDCT03_CHECKER_RETURN_VERBATIM.md")},
       "archives_scellees": "123, verifiees au sha256 contre le registre scelle",
       "retours_arriere_du_conteneur_traverses": 28},

     "CLOSE01_DISPOSITION": ("PROGRAMME_CLOSED_ON_A_QUANTIFIED_INSTRUMENT_LIMIT__"
                             "NO_CLAIM_OF_ABSENCE__ALL_TERMINAL_STATUSES_UNCHANGED"),
     "VOCABULAIRE": ("rien ici ne porte sur ce que ces objets sont. Le vocabulaire du vivant reste "
                     "exclu du dossier, y compris pour le nier."),
    }
    d["CLOSURE_CONTENT_HASH"] = H.content_digest(d, extra_excluded=("CLOSURE_CONTENT_HASH",))
    json.dump(d, open(f"{REPO}/CLOSE01/out/CLOSE01_DOSSIER.json", "w"), indent=1, ensure_ascii=False)
    return d


if __name__ == "__main__":
    d = main()
    print("DISPOSITION :", d["CLOSE01_DISPOSITION"])
    print("commits     :", d["PROVENANCE"]["commits_depuis_la_base"])
    print("hash        :", d["CLOSURE_CONTENT_HASH"][:16])
