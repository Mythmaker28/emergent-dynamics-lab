# ORGANIZER-BOUND-TIMESCALE-REDERIVATION-01 — rapport final

**Branche** `codex/organizer-bound-timescale-rederivation-01` · **base** `ad8f6bfb` (OBDCA01)
**Runs scientifiques utilisés : 0** · **`OBTR01_METHODS_CORE_HASH` = `86855fd1b480552fac4130d0019777d5563041f32b9c985f3e4ba4c06a01afc3`**
**Disposition : `ORIGINAL_WINDOW_NOT_PORTABLE`**

---

## 1. Ce que la mission devait faire

Redériver, dans le LawSpec effectivement qualifié — `BALANCED_CHEMOSTAT`, `NO_ADDED_COHESION`,
`NO_C3_PROTECTION`, `ORGANIZER_BOUND_SOURCE` — les échelles temporelles du nuage dissipatif lié
à l'organisateur : formation, relaxation, suivi de la source, renouvellement, disparition et
premier passage ; puis déterminer si une expérience future de « fenêtre de minorité » est
**analytiquement éligible**. La mission ne devait **pas** tester la fenêtre elle-même comme
résultat scientifique, et `|C−Y|` ne devait apparaître dans **aucun** outcome primaire.

## 2. Ce qu'elle a trouvé, en une phrase

La fenêtre historique n'échoue pas au point qualifié : **le mécanisme qu'elle contraint n'y
existe pas**, `k_Y = 0` et `µ_Y = 0` exactement ; et les échelles temporelles du nuage, une fois
redérivées, se révèlent être **une seule échelle** — sept des huit sont des multiples rationnels
fixes de `1/µ_X`.

## 3. Provenance, hors ligne

`provenance_obtr01.py` rejoué sous `unshare -rn`, sans réseau : `READBACK_STATUS =
SELF_CONTAINED_SPLIT_DELIVERY_PASS`. Neuf commits portés, 1687 fichiers, arbre
`2a74bbd8…`, `fsck` propre, zéro objet manquant, aucun paquet promisor, aucune récupération
implicite. Trajectoires brutes livrées : `OBTC02` 17, `OBDI01` 16, `OBDI02` 138, `CSC01` 28,
`MCM01` 8. Le manifeste de gel décrit bien le code livré et le LawSpec est identique à celui de
la livraison parente.

## 4. Le répertoire MTW01 est absent du dépôt — et a pourtant été récupéré

La question temporelle historique appartient à `MINCORE-TIMESCALE-WINDOW-01`, dont **aucun
répertoire n'existe dans le dépôt livré**. Elle n'y survit que par empreinte, citée dans
`MCM01/out/MCM01_APPEND_ONLY_CORRECTIONS.md` §C-2.

Cette empreinte est un **engagement antérieur** : elle a été gelée dans le dépôt avant cette
mission. Un fichier trouvé hors dépôt qui la reproduit **bit pour bit** ne peut donc pas avoir
été fabriqué pour l'occasion.

| vérification | résultat |
|---|---|
| `MTW01/out/_window.json` | `3a1b7ae50a6ea82730d7b33f15aeacca31c457a3ae6b77483b71895964216342` — préfixe et suffixe exactement ceux de C-2 |
| tête du paquet `MTW01_gen2_branch.bundle` | `85ba2d8892b82e2d0060b1b174b63fc1b950b43f`, le commit que C-2 **et** `MCM01_FINAL_REPORT.md` nomment tous deux |
| manifeste `MTW01_SHA256SUMS` | **20/20 vérifiés**, 0 divergent, 0 absent |
| recopie sous `OBTR01/verify/mtw01/` | 19 fichiers, 0 empreinte modifiée après copie |

`STATUS = HISTORICAL_ARTEFACTS_RECOVERED_AND_DIGEST_VERIFIED`. **Usage admissible borné à
dessein** : ces fichiers reconstruisent la *question* historique (§5, §13). Ils ne fournissent
aucun seuil, aucune marge, aucune prédiction et aucune disposition de cette mission.

## 5. La déviation d'adjudication d'OBDI02, close en append-only

Le mandat en fait une condition d'arrêt et non une formalité : la note n'est autorisée que si la
déviation n'a touché **ni les données, ni le gate, ni le gel, ni les trajectoires**. Les quatre
points ont été **vérifiés**, pas supposés.

