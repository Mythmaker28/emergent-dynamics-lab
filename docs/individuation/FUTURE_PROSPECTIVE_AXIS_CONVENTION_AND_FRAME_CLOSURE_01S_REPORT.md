# FUTURE-PROSPECTIVE-AXIS-CONVENTION-AND-FRAME-CLOSURE-01S — rapport

## Partie I — PROTOCOLE GELÉ

Cette partie est gelée **avant** tout test mécanique nouveau et avant toute conception de Route G ou E.
Elle est committée seule. La Partie II doit citer ce commit et être argumentée contre lui. Toute
correction ultérieure est **additive** : rien ici n'est réécrit.

**Aucun test mécanique nouveau n'a été exécuté et aucune route n'a été conçue, préférée ou classée à ce
commit.**

La Partie I reste un **préfixe byte-exact** du rapport final.

---

### 1. Autorité, lignée, portée

| Rôle | Objet |
|---|---|
| Branche autorisante | `codex/future-prospective-measurement-feasibility-route-selection-01r-human-review` |
| Commit parent | `c2f6b0c4b47b39e26bb7b6a2800ad5760ef55c54` |
| Lignée vérifiée | `a735c64d → f4bf11e4 → f19c9a8c → cc551374 → c2f6b0c4` |
| Cette branche | `codex/future-prospective-axis-convention-and-frame-closure-01s` |
| `refs/heads/main` épinglé au départ | `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77` (`HEAD` = `refs/heads/main`) |

Le parent porte `HUMAN_REVIEW_ACCEPTED`, l'acceptation de `MEASUREMENT_FEASIBILITY_REVISE`, **aucune
route sélectionnée**, et l'autorisation exclusive de `FUTURE_PROSPECTIVE_AXIS_CONVENTION_AND_FRAME_CLOSURE_01S`
avec douze finalités, extraites littéralement de son §13 et reproduites en Partie II §II.0.

**Portée.** 01S ferme le cadre prospectif, rend G et E réellement comparables, et **sélectionne
définitivement** G, E ou F. 01S ne démontre ni convention, ni ownership, ni individualité : elle
sélectionne un protocole expérimental.

### 2. Séparation ingénierie / mécanique / science

Trois registres, disjoints, jamais mélangés dans une même phrase :

- **Fait de source (ingénierie).** Une propriété lisible dans le code autorisé, établie par lecture.
  Exemple : « `LatticeBondSpec` ne contient aucun paramètre par axe. »
- **Fait mécanique.** Une propriété d'exécution du logiciel sur des **fixtures fabriquées**, établie par
  un test. Exemple : « sur les fixtures testées, `max |T(U(x)) − U(Tx)| = 5,6e-17`. » Un fait mécanique
  vaut **pour son domaine testé** et n'est jamais une observation d'un phénomène.
- **Fait scientifique.** Une propriété du substrat établie par une famille prospective préenregistrée.
  **01S n'en produit aucun.**

Toute phrase de la Partie II qui traite un nombre issu d'une fixture comme un résultat physique est un
défaut par construction. Les entités des fixtures ne sont pas des entités scientifiques.

### 3. Domaine revendiqué (gelé)

Le domaine de symétrie maximal revendicable est, et ne dépasse pas :

> **lattice carrée** `L × L` · **frontières périodiques sur les deux axes** · **loi tirée de
> `LatticeBondSpec`**, qui ne contient aucun paramètre privilégiant un axe.

Hors de ce domaine, aucune généralisation n'est faite. En particulier, sur une lattice **rectangulaire**
`H × W` avec `H ≠ W`, la transposition relie deux systèmes de **dimensions différentes** : elle n'est pas
un automorphisme, il n'existe **aucune symétrie interne Z₂**, et Route G n'y est pas définie. Ce point
doit être démontré mécaniquement, pas seulement affirmé.

### 4. Définitions exactes (gelées)

**4.1 Transposition `T`.** `T` agit simultanément sur tous les objets :

| Objet | Image sous `T` |
|---|---|
| lattice `L × L` | lui-même |
| état `x = (m, n, b, step)` | `(mᵀ, nᵀ, [b₁ᵀ, b₀ᵀ], step)` |
| loi `LatticeBondSpec` | **identité** (aucun champ par axe) |
| champ de bonds `b` de forme `(2,L,L)` | `b[0] → b[1]ᵀ`, `b[1] → b[0]ᵀ` |
| masque d'entité `M ⊆ [0,L)²` | `Mᵀ` |
| `FaceIntervention (matter_scale, resource_scale)` de forme `(2,L,L)` | `scale[0] → scale[1]ᵀ`, `scale[1] → scale[0]ᵀ`, pour les deux champs |
| sortie de mesure `(M, Q, S, …)` | `(Mᵀ, −Q, −S, …)` |

À démontrer dans le domaine du §3 : `T² = id` sur chacune de ces classes, et l'équivariance
`U(Tx, TI) = T·U(x, I)` pour l'update `U` et l'intervention `I`, à un pas **et** à plusieurs pas.

**4.2 Masque d'entité `M`.** L'ensemble des cellules d'un composant détecté, pris **comme ensemble** —
jamais comme index. `M` est persisté puis **relu sur disque** avant toute mesure. Les faces internes de
`M` selon l'axe `a` sont
`F_a(M) = { (a, y, x) : (y,x) ∈ M et son voisin positif selon a ∈ M }`,
c'est-à-dire `M ∧ roll(M, −1, axis=a)`. Sous `T`, `F_0(M) ↔ F_1(Mᵀ)` par construction.

**4.3 Observable `Q` (convention axis-signée).**

> `Q(x, M) = mean{ b[0][f] : f ∈ F_0(M) } − mean{ b[1][f] : f ∈ F_1(M) }`

`Q` est **indéfini** et l'entité **inéligible** si `F_0(M)` ou `F_1(M)` est vide. `Q` se calcule
exclusivement à partir de l'évidence persistée et relue : le champ `b` et le masque `M`. Les
identifiants de composant et de track n'entrent **jamais** dans `Q`.

Propriétés à démontrer mécaniquement : `Q(Tx, TM) = −Q(x, M)` (imparité exacte) et `Q = 0` pour tout
état invariant sous `T` restreint à un masque invariant sous `T`.

Le fait que `Q` compare les deux axes du lattice ne le disqualifie pas. Le lattice peut offrir deux
conventions équivalentes, comme un ferromagnétique offre `+` et `−`. Ce qui doit être exclu est un signe
**imposé** — voir §7.

**4.4 Observable de forme `S`, définie indépendamment de `Q`.** À partir du **masque seul**, sans aucun
champ de bonds :

> `S(M) = (I_yy − I_xx) / (I_yy + I_xx)`

où `I` est le tenseur des moments seconds de `M` autour de son centroïde, calculé avec la métrique
périodique du tore. `S` est indéfini si `I_yy + I_xx = 0`. Sous `T`, `S(Mᵀ) = −S(M)` : `S` est **aussi
`T`-impair**. C'est voulu : `S` est le concurrent géométrique naturel de `Q`, et un discriminateur qui
ne les opposerait pas serait vide.

**4.5 Jointure track–component.** La correspondance `(frame, cellules du composant) → track_id` est
définie **par géométrie**, jamais par index : deux composants de frames voisines appartiennent au même
track selon la sortie du tracker accepté, et la jointure est représentée par le triplet
`(frame, digest canonique de l'ensemble de cellules, track_id)`. La **représentation quotient**
utilisée pour toute assertion d'équivariance est le **multiensemble** `{ (M, Q(x,M), S(M)) }` sur les
composants d'une frame : elle ne contient aucun identifiant et est donc insensible à toute permutation.

### 5. Grille commune E/G (gelée)

Quatorze propriétés. **Une seule absence fait échouer la route.** Aucune moyenne, aucune pondération,
aucun score. Les reviewers ne choisissent pas la route : ils produisent des findings, et **la matrice
gelée décide**.

| # | Gate | Exigence |
|---|---|---|
| **C1** | Domaine fini / distribution propre normalisée | l'espace des lois, des CI, des tailles et des constantes est un ensemble borné de mesure finie strictement positive, muni d'une loi de probabilité **normalisée** et échantillonnable exactement |
| **C2** | Observable correctement définie | définie sur l'évidence persistée et relue, sans identifiant, avec son domaine d'indéfinition explicite |
| **C3** | Acquisition end-to-end suffisante | tout ce que les endpoints exigent est lié par le pont qualifié, ou déclaré `PRE_RUN_BLOCKER` avec sa fermeture nommée |
| **C4** | Falsificateurs prospectifs explicites | chaque explication concurrente a un test qui peut la retenir, figé avant toute donnée |
| **C5** | Estimand | population, unité, condition, outcome, stratégie d'événements intercurrents, mesure de résumé |
| **C6** | Null et alternative | les deux sont exprimables et distinctes |
| **C7** | Règle de décision | numérique, avec partition `POSITIF / NÉGATIF / INDÉTERMINÉ` non dégénérée |
| **C8** | MDE ou précision scientifiquement justifiée | dérivée d'un principe déclaré indépendant des familles fermées, **avant** le calcul de la taille |
| **C9** | Puissance compatible avec le plafond | puissance des **deux** bras, évaluée sous l'attrition propre au design, à l'intérieur du plafond de calcul mesuré |
| **C10** | Denominator sans remplacement | fixé à l'enrôlement, aucune unité jamais remplacée, retirée ou retirée |
| **C11** | Lifecycle des dissolutions, splits, merges, pertes | chacun est un **outcome ou événement concurrent**, jamais une exclusion |
| **C12** | Provenance et ancrage | racine externe, fail-closed, ordre des checks et liaison anti-replay fermés ou déclarés `PRE_RUN_BLOCKER` |
| **C13** | Faisabilité mécanique bornée | plafond de calcul **mesuré mécaniquement**, nombre de mondes borné, règle de terminaison indépendante de l'outcome |
| **C14** | Absence de calibration sur les familles fermées | aucune borne, marge, effet, taille ou seuil issu de Stage B, de `11/64`, de `0/8` ou de `M_MINUS` |

### 6. Construction de la distribution prospective (gelée)

**6.1 Coordonnées.** Une loi est fixée, aux trois échelles `dt`, `m_max`, `n_max` près, par neuf groupes
sans dimension :
`κ̂ = κ_m·dt` · `θ̂_m = θ_m·m_max` · `θ̂_n = θ_n·n_max` · `D̂ = D·dt` · `λ = resource_leak_floor` ·
`ε̂_b = ε_b/n_max` · `k̂_on = k_on·dt` · `k̂_off = k_off·dt` · `k̂_tens = k_tension·dt`.
Bornes dures de source : **(B1)** `κ̂ < ¼·e^{−(θ̂_m+θ̂_n)/2}` ; **(B2)** `4D̂ + 2·ε̂_b·k̂_on < 1` ;
**(B3)** `λ ∈ [0,1]`.

**6.2 Ordre de dérivation obligatoire.** Aucune quantité ne peut être fixée avant celles dont elle
dépend :

> plafond de calcul mesuré → tailles de lattice `𝓛` → horizon `H` → cadence `Δf` → boîte des groupes →
> ensemble admissible `A` → loi uniforme sur `A` → estimand → MDE ou précision → taille d'échantillon →
> puissance (**conséquence**, jamais justification)

**6.3 Boîte, par un unique principe de résolvabilité appliqué uniformément.** Un processus plus lent
qu'une fois par run est inobservable ; plus rapide qu'une fois par intervalle échantillonné, il est non
résolu par le calendrier déclaré. Donc **tous** les groupes de type taux :

> `κ̂, D̂, k̂_on, k̂_off, k̂_tens ∈ [1/H, 1/Δf]`

Les couplages d'affinité ne sont pas des taux ; leur borne vient de (B1) combinée à `κ̂ ≥ 1/H` :

> `S = θ̂_m + θ̂_n < 2·ln(H/4)`, avec `θ̂_m, θ̂_n ≥ 0` — un simplexe compact, non vide dès que `H > 4`

`ε̂_b` n'est pas un taux : c'est l'énergie stockée par bond en unités de ressource. Borne d'admissibilité
mécanique : l'énergie d'un bond ne peut excéder la capacité totale en ressource d'une cellule, faute de
quoi le carburant de formation peut faire passer `n` sous zéro et l'update lève `ArithmeticError`. Donc
`ε̂_b ∈ [0, 1]`. Et `λ ∈ [0,1]` par source.

