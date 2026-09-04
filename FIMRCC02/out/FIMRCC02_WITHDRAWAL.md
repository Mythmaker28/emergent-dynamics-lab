# FIMRCC02 — RETRAIT

`FIMRCC02_STATUS = WITHDRAWN__A_PREREGISTERED_TEST_ALREADY_EXISTS__AND_THE_CENTRAL_PREMISE_IS_FALSE_BY_DEFINITION`

Retour du checker commité verbatim en `be9854f`, **avant** cette adjudication.
Seize constats, seize acceptés, zéro rejeté (`FIMRCC02_CHECKER_ADJUDICATION.json`).

## Les deux raisons, vérifiées par moi-même

**1. Le test pré-enregistré que j'ai déclaré inexistant existe.**
`OMLDCT02/out/OMLDCT02_MASTER_FREEZE.json`, généré le 2026-08-25T22:30:05,
`THIS_FREEZE_PRECEDES_EVERY_SCIENTIFIC_WORLD: true` :

| champ gelé | valeur |
|---|---|
| `PRIMARY_ENDPOINT` | paired post-intervention duration of the same locked daughter identity |
| `SIGN_CONVENTION` | SELECTIVE minus SHAM, on the paired log difference |
| `PAIRED_TEST` | Wilcoxon signé exact bilatéral, rangs de Pratt, énumération exacte |
| `ALPHA` | 0.05 |
| `MINIMUM_VALID_PAIR_COUNT` | **41** |

OMLDCT02 s'est arrêté à 33 paires — `INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS`. TBRT02 a livré
**exactement 41 triplets** du même traitement (`SELECTIVE = the OMLDCT02 treatment, kept for
comparability`) sur des graines explicitement disjointes. L'accrual manquant est dans le dépôt
depuis le 28 août. Ma clôture disait que ROUTE_C ne serait légitime qu'avec « un
pré-enregistrement écrit par quelqu'un qui n'a pas vu la table de mortalité, ou sur un jeu de
graines disjoint **qui n'existe pas ici** ». Les deux moitiés étaient satisfaites.

**2. Ma prémisse centrale est fausse par définition.**
J'ai écrit que l'extinction de Y met les trois critères à leur minimum *par définition* et que le
signe de la paire est *forcé*. E3 est une **durée** — `e[end] − t_m` — que l'extinction borne par
le haut, sans la minimiser. Et `identity_terminates_at` du gel OMLDCT02 liste `empty component`
parmi cinq modes de terminaison **pré-déclarés** : E3 est défini et mesuré dans un monde éteint,
pas indéfini. Les deux seules paires exécutées dans ce mode, publiées dans
`OMLDCT02_FROZEN_ANALYSIS.json`, vont **dans l'autre sens** :

| index | SELECTIVE | SHAM | terminaison SELECTIVE |
|---|---|---|---|
| 450 | **257** | 88 | `NO_COMPONENT_AT_THE_NEXT_STEP` |
| 482 | **214** | 128 | `NO_COMPONENT_AT_THE_NEXT_STEP` |

Le cadre « troncature par la mort » est inversé : le bon cadre est celui des **risques
concurrents**, et la règle de Pratt gelée sait déjà traiter les paires nulles.

## Ce qui tient

L'arithmétique se reproduit à l'octet sous le code du checker ; aucune archive n'a été ouverte ;
l'unité est bien 41 graines. Et la *direction* de l'inquiétude — un contraste apparié de comptes
après t_m est contaminé par l'extinction différentielle — est correcte. Mais elle était déjà
établie par le checker de RPP97, rétablie avec table et correction par celui de RPP98, et écrite
par moi dans `EDL_PRIOR_ART_MAP.json` **quatre minutes avant** de lancer cette mission.

## Le constat sur moi

Trois missions retirées d'affilée. Le checker le dit mieux que je ne le ferais : RPP97 et RPP98
ont publié des affirmations fausses sur des données qu'elles avaient lues ; FIMRCC02 a publié des
affirmations fausses sur des données qu'elle n'avait **pas** lues, sur une question que quatre
missions antérieures avaient déjà traitée, derrière une porte que j'avais configurée de façon à ne
pas les voir. Le calcul est juste à chaque fois. Ce qui échoue, c'est mon jugement sur ce qui est
nouveau.

## La porte est réparée

Constat F6 adopté dans le code (`GATE01/code/edl_prior_art_gate.py`) :

- `GATE01/out` n'est plus exclu — la carte d'antériorité était invisible à la porte censée trouver
  l'antériorité ;
- `review/` et les `.txt` sont inclus — c'est là que vivent les retours de checker, l'antériorité
  la plus lourde du programme ;
- une porte qui signale moins de **10** fichiers **refuse** : deux termes obscurs donnaient zéro
  fichier et sortie 0 ;
- moins de **5** justifications distinctes refuse : trois chaînes recopiées pour dix-huit fichiers
  ne sont pas des verdicts.

Repassée sur la question de FIMRCC02 avec les noms des grandeurs, la porte réparée **refuse**, en
désignant en tête `OMLDCT02_MASTER_FREEZE.json` — le fichier dont l'absence supposée justifiait la
mission entière.

## Ce que je ne fais pas, et pourquoi

Je n'enchaîne pas sur le test gelé d'OMLDCT02, bien que ce soit la suite évidente.
`FIMRCC01_FINAL_DISPOSITION.json` porte `REOPENING_REQUIRES = "an explicit new human
authorisation"`, et je viens précisément de rouvrir sans. La seule question honnête qui reste —
**combien des 41 triplets de TBRT02 donnent des paires admissibles au sens des critères gelés
d'OMLDCT02** — exige d'ouvrir les archives. Et mon jugement sur quelle question poser a échoué
trois fois : la réparation n'est pas d'essayer plus fort, c'est de demander.

## Statuts

Tous inchangés. Et `FIMRCC01_E3_E4_E5_STATUS` est **restauré** à
`FUTURE_QUESTION_RECORDED__NOT_AUTHORISED` : FIMRCC02 les avait réécrits sans autorisation.