| catégorie | ce qui a été vérifié | verdict |
|---|---|---|
| **Gel** | les 16 fichiers de `METHODS_CORE` re-hachés depuis leurs octets ; `METHODS_CORE_HASH` recalculé par la construction lue dans `freeze_obdi02.py` | 16/16 identiques ; reproduit `59b19169…d525f1b` — **UNTOUCHED** |
| **Trajectoires** | autorité d'empreinte = les identifiants de blob git de la branche livrée, recalculés depuis les octets | 138/138, 0 modifié ; 138 graines déclarées = 138 présentes, aucune en double — **UNTOUCHED** |
| **Gate** | règle de qualification gelée ré-évaluée ; les trois exigences de validité technique réévaluées sur les 138 bras | 0 bras en échec ; 138/138 bras planifiés exécutés — **UNTOUCHED** |
| **Données** | estimand primaire recalculé indépendamment par OBDCA01 contre la valeur enregistrée par OBDI02 | `β = 0.082194877633092259` **identique au bit près**, test gelé à 0,25 : **PASS** — **LABEL_ONLY** |

Aucune catégorie bloquante. La mission ne s'arrête donc pas à `INHERITED_EVIDENCE_NOT_CLOSED`.

## 6. La cause était structurelle, pas un seuil déplacé

Le protocole gelé d'OBDI02 énumère neuf dispositions admissibles et **ne gèle aucune règle** qui
associe le vecteur d'issues à l'une d'elles. C'est ce vide, et non un seuil déplacé, qui a
laissé un fichier post-run de rang 7 choisir l'étiquette. Comme `0,042 < 0,25`, la condition
ajoutée était **strictement plus forte** : elle ne pouvait que *retenir* une qualification, pas
en accorder une.

```
OBDI02_POSTRUN_ADJUDICATION_DEVIATION = CONFIRMED
DEVIATION_DIRECTION                   = CONSERVATIVE_FALSE_NONQUALIFICATION
FROZEN_EVIDENCE_STATUS                = UNAFFECTED
CUMULATIVE_CLOUD_EVIDENCE_STATUS      = VALID
OBDCA01_FORMAL_LIMITATION             = QUALIFICATION_SUPPORTED_DESPITE_RECORDED_POSTRUN_ADJUDICATION_DEVIATION
```

## 7. La question historique, reconstruite

> Existe-t-il une bande non vide de taux de naissance de l'**organisateur** `R_Y` dans laquelle
> un organisateur se divise en deux à l'intérieur de l'horizon, tandis qu'un **troisième**
> n'apparaît pas avant que les deux existants se soient séparés de `Δ = 2 L_C` ?

Deux inégalités : `a_Y < R_Y` en bas, `R_Y < min(H3max/(2·safety·τ_sep), D_Y (a_X/R_X)^(2/d))`
en haut ; plus une condition de non-vacuité `2·safety·a_Y·τ_sep/H3max < 1`. C'est une condition
de **faisabilité de design**, pas une affirmation sur le système.

## 8. Table de portabilité des symboles

Vingt-et-un symboles, étiquetés par une règle énoncée une fois et non au cas par cas.

| étiquette | nombre |
|---|---|
| `INVALID_IN_QUALIFIED_LAWSPEC` | **8** |
| `OBSOLETE` | 5 |
| `PORTABLE_AFTER_REDERIVATION` | 7 |
| `PORTABLE_UNCHANGED` | 1 |
| `UNRESOLVED` | **0** |

Les huit invalides — `R_Y`, `γ_Y`, `a_Y`, `τ_sep`, `T_div`, `H3max` et les **deux** bornes de la
fenêtre — tombent ensemble et pour une seule raison : `k_Y = 0` et `µ_Y = 0` exactement, donc
aucun canal `X + Y → 2Y` et aucune mort d'organisateur. L'organisateur est une particule unique
et conservée pendant tout le run. **Ce zéro est structurel, pas petit.**

## 9. Correction C1 — la constante de diffusion

`D = p_hop/4` est remplacé par `D_eff = q(1−q)`, `q = p_hop/4`, parce que les quatre passes
séquentielles laissent une molécule bouger puis revenir dans le même pas. La correction est une
**identité exacte** : `D_eff/D_hist − 1 = −q`. À `q = 0,05` cela fait −5 % et à `q = 0,25`
−25 %, soit exactement les deux chiffres enregistrés. Au point qualifié `D_eff = 0,025`
exactement, et l'ancienne valeur surestime de +2,633 %.

## 10. Correction C2 — le premier passage, par voie discrète

`1519` et `190` ne sont pas des temps : ce sont les deux évaluations du membre de gauche de la
condition de non-vacuité, sous deux conventions.

```
τ = Δ²/D_Y            →  1518,5955
τ = Δ²/(8·D_Y)        →   189,8244        rapport 8,000000 (à 1e-12)
avec D_eff corrigé    →   180,4234
valeur de l'artefact gelé  189,8244316206  → reproduite à 1e-9
```

Le facteur 8 se décompose : **4** parce que le temps de sortie moyen d'un disque de rayon Δ vaut
`Δ²/(4D)` et non `Δ²/D`, et **2** parce que l'objet qui se sépare est la coordonnée relative de
deux organisateurs, de constante `D_rel = 2 D_Y`.

