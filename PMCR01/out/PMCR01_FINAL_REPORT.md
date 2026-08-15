# PMCR01 — atteignabilité exécutable d'un canal minoritaire `Y`
## Rapport final — zéro run scientifique

```
MISSION            PROSPECTIVE-MINORITY-CHANNEL-REACHABILITY-01
PARENT             OBFOR01-CONFIRMATORY-PROVENANCE-AND-CLAIM-SEAL-01 (scellé)
BRANCHE            codex/prospective-minority-channel-reachability-01
BASE               f9d9b61 (le sommet scellé)
FINAL_DISPOSITION  STOP__ARCHITECTURE_CHANGE_REQUIRED
SCIENTIFIC_RUNS    0
REVUE_ADVERSE      1 (obligatoire) — 6 défauts confirmés
TOUR_DE_RÉPARATION 1 (le seul autorisé) — appliqué, voir §8
```

Rien n'a été affirmé sur la foi d'un nom de paramètre. Chaque canal est prouvé par un oracle de
mutation déterministe ; chaque nombre est calculé exactement ; aucun moteur scientifique n'a été
démarré. **Y compris les affirmations de ce rapport** : la revue adverse obligatoire a trouvé six
défauts confirmés dans une première rédaction, et §8 en rend compte sans les lisser.

---

## 1. Liaison au parent scellé

Les valeurs machine du sceau sont lues depuis l'arbre committé, jamais de mémoire :

```
FINAL_SEAL_DISPOSITION       = CONDITIONAL_FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED
ORIGINAL_ZERO_RUN_COMPLIANCE = NOT_DETERMINABLE_FROM_THE_DELIVERED_EVIDENCE
FRESH_SUBSTUDY_PROSPECTIVITY = PASS
PREDICTION_MODE              = CONDITIONAL
NEXT_SCIENTIFIC_ELIGIBILITY  = PROSPECTIVE_MINORITY_CHANNEL_REACHABILITY_01
OBFOR01_FINAL_TIP            = 55e8812…
SEAL01_FINAL_TIP             = f9d9b61…
```

Le handoff de contrôle est **vérifié par empreinte** contre `SEAL01_SHA256SUMS`
(`94487834badff2eb…`). La branche part exactement du sommet scellé. `GATE = PROCEED`.

Le mode `CONDITIONAL` du parent est porté **verbatim** : PMCR01 ne peut traiter aucune trajectoire
réalisée ni aucun flux mesuré comme une entrée connue avant un run futur. Cette contrainte devient
décisive en §6.

## 2. Sentinelle de démarrage moteur

Installée **avant** tout import de code projet. Elle instrumente `kinetics.World.__init__`,
`_one_step` et les trois points d'entrée de `seed_one_organiser`, et classe chaque appel contre un
prédicat explicite. Sur **tous** les processus d'analyse :

```
ENGINE_CONSTRUCT_CALLS   = 0
ENGINE_ADVANCE_CALLS     = 0
SCIENTIFIC_WORLD_STARTS  = 0
SCIENTIFIC_SEEDS_OPENED  = 0
```

Toute construction se fait dans un `NON_SCIENTIFIC_SEMANTIC_FIXTURE` : `L = 3`, graines dans le
bloc ≥ 9 000 000, ≤ 8 pas **par fixture** (plafond par-fixture, pas seulement global),
`seed_one_organiser` jamais appelé, état posé à la main. Témoin indépendant : le **système de
fichiers** — aucun `.npz` écrit dans `OBFOR01/raw`, `OBTC02/raw`, `OBDI02/raw` pendant l'analyse.

## 3. Gate 0 — les canaux `Y` exécutables

Découverte statique sur les **blobs committés** : toute écriture sur `self.n[espèce]`, y compris
celles dont l'espèce est une variable de boucle — c'est là que vivent la naissance et la mort de
`Y`. Huit canaux cartographiés. Aucun `assert` ni `raise` de la chaîne exécutable ne refuse une
valeur non nulle de `kY` ou `muY`.

