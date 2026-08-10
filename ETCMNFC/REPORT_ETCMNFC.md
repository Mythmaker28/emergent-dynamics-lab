# `EXACT_TWIN_CANONICAL_MF0_NATIVE_FLUX_CONFIRMATION_00` (ETCMNFC)

**Branche** `confirm/exact-twin-canonical-mf0-native-flux-00`
**Parent** `d86d24864e0f88c6483d11bcde601d1f13221a82` (ETNBFC) · **grand-parent**
`de1524b22ff917dff1da6553f778a4f8019ac273` (EEFCA)
**Autorisation** ce handoff, envoyé par Tommy · portée
`QUALIFICATION_PLUS_FIXED_PRIMARY_PLUS_CONDITIONAL_HELD_OUT`
**Identifiants primaires alloués** `0` · **géométrie tenue à l'écart** `intacte`

---

## 0. Résultat

**L'opérateur que Tommy a décrit existe, et il fonctionne.** La correction exécutive était juste :
`ΔQ_paire = (w_i − w_j)(x_j − x_i)`, donc des poids identiques suffisent et `ρ` égal n'a jamais
été nécessaire. La bifurcation que j'avais proposée à la fin d'ETNBFC — miroir **ou** réécriture
du noyau OFF — était un faux dilemme, et je le retire.

**Le programme s'arrête néanmoins, une porte plus loin, sur une obstruction nouvelle et
mesurée** : le point de mesure autorisé — le transfert matière–bain réalisé **par composante** —
a un **support vide**.

```
COUNTERFACTUAL_INFRASTRUCTURE   = VALID
CANONICAL_CARRIER_OPERATOR      = EXACT_CONSERVATIVE_BYTE_INVOLUTION
ON_NATIVE_FLUX_OBSERVER         = VALID_PASSIVE_EXACT
GAIN_ZERO_PUBLIC_PATH_EXCLUSION = PASS_BIT_EXACT   (cycle gelé, blocs de développement)
PRIMARY_NATIVE_BOUNDARY_FLUX    = NOT_IDENTIFIABLE
REPLICATION                     = NOT_REACHED
ETCMNFC_DISPOSITION             = NOT_IDENTIFIABLE
```

Quatre des cinq briques sont désormais bonnes. C'est la cinquième — la définition même du point de
mesure sur cette configuration — qui ne tient pas.

---

## 1. Ce que le programme a établi

### 1.1 L'opérateur (Phase B, `60/60` hors ligne, 0 démarrage moteur)

Transposition d'octets bruts de `Mf[0]` sur des paires inter-composantes appariées par le seul
algorithme gelé : cardinalité maximale, puis, parmi les appariements maximaux, celui dont la liste
triée de couples d'identifiants immuables est lexicographiquement minimale.

| bloc | paires | à `ρ` **inégal** | `ΔQ_A = −ΔQ_B` | déplacement brut |
|---|---|---|---|---|
| 61000 | 21 | **21** | ±14,4009 | publié |
| 61001 | 21 | **21** | ∓14,4481 | publié |
| 61002 | 21 | **21** | ±14,4989 | publié |
| 61003 | 21 | **21** | ∓14,3417 | publié |

Fraction de sites appariés : **21/21 par composante**, soit la totalité du support commun
disponible. Multi-ensemble brut préservé ; contenu rationnel exact `Q` préservé (accumulateur
`Fraction`, jamais `np.sum` ni tolérance) ; **involution bit-exacte sur l'état complet** ; seul
`Mf[0]` modifié ; projection publique bit-identique à `t0` ; aucun écrêtage.

Trois précisions que les relecteurs ont imposées et que j'adopte :

- **`Q` n'est pas un invariant dynamique.** L'opérateur le préserve **à `t0`** ; un pas natif le
  fait passer de 0,184192 à 0,152807. « Conservateur » ne veut pas dire « conservé ».
- **Ce n'est ni une transplantation de `z`, ni un échange de parcelles.** Les `ρ` étant inégaux,
  `z'_i = Mf[0]_j/ρ_i` : des valeurs intensives qui n'existaient nulle part. `ρ` est intouché.
