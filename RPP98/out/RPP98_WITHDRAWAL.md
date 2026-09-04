# RPP98 — RETRAIT

`RPP98_STATUS = WITHDRAWN__THE_QUESTION_WAS_ALREADY_ANSWERED_BY_TLMR01__AND_THE_COUNTED_EVENT_IS_NOT_THE_CLAIMED_EVENT`

Le retour du checker adverse est commité verbatim en `bf47b4d`, **avant** cette adjudication.
Seize constats, seize acceptés, zéro rejeté (`RPP98_CHECKER_ADJUDICATION.json`).

## Pourquoi le retrait, en deux phrases

1. **La question n'était pas neuve.** `TLMR01/out/TLMR01_ANALYSIS.json`, généré le
   2026-08-25T14:07:05Z — quatre jours avant RPP98 — publie pour `LAW_C_MCTT01`, la loi exacte
   que TBRT02 fait tourner, sur **256 mondes** : **M1** = 8292 transitions vers deux centres ou
   plus sur 1 541 980 pas à un centre ; **M2** = 16 368 runs multi-centres, 44 atteignant la
   maturation, avec leurs terminateurs (`FORMED_A_THIRD_CENTRE`, `MERGED_TO_ONE_CENTRE`,
   `LOST_A_CENTRE_TO_A_SINGLE_Y`) ; **M4** = fraction médiane de l'horizon à un seul centre,
   0,7497. « Combien, quand, combien de temps la séparation tient-elle » **est** M1, M2 et M4.

2. **L'événement compté n'est pas l'événement revendiqué.** J'ai emprunté le seuil du
   déclencheur gelé (250) sans emprunter son état : le déclencheur court sur *exactement deux
   centres*, qu'un troisième brise, plus une porte locale sur X. Mon épisode fusionne
   deux-et-plus. 146 de mes 148 « épisodes tardifs persistants » atteignent trois composantes ou
   plus. Le compte de qualité-déclencheur est **2 événements sur 41 mondes**, et dans les deux
   les composantes font une et une, ou une et deux cellules.

## Ce que les fichiers de RPP98 restent

`RPP98_RESULT.json` n'est **pas modifié** : son `RESULT_CONTENT_HASH` est publié et le fichier
doit rester ce qu'il était quand je l'ai affirmé. Il est faux comme science et exact comme
arithmétique — le checker a tout recalculé avec son propre code et chaque chiffre se reproduit,
les sept blocs `dist()` à la dernière décimale. Le détecteur est correct. Les 123 archives sont
authentiques : 123/123 sha256 concordent avec le registre scellé.

Un calcul juste d'une grandeur déjà publiée sur une question déjà répondue n'est pas un résultat.

## Le constat qui compte, et il porte sur moi

Deux missions de suite retirées. J'ai écrit les sections 0, 3 et 4 de RPP98 **spécifiquement**
pour ne pas répéter les quatre échecs de RPP97, et trois des quatre sont revenus déguisés :
le temps absolu (F5), la statistique non normalisée (F6), la fenêtre vide par construction —
vide par extinction et non par calendrier, dans le bras dont l'intervention cause l'extinction
(F7). Plus la pseudo-réplication au triple que j'avais acceptée quatre commits plus tôt (F3).

Et le constat fatal ne relevait d'aucun raffinement statistique : **il suffisait de chercher dans
le dépôt avant de geler la question.** J'ai cité `TLMR01/code/tlmr01_world.py` par son chemin
dans mes propres définitions sans ouvrir `tlmr01_offline.py` à côté.

## Les quatre portes, en procédure et non en intention

1. **ANTÉRIORITÉ** — avant tout gel d'un pré-enregistrement, une recherche de travaux antérieurs
   dans le dépôt, mécanique et enregistrée. Outil : `EDL/code/edl_prior_art_gate.py`.
2. **UNITÉ** — l'unité indépendante est la graine de base, écrit dans le code d'agrégation.
3. **CONFONDANTS OBLIGATOIRES** — toute grandeur est testée contre le temps absolu et contre
   l'exposition (pas vivants) avant publication, pas après.
4. **L'OBJET AVANT LE SEUIL** — un seuil emprunté à une définition gelée s'applique au même état,
   ou la différence est écrite au titre.

## Statuts

Inchangés, sans exception. `H3_STATUS = NOT_TESTED`, `REPRODUCTION_STATUS = NOT_TESTED`,
`HEREDITY_STATUS = NOT_TESTED`, `AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED`,
`X_LAWSPEC_BASELINE = UNCHANGED`, `ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED`,
`COMPANION_PAPER_V1_1_STATUS = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED`,
`OMLDCT02_STATUS = INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED`,
`CLEA01_STATUS = CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED`,
`TBRT02_STATUS = CLOSED__RAW_COMPLETE__PRIMARY_ADJUDICATION_INCONCLUSIVE_BY_CONSTRUCTION`,
`RPP97_STATUS = WITHDRAWN_AS_A_DESCRIPTION__ARITHMETIC_SOUND__SCIENCE_MIS_SPECIFIED`.

Rien ici ne porte sur ce que ces objets sont.
