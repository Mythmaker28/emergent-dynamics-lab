> **RETIRÉE — 2026-08-29.** La section 1 de ce document est FAUSSE : elle déclare que la
> trajectoire de `n_components` n'a jamais été examinée. TLMR01 l'avait examinée et publiée
> quatre jours plus tôt (`TLMR01/out/TLMR01_ANALYSIS.json`, M1/M2/M4, `LAW_C_MCTT01`, 256
> mondes). Voir `RPP98_WITHDRAWAL.md` et `RPP98_CHECKER_ADJUDICATION.json` — seize constats,
> seize acceptés. Le document est conservé tel qu'il a été gelé, bandeau excepté : ce que j'ai
> affirmé doit rester lisible à côté de sa réfutation.

# RPP98 — pré-enregistrement, écrit AVANT toute mesure

**Ceci est un vrai pré-enregistrement**, à la différence de RPP97 qui portait
`THIS_IS_NOT_A_PREREGISTRATION` et a été retirée. Mais il ne vaut que si l'on est exact sur ce qui
a déjà été vu. La section 0 s'y emploie avant tout le reste.

---

## 0. CE QUI A DÉJÀ ÉTÉ VU, ET QUI EST DONC INTERDIT DE SERVIR ICI

Le checker adverse de RPP97 (retour verbatim `2e390d2`) a mesuré, et j'ai lu, les quantités
suivantes. **Aucune ne peut faire l'objet d'une prédiction pré-enregistrée de ma part**, et toute
statistique qui en dépendrait serait post-hoc :

- la **taille** des composantes sur tout l'horizon : maximum médian 248 cellules, 104 archives sur
  123 dépassant 100 cellules, premiers franchissements à t ≈ 1183 (5 cellules) et t ≈ 3606 (100) ;
- la **compacité** des composantes tardives : maximum jamais atteint 0,42 à 0,556, jamais 0,7 —
  ce sont des nuages percolants, pas des taches ;
- le **contraste cœur/périphérie** sur X, sur **SY**, sur la **capacité libre** et sur nY, pour les
  composantes ≥ 100 cellules : **nul sur les quatre champs** (médianes −0,005, +0,0008, −0,0018,
  +0,0000 ; fractions positives 0,489 à 0,509 sur 2877 composantes-pas dans 39 mondes) ;
- `n_components` **à t ≥ 10000** : médiane 1 ;
- l'**extinction de Y** dans 19 archives, dont 12 des 41 bras SELECTIVE ;
- le profil de S2 en fonction de t − t_m, maximum vers +750 à +1000.

**Conséquence directe :** la question que j'avais annoncée à la relève précédente — « la déplétion
du substrat structure-t-elle les corps étendus ? » — **est déjà répondue, et par la négative**. La
poser en pré-enregistrement serait une tricherie. Elle est abandonnée.

## 1. La question, choisie parce qu'elle n'a pas été regardée

`n_components` est enregistré à chaque pas dans `s[:,7]`, sur les 11 000 pas. Le checker n'en a lu
que la valeur finale. **La trajectoire complète du nombre de composantes n'a jamais été
examinée** — ni par RPP97, ni par le checker, ni par TBRT02, dont le déclencheur gelé ne lit que
la première séquence de 250 pas consécutifs à exactement deux composantes.

> **Les transitions vers deux composantes ou plus se produisent-elles ailleurs que dans la fenêtre
> que le déclencheur sélectionne, et si oui : combien, quand, et pendant combien de temps la
> séparation tient-elle ?**

Aucun monde neuf. Tout se lit dans `s[:,7]` et `k_ncells` des 123 archives déjà scellées.

## 2. Définitions, fixées ici

**Un ÉPISODE MULTI-COMPOSANTES** est un intervalle maximal de pas consécutifs pendant lequel
`n_components ≥ 2`. Ses attributs, tous lus et non estimés :

- `t_start`, `t_end`, `duree = t_end − t_start + 1` ;
- `n_max` : la valeur maximale de `n_components` pendant l'épisode ;
- `masse_parent` : `k_ncells` de la plus grande composante au pas `t_start − 1` ;
- `chevauche_t_m` : vrai si `[t_start, t_end]` contient `t_m`.

**Un épisode est dit PERSISTANT** si `duree ≥ 250` — le même seuil que le déclencheur gelé de
FDFLT01, repris pour comparabilité et non choisi ici.

