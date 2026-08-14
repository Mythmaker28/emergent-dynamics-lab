```
MISSION       ORGANIZER-BOUND-DOMAIN-INVARIANCE-02
DISPOSITION   DOMAIN_RELATIVE_ATTACHMENT_EQUIVALENCE_NOT_ESTABLISHED
```

L'audit préalable a établi deux faits qui changent la lecture de toute la chaîne. D'abord, la
disposition `DOMAIN_INVARIANCE_PARTIAL` d'OBDI01 **n'était pas autorisée** : son protocole gelé
ne contient aucune liste de dispositions, et l'espace de neuf états a été écrit par OBDI01
lui-même *après* ses résultats, ce qu'il déclarait d'ailleurs explicitement. La disposition
formellement correcte est `DOMAIN_TEST_UNDERPOWERED`. Ensuite, la marge d'équivalence gelée
d'OBDI01 valait **0,25 et non 0,042** : le nombre `0,042` est l'**excès** de l'intervalle sur
cette marge (`0,2918 − 0,2500 = 0,0418`), et une phrase française ambiguë de mon rapport OBDI01
a invité la confusion. La preuve est arithmétique : sous une marge de 0,042, `R_g` et `r80`
auraient eux aussi échoué, alors qu'OBDI01 les déclarait passants.

Cent trente-huit bras neufs ont ensuite tourné à `L ∈ {36, 72, 96}`, quarante-six par taille,
tous techniquement valides, les deux évaluateurs d'accord partout, sans arrêt anticipé. Le TOST
correctement spécifié **passe** à la marge héritée : `β_CY = +0,0822`, intervalle à 90 %
`[+0,0100 ; +0,1544]`, entièrement inclus dans `±0,25`. Mais la barre que le mandat fixe pour la
qualification cumulative est `[−0,042 ; +0,042]`, et la borne atteinte la dépasse d'un facteur
**3,7**. L'équivalence de précision n'est donc **pas établie**.

Ce que la mission établit en revanche est net : sur 138 bras frais, le rayon de giration du
nuage donne `β = −0,0030 ± 0,0084` et son rayon à 80 % `β = +0,0037 ± 0,0073`, tous deux plats à
un pour cent près et conformes à la prédiction sans paramètre — un intervalle **vingt fois plus
serré** que celui d'OBDI01. La taille du nuage est invariante ; c'est l'**écart entre son centre
estimé et l'organisateur** qui résiste, et un diagnostic post-hoc montre pourquoi : cet écart
est piloté par la population, pas par le domaine.

---

## 1. Provenance

Artefact scindé d'OBDI01 recomposé dans un répertoire neuf, relu **espace de noms réseau
supprimé** et `GIT_NO_LAZY_FETCH=1`.

```
3 morceaux, empreintes des trois conformes ; archive recomposée conforme
git rev-parse HEAD          5a37a7be73c3624e76b9c77ee75fd22172b6eb52   conforme
git rev-parse HEAD^{tree}   04eef05ebd74af0bab128051b9b823efebc69f5f   conforme
git rev-list --missing=print   0 objet manquant
git fsck --full                propre
git status --porcelain         vide
branche codex/organizer-bound-domain-invariance-01 présente ; 1491 fichiers
frontière superficielle bb7fea74… = la tête d'OBTC02 ; aucun distant ; aucun pack promisor
```

Contenus exigés, tous présents : manifeste de gel, spécification du test direct, sorties online
et post hoc, registre complet des seeds, les **quinze trajectoires** confirmatoires. Les
quatorze fichiers du noyau gelé d'OBDI01 correspondent tous à leurs empreintes, neuf d'entre eux
résolus dans `OBTC02/code/` — l'héritage est donc vérifiable *dans* la livraison. `lawspec_v2.py`
et `observe.py` sont **bit-à-bit identiques** à ceux livrés par OBTC02. Les harnais d'OBDI01
rejoués depuis l'état reconstruit : **25 tests sur 25**.

`PROVENANCE_STATUS = SELF_CONTAINED_SPLIT_DELIVERY_PASS`.

## 2. HEAD, arbre, branche et commits

```
branche   codex/organizer-bound-domain-invariance-02
parent    5a37a7be73c3624e76b9c77ee75fd22172b6eb52   (tête d'OBDI01, inchangée)
commits   sept, séparés selon le §23 du mandat
```

Aucun commit hérité n'a été réécrit, aucun rebase n'a eu lieu.

## 3. Disposition rapportée d'OBDI01

```
OBDI01_REPORTED_DISPOSITION = DOMAIN_INVARIANCE_PARTIAL
```

## 4. Disposition append-only adjudiquée

```
OBDI01_ADJUDICATED_DISPOSITION = DOMAIN_TEST_UNDERPOWERED
```

**Était-elle autorisée ?** Non. Le protocole gelé d'OBDI01 ne contient **aucune** clé de
disposition : la recherche porte sur `mission, parent, design_status, route, window, point,
identity_with_obtc02, domain, hypotheses, predictions, prediction_status_layers, power,
principal_outcome, secondary_endpoint, stopping, forbidden_claims, unconditional_status`. La
liste de neuf états vit dans `OBDI01/out/_evidence.json`, écrit **après** les runs, et ce fichier
déclare lui-même `DISPOSITION_SPACE_PROVENANCE = RECONSTRUCTED`. Une disposition inventée après
les résultats ne peut pas être la disposition autorisée de ces résultats.

