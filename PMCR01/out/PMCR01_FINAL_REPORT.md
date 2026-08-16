# PMCR01 — atteignabilité exécutable d'un canal minoritaire `Y`
## Rapport final — après revue adverse et tour de réparation unique — zéro run scientifique

```
MISSION            PROSPECTIVE-MINORITY-CHANNEL-REACHABILITY-01
RÉPARATION         PMCR01-REVIEW-DRIVEN-Q-INSTRUMENTATION-REPAIR-01
PARENT             OBFOR01-CONFIRMATORY-PROVENANCE-AND-CLAIM-SEAL-01 (scellé)
BRANCHE            codex/prospective-minority-channel-reachability-01
BASE               f9d9b61 (le sommet scellé)

ORIGINAL_CANDIDATE_DISPOSITION  STOP__ARCHITECTURE_CHANGE_REQUIRED     (provenance)
REPAIRED_FINAL_DISPOSITION      EXISTING_ARCHITECTURE_WINDOW_NOT_YET_PROSPECTIVELY_LOCATED
ARCHITECTURE_CHANGE_NECESSITY   NOT_ESTABLISHED
EXISTING_Q_INSTRUMENTATION      CONFIRMED
SCIENTIFIC_RUNS                 0
REVUE_ADVERSE                   1 — 8 défauts confirmés (1 porteur), 9 attaques réfutées
TOUR_DE_RÉPARATION              1 (le seul autorisé)
```

---

## 1. Ce que la revue adverse a trouvé

