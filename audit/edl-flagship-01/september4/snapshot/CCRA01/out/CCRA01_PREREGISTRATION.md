# CCRA01 — PRÉ-ENREGISTREMENT GELÉ

**Mission** : CCRA01 — *Competing-risks Cause-specific Re-Analysis 01*
**Laboratoire** : Emergent Life Lab
**Statut du rédacteur** : AVEUGLE. Cette spécification a été écrite avant toute
consultation d'une quelconque valeur d'issue du jeu de 41 paires.
**Objet gelé** : le jeu apparié SHAM / SELECTIVE à 41 paires issu de la campagne TBRT02.
**Convention de signe héritée** : SELECTIVE moins SHAM.

---

## 0. Pourquoi cette mission existe

Le contraste primaire des missions antérieures oppose deux bras sur une durée
d'intervalle d'identité. Ce contraste suppose implicitement que les deux bras
offrent le **même ensemble de façons de terminer l'intervalle**. Le code gelé
montre que c'est faux. CCRA01 ne rejoue pas le même test : il change d'estimand
pour en construire un qui soit défini sur un ensemble d'issues identique dans les
deux bras.

---

## 1. La question, en une phrase

**Question primaire** : sur les mêmes 41 graines appariées, le retrait du Y du
parent au pas déclencheur `t_m` dégrade-t-il l'issue de l'intervalle d'identité
de la fille verrouillée, lorsque cette issue est mesurée par un **rang composite
dont l'ensemble des valeurs atteignables est identique dans les deux bras** ?

**Ce sur quoi la question ne porte pas** — à lire comme faisant partie de la question :

- elle ne porte pas sur un mécanisme causal interne ni sur une quelconque
  fonction que le parent remplirait ;
- elle ne porte pas sur la durée brute, ni sur l'exposition brute, ni sur leur
  rapport logarithmique ;
- elle ne porte pas sur le bras DISPLACED de TBRT02, absent du jeu à 41 paires ;
- elle ne porte pas sur `R0`, `R1`, `R2`, `R3` ni sur le critère de multiplication
  minimale, dont les statuts restent inchangés ;
- elle ne porte sur aucune propriété d'un système autre que cet automate, à
  L = 36, CAP = 16, `T_HORIZON = 11000`, `CORE_R = 5.0`, sous `LAW_C_MCTT01` ;
- elle ne porte pas sur la question de savoir si un intervalle « aurait continué »
  au-delà de sa terminaison : la règle d'identité stricte est un instrument de
  comptabilité, pas une observation physique.

---

## 2. Le mapping chaîne → cause

### 2.1 Ce que le code fait réellement

Source lue : `/home/claude/edl/OMLDCT02/code/omldct02_e3_b.py` (classifieur B),
recoupée sur `/home/claude/edl/OMLDCT02/code/omldct02_e3_a.py` (classifieur A).

La règle d'appariement gelée est `_link_map`, **lignes 107 à 131**. Elle construit
la matrice booléenne `M[i, j] = (distance torique au carré ≤ CORE_R²)` entre les
centres du pas `t` et ceux du pas `t+1`, puis la réduit en deux vecteurs de
comptes, **ligne 125** :

- `rc[i]` = nombre de successeurs candidats dans le rayon, pour le centre `i` du pas `t` ;
- `cc[j]` = nombre de prédécesseurs candidats dans le rayon, pour le centre `j` du pas `t+1`.

Un lien `i → j` n'est retenu que si `rc[i] == 1` **et** `cc[j] == 1`
(**lignes 126 à 130**). La boucle de poursuite occupe les **lignes 204 à 228**, et
l'attribution de la chaîne de terminaison se fait aux **lignes 216 à 220** :

| ligne | condition atteinte | chaîne émise |
|---|---|---|
| 206–207 | `t + 1 >= W.T` | `REACHED_THE_WINDOW_HORIZON` |
| 208–209 | `W.rows(t+1) is None` — aucune ligne de cellule dans le monde entier | `NO_COMPONENT_AT_THE_NEXT_STEP` |
| 217 | `rc[cur] == 0` | `OUT_OF_RANGE` |
| 218 | `rc[cur] > 1` | `SPLIT_OR_TIE` |
| 219 | branche `else`, donc `rc[cur] == 1` et `cc[j] > 1` | `MERGE` |

### 2.2 Fait n°1 — `OUT_OF_RANGE` et `NO_COMPONENT_AT_THE_NEXT_STEP` ne sont pas deux causes

Ces deux chaînes ne sont pas deux événements disjoints proprement nommés. Elles
sont **le même prédicat**, scindé par un retour anticipé.