**Un épisode est dit TARDIF** si `t_start > t_m`.

## 3. Les grandeurs rapportées

Purement descriptives, toutes **sans échelle ou en comptages bruts**, jamais des différences de
densités contre un total mobile (leçon de RPP97) :

- **N_episodes** par archive, et la fraction persistants ;
- **distribution de `duree`** : min, quartiles, max ;
- **distribution de `masse_parent`** au début de chaque épisode ;
- **N_episodes_tardifs** par archive, et leur `masse_parent` ;
- **fraction du temps** passé à `n_components ≥ 2`, par archive : `sum(duree)/11000` ;
- par bras, **après t_m uniquement**, pour que le contraste ne soit pas vide par construction.

## 4. Faisabilité vérifiée AVANT gel — la leçon n°3 de RPP97

RPP97 a gelé une fenêtre de 2000 pas alors qu'aucun t_m n'atteignait 2000. Ici :

- la trajectoire couvre `[0, 10999]`, soit **11 000 pas disponibles dans chaque archive**, sans
  exception, puisque `steps_executed = 11000` est vérifié au registre pour les 123 archives ;
- `t_m` va de 370 à 1673, donc l'intervalle **après t_m compte au minimum 9 327 pas** dans le pire
  cas et 10 630 dans le meilleur ;
- aucune fenêtre n'est définie relativement à un point qui pourrait manquer. **Il n'y a rien à
  tronquer.**

Cette section est ce que RPP97 n'avait pas et qui lui a coûté sa fenêtre de contrôle.

## 5. Le contrôle

La question est descriptive, donc le contrôle n'est pas un contraste mais une **borne de
trivialité** : si les épisodes multi-composantes sont innombrables et d'une durée de un ou deux
pas, ils ne décrivent qu'un scintillement du critère de liaison simple à rayon 5, et non un fait
sur les objets. C'est pourquoi `duree` est rapportée en distribution complète et non en moyenne,
et pourquoi le seuil de persistance est repris du déclencheur gelé plutôt qu'inventé.

## 6. Ce qui compterait comme un résultat NUL

- aucun épisode persistant tardif dans aucune archive → le monde converge vers un corps unique et
  la fenêtre du déclencheur est le seul lieu où la question se pose ;
- ou : des épisodes persistants tardifs si nombreux et si brefs qu'ils ne se distinguent pas du
  bruit de la règle de liaison.

Les deux sont des réponses recevables et seront rapportées telles quelles.

## 7. Test de capacité, avant d'ouvrir une archive

Le détecteur d'épisodes sera exercé sur des séries `n_components` synthétiques dont la réponse est
connue par construction : une série constante à 1 → zéro épisode ; une série avec un plateau connu
à 2 → un épisode de la longueur exacte ; deux plateaux séparés → deux épisodes ; un créneau d'un
seul pas → un épisode de durée 1, non persistant. Si le détecteur ne restitue pas exactement ces
comptes et ces durées, la mesure ne se fait pas.

## 8. Le code d'agrégation sera commité

RPP97 ne pouvait pas être régénérée depuis le dépôt : seul le code de mesure y était. Ici le
script qui produit le fichier de résultat est commité au même titre que celui qui lit les archives.

## 9. Vocabulaire

On dira **« épisode multi-composantes »** et **« transition vers deux composantes »**. On ne dira
pas « division », ni « corps qui se divise », ni rien qui suppose qu'un objet s'est scindé plutôt
que que deux amas ont dérivé au-delà du rayon de liaison. C'est le constat n°12 du checker, adopté.

## 10. Statuts inchangés

H3_STATUS = NOT_TESTED ; REPRODUCTION_STATUS = NOT_TESTED ; HEREDITY_STATUS = NOT_TESTED ;
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED ; X_LAWSPEC_BASELINE = UNCHANGED ;
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED ;
COMPANION_PAPER_V1_1_STATUS = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED ;
OMLDCT02_STATUS = INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED ;
CLEA01_STATUS = CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED ;
TBRT02_STATUS = CLOSED__RAW_COMPLETE__PRIMARY_ADJUDICATION_INCONCLUSIVE_BY_CONSTRUCTION ;
RPP97_STATUS = WITHDRAWN_AS_A_DESCRIPTION__ARITHMETIC_SOUND__SCIENCE_MIS_SPECIFIED.

Rien ici ne portera sur ce que ces objets sont.