## 11. Une limitation nouvelle, trouvée en faisant le calcul discret

Le mandat exigeait le passage par une **équation de Poisson discrète**, `(I − P)T = 1` sur les
sites intérieurs du disque avec le noyau relatif exact, sans jamais substituer la loi continue
qu'on prétend tester. Résultat :

| rayon | sites | discret | continu `Δ²/(4D_rel)` | rapport |
|---|---|---|---|---|
| 5 | 81 | 34,728 | 28,571 | **1,21546** |
| 10 | 317 | 125,929 | 114,286 | 1,10188 |
| 20 | 1257 | 478,484 | 457,143 | 1,04668 |
| 40 | 5025 | 1870,551 | 1828,571 | 1,02296 |

L'excès décroît comme `rayon^(−1,082)` : c'est une couche limite de réseau, la marche
dépassant la frontière absorbante d'environ un pas. **Au rayon de design Δ = 5, la loi continue
sous-estime le vrai temps de sortie sur réseau de 21,5 %.** Le facteur 8 est juste ; la loi vers
laquelle il corrige n'est elle-même exacte qu'à `O(1/Δ)`, ce qui à Δ = 5 n'est pas négligeable.
Consigné comme limitation nouvelle, non comme correction du facteur enregistré.

## 12. Correction C3 — `Q_max`

Les deux espaces ont été énumérés exhaustivement, pour montrer la correction plutôt que
l'affirmer :

- sous la restriction **non fondée** `n_SY ≤ S0` : `Q_max = 27` à `(n_X 9, n_SY 3, free 3)` ;
- sur l'espace de capacité complet : `Q_max = **28**` à `(n_X 7, n_SY 4, free 4)`, l'argmax
  enregistré, depuis 3876 vecteurs d'occupation, et reproduit par une seconde route
  indépendante.

La restriction est non fondée parce que `_diffuse` s'applique aussi à `SY` et n'est bornée que
par la capacité libre de la destination, pas par `S0` : les unités de ressource peuvent
s'accumuler au-dessus de `S0`.

## 13. Correction C4 — la criticité scalaire n'a pas de référent ici

`_react` tire `births ~ Binomial(min(n_SX, free), min(1, k_X n_X n_Y))`. À `k_X = 1`, la
probabilité vaut **exactement 1** dès que la cellule de l'organisateur contient au moins un X et
un Y : le nombre de naissances est alors `min(n_SX, free)` et **ne dépend pas de `n_X`**. Un
rapport de branchement par particule n'a donc pas de référent, et `c_X·G(0) > 1` n'est ni
nécessaire ni suffisant.

Second motif : `G(0)` n'est pas un nombre unique. Sur la marche relative il vaut **9,6472**, sur
la marche X seule **16,7975**, un rapport de **1,741** au point qualifié. Un critère qui bouge
autant selon un choix de modélisation ne peut pas porter une décision primaire.

`SCALAR_CRITICALITY_STATUS = NOT_VALID_AS_PRIMARY_CRITICALITY`.

## 14. Correction C5 — la source est additive, pas multiplicative

Conséquence directe : `SOURCE_CLASSIFICATION = ADDITIVE_POINT_SOURCE_UNDER_A_BALANCED_CHEMOSTAT`,
bilan `N_X(t+1) = N_X(t) + B_t − Binomial(N_X(t), µ_X)` et population stationnaire
`N_X* = E[B]/µ_X`, **et non** `c_X/µ_X`. `E[B]` est une propriété de l'apport local du
chémostat : elle se **mesure**, elle ne se prédit pas.

## 15. Ce que fait réellement le moteur, lu verbatim

```python
for shift, ax in ((1,0), (-1,0), (1,1), (-1,1)):        # ordre gelé
    movers   = rng.binomial(max(n, 0), p_hop/4)
    dest_free = roll(self.free(), -shift, axis=ax)
    accepted  = min(movers, max(dest_free, 0))
    self.n[s] = n - accepted + roll(accepted, shift, axis=ax)
```

Trois conséquences que la convention historique manquait : (i) une molécule qui part en +y à la
passe 1 peut revenir en −y à la passe 2, donc le déplacement par axe est une **différence** de
deux Bernoulli(q) ; (ii) les passes 3 et 4 agissent après les passes 1 et 2, donc la loi a un
**support diagonal** et se factorise ; (iii) l'acceptation est une troncature de **lot par
cellule**, pas un amincissement par particule — elle ne peut donc pas être absorbée dans un `q`
effectif.

## 16. Les noyaux, validés des sept façons exigées