Les dispositions à autorité **héritée** sont celles que la chaîne nomme elle-même :
`INHERITED_NON_DOMAIN_AXIS_NOT_CLOSED`, `DOMAIN_TEST_UNDERPOWERED`, `AUDIT_INVALID`.

**Les huit faits, tous vérifiés :**

```
1  quinze runs techniquement valides               15/15
2  protocole exécuté en entier                     15 bras prévus, 15 lancés, aucun arrêt
3  LawSpec inchangé                                LAWSPEC_DIFF = NONE
4  aucune limite modifiée après les résultats      spec_sha256 asserté avant le premier bras
5  alternatives non bornées exclues                β = +0.0077, +0.0351, +0.0708 ; 0.5 et 1
                                                   exclus sur les trois statistiques
6  intervalle d'équivalence encore trop large      0.2918 contre une marge de 0.2500
7  puissance dimensionnée sur la mauvaise métrique  sizée sur R_g contre H_linear ; n issu d'un
                                                   plancher d'estimabilité, pas de la précision
8  environ huit bras par taille auraient suffi     8
```

`INHERITED_NON_DOMAIN_AXIS_NOT_CLOSED` ne s'applique pas : D était bien le seul axe non
satisfait. `AUDIT_INVALID` ne s'applique pas : rien dans l'instrument n'a failli.

**Mise en garde consignée.** La règle §14 d'OBDI01, *lue littéralement*, ne se déclenchait pas :
elle demandait 80 % de puissance contre `H_linear` mesurée sur `R_g`, atteinte dès `n = 1`. Elle
était indexée sur la mauvaise statistique et sur la mauvaise espèce d'alternative — puissance
contre une alternative lointaine plutôt que précision d'un intervalle d'équivalence — et ne
pouvait donc pas détecter la déficience qu'elle était censée surveiller. Ce n'est pas un
argument contre l'adjudication : c'est son mécanisme, et OBDI01 l'avait déjà consigné comme son
défaut (b).

Cette adjudication est **append-only** : le rapport gelé d'OBDI01 garde son texte, son empreinte
et son commit. Ce qui change est l'étiquette, pas un chiffre.

## 5. Les quatre composantes exactes du test direct

```
A_shape_invariance        R_g, r80, |C−Y|      PASS seulement si les trois passent   → FAIL
B_density_exponent        densité                                                    → PASS
C_no_true_winding         enroulement                                                → PASS
D_profile_compatibility   profil radial                                              → PASS
```

## 6. La composante non close

`A_shape_invariance`, et à l'intérieur d'elle **la seule statistique `|C−Y|`**. `R_g` et `r80`
passaient. « Trois composantes sur quatre » est exact au niveau **composante** ; au niveau
**statistique** c'est cinq sur six. Les deux énoncés décrivent le même résultat.

## 7. Signification exacte de `5/4, 4/4, 5/4`

La notation provient de `run_obdi01.py`, qui imprime `'%d/%d' % (arms_within, arms_required)`.
C'est donc **bras passants / bras requis**, et non passants sur total. Ce n'est ni une erreur de
transcription, ni un compte de statistiques. Un numérateur supérieur au dénominateur ne paraît
impossible que si l'on suppose le dénominateur égal au total.

```
L=36 : 5/5 bras passent ; seuil requis : 4/5
L=72 : 4/5 bras passent ; seuil requis : 4/5     (un bras éteint, TV indéfinie, compté hors enveloppe)
L=96 : 5/5 bras passent ; seuil requis : 4/5
```

## 8. Estimand primaire

```
β_CY : pente de log d_CY sur log L, où d_CY(L) est la MÉDIANE par bras de |C−Y| DIVISÉE par la
       prédiction exacte de taille finie de l'opérateur à cette taille.
```

La division fait partie de l'estimand gelé, pas d'un ajustement ultérieur : elle retire la
correction d'images périodiques et fait qu'un biais multiplicatif indépendant de `L` s'annule.

## 9. Définition de `C`

Centre de Fréchet toroïdal du champ `X` : le minimiseur exact et séparable de la somme des
distances toroïdales au carré, calculé axe par axe et arrondi à un site du réseau.

## 10. Définition de `Y`

L'organisateur : l'unique cellule portant `n_Y > 0`. Avec un seul organisateur sa position est
exacte, non estimée.

## 11. Unité indépendante

```
INDEPENDENT_UNIT   SEED
WITHIN_SEED_SUMMARY   la MÉDIANE de |C−Y| sur les 180 trames de la fenêtre d'analyse
```

Quatre candidats ont été mesurés sur les bras d'OBDI01 avant toute donnée neuve :

```
candidat     sd(log)@36  sd(log)@72  sd(log)@96   pire
médiane        0.1219      0.0558      0.0425     0.1219
moyenne        0.0982      0.0745      0.0642     0.0982
tronquée 10 %  0.0944      0.0758      0.0414     0.0944
q75            0.1129      0.0890      0.0244     0.1129
```

La médiane est en fait la **pire** des quatre. Elle est néanmoins conservée : avec quatre ou cinq
bras par taille, chacun de ces écarts-types porte une erreur relative d'environ 40 %, donc
l'ordre entre candidats n'est pas résoluble et choisir sur cette base serait une sélection sur
le bruit. Le garder rend `PRIMARY_ESTIMAND_DIFF_FROM_OBDI01 = NONE` littéralement vrai, au prix
d'un `n` plus grand. L'autocorrélation temporelle est traitée là où elle appartient — dans
l'erreur d'échantillonnage du résumé, mesurée par bootstrap par blocs — et **n'augmente jamais**
le nombre d'observations indépendantes, qui est le nombre de graines et rien d'autre.