- **L'appariement dépend de l'état.** L'*objectif* d'appariement ne lit aucune valeur (vérifié :
  matrice booléenne, invariance sous 200 réétiquetages), mais le *prédicat d'éligibilité* lit bien
  `ρ` et `Mf[0]` — l'autorisation le permet explicitement. Un relecteur a produit le
  contre-exemple : changer une seule valeur de `Mf[0]` change les paires choisies à cardinalité
  égale. **L'estimand est donc conditionnel à une politique d'appariement, et « la même
  intervention » d'un bloc à l'autre serait inexact.**

### 1.2 La sonde ON (Phase C, portes réécrites)

Fenêtre gelée : **exactement un pas natif**. Le pas contient exactement deux appels d'échange
(`_face_transport(c, kap)` puis `_face_transport(N, kap)`) et aucun limiteur n'agit sur les termes
de transport — le seul `np.clip` du pas porte sur l'absorption de croissance, plus tôt. Donc
`q_applied = dt·D_X·fl_e` est bien le transfert accepté.

`c` et `N` sont tous deux en **dépendance directe à `κ`**, via le **même** tableau `kap`, et la
mise à jour de `N` ne lit jamais le `c` déjà modifié : aucune médiation d'ordre intra-cycle.

### 1.3 L'exclusion OFF, sans inventer une seule face

Statiquement, à `gain == 0` le noyau retourne `lap(X)` sans lire `kap`, et la branche teste un
**paramètre**, pas un état. Dynamiquement, `OFF_SWAP` et `OFF_SHAM` ont des projections publiques
bit-identiques — `ρ, U, V, c, N, C, uptake` **et `Mf[1]`** — alors que `Mf[0]` diffère réellement.
Un relecteur a durci le test avec six perturbations dont une **injection de NaN** : aucune
n'atteint le moindre champ public. L'exclusion est **structurelle**.

Portée déclarée honnêtement : à `g = 0`, `κ(z,0) = 1` identiquement, donc cette porte est **proche
d'une tautologie**. Sa valeur est étroite mais réelle — elle exclut une fuite d'implémentation.
**Ce n'est pas un contrôle scientifique et elle ne dit rien des bras ON.**

---

## 2. L'incident qui compte : trois de mes portes ne pouvaient pas échouer

Les deux relectures indépendantes ont trouvé la même chose, et c'est le constat le plus important
de ce rapport.

| porte (premier jet) | pourquoi elle était vide |
|---|---|
| `F5` | comparait `recon` et `direct` : **la même expression évaluée deux fois sur la même entrée**. Passe sur du bruit aléatoire. |
| `F6` | `exact_sum(f) − exact_sum(roll(f,1,ax))` est identiquement nul pour **tout** tableau fini. C'était une propriété de `np.roll`. |
| `F2` | comparait `(out.rho>ε)` à `(tapped.rho>ε)` où `tapped is out`. |

C'est **exactement** le défaut que toute cette chaîne existe pour débusquer — EEFCA l'avait nommé
« une porte nommée qui ne testait pas la propriété qu'elle nomme », et l'avait qualifié de
constatation la plus grave de l'audit. Je l'ai reproduit trois fois, quatre programmes plus tard.

**Traitement.** Les portes vides sont **conservées au dossier** et déclarées `superseded`, jamais
effacées. Elles sont remplacées dans `etcmnfc_phaseC2.py` par des oracles qui **peuvent** échouer,
chacun assorti de son **contrôle négatif** :

| porte réécrite | ce qu'elle teste réellement | contrôle négatif |
|---|---|---|
| `F5_LEDGER_EQUALS_NATIVE_RETURN` | le registre reproduit le tableau **réellement retourné** par le noyau | une face décalée d'**un ulp** est rejetée |
| `F5_STATE_BUFFER_REPRODUCED` | `c` après la fenêtre est reconstruit depuis le seul registre, bit pour bit, et comparé au `c` du moteur | — |
| `F6_PAIRWISE_DEBIT_CREDIT` | perturber **une** face déplace exactement **deux** cellules, d'exactement `±` la même quantité, et ce sont les deux extrémités de cette face | comptage de cellules |
| `F2_MASK_CROSS_CHECK_VIA_KAPPA` | le masque enregistré est croisé avec un objet **indépendant**, le champ `κ` du noyau (`κ ≡ 1` exactement hors matière) | un masque corrompu en une cellule est rejeté |
| `O0` (`w ≡ 1`) | testé **par conséquence** : des poids non uniformes brisent la conservation sous la même permutation | — |

**14/14**, contrôles négatifs compris. Les faits que les portes vides prétendaient établir étaient
vrais — un relecteur l'a montré indépendamment — mais elles ne les établissaient pas.