| test | résultat |
|---|---|
| énumération | forme close = force brute sur les 2⁴ tirages, à 1e-15 |
| masse unité | `1,000000000000000` |
| implémentation indépendante | accord à la précision machine avec `source_operator.py`, gelé dans OBTC02 **avant** cette mission, sur `a_X`, `D_X` et `a_rel`, dans les deux régimes |
| Monte-Carlo moteur | 4000 tirages d'une molécule unique en mode TEST — aucun start, aucune écriture au registre : variation totale **0,00263** contre 1 σ par case **0,00791** |
| moments | variance par axe `0,05000000 = a`, covariance `0,00e+00` |
| symétries | réflexion en y, réflexion en x et échange d'axes : **exactes** |
| convention de diffusion | MSD/axe sur 400 pas du moteur : **21,25** mesuré contre `a·t = 20,00` (`z = +0,92`) et contre `(p_hop/4)·t = 10,26` (**8,1 σ**). Tranché. |

Neuf points de support, support diagonal confirmé ; `K_rel` en compte 25. Avec l'organisateur
immobilisé (condition S), `K_rel` **se rabat exactement sur `K_X`**.

## 17. L'opérateur source–transport–disparition

`ρ_{t+1} = (1 − µ_X) K_rel ρ_t + B_t δ_0`, avec spectre
`λ(k) = (1−µ)[1 − a(1−cos k_y)][1 − a(1−cos k_x)]`, résolvante `1/(1−λ)`, profil stationnaire par
inversion DFT.

- rayon spectral **exactement** `1 − µ = 0,9960000000` ;
- masse de la réponse impulsionnelle géométrique en `(1−µ)`, vérifiée pas à pas ;
- asymptote de la réponse échelon **250,0000 = 1/µ exactement** ;
- profil stationnaire `r80 = 8,54400374531753`, qui **reproduit le bloc analytique gelé jusqu'au
  dernier chiffre** par une route indépendante ;
- mode de forme `λ₁/λ₀ = 0,99848078`, `τ_shape,tore = 657,73`.

Statuts : `X_KERNEL_STATUS = ORGANIZER_KERNEL_STATUS = RELATIVE_KERNEL_STATUS =
CONDITIONAL_EXACT` ; `UNBLOCKED_SOURCE_RESPONSE_OPERATOR = CONDITIONAL_EXACT` ;
`FULL_SOURCE_RESPONSE_OPERATOR = APPROXIMATE_WITH_EMPIRICAL_ERROR` ; terme source
`CONDITIONALLY_LINEAR`.

## 18. Observables population-robustes — la règle

Une statistique est robuste en population si elle est une **moyenne par particule**, ou une
fonction **exactement débiaisée** de moyennes par particule. Sous-échantillonner une population
échangeable sans remise est alors sans biais à **tout** `N`. Les normes de vecteurs bruités ne
sont pas de cette forme.

Enregistrés : `M₂` (carré de la distance torique à l'**organisateur**, jamais à un centre
estimé) ; la CDF radiale centrée source sur une grille gelée — la **distribution**, pas ses
quantiles, qui sont non linéaires et biaisés à petit `N` ; une distance de profil de type
Cramér–von Mises contre la CDF stationnaire exacte de l'opérateur, dont la **variance
d'échantillonnage est soustraite exactement** par la correction de population finie ; `N_X`, qui
n'est jamais un dénominateur ; et un décalage directionnel défini comme la **projection signée**
`⟨m, u⟩` du décalage moyen sur le déplacement propre de l'organisateur.

## 19. Observables — la démonstration, sur 129 bras réels

Champs finaux réellement enregistrés, trois missions, seul le nombre de molécules est réduit.
Rapport de la valeur sous-échantillonnée à la valeur pleine population :

| `N` conservé | `M₂` | `\|C−Y\|` | `\|m\|` | `W²` naïf | `W²` débiaisé |
|---|---|---|---|---|---|
| 3 | **0,980** | 1,399 | 1,400 | 11,453 | 0,922 |
| 12 | **1,002** | 1,118 | 1,116 | 3,435 | 0,989 |
| 120 | **1,000** | 1,007 | 1,001 | 1,016 | 0,998 |

`M₂` est plat à 2 % jusqu'à **trois** molécules. `|C−Y|` s'enfle de 40 % à `N = 3` — et `|m|`
aussi, ce qui **isole le défaut** : `m` lui-même est sans biais, sa **norme** ne l'est pas. Le
problème est la norme, pas le centrage de Fréchet. La distance de profil naïve se trompe d'un
facteur 11 à `N = 3` ; le débiaisage exact l'élimine.

## 20. Les huit échelles temporelles