## 12. Méthode d'équivalence

**Audit de la méthode d'OBDI01, neuf points :**

```
était-ce un TOST ?                       NON dans la forme, OUI dans la logique : la règle
                                         |β| + c·se ≤ δ est la formulation par intervalle d'un TOST
niveau de l'intervalle                   99.49 %, pas 90 % ; demi-largeur 1.70 fois celle d'un
                                         TOST standard à α = 0.05
α nominal                                0.05 FAMILIAL sur K = 10 tests, Šidák → 0.005116 par test
la graine était-elle l'unité ?           OUI
les trames servaient-elles d'observations ?  NON pour la statistique primaire
hétéroscédasticité entre tailles         MODÉLISÉE PUIS NEUTRALISÉE : la règle
                                         se = max(sd_réalisé, sd_préenregistré)/√n a remplacé
                                         chaque sd réalisé par le même plancher 0.3605
échelle brute ou logarithmique           LOGARITHMIQUE
traitement des extinctions               AUCUNE RÈGLE PRÉSPÉCIFIÉE — le bras éteint était
                                         silencieusement retiré des statistiques de forme et
                                         ADMIS avec la valeur 0 dans la densité
équilibre entre tailles                  prévu 5/5/5, réalisé 5/4/5
```

```
OBDI01_EQUIVALENCE_METHOD = VALID_BUT_OVERCONSERVATIVE
```

L'estimand est bien défini et récupérable, l'unité est la graine, l'échelle est logarithmique et
la logique d'intervalle est une vraie règle d'équivalence : rien n'est `MISALIGNED`, rien n'est
`UNRESOLVED`. Mais l'intervalle a été construit à 99,49 %, avec un plancher de variance et une
correction de multiplicité dont une affirmation intersection-union n'a pas besoin. Diagnostic,
sur les mêmes données d'OBDI01, sans rien réviser :

```
estimateur gelé, intervalle gelé          β=+0.0708 se=0.0789   |β|+c·se = 0.2918
estimateur gelé, intervalle TOST 90 %     β=+0.0708 se=0.0789   |β|+c·se = 0.2007
variances réalisées, TOST 90 %            β=+0.0524 se=0.0529   |β|+c·se = 0.1394
régression au niveau bras, HC0, TOST 90 % β=+0.0769 se=0.0555   |β|+c·se = 0.1682
```

**OBDI02 emploie donc** le TOST que le §6 du mandat autorise sous ce verdict : forme par
intervalle, `α = 0,05` unilatéral, donc **intervalle bilatéral à 90 %**, entièrement inclus dans
la marge. Une estimation ponctuelle proche de zéro ne suffit pas ; exclure `H_linear` ne suffit
pas ; exclure `H_sublinear` ne suffit pas.

## 13. Marge

```
marge du test primaire        0.250   — héritée, inchangée
référence stringente          0.042   — la barre de qualification du mandat, rapportée
```

La marge gelée d'OBDI01 est `0,25`, lue dans
`principal_outcome.components.A_shape_invariance.margin`. Le chiffre `0,042` porté par le mandat
n'est **pas** une marge : c'est l'excès de l'intervalle d'OBDI01 sur cette marge,
`0,2918 − 0,2500 = 0,0418`. **Preuve** : sous une marge de 0,042, la composante `R_g`
(`|β|+c·se = 0,0514`) et la composante `r80` (`0,0862`) auraient également échoué, alors
qu'OBDI01 les rapportait passantes ; seule une marge de 0,25 reproduit le motif PASS/PASS/FAIL
publié.

Adopter `0,25` n'est donc pas un élargissement : c'est la restauration de la valeur héritée, et
c'est ce qui rend `EQUIVALENCE_MARGIN_DIFF_FROM_OBDI01 = NONE` vrai. Le chiffre `0,042` est
conservé et rapporté comme **référence stringente**, et il sert de barre à la qualification
cumulative au §35, conformément au §19 du mandat.

Le défaut appartient au rapport d'OBDI01, dont la formulation française invitait la mélecture.
Il est consigné comme tel.

## 14. Niveau de confiance

```
TOST, α = 0,05 unilatéral par test ; intervalle bilatéral à 90 % ; c = 1,64485
```

Aucune correction de multiplicité n'est appliquée pour fabriquer une réussite : le endpoint
primaire est **unique**, et les endpoints secondaires ne peuvent que veto, jamais accorder.

## 15. Traitement des extinctions

Préenregistré avant tout run.

```
une extinction est          SCIENTIFIC_OUTCOME
une extinction n'est pas    TECHNICAL_INVALIDITY
politique de graine         elle consomme sa graine ; jamais remplacée, jamais rejouée,
                            jamais supprimée comme donnée manquante
```

**Partie 1 — maintien de population.** À chaque taille, le nombre de bras **analysables** doit
valoir au moins `⌈5n/6⌉ = 39` sur les 46 lancés. Un bras est analysable si son résumé par graine
est fini et strictement positif. Sous le taux d'extinction historique de la chaîne (2/21 =
9,52 %), ce seuil a une probabilité d'échec à vide de **6,70 %**, calculée et consignée avant les
runs.