| canal | classe | oracle |
|---|---|---|
| `kY` — naissance `Y` (`_react_core`, `('Y','SY',kY)`) | **DORMANT_BUT_REACHABLE** | PASS |
| `muY` — mort `Y` (`_decay_core`, `('Y','WY',muY)`) | **DORMANT_BUT_REACHABLE** | PASS |
| `p_hop_Y` — transport `Y` (`_diffuse('Y', p_hop_Y)`) | **PARTIALLY_WIRED** | PASS (transport) |
| appartenance de `Y` au pool d'échange (`exchangeable=`) | DORMANT_BUT_REACHABLE (polarité inverse) | non exécuté |
| `organiser_off_at` — intervention déclarée | ACTIVE_EXISTING (intervention) | s.o. |
| `S0`, `phi` — substrat/échange (partagés SX/SY) | ALIASED_OR_NOT_INDEPENDENT | s.o. |
| `omega` — sortie de déchet | **SCHEMA_ONLY_INERT** (prouvé) | inerte |
| précurseur `Y` local / mort dépendante de l'âge | **ABSENT_REQUIRES_ARCHITECTURE_CHANGE** | s.o. |

**Oracles de mutation, déterministes par construction.** Le générateur du monde est enveloppé pour
capturer chaque couple `(n, p)` que l'ordonnanceur passe à `binomial` **au point d'usage**, et le
paramètre perturbé est poussé à une valeur qui rend l'événement déterministe :

```
kY      0 -> 1 : p capturé 0 -> 1 ; ΔY 0 -> +4 = min(nSY, free) exactement ; réversion bit-exacte
muY     0 -> 1 : p capturé 0 -> 1 ; ΔY 0 -> -1 ; réversion bit-exacte
p_hop_Y 0 -> 1 : p capturé 0 -> 0.25 ; compte conservé ; l'ensemble des configurations change
```

`kY` et `muY` sont copiés **verbatim** du manifeste par `spec_for`. L'isolement du côté `X` est
testé **par position d'appel** (branche `X` de `_react`/`_decay` inchangée dans le même pas), et
non par « tout ce qui précède la première différence » — cette dernière était vide par
construction et a été corrigée (§8).

**Trois faits qu'une lecture par le nom aurait manqués :**

1. **`p_hop_Y` n'est pas un champ du manifeste.** `spec_for` l'expose à **deux valeurs
   seulement** : `0` en condition S (statique) et `p_hop_X` en condition M (mobile). Ce n'est
   **pas** un alias général — `0 ≠ p_hop_X` — mais ce n'est pas non plus une horloge de
   séparation `Y` continûment réglable. *Le parent a utilisé les deux : 14 bras frais en S, 14 en
   M.*
2. **`omega` est inerte** sous `LAWSPEC_V2_EXCHANGE` : `_feed_and_outflow` retourne aussitôt après
   `_exchange`, qui ne lit jamais `omega`. Prouvé par empreinte d'état.
3. **`Y` n'est dans aucun pool d'échange** par défaut. Le chémostat ne peut jamais retirer un `Y`.
   (L'ajouter au pool est un canal de retrait légal **sans changement de code**, mais de polarité
   inverse : il tuerait `Y` le plus vite dans la cellule-source encombrée, là où la lignée doit
   persister.)

## 4. L'opérateur discret exact `K_Y`

Loi de descendance d'un `Y` en un pas, **écrite depuis le code** puis **vérifiée argument par
argument** contre l'ordonnanceur (concordance totale) :

```
f(z) = (m + (1−m) z) · (1 − p (1−m) (1−z))^c
c = min(nSY, free)        p = min(1, kY · nX · nY)        m = muY
R = E[descendance] = (1 − muY) · (1 + c p)
```

