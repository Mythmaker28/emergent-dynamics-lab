"""FIMRCC02 — cloture. Ecrite APRES l'analyse de puissance et AVANT tout gel d'endpoint.

L'analyse de puissance (FIMRCC02_POWER.json) a montre que le contraste apparie gele est
significatif par la seule mortalite differentielle. J'ai alors ecrit que « la seule version
posable » etait le meme contraste restreint aux 28 paires ou les deux bras ont Y vivant.

CETTE PHRASE ETAIT FAUSSE, ET JE LA RETIRE ICI AVANT QU'UN CHECKER LA TROUVE.

Restreindre aux paires ou les deux bras survivent, c'est CONDITIONNER SUR UNE VARIABLE
POST-TRAITEMENT. Les mondes ou le bras SELECTIVE survit ne sont pas un sous-ensemble tire au
hasard : ce sont exactement les mondes ou le retrait n'a pas tue. Le contraste restreint n'estime
donc rien de causal ; il compare des survivants selectionnes par le traitement lui-meme. C'est le
biais de conditionnement post-traitement, et il ne se repare pas en augmentant n.

Le probleme a un nom en methodologie : la TRONCATURE PAR LA MORT. Le critere « combien de pas
l'intervalle de la fille survit-il apres t_m » n'est pas defini dans un monde ou Y est eteint —
il n'est pas manquant, il n'existe pas.
"""
from __future__ import annotations
import os, sys, json, subprocess

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02/code"))
import omldct02_hashes as H