La démonstration est dans le code, pas dans une interprétation. À la **ligne 116**,
`_link_map` traite le cas où le pas `t+1` ne contient aucun centre en renvoyant
`rc = [0] * npv`. Si le retour anticipé des **lignes 208–209** n'existait pas, un
monde vide au pas `t+1` produirait `cn == []`, donc `rc[cur] == 0`, donc la
**ligne 217**, donc la chaîne `OUT_OF_RANGE`. Les deux chaînes recouvrent
exactement une seule et même condition : **« zéro successeur liable dans
`CORE_R` »**. Ce qui les sépare n'est pas une propriété du centre suivi, mais une
propriété **globale du monde** : le monde entier se trouve-t-il vide de Y au même
pas, ou non.

Le classifieur A reproduit la même scission (`omldct02_e3_a.py`, ligne 58).

### 2.3 Fait n°2 — cette scission est corrélée au bras, par construction

Considérons l'événement physique unique : *le Y de la fille s'éteint*.

- Dans **SHAM**, le Y du parent n'a pas été retiré. Le monde contient donc encore
  au moins une composante ailleurs. La chaîne émise sera `OUT_OF_RANGE`.
- Dans **SELECTIVE**, le Y du parent a été retiré par le canal de décroissance
  `Y -> WY`. Si la fille était le dernier objet, le monde devient vide et la
  chaîne émise sera `NO_COMPONENT_AT_THE_NEXT_STEP`.

**Le même événement change donc d'étiquette selon le bras.** Toute analyse qui
traite ces deux chaînes comme deux causes distinctes fabriquerait un effet de bras
là où il n'y a qu'un artefact de nommage. C'est le premier motif de fusion, et il
est décisif.

### 2.4 Fait n°3 — le canal `MERGE` n'est pas disponible dans les deux bras

`MERGE` est la branche `else` de la **ligne 219** : elle exige `rc[cur] == 1` et
`cc[j] > 1`. Or `cc[j]` compte des prédécesseurs. Si le pas `t` ne contient
qu'**un seul** centre (`npv == 1`), alors pour tout `j`, `cc[j] ≤ 1`. Si de plus
`rc[cur] == 1`, alors `M[cur, j]` est vrai, donc `cc[j] ≥ 1`, donc `cc[j] == 1`
exactement, donc le lien est retenu et **aucune terminaison n'a lieu**.

> **Théorème d'indisponibilité.** Lorsque la fille verrouillée est la seule
> composante du monde au pas `t`, la chaîne `MERGE` est **arithmétiquement
> inatteignable** au pas `t+1`. Ce n'est pas une observation, c'est une propriété
> de `_link_map` (lignes 116, 125, 126–130) et de la branche de la ligne 219.

Le retrait du Y du parent dans le bras SELECTIVE est précisément ce qui peut
rendre la fille seule au monde. **L'ensemble des risques concurrents n'est donc
pas le même dans les deux bras.** Deux conséquences, toutes deux fatales à une
analyse naïve :

1. Un contraste de durées brutes n'est pas à exposition égale. Retirer un canal de
   terminaison **allonge mécaniquement** les intervalles du bras SELECTIVE, sans
   qu'aucune dynamique n'ait changé. L'artefact pousse donc vers la conclusion
   absurde « retirer le parent fait durer l'intervalle plus longtemps ».
2. Une analyse **cause-spécifique** est également contaminée : la suppression d'un
   risque concurrent gonfle mécaniquement les hasards cause-spécifiques de tous
   les canaux restants. Un hasard cause-spécifique par canal n'est donc pas
   identifiable ici sans une hypothèse d'indépendance des risques que rien ne
   soutient.

### 2.5 Le mapping retenu

Le mapping est construit sur le **seul prédicat qui soit disponible à l'identique
dans les deux bras** : `rc[cur] == 0` contre `rc[cur] >= 1`.

| chaîne du classifieur gelé | CAUSE (identifiant gelé) | rang |
|---|---|---|
| `OUT_OF_RANGE` | `NO_LINKABLE_SUCCESSOR` | 0 |
| `NO_COMPONENT_AT_THE_NEXT_STEP` | `NO_LINKABLE_SUCCESSOR` | 0 |
| `SPLIT_OR_TIE` | `AMBIGUOUS_CONTINUATION` | 1 |
| `MERGE` | `AMBIGUOUS_CONTINUATION` | 1 |
| `REACHED_THE_WINDOW_HORIZON` | `NO_TERMINATION_OBSERVED` | 2 |