| échelle | pas | forme close |
|---|---|---|
| `TAU_LIFETIME` | 249,0000 | `(1−µ)/µ` |
| `TAU_MASS_ON` | 249,4997 | `−1/ln(1−µ)` |
| `TAU_SHAPE` | 250,0000 | `ℓ_rel²/D_rel` |
| `TAU_FOLLOW` | 249,0000 | `(1−µ)/µ` |
| `TAU_SOURCE_OFF` | 249,4997 | `−1/ln(1−µ)` |
| `TAU_TURNOVER` | 250,0000 | `N*/E[B]` |
| `TAU_FP_RELATIVE` | 147,4180 | Poisson discret, rayon 5,0 |
| `TAU_SOURCE_SEPARATION` | 145,5898 | Poisson discret, rayon `ℓ_rel` |
| *(mode du tore)* | 657,7304 | propriété de `L`, pas du nuage |

Contre-vérifications : l'e-folding source-off, le lag optimal et `ℓ_relative` reproduisent
**exactement** le bloc analytique gelé.

## 21. Trois identités exactes — et chacune est un avertissement

- `TAU_LIFETIME = TAU_FOLLOW` : les deux sont `E[S]` du même âge géométrique. **Le nuage suit la
  source exactement avec le retard que sa matière survit.** Un seul fait, écrit deux fois.
- `TAU_MASS_ON = TAU_SOURCE_OFF` : l'opérateur est linéaire en la masse, donc allumer et éteindre
  la source relaxent au même rythme.
- `TAU_SHAPE = TAU_TURNOVER` : `ℓ_rel` est **défini** comme `√(D_rel/µ)`. Conséquence à ne pas
  manquer : « le rayon du nuage est conforme à la prédiction diffusion–disparition » **n'est pas**
  un contrôle indépendant de la durée de vie, puisque le rayon en est construit.

## 22. Le point qualifié n'a qu'**une** échelle de temps

Au point qualifié `core_R = 2 ℓ_X` exactement, `ℓ_rel = √2 ℓ_X` et `D_rel = 2 D_X = 2 D_Y`. En
substituant, **les deux** premiers passages continus se réduisent à la même expression
`1/(2µ_X)`. En unités de `1/µ_X` :

```
LIFETIME 0,996000   MASS_ON 0,997999   SHAPE 1,000000   FOLLOW 0,996000
SOURCE_OFF 0,997999   TURNOVER 1,000000   FP_RELATIVE 0,589672   SOURCE_SEPARATION 0,582359
mode du tore 2,630921
```

**Sept des huit échelles sont des multiples rationnels fixes de `1/µ_X`** ; la huitième
appartient au domaine. Les six pilotées par `µ_X` ne s'écartent que de **0,402 %** — par
arithmétique, pas par physique. Une expérience qui les observerait « en accord » n'aurait rien
appris : l'accord **ne peut pas** échouer.

`DEGREES_OF_FREEDOM_AS_TIMESCALES = 1`.

## 23. Cohérence : la source n'est pas quasi-statique

`χ = 2,0000` exactement. La source parcourt un rayon de nuage en ~146 pas tandis que le nuage
met ~250 pas à relaxer sa forme. `SOURCE_IS_NOT_QUASI_STATIC` — et c'est précisément pourquoi le
noyau **relatif**, avec `a_rel = a_X + a_Y`, est l'opérateur de transport correct, et pourquoi un
profil à source fixe décrirait mal le nuage. La probabilité qu'une molécule atteigne le rayon de
cœur avant de mourir vaut **0,5948**.

## 24. Refus de capacité, sur 170 bras

| espèce | moyenne | médiane | maximum |
|---|---|---|---|
| X | 3,554e−04 | 3,612e−04 | 1,044e−03 |
| Y | 3,372e−04 | 0 | 2,703e−03 |
| SX | 3,481e−04 | 3,480e−04 | 3,748e−04 |
| SY | 3,514e−04 | 3,505e−04 | 3,772e−04 |

Par taille : 3,65e−4 / 3,41e−4 / 3,59e−4 à `L = 36 / 72 / 96`, **sans tendance** — ce n'est pas
un artefact de taille finie. Par population : pente log-log **+0,047**, corrélation +0,106 sur
144 bras — le refus est **indépendant du nuage**, ce qui, joint aux valeurs quasi identiques de
`SX` et `SY`, l'identifie comme une propriété de l'occupation de fond du chémostat. Par
condition : 4,37e−4 (D), 3,58e−4 (P), 3,63e−4 (R), 3,43e−4 (S), et exactement 0 sous N, où aucun
X n'existe.

## 25. Une borne certifiée, avec sa portée

Le mandat demandait de **chercher** une borne certifiée avant de se rabattre sur une
caractérisation empirique. Elle existe. Une molécule offre `p_hop` sauts par pas en moyenne et
vit `(1−µ)/µ` pas, donc `E[R] = p_hop · ε · (1−µ)/µ` refus sur sa vie entière, et Markov donne
`P(R ≥ 1) ≤ E[R]`. Aucune hypothèse distributionnelle.