def main():
    pw = json.load(open(f"{REPO}/FIMRCC02/out/FIMRCC02_POWER.json"))
    p_mort = pw["CONSTAT_1__LE_CONTRASTE_GELE_EST_SIGNIFICATIF_PAR_LA_SEULE_MORTALITE"][
        "p_bilateral_du_test_des_signes"]
    d = {
     "MISSION": "FIMRCC02",
     "SECTION": "cloture — aucun endpoint n'est gele, et voici pourquoi",
     "GENERATED_UTC": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%S+00:00"],
                                     capture_output=True, text=True).stdout.strip(),
     "PARENT": {"POWER_CONTENT_HASH": pw["POWER_CONTENT_HASH"],
                "FIMRCC01_ENDPOINT_PREREGISTRATION": "2026-08-25T16:31:48.018905+00:00",
                "GATE01": ("GATE01/out/FIMRCC02_PRIOR_ART.json — 18 fichiers signales, tous juges, "
                           "aucun ne repond a la question")},
     "AUCUNE_ARCHIVE_TBRT02_N_A_ETE_OUVERTE_PAR_CETTE_MISSION": True,

     "JE_RETIRE_UNE_PHRASE_QUE_J_AI_ECRITE_IL_Y_A_VINGT_MINUTES": {
       "la_phrase": ("« la seule version posable : le meme contraste restreint aux paires ou les "
                     "deux bras ont Y vivant, soit 28 paires »"),
       "ou": "FIMRCC02_POWER.json, CE_QUE_CETTE_ANALYSE_DECIDE.LA_SEULE_VERSION_POSABLE",
       "pourquoi_elle_est_fausse": ("survivre au retrait est une variable POST-TRAITEMENT. Les 28 "
         "paires ne sont pas un sous-ensemble tire au hasard des 41 : ce sont celles ou le retrait "
         "n'a pas tue le monde. Conditionner dessus selectionne sur une consequence du traitement "
         "et brise l'appariement que tout le dispositif TBRT02 avait construit. Le contraste "
         "restreint n'estime aucune quantite causale, et aucun n plus grand ne le repare."),
       "ce_que_j_aurais_du_ecrire": ("qu'il n'existe, sur ces bras, aucune restriction qui rende le "
         "critere gele interpretable — ni la version brute, confondue par la mortalite, ni la "
         "version restreinte, biaisee par le conditionnement post-traitement."),
       "le_nom_du_probleme": ("TRONCATURE PAR LA MORT. E3 — le nombre de pas que l'intervalle de "
         "la fille survit apres t_m — n'est pas MANQUANT dans un monde ou Y est eteint : il "
         "N'EXISTE PAS. Un critere non defini sous le traitement ne se moyenne pas."),
       "LE_FICHIER_PARENT_N_EST_PAS_MODIFIE": ("FIMRCC02_POWER.json garde son hachage publie et sa "
         "phrase fausse. La correction vit ici, a cote, et non par-dessus.")},

     "LES_TROIS_ROUTES_ET_POURQUOI_AUCUNE_N_EST_PRISE": {
       "ROUTE_A_contraste_brut_tel_que_gele": {
         "statut": "REJETEE",
         "raison": ("p = %.4f sous l'hypothese nulle STRICTE d'aucun effet sur la fille, par la "
                    "seule mortalite. Le test repondrait a la question « le retrait tue-t-il le "
                    "monde », a laquelle la reponse est deja connue et n'a pas besoin de E3."
                    % p_mort)},
       "ROUTE_B_restriction_aux_survivants": {
         "statut": "REJETEE",
         "raison": ("conditionnement sur une variable post-traitement ; non causale ; "
                    "non reparable par n")},
       "ROUTE_C_composite_ordonne_ou_la_mort_est_le_pire_rang": {
         "statut": "NON_PRISE__ET_LA_RAISON_EST_MA_PROPRE_CONTAMINATION",
         "ce_que_c_est": ("la reponse methodologique standard a la troncature par la mort : "
           "ordonner les paires en rangeant la mort du monde au-dessous de toute duree de survie, "
           "puis comparer par un rapport de gains ou un test de rang sur le composite. La methode "
           "existe, elle est legitime, et elle n'exige aucune donnee nouvelle."),
         "pourquoi_je_ne_la_prends_pas": ("ce serait un endpoint NOUVEAU, et je le concevrais "
           "APRES avoir vu la table de mortalite — 12 contre 2 — qui est precisement ce qui le "
           "rend attrayant. Le declarer maintenant serait post-hoc au sens strict : le choix de la "
           "statistique serait informe par le resultat qu'elle doit tester. C'est l'erreur pour "
           "laquelle RPP97 a ete retiree, et je ne la refais pas parce que la methode est bonne."),
         "ce_qui_le_rendrait_legitime": ("un pre-enregistrement ecrit par quelqu'un qui n'a pas vu "
           "la table de mortalite, ou sur un jeu de graines disjoint qui n'existe pas ici.")}},

     "LA_DISPOSITION": {
       "FIMRCC02_DISPOSITION": ("NO_PREREGISTERED_CONFIRMATORY_TEST_OF_DAUGHTER_PERSISTENCE_IS_"
                                "AVAILABLE_ON_THESE_ARMS__ENDPOINT_TRUNCATED_BY_DEATH"),
       "E3_STATUS": "POWER_NOW_IDENTIFIED__ENDPOINT_TRUNCATED_BY_DEATH__NOT_FROZEN",
       "E4_STATUS": "POWER_NOW_IDENTIFIED__UNDERPOWERED_BY_ITS_OWN_PUBLISHED_MARGINAL__NOT_FROZEN",
       "E5_STATUS": "NOT_ASSESSED__AMBIENT_POPULATION_SATURATED_AT_E0__NOT_FROZEN",
       "CE_QUE_LA_MISSION_A_QUAND_MEME_LIVRE": (
         "FIMRCC01 portait, pour E3, E4 et E5, le champ POWER_NOT_ESTIMABLE_IN_ADVANCE avec sa "
         "raison : aucun bras temoin apparie dans 512 mondes. TBRT02 a fourni ce bras. La "
         "puissance prospective de ces trois criteres est donc IDENTIFIEE pour la premiere fois, "
         "et le champ de FIMRCC01 peut etre remplace par un chiffre. Le chiffre dit que le "
         "critere n'est pas utilisable ici. C'est une reponse, pas une absence de reponse."),
       "CE_QUE_LA_MISSION_NE_LIVRE_PAS": (
         "aucune mesure sur les archives TBRT02. Aucune archive n'a ete ouverte. Rien n'est dit de "
         "la persistance de la fille, ni dans un sens ni dans l'autre.")},

     "POURQUOI_S_ARRETER_EST_LE_BON_COUP": (
       "trois missions de suite se terminent sans resultat confirmatoire. Mais celle-ci s'arrete "
       "AVANT d'avoir ouvert une archive, pour une raison etablie sur des tableaux deja publies, "
       "et elle rend au dossier un chiffre que la mission parente avait declare non calculable. "
       "RPP97 et RPP98 se sont arretees APRES avoir publie des affirmations fausses qu'un checker "
       "a du demolir. La difference entre les deux n'est pas le resultat : c'est le moment."),

     "CE_QUE_LE_PROGRAMME_DEVRAIT_REGARDER_ENSUITE__SANS_QUE_JE_LE_GELE": (
       "la carte d'anteriorite (GATE01/out/EDL_PRIOR_ART_MAP.json) montre que le mur est toujours "
       "le meme : le critere sature, ou se produit a 1,22 fois le plancher apparie. La mortalite "
       "differentielle mise au jour ici — 12 mondes sur 41 ou le retrait selectif eteint Y, contre "
       "2 temoins — est elle-meme un effet cause, large, apparie et non confondu, dont personne "
       "n'a encore fait un objet d'etude. Je ne le gele pas : je le note, et c'est a l'operateur "
       "humain de dire si c'est la question qui l'interesse."),

     "STATUTS_INCHANGES": pw["STATUTS_INCHANGES"],
     "VOCABULAIRE": ("rien ici ne porte sur ce que ces objets sont. « Mort du monde » designe "
                     "l'extinction de l'espece Y au sens du registre, pas autre chose."),
    }
    d["CLOSURE_CONTENT_HASH"] = H.content_digest(d, extra_excluded=("CLOSURE_CONTENT_HASH",))
    return d


if __name__ == "__main__":
    d = main()
    json.dump(d, open(f"{REPO}/FIMRCC02/out/FIMRCC02_CLOSURE.json", "w"), indent=1,
              ensure_ascii=False)
    print("DISPOSITION :", d["LA_DISPOSITION"]["FIMRCC02_DISPOSITION"])
    print("E3 :", d["LA_DISPOSITION"]["E3_STATUS"])
    print("hash", d["CLOSURE_CONTENT_HASH"][:16])
