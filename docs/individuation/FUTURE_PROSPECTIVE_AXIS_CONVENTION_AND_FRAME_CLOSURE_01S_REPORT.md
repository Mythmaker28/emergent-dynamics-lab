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