Lecture des deux causes terminales, en langage gelé :

- **`NO_LINKABLE_SUCCESSOR`** : au pas suivant, aucune composante ne se trouve
  dans `CORE_R` du centroïde suivi. Le Y de la fille s'est éteint, ou la
  composante s'est dispersée au-delà du rayon de liaison. Il n'y a rien à
  continuer.
- **`AMBIGUOUS_CONTINUATION`** : au moins une composante se trouve dans `CORE_R`,
  mais la règle stricte refuse de nommer un successeur unique. La matière suivie
  n'a pas disparu ; c'est la comptabilité d'identité qui s'arrête.

**Propriété d'arm-symétrie, pré-déclarée comme théorème.** Le rang 1 exige
`rc[cur] >= 2` (via `SPLIT_OR_TIE`, ligne 218) **ou** `cc[j] >= 2` (via `MERGE`,
ligne 219). La première condition ne porte que sur le nombre de **successeurs** et
ne requiert **aucun** second prédécesseur. Le rang 1 est donc atteignable même
lorsque la fille est le seul objet du monde. L'indisponibilité de `MERGE` seul
**ne retire aucun rang de l'ensemble des issues atteignables**. Les trois rangs
sont atteignables dans les deux bras.

### 2.6 Limites assumées de ce mapping

Elles sont assumées, pas contournées.

1. **La fusion 0 est plus large que « le Y s'éteint ».** `OUT_OF_RANGE` recouvre
   aussi le cas où le centroïde suivi se déplace de plus de `CORE_R` en un pas.
   Ce cas n'est pas séparable avec les champs disponibles. Le rang 0 se lit donc
   « aucun successeur liable », jamais « extinction » tout court.
2. **La fusion 1 agrège deux mécanismes physiquement distincts** (séparation en
   deux composantes en portée ; coalescence avec une autre composante). Cette
   agrégation est le prix payé pour l'arm-symétrie, et elle est délibérée : le
   mapping préfère perdre de la résolution plutôt que gagner un effet artefactuel.
3. **Le rang ordonne des issues de la règle de comptabilité, pas des états du
   monde.** Aucun rang ne mesure une quelconque compétence de la fille.
4. **Le rang 2 pourrait ne jamais être observé.** `LATEST_ALLOWED_TRIGGER = 6500`
   et `T_HORIZON = 11000` le rendent possible en principe ; il est pré-déclaré
   par prudence, sans qu'aucune valeur ne soit connue.
5. **Une cinquième chaîne inconnue est une invalidité technique**, pas une
   catégorie à créer après coup (§7).

---

## 3. L'ESTIMAND primaire

### 3.1 Le choix : (b) composite ordonné

Le choix est **(b) un composite ordonné**, et non (a) une analyse cause-spécifique.
Justification, écrite avant toute donnée :

- **(a) n'est pas identifiable ici.** §2.4 : la disponibilité du canal `MERGE`
  dépend du bras. Un hasard cause-spécifique estimé canal par canal mélange un
  effet de traitement et une modification de l'ensemble des risques concurrents.
  Il n'existe aucune hypothèse d'indépendance des risques défendable dans ce
  système, où les canaux sont définis par des comptes sur la même matrice `M`.
- **(a) fabriquerait de surcroît l'artefact de §2.3**, en séparant deux chaînes
  qui sont un seul prédicat.
- **(b) est constructible de sorte que son ensemble d'issues soit identique dans
  les deux bras** (théorème de §2.5). C'est la seule construction proposée ici qui
  jouisse de cette propriété.
- **(b) évite un défaut de définition du contraste logarithmique.** Une durée nulle
  est atteignable (`duration = end - t_m`, `omldct02_e3_b.py` ligne 230, avec
  `end` initialisé à `t_m` ligne 203). Le contraste logarithmique n'est **pas
  défini** quand une seule des deux durées est nulle. Cette indéfinition est
  elle-même dépendante de l'issue **et asymétrique entre bras**. Un estimand dont
  la définition même exige d'écarter des paires selon leur issue réalisée dans le
  bras traité est disqualifié par la règle de rétention de §5. Le composite ordonné
  n'a pas ce défaut : une durée nulle y est une valeur ordinaire.

### 3.2 Définition du composite

Pour chaque bras d'une paire, on forme le couple ordonné

```
OUTCOME = ( rank , duration )
```

où `rank` vient du tableau de §2.5 et `duration` est le champ `*_duration` de
l'enregistrement. **Rangement de la pire à la meilleure issue, pré-déclaré :**