Autres défauts signalés et corrigés : `transpose()` refuse désormais une liste de paires non
disjointe ; l'audit `O1` teste le type de la matrice d'éligibilité au lieu d'une liste noire de
noms ; la docstring « caractère pour caractère » est corrigée. Défauts consignés et **non**
corrigés, parce que sans effet sur une conclusion d'un programme qui s'arrête ici : recherches par
sous-chaîne restantes en `F0`/`F3`, fixtures adversariales qui ne traversaient pas l'opérateur,
code mort, `O11` impliquée par `O10`, hash de manifeste non auto-vérifiant.

---

## 3. L'arrêt : le point de mesure autorisé a un support vide

### 3.1 La mesure

Le prédicat matériel du noyau est `alive = ρ > 1e-4` — celui-là même qui construit `z`.

| bloc | régions matérielles connexes | A et B dans la **même** ? | liens matière–bain | liens **attribuables** à A ou B |
|---|---|---|---|---|
| 61000 | **1** | **oui** | 172 | **0** |
| 61001 | **1** | **oui** | 172 | **0** |
| 61002 | **1** | **oui** | 172 | **0** |
| 61003 | **1** | **oui** | 172 | **0** |

Zéro cellule de composante est adjacente à une cellule non vivante. Les extrémités matérielles des
172 liens sont à `ρ ≈ 1,3 × 10⁻⁴` ; le minimum de `ρ` **dans** A ou B est ≈ 0,30 — un facteur
≈ 2000. Les composantes sont enfouies **13 cellules de réseau** sous la frontière.

La porte `F10` exige que chaque événement inclus s'attache à exactement une composante gelée.
**0/172.** La somme du point de mesure est vide, donc identiquement nulle dans les deux bras :
exécuté tel quel, le test aurait renvoyé `p = 1,0` **par construction**, un « nul » de pure
vacuité définitionnelle.

### 3.2 Les deux sauvetages, testés et écartés

Un relecteur indépendant les a mesurés sur blocs de développement :

- **Point de mesure « total », sans attribution.** À la fenêtre gelée, `ON_SWAP` contre `ON_SHAM`
  au gain natif : **0 des 344 faces de frontière ne diffère**, pour les deux espèces, sur les deux
  graines. La perturbation atteint 2 cellules et s'arrête **8 cellules avant** le premier lien de
  frontière. Encore un nul garanti — pour une raison de localité de stencil. L'autorisation
  interdit d'ailleurs de réinterpréter en effet total.
- **Fenêtre plus longue.** Pire : l'écrivain contient `up_ref = float(uptake[alive].mean())`, une
  réduction de champ moyen **globale**. À `t = 1` seules 4,5 % des cellules vivantes ont un `z`
  perturbé ; à `t = 2`, `up_ref` diffère et **100 %** des cellules vivantes ont un `z` différent,
  les 344 faces de frontière diffèrent, et l'influence des deux composantes transite par le **même
  scalaire global**. L'attribution devient structurellement impossible.

**Conclusion, plus forte que `NOT_IDENTIFIABLE` seul :** le point de mesure a un support **vide** à
la fenêtre gelée, et **aucune fenêtre alternative ne restaure l'attribuabilité** dans cette
configuration — vide à `W = 1`, confondu globalement à `W ≥ 2`.

### 3.3 Ce que j'aurais dû faire plus tôt

Une vérification de cardinalité du support du point de mesure est une précondition d'une ligne.
Elle aurait dû précéder l'algorithme d'appariement, le protocole de scellement et la règle
co-primaire, au lieu d'arriver à la porte `F10` après tout cela. C'est un défaut d'ordonnancement
de ma conception, pas une malchance.

---

## 4. Sur la conception inférentielle, telle qu'elle était gelée

Elle n'a jamais été exécutée. La relecture causale l'a néanmoins attaquée, et ses constats
comptent pour la suite :

- Le modèle étant **déterministe**, sous l'hypothèse nulle nette `R = 0` exactement : la taille
  réelle du test de randomisation est **0**, pas 0,05. C'est un test des signes déguisé, `n = 10`,
  **aveugle à l'amplitude** (un étalement d'effets ×30 donne le même `p` qu'un étalement ×1,06).
  Le `p` n'ajoute rien que la bit-exactitude ne donne déjà plus fortement.