Les nouveau-nés sont exposés à la décroissance **dès leur pas de naissance**, car `_decay` suit
`_react` dans l'ordre gelé. `Q_max = 28` par énumération exhaustive des **15 504** états
cellulaires admissibles sous l'invariant d'occupation `Σ espèces ≤ CAP = 16` ; atteint en
`nX = 7, nSY = 4, free = 4`. **`Q = 0` est admissible dans 60,1 % des états** : l'infimum de `Q`
sur l'ensemble admissible est **0**.

Opérateur **CONDITIONAL_EXACT** ; densité marginale **NOT_CLOSED** — même diagnostic structurel
que le parent a posé pour `X`, redérivé ici. Constantes du noyau retrouvées :
`a = 2q(1−q) = 0.05`, `D = q(1−q) = 0.025`, `D_rel = 0.05`, concordantes avec le manifeste gelé.

## 5. Les quatre propositions, distinguées

```
ABSTRACT_INTERVAL_EXISTS       = OUI     (algèbre pure, explicatif)
EXECUTABLE_CHANNEL_EXISTS      = OUI     (oracles kY, muY)
PARAMETER_IS_REACHABLE         = OUI     (LawSpec seul, aucun refus de code)
ROBUST_NONEMPTY_REGION_EXISTS  = NON     (le point décisif — §6)
```

## 6. Les trois régions et la raison porteuse

**Région A (abstraite).** `Q·kY > muY/(1−muY)` : non vide, explicatif seulement.

**Région B (exécutable).** La borne **supérieure** en `kY` est certifiable sans aucun run
(`β ≤ Q_max·kY = 28 kY`). La borne **inférieure** ne l'est pas : `inf Q = 0`. Ensemble **unilatéral**, donc pas une fenêtre.

**Région C (robuste), la raison PORTEUSE — indépendante de la branche.**

> L'intensité de naissance minoritaire est `β = kY · E[Q]`, avec `Q = nX · min(nSY, free)` **à la
> cellule propre de l'organisateur**. La borne supérieure se transporte au contrôle
> (`kY ≤ β_max/28 ≈ 1,42×10⁻⁵`). La borne **inférieure** ne se transporte pas : comme `inf Q = 0`,
> aucun `kY` fini ne garantit `β ≥ β_min`. Or `E[Q]` est une propriété de la **mesure du nuage
> réalisé**, pas de la LawSpec — c'est exactement `MARGINAL_DENSITY_CLOSURE = NOT_CLOSED`, la
> raison même pour laquelle le parent a dû **mesurer** sa loi de flux et pour laquelle sa
> prédiction est CONDITIONNELLE. PMCR01 s'interdit une telle mesure de catégorie B comme entrée
> porteuse ; il ne peut donc pas situer le bord inférieur de la fenêtre `(kY, muY)`. La condition 2
> de la région robuste exige de dépasser la frontière de persistance **avec marge numérique** ;
> une marge est un nombre, et ce nombre n'existe pas en catégorie A.

Les bornes prédéclarées gelées ont été **essayées honnêtement**
(`mean_free_at_organiser_min = 0,5`, `mean_births_per_step_min = 0,1`, `N_X_min = 20`) : elles
établissent `E[Q] > 0` mais ne le **situent** pas — la chaîne s'arrête parce que `SY` à la cellule
de l'organisateur n'apparaît dans aucun gate gelé. Le réviseur adverse est parvenu à la même
impasse.

**Deux observations subsidiaires, conditionnelles à la branche, rapportées et NON porteuses :**

- *Branche mobile (condition M).* La région à source unique est **vide** aux 25 599 points de
  grille, pour `c ∈ {1,4,7}`. Forme close, sans grille :
  `survie ≤ ln(N*)·τ_sep/(T·ln(1/γ)) = 0,0379` contre `0,50` requis — court d'un facteur 13. La
  cause est le **collapse d'échelle** : `muY` doit être à la fois grand (tuer les nouveau-nés
  avant séparation) et petit (laisser persister la lignée). Une horloge, deux rôles.