1. le rang domine — un rang plus élevé est **meilleur** ; `NO_LINKABLE_SUCCESSOR`
   (0) est la pire issue, `NO_TERMINATION_OBSERVED` (2) la meilleure ;
2. à rang égal, une durée plus grande est **meilleure**.

Défendabilité de cet ordre, pré-déclarée : le rang 0 est le seul où plus rien
n'est liable au centre suivi ; le rang 1 laisse au moins un successeur en portée ;
le rang 2 signifie que l'intervalle ne s'est pas terminé dans la fenêtre observée.
L'ordre va donc du « rien à continuer » vers le « pas de terminaison observée ».
À rang égal, un intervalle d'identité plus long est ordonné au-dessus d'un
intervalle plus court.

**Pourquoi lexicographique et non additif.** Le rang est la couche
arm-symétrique ; la durée ne l'est pas entièrement (l'indisponibilité de `MERGE`
peut allonger un intervalle qui se terminera plus tard au rang 1). L'ordre
lexicographique confine ce résidu au **départage à l'intérieur d'un rang** et
fait reposer la comparaison primaire sur la quantité arm-symétrique. Un score
additif mélangerait les deux couches et rendrait l'artefact indissociable.

### 3.3 L'estimand

Pour chaque paire `i`, on définit la comparaison appariée

```
W_i = +1  si OUTCOME_SELECTIVE(i) >  OUTCOME_SHAM(i)      (SELECTIVE meilleur)
W_i = -1  si OUTCOME_SELECTIVE(i) <  OUTCOME_SHAM(i)      (SELECTIVE pire)
W_i =  0  si les deux couples sont identiques             (ex æquo)
```

**ESTIMAND PRIMAIRE** :

> `theta = P(W = -1) - P(W = +1)`, la probabilité nette qu'une paire appariée
> classe SELECTIVE strictement en dessous de SHAM sur le composite ordonné.

`theta = 0` sous l'hypothèse nulle d'échangeabilité des étiquettes de bras à
l'intérieur d'une paire. `theta > 0` signifie « SELECTIVE est plus souvent la
pire des deux ». Aucune quantité latente n'est estimée, aucun modèle n'est
ajusté, aucune hypothèse d'indépendance des risques n'est invoquée.

### 3.4 Ce que `theta` est, exactement : un effet total

`theta` est l'**effet total** de l'intervention sur l'issue ordonnée, y compris la
part de cet effet qui transite par la modification de l'ensemble des canaux de
terminaison disponibles. Ce point est essentiel et il est gelé ici :

- Les deux bras partent du **même état physique et du même état de générateur
  aléatoire** au pas `t_m` (`tbrt02_fork.py`, lignes 69–76 : `PHYSICAL_STATE_IDENTICAL`
  et `RNG_STATE_IDENTICAL` sont vérifiés). L'appariement est exact, par
  construction, et non par ajustement.
- Un effet total sur une issue ordonnée est donc identifié par la seule
  randomisation appariée. Il n'exige **aucune** hypothèse d'indépendance des
  risques concurrents.
- En revanche, un hasard **cause-spécifique** par canal exigerait une telle
  hypothèse, et §2.4 montre qu'elle serait fausse ici. C'est la raison technique
  du choix (b) sur (a).

Corollaire assumé : si le retrait du Y du parent rend la fille seule au monde, et
si le fait d'être seule modifie l'issue de l'intervalle, cette modification **fait
partie de l'effet mesuré** et n'est pas un biais. Ce qui serait un biais, et que
le mapping de §2.5 élimine, c'est qu'un **même** événement reçoive **deux
étiquettes différentes selon le bras** (§2.3).

---

## 4. La statistique de test, exacte, et alpha

**Statistique** : test des signes apparié, exact.

Soient `m = #{i : W_i ≠ 0}` le nombre de paires discordantes et
`k = #{i : W_i = -1}` le nombre de paires où SELECTIVE est la pire.
Sous H0 (échangeabilité des étiquettes de bras à l'intérieur d'une paire),
`k ~ Binomiale(m, 1/2)`, exactement.

**p unilatérale, direction pré-déclarée** :

```
p = P(K >= k)  =  ( somme_{i=k..m} C(m, i) )  /  2^m
```

calculée en arithmétique **entière exacte** (`math.comb` et `fractions.Fraction`),
sans flottant, donc sans erreur d'arrondi au seuil.

**alpha = 0.025 unilatérale**, soit exactement `Fraction(1, 40)`, gelée. Elle
correspond à la convention conservatrice équivalente à 0,05 bilatérale. La
comparaison `p <= alpha` est faite entre deux `Fraction`, donc exacte.