**6.4 Ensemble admissible et normalisation.** `A = Box ∩ {(B1)} ∩ {(B2)}` où `Box` est le produit des
intervalles ci-dessus. `Box` est borné, donc `|A| ≤ |Box| < ∞` ; la non-vacuité et `|A| > 0` doivent être
établies mécaniquement par un **témoin intérieur** et un voisinage ouvert. La loi prospective est alors
**uniforme sur `A`**, échantillonnée exactement par rejet depuis `Box` — donc **normalisée**, ce qui est
exactement ce que la mission précédente n'avait pas. **Borner un seul produit en laissant une mesure
infinie est interdit.**

**6.5 Le reste de la distribution.** La taille `L` est tirée uniformément sur un ensemble fini `𝓛` de
tailles **carrées** déclaré avant toute inspection ; les frontières sont périodiques et non tirées ;
`H` et `Δf` sont déclarés, non tirés ; les constantes du détecteur et du tracker sont déclarées avec
leur ensemble de sensibilité, non tirées. Le moteur étant **déterministe et sans RNG**, une réplication
n'est **pas** un pseudo-seed : c'est **un nouveau tirage préenregistré de (loi, condition initiale,
taille)**.

**6.6 Conditions initiales et invariance sous `T`.** Toute condition initiale est enrôlée en **paire
exacte `(x, Tx)`**. C'est la garantie la plus forte et la plus simple d'une distribution de CI invariante
sous `T`, et elle fournit gratuitement le réplicat transposé apparié. L'unité d'enrôlement est **la
paire**, comptée une fois.

### 7. Discriminateurs des artefacts de `Q` (gelés)

Route G doit pouvoir être **falsifiée** par chacune de ces explications concurrentes. Chaque
discriminateur est figé ici, avant toute donnée.

| Artefact | Discriminateur prospectif figé |
|---|---|
| **Signe imposé par la géométrie / la forme** | endpoint primaire conditionné sur `S` : l'association du signe de `Q` avec son histoire doit survivre au conditionnement sur `S` **et** à un bras d'**égalisation géométrique** où les entités sont appariées sur `S`. Si `S` seul explique `Q` aussi bien que l'état des bonds, **G est falsifiée** |
| **Orientation initiale / du monde** | CI enrôlées en paires `(x, Tx)` ; le signe ne doit pas être verrouillé à l'orientation mondiale. Un biais global de signe supérieur à la marge préjustifiée est un **FAIL** |
| **Ordre d'indexation** | toute assertion d'équivariance passe par la représentation quotient du §4.5 ; aucun identifiant n'entre dans `Q` |
| **Détecteur** | équivariance du détecteur sous `T` **à permutation près**, démontrée mécaniquement ; sinon la mesure doit être placée en amont de l'asymétrie de seeding par index linéaire. Tant que ni l'un ni l'autre n'est établi, c'est un **blocker** |
| **Tracker** | équivariance à permutation d'identifiants près, démontrée mécaniquement |
| **Environnement** | égalisation environnementale ; champ partagé identique entre entités cohébergées |
| **Intervention** | **aucun traitement signé avant la mesure d'émergence** ; sham et intervention voisine préfigés ; lecture **après washout**, jamais pendant le forçage |
| **Taille particulière** | plusieurs tailles carrées préfixées ; une convention n'existant qu'à une taille choisie après inspection fait **échouer G** |
| **Transitoire** | la convention doit apparaître **avant** la fenêtre de maintien, survivre à une fenêtre sans forçage signé, et survivre à un turnover vérifié. Un `Q` présent seulement juste après le forçage est un **FAIL** |

**Claim maximal futur de G**, jamais dépassé : *convention axis-signée entity-local dans le domaine
carré périodique*. Jamais « orientation indépendante de tout substrat ».

### 8. Ownership et unité statistique (gelés)

Le protocole futur de G doit permettre : deux entités **cohébergées** dans un environnement symétrique ;
des choix de signe **conditionnellement indépendants** ; une **intervention locale** sur A ; un **sham**
et une **intervention voisine** ; l'**absence** de changement correspondant chez B ; l'absence de
modification du champ partagé expliquant seule le résultat ; l'**égalisation environnementale** ; et le
**maintien après turnover vérifié**.

**L'unité statistique est le monde, ou le tirage (loi, CI, taille) — jamais chaque entité comme
réplication indépendante.** Toute analyse au niveau de l'entité est secondaire et doit déclarer sa
structure de dépendance. La pseudo-réplication est un `FAIL` de C5.

### 9. Denominator et événements concurrents (gelés)

- Le denominator est fixé à l'**enrôlement**, avant toute exécution, en paires `(x, Tx)`.
- **Aucun remplacement, aucun retirage, aucun complément.** Une unité qui échoue reste au dénominateur
  avec son outcome observé.
- **Dissolution, split, merge, perte, handoff non résolu et censure au horizon** sont des **outcomes ou
  événements concurrents**, jamais des exclusions. Exactement un état terminal par track, parmi les cinq
  du contrat de cycle de vie accepté.
- Le **rejet global** est réservé aux violations de contrat — schéma, calendrier, digest — qui sont des
  fautes logicielles : une famille où il se déclenche est une **famille échouée**, rapportée comme telle,
  jamais élaguée.
- Toute quantité conditionnée à la survie est secondaire et étiquetée.

### 10. Règles de puissance et de précision (gelées)

- **P1.** Une règle de décision **numérique** est obligatoire, avec une partition
  `POSITIF / NÉGATIF / INDÉTERMINÉ` dont **aucune** des trois régions n'est vide.
- **P2.** La MDE ou la cible de précision est **justifiée avant** le calcul de la taille, par un principe
  déclaré, indépendant des familles fermées. Une MDE qui est la **conséquence** arithmétique de la taille
  n'est pas une justification : c'est la circularité que C8 existe pour attraper.
- **P3.** `α`, la direction et **les deux** taux d'erreur aux frontières sont déclarés.
- **P4.** Une conclusion négative exige un critère d'intervalle ou d'équivalence préjustifié. La
  non-significativité seule ne soutient jamais une conclusion négative. Les deux frontières `Δ₁ < Δ₀`
  sont distinctes et la zone d'indifférence est non dégénérée.
- **P5.** Les caractéristiques opératoires sont évaluées **sous l'attrition propre au design**
  (inéligibilité mécanique, censure), pas dans le vide.
- **P6.** Multiplicité : séquence fixe déclarée ou contrôle du taux d'erreur par famille, à l'avance.
- **P7.** Les calculs sont analytiques ou par simulation **abstraite** sous `/tmp`, ne consommant aucune
  observation historique ni aucune sortie du moteur.
- **P8.** Chaque énoncé de puissance nomme l'hypothèse qui lui nuirait le plus si elle était fausse.

### 11. Priorité de sélection (gelée)

Appliquée **exactement**, après la grille du §5 :

1. Si **G** passe les quatorze gates → `primary_route = "G"`. **E** peut être backup **uniquement** si E
   passe également les quatorze.
2. Sinon, si **E** passe les quatorze → `primary_route = "E"`, et **G est définitivement rejetée pour ce
   programme**.
3. Sinon → `primary_route = "F"`, arrêt consolidé du programme prospectif.

`primary_route` n'est **jamais** `null`. **F ne peut pas être sélectionnée par préférence** si G ou E
passe. Nouveauté, attrait narratif, intérêt déclaré de l'opérateur, coût et difficulté ne sont **pas**
des critères.

### 12. Sorties terminales (gelées)

| Sortie | Condition |
|---|---|
| `AXIS_FRAME_CLOSURE_01S_ROUTE_G_SELECTED` | G passe les quatorze gates |
| `AXIS_FRAME_CLOSURE_01S_ROUTE_E_SELECTED` | G échoue, E passe les quatorze |
| `AXIS_FRAME_CLOSURE_01S_ROUTE_F_SELECTED` | ni G ni E ne passe |
| `STOP_01S_INTEGRITY` | **uniquement** incident d'intégrité procédural |

`REVISE`, `DEFERRED`, `UNRESOLVED`, `NONE`, une route primaire `null` ou une nouvelle mission de cadrage
sur les mêmes inconnues sont **interdits**. Un test négatif, une route qui échoue, un désaccord de
reviewer ou un push impossible **ne sont pas** des incidents d'intégrité : ils alimentent E/G/F.

Le JSON final fait autorité et doit porter `primary_route ∈ {"G","E","F"}`,
`backup_route ∈ {"E","G",null}`, `scientific_run_authorized = false`.

### 13. Rôles des reviewers (gelés)

- **Reviewer A** — symétrie ; `Q` versus forme ; estimands ; distribution prospective ; statistiques ;
  puissance ; pseudo-réplication.
- **Reviewer B** — implémentation ; détecteur/tracker ; intervention ; lifecycle ; provenance ; replay ;
  contournements ; firewall.

Catégories de findings : `PACKAGE_BLOCKER` · `ROUTE_G_GATE_FAIL` · `ROUTE_E_GATE_FAIL` ·
`MINOR_NON_BLOCKING`.

Procédure : deux reviewers **en parallèle**, puis **une seule** correction consolidée, puis **une seule**
re-review ciblée finale. Après celle-ci : un défaut **matériel** restant fait échouer la route ; un
défaut **documentaire non porteur** devient une limitation déclarée ; **aucune troisième boucle
corrective**.

**Le vote majoritaire ne contrôle jamais la disposition.** Les reviewers produisent des findings ; la
matrice du §5 et la priorité du §11 décident. La finalité 12 du human-review — « sélectionner une route
uniquement avec `PASS`/`PASS` » — est satisfaite ainsi : un `ROUTE_*_GATE_FAIL` survivant à la
re-review fait échouer cette route dans la matrice, et la sélection redescend `G → E → F`. Comme F est
toujours atteignable, la règle de sélection obligatoire et la règle `PASS`/`PASS` ne peuvent pas se
bloquer mutuellement.

### 14. Allowlist des modifications (gelée)

Seuls ces chemins peuvent changer :

1. `tests/test_axis_transpose_equivariance_01s.py` *(nouveau — faits mécaniques de 01S)*
2. `docs/individuation/FUTURE_PROSPECTIVE_AXIS_CONVENTION_AND_FRAME_CLOSURE_01S_REPORT.md`
3. `docs/individuation/FUTURE_PROSPECTIVE_AXIS_CONVENTION_AND_FRAME_CLOSURE_01S_DECISION.json`
4. `docs/individuation/FUTURE_PROSPECTIVE_AXIS_CONVENTION_AND_FRAME_CLOSURE_01S_REVIEW_JOURNAL.md`

**Non modifiés** : `engine.py` ; `edlab/specs.py` ; `edlab/state.py` ; le tracker ; le contrat de cycle
de vie ; les runners acceptés ; le pont de mesure et sa suite ; tout `__init__.py` ; tout test existant ;
tout document historique. Les réparations du pont autorisées par le human-review §13 sont **volontairement
non exercées** : elles sont enregistrées comme obligations `PRE_RUN_BLOCKER` (§15), ce qui réduit la
surface de changement de cette mission au strict nécessaire.

Le JSON fait autorité pour les gates, les hashes et la route ; le journal porte les findings et les
adjudications ; le rapport porte le raisonnement. Aucune observation n'est répétée dans les trois.

### 15. `PRE_RUN_BLOCKER` (gelé)

Un `PRE_RUN_BLOCKER` est une obligation d'infrastructure **nommée, bornée et non fermée** ici. Ce n'est
**pas** une raison de relancer l'architecture, et il ne fait **pas** échouer C3 ou C12 s'il est déclaré
avec sa fermeture exacte. **Aucune famille scientifique ne peut commencer avant sa fermeture**, et le
JSON final doit les énumérer.

### 16. Firewall (gelé)

**Interdit absolument** : toute famille scientifique ; toute réutilisation de Stage B ; tout résultat
`M_MINUS` comme confirmation ; tout seed ou namespace prospectif ; tout tuning sur une donnée
historique ; toute émission d'un résultat scientifique ; toute modification de `engine.py`, du cycle de
vie historique, de Stage B ou d'un paquet scientifique accepté.

**Accès** : chemins Git exacts uniquement, via `git cat-file -e <commit>:<path>` et
`git show <commit>:<path>`. Interdits : listing de répertoire, glob, wildcard, `ls-tree -r`, `find`,
`rg --files`, grep large, archive de l'arbre, parcours de `results/`, recherche mémoire globale,
ouverture d'un shard, monde, trajectoire, candidat, checkpoint ou résultat historique. `main` est
seulement épinglé avant et après ; son working tree n'est pas inspecté.

**Tests mécaniques autorisés**, sur fixtures fabriquées et sans seed scientifique : `T² = id` ;
équivariance à un pas et multi-pas ; imparité de `Q` ; état symétrique donnant zéro ; formes appariées ;
détecteur et tracker sous `T` ; intervention transposée ; receipt et ordre des checks ; copie/replay ;
tampering avec re-pinning ; jointure track–component ; cadence non unitaire et disparition ; zéro
détection ; calcul analytique ou simulation abstraite de puissance ; mesure mécanique du coût.

