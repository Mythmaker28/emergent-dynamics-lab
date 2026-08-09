# `P09` — passe de stabilisation, sans nouvelle exécution

**2026-08-09** · programme `P09_DOSE_YOKED_GUARD_SIGN_CLOSURE` ·
parent `b6bc514126ffd559407065eb89c07b4e950958ce`

`P09_STABILIZATION = CORRECTED_NO_NEW_RUNS`

Aucun moteur n'a été appelé, aucune trajectoire n'a été créée, aucun artefact scellé n'a été
modifié. Cette passe relit `p09_rows.csv` et `p09_summary.json` et corrige **quatre** points de
méthode. Le verdict scellé — `FLOOR_SPECIFIC_MECHANISM_NOT_IDENTIFIABLE` — est **inchangé**.

Sortie machine : `p09_stabilization.json` · code `p09_stabilize.py`.

---

## 1. Les bras sont appariés par bloc fondateur. Le test de survie ne l'était pas.

**Constat.** Dans chacune des quatre cellules, les six bras utilisent **exactement les mêmes neuf
blocs** (graines 890000–890008), et chaque bloc a un `M256` unique partagé par les six bras : le
moteur est déterministe et la première opportunité d'action est à `t = 272`, donc deux bras d'un
même bloc partagent un monde **identique** jusqu'à `t = 272`. L'appariement est exact, pas
approximatif.

**Défaut.** `p09_analyse.py` teste `SURVIVAL_ITT` avec un **Fisher exact à échantillons
indépendants** sur les effectifs marginaux. C'est le mauvais test pour un plan apparié : il ignore
l'appariement et surestime la précision. Les tests sur `UCR` et sur la masse délivrée étaient déjà
des tests des signes appariés et ne sont pas concernés.

**Correction.** Test exact de **McNemar** (binomial exact bilatéral sur les blocs discordants).

| cellule | contraste | survie | Δ blocs | discordants | **p apparié** | *p non apparié (périmé)* |
|---|---|---|---|---|---|---|
| `LAW_16` L24 | allocation | 9/9 → 0/9 | −9 | 9 | **0,0039** | *0,0000* |
| `LAW_16` L24 | réplication `P08` | 9/9 → 0/9 | −9 | 9 | **0,0039** | *0,0000* |
| `LAW_16` L32 | allocation | 9/9 → 0/9 | −9 | 9 | **0,0039** | *0,0000* |
| `LAW_16` L32 | réplication `P08` | 9/9 → 0/9 | −9 | 9 | **0,0039** | *0,0000* |
| `LAW_29` L24 | réduction de dose | 1/9 → 9/9 | +8 | 8 | **0,0078** | *0,0004* |
| `LAW_29` L24 | réplication `P08` | 1/9 → 9/9 | +8 | 8 | **0,0078** | *0,0004* |
| `LAW_29` L32 | réduction de dose | 1/9 → 9/9 | +8 | 8 | **0,0078** | *0,0004* |
| `LAW_29` L32 | réplication `P08` | 1/9 → 9/9 | +8 | 8 | **0,0078** | *0,0004* |
| `LAW_29` L24 | allocation | 6/9 → 9/9 | +3 | 3 | **0,25** | *0,21* |
| `LAW_29` L24 | profil temporel | 9/9 → 6/9 | −3 | 3 | **0,25** | *0,21* |
| toutes | les 5 autres | égalité | 0 | 0 | 1,00 | 1,00 |

**Conséquence quantitative à retenir.** Avec neuf blocs appariés, le test exact ne peut
**jamais** descendre au-dessous de `2 / 2⁹ = 0,0039`. Toute valeur inférieure publiée dans
`REPORT_P09.md` (les `p = 0,0004`) n'était pas atteignable par ce plan et doit être lue comme
`p = 0,0078`. Aucun contraste ne change de côté d'un seuil : les quatre effets massifs restent
au-dessous de 0,01, les deux effets à trois blocs restent non concluants.

---

## 2. La porte de dose scellée n'est pas un test d'équivalence