```
au ε moyen        E[R] = 0,00908   →   ≥ 99,09 % des molécules jamais refusées
au pire bras      E[R] = 0,02669   →   ≥ 97,33 % des molécules jamais refusées
```

Toute observable **par particule** bornée par `F` porte donc une erreur additive d'au plus
`F·E[R]` : pour une observable à valeurs de probabilité, 0,0091 en moyenne et 0,0267 au pire
bras. C'est exactement la classe enregistrée au §18. La borne **n'est pas** revendiquée pour les
observables jointes du nuage entier, où la borne d'union sur `N` molécules dépasse 1 et ne dit
rien.

`FULL_OPERATOR_ERROR = CERTIFIED_FOR_PER_PARTICLE_BOUNDED_OBSERVABLES__EMPIRICALLY_CHARACTERIZED_OTHERWISE`

## 26. Phase historique — la définition d'abord, les nombres ensuite

Le mandat exigeait de vérifier la **définition** avant de recalculer. Elle n'est pas ce que le
mot « e-folding » suggère : `source_off_response` prend la moyenne de `N_X` sur les 200 pas
**précédant** le retrait comme référence, puis rapporte le premier pas où `N_X` tombe sous
`référence/e`. C'est un **temps de premier passage** sous un seuil fixé par une référence
bruitée, pas un taux ajusté.

## 27. Les trois valeurs source-off, replacées dans leur loi

Les trois valeurs enregistrées se reproduisent exactement, références comprises. Plutôt que de
les comparer directement à 249,4997, la **loi nulle de l'estimateur** est obtenue en rejouant le
processus de mort binomial exact que le moteur applique après le retrait — sans démarrage, sans
réseau.

| bras | observé | moyenne nulle | σ nulle | `z` |
|---|---|---|---|---|
| `R/seed9301` | 233,0 | 250,1 | 30,5 | **−0,56** |
| `R/seed9302` | 297,0 | 272,7 | 33,3 | **+0,73** |
| `R/seed9303` | 245,0 | 249,6 | 30,8 | **−0,15** |

L'estimateur est biaisé de **+7,9 pas** par rapport à `τ`. Un second estimateur indépendant — la
pente des moindres carrés de `log N` sur `t` — donne 277,4 / 264,6 / 274,9, avec sa **propre**
loi nulle (moyenne 255,2, σ 36,3), soit `z = +0,62 / +0,26 / +0,54`. Les deux estimateurs placent
les trois bras à **moins d'un sigma** de leur propre loi. La dispersion des trois valeurs est
celle que la loi analytique prédit ; elle n'est pas l'indice d'un taux différent.

## 28. Les résultats à source statique, récupérés — et ils tranchent

OBTC02 avait rapporté la condition S comme « six statistiques sur six dans l'enveloppe », sans
les nombres. Ils comptent : la condition S fixe `p_hop_Y = 0`, donc `K_rel` se rabat sur `K_X` et
`a_rel = a_X` au lieu de `2 a_X`.

```
prédit   r80 statique 6,082763    r80 mobile 8,544004    rapport 1,4046
observé  r80 statique 5,9712      r80 mobile 8,0272      rapport 1,3443
```

Les deux prédictions reproduisent **exactement** le bloc analytique gelé par une route
indépendante. L'hypothèse concurrente — « le mouvement de la source est sans effet » — prédit un
rapport de **1,0000**. L'intervalle bootstrap à 95 % est **[1,2740 ; 1,4044]** et le pire cas
`min(P)/max(S)` vaut **1,1968** : 1 est exclu, et le rapport observé se place 4,3 % sous la
prédiction du noyau relatif.

**Consigné et non expliqué** : les deux régimes sont sous leurs prédictions **absolues**, de
1,8 % en statique et de 6,1 % en mobile, alors que leur **rapport** concorde. Le rapport est le
discriminant sans paramètre et sert de comparaison primaire ; le déficit absolu reste un résidu
ouvert. Le bras éteint `P/seed9101` est écarté de l'agrégat primaire par la définition héritée
d'« analysable », rapporté à part, et jamais supprimé.

## 29. Le piège de la redérivation, et comment il a été évité

Substituer `µ_Y = 0` et `k_Y = 0` fait lire la borne basse `0 < R_Y` et les deux bornes hautes
`R_Y < quelque chose de positif` : la fenêtre, **lue comme un ensemble de taux**, ressort **non
vide**, l'intervalle ouvert `(0 ; 1,787e−4)`. Le rapporter comme une condition satisfaite serait
exactement l'erreur que §27 du mandat interdit.

L'ensemble des taux que le LawSpec qualifié peut **atteindre** est le point unique `{0}`, et la
borne basse stricte l'exclut. **La fenêtre et l'ensemble atteignable ne s'intersectent pas.**
Chaque inégalité a donc été redérivée deux fois : comme énoncé sur `R_Y`, et contre la bande
atteignable.

