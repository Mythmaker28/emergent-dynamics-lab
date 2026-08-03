# HUMAN REVIEW — FUTURE_PROSPECTIVE_AXIS_CONVENTION_AND_FRAME_CLOSURE_01S

> ## Disposition : `HUMAN_REVIEW_ACCEPTED`
>
> **Acceptant : `AXIS_FRAME_CLOSURE_01S_ROUTE_E_SELECTED`**
>
> `primary_route = "E"` · `backup_route = null` · `scientific_run_authorized = false` ·
> Route G **rejetée définitivement pour ce programme** · Route F **non sélectionnée**

Ce record est un acte de gouvernance. Il n'ajoute aucun fait mécanique, ne relance aucun test, ne
modifie pas le candidat et n'autorise aucune exécution scientifique. Il enregistre ce qui a été
vérifié, ce qui est accepté, ce qui est supersédé en formulation, et ce qui reste dû.

---

## 1. Candidat, lignée, autorité

| Élément | Valeur vérifiée |
|---|---|
| Branche | `codex/future-prospective-axis-convention-and-frame-closure-01s` |
| Candidat (SHA complet) | `63c371d52036c7e91ec928118c2b8901776d79d0` |
| Parent autorisé | `c2f6b0c4b47b39e26bb7b6a2800ad5760ef55c54` |
| Lignée interne 01S | `c2f6b0c4` → `b560909b9e88e8eb00a6d542ed731239e329573d` → `f340a123` → `63c371d5` |
| Nombre de parents par commit | **1** à chaque maillon — chaîne strictement linéaire, **aucun merge** |
| `main` | `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`, **immobile** avant et après ; `HEAD` = `refs/heads/main` |
| Branches antérieures | `…01r` = `cc551374`, `…01r-human-review` = `c2f6b0c4`, `…architecture-01` = `02f7405d` — **aucune déplacée** |
| Branche de revue humaine 01S | **absente** avant ce record |

Le parent `c2f6b0c4` porte `HUMAN_REVIEW_ACCEPTED` et son autorisation successeur exclusive est
littéralement `FUTURE_PROSPECTIVE_AXIS_CONVENTION_AND_FRAME_CLOSURE_01S`. Le candidat est donc
autorisé, et il l'est **seul**.

**Quatrième chemin technique.** Il n'a pas été deviné : il a été extrait littéralement du package
avant toute ouverture, depuis `…_01S_DECISION.json` → `mechanical_facts.test_file` =
`tests/test_axis_transpose_equivariance_01s.py`, puis ouvert par chemin Git exact.

---

## 2. Les onze contrôles

### Contrôle 1 — Autorité et lignée — **PASS**

Les cinq points sont vérifiés au tableau du §1 : parent porteur de `HUMAN_REVIEW_ACCEPTED`,
autorisation exclusive de 01S, existence et parent exact des quatre commits, chaîne linéaire sans
merge, candidat et branches antérieures non déplacés.

### Contrôle 2 — Ensemble des changements — **PASS**

Preuve **bidirectionnelle et constructive**, par reconstruction d'index sous `/tmp`, sans aucun
listing de répertoire :

- **Sens direct.** Index initialisé sur l'arbre du parent `c2f6b0c4`, puis les **quatre** chemins
  déclarés ajoutés un par un par `--cacheinfo`. `write-tree` produit
  `0d196f160450f7eb5a760aa41f544c48f0d6e2a8`, qui **est** `63c371d5^{tree}`.
- **Sens inverse.** Index initialisé sur l'arbre du candidat, les quatre chemins retirés par
  `--force-remove`. `write-tree` produit `f303d7949c2e9b1aa60c17b0c9ea331412c9ddc6`, qui **est**
  `c2f6b0c4^{tree}`.

Les deux sens ensemble prouvent que les quatre chemins expliquent **entièrement** la différence, et
qu'il n'existe **aucun** changement non déclaré, sans avoir énuméré l'arbre.

**Décompte réel A / M / D = 4 / 0 / 0.** Les quatre chemins sont **absents** chez le parent
(`cat-file -e` échoue sur chacun) : ce sont quatre ajouts, aucune modification, aucune suppression.

| Chemin | Nature | Octets | sha256 du contenu |
|---|---|---|---|
| `tests/test_axis_transpose_equivariance_01s.py` | **fichier technique 01S** | 72 939 | `5c0b02681a16211b87a88baeb9ccbc96793dc3530440f93ad5064e5313f480ab` |
| `docs/individuation/…_01S_REPORT.md` | document | 91 874 | `c9bdc2c0416631cee37078e5f2b422a68b821bf2b25ea0813e8e03cfed41cefb` |
| `docs/individuation/…_01S_DECISION.json` | document | 12 456 | (blob `2e208081…`) |
| `docs/individuation/…_01S_REVIEW_JOURNAL.md` | document | 9 092 | `14b4b212c117d4bad9debadde8e78759323562ba53be75af157a42df8f393200` |

Un seul fichier technique ; trois documents. **Aucune source précédemment acceptée n'a changé** :
les dix-huit chemins acceptés — moteur, instrumentation, lifecycle, runner, pipeline possédé, pont
de mesure 01R, les `__init__.py`, `specs.py`, `state.py`, `pyproject.toml`, les cinq fichiers de
tests acceptés et le fichier de tests du pont — sont **identiques** (même blob) entre parent et
candidat. **Le scellement n'a touché aucun test existant** : le seul fichier de tests présent est
le nouveau, et il est ajouté, non modifié.

### Contrôle 3 — Partie I gelée — **PASS**

`b560909b:…_01S_REPORT.md` fait **23 901 octets**, sha256
`096cd174213e9dec4a7518ac8e46426e3a59435aabf200712eee383f3770e5c6`. Les **23 901 premiers octets**
du rapport final (91 874 octets) ont **le même sha256**. La Partie I est donc un **préfixe
byte-exact**, sans une suppression ni une réécriture d'un seul octet.

Le checkpoint intermédiaire `f340a123` laisse le rapport **inchangé** et n'ajoute que le fichier de
tests : en retirant ce seul chemin de son arbre on retrouve `a8a817f38d81bf0602c4af56ed7330703f99837d`,
qui est `b560909b^{tree}`.

**Abandon de l'appariement déclaré additivement.** Le §6.6 gelé impose l'enrôlement en paires
`(x, Tx)` et « la paire » comme unité. Route E corrigée abandonne les deux. Cet abandon **n'est pas**
une réécriture de la Partie I : il est déclaré **par ajout**, en Partie IV, comme déviation A19, et
répliqué dans le JSON (`declared_part_I_deviation`). Le **but** du §6.6 — une loi de conditions
initiales invariante sous `T` — est préservé : des entrées i.i.d. `U[0,1]` sont échangeables, donc
invariantes en loi sous transposition. La déviation est **substantiellement correcte** et
**formellement déclarée**. C'est la bonne manière de dévier d'un gel.