**Partie 2 — équivalence spatiale conditionnelle**, calculée sur les bras analysables. La
qualification exige **les deux parties**.

**Analyse de sensibilité conservatrice**, préenregistrée : chaque bras éteint reçoit la valeur la
moins favorable observée à sa taille, d'abord le maximum puis le minimum, et le test primaire est
rejoué sur les données complétées.

## 16. Analyse de puissance

Centrée sur `|C−Y|`, jamais sur `R_g`. Les quinze bras d'OBDI01 servent **uniquement** de données
historiques de conception.

```
formule    se(β) = [ Σ_L w_L (log L − x̄_w)² ]^(−1/2),  w_L = n_L / cv_L²
           puissance = 2 Φ(δ/se − c) − 1  sous β = 0,  c = 1,64485
hypothèses la graine est l'unité ; la dispersion par taille est celle d'OBDI01 ET SON PROPRE
           ALÉA EST PROPAGÉ par un tirage χ² sur df = n_bras − 1 ; les extinctions surviennent
           au taux historique ; le modèle source-bound fixe β = 0 exactement
variances  sd(log) = 0,1219 / 0,0558 / 0,0425 à L = 36 / 72 / 96 (df = 4 / 3 / 4)
```

La simulation reproduit tout le pipeline, y compris l'estimation des variances sur les bras
eux-mêmes. Elle est bien plus exigeante que le calcul analytique, parce que dimensionner sur une
variance estimée sur quatre bras en la traitant comme connue est précisément l'erreur qui a
produit OBDI01.

```
n/taille   se(β)     puiss. analytique 0.042   puiss. simulée 0.042   simulée 0.25   coût
10         0.03931          0.0000                   0.0063              0.9750       1810 s
20         0.02780          0.0000                   0.0432              0.9982       3620 s
46         0.01833            —                      0.3144                1.000      8326 s
100        0.01243          0.9170                   0.7050              1.0000      18100 s
200        0.00879          0.9983                   0.9210              1.0000      36200 s
```

```
n minimal pour 90 % de puissance à la marge 0.25       6
n minimal pour 90 % de puissance à la référence 0.042  200 par taille, soit 600 bras ≈ 10 h
taux d'erreur de type I à la frontière β = ±0.042      0.0534 / 0.0530   (nominal 0.05)
puissance à β = 0                                      0.9076
puissance à β = δ/2                                    0.6404
déclare l'équivalence à tort sous H_sublinear (β=0.5)  0.0000
déclare l'équivalence à tort sous H_linear (β=1.0)     0.0000
```

**Plafond de budget, fixé avant toute comparaison avec le `n` requis.** Débit mesuré : deux bras
concurrents à `L = 36` prennent 30,1 s contre 29,2 s pour un seul, donc les deux CPU disponibles
donnent une accélération quasi linéaire. Enveloppe déclarée : **75 minutes** de phase moteur,
parce que le travail obligatoire qui suit — analyse, figures, rapport, artefact scindé, relecture
hors ligne — demande environ 45 minutes et que la livraison est obligatoire. D'où un plafond de
**49 bras par taille**.

La référence stringente 0,042 exige 200 bras par taille : **au-delà du plafond d'un facteur 4**.
Elle est donc **déclarée sous-puissante avant tout run**, avec une puissance de `0,314`, et
rapportée sans jamais être décisive.

## 17. Nombre de graines par taille

```
n minimal issu de la règle de puissance      6
n issu de la cible de précision              46
n ADOPTÉ                                     46 par taille, 138 bras au total
plafond de budget                            49 par taille
durée estimée                                69,4 min ; réalisée 73,0 min
```

Cible de précision préenregistrée : borne d'équivalence atteinte attendue
`E[δ*] = (0,798 + c)·se(β) ≤ 0,045` sous `β = 0`, la plus petite cible ronde atteignable dans le
plafond, choisie pour amener la borne à l'ordre de grandeur du chiffre `0,042` que le mandat
interroge.

**Déviation déclarée.** Le §9 demande le *plus petit* `n` atteignant 90 % de puissance : à la
marge héritée ce serait `n = 6`. `n = 46` est adopté à la place, parce que l'objet même de la
mission est la précision et non un succès à marge large. Le `n` plus grand est fixé ici, avant
tout run, borné par un plafond déclaré sur des motifs indépendants, et consigné comme déviation
plutôt que présenté comme la sortie de la règle.

Graines fraîches, 855 fichiers balayés, **181 entiers de type graine retirés** (MCM01 2, ORR01
10, CSC01 30, OBTC01 41, OBTC02 23, OBDI01 37) :

```
L=36   8100000 … 8100045
L=72   8101000 … 8101045
L=96   8102000 … 8102045
DISJOINT = True     aucun recouvrement
```

## 18. Freeze

```
OBDI02_METHODS_CORE_HASH   59b19169fa087caa39f8b1139a946d8a1cbad23519bea3e604c8bd5bad525f1b
spec_sha256                c65aaef49e07115df647afaaf0ddea088eb494eef7734e1b8db8177921046a51
fichiers couverts          16     manquants : aucun
SCIENTIFIC_RUNS_USED_AT_FREEZE   0
```

