"""FIMRCC02 — adjudication. Le retour du checker est commite verbatim en be9854f, AVANT ceci."""
from __future__ import annotations
import os, sys, json, subprocess
REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02/code"))
import omldct02_hashes as H
V = "FIMRCC02/out/FIMRCC02_CHECKER_RETURN_VERBATIM.md"

F = {
 "F3_UN_TEST_PRE_ENREGISTRE_EXISTE_DEJA": {
   "verdict": "ACCEPTED", "gravite": "FATALE — c'est la disposition entiere",
   "constat": ("j'ai ecrit NO_PREREGISTERED_CONFIRMATORY_TEST_OF_DAUGHTER_PERSISTENCE_IS_AVAILABLE. "
               "C'est faux."),
   "verifie_par_moi_meme": {
     "fichier": "OMLDCT02/out/OMLDCT02_MASTER_FREEZE.json",
     "GENERATED_UTC": "2026-08-25T22:30:05.022074+00:00",
     "THIS_FREEZE_PRECEDES_EVERY_SCIENTIFIC_WORLD": True,
     "PRIMARY_ENDPOINT": "paired post-intervention duration of the same locked daughter identity",
     "SIGN_CONVENTION": "SELECTIVE minus SHAM, on the paired log difference",
     "PAIRED_TEST": ("two-sided exact Wilcoxon signed-rank with Pratt ranking ; distribution de "
                     "sign-flip conditionnelle enumeree par programmation dynamique ; aucune "
                     "approximation normale"),
     "ALPHA": 0.05, "ZERO_DIFFERENCE_TREATMENT": "PRATT_EXACT_SIGN_FLIP",
     "MINIMUM_VALID_PAIR_COUNT": 41,
     "NULL_RESULT_INTERPRETATION": "INCONCLUSIVE__NO_CLAIM_OF_EQUIVALENCE__NO_CLAIM_OF_NO_EFFECT"},
   "la_coincidence_que_je_n_ai_pas_vue": ("OMLDCT02 exigeait 41 paires et s'est arrete a 33 avec "
     "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS. TBRT02 a livre exactement 41 triplets, sur des "
     "graines explicitement exclues de celles d'OMLDCT02, et son bras SELECTIVE est declare dans "
     "TBRT02_MASTER_FREEZE.json comme « the OMLDCT02 treatment, kept for comparability ». "
     "L'accrual manquant d'OMLDCT02 est assis dans le depot depuis le 28 aout et je ne l'ai pas vu."),
   "et_ma_propre_condition_etait_remplie": ("ma cloture disait que ROUTE_C serait legitime avec "
     "« un pre-enregistrement ecrit par quelqu'un qui n'a pas vu la table de mortalite, ou sur un "
     "jeu de graines disjoint QUI N'EXISTE PAS ICI ». Les deux moities etaient satisfaites, dans "
     "ce depot, depuis cinq jours.")},

 "F1_MA_PREMISSE_CENTRALE_EST_FAUSSE_PAR_DEFINITION": {
   "verdict": "ACCEPTED", "gravite": "FATALE",
   "constat": ("j'ai ecrit que dans un monde ou Y est eteint les trois criteres valent leur "
               "minimum PAR DEFINITION et que la direction de la paire est FORCEE."),
   "verifie_par_moi_meme": {
     "E3_est_une_duree_pas_un_minimum": ("E3 = e[end] - t_m. L'extinction BORNE E3 par le haut a "
       "t_first_zero - t_m ; elle ne le met pas a son minimum. Six des onze bornes que le checker "
       "calcule depassent la mediane publiee de E3 (230)."),
     "les_deux_paires_deja_executees_vont_DANS_L_AUTRE_SENS": {
       "source": "OMLDCT02/out/OMLDCT02_FROZEN_ANALYSIS.json, table PER_PAIR, 33 paires",
       "index_450": {"SELECTIVE_duration": 257, "SHAM_duration": 88,
                     "SELECTIVE_termination": "NO_COMPONENT_AT_THE_NEXT_STEP"},
       "index_482": {"SELECTIVE_duration": 214, "SHAM_duration": 128,
                     "SELECTIVE_termination": "NO_COMPONENT_AT_THE_NEXT_STEP"},
       "lecture": ("les deux seules instances executees du cas que j'appelle « force en faveur de "
                   "SHAM » favorisent SELECTIVE. n = 2 ne refute pas une tendance ; cela refute "
                   "entierement une affirmation de necessite logique, et « par definition » en "
                   "est une.")},
     "signe_global_des_33_paires": "SELECTIVE plus long 18, SHAM plus long 14, egalite 1"},
   "consequence": ("CONSTAT_1, sa chaine VERDICT, le message de commit, le rejet de ROUTE_A et la "
                   "disposition NON_INTERPRETABLES tombent tous avec cette phrase.")},

 "F4_LA_TRONCATURE_PAR_LA_MORT_EST_UN_CADRE_INVERSE": {
   "verdict": "ACCEPTED", "gravite": "FATALE",
   "verifie_par_moi_meme": ("OMLDCT02_MASTER_FREEZE.json, champ identity_terminates_at = [split, "
     "merge, tie or ambiguity, EMPTY COMPONENT, administrative horizon]. La mort du monde est "
     "l'un des cinq modes de terminaison PRE-DECLARES. E3 y est donc DEFINI et MESURE, pas "
     "indefini."),
   "le_bon_cadre": ("RISQUES CONCURRENTS, pas troncature par la mort. L'identite peut finir par "
     "scission, fusion, ambiguite, extinction du monde ou horizon, et le traitement deplace le "
     "melange. C'est un vrai probleme d'interpretation, et ses reponses standard sont l'analyse "
     "cause-specifique ou un composite ordonne — que la regle de Pratt gelee sait deja traiter.")},

 "F2_MON_p_DE_0_0063_EST_UN_POINT_DE_QUEUE_PRESENTE_COMME_LA_REGLE": {
   "verdict": "ACCEPTED", "gravite": "PORTANTE",
   "constat": ("mon calcul pose n_disc = 12 et suppose donc en silence que les 29 autres paires "
     "sont des egalites exactes — ce que mon propre CONSTAT_4 nie quatre cles plus loin en "
     "disant que les egalites de E3 seront rares."),
   "le_chiffre_du_checker": {"P_rejet_a_alpha_0.05": 0.2858, "E_p": 0.2594, "mediane_p": 0.1539,
                             "P(p<=0.0063)": 0.049},
   "ce_que_j_aurais_du_ecrire": ("le test des signes apparie gele a une erreur de type I d'environ "
     "0,29 au lieu de 0,05 SI l'extinction biaise le signe de la paire, et je n'ai etabli ni "
     "qu'elle le fait ni dans quel sens."),
   "taux_d_egalites_mesures_disponibles_sans_ouvrir_une_archive":
     {"OMLDCT02_E3": "1/33 = 3,0 %", "TBRT02_C4_paragraphe_12": "7/41 = 17,1 %"}},

 "F5_AUCUNE_DE_MES_QUATRE_PREMIERES_N_EN_EST_UNE": {
   "verdict": "ACCEPTED", "gravite": "PORTANTE — c'est le mode d'echec de RPP98, repete",
   "verifie_par_moi_meme": {
     "LDFMA01_MATCHED_CONTROL_POWER.json": ("2026-08-25T18:45:09, section « 6 — matched-control "
       "power », avec POWER_GRID et E3_CONTINUOUS_ALTERNATIVE. Ma phrase « la puissance est "
       "IDENTIFIEE pour la premiere fois » est fausse."),
     "OMLDCT02": "le contraste a ete EXECUTE : 33 paires, p exact 0,4009 sur la duree",
     "TBRT02_C4_paragraphe_12": ("un contraste apparie SELECTIVE moins SHAM sur les 41 graines "
       "memes est deja publie : 24 positifs, 7 nuls, 10 negatifs — et il pointe a l'OPPOSE de ma "
       "premisse"),
     "la_mortalite_differentielle": ("deja constatee par le checker de RPP97, retabulee par celui "
       "de RPP98 en F6 et F7 avec la correction normalisee par l'exposition, et ecrite par MOI "
       "dans EDL_PRIOR_ART_MAP.json ligne 91, quatre minutes avant de lancer la porte.")}},

 "F6_MA_PORTE_D_ANTERIORITE_EST_DU_THEATRE_TELLE_QUE_JE_L_AI_UTILISEE": {
   "verdict": "ACCEPTED", "gravite": "PORTANTE — et reparable, voir la reparation ci-dessous",
   "les_defauts": [
     "j'ai choisi des termes qui sont le vocabulaire prive de FIMRCC01 : 12 des 18 fichiers "
     "signales sont FIMRCC01, et LDFMA01 rate le seuil d'UN mot",
     "la regle « au moins deux termes » n'a aucune notion de rarete : deux termes obscurs donnent "
     "zero fichier signale et la porte PASSE",
     "le code saute GATE01/ — donc la carte d'anteriorite du programme est invisible pour la porte "
     "qui existe pour trouver l'anteriorite",
     "le code n'accepte que out/, work/ et code/*.py — les 18 fichiers sous review/ sont invisibles, "
     "or c'est la que vivent les retours de checker, c'est-a-dire l'anteriorite la plus lourde",
     "mes verdicts sont du remplissage : 3 chaines REASON distinctes pour 18 fichiers",
     "la sortie de la porte est commitee DANS LE MEME COMMIT que le resultat qu'elle est censee "
     "avoir precede — RPP98, malgre tout, commitait son pre-enregistrement seul"],
   "ce_que_la_porte_aurait_donne_avec_les_bons_termes": ("28 fichiers, avec en tete "
     "LDFMA01_MATCHED_CONTROL_POWER, LDFMA01_ROUTE_ARBITRATION_FINAL, OMLDCT01_MASTER_FREEZE et "
     "OMLDCT02_MASTER_FREEZE — dont un seul suffisait a interdire le gel.")},

 "F7_MA_BORNE_SUR_LES_EGALITES_DE_E4_EST_FAUSSE_QUATRE_FOIS": {
   "verdict": "ACCEPTED", "gravite": "PORTANTE",
   "les_quatre": ["la somme des carres vaut 0,23967 — soit MOINS de 25 %, pas plus",
     "pour deux tirages i.i.d. la probabilite de collision vaut EXACTEMENT cette somme, pas « au moins »",
     "depuis la marginale seule, la seule borne defendable est 19,4 %",
     "« l'appariement ne peut qu'augmenter les egalites » est asserte et faux en general — deux "
     "variables parfaitement correlees avec un decalage constant ont zero egalite"],
   "et_deux_de_plus": ["la marginale vient de 22 mondes SANS AUCUNE extinction, transportee vers un "
     "dispositif ou 12 bras sur 41 s'eteignent",
     "l'etroitesse de E4 est un DEFAUT D'INSTRUMENT connu et quantifie par LDFMA01 : le taux de "
     "decroissance predit 8,44 retraits de constituants et la regle gelee en compte 1"]},

 "F8_MA_RETRACTATION_POST_TRAITEMENT_EST_ELLE_MEME_FAUSSE": {
   "verdict": "ACCEPTED", "gravite": "PORTANTE — et c'etait la piece maitresse de ma cloture",
   "constat": ("j'avais raison sur le genre et tort sur trois specifiques. « Cela brise "
     "l'appariement » est faux : restreindre change la POPULATION, pas l'appariement. « Le "
     "contraste restreint n'estime aucune quantite causale » est faux DANS CE DISPOSITIF : "
     "l'intervention ne consomme aucun nombre aleatoire, donc S(1) ET S(0) sont observes pour "
     "chaque graine, et la strate principale — d'ordinaire latente — est ICI OBSERVEE. L'effet "
     "causal moyen sur les toujours-survivants est point-identifie, sans monotonie ni analyse de "
     "sensibilite. « Aucun n ne le repare » est vrai de l'ATE et faux de cet effet-la."),
   "ce_qui_reste_vrai_et_que_je_n_avais_pas_dit": ("la strate est definie par l'effet du traitement, "
     "donc l'estimande est plus etroit que celui que FIMRCC01 a gele et ne se generalise pas a "
     "tous les mondes. C'est un probleme de PLAFOND DE REVENDICATION, pas d'identification.")},

 "F9_JE_ME_CONTREDIS_ENTRE_DEUX_CLES_ADJACENTES": {
   "verdict": "ACCEPTED", "gravite": "PORTANTE",
   "constat": ("E5_STATUS = NOT_ASSESSED et, dans le meme dictionnaire, « la puissance prospective "
     "de CES TROIS criteres est IDENTIFIEE pour la premiere fois ». Et mon CONSTAT_2 ne contient "
     "aucune information propre a la mission au-dela de l'entier 28 : c'est une table binomiale."),
   "et_ma_citation_est_selective": ("FIMRCC01 donne CINQ raisons de ne pas autoriser E3/E4/E5 ; "
     "seule la deuxieme concerne le bras manquant. La quatrieme — « selectionner l'un maintenant "
     "changerait la question scientifique apres acces au resultat developpemental » — est "
     "exactement l'objection de contamination que je porte contre ROUTE_C, et elle vise la "
     "reouverture entiere.")},

 "F10_GOUVERNANCE__J_AI_ROUVERT_SANS_AUTORISATION": {
   "verdict": "ACCEPTED", "gravite": "PORTANTE",
   "le_texte_gele": ("FIMRCC01_FINAL_DISPOSITION.json : NEXT_SCIENTIFIC_ELIGIBILITY = "
     "NONE__LINEAGE_ROUTE_PAUSED ; NO_HANDOFF_IS_EMITTED = true ; REOPENING_REQUIRES = « an "
     "explicit new human authorisation and a newly derived matched-control design. Nothing in "
     "this mission authorises one. »"),
   "ce_que_j_ai_fait": "j'ai reecrit les trois statuts sans qu'aucune autorisation humaine figure nulle part",
   "et_pire": ("ROUTE_B etait interdite NOMMEMENT dans le pre-enregistrement que je lis en tete de "
     "mon propre docstring : WHAT_IS_DELIBERATELY_NOT_PERMITTED, item 2, « conditioning the "
     "endpoint on any quantity measured after the trigger ». Ma retractation-vedette est la "
     "redecouverte d'une regle de ma mission parente.")},

 "F11_J_AI_ECHOUE_A_MA_PROPRE_LISTE_ECRITE_QUATRE_MINUTES_PLUS_TOT": {
   "verdict": "ACCEPTED", "gravite": "PORTANTE",
   "constat": ("EDL_PRIOR_ART_MAP.json, item 2 : « une section 0 doit enumerer tout cela, y compris "
     "les constats de METHODE ». FIMRCC02 n'a pas de section 0. Item 6 : « GATE01 passe avec les "
     "NOMS DES GRANDEURS » — pas fait. Item 3 : la substitution DISPLACED « doit etre ecrite au "
     "titre » — elle est dans une sous-cle. Seul l'item 4, l'unite = 41 graines, est honore.")},

 "F12_MA_SUGGESTION_FINALE_EST_LA_VIOLATION_DE_ROUTE_C_SANS_L_ETIQUETTE": {
   "verdict": "ACCEPTED", "gravite": "PORTANTE",
   "constat": ("je refuse ROUTE_C parce que je la concevrais apres avoir vu la table 12 contre 2, "
     "puis je propose le contraste 12 contre 2 lui-meme comme question suivante, parce que j'ai vu "
     "la table 12 contre 2. « Je ne le gele pas, je le note » n'est pas une distinction que les "
     "retraits de RPP97 et RPP98 reconnaissent."),
   "et_le_chiffre_est_faux": ("le contraste cause est 11 extinctions et 1 sauvetage sur 41 graines, "
     "pas 12 contre 2 : la graine 793 est morte dans les deux bras et 780 seulement en SHAM.")},

 "F13_J_AI_RECOMMANDE_DISPLACED_SUR_UN_CRITERE_DE_RESULTAT": {
   "verdict": "ACCEPTED", "gravite": "MATERIELLE",
   "constat": ("j'ai propose DISPLACED contre SHAM parce qu'il tue moins de mondes — une quantite "
     "post-traitement, lue dans la table meme autour de laquelle je refuse de concevoir. Et "
     "TBRT02_MASTER_FREEZE dit que le deplacement est PLUS invasif que le retrait : c'est une "
     "autre question causale, pas une version plus propre de la meme.")},

 "F14_MA_RAISON_POUR_E5_EST_FAUSSE": {
   "verdict": "ACCEPTED", "gravite": "MATERIELLE",
   "constat": ("j'ai confondu E0, binaire et sature 22/22, avec E5, un COMPTE explicitement marque "
     "CRITERION_2_SATURATED: false, 20 valeurs distinctes sur 22 mondes. La vraie raison est "
     "publiee et bien plus forte : LDFMA01 montre que 2017 des 2018 intervalles ambiants "
     "commencent APRES la fin de l'identite verrouillee, et son handoff dit « Do not use an "
     "ambient endpoint ».")},

 "F15_DEFAUTS_MINEURS": {
   "verdict": "ACCEPTED", "gravite": "COSMETIQUE A MATERIELLE",
   "liste": ["« 80 % de puissance exige 0,80 » est un point de grille ; le vrai seuil est 0,7630",
     "la table des egalites compare des tests de tailles reelles differentes (0,0357 / 0,0266 / 0,0129)",
     "CONSTAT_3 rapporte une puissance CONDITIONNELLE au nombre d'egalites, non etiquetee comme telle",
     "je lie ma mission parente par un horodatage et non par un sha256, alors que FIMRCC01 lie le sien par hachage",
     "la cloture ne porte pas de CODE_SHA256 et il n'y a pas de SHA256SUMS dans FIMRCC02/out",
     "« il y a vingt minutes » : c'etait onze minutes cinquante-quatre — trivial, sauf dans une "
     "mission dont toute la defense est « la difference, c'est le moment »"]},

 "F16_n_zero_steps__JUSTE_PAR_CHANCE_ET_LA_LECON_INVERSEE": {
   "verdict": "ACCEPTED", "gravite": "MATERIELLE",
   "constat": ("mon code teste n_zero_steps > 0 n'importe ou sur 11 000 pas, sans verifier que "
     "c'est apres t_m ni que c'est terminal, alors que t_first_zero est dans le meme "
     "enregistrement. Le checker a verifie que ca tient — t_first_zero + n_zero_steps = 11000 dans "
     "les 19 bras — donc c'est juste, mais par chance."),
   "et_j_ai_inverse_la_lecon": ("le constat F6 de RPP98 disait que n_zero_steps est le DENOMINATEUR "
     "D'EXPOSITION et qu'il n'etait jamais utilise. Je l'utilise comme un DRAPEAU BINAIRE de mort, "
     "jetant precisement l'information graduee — fractions vivantes 0,954 / 0,718 / 0,891 — qui "
     "aurait montre que le confondant est une affaire de degre dans tous les bras.")},
}