**Traitement des ex æquo** : les paires `W_i = 0` sont retirées du dénominateur
(convention du test des signes). Ce retrait est symétrique entre bras par
construction — il ne dépend d'aucune étiquette de bras — et il est comptabilisé
et reporté.

**Valeurs critiques exactes, pré-calculées et gelées** (aucune donnée réelle n'a
servi à les obtenir) :

| m (paires discordantes) | k critique | p exacte au seuil |
|---|---|---|
| 41 | 28 | 0,013767 |
| 40 | 27 | 0,019239 |
| 38 | 26 | 0,016776 |
| 35 | 24 | 0,020480 |
| 30 | 21 | 0,021387 |
| 20 | 15 | 0,020695 |
| 10 |  9 | 0,010742 |
|  6 |  6 | 0,015625 |

**Plancher de résolution, gelé.** Le plus petit `p` atteignable avec `m` paires
discordantes vaut `2^-m`. Il faut `2^-m <= 1/40`, donc **`m >= 6`**
(`2^-5 = 0,03125 > 0,025` ; `2^-6 = 0,015625 <= 0,025`). En dessous de six paires
discordantes, le test **ne peut pas** franchir son seuil, quelles que soient les
données : l'issue est alors NON CONCLUANT et jamais NÉGATIF (§8).

**Analyses secondaires, pré-déclarées comme NON confirmatoires** — elles ne
peuvent ni créer ni annuler la conclusion primaire :

- S1 : le même test des signes, en remplaçant la durée par l'exposition comme
  départage à rang égal ;
- S2 : le tableau de contingence bras × chaîne de terminaison (4 ou 5 colonnes),
  purement descriptif ;
- S3 : le tableau bras × cause après mapping (3 colonnes), purement descriptif ;
- S4 : le nombre de paires où le rang seul départage, et le nombre où il a fallu
  descendre à la durée — mesure directe de la part du résultat qui repose sur la
  couche arm-symétrique.

---

## 5. La règle de rétention

**Règle gelée : les 41 paires entrent toutes. Aucune n'est écartée.**

C'est la seule règle qui satisfasse la contrainte imposée : ne jamais conditionner
sur une variable réalisée après le traitement dans le seul bras traité. Le
composite est défini pour les quatre chaînes et pour toute durée entière `>= 0`,
donc aucune paire ne peut être « indéfinie ».

**Exclusions nommées d'avance et interdites.** Aucune des règles suivantes ne sera
appliquée, quelles que soient les données observées :

- écarter les paires où SELECTIVE a terminé par `NO_COMPONENT_AT_THE_NEXT_STEP`
  — conditionnement sur l'issue réalisée du seul bras traité ;
- écarter les paires où le canal `MERGE` était indisponible dans SELECTIVE
  — conditionnement sur un état du monde postérieur au traitement, dans le seul
  bras traité ;
- écarter les paires de durée nulle, ou de durée nulle dans un seul bras
  — conditionnement sur l'issue, et c'est exactement l'exclusion qu'un contraste
  logarithmique aurait exigée (§3.1) ;
- écarter les paires selon `t_m`, selon l'exposition, ou selon tout autre champ
  réalisé après `t_m` ;
- écarter une paire au motif que son issue paraît aberrante.

**Contrôles d'intégrité, opérant au niveau de la campagne entière et jamais au
niveau d'une paire.** Ils ne retirent aucune paire : ils invalident le run entier,
qui devient NON CONCLUANT pour cause technique (§8).

- I1 : le fichier doit contenir **exactement 41** enregistrements. Sinon le
  programme **refuse de tourner**.
- I2 : chaque enregistrement doit porter les onze champs du schéma.
- I3 : les deux chaînes de terminaison doivent appartenir à l'ensemble gelé de
  cinq chaînes. Une chaîne inconnue invalide le run.
- I4 : `duration >= 0` et `exposure >= 0` dans les deux bras.
- I5 : **invariant différentiel**, dérivé du code et non des données. Le nombre de
  lignes de l'intervalle vaut `duration + 1` (`omldct02_e3_b.py`, ligne 236) et
  chaque ligne contribue à l'exposition au moins 1, puisqu'une composante possède
  au moins une cellule Y-occupée et que `nY >= 1` sur une cellule occupée
  (accumulation lignes 196 et 222–223). Donc **`exposure >= duration + 1`** dans
  chaque bras. Une violation signale une corruption de schéma, pas un résultat.
- I6 : les indices doivent être distincts.

Ces six contrôles sont indépendants de toute étiquette de bras et de tout ordre
de préférence entre issues.