La revue indépendante a mené onze axes d'attaque contre le résultat candidat. Neuf attaques ont
échoué et les revendications ont tenu : la fonction génératrice de descendance concorde à 1e-15
avec une énumération exhaustive ; `Q_max = 28` et `15504 = C(20,5)` se reproduisent
indépendamment ; l'invariant `CAP` tient sur les quatre décalages gelés ; la routine de survie
exacte concorde à 1,7e-11 près avec une récursion stable écrite séparément ; aucune borne issue
des **gates gelés** ne situe `E[Q]` (le mot `SY` n'apparaît **0 fois** dans le protocole gelé).

Mais un défaut **porteur** a été confirmé, et il renverse la conclusion.

## 2. Où `Q` est enregistré

La jambe porteuse du candidat affirmait que l'exposition environnementale

```
Q = nX · min(nSY, free)      à la cellule propre de l'organisateur
```

est « une propriété de la mesure réalisée » qu'il faudrait « mesurer sur le nuage ». C'est faux.
Le **chemin d'instrumentation** — distinct du chemin d'exécution du canal — la calcule et
l'enregistre :

```
ORR01/code/observe.py        (committé ; blob on-disk == blob HEAD)
  ligne 55 :  m  = nY > 0
  ligne 59 :  cy = np.minimum(nSY[m], free[m])
  ligne 69 :  "Q": float((nX[m] * cy).sum())
```

soit, **au bit près**, le `Q` de la dérivation d'opérateur de PMCR01. Champ d'indice **20** dans
`observe.Recorder.FIELDS`, aux côtés de `nSY_at_org`, `cand_Y_at_org` et `free_at_org`.
`protocol_obtc02.py` insère `/home/claude/ORR01/code` en tête de `sys.path` puis fait
`import observe as OBS` ; aucun `observe.py` n'existe dans `OBTC02/code`, donc l'import résout
vers ce fichier, qui est sur le chemin de production des données.

**Cause racine** : `pmcr01_channels.py` excluait `observe.py` de l'ensemble analysé. Ce fichier ne
définit aucun taux — il ne crée donc **aucun canal `Y`** — mais son omission a produit une
conclusion fausse sur la *mesurabilité*. L'audit sépare désormais explicitement
`CHANNEL_EXECUTION_PATH` et `MEASUREMENT_AND_INSTRUMENTATION_PATH`.

## 3. Combien de bras le contiennent — recalculé, non repris

Toutes les valeurs ci-dessous sont **recalculées** depuis les tableaux livrés. L'approximation du
réviseur (`E[Q] ≈ 3,17`) n'est utilisée nulle part ; elle s'avère être la valeur de la branche
**mobile** seule.

| grandeur | valeur |
|---|---|
| bras livrés | 28 |
| bras contenant `Q` | **28 / 28** |
| trames contenant `Q` | **308 000** (9 000 en fenêtre par bras) |
| valeurs manquantes (NaN) | **0** |
| allocation de branche reconstruite | **S = 14, M = 14**, préfixe de tag concordant |
| une seule cellule-organisateur dans **chaque** trame en fenêtre | oui |
| **branche STATIQUE** (n=14) — moyenne des moyennes par bras | **2,369048** (σ 0,130602) |
| étendue des moyennes par bras, statique | [2,0777 ; 2,5986] |
| **branche MOBILE** (n=14) — moyenne des moyennes par bras | **3,169730** (σ 0,162990) |
| étendue des moyennes par bras, mobile | [2,8726 ; 3,4299] |
| **ensemble complet** (n=28) | **2,769389** (σ 0,432681) |
| `P(Q = 0)` statique / mobile | 0,6470 / 0,5428 |
| maximum observé, groupé | **28** |

**Contrôle différentiel décisif** : le maximum observé (28) **égale exactement** le `Q_max` dérivé
indépendamment par énumération exhaustive des 15 504 états cellulaires admissibles sous
l'invariant d'occupation. Le champ enregistré et la quantité dérivée sont le **même objet**, pas
deux objets au nom voisin.

## 4. Pourquoi ces valeurs sont développementales et non confirmatoires

```
LES_28_BRAS = POST_OUTCOME_DEVELOPMENT_DIAGNOSTIC
```

Ces bras ont été exécutés et livrés **avant** l'ouverture de PMCR01, et **aucune borne sur `Q`
n'a été gelée avant leur exécution**. Ils sont donc :

- **admissibles** comme jeu de **découverte** et de conception d'une calibration ultérieure ;
- **inadmissibles** comme borne inférieure prospectivement gelée, et ils ne doivent jamais être
  présentés comme une preuve confirmatoire d'une fenêtre `kY`.

Les deux erreurs symétriques sont refusées. Il serait faux de dire que ces valeurs **prouvent**
déjà une borne transportable. Il serait tout aussi faux de les déclarer **scientifiquement
inertes** au seul motif qu'elles n'ont pas été préenregistrées : un jeu de découverte déclaré est
une pièce légitime pour concevoir une confirmation indépendante.

## 5. Pourquoi le changement d'architecture n'est plus établi

L'implication suivante est **invalide** et a été retirée :

> ~~`inf Q = 0` et `E[Q]` non connu en catégorie A, donc un changement d'architecture est
> requis.~~

Son antécédent porte sur ce que **cette mission** peut employer comme entrée porteuse sous ses
propres règles de preuve *ex ante*. Son conséquent est une affirmation sur ce que
l'**architecture** peut exprimer. Le second ne découle pas du premier — et il est réfuté par le
fait que l'architecture instrumente et enregistre déjà la quantité.

La hiérarchie exacte qui la remplace :

1. `inf Q = 0` ⇒ il n'existe **aucune borne inférieure uniforme état par état** sur `Q`.
   (Vérifié : 60,09 % des états admissibles ont `Q = 0`.)
2. `inf Q = 0` **n'implique pas** `E[Q] = 0`. L'infimum porte sur l'**ensemble** des états ;
   `E[Q]` porte sur la **mesure**.
3. `Q` est **déjà enregistré** par l'architecture existante (§2, §3).
4. Les valeurs `Q` des 28 bras existants **n'ont pas été désignées à l'avance** comme jeu de
   calibration confirmatoire.
5. **Donc** PMCR01 ne peut pas certifier une borne inférieure **prospective** en `kY` depuis ces
   valeurs, à l'intérieur de sa preuve zéro-run d'origine.
6. **Mais** l'incapacité de PMCR01 à certifier cette borne **n'établit pas** que l'architecture
   doive changer.
7. L'architecture existante peut suffire après **(A)** une dérivation développementale de borne
   `Q`, brute uniquement, sur les 28 bras existants et, **seulement si nécessaire**, **(B)** une
   calibration prospective de `Q` gelée indépendamment.

```
MEASUREMENT_AVAILABILITY            = CONFIRMED
PROSPECTIVE_BOUND_ALREADY_QUALIFIED = false
ARCHITECTURE_CHANGE_NECESSITY       = NOT_ESTABLISHED
EXISTING_CHANNEL_SUFFICIENCY        = UNRESOLVED
```

## 6. Les autres défauts confirmés, et leur réparation

| # | défaut confirmé | réparation |
|---|---|---|
| **F2** | `ROBUST_REGION_POSITIVE_WIDTH` — l'unique item décisif — était calculé sur les balayages de la branche **mobile seule**, alors que la justification se disait indépendante de la branche | remplacé par `PROSPECTIVELY_QUALIFIED_REGION_LOCATED`, calculé sur la question de transport, indépendante de la branche. Les deux branches sont rapportées **séparément**, avec une règle de portée explicite ; la contre-région statique non vide est **préservée** |
| **F3** | `NO_TARGET_DERIVED_INPUT` et `INDEPENDENCE_OR_ALIAS_STATUS_RESOLVED` étaient des littéraux `True` codés en dur — le mode d'échec même que le sceau parent s'était infligé et avait rétrogradé | chaque item porte désormais `source / calculation / observed_value / threshold_or_rule / result`. Le scan calculé a d'abord renvoyé `False` sur trois mentions de `r80` **en prose** ; le contrôle a été **corrigé** (AST, distinguant un accès de données d'une phrase) — et non le seuil relâché |
| **F4** | le contrôle d'admissibilité ne scannait que les nœuds `Assert`/`Raise`, dont les fichiers analysés contiennent **zéro** : vérité vide | remplacé par un audit des mécanismes qui bornent réellement — copie constructeur, clamp `min(1, ·)`, domaine de Bernoulli sur `muY`, court-circuits conditionnels, choix du manifeste, `p_hop_Y` dépendant de la branche, préservation de `CAP`, oracles de mutation. Un **contrôle positif de vacuité** contre `guard_obtc.py` (8 nœuds) prouve que le chercheur trouve les `raise` quand il y en a |
| **F5** | le déficit mobile de tête était `13,2×`, un coin de forme close | le **maximum exact** de survie sur l'ensemble faisable réel est publié : `4,537×10⁻⁶`, soit un facteur **110 213×**. La forme close est rétrogradée en illustration, étiquetée branche mobile |
| **F6** | « le branchement mono-`Y` surestime, donc les 87 points statiques sont une borne optimiste » — affirmé qualitativement ; `admissible_Q(CAP, nY)` n'était jamais appelé avec `nY ≠ 1` | `Q_max(nY)` publié : **28, 24, 21, 18, 15, 12, 10, 8, 6, 4, 3, 2, 1, 0** (nul dès `nY = 14`), et une chaîne de Markov exacte à 17 états respectant l'invariant d'occupation. Résultat : survie **0,9341**, `E[nY(T)] = 7,60` contre 0,894 et ≤ 10 sans contrainte. **La mitigation est retirée** : la correction est négligeable et la contre-région survit intacte |
| **F7** | « répondu négativement sur **trois** fondements indépendants » contredisait la structure réparée | réécrit : un seul fondement opérationnel, indépendant de la branche |
| **F8** | le témoin système de fichiers surveillait trois répertoires **choisis par la partie auditée**, dont un vide ; la sentinelle était par processus | les racines sont **découvertes** par glob (`/home/claude/*/raw`, `/home/claude/*/out`) — **29 racines** ; les `.npz` sont comptés par racine ; `NEW_PHYSICS_ARRAYS_WRITTEN` est publié ; la sentinelle est agrégée sur tous les processus |