```
LAWSPEC_DIFF_FROM_OBDI01                       NONE
CHEMOSTAT_DIFF_FROM_OBDI01                     NONE
COHESION_DIFF_FROM_OBDI01                      NONE
DOMAIN_SIZES_DIFF_FROM_OBDI01                  NONE
EQUIVALENCE_MARGIN_DIFF_FROM_OBDI01            NONE
PRIMARY_ESTIMAND_DIFF_FROM_OBDI01              NONE
EQUIVALENCE_INTERVAL_LEVEL_DIFF_FROM_OBDI01    NON_EMPTY
```

**Confirmation ou redesign ?** Une **confirmation** de l'estimand et de la marge, avec un
**redesign méthodologique ciblé de l'intervalle seul**. La loi, le chémostat, les tailles, la
préparation, l'estimand, le résumé par graine et la couche technique sont les objets hérités.
Ce qui change est que l'intervalle à 99,49 % corrigé Šidák est remplacé par l'intervalle à 90 %
qu'un TOST à `α = 0,05` réclame. Le §6 du mandat prévoit exactement cela sous
`VALID_BUT_OVERCONSERVATIVE`, à condition que ce soit gelé avant tout run et déclaré comme
redesign. Ce l'est.

L'identité est une propriété du graphe d'appel : les bras sont produits en appelant le `run_one`
d'OBDI01, qui appelle le `run_arm` d'OBTC02, tous deux non modifiés. Seuls diffèrent `L`, la
graine et le répertoire d'écriture.

## 19. Starts consommés

```
classe          consommé
confirmation      138
invalides           0
SCIENTIFIC_RUNS_USED = 138
```

Chaque bras a tourné dans son propre processus, ouvrant exactement un start dans son propre
registre ; les 138 entrées sont consolidées dans un registre unique. Deux ouvriers concurrents
ont été utilisés parce que la machine a deux CPU ; l'ordre des bras est l'ordre gelé, seul le
lancement est concurrent, et aucun bras n'en est modifié.

## 20. Invalidités techniques

```
TECHNICALLY_INVALID_RUNS = 0
```

138 bras sur 138 techniquement valides ; les deux évaluateurs d'accord sur 138 sur 138 ;
occupation exactement constante sur 138 sur 138 ; refus de transport au plus `1,04 × 10⁻³` pour
`X` et `2,69 × 10⁻³` pour `Y`.

## 21. Extinctions

```
L = 36    3 / 46   (6,5 %)
L = 72    4 / 46   (8,7 %)
L = 96    2 / 46   (4,3 %)
total     9 / 138  (6,5 %)   contre 9,5 % historiques
tendance croissante avec L : z = −0,24, p unilatéral = 0,595  →  AUCUNE
```

Aucune graine n'a été remplacée, aucun bras rejoué, aucune extinction supprimée.

## 22. Résultats à `L = 36`

```
bras 46, analysables 43 (seuil requis 39/46)
|C−Y|  moyenne 2,9048   sd(log) 0,1488   prédiction 3,0798   écart −6,73 %
R_g    5,7957 contre 5,8298 prédit   −0,58 %
r80    7,0296 contre 7,0137 prédit   +0,23 %
densité 0,090655   N_X 117,49
enroulement 0 / 8280 trames
profil radial 42/46 bras passent ; seuil requis : 37/46
gate D hérité 29/46 bras passent  →  taux d'échec 37,0 %
```

## 23. Résultats à `L = 72`

```
bras 46, analysables 42 (seuil requis 39/46)
|C−Y|  moyenne 3,1345   sd(log) 0,1902   prédiction 3,1717   écart −3,25 %
R_g    5,9738 contre 6,0303 prédit   −0,94 %
r80    7,0108 contre 6,9775 prédit   +0,48 %
densité 0,022382   N_X 116,03
enroulement 0 / 8280 trames
profil radial 41/46 bras passent ; seuil requis : 37/46
gate D hérité 25/46 bras passent  →  taux d'échec 45,7 %
```

## 24. Résultats à `L = 96`

```
bras 46, analysables 44 (seuil requis 39/46)
|C−Y|  moyenne 3,6149   sd(log) 0,3478   prédiction 3,1511   écart +4,81 %
R_g    6,0268 contre 6,0526 prédit   −0,43 %
r80    7,0448 contre 6,9895 prédit   +0,79 %
densité 0,012043   N_X 110,99
enroulement 0 / 8280 trames
profil radial 41/46 bras passent ; seuil requis : 37/46
gate D hérité 34/46 bras passent  →  taux d'échec 26,1 %
```

La dispersion à `L = 96`, `sd(log) = 0,3478`, vaut **huit fois** l'estimation historique tirée de
cinq bras d'OBDI01 (`0,0425`). C'est la leçon méthodologique centrale de la mission : une
variance estimée sur cinq graines n'est pas une variance connue.

## 25. Estimation de l'effet d'échelle

```
β_CY = +0,08219   se = 0,04391
```

Soit une croissance de `2,67^0,0822 = 1,083`, **8,3 %** sur toute la plage `36 → 96`.

## 26. Intervalle d'équivalence

```
intervalle à 90 %          [ +0,00998 ; +0,15441 ]
borne d'équivalence atteinte   0,15441
marge du test primaire         0,250    →  PASS
référence stringente           0,042    →  FAIL, dépassée d'un facteur 3,7
H_sublinear (β = 0,5) exclu    OUI
H_linear   (β = 1,0) exclu     OUI
```

L'intervalle **n'inclut pas zéro** à 90 % — sa borne basse vaut `+0,0100`. À 95 % il l'inclurait
(`[−0,0039 ; +0,1683]`). Il y a donc une indication faible d'une petite dépendance positive, et
elle est rapportée comme telle.