---

## 6. La direction pré-déclarée, et ce qui compterait comme réfutation

**Direction pré-déclarée, unilatérale** :

> **H1 : `theta > 0`.** SELECTIVE est plus souvent la pire des deux issues du
> composite ordonné. Le retrait du Y du parent dégrade l'issue de l'intervalle
> d'identité de la fille verrouillée.

**Propriété de conservatisme, énoncée avec sa portée exacte.** Il faut distinguer
deux couches, et ne pas revendiquer plus que ce qui est vrai.

- **Couche durée — conservatisme établi.** L'indisponibilité de `MERGE` retire un
  canal de terminaison au bras SELECTIVE ; l'intervalle se termine donc plus tard.
  Cette inflation pousse `theta` vers le **négatif**, soit dans la direction
  **opposée** à H1. C'est exactement l'artefact qui invalide un contraste de
  durées brutes ou de leur rapport logarithmique, et il **ne peut pas** fabriquer
  un franchissement du seuil dans la direction pré-déclarée. Ce point est vérifié
  par le contrôle adverse C3 de §11.
- **Couche rang — pas de conservatisme revendiqué.** Lorsque `MERGE` est retiré,
  l'intervalle poursuit jusqu'à un canal ultérieur, dont le rang peut être 1
  (inchangé) ou 0 (dégradé). Le rang peut donc se dégrader. **Ce n'est pas un
  biais** : c'est une conséquence réelle de l'intervention sur le monde, et §3.4
  établit qu'elle appartient à l'effet total mesuré. Aucune revendication de
  conservatisme n'est faite sur cette couche, et aucune n'est nécessaire.
- **Ce qui est éliminé, et non pas seulement atténué.** Le renommage dépendant du
  bras de §2.3 — `OUT_OF_RANGE` contre `NO_COMPONENT_AT_THE_NEXT_STEP` — est
  neutralisé exactement par le mapping de §2.5. Le contrôle adverse C5 de §11
  l'exige sous forme d'une invariance **bit à bit** de la décision.

Le test est unilatéral dans le sens de H1 pour la raison de la couche durée, et
cette raison est gelée ici, avant toute donnée.

**Ce qui compterait comme réfutation de H1** :

- `p > alpha` avec `m >= 6` : H1 n'est pas soutenue par ces données, à la
  résolution du design. C'est l'issue NÉGATIF.
- Un résultat dans la direction opposée (`k` nettement inférieur à `m/2`) **ne
  sera pas retourné en une revendication** que le retrait améliore l'issue. Il est
  au contraire l'empreinte attendue de l'artefact de §2.4, et il sera rapporté
  comme tel, sans revendication. Cette clause est gelée pour empêcher toute
  lecture opportuniste d'un signe inversé.

**Ce qui ne compterait pas comme réfutation** : une taille d'effet jugée petite,
un désaccord avec une mission antérieure, ou l'absence de significativité sur une
analyse secondaire S1 à S4.

---

## 7. Chaînes inattendues

L'ensemble gelé des chaînes admissibles est de cinq éléments : les quatre
annoncées, plus `REACHED_THE_WINDOW_HORIZON`, que le classifieur peut émettre
(`omldct02_e3_b.py`, lignes 206–207 ; `omldct02_e3_a.py`, ligne 55). Toute autre
chaîne déclenche I3 : le run entier devient NON CONCLUANT pour invalidité
technique. **Aucune catégorie nouvelle ne sera créée après avoir vu les données**,
et aucune chaîne inconnue ne sera repliée sur une catégorie existante.

---

## 8. Les trois issues, nommées d'avance

Elles sont mutuellement exclusives et exhaustives, et elles sont décidées par le
code, pas par un jugement.

**CONFIRMATOIRE** — `m >= 6` **et** `p <= 1/40` dans la direction pré-déclarée.
Énoncé autorisé, et rien de plus : *sur ces 41 paires appariées, l'issue de
l'intervalle d'identité de la fille verrouillée, mesurée par le composite ordonné
arm-symétrique de §3.2, est significativement pire dans le bras SELECTIVE que
dans le bras SHAM, au seuil unilatéral exact de 0,025.*

**NÉGATIF** — `m >= 6` **et** `p > 1/40`. Un critère gelé a été exécuté et n'a pas
été franchi, à une résolution démontrée suffisante pour qu'il pût l'être. Statut
de registre proposé : `NEGATIVE_BUT_VALID`. Ce n'est pas une perte. Aucune
revendication d'équivalence ni d'absence d'effet ne s'y attache.