**Laissé non réparé, avec raison** : `_diffuse`/`_react`/`_decay` ne sont toujours pas instrumentés
individuellement. Les instrumenter reviendrait à modifier, pendant l'audit, le chemin de code
audité. La lacune est fermée par deux moyens indépendants — un grep prouvant qu'aucun code PMCR01
n'appelle les opérateurs directement (l'unique correspondance, `pmcr01_map.py:21`, est dans une
docstring), et le témoin système de fichiers sur 29 racines avec
`NEW_PHYSICS_ARRAYS_WRITTEN = 0`. La garantie est **énoncée avec sa portée exacte** plutôt que
surévaluée.

## 7. Portée des branches, préservée dans les deux sens

```
STATIQUE (condition S, p_hop_Y = 0) : tau_séparation = ∞. Les descendants immobiles ne se
    séparent jamais. La région à source unique en (β, muY) est NON VIDE : 87 points,
    β ∈ [1,0×10⁻⁴ ; 4,0×10⁻⁴], muY ∈ [2,6×10⁻⁵ ; 2,1×10⁻⁴]. PRÉSERVÉE.
MOBILE  (condition M, p_hop_Y = p_hop_X) : tau_séparation = 125 pas. La région à source unique
    est VIDE, avec un déficit exact de 110 213×.
```