- `D` est **antisymétrique par construction** : tout mode commun s'annule. Or ce mode commun n'est
  pas nul (`Σκ(z)` change sous la permutation, et pas même de signe constant). Seule une
  affirmation *différentielle* aurait pu être autorisée.
- L'intervalle inversé est un intervalle de **décalage constant**, jamais un intervalle de
  confiance pour `θ`.
- `c` et `N` sont anti-corrélés au niveau des faces (`r ≈ −0,85`) : la règle co-primaire, correcte
  comme test intersection-union, est un contrôle de multiplicité quasi vide.
- `eta_X` n'est **pas** une borne d'erreur d'observateur — la sonde est bit-exacte, il n'y a pas
  d'erreur à borner. C'est un **seuil de matérialité**, et c'est lui, pas le `p`, qui aurait fait
  le travail scientifique.
- Le bit d'allocation scellé est un dispositif d'**aveuglement** contre le biais d'analyste. C'est
  sa fonction authentique ; le décrire comme une randomisation serait inexact.
- Point crédité : `s0` n'introduit **aucune circularité** — calculé depuis la ligne de base et le
  manifeste avant toute avance de branche. Réserve : sa condition `s0[A] = −s0[B]` est
  automatiquement satisfaite par `O8`, donc elle ne peut jamais exclure un bloc.

---

## 5. Registres

### Démarrages moteur

| poste | démarrages |
|---|---|
| Phase B, hors ligne (opérateur, `O0–O11`, adversariaux) | **0** |
| Phase C, première passe (sonde, exclusion OFF, jumeaux) | 12 |
| Phase C, seconde passe (oracles réécrits + contrôles négatifs) | 5 |
| **total du programme** | **17** (plafond de qualification 20) |
| contrastes cibles réduits en point de mesure | **0** |
| identifiants primaires avancés | **0** |
| blocs tenus à l'écart | **0** |
| parent ETNBFC, rapporté séparément et jamais reclassé | 8 |