**Sensibilité aux extinctions**, préenregistrée, imputation conservatrice :

```
imputation au maximum observé   β = +0,1344   borne atteinte 0,2339   PASS à 0,25
imputation au minimum observé   β = +0,0745   borne atteinte 0,1473   PASS à 0,25
robuste : OUI
```

**Diagnostic post-hoc, non décisif, qui n'est appliqué nulle part.** La médiane inter-bras des
mêmes résumés vaut `3,000 / 3,081 / 3,000` à `L = 36 / 72 / 96` : **parfaitement plate**, et la
pente qui en découle vaut `−0,0198`. L'estimateur gelé agrège par la **moyenne des logarithmes**,
que déplace une queue à droite. Six bras — un à `L=36`, un à `L=72`, **quatre à `L=96`** — ont
gardé une population cinq à vingt fois inférieure à la normale sans s'éteindre avant la fin de la
fenêtre ; avec si peu de molécules le centre de Fréchet est une estimation bruitée de la position
du nuage et dérive loin de l'organisateur. La corrélation entre `log N_X` et `log |C−Y|` sur les
129 bras analysables vaut **−0,846**. Un effet de **population** entre donc dans une statistique
**spatiale** par le bruit d'échantillonnage du centre. En retirant ces six bras :
`β = +0,0414 ± 0,0242`, borne atteinte `0,0812`.

**Défaut consigné.** La définition gelée d'un bras « analysable » — un résumé fini et positif —
admet un bras dont la population s'est partiellement effondrée. Un plancher préenregistré sur la
population en fenêtre aurait séparé « le nuage existe » de « le nuage est mesurable ». C'est un
défaut de conception d'OBDI02, consigné et non appliqué.

## 27. Gate de maintien de population

```
L=36 : 43/46 bras analysables ; seuil requis : 39/46      PASS
L=72 : 42/46 bras analysables ; seuil requis : 39/46      PASS
L=96 : 44/46 bras analysables ; seuil requis : 39/46      PASS
POPULATION_SUPPORT_GATE = PASS
```

## 28. `R_g`

```
β = −0,00304   se = 0,00843   intervalle à 90 % [ −0,01691 ; +0,01083 ]
écarts à la prédiction sans paramètre : −0,58 %, −0,94 %, −0,43 %
```

Le rayon de giration est **invariant à un pour cent près** sur une plage de domaine de facteur
2,67, avec un intervalle vingt fois plus serré que celui d'OBDI01 (`±0,0139` contre `±0,437`).

## 29. `r80`

```
β = +0,00373   se = 0,00727   intervalle à 90 % [ −0,00823 ; +0,01569 ]
écarts à la prédiction : +0,23 %, +0,48 %, +0,79 %
```

## 30. Densité

```
γ = −2,0612   se = 0,0853
N_X moyen : 117,49 / 116,03 / 110,99
```

`H_bound` prédit `−2`, `H_sublinear` `−1`, `H_fill` `0`. La population est indépendante de la
taille du domaine et la densité tombe donc en `L⁻²`.

## 31. Winding

```
0 / 8280 trames à chaque taille, 0 / 24 840 au total ; tolérance gelée 0,01
```

## 32. Profil radial

```
L=36 : 42/46 bras passent ; seuil requis : 37/46
L=72 : 41/46 bras passent ; seuil requis : 37/46
L=96 : 41/46 bras passent ; seuil requis : 37/46
```

## 33. Endpoint historique

```
LEGACY_D_GATE_STATUS = MISALIGNED_WITH_DOMAIN_INVARIANCE   (inchangé)
L=36 : 29/46 bras passent   taux d'échec 37,0 %
L=72 : 25/46 bras passent   taux d'échec 45,7 %
L=96 : 34/46 bras passent   taux d'échec 26,1 %
global : 88/138             taux d'échec 36,2 %
```

Sur 138 bras sains produits par le LawSpec gelé, le gate hérité en rejette **cinquante**, y
compris à la plus petite taille de domaine. Avec 46 bras par taille au lieu de 5, le taux est
enfin estimé avec précision, et il confirme sans ambiguïté le diagnostic d'OBDI01 : ce gate est
un test **absolu bruité à toutes les tailles**, et non un problème propre aux grands domaines.

## 34. Matrice cumulative