La persistance statique **ne prouve pas** la séparation mobile. La non-séparation statique **ne
prouve pas** l'impossibilité de persistance mobile. Les deux branches sont des conditions gelées
distinctes — le parent a exécuté 14 bras dans chacune — et ne sont jamais moyennées.

## 8. Ce que décidera la mission `Q` brute

`HANDOFF_MINORITY_Y_Q_BOUND_DERIVATION_01.md` (produit, **non exécuté**, zéro run) pose une
question unique : les trajectoires `Q` déjà enregistrées des 28 bras, traitées **explicitement**
comme jeu de développement, fournissent-elles un opérateur d'environnement rigoureux
**spécifique à la branche**, ou une borne conservatrice, suffisant pour cartographier la région
non vide `(β, muY)` en une région candidate exécutable `(kY, muY)` pour un test indépendant
ultérieur ?

Elle exige notamment : reconstruction exacte des 28 trajectoires ; analyses statique et mobile
séparées, la mobile étant porteuse pour la séparation ; **l'unité indépendante est le monde,
jamais la trame** ; analyse d'autocorrélation temporelle ; fréquence et durée des épisodes
`Q = 0` ; exposition de queue basse au niveau du monde ; traitement exact du clamp
`min(1, kY·nX·nY)` ; et la vérification explicite que `β = kY·E[Q]` **suffit**, ou que l'opérateur
complet conditionné au temps est requis.

Trois dispositions terminales seulement :

```
EXISTING_Q_DATA_SUPPORTS_DISCOVERY_DERIVED_EXECUTABLE_Y_REGION
EXISTING_Q_DATA_INSUFFICIENT__PROSPECTIVE_Q_CALIBRATION_REQUIRED
EXISTING_ENVIRONMENT_OPERATOR_STRUCTURALLY_PRECLUDES_WINDOW
```

Seule la troisième peut rouvrir la conception d'architecture, et uniquement si l'**opérateur** —
et non une simple incertitude large — démontre une impossibilité structurelle.

`HANDOFF_MINIMAL_Y_CHANNEL_ARCHITECTURE_DESIGN_01.md` est conservé comme pièce historique et
marqué `STATUS = SUPERSEDED_NOT_AUTHORIZED`, `SUPERSEDED_BY = MINORITY_Y_Q_BOUND_DERIVATION_01`.
Aucune espèce précurseur, production `Y` basale, pool conservé, survie dépendante de l'âge,
nouveau champ de manifeste ou contrôle `p_hop_Y` indépendant n'a été implémenté.

## 9. Vocabulaire terminal d'origine

```
ORIGINAL_TERMINAL_VOCABULARY_INCOMPLETE = true
```

L'ensemble gelé n'offrait que `REACHABLE_NONEMPTY_Y_WINDOW_DERIVED`,
`NO_MINIMAL_REACHABLE_Y_CHANNEL` et `STOP__ARCHITECTURE_CHANGE_REQUIRED`. L'état réel — canaux
atteignables, région non vide en `β`, transport vers `kY` pas encore qualifié prospectivement —
n'y a pas d'étiquette. Le forcer dans `STOP__ARCHITECTURE_CHANGE_REQUIRED` affirmait une
impossibilité architecturale que la preuve n'a jamais établie.

**Ceci est un affaiblissement imposé par un défaut confirmé, pas une revalorisation pilotée par le
résultat.**

## 10. Conformité zéro-run

```
ENGINE_CONSTRUCT_CALLS      = 0
ENGINE_ADVANCE_CALLS        = 0
SCIENTIFIC_WORLD_STARTS     = 0
SCIENTIFIC_SEEDS_OPENED     = 0
NEW_PHYSICS_ARRAYS_WRITTEN  = 0
racines de sortie surveillées = 29 (découvertes par glob, non choisies)
graines scientifiques dans les registres = 406 ; graines de fixture utilisées = 13, toutes ≥ 9 000 017
```

Agrégé sur tous les processus d'analyse. Toute construction reste dans un
`NON_SCIENTIFIC_SEMANTIC_FIXTURE` : `L = 3`, ≤ 8 pas **par fixture**, `seed_one_organiser` jamais
appelé (les trois points d'entrée sont instrumentés).

```
H3_STATUS = NOT_TESTED   REPRODUCTION_STATUS = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED   HISTORICAL_WINDOW_STATUS = NOT_PORTABLE
X_LAWSPEC_BASELINE = UNCHANGED   ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
SCIENTIFIC_RUNS_USED = 0   TOMMY_ACTION_REQUIRED = NONE
```