| inégalité | la bande atteignable la satisfait | statut |
|---|---|---|
| basse `a_Y < R_Y` | **non** | `FAILS_ON_THE_REACHABLE_BAND` |
| haute, hasard d'un troisième organisateur | oui | `VACUOUSLY_SATISFIED` |
| haute, borne compacte KK | oui | `VACUOUSLY_SATISFIED` |
| non-vacuité | **non** | `VACUOUSLY_SATISFIED_BUT_UNREACHABLE` |

## 30. Les bornes, recalculées et non héritées

`D_eff` corrigé, `Q_max = 28` exhaustif, premier passage **discret** pour `τ_sep`
(**147,418** contre 125,000 en continu, rapport 1,1793), et `R_X` remplacé par l'intensité
additive opérante `E[B] = 0,4601` **mesurée sur 129 bras livrés**, puisque C4/C5 ont montré que
`k_X Q_max` n'est pas la quantité opérante. `ℓ_X = 2,5000`, `L_packed = 1,9886`, donc
`L_C = 2,5000` (la borne diffusive lie), `Δ = 5,0000`. La borne de hasard lie à **1,787e−4**
contre 2,173e−4 pour la borne compacte.

```
WINDOW_STATUS                 = NOT_PORTABLE
QUALIFIED_POINT_WINDOW_STATUS = UNREACHABLE_AT_THE_QUALIFIED_POINT
```

## 31. Les trois objets du §14, séparés

- **`CURRENT_QUALIFIED_POINT`** — ne *échoue* pas la fenêtre : il **n'a pas** le mécanisme dont
  elle parle. Ce qu'il ne faut **pas** dire : que la fenêtre y est « satisfaite », « non vide »
  ou « franchie ». Deux des trois inégalités le sont vacuement et la troisième échoue ; une
  satisfaction vacuité n'est pas un résultat.
- **`ANALYTICALLY_ADMISSIBLE_FAMILY`** — `k_Y ≤ 3,19065e−06` et `µ_Y ≤ 3,19065e−07` aux marges de
  design déclarées. Mais `k_Y > 0` **retire** `ORGANIZER_BOUND_SOURCE` : c'est un **autre**
  LawSpec, et rien de ce qui a été établi ici ne s'y transporte sans une qualification propre.
  Une division attendue y prend environ **22 387 pas**, soit **2,0 fois l'horizon gelé** :
  analytiquement éligible, mais pas gratuit.
- **`FUTURE_SELECTED_DESIGN_POINT`** — `NOT_SELECTED_IN_THIS_MISSION`. §18 interdit
  l'optimisation.

## 32. Le gate, et la condition qui le ferme

| condition | verdict |
|---|---|
| G1 provenance | PASS |
| G2 preuve héritée close | PASS |
| G3 artefacts historiques récupérés | PASS |
| G4 symboles classés, aucun `UNRESOLVED` | PASS |
| G5 corrections reproduites | PASS |
| G6 noyaux validés sept fois | PASS |
| G7 observables robustes en population | PASS |
| G8 échelles dérivées et relations classées | PASS |
| G9 erreur de capacité bornée | PASS |
| **G10 fenêtre originale reconstructible** | **FAIL — décisive** |

Neuf sur dix passent. La dixième est celle que le mandat rend décisive, et elle échoue pour une
raison **structurelle**, non statistique. `GATE_OPEN = False`, `FRESH_RUNS_AUTHORISED = False`.

## 33. La disposition n'a pas été choisie par un fichier post-run

C'est la correction structurelle du défaut établi au §5–§6. La règle appliquée est celle que le
**mandat** énonce en §16 — *si la fenêtre originale n'est pas reconstructible dans le LawSpec
qualifié, consigner `ORIGINAL_WINDOW_NOT_PORTABLE` et ne rien exécuter* — une source de **rang 1**,
écrite avant que la moindre analyse de cette mission n'existe. `freeze_obtr01.py` évalue
l'antécédent et applique la règle ; il ne choisit pas.

## 34. Gel, livraison et intégrité

`OBTR01_METHODS_CORE_HASH = 86855fd1b480552fac4130d0019777d5563041f32b9c985f3e4ba4c06a01afc3`,
sur 22 fichiers, 0 manquant, par la construction `nom | NUL | empreinte | LF` sur noms triés.
La mission n'ayant consommé **aucun** run scientifique, le gel **autorise** des travaux futurs
plutôt qu'il ne scelle un plan exécuté : chaque nombre des artefacts est une forme close, une
résolution discrète exacte, ou un recalcul depuis des trajectoires livrées.

Branche `codex/organizer-bound-timescale-rederivation-01`, commits séparés par section, **aucun
commit hérité réécrit**, aucun rebase. Une seule tentative de push, consignée telle quelle.