**Écart de comptabilité déclaré.** Les deux relectures indépendantes exigées ont elles-mêmes
exécuté le moteur, sur blocs de développement, dans des bacs à sable séparés, en nombre non
individuellement compté (probablement plusieurs dizaines de branches d'un pas). Elles ont vérifié
un arrêt déjà déclenché et n'ont servi à sélectionner ni paire, ni fenêtre, ni signe, ni règle.
Je le déclare plutôt que de l'exempter en silence : c'est à Tommy d'en juger la conformité.

### Rôles des blocs

| identifiants | géométrie | rôle |
|---|---|---|
| `61000–61009` | FAR | `DEVELOPMENT_ONLY`, définitivement (ETPC exposés) |
| `61000–61003` | FAR | blocs de qualification de ce programme, `DEVELOPMENT_ONLY` |
| `62000–62009` | NEAR | `HELD_OUT_UNSEEN` — engagement d'identité **vérifié** (voir ci-dessous) |
| primaires | — | **non alloués** : arrêt en amont du gel |

`PARENT_HELD_OUT_IDENTITY_COMMITMENT` passe de `TO_BE_VERIFIED` à **`VERIFIED`** : `62000–62009`
et la classe `NEAR` sont écrits dans `ETPC/etpc_run.py`, dont le sha256 est dans le `code_sha256`
scellé de `ETPC/etpc_protocol.json`, commis en `3f8dae8b…`. Engagement auditable et antérieur aux
résultats.

**Limite déclarée sur la généralité de l'arrêt :** les quatre blocs de développement ont des
**ensembles de cellules A et B identiques** (mêmes 21+21 cellules, même pas). Le résultat
topologique est donc **`n = 1` en géométrie**, pas quatre observations indépendantes. Les valeurs
de champ diffèrent, la topologie non.

---

## 6. Affirmation maximale, et ce qui est proscrit

**Affirmation maximale défendable :** *dans un modèle construit explicitement, une redistribution
préenregistrée, admissible en domaine, exactement conservatrice du contenu pondéré et involutive
au niveau des octets du porteur canonique `Mf[0]` a été construite et qualifiée ; le point de
mesure matière–bain **par composante** préenregistré a un support **vide** dans cette
configuration, et aucune fenêtre alternative ne restaure l'attribuabilité ; le programme s'est
arrêté avant d'allouer le moindre identifiant primaire ; aucune affirmation n'est faite sur
l'effet de la redistribution sur le transport.*

Sont proscrits, quelle que soit la suite : « aucun effet » ; « aucune conséquence publique » sans
le qualificatif « à gain natif nul » ; « transplantation de `z` » ; « échange de parcelles
matérielles » ; « globalement conservateur » sans qualificatif ; la porte OFF présentée comme un
résultat de flux ; « 60/60 portes » placé près de la discussion du point de mesure — l'opérateur a
qualifié, l'expérience non. Et aucun vocabulaire de fonction, d'appartenance, d'individualité, de
clôture, de persistance sous renouvellement, d'autonomie, de métabolisme, d'organismalité, de
reproduction, d'hérédité, de vie, de conscience ou d'AGI : A et B sont 42 cellules définies par un
seuil, enfouies 13 cellules sous la surface d'**une seule** région matérielle de 1662 cellules.

---

## 7. Force du dossier, avant / après

| | avant | après |
|---|---|---|
| mécanisme causal `c`/`N` | non établi | **inchangé — rien n'a été mesuré** |
| opérateur conservateur involutif sur blocs réels | inconnu, cru impossible | **CONSTRUIT ET QUALIFIÉ, 60/60** |
| sonde de flux natif ON | non testée | **VALID_PASSIVE_EXACT**, oracles avec contrôles négatifs |
| exclusion publique à gain nul | registre par face jugé nécessaire | **PASS_BIT_EXACT** sans inventer de face |
| faux dilemme miroir / réécriture OFF | proposé | **RETIRÉ** |
| identifiabilité du point de mesure autorisé | inconnue | **RÉSOLUE : support vide, avec la mesure** |
| discipline des oracles | crue acquise | **défaillance reproduite, détectée par relecture, corrigée** |

Solde : **positif sur l'outillage, nul sur la question causale**, et négatif d'un point sur la
confiance qu'on peut accorder à mes portes sans relecture indépendante — ce qui est en soi le
résultat le plus utile de la journée.

---

## 8. Arrêts déclenchés

```
PRIMARY_ESTIMAND_NOT_IDENTIFIABLE     (pré-cible, à la porte F10, aucun identifiant primaire alloué)
```

Non déclenchés : `TARGET_OPENED_BEFORE_FREEZE`, `HELD_OUT_PEEK_BEFORE_PRIMARY_PASS`,
`PRIMARY_BLOCK_REPLACEMENT`, `QUALIFICATION_BUDGET_EXHAUSTED`,
`CANONICAL_CONTENT_SEMANTICS_UNRESOLVED`, `CANONICAL_REDISTRIBUTION_UNAVAILABLE`,
`ON_OBSERVER_NOT_PASSIVE`, `GAIN_ZERO_PUBLIC_PATH_EXCLUSION_FAIL`.

Aucune réparation n'est tentée sous cet identifiant : ni monde miroir, ni refonte OFF, ni
changement de gain, ni point de mesure approché, ni fenêtre allongée, ni nouvel opérateur, ni
normalisation, ni sous-groupe, ni sauvetage unilatéral, ni remplacement de bloc.

---

## 9. Artefacts

| fichier | rôle |
|---|---|
| `etcmnfc_protocol.json` + `.sha256` | portée, gel, interdits, empreintes de code |
| `etcmnfc_core.py` | sémantique, arithmétique exacte, éligibilité, appariement gelé, opérateur, sonde |
| `etcmnfc_gates.py` / `etcmnfc_gates_offline.json` | `O0–O11` + adversariaux, **60/60**, 0 démarrage |
| `etcmnfc_phaseC.py` / `.json` | première passe — **contient les trois oracles vides, conservés** |
| `etcmnfc_phaseC2.py` / `.json` | oracles réécrits avec contrôles négatifs, **14/14** |
| `probe_alive_topology.json`, `probe_attribution.json`, `probe_depth.json` | les mesures de l'arrêt |
| `REVIEW_1_NUMERICAL_ORACLE.md` | relecture indépendante 1 (numérique / oracles) |
| `REVIEW_2_CAUSAL_STATISTICAL.md` | relecture indépendante 2 (causale / statistique) |
| `ETNBFC_CORRIGENDUM.md` | corrigendum borné du parent, six points |
| `REPORT_ETCMNFC.md` | le présent rapport |
| `etcmnfc_verify.py` / `.json` | vérificateur indépendant |
| `SHA256SUMS` | empreintes de tous les artefacts |