**Constat.** La règle scellée était : *médiane du rapport apparié dans `[0,847 ; 1,180]` **et** son
IC bootstrap à 95 % dans `[0,781 ; 1,280]`*. C'est une **porte de comparabilité** — un critère de
confinement d'estimateurs. Elle ne teste pas l'hypothèse d'équivalence et ne produit aucune
valeur *p* d'équivalence. La nommer « équivalence de dose » était une surqualification.

**Correction.** Deux objets distincts, nommés distinctement :

| cellule | porte scellée (confinement) | médiane | **TOST post hoc** (log-rapport, IC 90 %) | conclusion TOST |
|---|---|---|---|---|
| `LAW_16` L24 | **PASSE** | 1,001 | rapport géom. 0,937 · [0,875 ; **1,002**] | équivalence établie *de justesse* |
| `LAW_16` L32 | **PASSE** | 0,906 | rapport géom. 0,939 · [0,883 ; **0,998**] | équivalence établie *de justesse* |
| `LAW_29` L24 | **ÉCHOUE** | 0,796 | rapport géom. 0,777 · [0,725 ; 0,833] | non-équivalence : IC entièrement sous 0,847 |
| `LAW_29` L32 | **ÉCHOUE** | 0,767 | rapport géom. 0,766 · [0,728 ; 0,807] | non-équivalence : IC entièrement sous 0,847 |

Le TOST est **post hoc** : il n'a pas été scellé avant exécution et **ne peut pas** relever le
verdict scellé. Il est rapporté parce qu'il concorde avec la porte dans les quatre cellules, ce
qui est une information utile sur la robustesse — et parce qu'il montre que sous `LAW_16`
l'équivalence tient à 0,002 et 0,004 près de la borne haute, donc qu'elle est **marginale**, ce
que le seul énoncé « PASSE » masquait.

---

## 3. Masse réalisée côté source et côté puits, séparément

| cellule | bras | source réalisée / `M₂₅₆` | puits réalisé / `M₂₅₆` | écart | survie ITT |
|---|---|---|---|---|---|
| `LAW_16` L24 | `PARENT_FULL` | 0,6104 | 0,6104 | **0,0000** | 9/9 |
| | `FLOOR_FULL` | 0,3025 | 0,3025 | **0,0000** | 0/9 |
| | `PARENT_Q_REPLAY` | 0,2949 | 0,2949 | **0,0000** | 9/9 |
| | `FLOOR_Q_REPLAY` | 0,2737 | 0,2737 | **0,0000** | 0/9 |
| | `PARENT_LOW_CONSTANT` | 0,2918 | 0,2918 | **0,0000** | 9/9 |
| `LAW_16` L32 | `PARENT_FULL` | 0,4391 | 0,4391 | 0,0000 | 9/9 |
| | `FLOOR_FULL` | 0,3047 | 0,3047 | 0,0000 | 0/9 |
| | `PARENT_Q_REPLAY` | 0,2982 | 0,2982 | 0,0000 | 9/9 |
| | `FLOOR_Q_REPLAY` | 0,2793 | 0,2793 | 0,0000 | 0/9 |
| | `PARENT_LOW_CONSTANT` | 0,3083 | 0,3083 | 0,0000 | 9/9 |
| `LAW_29` L24 | `PARENT_FULL` | 0,4653 | 0,4653 | 0,0000 | 1/9 |
| | `FLOOR_FULL` | 0,2311 | 0,2311 | 0,0000 | 9/9 |
| | `PARENT_Q_REPLAY` | 0,3061 | 0,3061 | 0,0000 | 6/9 |
| | `FLOOR_Q_REPLAY` | 0,2309 | 0,2309 | 0,0000 | 9/9 |
| | `PARENT_LOW_CONSTANT` | 0,2081 | 0,2081 | 0,0000 | 9/9 |
| `LAW_29` L32 | `PARENT_FULL` | 0,5214 | 0,5214 | 0,0000 | 1/9 |
| | `FLOOR_FULL` | 0,2520 | 0,2520 | 0,0000 | 9/9 |
| | `PARENT_Q_REPLAY` | 0,3083 | 0,3083 | 0,0000 | 9/9 |
| | `FLOOR_Q_REPLAY` | 0,2436 | 0,2436 | 0,0000 | 9/9 |
| | `PARENT_LOW_CONSTANT` | 0,2381 | 0,2381 | 0,0000 | 9/9 |