**NON CONCLUANT** — `m < 6` (le design ne pouvait pas franchir son seuil), **ou**
échec d'un contrôle d'intégrité I1 à I6, **ou** présence d'une chaîne hors de
l'ensemble gelé. Aucune revendication dans aucune direction.

---

## 9. CE QUE CE TEST NE DIT PAS

1. Il ne dit rien sur une quelconque capacité de la fille verrouillée. Un rang est
   une propriété de la règle de comptabilité d'identité, pas d'un objet.
2. Il ne dit rien sur un mécanisme. Un composite ordonné n'identifie pas de voie
   causale ; il compare deux issues appariées.
3. Il ne dit rien sur les hasards cause-spécifiques par canal. §2.4 établit qu'ils
   ne sont pas identifiables ici ; l'analyse est construite pour ne pas en dépendre.
4. Il ne dit rien sur ce qu'aurait donné un bras où le canal `MERGE` serait resté
   disponible. Ce bras n'existe pas dans le jeu.
5. Il ne dit rien sur la durée en tant que grandeur. La durée n'entre que comme
   départage à l'intérieur d'un rang, et jamais sur une échelle.
6. Il ne dit rien sur les statuts permanents du registre, qui restent inchangés et
   sont ré-émis : `REPRODUCTION_STATUS = NOT_TESTED`,
   `HEREDITY_STATUS = NOT_TESTED`, `H3_STATUS = NOT_TESTED`,
   `AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED`,
   `ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED`.
7. Il ne dit rien hors de ce jeu de paramètres gelé, ni pour un autre `CORE_R`,
   ni pour un autre `L`, ni sous une autre loi.
8. Il ne dit rien sur le bras DISPLACED, ni sur la condition de réfutation de
   TBRT02, qui sont hors périmètre.
9. Il ne renverse ni ne confirme aucune conclusion d'une mission antérieure. Il
   change d'estimand ; il ne rejuge pas l'ancien.
10. Une définition d'un centre comme composante **connexe** est contestée dans la
    littérature (Hintze & Bohm, *npj Complexity*, 16 février 2026, admettent des
    réplicateurs spatialement disjoints). Tout ce qui précède est conditionnel à
    la définition connexe gelée par `CORE_R = 5.0`.

---

## 10. CONTAMINATION

**Ce que le rédacteur a vu, exhaustivement :**

1. **Le fait structurel `MERGE`**, tel qu'il lui a été transmis dans son mandat :
   le canal `MERGE` exige au moins deux prédécesseurs dans le rayon de liaison ;
   lorsque le Y du parent est retiré, la fille peut être le seul objet du monde,
   et `MERGE` devient alors arithmétiquement indisponible dans le bras SELECTIVE.
   Ce fait a été **vérifié indépendamment dans le code** (§2.4) et non accepté sur
   parole.
2. **Les fichiers de code et de design suivants, et eux seuls** :
   - `/home/claude/edl/OMLDCT02/code/omldct02_e3_b.py`
   - `/home/claude/edl/OMLDCT02/code/omldct02_e3_a.py`
   - `/home/claude/edl/OMLDCT02/code/omldct02_c3_raw.py`
   - `/home/claude/edl/TBRT02/out/TBRT02_MASTER_FREEZE.json`
   - `/home/claude/edl/TBRT02/code/tbrt02_fork.py`
   - `/home/claude/edl/FDOT01/code/fdot01_centres.py`
3. Le protocole de laboratoire ELAB (vocabulaire gelé, statuts de registre,
   protocole de mission), qui ne contient aucune valeur d'issue de ce jeu.

**Déclaration explicite :**

> Le rédacteur de ce pré-enregistrement **n'a vu aucune valeur d'issue** du jeu de
> 41 paires. Il ne connaît, pour aucune paire et pour aucun bras : ni `index`, ni
> `t_m`, ni `SELECTIVE_duration`, ni `SHAM_duration`, ni `SELECTIVE_exposure`, ni
> `SHAM_exposure`, ni `log_duration_difference`, ni `log_exposure_difference`, ni
> `SELECTIVE_termination`, ni `SHAM_termination`. Il ne connaît ni le nombre de
> paires discordantes, ni le signe de la statistique, ni aucune fréquence de
> chaîne de terminaison, ni aucun résultat des missions OMLDCT03, FIMRCC02,
> TBRT02 (sections C3, C4, C4bis, C5), RPP97, RPP98, CLOSE01, GATE01 ou REVIEW01.