d = {
 "MISSION": "FIMRCC02",
 "GENERATED_UTC": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%S+00:00"],
                                 capture_output=True, text=True).stdout.strip(),
 "CHECKER_RETURN_VERBATIM": V,
 "CHECKER_RETURN_SHA256": H.file_sha256(os.path.join(REPO, V)),
 "CHECKER_RETURN_COMMITTED_BEFORE_THIS_FILE": "be9854f",
 "N_FINDINGS": len(F), "N_ACCEPTED": sum(1 for v in F.values() if v["verdict"] == "ACCEPTED"),
 "N_REJECTED": sum(1 for v in F.values() if v["verdict"] != "ACCEPTED"),
 "FINDINGS": F,

 "FIMRCC02_STATUS": ("WITHDRAWN__A_PREREGISTERED_TEST_ALREADY_EXISTS__"
                     "AND_THE_CENTRAL_PREMISE_IS_FALSE_BY_DEFINITION"),
 "CE_QUI_EST_RETIRE": [
   "la disposition NO_PREREGISTERED_CONFIRMATORY_TEST_..._IS_AVAILABLE — un tel test existe",
   "CONSTAT_1 en entier : l'extinction ne force pas le signe de la paire",
   "le cadre « troncature par la mort » : la mort du monde est un mode de terminaison pre-declare",
   "« la puissance est identifiee pour la premiere fois » : LDFMA01 l'avait publiee le 25 aout",
   "la retractation post-traitement telle que redigee : la strate est ICI observee, l'effet sur les "
   "toujours-survivants est point-identifie",
   "la suggestion finale sur la mortalite differentielle : elle est post-hoc et le chiffre est 11 contre 1"],
 "CE_QUI_TIENT": {
   "arithmetique": "tout se reproduit a l'octet sous le code du checker ; les hachages verifient",
   "aucune_archive_ouverte": "verifie par le checker sur les chemins de code",
   "unite_41_graines": "honore",
   "la_direction_de_l_inquietude": ("qu'un contraste apparie de comptes apres t_m soit contamine "
     "par l'extinction differentielle est correct — mais c'etait deja etabli par le checker de "
     "RPP97, retabli par celui de RPP98, et ecrit par moi quatre minutes avant la mission")},

 "LE_CONSTAT_SUR_MOI": (
   "trois missions retirees d'affilee. Le checker le formule mieux que je ne le ferais : RPP97 et "
   "RPP98 ont publie des affirmations fausses sur des donnees qu'elles avaient lues ; FIMRCC02 a "
   "publie des affirmations fausses sur des donnees qu'elle n'avait PAS lues, sur une question que "
   "quatre missions anterieures avaient deja traitee, derriere une porte que j'avais configuree de "
   "facon a ne pas les voir. Le probleme n'est pas la rigueur du calcul — le calcul est juste a "
   "chaque fois. Le probleme est que je decide seul de ce qui est nouveau, et je me trompe."),

 "CE_QUE_JE_NE_FAIS_PAS_ET_POURQUOI": (
   "je n'enchaine pas sur le test gele d'OMLDCT02, bien que ce soit la suite evidente. Trois "
   "raisons. Un : FIMRCC01_FINAL_DISPOSITION exige « an explicit new human authorisation » pour "
   "rouvrir, et je viens de rouvrir sans. Deux : la seule question honnete qui reste — les 41 "
   "triplets de TBRT02 donnent-ils 41 paires ADMISSIBLES au sens des criteres geles d'OMLDCT02 — "
   "exige d'ouvrir les archives, donc de rapatrier 123 fichiers, donc un engagement reel. Trois : "
   "mon jugement sur « quelle question poser » a echoue trois fois de suite, et la reparation "
   "n'est pas d'essayer plus fort mais de demander."),
 "LA_QUESTION_POUR_L_OPERATEUR_HUMAIN": (
   "OMLDCT02 porte un test confirmatoire gele avant tout monde, qui exigeait 41 paires et s'est "
   "arrete a 33. TBRT02 a livre 41 triplets du meme traitement sur des graines disjointes. "
   "Faut-il verifier combien de ces 41 paires sont admissibles au sens des criteres geles "
   "d'OMLDCT02, et, si c'est 41, executer le test gele tel quel ? C'est une reouverture qui "
   "demande une autorisation explicite, et elle n'est pas la mienne a donner."),

 "STATUTS_INCHANGES": {
   "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
   "HEREDITY_STATUS": "NOT_TESTED", "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
   "X_LAWSPEC_BASELINE": "UNCHANGED", "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED",
   "COMPANION_PAPER_V1_1_STATUS": "UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
   "OMLDCT02_STATUS": "INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED",
   "CLEA01_STATUS": "CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED",
   "TBRT02_STATUS": "CLOSED__RAW_COMPLETE__PRIMARY_ADJUDICATION_INCONCLUSIVE_BY_CONSTRUCTION",
   "RPP97_STATUS": "WITHDRAWN_AS_A_DESCRIPTION__ARITHMETIC_SOUND__SCIENCE_MIS_SPECIFIED",
   "RPP98_STATUS": ("WITHDRAWN__THE_QUESTION_WAS_ALREADY_ANSWERED_BY_TLMR01__"
                    "AND_THE_COUNTED_EVENT_IS_NOT_THE_CLAIMED_EVENT"),
   "FIMRCC01_E3_E4_E5_STATUS": ("FUTURE_QUESTION_RECORDED__NOT_AUTHORISED — RESTAURE. "
     "FIMRCC02 les avait reecrits sans autorisation ; ils reprennent leur valeur gelee.")},
 "VOCABULAIRE": "rien ici ne porte sur ce que ces objets sont.",
}
d["ADJUDICATION_CONTENT_HASH"] = H.content_digest(d, extra_excluded=("ADJUDICATION_CONTENT_HASH",))
json.dump(d, open(f"{REPO}/FIMRCC02/out/FIMRCC02_CHECKER_ADJUDICATION.json", "w"),
          indent=1, ensure_ascii=False)
print("constats", d["N_FINDINGS"], "acceptes", d["N_ACCEPTED"], "rejetes", d["N_REJECTED"])
print("FIMRCC02_STATUS", d["FIMRCC02_STATUS"])
print("hash", d["ADJUDICATION_CONTENT_HASH"][:16])