- *Branche statique (condition S, `p_hop_Y = 0`) — contre-région, rapportée ouvertement.* Les
  nouveau-nés immobiles ne se séparent jamais (`τ_sep = ∞`), donc la contrainte de source unique
  est satisfaite trivialement : la région à source unique en `(β, muY)` **n'est pas vide** (87
  points, `β ∈ [1,0×10⁻⁴ ; 4,0×10⁻⁴]`, `muY ∈ [2,6×10⁻⁵ ; 2,1×10⁻⁴]`). **Cela ne renverse pas la
  disposition** : l'axe reste `β = kY·E[Q]`, `inf Q = 0`, donc le bord inférieur en `kY` reste
  non-certifiable (la raison porteuse, indépendante de la branche). De plus le branchement mono-`Y`
  **surestime** la croissance ici, car tous les `Y` partagent une cellule ; les 87 points sont une
  borne optimiste.

## 7. Portes d'indépendance et collapse d'échelle

```
Y_BIRTH_CONTROL_IS_ACTIVE                        = OUI
Y_DEATH_OR_SURVIVAL_CONTROL_IS_ACTIVE            = OUI
CONTROLS_ARE_NOT_ALIASES (kY vs muY)             = OUI
CONTROLS_DO_NOT_ONLY_RESCALE_X                   = PARTIEL (p_X saturé ; un 2e Y ajoute une source)
PARAMETER_VALUES_ARE_ADMISSIBLE                  = OUI
OPERATOR_IS_IDENTIFIABLE_FROM_EXECUTABLE_SEMANTICS = NON (environnement endogène)
ROBUST_REGION_HAS_POSITIVE_WIDTH                 = NON
```

