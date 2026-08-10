# `WSFSCRP00` — spécification du point de mesure à support figé

## Le lecteur, utilisé **une seule fois**, avant intervention

Détecteur hérité appliqué à `t0` de chaque fondateur frais : composantes connexes de
`{ρ > 0,30}` (strict), au moins 12 sites, réseau **périodique 4-connexe**. Un fondateur est
admissible **si et seulement si** la règle donne **exactement deux** composantes éligibles ;
zéro, une ou plus de deux → rejet via la file de candidats précommise, jamais une sélection de la
paire la plus commode après coup. Paire **non ordonnée**, canonicalisée par les listes triées
d'identifiants de sites immuables.

Les deux masques booléens disjoints `M_A0[b]`, `M_B0[b]` sont sérialisés et hachés **avant**
qu'un bras n'avance, puis figés byte-identiquement pour tous les temps, les deux jumeaux, toutes
les instances, les deux implémentations de lecteur et la construction des entrées comme des
sorties. **Aucun champ postérieur à `t0` ne change l'appartenance.**

## Le point de mesure

```
B_b       = Σ_i (M_A0 + M_B0)_i · ρ_b[i, t0]  > 0        (figé avant traitement)
q_A[Z,h]  = Σ_i M_A0_i · ρ[Z,h,i] / B_b
q_B[Z,h]  = Σ_i M_B0_i · ρ[Z,h,i] / B_b
δ_A[b,u,h] = q_A[INT] − q_A[SHAM] ;  δ_B[b,u,h] = q_B[INT] − q_B[SHAM]
r[b,u,h]   = (δ_A, δ_B)
```

Chaque valeur IEEE finie est accumulée comme **rationnel dyadique exact** (`Fraction`) ; aucune
réduction flottante dépendante de l'ordre n'est appelée exacte. Grille physique héritée
`h = 4,0 … 40,0` (pas natifs 40 … 400), horizon terminal **400** vérifié contre le gel parent.
Poids trapézoïdaux en temps physique, normalisés à 1, calculés en rationnels exacts.

Perte primaire, en arithmétique rationnelle exacte :

```
L[g,b,u] = Σ_h w_h ( |δ̂_A − δ_A| + |δ̂_B − δ_B| )
```

## Plafond d'interprétation

`r` s'appelle exactement : **réponse intégrée de `ρ` sur le support figé à `t0`**. C'est une
observable **eulérienne de région de base**, pas un traceur lagrangien de matière. Une réponse
peut mêler transport, source, puits et renouvellement à l'intérieur ou à travers la région figée ;
ce point de mesure **ne les sépare pas**.

Jamais appelé : réponse de composante évoluante · identité ou individualité de composante ·
suivi de parcelle, de lignée ou d'appartenance · transfert ou flux composante–bain ·
transplantation de `z` · fonction organismale, vie, reproduction, hérédité.
