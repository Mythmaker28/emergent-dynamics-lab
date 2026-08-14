# CSC01 — plan d'autopsie brute (§5), déclaré avant toute lecture des mesures

Ce document fixe les définitions, les nuls et la règle de décision de l'étape A **avant** que la
moindre statistique spatiale n'ait été regardée. Il n'est pas modifié ensuite ; toute correction
est ajoutée en append-only.

---

## 0. Statut de la donnée : ce qui est réellement disponible

ORR01 a enregistré, par bras :

* la série scalaire complète, 29 champs × 10 250 pas ;
* les champs finaux entiers des six espèces (36 × 36) ;
* **seulement les 3 derniers** des 102 relevés de composantes (`component_samples = comp[-3:]`).

L'histoire spatiale est donc absente du brut sauvegardé, alors que **l'état qui l'a produite est
entièrement déterminé** par la graine sauvegardée, le moteur gelé et le protocole gelé.

### Rejeu comme décompression déterministe

Un rejeu re-dérive cette histoire. Il n'ouvre aucun démarrage nouveau dans le budget ORR01,
n'emploie aucune graine nouvelle, ne tire aucun nombre aléatoire qu'ORR01 n'ait déjà tiré, et ne
peut modifier aucun résultat. Il est admis dans l'analyse **uniquement** après preuve mécanique,
bras par bras :

1. la série rejouée 10 250 × 29 est **exactement** égale à la série enregistrée
   (`np.array_equal`, float64, sans tolérance) ; et
2. les six champs finaux entiers rejoués sont **exactement** égaux aux champs enregistrés.

Si les deux conditions tiennent, toute observable spatiale calculée ici est une fonction
mesurable du brut enregistré et la question A reste bien *raw-only*. Si l'une échoue pour un
bras, le rejeu de ce bras est **écarté** et le bras est analysé à partir du brut seul.

Les rejeux sont comptés dans une classe dédiée `raw_replay`, déclarée **non scientifique** ;
`SCIENTIFIC_RUNS_USED` ne compte que `calibration`, `confirmation`, `control`.

---

## 1. Géométrie torique — définitions employées

`L = 36`, 4-connexité, conditions périodiques dans les deux directions.