**Saturation `X`.** `p_X = min(1, kX·nX·nY) = 1` exactement à `kX = 1,0` dès que `nX·nY ≥ 1`
(vérifié contre l'ordonnanceur). Un organisateur sature déjà la source ; « minorité en nombre » et
« minorité en rôle causal » se dissocient. Vrai dans les deux branches.

**Collapse d'échelle.** `τ_newborn_removal ≡ τ_Y_removal` : `_decay` tire `Binomial(n_Y, muY)` sur
tout le champ `Y`, sans lire âge, position ni lignée. Différent du collapse `X` d'OBTR01 : ici
c'est l'horloge de retrait **partagée entre deux rôles**, non deux formules partageant un
paramètre. Fatal en branche mobile ; dissous en branche statique (où l'échec est celui, porteur,
de la borne inférieure).

## 8. Revue adverse obligatoire et tour de réparation

La revue adverse exigée a été menée contre cette rédaction, sur instruction de réfuter. Elle a
rendu **six défauts confirmés**, un partiellement confirmé, et une série d'attaques réfutées. Le
tour de réparation unique autorisé a été appliqué intégralement ; chaque nombre de réparation est
recalculé par le code, jamais repris de la prose de la revue.

| # | défaut confirmé | correction |
|---|---|---|
| 1 | `p_hop_Y` décrit comme « aliasé » à `p_hop_X` — faux : il vaut **0** en condition S, que le parent a utilisée pour 14 bras. Leg 1 (région vide) était énoncé sans le restreindre à la branche mobile. | `p_hop_Y` reclassé **PARTIALLY_WIRED** {0, p_hop_X} ; Leg 1 restreint à la branche mobile ; **contre-région statique** calculée et rapportée (§6) ; disposition re-fondée sur la seule raison indépendante de la branche |
| 2 | l'oracle d'alias ne testait que `immobile=False` | teste désormais les deux branches ; valeurs atteignables `{0, p_hop_X}` |
| 3 | témoin 3 (isolement `X`) vide par construction | comparaison des arguments `binomial` de la branche `X` **par position d'appel** |
| 4 | « témoin indépendant » `guard_obtc` = compteur mémoire jamais peuplé | remplacé par un **témoin système de fichiers** (npz écrits avant/après) ; `guard_obtc` rétrogradé en contrôle faible étiqueté |
| 5 | Gate 0 « exhaustif » ne couvrait pas les liaisons d'argument (`exchangeable`, `insert_mode`) | canal du pool d'échange ajouté ; exhaustivité **scopée à la liaison gelée** `protocol_obtc02.py:79-81` |
| 6 | comptabilité sentinelle partielle ; plafond de pas par-fixture non appliqué ; `seed_one_organiser` de `lawspec_v2` non patché | sentinelle unifiée sur tous les processus ; plafond par-fixture appliqué ; troisième point d'entrée patché |
| 7 | citation « handoff §3.5 » fabriquée pour le cadre de division | corrigée : les trois identifiants viennent du **launcher §7**, non du handoff ; attribution rectifiée |
| (aussi) | liste de conditions publiée ≠ conditions évaluées | alignées sur `C1…C6` ; condition « `nY << CAP` » explicitée |

**Attaques réfutées et consignées :** la loi de descendance et `R` sont correctes ; `Q_max = 28`
et l'invariant `CAP` tiennent (revérifiés indépendamment) ; `p_X = 1` à `kX = 1` ; la forme close
concorde à 7 % avec l'itération exacte de la pgf et ne décide rien que l'exact contredise ;
`NO_MINIMAL_REACHABLE_Y_CHANNEL` correctement refusée (les oracles établissent `kY`, `muY` vivants).

**Verdict du réviseur, retenu :** `STOP__ARCHITECTURE_CHANGE_REQUIRED` est la bonne étiquette des
trois, mais elle doit reposer sur **la seule raison indépendante de la branche** (borne inférieure
non-certifiable), les deux arguments de branche mobile et la contre-région statique étant rapportés
sans être des piliers. C'est la structure de ce rapport après réparation.

## 9. Disposition terminale et frontière d'architecture

Sur les dix exigences de la disposition positive, neuf sont remplies ; seule
`ROBUST_REGION_POSITIVE_WIDTH` échoue.

```
FINAL_DISPOSITION = STOP__ARCHITECTURE_CHANGE_REQUIRED
```

Ni `REACHABLE_NONEMPTY_Y_WINDOW_DERIVED` (la région ne se transporte pas au contrôle `kY`), ni
`NO_MINIMAL_REACHABLE_Y_CHANNEL` (faux : `kY` et `muY` passent les oracles).

**Capacité minimale manquante (évaluée, NON implémentée) :** une **espèce précurseur `Y` locale,
finie, conservée**, liée à l'organisateur, avec son propre taux de reconstitution `rho`. Elle vise
le blocage porteur : un pool plein borne l'intensité de naissance `Y` **par le bas via une quantité
de LawSpec** (taille du pool, `rho`) au lieu du `E[Q]` non-situable. Nouveaux modes d'échec
recensés : nouvel état absorbant (pool vide ∧ `nY=1`) ; compétition avec SX/SY pour `CAP`, donc
perturbation de la ligne de base `X` — précisément ce que la mission interdit de bouger ; si le
pool est reconstitué par le chémostat, `rho` s'aliase à `phi`/`S0` et le degré de liberté
s'évapore. **Aucun code écrit.** Écarté explicitement : membrane, génome, couche de saturation,
« nouvelles mémoires » — aucun n'est impliqué par un blocage trouvé ici.

```
H3_STATUS = NOT_TESTED   REPRODUCTION_STATUS = NOT_TESTED
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED   HISTORICAL_WINDOW_STATUS = NOT_PORTABLE
X_LAWSPEC_BASELINE = UNCHANGED   SCIENTIFIC_RUNS_USED = 0   TOMMY_ACTION_REQUIRED = NONE
```