### Contrôle 4 — Sélection E / G / F — **PASS**

Matrice reconstruite depuis `DECISION.json` (quatorze gates, binaire seulement) :

| Route | Résultat | Gates fatals | Admissible |
|---|---|---|---|
| **E** | **PASS** | **aucun** (0) | **oui** |
| G | **FAIL** | `C2, C3, C4, C5, C7, C9` — **six** | non |
| F | `N-A` sur les quatorze | — | décidée hors matrice |

- **E passe chaque gate** : zéro gate fatal ; C1 à C14 sont soit `PASS` soit sans objet, jamais
  `FAIL`.
- **G a bien six `FAIL` fatals**, et ce sont exactement les six énumérés dans
  `route_G_rejection_reasons`. Chacun est motivé au rapport §III.4.
- **F n'est pas sélectionnée parce qu'une route bornée existe.** Le rapport ne rejette pas F par
  préférence : il lui applique un **test affirmatif** (§II.5) — F doit démontrer sa propre valeur
  épistémique — et ce test échoue, parce que la consolidation n'apporte aucune information nouvelle
  sur les deux questions ouvertes alors qu'une famille bornée et exécutable existe. `route_F_selected
  = false`.
- **La matrice gelée impose E.** La priorité de la Partie I §11 est appliquée mécaniquement : G échoue,
  E passe → E est primaire et G est définitivement rejetée. `backup_route = null` parce que le §11
  n'ouvre un emplacement de backup que dans la branche où G serait primaire.
- **Aucun vote de reviewer ne remplace la règle.** Le journal §2 et §7 l'énoncent, et le fait le
  prouve : la décision préliminaire de l'auteur était `ROUTE_G_SELECTED` avec E en backup ; elle a
  été **renversée** par la matrice après review, et ce renversement est enregistré tel quel.
- **Aucune ancienne valeur retirée n'a été réintroduite.** L'ordre de dérivation (§II.2) est suivi
  du rang 1 au rang 10 et chaque constante est redérivée sur place : le plafond de calcul est un
  budget déclaré ; `𝓛 = {16,24,32}` vient d'un plancher géométrique ; `H = 1024` vient de
  64 échantillons × `Δf = 16` ; le plafond `θ̂_m + θ̂_n < 11,0904` est **recomputé ici** comme
  `2·ln(H/4) = 2·ln(256) = 11,090354888959125` ; les frontières viennent du principe déclaré du point
  milieu ; `n = 67` est une conséquence de la cible de précision. Les douze retraits `R1`–`R12` ne
  sont pas reformulés ailleurs dans le package.

### Contrôle 5 — Cadre probabiliste de Route E — **PASS, avec deux formulations supersédées**

| Exigence | Statut |
|---|---|
| Domaine exact `dt = m_max = n_max = 1` | **déclaré explicitement** comme choix d'unités, au rapport §III.5.2 et dans `route_E_design.scales` |
| Relation des neuf groupes sans dimension avec `LatticeBondSpec` | **établie** : à ces échelles, les neuf groupes **sont numériquement** les champs de `LatticeBondSpec` |
| Ensemble de lois borné, mesurable, fini, non vide | **oui** — voir la justification corrigée ci-dessous |
| Distribution conditionnelle uniforme exactement échantillonnable | **oui** — uniforme sur `A`, par rejet depuis la boîte, sans troncature ni pondération |
| Boîte de proposition et bornes explicitement déclarées | **oui** — taux `∈ [1/1024, 1/16]` ; `θ̂_m + θ̂_n < 11,0904` ; `ε̂_b ∈ [0,1]` (restriction de **portée déclarée**, R10) ; `λ ∈ [0,1]` |
| CI sur une boîte compacte normalisée | **oui** — `m[y,x] ~ U[0,1]` i.i.d., `n[y,x] ~ U[0,1]` i.i.d., `b ≡ 0` : produit de mesures uniformes, normalisé et exactement échantillonnable par construction |
| Tailles 16/24/32 avec probabilités préfixées | **oui** — tirage **uniforme**, donc `1/3` chacune, fixé avant tout tirage |
| Horizon 1 024, cadence 16 | **oui**, tous deux déclarés et dérivés au rang 3 et au rang 4 |
| Aucune calibration sur Stage B ou `M_MINUS` | **oui** — `stage_b_used = false`, `m_minus_used = false`, `tuning_against_mechanical_outcomes = false` |

**Formulation supersédée 5a — le taux 0,099.** Le rapport §II.1 (M9) et le tableau §III.5.2
l'invoquent comme fondement de « mesure finie > 0 ». Ce record le **supersède** : **0,099 est
uniquement l'efficacité estimée du sampler par rejet** (1 980 acceptations sur 20 000 propositions).
Ce n'est **pas** une constante de normalisation, **pas** une mesure de `A`, et **pas** un résultat
scientifique. Le package avait aussi proposé une « boule ouverte » comme fondement, mais il l'a
lui-même retirée (R12 : ce n'étaient que 18 points axiaux). Le fondement correct, qui n'a besoin
d'aucun nombre empirique, est enregistré ici :

> `A = Boîte ∩ {κ̂ < ¼·e^{−(θ̂_m+θ̂_n)/2}} ∩ {4D̂ + 2·ε̂_b·k̂_on < 1}`. Les deux contraintes sont des
> inégalités **strictes** portant sur des fonctions **continues** des neuf coordonnées : chacune
> définit un ouvert de `ℝ⁹`. Le point `κ̂ = D̂ = k̂_on = k̂_off = k̂_tens = 1/512`,
> `θ̂_m = θ̂_n = 1`, `ε̂_b = λ = 1/2` est **intérieur à la Boîte** et vérifie les deux contraintes
> strictement — `1/512 = 0,001953125 < ¼·e^{−1} = 0,091970` et `4/512 + 2·(1/2)·(1/512) =
> 0,009765625 < 1`. Par continuité, un voisinage ouvert de ce point est inclus dans `A`, donc
> `|A| > 0`. Et `A ⊆ Boîte` bornée, donc `|A| ≤ |Boîte| < ∞`. La loi uniforme sur `A` est donc une
> loi de probabilité propre, et le rejet depuis la Boîte l'échantillonne exactement.

Le taux 0,099 ne joue plus aucun rôle démonstratif : il ne sert qu'à dimensionner le coût du
tirage à la prérégistration.

**Formulation supersédée 5b — « équivaut exactement », « conséquence prouvée ».** Le package
qualifie de *prouvée* l'équivalence entre l'admissibilité moteur et `(B1) ∧ (B2)`, en s'appuyant sur
2 500 points avec zéro discordance. **2 500 points sont une validation mécanique, pas une preuve sur
un domaine continu.** Ce record fournit la dérivation algébrique manquante, à partir des **faits de
source déjà établis et acceptés** dans la lignée (01R, Partie I §4, confirmés indépendamment par la
revue humaine 01R) :

> Source : `affinity_span = θ_m·m_max + θ_n·n_max` ; `matter_dt_bound = 1/(4·κ_m·e^{affinity_span/2})`
> (`∞` si `κ_m = 0`) ; `resource_bond_dt_bound = 1/(4D + 2·ε_b·k_on/n_max)` (`∞` si ce taux est nul) ;
> `analytic_dt_bound = min(...)` ; `admissible_dt_limit = nextafter(analytic_dt_bound, 0)` ; et
> `LatticeBondSpec.__post_init__` lève `AdmissibilityError` si `dt > admissible_dt_limit`.
>
> Posons `dt = m_max = n_max = 1`. Alors `κ̂ = κ_m`, `D̂ = D`, `ε̂_b = ε_b`, `k̂_on = k_on`, et
> `affinity_span = θ̂_m + θ̂_n =: S`. Le spec est admissible ⇔ `1 ≤ admissible_dt_limit` ⇔
> `1 ≤ nextafter(b, 0)` où `b = analytic_dt_bound`. Comme `1` est exactement représentable et que
> `nextafter(b, 0)` est le plus grand flottant strictement inférieur à `b`, cette condition équivaut
> à **`1 < b`**, c'est-à-dire `1 < matter_dt_bound` **et** `1 < resource_bond_dt_bound`, soit
> `4·κ̂·e^{S/2} < 1` **et** `4D̂ + 2·ε̂_b·k̂_on < 1`, soit exactement
> **`κ̂ < ¼·e^{−S/2}` (B1) et `4D̂ + 2·ε̂_b·k̂_on < 1` (B2)**. ∎
>
> Les frontières du domaine sont couvertes : `κ_m = 0` donne `matter_dt_bound = ∞`, et (B1) est
> alors satisfaite puisque `0 < ¼e^{−S/2}` ; `4D + 2ε_b k_on = 0` donne
> `resource_bond_dt_bound = ∞`, et (B2) est alors satisfaite puisque `0 < 1`. Le `nextafter`
> transforme précisément un `≤` en `<`, ce qui est le sens strict des deux bornes.

**Bornage résiduel, et pourquoi il n'est pas matériel.** La dérivation est exacte en arithmétique
réelle. En IEEE-754 double, l'évaluation de `e^{S/2}` et des produits est arrondie, si bien qu'à
moins d'un ulp de la frontière le prédicat calculé et la borne calculée peuvent en principe
diverger. Cet ensemble est de mesure nulle sous la loi uniforme, et surtout **le moteur est
fail-closed** : tout `LatticeBondSpec` est validé à la construction et lève `AdmissibilityError` si
`dt > admissible_dt_limit`. Le sampler ne peut donc **pas** faire entrer silencieusement une loi
inadmissible dans un run ; le pire cas est une construction refusée. Le claim est en conséquence
borné ainsi, et une **obligation** est portée au §8 : à la prérégistration, le prédicat d'acceptation
du sampler doit **être** la construction du `LatticeBondSpec` par le moteur lui-même, de sorte que
l'ensemble échantillonné soit par définition exactement l'ensemble admis par le moteur, et que
l'écart d'un ulp disparaisse au lieu d'être estimé.

### Contrôle 6 — Unité statistique et règle des deux CI — **PASS** *(contrôle principal)*

**La règle réellement scellée** — lue au rapport §III.5.4, non inventée :

> « Pour le discriminateur de dépendance aux CI, **deux CI indépendantes par loi** sont tirées : la
> première sert le primaire, la seconde le discriminateur. »

La règle scellée **n'est donc pas conjonctive**. Elle est :

> **Y_i = 1{ D(loi_i, L_i, X_{i1}) = 1 }**, pour **i = 1, …, 67**, et **k = Σ_i Y_i**.

où `D` vaut 1 si et seulement si, dans le monde construit à partir de `(loi_i, L_i, X_{i1})`, **au
moins un composant éligible** satisfait la conjonction *persistance* (`RIGHT_CENSORED_AT_HORIZON`,
observé continûment jusqu'à `H = 1024`) **et** *remplacement matériel vérifié*
(`cohort_residual ≤ cohort_residual_fraction`).

- **`i = 1, …, 67`** — oui : `n_draws = 67` dans le JSON, `n = 67` partout dans le rapport, et toute
  l'arithmétique CP est faite à `n = 67`.
- **`k = Σ Y_i`** — oui : la règle de décision porte sur `k` avec les régions `k ≥ 42`, `k ≤ 9`,
  `10 ≤ k ≤ 41`.
- **Indépendance** — `loi_i` est tirée i.i.d. uniforme sur `A`, `L_i` i.i.d. uniforme sur `{16,24,32}`,
  `X_{i1}` i.i.d. selon la loi de CI, et les trois tirages sont indépendants. Le moteur étant
  **déterministe et sans RNG**, `Y_i` est une fonction déterministe de `(loi_i, L_i, X_{i1})`. Les
  `Y_i` sont donc i.i.d. Bernoulli(`Δ`) — exactement le modèle sous lequel Clopper–Pearson est exact.
- **Les 134 mondes ne sont jamais traités comme 134 réplications** — **vérifié, et c'est décisif.**
  Le package n'utilise **nulle part** 134 comme taille d'échantillon : `sample_size.n_draws = 67`,
  la règle de décision est `k ≥ 42` **sur 67**, les demi-largeurs `0,124721` (n = 67) et `0,125693`
  (n = 66) sont calculées à `n = 67` et `n = 66`, la famille de reproduction est `n₂ = 67`. **134**
  n'apparaît que comme **compte de mondes exécutés**, dans le calcul de coût (`134 mondes × 1024
  pas`) et dans `route_E_design.sample_size.worlds`. Il n'y a **aucune ambiguïté employant 134 comme
  nombre de réplications**, et donc **aucun rejet matériel** de ce chef.
- **Les deux CI ne deviennent pas deux unités statistiques** — la seconde CI n'entre **que** dans le
  discriminateur de dépendance aux CI (concordance intra-loi entre les deux CI, comparée au taux
  impliqué par l'indépendance), qui est une analyse **secondaire** d'attribution de cause et ne
  touche jamais `k`.
- **Aucun monde n'est remplacé** — la Partie I §9 gelée l'interdit littéralement : « Aucun
  remplacement, aucun retirage, aucun complément. Une unité qui échoue reste au dénominateur avec son
  outcome observé. »

**Portée de l'estimand, énoncée exactement.** `Δ` est la **probabilité marginale**, sous le produit
des trois lois déclarées, qu'**un tirage** produise un monde contenant au moins un composant éligible
satisfaisant la conjonction. Ce **n'est pas** « la fraction des lois dont la probabilité propre
dépasse un seuil », et le package ne le prétend nulle part : son plafond de claim (§III.5.6) énonce
« la conjonction … est instanciée par une proportion `Δ` des **tirages** … au niveau du tirage,
jamais de l'entité ».

**« Densité de réplication ».** C'est le **nom** de la route, pas un estimand. Le package n'emploie
**pas** l'expression « densité de lois reproductibles » (vérifié) et n'affirme rien au niveau de la
loi. Ce record fixe la lecture : *densité de réplication* signifie **la proportion de tirages
satisfaisant le critère binaire ci-dessus**, et rien de plus fort.

**Formulation supersédée 6a.** Le rapport §III.5.3 écrit « **Unité : le tirage** (un monde) » et le
§III.5.4 « **134 mondes** » ; le JSON écrit `unit = "the draw (one world)"` à côté de `worlds = 134`.
Lus isolément, ces deux fragments pourraient laisser croire à 134 unités. Ils sont **supersédés**
ici : **l'unité primaire est le triplet `(loi_i, L_i, X_{i1})`, il y en a 67, et les 67 mondes de
seconde CI ne sont pas des unités du primaire.** Le défaut est **de formulation seulement** — aucun
nombre, aucun intervalle, aucune règle du package n'en dépend — il est donc supersédé, non porté au
rejet, et le candidat n'est pas modifié.

### Contrôle 7 — Seuils binomiaux — **PASS (recomputé indépendamment)**

Recalculs faits ici, en arithmétique fermée, sans consommer aucune donnée du dépôt :

| Quantité | Recalcul | Package |
|---|---|---|
| CP bilatéral 95 %, borne **inférieure** à `k = 42`, `n = 67` | **0,5001047440198192** | 0,50010 |
| CP borne inférieure à `k = 41` | **0,4850181325667384** | 0,48502 |
| CP borne **supérieure** à `k = 9` | **0,2397417520625535** | 0,23974 |
| CP borne supérieure à `k = 10` | **0,2574024526077781** | 0,25740 |
| `P(K >= 42 given p = 0,50)` | **0,02490005714736432** | 0,0249005 |
| `P(K <= 9 given p = 0,25)` | **0,015973215853012406** | 0,0159732 |
| `p` donnant 80 % de puissance, bras POSITIF | **0,6675969** | 0,66760 |
| `p` donnant 80 % de puissance, bras NÉGATIF | **0,1102662** | 0,110266 |
| Puissance à `p = 0,70` / `p = 0,10` | **0,92277 / 0,87095** | 0,923 / 0,871 |
| Demi-largeur CP pire-cas, `n = 67` | **0,12472119532629714** | 0,124721 |
| Demi-largeur CP pire-cas, `n = 66` | **0,12569283054844493** | 0,125693 |

`0,124721 ≤ 0,125` et `0,125693 > 0,125` : **67 est bien la plus petite taille satisfaisant la cible
de précision**, et la cible elle-même — demi-largeur pire-cas ≤ **la moitié** de la largeur
d'indifférence `[0,25 ; 0,50]` — est déclarée **avant** le calcul de taille. La règle de décision est
donc exactement :

```text
POSITIF       k ≥ 42
NÉGATIF       k ≤ 9
INDÉTERMINÉ   10 ≤ k ≤ 41
```

**Vocabulaire corrigé.** Les valeurs `0,6676` et `0,1103` sont des **valeurs alternatives de `p`** à
80 % de puissance, et non des « effets minimaux détectables » au sens d'un écart : leurs **écarts aux
frontières** valent **+0,1676** (par rapport à `Δ₀ = 0,50`) et **−0,1397** (par rapport à
`Δ₁ = 0,25`). Le rapport les étiquette « MDE à 80 % : `Δ = 0,668` et `Δ = 0,110` », ce qui est
correct comme valeur de `p` mais ambigu comme « MDE » ; la lecture ci-dessus est celle qui fait foi.
Les caractéristiques opératoires restent une **conséquence** de la cible de précision, jamais sa
justification — le package le dit lui-même (`operating_characteristics.note`).

### Contrôle 8 — Tailles, RNG et denominator — **PASS, avec une obligation portée à la prérégistration**

- **Tailles avec poids préfixés** — `L ∈ {16,24,32}`, **tirage uniforme**, donc `1/3` chacune, fixé
  d'avance. L'estimand est en conséquence **marginal sur `L`**.
- **Aucune allocation fixe 22/22/23** — vérifié : elle n'apparaît nulle part dans le package. C'est
  correct, et il faut le dire explicitement : une allocation déterministe 22/22/23 **ne serait pas
  équivalente** au tirage i.i.d. si la probabilité de succès diffère entre tailles, car le
  dénominateur cesserait d'être un échantillon i.i.d. de la loi produit. Le package ne commet pas
  cette substitution.
- **Générateur externe, ordre des tirages, stratégie de seed** — le **versant négatif est fermé** ici
  et l'est correctement : le moteur ne contient **aucun RNG** et `LatticeBondSpec` n'a **aucun champ
  de seed**, donc une réplication n'est **jamais** un pseudo-seed mais **un nouveau tirage
  préenregistré de (loi, condition initiale, taille)** ; et le firewall interdit de créer ici le
  moindre seed (`scientific_seed_created = false`). Le **versant positif** — *quel* générateur
  externe, dans *quel* ordre, sous *quelle* stratégie de seed enregistrée — n'est **pas** spécifié
  dans le package, et **ne pouvait pas l'être** sans violer ce même firewall. Il est donc porté au
  §8 comme obligation nommée de la prérégistration. Ce n'est pas un écart matériel : c'est le bon
  emplacement de l'obligation.
- **Aucune substitution après enrôlement** — Partie I §9 gelée, littéralement : denominator fixé à
  l'enrôlement, aucun remplacement, aucun retirage, aucun complément.
- **Dispositions préfixées des événements concurrents** — le mapping des six événements sur les cinq
  états terminaux du contrat de cycle de vie accepté est explicite et **exhaustif** : dissolution →
  `DISSOLVED_DETECTED_TRACK` ; split → `SPLIT_INTO_TRACKS` ; merge → `MERGED_INTO_TRACK` ; perte et
  handoff non résolu → `UNRESOLVED_HANDOFF` ; survie à l'horizon (timeout) →
  `RIGHT_CENSORED_AT_HORIZON`. Les quatre premiers **valent 0** ; le cinquième est le **seul** état
  pouvant valoir 1, et seulement si le remplacement est aussi vérifié. **L'erreur** a sa propre
  disposition préfixée, distincte : une violation de contrat (schéma, calendrier, digest) est une
  **faute logicielle**, la famille est déclarée **famille échouée** et rapportée comme telle, jamais
  élaguée.
- **Aucun arrêt anticipé** — « Terminaison sur compte de mondes et horloge. **Aucune analyse
  intermédiaire.** » Il n'existe donc aucun mécanisme pouvant s'arrêter à `k = 42` ou `k ≤ 9`.

### Contrôle 9 — Rejet de Route G — **PASS**

Les six `FAIL` correspondent aux gates gelés `C2, C3, C4, C5, C7, C9`, et chacun des points exigés
est vérifié :

- **Origine des passages de signe.** Les croisements de `sign(Q)` aux pas **509, 774 et 820**
  proviennent d'une **fixture mécanique** — la fixture symétrique, à la loi par défaut, épinglée par
  `fact19` — et **non** d'un tirage scientifique. Le package le classe explicitement comme fait
  mécanique, valable pour son domaine testé, et jamais comme observation d'un phénomène.
- **Aucune fenêtre n'a été raccourcie après observation.** C'est le point de gouvernance le plus
  important du package et il est tenu : le rapport refuse explicitement de raccourcir les fenêtres
  pour restaurer le signal, parce que ce serait **caler un constant de design sur une sortie
  mécanique**, ce que le parent et la Partie I §16 interdisent. Le JSON le répète
  (`firewall.note`). Refuser de sauver sa propre route préférée par un ajustement de constante est
  le comportement correct, et il est enregistré comme tel.
- **Le bridge ne permet pas les interventions requises** — un seul plan d'intervention, appliqué à
  chaque pas, non retirable, non dépendant de l'état ; cohorte et tracks réinitialisés à chaque run.
- **Aucune opération autorisée n'égalise le champ de ressource** — d'où l'impossibilité de H6.
- **Falsificateur d'orientation vide par construction** (H1), donc incapable de soutenir G.
- **Test de forme sur une strate où `S ≡ 0`** (H2), donc incapable de se déclencher.
- **Séquence confirmatoire pseudo-répliquée** — H2, H4, H5, H6 siègent à `α = 0,05` sans unité, sans
  structure de dépendance, sans taille, sans puissance ; et l'argument « la paire compte pour une
  observation » repose sur une équivariance du tracker **fausse** dès qu'un composant enroule le tore.
- **Cinq seuils déterminant l'outcome restent sans valeur**, et la stratégie composite, prise à la
  lettre, rend `π ≡ 0`.
- **L'attrition peut fabriquer un négatif** — le garde-fou déclaré de G est sous la bande où
  l'attrition seule produit un `NÉGATIF` avec probabilité 0,92.

**Capacité manquante non déclarée `PRE_RUN_BLOCKER` — correct.** Un `PRE_RUN_BLOCKER` est par
définition une obligation **bornée**. L'ordonnancement d'interventions fenêtrées et dépendantes de
l'état plus la substitution de champ en cours de run est un **nouveau programme d'ingénierie**, non
borné : le déclarer blocker aurait été du maquillage de gate. Ne pas le faire est le choix rigoureux.

**Conclusion enregistrée.** *Route G est rejetée définitivement pour ce programme et pour ce cadre.*
Elle n'est **pas** scientifiquement réfutée. Ce qui est établi est qu'elle n'est **ni exécutable ni
mesurable** sur ce substrat avec ce contrat. **Ce record n'affirme pas — et interdit d'inférer — qu'une
convention axis-signée serait physiquement impossible dans tous les systèmes.** Ce qui survit et est
banqué : l'équivariance exacte de l'update et de son ledger sous transposition dans le domaine carré
périodique, aux tailles et aux lois déclarées ; `Q` n'est pas une fonction du masque ; l'algèbre
d'intervention locale existe ; et l'asymétrie du tracker est localisée et **contenue** par l'exclusion
des composants enroulants.

**Une limitation déclarée est reprise ici parce qu'elle touche la motivation de C2.** La limitation
**A15** établit que le libellé de C2 — instabilité « purement numérique », `min|Q| = 1,41e-05` « du
même ordre » que la dérive `2,22e-16` — est **faux de onze ordres de grandeur**, et que les
croisements aux pas 774 et 820 sont des sauts de 0,021 et 0,101, donc **dynamiques**. Ce record le
confirme et en tire la conséquence exacte : **le fait qui fait échouer C2 est le croisement de zéro à
l'intérieur de l'horizon**, et ce fait est intact — A15 le renforce plutôt qu'elle ne l'affaiblit,
puisqu'une instabilité dynamique est plus dommageable pour un endpoint de rétention de signe qu'une
dérive numérique. Seule l'**explication** donnée était erronée. Et le rejet de G tient de toute façon
sur cinq autres gates indépendants.

### Contrôle 10 — Preuves et reviews — **PASS**

Bindings vérifiés **sans relancer aucun test** :

| Élément | Valeur liée dans le package |
|---|---|
| Fichier de tests 01S | `tests/test_axis_transpose_equivariance_01s.py`, 72 939 octets, sha256 `5c0b0268…f480ab` |
| Tests 01S | **27** |
| Suite complète | **673 passés**, **0 échec**, **0 skip** |
| Environnement | Python 3.11.15, pytest 8.4.2, numpy 2.4.4 |

Le sha256 du fichier de tests déclaré dans `mechanical_facts` est **identique** à celui du blob
réellement présent dans l'arbre du candidat (contrôle 2) : le binding hash ↔ objet Git tient. Les
faits `fact01`–`fact24` sont nommés individuellement dans le rapport et rattachés aux findings qu'ils
réparent (`fact19` ← A1, `fact20`/`fact21` ← B1, `fact22`/`fact23` ← A5, `fact24` ← A12).

Faits mécaniques liés, et **aucun n'est un résultat scientifique** :

- `T² = id` sur l'état, l'intervention et le masque ; `T` agit trivialement sur la loi.
- `U(Tx, TI) = T·U(x, I)` à un pas et à 25 pas, sur les deux backends, avec et sans intervention,
  ledger compris ; résidus de **0,0 à 2,22e-16** ; et aussi **aux tailles déclarées 16/24/32 et à
  des lois tirées de `A`**.
- `Q` et `S` **exactement impairs** sous `T` ; `Q = 0` exactement sur les états invariants sous `T`.
- `Q` **n'est pas** une fonction du masque (masque identique, `Q = +0,625` et `−0,625`).
- `sign(Q)` **n'est pas** stable à l'horizon de design : croisements aux pas 509, 774, 820 ;
  imparité inter-branches en échec à **247 des 1 025** échantillons.
- Le tracker **n'est pas** équivariant sous transposition quand un composant enroule le tore :
  **179 des 3 840** séquences ; **contrôle positif : 1 280 séquences sans enroulement, 0 asymétrie**.
- Distributions **mécaniquement validées** : `(B1) ∧ (B2)` ⇔ admissibilité (2 500 points, 0
  discordance — validation, cf. contrôle 5b) ; loi de CI produit d'uniformes (1 680 validations,
  0 rejet, 210 `step` complets).
- `Q` est **recomputable à l'octet près** depuis l'évidence persistée puis relue.

Registre de review :

| Élément | Vérifié |
|---|---|
| Round 1 | **FAIL / FAIL** — A1–A14 (1 blocker, 6 G-fail, 3 E-fail, 5 mineurs) ; B1–B14 (1 blocker, 4 G-fail, 1 E-fail, 8 mineurs) |
| Re-review ciblée | **PASS / PASS** — A15–A19 et B15–B19, tous `MINOR_NON_BLOCKING` ; 0 `PACKAGE_BLOCKER` et 0 `ROUTE_E_GATE_FAIL` survivants |
| Findings | **38** (28 + 10), cohérent entre journal §6 et `DECISION.json.review` |
| Findings jugés invalides | **0** |
| Retraits | **12** (`R1`–`R12`) |
| Limitations déclarées | **10** |
| Boucles correctives | **une seule** ; pas de troisième boucle |
| Packages de review | round 1 : 54 712 o, sha256 `79e9a85f…` ; re-review : 86 031 o, sha256 `d44609cc…` ; les verdicts sont rendus contre ces états **et aucun autre** |

Deux corrections vont **contre** la position initiale de l'auteur (`R1`, `R2` détruisent le résultat
présenté comme décisif pour sa route préférée ; `R3` supprime un dispositif d'enrôlement qu'il avait
lui-même gelé), et la décision préliminaire `ROUTE_G_SELECTED` a été **renversée**. Ce sont les
marques d'une review qui mord.

### Contrôle 11 — Six `PRE_RUN_BLOCKER` et firewall — **PASS**

**Les six blockers, recopiés littéralement depuis `DECISION.json` :**

| ID | `obligation` | `closure` |
|---|---|---|
| **PRB-1** | persist the track-component join | write (frame, canonical cell-set digest, track_id) into root-bound evidence |
| **PRB-2** | mandatory receipt | the supported scientific entry point refuses without a verified receipt |
| **PRB-3** | frozen check order | pin by test: local evidence -> root digest -> verifier |
| **PRB-4** | replay binding | bind run identity and family enrolment into the root |
| **PRB-5** | single supported entry point | close or declare out of protocol, with a refusal test: `open_owned_analysis_access`, `future_lifecycle_runner.open_analysis_access`, `publish_future_family_completion`, `qualify_and_write_lifecycle_contract` (and, per B15, `run_owned_future_pipeline`) |
| **PRB-6** | external anchoring of the final root | public immutable or append-only commitment, verifiable without a secret |

Chacun est :

- **borné** — chaque `closure` nomme un artefact ou un test précis à produire, pas un programme
  ouvert ;
- **falsifiable** — chacun a un critère de vérification qu'un tiers peut exécuter : la jointure est
  présente ou absente de l'évidence liée à la racine ; le point d'entrée refuse ou ne refuse pas sans
  receipt ; l'ordre des checks est épinglé par un test ou ne l'est pas ; la liaison anti-replay est
  dans la racine ou non ; les cinq fonctions sont fermées ou déclarées hors protocole ; le
  commitment est publiquement vérifiable **sans secret** ou non ;
- **non présenté comme fermé** — aucun n'est marqué résolu, et PRB-5 est même **élargi** par la
  limitation B15 (`run_owned_future_pipeline` à nommer) plutôt que refermé ;
- **obligatoire avant prérégistration ou exécution** — la Partie I §15 le pose : « aucune famille
  scientifique ne peut commencer avant sa fermeture ».

Sur **PRB-6**, ce record réaffirme la correction d'ancrage établie à la revue humaine
`ARCHITECTURE_01` : *la publication peut exiger un credential d'authentification, tandis que la
vérification publique du commitment résultant ne dépend pas de ce secret. L'exigence scientifique est
un commitment immuable ou append-only vérifiable indépendamment, pas une publication sans
credential.* Le libellé du package (« vérifiable sans secret ») est conforme à cette lecture.

**La décision maintient `scientific_run_authorized = false`.** Aucune famille, aucune loi, aucune
condition initiale, aucun seed, aucun namespace, aucun des 67 tirages n'a été créé — et aucun ne peut
l'être avant la fermeture des six blockers, une prérégistration, et une revue humaine autorisant
l'exécution.

Firewall vérifié, valeur par valeur dans `DECISION.json.firewall` et par la conduite constatée du
package : chemins Git exacts uniquement ; **aucune donnée scientifique historique ouverte** ; Stage B
non utilisé ; `M_MINUS` non utilisé ; aucun seed scientifique créé ; aucun namespace prospectif
utilisé ; aucune famille prospective exécutée ; aucun balayage de paramètres exécuté ; aucun calage
sur une sortie mécanique. `main` **immobile**, épinglé avant et après à
`f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`. **Aucune densité de réplication n'est prétendue
observée** : le package n'énonce aucune valeur de `Δ`, et n'en énoncera aucune avant l'exécution.

---

## 3. Le claim accepté, énoncé exactement

Ce record accepte **une décision de conception**, et rien d'autre.

**Ce qui est accepté :**

> Dans le cadre déclaré — moteur `LatticeBondEngine`, lattices **carrées** de `𝓛 = {16, 24, 32}`,
> frontières **périodiques**, échelles `dt = m_max = n_max = 1`, loi uniforme sur
> `A = Boîte ∩ (B1) ∩ (B2)` avec `ε̂_b ≤ 1`, conditions initiales `m, n ~ U[0,1]` i.i.d. et `b ≡ 0`,
> horizon `H = 1024`, cadence `Δf = 16` — **Route E est une expérience prospective entièrement
> spécifiée, bornée, exécutable et falsifiable**, dont l'unité est le tirage
> `(loi_i, L_i, X_{i1})`, dont l'estimand `Δ` est la probabilité marginale qu'un tirage produise un
> monde où au moins un composant éligible est à la fois **persistant** et **matériellement remplacé
> de façon vérifiée**, dont la taille est `n = 67`, et dont la règle de décision est
> `POSITIF k ≥ 42` / `NÉGATIF k ≤ 9` / `INDÉTERMINÉ` sinon.
>
> Et : **Route G est définitivement rejetée pour ce programme**, sur six gates fatals, comme
> non exécutable et non mesurable sur ce substrat avec ce contrat — **pas** comme physiquement
> impossible.

**Ce qui n'est pas accepté, parce que ce n'est pas revendiqué :** aucune valeur de `Δ`, aucune
observation, aucun résultat scientifique. **Aucune famille n'a été exécutée.** Les faits mécaniques
du package sont des propriétés du logiciel sur fixtures fabriquées, valables pour leur domaine testé,
et jamais des observations d'un phénomène.

**Plafond de claim, maintenu tel que scellé :** un succès complet de Route E établirait au plus la
proportion `Δ` **au niveau du tirage**, jamais au niveau de l'entité. C'est **en deçà du barreau 3**
de l'échelle d'individuation : Route E ne mesure aucune variable d'état. Elle n'établirait rien sur
l'adressabilité, rien sur l'ownership, rien sur une convention, et rien hors du cadre déclaré.

---

## 4. Formulations supersédées dans ce record

Aucune n'est porteuse ; aucune ne modifie le candidat ; aucune n'ouvre une nouvelle boucle
documentaire. Elles sont supersédées ici, une fois, et cette lecture fait foi.

| # | Formulation du package | Lecture qui fait foi |
|---|---|---|
| **S1** | « Unité : le tirage (un monde) » à côté de « 134 mondes » ; `unit` + `worlds = 134` dans le JSON | L'unité primaire est `(loi_i, L_i, X_{i1})` ; **il y en a 67** ; les 67 mondes de seconde CI servent **uniquement** le discriminateur et ne sont **pas** des unités du primaire |
| **S2** | « mesure finie > 0 (taux d'acceptation 0,099) » | **0,099 = efficacité estimée du sampler par rejet, rien d'autre.** La mesure de `A` est strictement positive par ouverture et point intérieur exhibé, et finie parce que `A ⊆ Boîte` bornée |
| **S3** | « équivaut exactement », « conséquence prouvée » pour `(B1) ∧ (B2)` ⇔ admissibilité | **2 500 points = validation mécanique.** La **preuve** est la dérivation algébrique du contrôle 5b, frontières incluses ; le claim est borné par la validation fail-closed du moteur |
| **S4** | « MDE à 80 % : `Δ = 0,668` et `Δ = 0,110` » | Ce sont des **valeurs alternatives de `p`** (0,6676 et 0,1103) ; les **écarts** aux frontières valent **+0,1676** et **−0,1397** |
| **S5** | C2 : instabilité « purement numérique », `1,41e-05` « du même ordre » que `2,22e-16` | Faux de onze ordres de grandeur (limitation A15 du package). **Le fait qui fait échouer C2 — le croisement de zéro dans l'horizon — est intact et renforcé** ; seule l'explication était erronée ; C2 est de toute façon surdéterminé par cinq autres gates |

---

## 5. Limites enregistrées

Les **dix limitations déclarées** au rapport §IV.2 sont acceptées **comme limitations** et ne sont
pas corrigées, la mission n'autorisant pas de troisième boucle. Celles qui portent une obligation
future sont reprises au §8. Résumé :

- **A15** — libellé de C2 sous-estimant le défaut (cf. S5).
- **A16 / B16** — deux seuils de Route E ne sont pas chiffrés : la fraction de censure et la
  concordance inter-CI. Ils ne gouvernent **pas** la décision ternaire mais l'**attribution de cause**
  d'un nul ; le repère de concordance proposé est biaisé au sens de Jensen vers « pas de dépendance
  aux CI ». **À chiffrer à la prérégistration.**
- **A17** — le garde-fou d'inéligibilité est à 0,50 alors que la décision POSITIVE devient
  arithmétiquement inatteignable dès `25/67 = 0,373134…`. Non porteur : l'estimand est
  inconditionnel, les mondes inéligibles sont de vrais zéros, et la fraction est co-primaire.
- **A18** — les caractéristiques opératoires ne sont pas re-dérivées sous la règle d'invariance de
  `cohort_residual_fraction` ; par emboîtement monotone le bras POSITIF teste `Δ` à `f = 0,01` et le
  bras NÉGATIF à `f = 0,20`. L'arithmétique est inchangée, mais **le plafond de claim doit dire de
  quel `Δ` il parle**.
- **A19** — déviation déclarée de la Partie I §6.6 (cf. contrôle 3).
- **B15** — PRB-5 omet `run_owned_future_pipeline` ; à nommer pour que le test de refus le couvre.
- **B17** — la taxonomie des causes d'un nul omet la rupture de track par la porte d'association
  (`max_centroid_displacement = 3,0` à `Δf = 16`) — le mécanisme même de `fact20`, applicable aussi
  aux composants **non** enroulants. Diagnosticable depuis la distribution co-primaire des cinq états
  terminaux, mais **non préenregistré comme cause**.
- **B18** — la clause d'éligibilité `masse > 0` est **inerte** ; l'outcome est inchangé mais la
  justification donnée est fausse.
- **B19** — documentation non épinglée dans le fichier de tests scellé.

Limites supplémentaires enregistrées par cette revue :

- **L-HR1.** L'équivalence `(B1) ∧ (B2)` ⇔ admissibilité est exacte en arithmétique réelle ; en
  IEEE-754, un désaccord d'un ulp au voisinage de la frontière n'est pas exclu. Non porteur parce que
  le moteur est fail-closed, mais **à supprimer** par la construction prescrite au §8.
- **L-HR2.** Le générateur externe, l'ordre des tirages et la stratégie de seed ne sont pas
  spécifiés — correctement, puisque le firewall l'interdisait ici. **Obligation portée au §8.**
- **L-HR3.** Le bloc `deliverables` du JSON n'énumère que `REPORT.md` et `REVIEW_JOURNAL.md` ; le
  fichier de tests et le `DECISION.json` lui-même n'y figurent pas. Sans conséquence : le fichier de
  tests est lié par `mechanical_facts` avec ses octets et son sha256, et les deux bindings ont été
  vérifiés contre l'arbre Git.

---

## 6. Route F — non sélectionnée

`route_F_selected = false`. F n'est pas écartée par préférence ni par défaut : le package lui applique
un **test affirmatif** — F doit démontrer sa propre valeur épistémique — et F échoue ce test, parce
que la consolidation n'apporte aucune information nouvelle sur les deux questions ouvertes alors
qu'une famille bornée et exécutable existe, à un coût de l'ordre de 0,09 heure CPU. La matrice des
quatorze gates est `N-A` pour F : ces gates régulent une conception prospective et n'ont pas d'objet
pour une route qui n'enrôle aucune unité, ne mesure aucune quantité et n'exécute aucune famille. F est
donc décidée **hors matrice, par son propre test affirmatif**, ce qui est la manière correcte de la
traiter et non un contournement.

---

## 7. Ce que la sélection de E signifie — et ce qu'elle ne signifie pas

Sélectionner Route E signifie que, pour la première fois dans ce programme, **nous savons quelle
expérience il serait honnête de lancer**. Le cadre est fermé : la population de lois est une vraie
loi de probabilité, sur un domaine explicitement borné ; les conditions initiales ont une loi
déclarée ; les tailles, l'horizon et la cadence sont fixés d'avance ; l'unité, le dénominateur et
l'outcome binaire sont définis avant tout tirage ; la taille d'échantillon découle d'une cible de
précision posée **avant** de calculer la puissance ; et les trois issues `POSITIF`, `NÉGATIF`,
`INDÉTERMINÉ` sont non vides et fixées à l'avance, de sorte qu'aucun résultat ne pourra être
réinterprété après coup.

**Cela ne signifie pas que nous connaissons déjà le résultat.** `Δ` est inconnue. L'expérience peut
revenir `POSITIF`, `NÉGATIF` ou `INDÉTERMINÉ`, et les trois sont des issues légitimes et publiables
en méthode. C'est précisément la valeur de ce travail : la règle est écrite **avant** de connaître la
réponse, donc la réponse comptera quelle qu'elle soit.

Et Route G, qui était la route préférée de l'auteur, a été abandonnée pour ce programme **parce
qu'elle n'est pas mesurable ici**, et non parce qu'elle serait fausse. Refuser de raccourcir une
fenêtre pour sauver un signal est ce qui rend le reste croyable.

---

## 8. Prochaine mission autorisée

**Autorisée, et seule autorisée :**

> ### `FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00`

**Contradiction avec le JSON : aucune.** `DECISION.json` porte
`preregistration_mission_named = "ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00"` **et**
`preregistration_authorised_here = false` : il nomme la **prérégistration ultérieure**, il ne
l'autorise pas, et il ne prescrit **aucun** identifiant pour la mission de fermeture des blockers.
`next_action_authorised` y vaut « HUMAN REVIEW — …_01S », c'est-à-dire **cette revue**, qui est
maintenant faite. Il n'y a donc pas d'identifiant divergent à signaler : les deux missions
coexistent dans l'ordre `fermeture des blockers → revue humaine → prérégistration → revue humaine →
exécution`.

`FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00` **pourra** fermer les six `PRE_RUN_BLOCKER`. Elle **ne
pourra pas** :

- changer la distribution ou l'estimand ;
- changer `67`, `134`, les seuils `k ≥ 42` / `k ≤ 9`, `𝓛 = {16,24,32}`, `H = 1024` ou `Δf = 16` ;
- rouvrir Route G ;
- créer les tirages ;
- lancer une famille ;
- commencer la prérégistration.

**Obligations portées à la prérégistration** (`ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00`), à
n'exécuter qu'après fermeture **et** revue humaine des blockers :

1. **Chiffrer les deux seuils non chiffrés** (A16 / B16) : fraction de censure et concordance
   inter-CI, avec un repère non biaisé au sens de Jensen.
2. **Nommer le générateur externe, l'ordre des tirages et la stratégie de seed enregistrée**
   (L-HR2), sachant que le moteur n'a aucun RNG et qu'une réplication est un nouveau tirage
   préenregistré, jamais un pseudo-seed.
3. **Faire du prédicat d'acceptation du sampler la construction du `LatticeBondSpec` par le moteur
   lui-même** (L-HR1), afin que l'ensemble échantillonné soit par définition exactement l'ensemble
   admis, et que l'écart d'un ulp à la frontière disparaisse.
4. **Préenregistrer la rupture de track par la porte d'association comme cause d'un nul** (B17).
5. **Dire de quel `Δ` parle le plafond de claim** sous la règle d'invariance de
   `cohort_residual_fraction` (A18).
6. **Nommer `run_owned_future_pipeline` dans le test de refus** de PRB-5 (B15).

Aucune de ces six obligations n'autorise à modifier la distribution, l'estimand, la taille ou les
seuils.

---

## 9. Firewall et remote de cette revue

**Firewall de la revue, tenu.** Chemins Git exacts uniquement (`cat-file -e`, `show`, `rev-parse`).
**Aucun** listing de répertoire, **aucun** glob, **aucun** wildcard, **aucun** `ls-tree -r`, **aucun**
`find`, **aucun** `rg --files`, **aucun** grep large, **aucun** parcours de `results/`, **aucune**
recherche mémoire globale. Stage B, `M_MINUS`, Kovacs, shards, mondes, trajectoires, candidats,
checkpoints et données du premier papier : **non ouverts**. Moteur, tracker, pont, tests, mutations,
expériences : **non exécutés**. Les seuls calculs indépendants faits ici sont **binomiaux fermés**
(Clopper–Pearson, queues binomiales, puissance, demi-largeur pire-cas) et deux vérifications
arithmétiques élémentaires — `2·ln(256)` et le point témoin du contrôle 5a — qui ne consomment
aucune donnée du dépôt.

L'inspection a commencé par `…_01R_HUMAN_REVIEW.md`, puis a ouvert les trois documents 01S et le
quatrième chemin technique **extrait littéralement du package avant ouverture**. La preuve de
l'ensemble des changements a été faite par reconstruction d'index sous `/tmp`, précisément pour
n'avoir à énumérer aucun arbre.

**Candidat non modifié.** Aucun test corrigé, aucune expérience réexécutée, aucune mission
scientifique commencée. **Un seul fichier est ajouté par ce record** — celui-ci — sur une branche
dont l'unique parent est le candidat.

**Résidu non supprimable, redivulgué.** Le montage de travail est en création seule : `rm` y renvoie
`EPERM`. Subsistent donc, sans effet sur l'arbre committé ni sur aucun objet référencé, un fichier
sonde `.opr00_probe_delete_me` (6 octets) et des fichiers temporaires `.git/objects/*/tmp_obj_*`.

**Remote.** Une tentative de push **normale**, unique, de la seule branche de décision. Aucun
`--force`, aucun changement de credentials, aucun retry automatique. Si elle échoue, l'échec est
enregistré, la référence locale est préservée intacte, et la commande de push sûre est rapportée pour
exécution manuelle.

---

## 10. Disposition

> ## `HUMAN_REVIEW_ACCEPTED`
>
> **Acceptant : `AXIS_FRAME_CLOSURE_01S_ROUTE_E_SELECTED`**
>
> Les onze conditions passent. Cinq formulations sont supersédées au §4 ; aucune n'est porteuse ;
> le candidat n'est pas modifié.
>
> `primary_route = "E"` · `backup_route = null` · `scientific_run_authorized = false` ·
> `route_G_status = REJECTED_DEFINITIVELY_FOR_THIS_PROGRAMME` · `route_F_selected = false`
>
> Prochaine mission autorisée, et seule autorisée : **`FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00`**.