| observable | définition retenue |
|---|---|
| distance | `d(a,b)² = Σ_axe min(|Δ|, L−|Δ|)²` |
| centre | **centre de Fréchet discret** : le site `c` de la grille qui minimise `Σ_i w_i d(i,c)²`, évalué exhaustivement sur les 1 296 sites. Défini même si la masse enroule ou est multimodale. |
| `Rg` (primaire) | forme **par paires**, sans centre : `Rg² = (1/2M²)·Σ_ij w_i w_j d(i,j)²`. Correcte sur le tore en toutes circonstances. |
| `Rg_centre` | forme centrée sur le centre de Fréchet, reportée pour comparaison avec la forme ORR01 (qui utilisait la moyenne angulaire, exacte seulement si la composante n'enroule pas). |
| `r50 / r80 / r90` | quantiles pondérés de `d(i, centre de Fréchet)` sur la masse `X`. |
| diamètre géodésique | plus long des plus courts chemins **à l'intérieur** de la composante (BFS, adjacence périodique). Distingue un amas compact d'un filament. |
| enroulement / percolation | relèvement dans le revêtement universel : BFS attribuant des coordonnées entières non repliées ; si un site est atteint deux fois avec des relevés différents, la différence est `L × (vecteur d'enroulement)`. Enroulement non nul dans un axe ⇒ percolation dans cet axe. |
| `N_eff` composantes | `(Σ mᵢ)² / Σ mᵢ²` (Simpson inverse) : vaut 1 pour un amas, k pour k amas égaux. |
| fraction de masse principale | `m_max / Σ m` |
| distance organisateur–cœur | `d(cellule Y, centre de Fréchet)` |
| contact avec l'image périodique | `gap = L − extent`, plus le test d'enroulement ci-dessus, qui le remplace comme critère dur |

**Cœur.** Le *cœur spatial* à l'instant `t` est la boule torique `B(c(t), R)` centrée sur le
centre de Fréchet, de rayon `R = r50(t)`, et sa masse est la masse `X` qu'elle contient.
Le cœur **existe** à `t` si `B(c(t), 2·ℓ_X)` contient au moins 50 % de la masse `X`,
avec `ℓ_X = sqrt(D_X/µ_X) = 2.5` exactement au point gelé.

**Halo vs fragmentation.** Une composante autre que la principale est comptée comme
*halo* si (a) son centre est à moins de `4·ℓ_X` du centre du cœur **et** (b) sa durée de vie est
inférieure à `1/µ_X = 250` pas ; comme *fragment* sinon. La distinction est mesurée, pas
supposée : les composantes sont appariées d'une trame à la suivante par recouvrement de
cellules, ce qui donne durées de vie, fusions et scissions.

---

## 2. Les trois persistances, séparées

| étiquette | définition opérationnelle sur la fenêtre de maintien |
|---|---|
| `POPULATION_PERSISTENCE` | `N_X(t) > 0` pour tout `t` de la fenêtre, et `N_X` reste au niveau quasi-stationnaire |
| `SPATIAL_CORE_PERSISTENCE` | un cœur existe (au sens ci-dessus) à une fraction `≥ 0.95` des trames de la fenêtre, **et** la chaîne d'identité de la composante principale, par recouvrement de cellules, couvre la même fraction |
| `MATERIAL_TURNOVER` | `renouvellements = (Σ décès X sur la fenêtre) / (moyenne de N_X sur la fenêtre)` ; le renouvellement est déclaré effectif si `renouvellements ≥ 10` |

Ces trois quantités sont rapportées séparément et ne sont **jamais** additionnées en une seule
affirmation.

---

## 3. Les cinq nuls spatiaux

| nul | construction | ce qu'il teste |
|---|---|---|
| N1 `CSR` | les mêmes `N_X` molécules placées uniformément au hasard sur les 1 296 cellules, capacité respectée ; `N_Y` de même | distribution de `Rg`, `r80`, `N_eff`, fraction principale pour une population **délocalisée** de même taille |
| N2 `diffusion pure` | les molécules `X` observées relâchées depuis le centre observé et diffusées pendant la durée écoulée avec le `D_X` du moteur, sans naissance ni mort | étalement attendu en l'absence de tout maintien |
| N3 `source ponctuelle` | profil stationnaire naissance–diffusion–mort avec source ponctuelle à l'organisateur : `n(r) ∝ G_µ(r)`, longueur `ℓ_X` | **le nul décisif** : une population est localisée *trivialement* si sa source est ponctuelle. Un mécanisme de cohésion doit faire mieux que N3, pas mieux que N1 |
| N4 `permutation d'étiquettes` | permutation aléatoire des cellules du champ d'occupation, multiset des comptes par cellule conservé | sépare la *structure* spatiale de la simple distribution des comptes |
| N5 `trames décorrélées` | appariement de trames prises à des temps différents, distribution marginale des positions du cœur conservée, continuité temporelle détruite | teste si la persistance du cœur est une vraie continuité ou seulement la lenteur de l'organisateur |

Chaque nul est tiré 200 fois par bras et par instant testé ; les seuils sont des quantiles du nul,
fixés ici : **q01** pour un test de compacité (l'observation doit être plus compacte que 99 % du
nul), **q99** pour un test d'étalement.

---

## 4. Recalcul indépendant du gate, champ par champ

Les 102 relevés de composantes sont régénérés par le rejeu à la cadence d'ORR01
(`SAMPLE_EVERY = 100`), puis le gate post-hoc gelé est recalculé et comparé **champ par champ**
au `gate_posthoc` enregistré dans `_results.json` / `_results2.json`. Toute divergence est un
échec de rejeu et déclenche l'écartement du bras.

C'est un test plus fort que la seule égalité des séries : il vérifie que le rejeu reproduit aussi
les observables **spatiales** dont ORR01 n'a gardé que trois exemplaires.

---

## 5. Règle de décision de la question A, déclarée d'avance

Quatre axes, évalués sur la fenêtre de maintien de chaque bras `REPAIRED` :

* **A1 COMPACITÉ** — `r80 ≤ q01(r80 | N1)` **et** `r80 ≤ L/6 = 6`, à une fraction ≥ 0.95 des trames.
* **A2 PERSISTANCE DU CŒUR** — `SPATIAL_CORE_PERSISTENCE` au sens du §2.
* **A3 RENOUVELLEMENT** — `MATERIAL_TURNOVER` au sens du §2.
* **A4 NON CONFINÉ PAR LE BORD** — aucun enroulement, aucune percolation, à toutes les trames.

Verdict, dans cet ordre strict, la première ligne qui s'applique l'emporte :

1. rejeu non exact pour ≥ 2 bras, ou observable indéfinie → `ORR01_RAW_LOCALIZATION_UNRESOLVED`
2. A1 échoue dans ≥ 4 bras sur 6 → `ORR01_DELOCALIZATION_CONFIRMED`
3. A1 ∧ A2 ∧ A4 tiennent dans ≥ 5 bras sur 6 **et** le critère spatial du gate ORR01
   (`main_component_carries_the_mass`) est vrai dans ces bras → `ORR01_RAW_LOCALIZATION_CONFIRMED`
4. A1 ∧ A2 tiennent dans ≥ 4 bras sur 6, le critère du gate ORR01 est faux dans ces bras,
   **et** un état synthétique construit à la main — cœur compact vivant plus halo fin — fait
   échouer ce même critère : le défaut est alors dans la définition du gate
   → `ORR01_LOCALIZATION_GATE_INVALID`
5. A1 ∧ A2 tiennent dans ≥ 4 bras sur 6 mais une fraction non négligeable de la masse est hors du
   cœur sans que le gate soit démontré défectueux → `ORR01_PARTIAL_LOCALIZED_CORE`
6. sinon → `ORR01_RAW_LOCALIZATION_UNRESOLVED`

**Un seul** verdict est délivré. La condition 4 exige une démonstration constructive : il ne
suffit pas que le gate soit en désaccord avec la mesure, il faut exhiber l'état sur lequel sa
définition se trompe.

---

## 6. Ce que cette étape ne peut pas établir

Aucune mesure de cette étape ne teste : la reproduction, l'hérédité, l'individualité, la
propriété matérielle, ni H3. `H3_STATUS = NOT_TESTED` et `REPRODUCTION_STATUS = NOT_TESTED`
restent vrais inconditionnellement. Avant qualification, la population est nommée
`X_POPULATION`, `X_CLOUD`, `MAIN_COMPONENT` ou `SPATIAL_CORE` — jamais `BODY`.