**Aucun nombre retiré des missions précédentes ne peut être réintroduit sans nouvelle dérivation
préalable** : aucun `Δ`, aucune marge, aucun horizon, aucune taille de lattice, aucun `L, R, N, L₂`,
aucune MDE, aucun plafond, aucune taille d'échantillon. Les valeurs de 01R sont mortes.

---

*La Partie II (finalités extraites, faits mécaniques, conception de G, conception de E, cas affirmatif
de F, matrice commune, reviews, correction consolidée, décision) est ajoutée après ce commit. L'état de
ce fichier au commit pré-conception est la référence gelée.*

## Partie II — FINALITÉS, FAITS MÉCANIQUES, CONCEPTION G/E/F, MATRICE, DÉCISION

*La Partie I est gelée et reste un préfixe byte-exact. Rien n'y est réécrit.*

### II.0 Finalités extraites du parent (littéral)

Ouvert par chemin Git exact :
`docs/individuation/FUTURE_PROSPECTIVE_MEASUREMENT_FEASIBILITY_AND_ROUTE_SELECTION_01R_HUMAN_REVIEW.md`
(29 694 octets au commit `c2f6b0c4`). Son §13 autorise exactement 01S et énumère douze finalités :
(1) dérivation d'équivariance à la transposition au niveau source, avec son domaine exact ; (2) gel des
dimensions et de la forme du lattice, des frontières, de l'horizon, du plafond d'exécution, du
calendrier d'échantillonnage et des cartes de transposition état/loi/**intervention** ; (3) distribution
de probabilité **finie et normalisée** sur les neuf groupes sans dimension, indépendamment des résultats
historiques ; (4) résolution de la taille d'échantillon, de la MDE, de la précision et de l'arithmétique
de la famille de reproduction de Route E ; (5) observable d'anisotropie de **forme** figée
prospectivement, à partir de la géométrie matière/masque de l'entité ; (6) observable de bond signée `Q`
définie **indépendamment** de cette mesure de forme ; (7) contre-exemples mécaniques appariés ;
(8) établir si `Q` peut **en principe** être maintenue indépendamment de la forme plutôt que simplement
corrélée à elle ; (9) gel du **timing** d'intervention ; (10) fermeture de l'ordre des checks d'ancrage
et de la liaison anti-replay ; (11) réévaluation **symétrique** de E, G et F ; (12) sélection d'une route.

Interdictions littérales du même §13 : ne pas ouvrir de donnée scientifique historique ; ne pas utiliser
`M_MINUS` ; ne pas exécuter de famille prospective ; ne pas créer de seed scientifique ; ne pas caler de
paramètres sur des sorties mécaniques ; ne pas interpréter des fixtures mécaniques comme des entités
scientifiques. Et : *« si aucune distribution de loi finie ne peut être justifiée, ou aucune convention
signée indépendante de la forme, rejeter définitivement la route concernée plutôt que la différer encore
une fois pour le même motif. »*

Sources et tests autorisés, hashes acceptés : le pont de mesure
`edlab/substrates/lattice_bond/future_prospective_measurement_bridge.py` (53 493 o, sha256
`ecb0a03d16c0fe9429f13d76a5de82687ad23eb24d143ba422300274bc10b15e`) et sa suite (65 805 o,
`eecadb4aebe96aa16f5bf18283bd2d8fb6c5ebde62c6ad5e1fd47ade89cca30c`) ; le moteur, les specs, l'état, le
tracker, le contrat de cycle de vie, les runners acceptés et les cinq suites acceptées, tous
byte-identiques au parent. Modifications autorisées : réparations du pont **et** les documents 01S ; 01S
choisit de ne pas exercer les réparations du pont et de les enregistrer en `PRE_RUN_BLOCKER`
(Partie I §14–§15), ce qui réduit la surface de changement à un seul fichier de test plus les trois
documents.

### II.1 Faits mécaniques établis

Une seule addition : `tests/test_axis_transpose_equivariance_01s.py` (38 924 o, sha256
`999328f69b90f538e5a4323dc245e3279a850b2cdcab645b8d739f22267f36b5`), **21 tests**, tous passants.
Suite complète : **667 passés, 0 échec, 0 skip** (646 acceptés inchangés + 21 nouveaux). Aucun autre
fichier n'a changé : le sha256 de chaque fichier préexistant a été recalculé et comparé.

Tout ce qui suit est un **fait mécanique** au sens de la Partie I §2 : établi sur fixtures fabriquées,
valable pour son domaine testé, jamais l'observation d'un phénomène.

**M1 — Involution et loi.** `T(T(x)) = x` bit-exact sur états, interventions et masques. `LatticeBondSpec`
a exactement douze champs — `dt, m_max, n_max, kappa_m, theta_m, theta_n, resource_diffusivity,
resource_leak_floor, epsilon_b, k_on, k_off, k_tension` — **aucun** ne privilégie un axe : `theta_m` et
`theta_n` indexent les deux *champs* `m` et `n`, pas les deux axes. `T` agit trivialement sur la loi.

**M2 — Équivariance de l'update.** `T(U(x)) = U(T x)` : résidu max **0,0** (backend vectorisé) et
**5,55e-17** (backend de référence) à un pas, sur trois lattices carrées de tailles différentes ;
**1,39e-17** et **1,67e-16** cumulés sur 25 pas. Sous intervention non triviale avec `I ≠ T(I)` :
`T(U(x,I)) = U(Tx, TI)`, résidu **0,0** / **5,55e-17**. Le ledger est équivariant lui aussi :
`matter_natural`, `matter_active`, `matter_missing`, `bond_cue`, `resource_natural`, `r_on`, `r_off`,
`gross_formation`, `gross_rupture`, `formation_fuel` — résidus **exactement 0,0**.

**M3 — Imparité de `Q` et zéro symétrique.** `Q(Tx, TM) = −Q(x, M)` **exactement** (`fsum`, donc
indépendant de l'ordre de sommation ; ce n'est pas une tolérance). `Q = 0,0` exactement pour deux états
invariants sous `T` restreints à un masque invariant.

**M4 — `S` est bien un concurrent géométrique impair.** `S(Mᵀ) = −S(M)` exactement, et `S = 0`
exactement pour un masque invariant (bloc carré, croix).

**M5 — `Q` n'est PAS une fonction du masque.** Deux états avec le **même** masque `M` (`M = Mᵀ`, donc
`S(M) = 0`), le **même** champ `m` et le même masque de seuil, donnent `Q₁ = +0,625` et `Q₂ = −0,625`.
La forme ne détermine pas le signe.

**M6 — `Q` peut être maintenue indépendamment de la forme.** Sur la paire `(x, Tx)` avec masque
invariant sous `T`, sur **30 pas** : le masque détecté des deux branches est **identique** à chaque
échantillon, et `Q` des deux branches est **exactement opposé** à chaque échantillon
(`max |Q_a + Q_b| = 0,0`), avec `min |Q_a| = 0,4008`. Trajectoire d'une branche :
`0,600 → 0,591 → 0,583 → … → 0,401`, décroissance monotone, jamais proche de zéro.

C'est la réponse mécanique à la finalité (8) du parent : **oui, en principe**. Et ce n'est pas une
coïncidence de fixture : c'est une **conséquence de M2**. Si le masque est invariant sous `T`, alors `x`
et `Tx` ont le même masque à tout instant et, par équivariance exacte, `Q(U^k(Tx)) = −Q(U^k(x))` pour
tout `k`. Même forme, signe opposé, maintenu — exactement, indéfiniment, dans le domaine du §3.

**M7 — Détecteur et tracker, à permutation près.** Le multiensemble quotient `{(M, Q, S)}` du §4.5 est
équivariant : appliquer `T` aux cellules et nier `Q` et `S` reproduit exactement le quotient de `Tx`.
L'asymétrie qui rend le quotient **nécessaire** est démontrée, non supposée : sur une fixture à deux
blobs, `detect_components` renvoie l'ordre `{0→1, 1→0}` entre `x` et `Tx`, car le seeding se fait par
index linéaire `y·L + x`. Le tracker est équivariant à bijection d'identifiants près : sur une séquence
de 5 frames, 2 tracks et 10 événements par branche, les multiensembles de suites
`(frame, ensemble de cellules)` coïncident après transposition, et les multiensembles de types
d'événements aussi.

*Limitation déclarée.* Sur une fixture 8×8 « tissée », 2 composants sur 3 ont un ensemble de faces
internes vide sur un axe : `Q` y est **indéfini** et l'entité inéligible, comme le §4.3 le prévoit.
L'omission est elle-même symétrique sous `T` (les faces internes axe-0 de `M` sont les faces internes
axe-1 de `Mᵀ`), donc elle ne peut pas fabriquer l'égalité.

**M8 — Rectangulaire : pas de Z₂ interne.** Sur `5×8`, `T` envoie l'état vers la forme `(8,5)` et le
champ de bonds `(2,5,8)` vers `(2,8,5)`. `T(T(x)) = x` tient encore, mais `T(x)` **n'appartient pas au
même espace** : la soustraction des deux champs lève `ValueError`, et un plan d'intervention construit
pour `(5,8)` est refusé par `step` sur l'état transposé. **Route G n'est pas définie hors du domaine
carré.**

**M9 — Fermeture du cadre : témoin de mesure.** Avec les valeurs **témoins** `H = 1024`, `Δf = 16`
(étiquetées comme témoins mécaniques, pas comme valeurs de design) : la boîte est
`taux ∈ [9,7656e-4, 6,25e-2]`, plafond `θ̂_m + θ̂_n < 2·ln(H/4) = 11,0904`. Un **point témoin intérieur**
explicite appartient à `A`, ainsi que ses **18** perturbations axiales à rayon `r = 5e-3` : une boule
ouverte est exhibée, donc `|A| > 0`. Échantillonnage par rejet depuis la boîte : **20 000 tirages,
1 980 acceptés, taux d'acceptation 0,099** — strictement entre 0 et 1. `A` est borné, de mesure de
Lebesgue **finie et strictement positive** : **la loi uniforme sur `A` est une distribution de
probabilité propre et normalisée, échantillonnée exactement par rejet.** Les **1 980** tirages acceptés
donnent tous un `LatticeBondSpec` que le moteur accepte, et 200 `step` complets réussissent.

Fait mécanique supplémentaire, à charge du design : **(B2) n'est pas contraignante dans la boîte
déclarée** — 0 tirage sur 20 000 ne l'a violée, son maximum sur la boîte valant 0,375. Les contraintes
actives sont **(B1)** et le plafond sur `θ̂_m + θ̂_n`. Et à la frontière du plafond, `¼·e^{−S/2} = 1/H`
exactement : (B1) rejoint le plancher de la boîte au bord du simplexe.