Le `SHAM` est exactement 0,0000 partout (aucun opérateur).

**Ce que la séparation établit.** L'écart source − puits est **exactement nul dans les vingt
cellules-bras**, à la précision de la sortie. L'opérateur couplé est donc conservatif
**événement par événement**, et non seulement en moyenne : la quantité déclarée « délivrée »
n'est ni un double comptage ni une somme de deux grandeurs différentes. C'est une propriété qui
n'avait jamais été publiée séparément, et elle est plus forte que ce que la demande supposait.

---

## 4. Les quatre formulations mandatées remplacent les énoncés causaux exclusifs

| # | formulation retenue | statut | appui |
|---|---|---|---|
| A | **Une dose basse sans aucune garde suffit à reproduire le sauvetage de `LAW_29`.** | ÉTABLI | `PARENT_LOW_CONSTANT` (allocation parent, `floor = 0`) : 1/9 → 9/9 aux deux tailles, McNemar exact **p = 0,0078** |
| B | **La médiation exclusive par la dose n'est pas établie.** | ÉTABLI comme non-établi | Sous `LAW_29` la porte de dose échoue (0,796 et 0,767) : le contraste d'allocation n'est pas à dose égale, donc aucune décomposition dose / allocation n'est identifiée dans un sens ni dans l'autre |
| C | **Sous `LAW_29`, l'allocation spécifique au plancher reste non identifiable.** | ÉTABLI comme non-identifiable | Disposition scellée avant exécution pour le cas « porte de dose en échec » ; c'est le verdict `FLOOR_SPECIFIC_MECHANISM_NOT_IDENTIFIABLE` |
| D | **Un effet de calendrier n'est pas établi.** | ÉTABLI comme non-établi | À dose totale et nombre d'événements égaux, `PARENT_Q_REPLAY` − `PARENT_LOW_CONSTANT` : 0 bloc discordant dans trois cellules, 3 blocs discordants **en défaveur** du replay dans la quatrième (`LAW_29` L24, p = 0,25) |

**Énoncés retirés.** Toute formulation de la forme « le sauvetage **vient de** la réduction de
dose », « le sauvetage s'obtient **uniquement** par la dose », ou « le plancher **ne fait que**
throttler » est retirée. Ce sont des énoncés de médiation exclusive ; le plan `P09` peut établir
la **suffisance** d'une dose basse non gardée, il ne peut pas établir la **nécessité**, parce que
sous `LAW_29` les deux bras d'allocation ne sont pas à dose comparable.

**Titre du manuscrit.** L'ancien sous-titre — *« a guard that harms by allocation but rescues only
by dose »* — contient l'adverbe exclusif *only*. Il devient :

> *A conjugate saturation limit on forced material exchange, and a guard whose harm is an
> allocation effect while its rescue is reproduced by low dose alone*

**Registre des revendications.** La ligne 7 de `REPORT_P09.md` — « sous `LAW_29` le sauvetage vient
de la réduction de dose · ÉTABLI » — devient : « sous `LAW_29`, une dose basse sans garde **suffit
à reproduire** le sauvetage · ÉTABLI (suffisance seulement) ». La ligne 8 est inchangée
(`NON IDENTIFIABLE`), avec `p = 0,25` apparié au lieu de `p = 0,21`.

---

## 5. Ce que cette passe ne fait pas

Elle ne rouvre aucune question, n'ajoute aucun bras, ne prolonge aucun horizon et ne change pas le
verdict. `ROUTE_E_STATUS` reste `CLOSED`. Les quatre corrections sont de méthode statistique et de
formulation ; les données sont celles de l'exécution scellée du 9 août 2026.