| axe | source | protocole | seeds | hash | disposition | limitations |
|---|---|---|---|---|---|---|
| Population stationnaire | OBTC02 | obtc02_protocol.yaml | 9101–9106 | 747c1f5e… | PASS | un bras P éteint sur six |
| Source statique | OBTC02 | obtc02_protocol.yaml | 9201–9203 | 747c1f5e… | FAIL_ON_THE_PER_ARM_GATE__NO_FROZEN_REQUIREMENT | échec structurel 0/0 = NaN |
| Retrait de source | OBTC02 | obtc02_protocol.yaml | 9301–9303 | 747c1f5e… | PASS | — |
| Absence de source | OBTC02 | obtc02_protocol.yaml | 9401–9402 | 747c1f5e… | PASS | — |
| Turnover | OBTC02 | obtc02_protocol.yaml | 9102–9106 | 747c1f5e… | PASS | ≈ 36 renouvellements/fenêtre |
| Causalité de la source | OBTC02 | obtc02_protocol.yaml | 9301–9402 | 747c1f5e… | PASS | — |
| Compatibilité opérateur | OBTC02 | enveloppe N2 | 9101–9503 | 747c1f5e… | PASS | opérateur complet APPROXIMATE_WITH_EMPIRICAL_ERROR |
| `R_g` et `r80` selon `L` | OBDI01 | obdi01_protocol.yaml | 771010–771214 | 6de8d12b… | PASS | intervalle à 99,49 %, surconservateur |
| Densité selon `L` | OBDI01 | obdi01_protocol.yaml | 771010–771214 | 6de8d12b… | PASS | un bras éteint entre avec densité nulle |
| Winding selon `L` | OBDI01 | obdi01_protocol.yaml | 771010–771214 | 6de8d12b… | PASS | unité = la trame, admissible car compte nul |
| Profil radial selon `L` | OBDI01 | obdi01_protocol.yaml | 771010–771214 | 6de8d12b… | PASS | seuil atteint exactement à `L=72` |
| **Équivalence précise de `\|C−Y\|`** | **OBDI02** | obdi02_protocol.yaml | 8100000–8102045 | 59b19169… | **FAIL à la barre 0,042 ; PASS à la marge héritée 0,25** | référence stringente sous-puissante par construction |

Graines : OBTC02 17, OBDI01 15, OBDI02 138. Recouvrement entre missions : **zéro**. Aucune graine
n'est comptée deux fois dans une même statistique. Les axes d'OBDI01 sont ici **répliqués et
resserrés** par OBDI02, non recomptés : `R_g`, `r80`, la densité, le winding et le profil radial
d'OBDI02 sont mesurés sur des graines entièrement disjointes.

## 35. Portée scientifique

**Peut être dit.** Sur 138 bras frais préenregistrés et sur une plage de domaine de facteur 2,67,
la taille propre du nuage est invariante : rayon de giration `β = −0,0030 ± 0,0084`, rayon à 80 %
`β = +0,0037 ± 0,0073`, tous deux plats à un pour cent près et conformes à la prédiction sans
paramètre de l'opérateur. La population est indépendante de `L`, la densité tombe en
`L^−2,061 ± 0,085`. Aucun enroulement topologique sur 24 840 trames. Le profil radial est
compatible avec le noyau exact à toutes les tailles. Le maintien de population passe aux trois
tailles sans tendance avec `L`. Le gate D hérité rejette 36 % des bras sains à toutes les
tailles.

**Ne peut pas être dit.** Que l'échelle relative entre le cœur et l'organisateur est équivalente
à une constante : la borne atteinte vaut `0,1544`, contre une barre de qualification de `0,042`.
Que le nuage est self-bound, qu'il possède une cohésion autonome, qu'il constitue une cellule ou
une identité, qu'il se reproduit, qu'il possède une mémoire, qu'il confirme H3, ou qu'il valide
globalement Kamimura–Kaneko.

**Défauts de cette mission, consignés.** (a) La définition gelée d'un bras analysable admet une
population partiellement effondrée, ce qui laisse un effet de population entrer dans une
statistique spatiale. (b) La cible de précision préenregistrée (`0,045`) a été manquée d'un
facteur 3,4 parce que la variance historique, estimée sur quatre ou cinq bras, sous-estimait la
vraie dispersion d'un facteur huit à `L = 96` ; la simulation de puissance l'avait partiellement
anticipé en propageant l'aléa des variances, mais pas à cette amplitude. (c) Le `n` adopté dévie
de la règle littérale « le plus petit `n` », déviation déclarée avant les runs.

## 36. Prochaine éligibilité

```
NEXT_SCIENTIFIC_ELIGIBILITY = NONE
```

Le mandat est explicite : *« Ne lance pas une troisième collecte identique sans analyser pourquoi
la variance réelle dépasse encore la puissance prévue. »* Cette analyse est faite et elle est au
§26 : la variance excédentaire n'est pas du bruit de graine, c'est un mélange. Les bras à
population effondrée forment une seconde population dans laquelle `|C−Y|` mesure le bruit du
centre plutôt que la géométrie du nuage. Une troisième collecte identique à 200 bras par taille
coûterait dix heures et mesurerait encore ce mélange. Ce qu'il faudrait d'abord est une décision
méthodologique — un plancher de population préenregistré, ou un estimand de position robuste aux
petits effectifs — et cette décision n'est pas une collecte.

---