**M10 — Coût (fait d'ingénierie, jamais scientifique).** `s/pas` : `8,745e-4` (16×16), `2,045e-3`
(32×32), `7,029e-3` (64×64) ; soit `s/pas/cellule` de `3,42e-6`, `2,00e-6`, `1,72e-6`. Moyenne retenue
`2,376e-6 s/pas/cellule`.

**M11 — Aller-retour disque.** Le pont persiste `measurement_frames/frame_%06d_bond.bin` (float64
little-endian, `(2,L,L)`) et `frame_%06d_mask.bin` (uint8 0/1). `Q` recalculée **à partir de ces octets
seuls** égale exactement la `Q` en mémoire aux quatre frames échantillonnées (`disque − mémoire = 0,0`),
et le masque persisté est bit-égal au masque de seuil. **`Q` est mesurable sur l'évidence persistée et
relue**, comme la Partie I §4.3 l'exige.

*Divulgation.* Le test de fermeture du cadre (M9) utilise un générateur pseudo-aléatoire pour le rejet —
l'échantillonnage par rejet ne peut pas se faire sur fixtures fabriquées. Il est étiqueté en code comme
dispositif numérique pour un témoin de mesure, **explicitement pas un seed scientifique** ; aucune
assertion ne dépend de sa valeur, seulement de `0 < taux < 1`.

### II.2 Ordre de dérivation et constantes déclarées

L'ordre de la Partie I §6.2 est suivi strictement. **Aucune valeur des missions précédentes n'est
réintroduite.**

| Rang | Quantité | Valeur | Dérivation |
|---|---|---|---|
| 1 | Plafond de calcul | **8 heures CPU** pour la famille scientifique | budget déclaré, indépendant de tout outcome ; sa suffisance est vérifiée en fin de chaîne, jamais utilisée pour la fixer |
| 2 | Tailles `𝓛` | **{16, 24, 32}**, carrées | plancher : deux entités cohébergées, chacune de support ≥ `min_cells = 3`, séparées par plus que la fenêtre d'association du tracker (3,0 cellules) et le rayon de dilatation (1), sur un tore, exigent `L ≥ 2·(3 + 3 + 1) ≈ 14` → 16, la première puissance de deux admissible. Plafond : le coût croît en `L²` (M10). Trois tailles, pas d'inspection préalable |
| 3 | Horizon `H` | **1024 pas** | structure déclarée du run : trois fenêtres — émergence, maintien sans forçage, lecture post-turnover — à ≥ 16 échantillons chacune, arrondi à **64 échantillons/run** ; avec `Δf = 16`, `H = 64 × 16 = 1024` |
| 4 | Cadence `Δf` | **16 pas** | choisie pour que la bande de taux résolvable `[1/H, 1/Δf]` couvre un facteur `H/Δf = 64` (≈ 1,8 décade), le plus large facteur compatible avec 64 échantillons par run |
| 5 | Boîte des groupes | taux `∈ [1/1024, 1/16]` ; `θ̂_m + θ̂_n < 11,0904` ; `ε̂_b ∈ [0,1]` ; `λ ∈ [0,1]` | principe unique de résolvabilité (Partie I §6.3) + borne d'admissibilité mécanique sur `ε̂_b` |
| 6 | Ensemble `A` et loi | uniforme sur `A`, par rejet | **normalisée**, non vide, mesure finie strictement positive (M9) |
| 7 | Frontières de décision | principe **du point milieu d'identifiabilité** | voir §II.3.4 et §II.4.4 — un seul principe, appliqué identiquement aux deux routes |
| 8 | Précision | demi-largeur pire-cas de l'IC exact 95 % **≤ la demi-largeur de la zone d'indifférence** | pour qu'une seule étude puisse tomber strictement dans un bras |
| 9 | Taille d'échantillon | **conséquence** du rang 8 | G : 260 paires ; E : 67 paires |
| 10 | Puissance | **conséquence**, jamais justification | §II.3.5, §II.4.5 |

Constantes du détecteur et du tracker : héritées telles quelles, déclarées comme **conventions de
mesure** avec leurs ensembles de sensibilité, exactement comme le `MEASUREMENT_SPEC` de 01R les a gelées.
Aucune n'est retirée d'un résultat.

### II.3 Route G — convention axis-signée entity-local

**II.3.1 Domaine.** Lattice carrée `L ∈ {16,24,32}`, frontières périodiques, loi tirée de `A`. `T` défini
comme en Partie I §4.1 sur les sept classes d'objets. `T² = id` et `U(Tx,TI) = T·U(x,I)` établis
mécaniquement (M1, M2). Hors domaine carré : pas de Z₂ (M8), Route G non définie.

**II.3.2 Observables.** `Q` (Partie I §4.3), impaire exactement (M3), nulle sur les états symétriques
(M3), **non déterminée par le masque** (M5), calculable sur l'évidence relue (M11). `S` (Partie I §4.4),
définie sur le masque seul, impaire (M4). `Q` et `S` sont indépendantes par construction : `S` ne lit
aucun champ de bonds.

**II.3.3 Estimand primaire et unité.**

- **Population** : tirages `(loi ∈ A, taille ∈ 𝓛, condition initiale)` selon la loi du rang 6, enrôlés en
  **paires exactes `(x, Tx)`**.
- **Unité** : la **paire**. Par équivariance exacte, la branche miroir produit l'indicateur miroir ; la
  paire compte donc **une** observation. Aucune pseudo-réplication : jamais l'entité, jamais la frame.
- **Condition** : aucune pour l'endpoint primaire — il est observationnel. Les bras d'intervention sont
  hiérarchiquement postérieurs.
- **Outcome** : indicateur binaire de **rétention de signe** — l'entité éligible d'une paire porte le
  même `sign(Q)` à la lecture post-turnover qu'à la lecture d'émergence, la lecture post-turnover ayant
  lieu **après** une fenêtre sans aucun forçage signé et après un turnover matériel vérifié par le canal
  de cohorte du pont (`cohort_residual` sous sa convention déclarée).
- **Événements intercurrents** : stratégie **composite**. Dissolution, split, merge, perte, handoff non
  résolu, censure au horizon, `Q` indéfinie et inéligibilité mécanique valent **0**, jamais exclusion.
- **Mesure de résumé** : `π` = proportion de paires enrôlées à outcome 1, intervalle de Clopper–Pearson
  exact à 95 %.

**II.3.4 Frontières — principe du point milieu d'identifiabilité (déclaré une fois).** Un signe non
maintenu est un tirage à pile ou face : `π = 1/2`. Un signe parfaitement maintenu donne `π = 1`. La
frontière POSITIVE est le **point milieu** de cet intervalle d'identifiabilité, `π₀ = 0,75` : c'est le
plus petit taux de rétention plus proche du déterminisme que du hasard. La frontière NÉGATIVE est le
point milieu de `[0,5 ; 0,75]`, soit `π₁ = 0,625` : au-dessous, la rétention est plus proche du hasard
que du seuil signifiant. Zone d'indifférence `[0,625 ; 0,75]`, largeur 0,125, **non dégénérée**. Aucune
de ces valeurs ne vient d'une observation ; le principe est déclaré avant tout calcul de taille et sera
appliqué **identiquement** à Route E.

**II.3.5 Taille, décision, puissance.** Cible de précision : demi-largeur pire-cas ≤ 0,0625.
**Plus petit `n` : 260 paires** (0,0624 ; `n = 259` donne 0,0625). **520 mondes.**

| Décision | Règle | Région à `n = 260` |
|---|---|---|
| `POSITIF` | borne CP inférieure `> 0,75` | `k ≥ 209` (0,8038) |
| `NÉGATIF` | borne CP supérieure `< 0,625` | `k ≤ 146` (0,5615) |
| `INDÉTERMINÉ` | sinon | `147 ≤ k ≤ 208` |

Caractéristiques opératoires — **conséquences**, jamais justifications : erreur de type I 0,0244 au bord
POSITIF et 0,0209 au bord NÉGATIF ; **MDE à 80 % : `π = 0,822` (POSITIF) et `π = 0,537` (NÉGATIF)** ;
puissance 0,982 à `π = 0,85` et 0,980 à `π = 0,50`. Les deux bras sont armés contre leur propre
frontière.

**Sous attrition (P5).** L'estimand est **inconditionnel** : les non-survivants comptent 0. Donc
`π_observé = π_rétention × fraction de survie`. Discriminateur figé : si la fraction de survie est
`< 0,5`, le bras POSITIF est inatteignable par construction et la famille rapporte
`INDÉTERMINÉ — INÉLIGIBILITÉ_MÉCANIQUE`, jamais `NÉGATIF`. La fraction de survie, la fraction de censure
au horizon et la fraction de `Q` indéfinie sont **co-primaires obligatoires**, rapportées
inconditionnellement.

**Hypothèse la plus dommageable si fausse (P8).** Que la fenêtre de maintien de 16 échantillons soit
longue au regard du temps de relaxation de `Q`. Si elle est courte, la rétention est triviale ; si elle
est trop longue, tout se dissout. C'est pourquoi la fenêtre est déclarée en **échantillons**, la
trajectoire complète de `Q` est publiée, et la sensibilité de la conclusion aux trois fenêtres est
préspécifiée.

**II.3.6 Séquence hiérarchique figée** (séquence fixe, `α = 0,05` par étape, arrêt au premier non-rejet ;
tout endpoint ultérieur devient exploratoire) :

| # | Endpoint | Test | Falsificateur |
|---|---|---|---|
| **H1** | Émergence non imposée | les deux signes surviennent ; biais global de signe testé contre la marge préjustifiée | biais > marge → **FAIL** ; par construction les paires `(x,Tx)` rendent le biais nul, donc H1 teste surtout `\|Q\|` au-dessus du plancher d'éligibilité |
| **H2** | **Indépendance à la forme** | rétention **stratifiée sur `S`**, endpoint primaire restreint à la strate `S ≈ 0` où la forme ne porte aucun signe ; plus un bras d'**égalisation géométrique** appariant les entités sur `S` | si `S` seul explique `Q` aussi bien que l'état des bonds, ou si le signal disparaît après égalisation → **G falsifiée** |
| **H3** | Maintien à travers le turnover | rétention entre lecture d'émergence et lecture post-turnover vérifié, la lecture ayant lieu **après washout**, jamais pendant un forçage | `Q` présent seulement juste après le forçage → **FAIL** |
| **H4** | Adressabilité locale | `FaceIntervention` sur les faces de A seulement ; bras **sham** (plan identité par le même chemin de code) et bras **hors cible** (même nombre de faces ailleurs) | pas d'effet différentiel cible/sham → **FAIL** |
| **H5** | Indépendance du partenaire | B cohébergé ne change pas ; concordance intra-paire d'entités testée en **équivalence** avec marge déclarée | changement correspondant chez B → **FAIL** |
| **H6** | Égalisation environnementale | champ de ressource égalisé/échangé entre A et B | le signe suit l'environnement → **FAIL** |
| **H7** | Invariance de taille | la conclusion doit tenir sur les trois tailles de `𝓛` | convention n'existant qu'à une taille → **FAIL** |

**Timing d'intervention gelé** : **aucun** traitement signé avant la lecture d'émergence. Les
interventions n'existent qu'à partir de H4, après H1–H3.

**II.3.7 Plafond et terminaison.** `260` paires `× 2` mondes `× 1024` pas, tailles `{16,24,32}` : coût
modélisé **783 s ≈ 0,22 heure CPU** sur la mesure M10 — largement sous le plafond déclaré de 8 heures.
Terminaison sur compte de mondes et horloge uniquement. Pas d'analyse intermédiaire. **Autorisation
fail-closed** : si le coût mesuré à la prérégistration dépasse le plafond, la famille **n'est pas
autorisée** et **n'est pas rétrécie**.

**II.3.8 Plafond de claim.** Un succès complet établirait au plus : **une convention axis-signée
entity-local dans le domaine carré périodique**, maintenue à travers un turnover vérifié, adressable
localement sous les interventions testées. Il **n'établirait pas** : une orientation indépendante de
tout substrat ; une individualité riche ; un ownership au-delà des modèles concurrents testés ; ni quoi
que ce soit hors du domaine carré.

### II.4 Route E — densité de réplication

**II.4.1 Distribution.** Identique au rang 6 : uniforme sur `A`, plus `L ∈ 𝓛`, plus des CI enrôlées en
paires `(x, Tx)`. Le moteur étant déterministe et sans RNG, **une réplication est un nouveau tirage
préenregistré de (loi, CI, taille)**, jamais un pseudo-seed. Le même `H` et le même `Δf`.

**II.4.2 Estimand.** Population : les tirages ci-dessus. **Unité : la paire.** Outcome binaire par
paire : au moins une entité éligible satisfait la conjonction — **persistance** (observée continûment
jusqu'au horizon, état terminal `RIGHT_CENSORED_AT_HORIZON`) **et** **turnover matériel complet
vérifié** (`cohort_residual` descend sous sa convention déclarée, mesurée entity-localement par le canal
de cohorte du pont). Événements intercurrents : composite, comme en G. Mesure de résumé : `Δ` =
proportion de paires à outcome 1, IC de Clopper–Pearson exact à 95 %.

**II.4.3 Éligibilité et bornes.** `E-1` géométrique : composant non enroulant (`wraps_y = wraps_x =
False`) et `aire ≤ ½·L²` — sur un tore, au plus un composant peut dépasser la moitié de l'aire, donc la
borne sépare l'entité de la phase de fond sans aucune constante ajustée. Rejet **avant enrôlement** des
lois que les validateurs du moteur refusent : ce sont des prédicats purs sur les paramètres et sur
l'état initial, lus en source, jamais des outcomes ; le compte des rejets est rapporté.

**II.4.4 Frontières — même principe du point milieu.** Un phénomène absent du cadre donne `Δ = 0` ; un
phénomène **typique** du cadre donne `Δ = 1/2`, la coupure sans a priori. Frontière POSITIVE
`Δ₀ = 0,50` : la conjonction est une propriété d'une loi typique. Frontière NÉGATIVE `Δ₁ = 0,25`, point
milieu de `[0 ; 0,5]` : plus proche de l'absence que du typique. Zone d'indifférence `[0,25 ; 0,50]`,
largeur 0,25, non dégénérée. **Le principe déclaré est exactement celui de G.**

**II.4.5 Taille, décision, puissance.** Cible de précision : demi-largeur pire-cas ≤ 0,125.
**Plus petit `n` : 67 paires** (0,1247 ; `n = 66` donne 0,1257). **134 mondes.**

| Décision | Règle | Région à `n = 67` |
|---|---|---|
| `POSITIF` | borne CP inférieure `> 0,50` | `k ≥ 42` (0,6269) |
| `NÉGATIF` | borne CP supérieure `< 0,25` | `k ≤ 9` (0,1343) |
| `INDÉTERMINÉ` | sinon | `10 ≤ k ≤ 41` |

Conséquences : type I 0,0249 et 0,0160 ; **MDE à 80 % : `Δ = 0,668` (POSITIF) et `Δ = 0,110`
(NÉGATIF)** ; puissance 0,923 à `Δ = 0,70` et 0,871 à `Δ = 0,10`. Coût modélisé **202 s ≈ 0,06 heure
CPU**.

**II.4.6 Négatif informatif.** Discriminateurs figés, rapportés inconditionnellement : fraction
d'inéligibilité mécanique ; fraction de censure au horizon (turnover jamais atteint) ; **dépendance aux
conditions initiales**, testée comme concordance intra-paire de loi contre le taux impliqué par
l'indépendance intra-loi, avec seuil numérique et mapping `POSITIF/NÉGATIF/INDÉTERMINÉ` propre ; et `Δ̂`
recalculée sur l'ensemble de sensibilité des sept constantes de mesure. **L'impossibilité structurelle
n'est jamais revendiquée.**

**II.4.7 Famille de reproduction.** Famille séparément autorisée, tirée d'un troisième bloc disjoint du
flux engagé, aux mêmes hashes de source, avec un critère **numérique** : reproduire l'appel primaire aux
mêmes frontières. Sa taille est fixée par le **même** principe de précision — donc `n₂ = 67` reproduit
les deux bras avec les mêmes caractéristiques opératoires que la primaire. C'est la réparation exacte du
défaut de 01R, où la famille de reproduction ne pouvait pas reproduire son propre bras négatif.

**II.4.8 Plafond de claim.** Un succès complet établirait au plus : **dans le cadre déclaré, la
conjonction persistance ∧ turnover matériel complet vérifié est instanciée par une proportion `Δ` des
tirages, avec l'intervalle indiqué**, au niveau du **tirage**, pas de l'entité. C'est **en deçà du
barreau 3** de l'échelle : Route E ne mesure aucune variable d'état, seulement la survie d'un composant
détecté à travers un remplacement matériel. Elle n'établit rien sur l'adressabilité ni sur l'ownership.

### II.5 Route F — cas affirmatif, évalué pour lui-même

Route F est sélectionnée **seulement si** ni G ni E ne passe. Son cas affirmatif est évalué ici, comme
la Partie I §11 l'exige, et non déduit de la disponibilité des autres :

- **Question qui resterait ouverte** : les deux, Q-G et Q-E, définitivement pour ce substrat.
- **Ce qui est déjà acquis** : la mémoire causale de bas niveau ; l'insuffisance de la mémoire pour
  l'individualité ; le pont de mesure qualifié ; l'existence d'une algèbre d'intervention locale ; et
  désormais l'équivariance exacte du substrat sous `T` et l'existence d'une observable signée non
  déterminée par la forme.
- **Ce qui devrait être abandonné** : rien de nouveau — les designs morts de 01R le sont déjà.
- **Arrêt temporaire ou définitif** : sous sa propre logique, temporaire, conditionné à une avancée
  externe.
- **Valeur épistémique attendue** : la consolidation n'apporte aucune information nouvelle sur les deux
  questions ouvertes, alors que **deux familles bornées et exécutables** existent, à 0,22 et 0,06 heure
  CPU. **Le cas affirmatif de F échoue.**

### II.6 Matrice commune — quatorze gates, application symétrique

`PASS` / `FAIL` uniquement. Un `FAIL` bloque la route. Aucune moyenne, aucun score.

| # | Gate | Route G | Route E | Route F |
|---|---|---|---|---|
| C1 | Domaine fini / distribution normalisée | **PASS** — uniforme sur `A`, non vide, mesure finie > 0, échantillonnée exactement par rejet (M9) ; `𝓛` fini ; CI en paires | **PASS** — identique | N-A |
| C2 | Observable correctement définie | **PASS** — `Q` sur évidence relue, sans identifiant, domaine d'indéfinition explicite (M3, M5, M11) | **PASS** — conjonction persistance ∧ turnover, sur évidence relue | N-A |
| C3 | Acquisition end-to-end | **PASS** avec `PRE_RUN_BLOCKER` §II.7 | **PASS** avec les mêmes `PRE_RUN_BLOCKER` | N-A |
| C4 | Falsificateurs prospectifs | **PASS** — neuf artefacts, chacun avec son discriminateur figé (Partie I §7) ; H2 peut falsifier G | **PASS** — quatre causes de nul discriminées | N-A |
| C5 | Estimand | **PASS** — six attributs ; unité = la paire ; pas de pseudo-réplication | **PASS** — six attributs ; unité = la paire | N-A |
| C6 | Null et alternative | **PASS** — `π = 1/2` contre maintien | **PASS** — `Δ` contre les deux frontières | N-A |
| C7 | Règle de décision | **PASS** — trois régions non vides | **PASS** — trois régions non vides | N-A |
| C8 | MDE / précision justifiée | **PASS** — principe du point milieu, déclaré avant la taille, identique aux deux routes ; précision = demi-largeur ≤ demi-indifférence | **PASS** — même principe | N-A |
| C9 | Puissance dans le plafond | **PASS** — MDE 0,822 / 0,537 ; 0,22 h CPU contre 8 h | **PASS** — MDE 0,668 / 0,110 ; 0,06 h CPU | N-A |
| C10 | Denominator sans remplacement | **PASS** — fixé à l'enrôlement en paires | **PASS** — identique | N-A |
| C11 | Lifecycle | **PASS** — cinq états terminaux, tous outcomes | **PASS** — identique | N-A |
| C12 | Provenance et ancrage | **PASS** avec `PRE_RUN_BLOCKER` §II.7 | **PASS** avec les mêmes | N-A |
| C13 | Faisabilité bornée | **PASS** — coût mesuré (M10), 520 mondes, terminaison hors outcome | **PASS** — 134 mondes | N-A |
| C14 | Pas de calibration sur familles fermées | **PASS** — chaque borne vient de la source, de la géométrie, du principe de résolvabilité ou du principe du point milieu | **PASS** — identique | N-A |
| | **Résultat** | **14 PASS — admissible** | **14 PASS — admissible** | **cas affirmatif échoué** |

**Raison du `N-A` de F, énoncée une fois** : F n'enrôle aucune unité, ne mesure aucune quantité et
n'exécute aucune famille ; chaque gate régit un design prospectif et n'a donc pas d'objet. Son
admissibilité se décide uniquement par le test affirmatif de la Partie I §11.3, qu'elle échoue (§II.5).

**Contrôle de symétrie.** Aucune capacité n'est fatale pour une route et différée pour l'autre : les
mêmes `PRE_RUN_BLOCKER`, la même distribution, le même principe de frontière, la même règle de
précision, la même unité statistique, la même stratégie composite. Les deux routes se distinguent par
leur **question**, pas par leur traitement.

### II.7 `PRE_RUN_BLOCKER` (identiques pour G et E)

| # | Obligation | Fermeture exacte exigée avant toute famille scientifique |
|---|---|---|
| **PRB-1** | Jointure track–component persistée | écrire les triplets `(frame, digest canonique de l'ensemble de cellules, track_id)` dans l'évidence liée à la racine |
| **PRB-2** | Receipt obligatoire | l'entrée scientifique supportée refuse sans receipt vérifié |
| **PRB-3** | Ordre des checks figé | épingler par test l'ordre « évidence locale → digest de la racine → vérificateur » |
| **PRB-4** | Copie/replay liée à une racine extérieure | lier l'identité du run et l'enrôlement de la famille dans la racine, de sorte qu'une copie bit-identique ne rejoue pas |
| **PRB-5** | Entry point scientifique unique | un seul point d'entrée supporté ; `open_owned_analysis_access` reste atteignable au niveau inférieur et doit être fermé ou déclaré hors protocole |
| **PRB-6** | Ancrage externe de la racine finale | commitment public immuable ou append-only, vérifiable sans secret ; l'authentification de publication reste séparée de la vérification publique |

Un `PRE_RUN_BLOCKER` n'est pas une raison de relancer l'architecture. **Aucune famille scientifique ne
peut commencer avant sa fermeture.**

### II.8 Décision préliminaire

Priorité de la Partie I §11 appliquée mécaniquement :

1. **G passe les quatorze gates** → `primary_route = "G"`.
2. **E passe également les quatorze** → `backup_route = "E"`.
3. F n'est pas sélectionnée : son test affirmatif échoue, et la Partie I §11 interdit de la préférer
   quand G ou E passe.

**Disposition terminale préliminaire :** `AXIS_FRAME_CLOSURE_01S_ROUTE_G_SELECTED`, sous réserve des deux
reviews adversariales.

**Pourquoi G plutôt que E, sur la matrice et non sur le goût.** Les deux passent ; la priorité gelée
`G → E → F` a été fixée en Partie I §11 **avant** toute conception, et elle n'est pas un jugement de
valeur : elle reflète que G interroge le barreau qui compte — l'ownership causal entity-local d'un état
— tandis que E interroge une prévalence au niveau du tirage, en deçà du barreau 3. E reste backup
précisément parce qu'elle passe.

---

## Partie III — REVIEWS, CORRECTION CONSOLIDÉE, DÉCISION TERMINALE

*Les Parties I et II sont inchangées. La Partie I reste un préfixe byte-exact de 23 901 octets. Toute
correction ici est additive : rien n'est réécrit au-dessus.*

### III.1 Verdicts

Les deux reviewers ont été lancés **en parallèle**, contre le même package (Parties I + II, 54 712
octets, sha256 `79e9a85fb13c79732421106f4a2d142cfe716a6c8e2a19141cb8d6628ac1da6c`), le fichier de test
et l'arithmétique de design.

| Reviewer | Verdict | Findings |
|---|---|---|
| A — symétrie, `Q` vs forme, estimands, distribution, statistiques, puissance, pseudo-réplication | **FAIL** | A1–A14 : 1 `PACKAGE_BLOCKER`, 6 `ROUTE_G_GATE_FAIL`, 3 `ROUTE_E_GATE_FAIL`, 5 `MINOR_NON_BLOCKING` |
| B — implémentation, détecteur/tracker, intervention, lifecycle, provenance, replay, contournements, firewall | **FAIL** | B1–B14 : 1 `PACKAGE_BLOCKER`, 4 `ROUTE_G_GATE_FAIL`, 1 `ROUTE_E_GATE_FAIL`, 8 `MINOR_NON_BLOCKING` |

Les deux ont reproduit toute l'arithmétique de la Partie II sans écart, et Reviewer A l'a recalculée par
une implémentation indépendante de Clopper–Pearson. **Aucun finding n'a été jugé invalide.** Le registre
complet est au journal.

**Deux findings sont décisifs et ont été reproduits mécaniquement par l'auteur, aux valeurs exactes
rapportées, et ajoutés au fichier de test scellé** (`fact19`–`fact24`, +6 tests ; suite complète
**673 passés, 0 échec, 0 skip**) :

**A1 / `fact19` — le signe de `Q` n'est pas stable à l'horizon de design.** Sur la fixture symétrique, à
la loi par défaut, sur **1024 pas** échantillonnés à chaque pas : `sign(Q_a)` **change trois fois**, aux
pas **509, 774 et 820** ; l'identité d'imparité inter-branches `Q_b = −Q_a` **échoue à 247 des 1025
échantillons** (résidu 1,11e-16 à 2,22e-16), la première fois au pas 509 ; `min |Q_a| = 1,41e-05` et
`Q_a(1024) = −5,67e-03`. Les masques détectés restent des transposés exacts aux 1025 échantillons :
l'instabilité est **purement numérique**, `Q` étant une différence de deux moyennes presque égales.

**B1 / `fact20`–`fact21` — le tracker n'est pas équivariant sous transposition quand un composant
enroule le tore.** Recherche sur 3 840 séquences 8×8 à trois frames contenant un composant enroulant :
**179 asymétriques**. Contre-exemple épinglé : branche simple `APPEARANCE, CONTINUATION, DISSOLUTION,
APPEARANCE` (2 tracks) contre branche transposée `APPEARANCE, CONTINUATION, CONTINUATION` (1 track). Le
mécanisme est établi au niveau de l'arête : le relèvement DFS de `detect_components` est amorcé sur le
**minimum d'index linéaire**, non covariant sous transposition ; en frame 2 le centroïde saute
`2,5556 → 5,2222` en `x` sans qu'aucune cellule ne bouge en `x`, la distance périodique vaut 3,3333 > 3,0
et l'arête est rejetée par `REJECT_CENTROID_DISTANCE`. **Contrôle positif** : sur **1 280** séquences
sans aucun composant enroulant, **0 asymétrie** — l'exclusion des composants enroulants contient
exactement le défaut.

### III.2 Claims retirés

Conformément à la Partie I §13, chacun est **retiré**, pas reformulé ; le texte d'origine reste au-dessus.

**R1 — §II.1 M6, « maintenu — exactement, indéfiniment »** (A1). **FAUX.** L'inférence « par
équivariance exacte, `Q(U^k(Tx)) = −Q(U^k(x))` pour tout `k` » confond deux choses : la relation
**inter-branches** `Q_b = −Q_a`, qui est une identité de symétrie sans contenu temporel, et la
**persistance temporelle** de `sign(Q_a)`, qui est une affirmation empirique et qui est **réfutée par la
seule trajectoire jamais exécutée**, bien à l'intérieur de l'horizon. La forme correcte, retenue : *sur
cette fixture, à la loi par défaut, `|Q|` décroît de 0,600 à 0,401 en 30 pas, puis traverse zéro au pas
509*. Rien de plus.

**R2 — §II.1 M6 et §II.3.6 H2, « `Q` peut être maintenue indépendamment de la forme »** (A2). **NON
ÉTABLI.** M5 (`Q` n'est pas une fonction du masque) tient et n'est pas contesté. Mais M6 opère sur un
masque invariant sous `T`, donc `S ≡ 0` : **la variable explicative concurrente a une variance nulle
pendant toute la démonstration**. On ne peut pas identifier l'indépendance de `Q` vis-à-vis de `S` dans
un design où `S` ne varie pas. Et H2 rend la chose intestable : son primaire est restreint à la strate
`S ≈ 0`, où son propre falsificateur gelé — « si `S` seul explique `Q` aussi bien que l'état des bonds →
G falsifiée » — **ne peut pas se déclencher**.

**R3 — §II.3.6 H1 et §II.4.6, les falsificateurs d'orientation et de dépendance aux CI** (A3, A4).
**VIDES PAR CONSTRUCTION.** L'enrôlement en paires `(x, Tx)` force la somme globale des signes à zéro
comme **identité algébrique** : la probabilité de rejet de H1 est 0 sous toute hypothèse. De même
l'outcome de E est invariant sous `T`, donc la concordance intra-paire vaut 1 avec probabilité 1. La
Partie II substitue silencieusement à H1 un autre endpoint (`|Q|` au-dessus d'un « plancher
d'éligibilité » jamais chiffré), ce que la Partie I §7 interdit : les discriminateurs sont gelés avant
toute donnée.

**R4 — §II.1 M7 et §II.3.3, l'équivariance du tracker et « la paire compte une observation »** (B1).
**FAUX HORS DU SOUS-DOMAINE SANS ENROULEMENT.** Voir `fact20`. Le quotient `{(M, Q, S)}` ne pouvait pas
attraper le défaut : il écarte précisément `centroid_y`, `centroid_x`, `wraps_*` et `radius_gyration`,
c'est-à-dire les champs que le tracker consomme ; `fact12` était une tautologie donnée M2–M4.

**R5 — §II.3.6 H3/H4/H6, exécutables avec le contrat accepté** (B2, B3). **FAUX.**
`run_measurement_bridge` accepte **un seul** `FaceIntervention` et l'applique à **chaque** pas du
calendrier. Donc : le bras cible est actif dès le premier pas — « aucun traitement signé avant la
lecture d'émergence » est violé **par construction** ; le plan ne peut pas être retiré, donc « lecture
après washout » est inatteignable ; et le plan doit viser les faces de A, inconnues avant l'émergence de
A, ce que la signature ne peut pas accepter. Chaîner trois runs ne répare rien : la cohorte est enrôlée
à la première frame échantillonnée **de chaque run** (vérifié : un run chaîné repart à
`cohort_residual = 1,0`), et les identifiants de track sont par run. Enfin **aucune opération du code
accepté n'égalise ni n'échange le champ de ressource `n`** entre deux entités cohébergées : H6 n'a
aucun chemin d'implémentation.

**R6 — §II.7 PRB-5, « un seul point d'entrée supporté »** (B4). **ÉNUMÉRATION INCOMPLÈTE.**
`future_lifecycle_runner.open_analysis_access(directory, tracking, sampled_frames)` accepte un
`TrackingResult` **fourni par l'appelant** et délivre un `AnalysisAccess` à partir du manifeste de
complétion et du document de cycle de vie seuls — sans document de mesure, sans racine, sans receipt
d'ancrage. `publish_future_family_completion` et `qualify_and_write_lifecycle_contract` sont également
exportés. C3 et C12 n'étaient marqués `PASS` que « avec `PRE_RUN_BLOCKER` » : une énumération incomplète
rend ces `PASS` non acquis **pour les deux routes**.

**R7 — §II.3.5, les caractéristiques opératoires sous attrition** (A6). **ASSERTÉES, NON ÉVALUÉES.** À
`n = 260`, rétention **parfaite** parmi les survivants et survie `s`, la probabilité de conclure est :
`P(POSITIF) = 0,803` à `s = 0,822`, `0,475` à `s = 0,80`, `0,024` à `s = 0,75` ; et
`P(NÉGATIF) = 0,920` à `s = 0,52`. Le garde-fou déclaré (`survie < 0,5 → INDÉTERMINÉ`) est **sous** toute
la bande dangereuse `s ∈ [0,50 ; 0,62]` : avec 52 % de survie et 100 % de rétention, l'étude conclut
`NÉGATIF` avec probabilité 0,92 — un faux négatif fabriqué par la seule attrition. Le garde-fou ne
couvre pas non plus l'inéligibilité (`Q` indéfinie), dont M7 rapporte 2 composants sur 3 sur une
fixture.

**R8 — §II.3.3 et §II.4.2, la stratégie composite et l'outcome par paire** (B5, B6, A7). **AMBIGUËS OU
DÉGÉNÉRÉES.** Le contrat accepté a exactement cinq états terminaux ; §II.3.3 attribue 0 aux six
événements nommés, dont « censure au horizon », alors qu'une entité vivante à la lecture post-turnover
termine **nécessairement** en `RIGHT_CENSORED_AT_HORIZON` : à la lettre, `π ≡ 0` et la région `POSITIF`
est inatteignable. Le même terme sert de **succès** pour E en §II.4.2 et d'échec pour G en §II.3.3.
« Perte » n'a pas d'état correspondant. L'outcome dit « **l'**entité éligible » au singulier alors que
H4–H6 exigent deux entités cohébergées. E ne dit pas si « au moins une entité éligible » porte sur une
branche ou sur les deux.

**R9 — §II.3.6, cinq seuils déterminant l'outcome sans aucun nombre** (A8, A9). « Marge préjustifiée »
(H1), « plancher d'éligibilité » (H1), bande de la strate `S ≈ 0` et calibre d'appariement (H2),
statistique et seuil cible/sham (H4), marge d'équivalence (H5) : aucun n'est chiffré. Pire,
`cohort_residual_fraction = 0,05`, qui définit l'outcome primaire de E et la lecture post-turnover de G,
n'existe que comme **défaut du pont** ; il n'est ni énoncé ni dérivé, et la Partie I §16 interdit de
réintroduire « aucune marge » sans dérivation nouvelle.

**R10 — §II.2 rang 5 et Partie I §6.3, la justification de `ε̂_b ∈ [0,1]`** (A10). **FAUSSE.** Avec
`ε̂_b = 5` et `D̂ = k̂_on = 0,015`, (B2) vaut 0,21, le spec se construit et **200 pas complets
s'exécutent avec `min(n) = 0,256 > 0`** : aucun `ArithmeticError`. La borne mécanique réelle est (B2)
elle-même, soit `ε̂_b < (1 − 4D̂)/(2k̂_on) ≈ 505` au plancher de la boîte. `ε̂_b ∈ [0,1]` est donc une
**restriction de portée déclarée**, pas une borne mécanique — et le fait annoncé que « (B2) n'est pas
contraignante » en est l'artefact direct.

**R11 — §II.2 rangs 3–4 et §II.1 M9** (A11). L'arrondi de 48 à 64 échantillons n'était pas justifié, la
justification de `Δf` était vacue (`H/Δf = 64` par définition de 64 échantillons), les valeurs
`H = 1024`, `Δf = 16` étaient étiquetées « témoins mécaniques, **pas** valeurs de design » dans le test
et adoptées comme valeurs de design en §II.2, et « `¼·e^{−S/2} = 1/H` exactement » était présentée comme
un fait découvert alors que c'est l'identité définissant le plafond.

**R12 — défauts mineurs, acceptés en bloc** (A12, A13, A14, B7–B14). L'équivariance n'était testée
qu'à la loi par défaut et aux tailles 4/6/9, jamais aux tailles déclarées ni aux lois de `A` ; « `n = 259`
donne 0,0625 » masquait 0,06252, qui **échoue** la cible ; l'en-tête « `PASS`/`FAIL` uniquement »
précédait quatorze cellules `N-A` ; §II.5 citait une « Partie I §11.3 » qui ne définit aucun test
affirmatif ; le plancher `L ≥ 2·(3+3+1)` additionne un **compte** et des **longueurs** ; M10 n'est pas
reproductible à mieux que ±15 % et ne compte que les pas moteur, sans acquisition (facteur mesuré 1,52×)
ni bras H4–H6 ni plafond de stockage ; la paire ne fournit **aucun** réplicat (l'indicateur de la
branche miroir est algébriquement identique) ; M3 revendiquait l'exactitude là où le test asserait une
tolérance ; la « boule ouverte » de M9 n'était que 18 points axiaux ; M11 n'était établi que sur un
composant.

### III.3 Correction consolidée — une seule passe

**III.3.1 Ce qui a été ajouté mécaniquement** (`fact19`–`fact24`, fichier de test porté à 72 939 octets,
sha256 `5c0b02681a16211b87a88baeb9ccbc96793dc3530440f93ad5064e5313f480ab`, **27 tests**, suite complète
**673 passés**) :

- **`fact19`** — l'instabilité de `sign(Q)` à 1024 pas (A1), avec les pas de croisement et le compte
  d'échecs d'imparité.
- **`fact20`/`fact21`** — le contre-exemple d'enroulement (B1) **et** le contrôle positif : 1 280
  séquences sans enroulement, **0 asymétrie**.
- **`fact22`/`fact23`** — **la fermeture complète du cadre.** Avec `dt = 1`, `m_max = n_max = 1`, les
  neuf groupes sans dimension **sont numériquement les champs de `LatticeBondSpec`**, et le contrôle
  d'admissibilité du moteur `dt ≤ admissible_dt_limit` est **exactement équivalent** à la conjonction
  (B1) ∧ (B2) : vérifié sur **2 500 points** de part et d'autre de la frontière, **0 discordance**. Et la
  loi des conditions initiales — `m[y,x] ~ U[0,1]` i.i.d., `n[y,x] ~ U[0,1]` i.i.d., `b ≡ 0` — est un
  **produit de mesures uniformes sur une boîte compacte**, donc normalisée et exactement
  échantillonnable par construction : **1 680 validations** sur `L ∈ {16,24,32}`, **0 rejet**, bornes du
  support vérifiées, **210 `engine.step` complets** réussis. C'est la réparation exacte de A5.
- **`fact24`** — l'équivariance **aux tailles déclarées et aux lois de `A`** : 8 lois tirées de
  l'ensemble admissible, `dt = 1`, intervention non auto-transposée, `L ∈ {16,24,32}` : résidu maximal
  **0,0** à un pas et **2,22e-16** cumulé sur 25 pas. C'est la réparation exacte de A12.
- **`fact07`/`fact08`** — tolérances remplacées par l'égalité exacte, qui passe (B7).

**III.3.2 Corrections documentaires acceptées en bloc.** R10 : `ε̂_b ∈ [0,1]` est reclassée
**restriction de portée déclarée**, portée au plafond de claim ; la justification par `ArithmeticError`
est supprimée. R11 : `H = 1024` et `Δf = 16` sont **déclarés** comme valeurs de design — quatre fenêtres
de 16 échantillons (base, turnover, persistance post-turnover, marge d'horizon) — et l'étiquette
« témoins, pas valeurs de design » est retirée ; l'identité `¼e^{−S/2} = 1/H` est dégradée en remarque.
R12 : `n = 259` donne **0,06252**, qui échoue la cible ; l'en-tête de la matrice admet `N-A` avec sa
raison unique ; le test affirmatif de F est régi par la **Partie I §11.3** telle qu'elle est écrite —
« sinon `primary_route = "F"` » — plus le §II.5 de ce rapport, et la citation d'un « test affirmatif »
gelé est retirée ; le plancher de taille est reformulé sans addition dimensionnellement incohérente ;
M10 est rapporté comme un **intervalle** (±15 %) portant sur les pas moteur seuls, avec le facteur
d'acquisition mesuré **1,52×** et un plafond de stockage déclaré ; la paire n'est plus appelée un
réplicat.

### III.4 Route G — rejetée définitivement

La Partie I §11 impose : si G échoue et E passe, **G est définitivement rejetée pour ce programme**. Le
parent l'impose aussi, littéralement : *« si aucune convention signée indépendante de la forme ne peut
être justifiée, rejeter définitivement la route concernée plutôt que la différer encore une fois pour le
même motif. »* **01S est la troisième mission à buter sur Route G. Il n'y aura pas de quatrième
report.**

| Gate | Verdict | Motif |
|---|---|---|
| **C2** | **FAIL** | l'observable primaire n'est pas *stable* à l'horizon de design : sur la seule trajectoire jamais exécutée, `sign(Q)` traverse zéro aux pas 509, 774 et 820, et `|Q|` descend à 1,4e-05, du même ordre que la dérive numérique qui casse l'imparité inter-branches à 247 échantillons sur 1025. Un endpoint de rétention de signe entre deux lectures séparées de centaines de pas n'est pas mesurable dans ces conditions. **Raccourcir les fenêtres pour restaurer le signal serait caler le design sur une sortie mécanique — explicitement interdit par le parent §13 et par la Partie I §16.** |
| **C3** | **FAIL** | H3, H4 et H6 ne sont pas exécutables avec le contrat accepté : un seul plan d'intervention, appliqué à chaque pas, non retirable, non dépendant de l'état ; cohorte et tracks réinitialisés à chaque run ; **aucune opération n'égalise ni n'échange le champ de ressource**. La capacité manquante — ordonnancement d'interventions fenêtrées et dépendantes de l'état, plus substitution de champ en cours de run — n'est pas une fermeture bornée au sens de la Partie I §15 : c'est un nouveau programme d'ingénierie. La déclarer `PRE_RUN_BLOCKER` serait exactement le maquillage de gate que la Partie I §15 interdit |
| **C4** | **FAIL** | le falsificateur d'orientation (H1) est vide par construction ; celui de forme (H2) ne peut pas se déclencher sur sa propre strate primaire, où `S ≡ 0` ; ceux d'intervention et d'environnement disparaissent avec H4 et H6. Quatre des neuf artefacts gelés de la Partie I §7 n'ont plus de discriminateur |
| **C5** | **FAIL** | pseudo-réplication dans la séquence confirmatoire : H2, H4, H5 et H6 y siègent à `α = 0,05` sans unité déclarée, sans structure de dépendance, sans taille et sans puissance, ce que la Partie I §8 qualifie explicitement de `FAIL` de C5 ; et l'argument « la paire compte une observation » repose sur une équivariance du tracker qui est fausse dès qu'un composant enroule le tore |
| **C7** | **FAIL** | cinq seuils déterminant l'outcome sans valeur ; et la stratégie composite, à la lettre, rend `π ≡ 0` et la région `POSITIF` inatteignable |
| **C9** | **FAIL** | caractéristiques opératoires non évaluées sous l'attrition ; le garde-fou déclaré est sous la bande où l'attrition seule fabrique un `NÉGATIF` avec probabilité 0,92 |
| C1, C6, C8, C10, C11, C12, C13, C14 | atteints ou non atteints | non crédités : six échecs fatals suffisent |

**Six gates fatals. Route G est inadmissible et définitivement rejetée pour ce programme.**

**Ce qui n'est pas dit.** Route G n'est pas scientifiquement réfutée. Ce qui est établi est qu'elle
n'est pas *exécutable ni mesurable* sur ce substrat avec ce contrat : l'observable perd son signe à
l'intérieur de l'horizon pour des raisons numériques, le tracker n'est pas équivariant là où
l'observable l'est, et les endpoints d'ownership exigent des capacités qui n'existent pas. Ce qui
survit et est banqué : l'équivariance exacte de l'update et de son ledger sous transposition, dans le
domaine carré périodique, aux tailles et aux lois déclarées ; `Q` n'est pas une fonction du masque ;
l'algèbre d'intervention locale existe ; l'asymétrie du tracker est localisée et **contenue par
l'exclusion des composants enroulants** (1 280 séquences, 0 asymétrie).

### III.5 Route E — corrigée

**III.5.1 Corrections.** La pairing `(x, Tx)` est **abandonnée** : l'outcome de E est invariant sous
`T`, la branche miroir ne porte aucune information (R3), et l'appariement voulait servir un
discriminateur qui était vide. **L'unité est le tirage.** Route E ne dépend donc plus du tout de la
symétrie de transposition, et le défaut du tracker (R4) ne la touche que par l'exclusion des composants
enroulants, qu'elle imposait déjà.

**III.5.2 Cadre, entièrement fermé et prouvé.**

| Élément | Valeur | Fondement |
|---|---|---|
| Échelles | `dt = 1`, `m_max = 1`, `n_max = 1` | choix d'unités ; **conséquence prouvée** : les neuf groupes sans dimension *sont* les champs de `LatticeBondSpec`, et `dt ≤ admissible_dt_limit` **équivaut exactement** à (B1) ∧ (B2) — 2 500 points, 0 discordance (`fact22`) |
| Loi sur les neuf groupes | uniforme sur `A = Boîte ∩ (B1) ∩ (B2)` | bornée, mesure finie > 0 (taux d'acceptation 0,099), échantillonnée exactement par rejet — **normalisée** |
| Boîte | taux `∈ [1/1024, 1/16]` ; `θ̂_m + θ̂_n < 11,0904` ; `ε̂_b ∈ [0,1]` (**restriction de portée déclarée**, R10) ; `λ ∈ [0,1]` | principe de résolvabilité + source |
| **Loi des conditions initiales** | `m[y,x] ~ U[0,1]` i.i.d., `n[y,x] ~ U[0,1]` i.i.d., `b ≡ 0` | **produit de mesures uniformes sur une boîte compacte** : normalisée et exactement échantillonnable par construction ; 1 680 validations, 0 rejet (`fact23`) |
| Tailles | `L ∈ {16, 24, 32}`, carrées, tirage uniforme | plancher : deux entités séparées par plus que la fenêtre d'association (3,0 cellules) et le rayon de dilatation (1), chacune de diamètre au moins 2, sur un tore → `L ≥ 16` ; plafond : coût en `L²` |
| Horizon, cadence | `H = 1024` pas, `Δf = 16` | quatre fenêtres de 16 échantillons : base, turnover, persistance post-turnover, marge d'horizon → 64 échantillons ; `Δf = 16` co-déclaré avec le bord supérieur de la boîte |

**III.5.3 Estimand.** Population : tirages `(loi ∈ A, L ∈ 𝓛, CI)` selon les lois ci-dessus. **Unité : le
tirage** (un monde). Outcome binaire : **au moins un composant éligible du monde satisfait la
conjonction**. Éligibilité : `wraps_y = wraps_x = False` **à chaque frame échantillonnée où il est
observé**, `aire ≤ ½·L²`, masse `> 0` à la lecture, et — nouveauté R8 — **aucun composant enroulant
n'est présent dans le monde à aucune frame échantillonnée**, puisque le graphe d'association est global.
Conjonction : **persistance** — le track est observé continûment jusqu'au horizon et son état terminal
est `RIGHT_CENSORED_AT_HORIZON` — **et** **remplacement matériel vérifié** — `cohort_residual` du
composant descend au plus à `cohort_residual_fraction`.

**Mapping des six événements sur les cinq états terminaux** (R8) : dissolution →
`DISSOLVED_DETECTED_TRACK` ; split → `SPLIT_INTO_TRACKS` ; merge → `MERGED_INTO_TRACK` ; perte et
handoff non résolu → `UNRESOLVED_HANDOFF` ; survie à l'horizon → `RIGHT_CENSORED_AT_HORIZON`. Les quatre
premiers **valent 0** ; le cinquième est la **seule** configuration pouvant valoir 1, et seulement si le
remplacement est aussi vérifié. **Un composant dissous a une masse nulle et un `cohort_residual` de 0,0
par convention du pont : il ne compte jamais comme remplacement complet**, l'éligibilité exigeant
`masse > 0` à la lecture (R8, A9).

**`cohort_residual_fraction`** (R9) : il n'est **pas** hérité comme valeur d'autorité. Il est déclaré
**convention de mesure** avec une **règle de décision préspécifiée sur son ensemble de sensibilité**
`{0,01 ; 0,05 ; 0,20}` : **la conclusion doit être invariante sur les trois valeurs, sinon la famille
rapporte `INDÉTERMINÉ — CONVENTION_DE_REMPLACEMENT`.** C'est une règle nouvelle, indépendante de tout
outcome, qui remplace une valeur silencieuse par une exigence d'invariance.

**III.5.4 Frontières et décision.** Principe **déclaré** — et désormais étiqueté **convention**, non
principe scientifique (A, sur le point milieu) : absence `Δ = 0`, typique `Δ = 1/2` ; frontière POSITIVE
`Δ₀ = 0,50`, frontière NÉGATIVE `Δ₁ = 0,25` (point milieu de `[0 ; 0,5]`). Zone d'indifférence
`[0,25 ; 0,50]`, largeur 0,25, non dégénérée. Précision : demi-largeur pire-cas de l'IC exact 95 % ≤ la
demi-largeur d'indifférence, soit ≤ 0,125.

**Taille : `n = 67` tirages** — la plus petite (`0,124721` ; `n = 66` donne `0,125693`, qui échoue).
Pour le discriminateur de dépendance aux CI, **deux CI indépendantes par loi** sont tirées : la première
sert le primaire, la seconde le discriminateur. **134 mondes.**

| Décision | Règle | Région |
|---|---|---|
| `POSITIF` | borne CP inférieure `> 0,50` | `k ≥ 42` (0,6269) |
| `NÉGATIF` | borne CP supérieure `< 0,25` | `k ≤ 9` (0,1343) |
| `INDÉTERMINÉ` | sinon | `10 ≤ k ≤ 41` |

Conséquences : erreurs de type I **0,0249** et **0,0160** ; **MDE à 80 % : `Δ = 0,668` et `Δ = 0,110`** ;
puissance 0,923 à `Δ = 0,70` et 0,871 à `Δ = 0,10`.

**Sous attrition (R7 appliqué à E).** L'estimand est inconditionnel ; les tirages sans composant
éligible valent 0. Garde-fou **rattaché à la coupure POSITIVE**, pas à un demi arbitraire : si la
fraction de tirages sans aucun composant éligible dépasse **0,50**, `Δ ≤ 0,50` et le bras POSITIF est
inatteignable par construction — la famille rapporte `INDÉTERMINÉ — INÉLIGIBILITÉ_MÉCANIQUE`, jamais
`NÉGATIF`. Sont co-primaires obligatoires et rapportées inconditionnellement : la fraction
d'inéligibilité mécanique, la fraction de censure (turnover jamais atteint avant l'horizon), et la
répartition complète sur les cinq états terminaux.

**Négatif informatif.** Quatre causes discriminées : densité réellement basse (`k ≤ 9` avec les deux
fractions ci-dessus sous leurs seuils) ; **dépendance aux conditions initiales** — concordance entre les
**deux CI indépendantes** de chaque loi, comparée au taux impliqué par l'indépendance intra-loi, seuil
numérique déclaré, avec son propre mapping ternaire ; inéligibilité mécanique ; censure d'horizon. Et
`Δ̂` est recalculée sur l'ensemble de sensibilité des constantes de mesure.

**III.5.5 Coût, terminaison, reproduction.** 134 mondes × 1024 pas, `L ∈ {16,24,32}` : **202 s ± 15 %**
de pas moteur, **×1,52** pour l'acquisition mesurée → **≈ 307 s ≈ 0,09 heure CPU**, contre le plafond
déclaré de **8 heures**. Stockage : ≈ 2,9 Mo d'évidence par monde à `L = 32` → **plafond de stockage
déclaré 8 Go**. Terminaison sur compte de mondes et horloge. Aucune analyse intermédiaire.
**Autorisation fail-closed** : si le coût mesuré à la prérégistration dépasse un plafond, la famille
n'est pas autorisée et **n'est pas rétrécie**. Famille de reproduction : `n₂ = 67` tirages d'un troisième
bloc disjoint, aux mêmes hashes, avec le **même** critère numérique — elle reproduit donc les deux bras
avec les mêmes caractéristiques opératoires que la primaire.

**III.5.6 Plafond de claim.** Un succès complet établirait au plus : *dans le cadre déclaré — lattices
carrées de `𝓛`, frontières périodiques, lois uniformes sur `A` avec `ε̂_b ≤ 1`, CI uniformes — la
conjonction persistance ∧ remplacement matériel vérifié est instanciée par une proportion `Δ` des
tirages, avec l'intervalle indiqué*. Au niveau du **tirage**, jamais de l'entité. C'est **en deçà du
barreau 3** : Route E ne mesure aucune variable d'état. Elle n'établit rien sur l'adressabilité, rien
sur l'ownership, rien sur une convention, rien hors du cadre déclaré.

### III.6 `PRE_RUN_BLOCKER` corrigés (R6)

| # | Obligation | Fermeture exacte |
|---|---|---|
| PRB-1 | jointure track–component persistée | écrire `(frame, digest canonique de l'ensemble de cellules, track_id)` dans l'évidence liée à la racine |
| PRB-2 | receipt obligatoire | l'entrée scientifique supportée refuse sans receipt vérifié |
| PRB-3 | ordre des checks figé | épingler par test « évidence locale → digest de racine → vérificateur » |
| PRB-4 | replay | lier identité du run et enrôlement de la famille dans la racine |
| **PRB-5** | **entrée unique — énumération complète** | fermer ou déclarer hors protocole, avec un test épinglant le refus : `open_owned_analysis_access`, **`future_lifecycle_runner.open_analysis_access`**, **`publish_future_family_completion`**, **`qualify_and_write_lifecycle_contract`** |
| PRB-6 | ancrage externe | commitment public immuable ou append-only, vérifiable sans secret |

### III.7 Matrice commune corrigée

| # | Gate | Route G | Route E | Route F |
|---|---|---|---|---|
| C1 | domaine fini / distribution normalisée | — | **PASS** — loi sur `A` **et** loi des CI, toutes deux normalisées et prouvées (`fact22`, `fact23`) | N-A |
| C2 | observable correctement définie | **FAIL** (III.4) | **PASS** — conjonction sur évidence relue ; seuil de remplacement déclaré avec règle d'invariance ; convention `masse = 0` explicitée | N-A |
| C3 | acquisition end-to-end | **FAIL** (III.4) | **PASS** — tout est lié par le pont qualifié ; PRB-1..6 déclarés avec fermeture exacte | N-A |
| C4 | falsificateurs prospectifs | **FAIL** (III.4) | **PASS** — quatre causes de nul, chacune avec son discriminateur chiffré | N-A |
| C5 | estimand | **FAIL** (III.4) | **PASS** — unité = le tirage ; outcome au niveau du monde ; aucune pseudo-réplication | N-A |
| C6 | null et alternative | — | **PASS** | N-A |
| C7 | règle de décision | **FAIL** (III.4) | **PASS** — trois régions non vides, mapping des cinq états terminaux explicite | N-A |
| C8 | MDE / précision justifiée | — | **PASS** — convention de frontière déclarée avant la taille ; précision ≤ demi-indifférence | N-A |
| C9 | puissance dans le plafond | **FAIL** (III.4) | **PASS** — MDE 0,668 / 0,110 ; garde-fou d'attrition rattaché à la coupure POSITIVE ; 0,09 h contre 8 h | N-A |
| C10 | denominator sans remplacement | — | **PASS** | N-A |
| C11 | lifecycle | — | **PASS** — six événements mappés sur cinq états, tous outcomes | N-A |
| C12 | provenance et ancrage | — | **PASS** — PRB-5 complété | N-A |
| C13 | faisabilité bornée | — | **PASS** — coût mesuré avec intervalle et facteur d'acquisition, plafond de stockage déclaré | N-A |
| C14 | pas de calibration sur familles fermées | — | **PASS** | N-A |
| | **Résultat** | **6 FAIL — inadmissible, rejetée définitivement** | **14 PASS — admissible** | **cas affirmatif échoué (§II.5)** |

`N-A` pour F, raison énoncée une fois : F n'enrôle aucune unité, ne mesure rien et n'exécute aucune
famille ; les gates régissent un design prospectif et n'ont pas d'objet. Son admissibilité se décide
par le test affirmatif du §II.5, qu'elle échoue : deux questions restent ouvertes et une famille bornée
et exécutable existe à 0,09 heure CPU.

### III.8 Décision terminale

Priorité de la Partie I §11, appliquée mécaniquement : G échoue → E passe les quatorze →

> ## `AXIS_FRAME_CLOSURE_01S_ROUTE_E_SELECTED`
>
> **`primary_route = "E"` · `backup_route = null` · Route G définitivement rejetée pour ce programme ·
> `scientific_run_authorized = false`**

`backup_route` est `null` parce que la Partie I §11 n'autorise G comme backup que si G passe les
quatorze gates, ce qu'elle ne fait pas, et parce que F n'est pas une route. `primary_route` n'est pas
`null`. F n'est pas sélectionnée par préférence : E passe.

**Ce qui a réellement été prouvé** (faits mécaniques, domaine testé) : l'équivariance exacte de l'update
et de son ledger sous transposition, aux tailles déclarées et aux lois de `A` ; l'imparité exacte de
`Q` et de `S` ; que `Q` n'est pas une fonction du masque ; que `sign(Q)` traverse zéro à l'intérieur de
l'horizon ; que le tracker n'est pas équivariant en présence d'un composant enroulant, et qu'il l'est en
son absence sur 1 280 séquences ; que `dt ≤ admissible_dt_limit` équivaut exactement à (B1) ∧ (B2) ; que
la loi des lois et la loi des CI sont normalisées et exactement échantillonnables ; et que `Q` est
recalculable à l'octet près sur l'évidence relue. **Rien de tout cela n'est un fait scientifique.**

**Ce qui reste seulement conçu** : le protocole de Route E dans son intégralité. Aucune famille, aucun
seed, aucun monde scientifique n'existe.

**Distance restante avant la première expérience scientifique** : la fermeture des six
`PRE_RUN_BLOCKER`, puis une prérégistration, puis une revue humaine autorisant l'exécution. Aucune
famille ne peut commencer avant.

**Limites de publication** : rien de publiable comme résultat scientifique. Publiable comme travail
d'ingénierie et de méthode : le pont de mesure, la fermeture du cadre, l'équivariance, et le rejet
motivé de Route G.

---

## Partie IV — RE-REVIEW CIBLÉE, LIMITATIONS DÉCLARÉES, DISPOSITION SCELLÉE

*Parties I–III inchangées. La Partie I reste un préfixe byte-exact de 23 901 octets.*

### IV.1 Verdicts de la re-review ciblée

Package soumis : Parties I + II + III, 86 031 octets, sha256
`d44609cc9365857ca41f3e21c30b5e05f32df35d28f1279f40004bc11096db36`, plus le fichier de test à 27 tests.

| Reviewer | Verdict | Findings restants |
|---|---|---|
| A | **PASS** | A15–A19, tous `MINOR_NON_BLOCKING` |
| B | **PASS** | B15–B19, tous `MINOR_NON_BLOCKING` |

**Aucun `PACKAGE_BLOCKER` ni `ROUTE_E_GATE_FAIL` ne survit.** Les deux reviewers ont revérifié
indépendamment : la préfixation byte-exacte (23 901 / 54 712 / 86 031), les six nouveaux faits
mécaniques, la suite complète (673 passés), et toute l'arithmétique de Route E — `n = 66` donne
0,125693 (échoue) et `n = 67` donne 0,124721 ; CP inférieure(42) = 0,50010 > 0,50 et CP inférieure(41)
= 0,48502 ; CP supérieure(9) = 0,23974 < 0,25 et CP supérieure(10) = 0,25740 ; type I 0,0249005 et
0,0159732 ; MDE 0,66760 et 0,110266. Tout reproduit.

Les deux confirment aussi que **le rejet de Route G est honnête et surdéterminé**, que refuser de
raccourcir les fenêtres est correct (ce serait caler un constant de design sur une sortie mécanique), et
que ne pas déclarer la capacité manquante de G comme `PRE_RUN_BLOCKER` est juste, la Partie I §15
exigeant une fermeture **bornée**.

### IV.2 Limitations déclarées

Conformément à la règle de mission — après la re-review ciblée, un défaut documentaire non porteur
devient une limitation, et il n'y a pas de troisième boucle — les dix findings restants sont déclarés
ici et ne sont pas corrigés.

| ID | Limitation |
|---|---|
| **A15** | La motivation de C2 pour G dit que l'instabilité est « purement numérique » et que `min\|Q\| = 1,41e-05` est « du même ordre » que la dérive 2,22e-16 : c'est faux de onze ordres de grandeur, et les croisements aux pas 774 et 820 sont des sauts de 0,021 et 0,101, donc **dynamiques**. La dérive numérique n'explique que la rupture de l'imparité inter-branches. Le libellé **sous-estime** le défaut ; le rejet de G tient sur cinq autres gates |
| **A16 / B16** | Deux seuils de Route E ne sont pas chiffrés : la fraction de censure et la concordance inter-CI. Ils ne gouvernent **pas** la décision `POSITIF/NÉGATIF/INDÉTERMINÉ` mais l'**attribution de cause** d'un nul, et les deux fractions concernées sont co-primaires obligatoires. De plus le repère de concordance proposé est biaisé au sens de Jensen vers « pas de dépendance aux CI ». **À chiffrer à la prérégistration** |
| **A17** | Le garde-fou d'inéligibilité est à 0,50, alors que la **décision** POSITIVE devient arithmétiquement inatteignable dès 25/67 = 0,3731. Non porteur : l'estimand est inconditionnel, les mondes inéligibles sont de vrais zéros, et la fraction est rapportée |
| **A18** | Les caractéristiques opératoires ne sont pas re-dérivées sous la règle d'invariance de `cohort_residual_fraction`. Par emboîtement monotone, le bras POSITIF teste `Δ` à `f = 0,01` et le bras NÉGATIF à `f = 0,20` ; l'arithmétique est inchangée, mais le plafond de claim doit dire de quel `Δ` il parle |
| **A19** | **Déviation déclarée de la Partie I §6.6.** Le §6.6 gelé impose l'enrôlement en paires `(x, Tx)` et l'unité « la paire ». Route E corrigée abandonne les deux. C'est imposé par les findings A3/A4, et le **but** du §6.6 — une loi de CI invariante sous `T` — est préservé : des entrées i.i.d. `U[0,1]` sont échangeables, donc invariantes en loi sous transposition. La déviation est enregistrée ici explicitement, comme la Partie I l'exige |
| **B15** | PRB-5 omet `run_owned_future_pipeline`. Non bloquant : il se termine dans deux fonctions déjà listées, donc les fermer le ferme transitivement. À nommer pour que le test de refus le couvre |
| **B17** | La taxonomie des causes d'un nul omet la rupture de track par la porte d'association (`max_centroid_displacement = 3,0` à `Δf = 16`) — le mécanisme même de `fact20`, applicable aussi aux composants non enroulants. Diagnosticable depuis la distribution co-primaire des cinq états terminaux, mais non préenregistré comme cause |
| **B18** | La clause d'éligibilité `masse > 0` est inerte : `ABSENT_MATTER = 0,1 < matter_threshold`, donc tout composant détecté a une masse strictement positive, et un composant dissous n'est pas rapporté du tout. L'outcome est inchangé — la dissolution est exclue par le mapping des états terminaux — mais la **justification** donnée est fausse |
| **B19** | Documentation non épinglée : la docstring du test scellé dit encore « aucun balayage de paramètres » et un seul flux pseudo-aléatoire (il y en a quatre) ; `fact16` imprime encore « NOT design values » pour `H`/`Δf` ; le facteur d'acquisition 1,52×, la recherche 3 840/179 et le plancher `L ≥ 16` (le raisonnement énoncé donne 12) n'ont pas de pin dans le package |

### IV.3 Disposition terminale scellée

> ## `AXIS_FRAME_CLOSURE_01S_ROUTE_E_SELECTED`
>
> **`primary_route = "E"` · `backup_route = null` · Route G rejetée définitivement pour ce programme ·
> Route F non sélectionnée · `scientific_run_authorized = false`**

`primary_route` n'est pas `null`. `backup_route` est `null` parce que la Partie I §11 n'ouvre un
emplacement de backup que dans la branche (1), où G serait primaire ; en branche (2) il n'y en a pas, et
F n'est pas une route. Aucune nouvelle mission de cadrage sur les mêmes inconnues n'est autorisée.

**Seule action suivante autorisée : la revue humaine de 01S.** Aucune prérégistration, aucune famille,
aucun seed, aucune exécution scientifique n'est autorisé ici, et aucun n'a eu lieu.