## 35. Éligibilité suivante

`NEXT_SCIENTIFIC_ELIGIBILITY = NO_FRESH_RUN_AT_THE_QUALIFIED_POINT_FOR_THIS_QUESTION` — aucun run
au point qualifié ne peut répondre à cette question, quelle qu'en soit la durée, parce que la
naissance et la mort de l'organisateur n'y existent pas. **Mécanisme absent, pas test
sous-puissant.**

Trois cibles, avec leur statut :

1. **un nouveau LawSpec avec `k_Y > 0` et `µ_Y > 0`** — `ANALYTICALLY_ELIGIBLE__REQUIRES_ITS_OWN_QUALIFICATION`.
2. **séparer les échelles à LawSpec fixé** — `NOT_ELIGIBLE_AS_POSED` : sept des huit sont des
   multiples rationnels fixes de `1/µ_X`, donc aucun run ne peut les faire diverger. Il faudrait
   bouger `µ_X` et `p_hop` **indépendamment**, de sorte que `ℓ_X` change en sites de réseau.
3. **le déficit radial absolu du §28** — `ELIGIBLE_AT_THE_QUALIFIED_POINT` : les deux régimes
   sont sous leurs prédictions absolues alors que leur rapport concorde. Ce résidu est une
   vraie question ouverte **à ce point**, il n'exige aucun nouveau LawSpec, et les observables
   du §18 en sont le bon instrument.

## 36. Ce qui n'est pas affirmé

Rien dans ce rapport n'affirme que le système se reproduit, reconstruit une identité, possède
une mémoire, possède une individualité, est vivant, est self-bound, ou possède une cohésion
autonome. Rien n'y confirme H3 ni ne valide globalement Kamimura–Kaneko. La fenêtre de minorité
n'a pas été testée : elle a été **redérivée**, et jugée sans référent au point qualifié.

---

```
MISSION                        = ORGANIZER-BOUND-TIMESCALE-REDERIVATION-01
DISPOSITION                    = ORIGINAL_WINDOW_NOT_PORTABLE
WINDOW_STATUS                  = NOT_PORTABLE
QUALIFIED_POINT_WINDOW_STATUS  = UNREACHABLE_AT_THE_QUALIFIED_POINT
FUTURE_SELECTED_DESIGN_POINT   = NOT_SELECTED_IN_THIS_MISSION

X_KERNEL_STATUS                = CONDITIONAL_EXACT
ORGANIZER_KERNEL_STATUS        = CONDITIONAL_EXACT
RELATIVE_KERNEL_STATUS         = CONDITIONAL_EXACT
UNBLOCKED_SOURCE_RESPONSE_OPERATOR = CONDITIONAL_EXACT
FULL_SOURCE_RESPONSE_OPERATOR  = APPROXIMATE_WITH_EMPIRICAL_ERROR
FULL_OPERATOR_ERROR            = CERTIFIED_FOR_PER_PARTICLE_BOUNDED_OBSERVABLES__EMPIRICALLY_CHARACTERIZED_OTHERWISE
SOURCE_TERM                    = CONDITIONALLY_LINEAR
SOURCE_CLASSIFICATION          = ADDITIVE_POINT_SOURCE_UNDER_A_BALANCED_CHEMOSTAT
SCALAR_CRITICALITY_STATUS      = NOT_VALID_AS_PRIMARY_CRITICALITY
SOURCE_QUASI_STATIC_STATUS     = SOURCE_IS_NOT_QUASI_STATIC
TIMESCALE_DEGREES_OF_FREEDOM   = 1

OBDI02_POSTRUN_ADJUDICATION_DEVIATION = CONFIRMED
DEVIATION_DIRECTION                   = CONSERVATIVE_FALSE_NONQUALIFICATION
FROZEN_EVIDENCE_STATUS                = UNAFFECTED
CUMULATIVE_CLOUD_EVIDENCE_STATUS      = VALID
OBDCA01_FORMAL_LIMITATION             = QUALIFICATION_SUPPORTED_DESPITE_RECORDED_POSTRUN_ADJUDICATION_DEVIATION

H3_STATUS                      = NOT_TESTED
REPRODUCTION_STATUS            = NOT_TESTED
AUTONOMOUS_COHESION_STATUS     = NOT_ESTABLISHED

SCIENTIFIC_RUNS_USED           = 0
OBTR01_METHODS_CORE_HASH       = 86855fd1b480552fac4130d0019777d5563041f32b9c985f3e4ba4c06a01afc3
NEXT_SCIENTIFIC_ELIGIBILITY    = NO_FRESH_RUN_AT_THE_QUALIFIED_POINT_FOR_THIS_QUESTION
TOMMY_ACTION_REQUIRED          = NONE
```
