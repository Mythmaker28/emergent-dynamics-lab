# NONMERGING_CONFIRM_RSTAR_SENSITIVITY_02 — R*=0.2575 geometric sensitivity (DEV only, POST HOC)

*Extension demandée : tester le probe uniforme amp=0.2575×5 (R*=0.2575) comme **test de sensibilité
géométrique** contre le probe scellé 0.25×5. **Géométrie uniquement** (fusion, collision, couverture maximale,
survie, composantes uniques) ; **la taille de l'effet causal n'est jamais consultée**. Ce document ne modifie
**rien** de scellé : la prospective CONFIRM-02 (probe 0.25×5) est déjà gelée (PRESEAL `9b7580bc`) et exécutée une
fois (RESULTS `830c2d0`). Il sert de **preuve de robustesse** et **fige le choix** pour toute réplication future.
`dev_rstar_sensitivity.py`.*

## 1. Comparaison géométrique (8 mondes DEV, tracker bijectif)

| probe | injection cumulée | sans fusion | sans événement tracker | couverture pire @H40 | @H120 | 3 distinctes @H40 | G0-valide @H40 |
|---|---|---|---|---|---|---|---|
| **0.25×5 (scellé)** | 1.2500 | 8/8 | 8/8 | **3.32 %** | 3.69 % | 8/8 | **8/8** |
| 0.2575×5 (R*) | 1.2875 | 8/8 | 8/8 | **3.34 %** | 3.71 % | 8/8 | **8/8** |

**Les deux passent** G0 sur tous les mondes DEV. Différence de couverture pire-monde à H40 = **+0.02 point de
pourcentage** — dans le bruit ; les deux ont une marge quasi identique (~11.7 points sous le cap 15 %). **Aucun ne
« bat » l'autre géométriquement.**

## 2. R*=0.2575 a-t-il une dérivation théorique indépendante ? (les 6 critères)

La question n'est pas « ce nombre apparaît-il près d'un résultat ? » (0.2575 tombe simplement à l'intérieur d'un
large intervalle géométriquement valide, ~[0.05, 0.35]) mais s'il résiste aux 6 critères anti-numérologie :

1. **Sans dimension ?** Nominalement oui (amp/N0 = 0.2575 ; cumul 1.2875·N0). **Mais non-discriminant** : 0.25,
   0.24, 0.26 sont tout aussi sans dimension. Être exprimable en ratio ne confère aucune signification.
2. **Invariant sous changement d'unité/échelle ?** Le ratio amp/N0 est invariant par rescaling de N — encore une
   fois pour **toute** amplitude, pas spécifiquement 0.2575. Or la valeur *admissible* du probe dépend de seuils
   **spécifiques au système** (grille 64², ρ_max, constantes de diffusion, cap de fusion 15 %) : rien de scale-free
   ne privilégie 0.2575. **Échoue à distinguer.**
3. **Correspondance R*↔observable définie AVANT les résultats ?** **NON — échec décisif.** Le probe a été choisi
   par géométrie et gelé à **0.25** dans le PRESEAL, **avant** tout seed 53xxx. Aucune préinscription ne dit « le
   probe doit valoir R* » ni qu'un observable doit égaler 0.2575. La correspondance « R* = amplitude du probe »
   est proposée **a posteriori**.
4. **Mécanisme imposant la valeur ?** **NON.** Aucune équation, loi de conservation, point fixe ou bifurcation de
   la PDE ne force l'amplitude à 0.2575 ; c'est un **paramètre d'entrée libre** borné par la géométrie. 1.2875
   n'est pas non plus un seuil mécaniquement imposé.
5. **Bat-il valeurs témoins et rapports voisins ?** **NON.** 0.2575×5 et 0.25×5 sont géométriquement
   indiscernables (3.34 % vs 3.32 %, Δ 0.02 pp) ; 0.2575 ne bat ni 0.25, ni 0.24, ni 0.26.
6. **Réapparaît-il dans de nouvelles graines/familles ?** **NON.** Un paramètre d'entrée ne « réapparaît » pas —
   on l'impose. Aucun **observable** (own +0.223, couverture ~3 %, DD 2590, dose R² 0.691) n'est mécaniquement
   égal à 0.2575. Il n'émerge nulle part.

**Bilan : 4 critères sur 6 échouent (3, 4, 5, 6) ; les 2 premiers sont non-discriminants. R*=0.2575 n'a PAS de
dérivation théorique indépendante documentée.**

## 3. Décision (figée)

Les deux probes passent la géométrie ⇒ **règle appliquée : on CONSERVE 0.25×5 par défaut.** L'exception (« sauf
si R* possède une dérivation indépendante documentée avant la prospective ») **n'est pas remplie**. La prospective
CONFIRM-02 reste celle exécutée avec 0.25×5 ; toute réplication future utilisera **0.25×5** — sauf si une
dérivation mécaniste de R* est produite et **préinscrite avant** cette réplication (auquel cas critères 3–4
pourraient changer, mais 5–6 resteraient à démontrer empiriquement).

**Garde-fous respectés :** géométrie seule (effet causal jamais consulté) ; exactement **deux** probes testés
(0.25×5 et 0.2575×5) — **aucune prolifération** de valeurs intermédiaires (0.255, 0.2525, 0.26…) ; rien de scellé
modifié ; aucun seed prospectif nouveau ouvert.

**Lecture positive de robustesse :** une perturbation de +3 % de l'amplitude (0.25 → 0.2575) laisse la géométrie
inchangée (les deux 8/8 G0-valides) — la conclusion de CONFIRM-02 **ne dépend pas** du réglage fin de l'amplitude,
ce qui est rassurant, sans pour autant conférer la moindre signification à 0.2575.

*Post hoc à la prospective scellée. main/V4/release intacts. Rien poussé/mergé/publié.*