**Fichiers dont l'ouverture était interdite et qui n'ont pas été ouverts**, par
aucun moyen direct ni indirect (ni lecture, ni `grep`, ni `cat`, ni listage de
contenu) : `OMLDCT03/out/*`, `OMLDCT03/work/*`, `FIMRCC02/out/*`,
`TBRT02/out/TBRT02_C4_ANALYSIS.json`, `TBRT02/out/TBRT02_C5_CLOSURE.json`,
`TBRT02/out/TBRT02_C4BIS_CHECKER_ADJUDICATION.json`,
`TBRT02/out/TBRT02_C4_CHECKER_RETURN_VERBATIM.md`,
`TBRT02/out/TBRT02_C3_RAW_CLOSE.json`, `TBRT02/work/*`, `RPP97/*`, `RPP98/*`,
`CLOSE01/*`, `GATE01/*`, `REVIEW01/*`, `/home/claude/deliverables/*`, et tout
fichier dont le nom contient `RESULT`, `ANALYSIS`, `CLOSURE`, `CHECKER`, `POWER`,
`ADJUDICATION`, `BILAN`, `WITHDRAWAL`, `STATEMENT` ou `DOSSIER`.

**Note de discipline.** `omldct02_analysis.py` et `fdot01_analyse.py` existent dans
les répertoires de code consultés. Ils n'ont **pas** été ouverts, en application de
la règle de nommage, bien que leur répertoire fût par ailleurs autorisé.

**Le test de capacité (§11) n'utilise que des données synthétiques fabriquées par
le programme lui-même.** Le mode `--run` n'a jamais été exécuté par le rédacteur.

---

## 11. Test de capacité — obligation gelée

Le programme `ccra01_frozen.py` contient une recherche adverse sur données
synthétiques, exécutable par `--capability`, sans lire aucune donnée réelle. Une
condition dont on n'a jamais montré qu'elle peut se déclencher n'est pas un test.
Cinq contrôles, tous devant passer :

- **C1 — la statistique PEUT franchir son seuil.** Sous une règle de génération
  connue pour le permettre (SELECTIVE dégradé de façon systématique), le
  programme doit rendre `CONFIRMATOIRE`.
- **C2 — la statistique NE franchit PAS son seuil sur données nulles par
  permutation d'étiquettes de bras.** Un réplicat nul graine doit rendre
  non-confirmatoire, et sur 2000 réplicats permutés le taux empirique de
  franchissement doit rester au voisinage de alpha, borne d'acceptation 0,04.
- **C3 — recherche adverse n°1 : l'inflation de durée due à `MERGE` ne suffit
  pas.** À partir de données échangeables, on retire le canal `MERGE` du seul bras
  SELECTIVE en le convertissant en une terminaison de rang 1 **plus tardive** —
  exactement l'artefact de §2.4 dans sa forme qui invalide un contraste de durées.
  Le programme ne doit **pas** rendre `CONFIRMATOIRE` dans la direction
  pré-déclarée. Un diagnostic accompagne ce contrôle : la variante où le canal
  ultérieur peut être de rang 0 est **rapportée sans être asservie à une
  assertion**, puisque §3.4 et §6 établissent qu'elle relève de l'effet total et
  non d'un biais.
- **C4 — exactitude arithmétique.** La queue binomiale exacte est recoupée contre
  une énumération exhaustive des `2^m` séquences de signes pour de petits `m`.
  C'est un contrôle différentiel : deux chemins indépendants vers la même valeur.
- **C5 — recherche adverse n°2 : invariance au renommage dépendant du bras.** À
  partir de données échangeables, on remplace dans le **seul** bras SELECTIVE
  chaque `OUT_OF_RANGE` par `NO_COMPONENT_AT_THE_NEXT_STEP` — exactement l'artefact
  de §2.3. La décision, le `p` exact, `m` et `k` doivent être **identiques bit à
  bit** avant et après. Le contrôle rapporte en regard le déplacement qu'aurait
  subi une statistique naïve fondée sur les chaînes, afin que l'ampleur de
  l'artefact évité soit mesurée et non supposée.

Si l'un des cinq échoue, la spécification n'est pas exécutable et le run réel ne
doit pas avoir lieu.

---

## 12. Gel

Rien de ce document ne se négocie après la première exécution de `--run`. Toute
modification ultérieure du mapping, de l'ordre du composite, de la statistique,
d'alpha, de la règle de rétention ou de la direction constitue une invalidité
technique de CCRA01 et doit être déclarée comme telle.

`REPRODUCTION_STATUS = NOT_TESTED` · `HEREDITY_STATUS = NOT_TESTED` ·
`H3_STATUS = NOT_TESTED` · `AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED` ·
`ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED`