```
GOOD_NEWS
Sur 138 bras entierement neufs, la taille propre du nuage ne depend pas du domaine : rayon de
giration beta = -0.0030 +- 0.0084 et rayon a 80 pct beta = +0.0037 +- 0.0073, plats a un pour
cent pres et conformes a la prediction sans parametre de l'operateur, avec un intervalle vingt
fois plus serre que celui d'OBDI01. La densite tombe en L^-2.061 +- 0.085, la population est
independante de L, aucun enroulement topologique n'apparait sur 24 840 trames, le profil radial
est compatible avec le noyau exact partout, et le maintien de population passe aux trois tailles
sans aucune tendance avec L. Deux ambiguites heritees sont fermees definitivement : la marge
gelee d'OBDI01 valait 0.25 et non 0.042, et la notation 5/4 signifiait bras passants sur bras
requis. Le gate D herite, mesure sur 138 bras au lieu de 15, rejette 36.2 pct des bras sains a
toutes les tailles : le diagnostic de desalignement est confirme sans ambiguite.

LESS_GOOD_NEWS
L'equivalence de precision visee n'est pas atteinte. La borne atteinte vaut 0.1544, soit 3.7
fois la barre de qualification de 0.042, et l'intervalle a 90 pct n'inclut pas zero. La cible de
precision preenregistree de 0.045 est manquee d'un facteur 3.4 parce que la dispersion reelle a
L = 96 vaut huit fois l'estimation historique tiree de cinq bras. Le defaut de conception qui le
permet est identifie : la definition gelee d'un bras analysable admet un bras dont la population
s'est partiellement effondree, et |C-Y| y mesure le bruit du centre de Frechet plutot que la
geometrie du nuage — la correlation entre log N_X et log |C-Y| vaut -0.846. La disposition
DOMAIN_INVARIANCE_PARTIAL d'OBDI01 n'etait pas autorisee ; elle est adjugee DOMAIN_TEST_UNDERPOWERED.

OBDI01_REPORTED_DISPOSITION
DOMAIN_INVARIANCE_PARTIAL

OBDI01_ADJUDICATED_DISPOSITION
DOMAIN_TEST_UNDERPOWERED

PRIMARY_ESTIMAND
beta_CY : pente de log d_CY sur log L, ou d_CY(L) est la mediane par graine de |C-Y| sur les 180
trames de la fenetre, divisee par la prediction exacte de taille finie de l'operateur a cette
taille. C est le centre de Frechet toroidal du champ X ; Y est l'unique cellule organisatrice ;
|C-Y| est la distance euclidienne toroidale.

EQUIVALENCE_MARGIN
0.042 comme barre de qualification du mandat ; 0.250 comme marge gelee heritee et effectivement
testee. Les deux sont rapportees. Le chiffre 0.042 n'a jamais ete une marge gelee : c'est
l'exces de l'intervalle d'OBDI01 sur 0.250.

EQUIVALENCE_METHOD
TOST_90CI : forme par intervalle, alpha = 0.05 unilateral par test, intervalle bilateral a 90
pct, c = 1.64485, entierement inclus dans la marge. Unite = la graine.

POPULATION_SUPPORT_GATE
PASS

RELATIVE_ATTACHMENT_EQUIVALENCE
UNRESOLVED

DIRECT_DOMAIN_INVARIANCE
PASS pour la taille propre du nuage (R_g et r80, invariants a un pour cent pres) ; UNRESOLVED
pour l'ecart coeur-organisateur.

LEGACY_D_GATE_STATUS
MISALIGNED_WITH_DOMAIN_INVARIANCE

LEGACY_D_GATE_REPLICATION
NOT_PRIMARY. Rapporte : 29/46, 25/46, 34/46 bras passent, soit 36.2 pct d'echec global sur des
bras sains.

SOURCE_BOUND_LOCALIZATION
PARTIAL

DOMAIN_SIZE_INVARIANCE
PASS pour R_g, r80, la densite, le winding et le profil radial ; UNRESOLVED pour |C-Y|.

SOURCE_RESPONSE_OPERATOR_FULL
APPROXIMATE_WITH_EMPIRICAL_ERROR

AUTONOMOUS_COHESION_STATUS
NOT_ESTABLISHED

C3_STATUS
NOT_QUALIFIED

WHAT_IT_CHANGES
La mission separe proprement deux choses que la chaine confondait. La TAILLE du nuage est
invariante au domaine, et cela est maintenant etabli avec une precision vingt fois superieure a
celle d'OBDI01 sur 138 graines fraiches. L'ECART entre le centre estime du nuage et
l'organisateur ne l'est pas, et la mission montre pourquoi : ce n'est pas une propriete spatiale
mais un artefact d'effectif. Quand la population s'effondre partiellement sans s'eteindre, le
centre de Frechet devient une estimation bruitee et derive ; la correlation entre log N_X et
log |C-Y| vaut -0.846, et la mediane inter-bras de |C-Y| est parfaitement plate a 3.000, 3.081,
3.000. La question posee n'etait donc pas entierement une question de taille de domaine. Deux
defauts de reporting herites sont egalement fermes : la marge gelee et la notation ambigue.

NEXT_SCIENTIFIC_ELIGIBILITY
NONE

H3_STATUS
NOT_TESTED

REPRODUCTION_STATUS
NOT_TESTED

SCIENTIFIC_RUNS_USED
138 : confirmation 138, controle 0, calibration 0, sonde de cout 0, invalides 0. Quarante-six
bras a chacune des trois tailles. Les tests d'instrument et les relectures de donnees
enregistrees ne sont pas des demarrages.

SCIENTIFIC_EXTINCTIONS
9 au total : 3 a L=36, 4 a L=72, 2 a L=96. Aucune tendance avec L (p unilateral 0.595). Aucune
graine remplacee, aucune extinction supprimee.

TECHNICALLY_INVALID_RUNS
0

PROTOCOL_VIOLATIONS
NONE. Aucun seuil scientifique n'a bouge apres le gel, aucun run n'a ete relance, aucune graine
remplacee, aucun arret anticipe, aucune analyse intermediaire. Trois defauts de conception sont
consignes au paragraphe 35 : la definition d'un bras analysable qui admet un effondrement
partiel, la cible de precision manquee parce que la variance historique etait sous-estimee, et
la deviation declaree de la regle du plus petit n.

PROVENANCE_STATUS
SELF_CONTAINED_SPLIT_DELIVERY_PASS

TOMMY_ACTION_REQUIRED
NONE
```
