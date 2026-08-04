# FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00 — rapport

> ## Disposition : `ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_CARRIED_OBLIGATIONS_CLOSED`
>
> Les **six obligations PRB-A … PRB-F** transportées par la revue humaine 01S sont fermées,
> mécaniquement et sémantiquement, chacune avec sa preuve et ses tests de frontière.
>
> **`scientific_run_authorized = false`.** Aucune famille, aucun seed scientifique, aucun
> namespace, aucune loi, aucune condition initiale, aucun monde n'a été créé.
>
> Les six `PRE_RUN_BLOCKER` gelés **PRB-1 … PRB-6** de la décision 01S **restent ouverts**.
> Cette mission n'était pas mandatée pour les fermer et ne les ferme pas.

---

## 0. Distinction imposée, appliquée à tout ce document

1. **Preuve mécanique** — une propriété du logiciel sur fixtures fabriquées, établie par un
   test. Vaut pour son domaine testé. N'est jamais l'observation d'un phénomène.
2. **Décision de gouvernance** — un choix prospectif déclaré avant toute exécution, justifié
   sans consulter le moindre résultat scientifique fermé.
3. **Résultat scientifique** — une propriété du substrat établie par une famille prospective
   préenregistrée. **Cette mission n'en produit aucun.** Il n'en existe aucun pour Route E.

---

## 1. Autorité, lignée, portée

| Élément | Valeur vérifiée |
|---|---|
| Record accepté | `docs/individuation/FUTURE_PROSPECTIVE_AXIS_CONVENTION_AND_FRAME_CLOSURE_01S_HUMAN_REVIEW.md` |
| Commit de décision parent | `00afcdd1aacbdf32bb030d85ced735a2920421f6` |
| Parent unique de ce commit | `63c371d52036c7e91ec928118c2b8901776d79d0` |
| Ancestry vérifiée | `63c371d5` est ancêtre de `00afcdd1` ; chaîne linéaire, aucun merge |
| `main` | `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77` — **immobile**, working tree sale **préservé** |
| Branche de cette mission | `codex/future-route-e-pre-run-blocker-closure-00`, créée depuis `00afcdd1` et depuis rien d'autre |

**L'autorisation existe et est exclusive.** Le §8 du record accepté énonce littéralement :
*« Autorisée, et seule autorisée : `FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00` »*, et
énumère les six obligations portées à cette mission. La portée est donc dérivable, et elle
est dérivée du record, pas inventée ici.

**Les six obligations, telles que le record accepté les nomme** (§8, littéral) :

1. *Chiffrer les deux seuils non chiffrés (A16 / B16) : fraction de censure et concordance
   inter-CI, avec un repère non biaisé au sens de Jensen.* → **PRB-A**
2. *Nommer le générateur externe, l'ordre des tirages et la stratégie de seed enregistrée
   (L-HR2), sachant que le moteur n'a aucun RNG et qu'une réplication est un nouveau tirage
   préenregistré, jamais un pseudo-seed.* → **PRB-B**
3. *Faire du prédicat d'acceptation du sampler la construction du `LatticeBondSpec` par le
   moteur lui-même (L-HR1), afin que l'ensemble échantillonné soit par définition exactement
   l'ensemble admis, et que l'écart d'un ulp à la frontière disparaisse.* → **PRB-C**
4. *Préenregistrer la rupture de track par la porte d'association comme cause d'un nul
   (B17).* → **PRB-D**
5. *Dire de quel `Δ` parle le plafond de claim sous la règle d'invariance de
   `cohort_residual_fraction` (A18).* → **PRB-E**
6. *Nommer `run_owned_future_pipeline` dans le test de refus de PRB-5 (B15).* → **PRB-F**

**Ce que ces six obligations ne sont pas.** Elles ne sont **pas** les six `PRE_RUN_BLOCKER`
gelés `PRB-1 … PRB-6` du JSON 01S (jointure track–composant persistée ; receipt
obligatoire ; ordre de checks gelé ; liaison anti-replay ; point d'entrée unique ; ancrage
externe). Seul `PRB-5` est touché ici, et seulement par la déclaration hors protocole et le
test de refus de PRB-F. **PRB-1, PRB-2, PRB-3, PRB-4 et PRB-6 restent entièrement ouverts,
et PRB-5 reste ouvert lui aussi** (§9). Confondre les deux séries serait exactement le
maquillage que la Partie I §15 de 01S interdit.

### 1.1 Allowlist, écrite avant la première édition

| # | Chemin | Nature | Statut |
|---|---|---|---|
| 1 | `edlab/substrates/lattice_bond/future_route_e_pre_run_frame.py` | **nouveau** module | ajouté |
| 2 | `tests/test_future_route_e_pre_run_blocker_closure_00.py` | **nouveau** fichier de tests | ajouté |
| 3 | `docs/individuation/FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_REPORT.md` | **nouveau** document | ajouté |
| 4 | `docs/individuation/FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_DECISION.json` | **nouveau** document | ajouté |

**Additive seulement. Zéro modification, zéro suppression.** Ne sont pas modifiés, et n'ont
pas été modifiés : `engine.py` ; `edlab/specs.py` ; `edlab/state.py` ; `instrumentation.py` ;
`lifecycle.py` ; `future_lifecycle_runner.py` ; `future_lifecycle_owned_pipeline.py` ;
`future_prospective_measurement_bridge.py` ; tout `__init__.py` ; `pyproject.toml` ; tout
test existant ; tout document historique ; tout record 01S accepté.

L'allowlist est dérivée du firewall gelé (01S Partie I §16 : aucune modification du moteur,
du cycle de vie, de Stage B ou d'un paquet scientifique accepté) et de la contrainte
structurelle de PRB-F, qui exige un test exerçant une entrée publique réelle et donc un
nouveau fichier de tests. Aucune extension silencieuse n'a eu lieu.

---

## 2. Décisions 01S rouvertes : aucune

Rien de ce qui suit n'a été rouvert, amélioré, réinterprété ou recalculé :
67 tirages de loi · 2 CI par loi · 134 mondes · lattices carrées {16, 24, 32} ·
horizon 1024 · cadence 16 · `POSITIF k ≥ 42` · `NÉGATIF k ≤ 9` · `INDÉTERMINÉ 10 ≤ k ≤ 41` ·
`Δ₀ = 0,50` · `Δ₁ = 0,25` · ensemble de sensibilité `{0,01 ; 0,05 ; 0,20}` ·
`Y_i = 1{D(loi_i, L_i, X_i1) = 1}` · `k = Σ Y_i`.

Ces valeurs sont **restituées** dans le module comme constantes, jamais recalculées. Les
seuils Clopper–Pearson gelés sont **re-vérifiés** par une implémentation indépendante
(bissection sur la queue binomiale exacte via `math.comb`, sans dépendance tierce) et
reproduits à mieux que `1e-12` : `0,5001047440198192` (k = 42), `0,4850181325667385`
(k = 41), `0,2397417520625535` (k = 9), `0,2574024526077781` (k = 10).

**La seconde condition initiale n'a été transformée en rien.** Le module ne contient aucun
chemin par lequel `X_i2` deviendrait une réplication, un motif d'exclusion, un remplaçant
de `X_i1` ou un sélecteur du meilleur des deux mondes. C'est pinné structurellement :
`classify_ic_dependence` ne prend qu'un compte de discordances, ne retourne que des
étiquettes, et son code ne contient aucune référence à `Δ` ni au nombre 134.

---

## 3. PRB-A — les deux seuils non chiffrés

### 3.1 Ce que le record accepté nomme

Limitation **A16 / B16**, littéralement : *« Deux seuils de Route E ne sont pas chiffrés :
la fraction de censure et la concordance inter-CI. Ils ne gouvernent **pas** la décision
`POSITIF/NÉGATIF/INDÉTERMINÉ` mais l'**attribution de cause** d'un nul, et les deux
fractions concernées sont co-primaires obligatoires. De plus le repère de concordance
proposé est biaisé au sens de Jensen vers "pas de dépendance aux CI". **À chiffrer à la
prérégistration** »*.

Les noms et les rôles viennent de là. Rien n'a été inventé à partir du handoff.

### 3.2 Seuil 1 — `HORIZON_CENSORING_ATTRIBUTION`

| Champ | Valeur |
|---|---|
| Quantité | fraction des 67 tirages primaires dont le composant éligible n'atteint jamais le remplacement matériel vérifié avant le pas 1024 |
| Unité | fraction sans dimension, compte de tirages censurés divisé par 67 |
| Domaine | `[0, 1]` |
| **Valeur** | **`25/67 = 0,3731343283582090`** |
| Comparaison | **strictement supérieure** |
| Frontière | **stricte**. Exactement `25/67` n'est **pas** attribué : à `C = 25`, le bras POSITIF reste atteignable à `k = 42` |
| NaN / ±∞ / hors domaine | **fail-closed** : lève. Aucun clamp, aucun défaut, aucune coercition silencieuse |
| Gouverne la décision ternaire | **non** |
| Digest | `04cd442db8dcc518f9c2be044e79ba5256cd26a2bc00039fac845db82b209817` |

**Dérivation, sans aucune donnée scientifique.** Un tirage censuré sur le turnover vaut 0.
Avec `C` tirages censurés parmi `n = 67`, nécessairement `k ≤ 67 − C`. Le bras POSITIF exige
`k ≥ 42`. Il est donc arithmétiquement inatteignable exactement quand `67 − C < 42`, soit
`C > 25`, soit `C ≥ 26`, soit `C/67 > 25/67`. **Seuls la taille gelée 67 et la coupure gelée
`k ≥ 42` entrent.** Rien d'autre.

### 3.3 Seuil 2 — `IC_DISCORDANCE`

Le biais de Jensen identifié par A16 vient de comparer la concordance observée à un repère
construit en injectant l'estimation **marginale** dans `π² + (1−π)²`, alors que
`E[π² + (1−π)²] ≥ Δ² + (1−Δ)²` par convexité. **La réparation est de supprimer le repère**,
et d'estimer directement la probabilité de discordance :

> `ψ = P(Y_i1 ≠ Y_i2) = E[2 π_i (1 − π_i)]`, avec `ψ ∈ [0, 1/2]`

`d/67`, où `d` compte les paires de lois discordantes, est un estimateur **exactement sans
biais** de `ψ` sous la loi de tirage déclarée. Aucune étape de convexité n'est franchie, donc
aucun biais de Jensen ne subsiste. `ψ = 0` signifie que l'outcome est fonction de
`(loi, taille)` seules ; `ψ = 1/2` est le bruit intra-loi maximal (`π ≡ 1/2`).

| Champ | Valeur |
|---|---|
| Quantité | `ψ = P(Y_i1 ≠ Y_i2)`, estimée sans biais par `d/67` |
| Unité | probabilité sans dimension |
| Domaine | `[0, 1/2]` — borne atteinte, `2π(1−π)` étant maximal en `π = 1/2` |
| **Frontières** | **`ψ₀ = 1/4`** et **`ψ₁ = 1/8`** |
| Règle | `MATERIAL` ssi `CP inf(d,67) > 0,25` ; `NEGLIGIBLE` ssi `CP sup(d,67) < 0,125` ; `INDETERMINATE` sinon |
| Régions | **`MATERIAL : d ≥ 25`** · **`NEGLIGIBLE : d ≤ 2`** · **`INDETERMINATE : 3 ≤ d ≤ 24`** |
| Frontière | **stricte** sur les bornes exactes ; une borne tombant exactement sur `0,25` ou `0,125` verse dans `INDETERMINATE` |
| NaN / hors domaine | **fail-closed** : `d` doit être un `int` simple dans `[0, 67]` |
| Gouverne la décision ternaire | **non** |
| Digest | `e3e9abf96ff5da1699f35aec40d2eb4a26d744dd3141e42dc601d68a32393575` |

**Dérivation, sans aucune donnée scientifique.** La **même** convention du point milieu
d'identifiabilité que le paquet a déjà gelée pour `Δ`, appliquée à la plage propre de `ψ` :
`ψ₀` = milieu de `[0, 1/2]` = `1/4` ; puis `ψ₁` = milieu de `[0, 1/4]` = `1/8`. Exactement la
construction qui a donné `Δ₀ = 1/2` et `Δ₁ = 1/4` sur `[0, 1]`.

**Bornes exactes, recomputées ici :** `CP inf(25,67) = 0,257974…` `> 0,25` et
`CP inf(24,67) = 0,244695…` `≤ 0,25` ; `CP sup(2,67) = 0,103708…` `< 0,125` et
`CP sup(3,67) = 0,125327…` `≥ 0,125`.

### 3.4 Limitation déclarée, non maquillée — **RE-L1**

La largeur d'indifférence du discriminateur est `0,25 − 0,125 = 0,125`. Le **principe de
précision** du paquet exigerait une demi-largeur pire-cas `≤ 0,0625`. La demi-largeur
pire-cas atteignable à `n = 67` est **`0,124721195…`**. Le discriminateur est donc
**sous-dimensionné au regard du principe de précision du paquet lui-même**.

`n = 67` est gelé et ne peut pas être changé ici ni à la prérégistration. Le discriminateur
est secondaire, il ne gouverne jamais `POSITIF/NÉGATIF/INDÉTERMINÉ`, et cette limitation est
**déclarée** plutôt que réparée. Elle est pinnée par le test `test_prb_a_12`, qui échouerait
si quelqu'un prétendait plus tard que la précision est atteinte.

**Ce que cela veut dire concrètement.** Le discriminateur pourra dire « dépendance aux CI
matérielle » ou « négligeable » quand `d` est extrême, et dira honnêtement
`INDETERMINATE` sur toute la plage `3 ≤ d ≤ 24`, qui est large. Il ne faudra pas lire un
`INDETERMINATE` comme « pas de dépendance aux CI ».

### 3.5 Interdiction de modification après observation

Les deux `ThresholdSpec` sont des dataclasses gelées portant un **digest SHA-256** de leur
contenu décisionnel. Les deux digests sont inscrits dans le `DECISION.json` de cette mission
et dans ce rapport. Toute valeur, comparaison, frontière ou politique NaN modifiée après
l'observation change le digest et est immédiatement détectable par diff contre ce commit.

---

## 4. PRB-B — générateur externe, ordre des tirages, stratégie de seed

Rien de ce qui suit ne crée un seed scientifique, une famille, un namespace, une `LawSpec`
concrète, une CI concrète ou un monde. Le module **n'effectue aucun accès réseau** ; les
octets du beacon sont un argument.

### 4.1 Générateur

| Champ | Valeur |
|---|---|
| Algorithme | **SHA-256 en mode compteur** |
| Spécification | **FIPS 180-4** |
| Implémentation | `hashlib.sha256`, bibliothèque standard |
| Étiquette de version | `EDLAB-ROUTE-E-DRAW/v1` |
| Indépendance de version | la sortie SHA-256 est fixée par FIPS 180-4 : aucune version de bibliothèque, aucune plateforme, aucun build numpy ne peut changer un seul octet dérivé |
| Bloc | `block(seed_root, domain, index) = sha256(seed_root ‖ 0x00 ‖ domain ‖ 0x00 ‖ uint64_be(index))` |
| Uniforme | `u = int.from_bytes(block[0:8], 'big') / 2⁶⁴`, rationnel dyadique dans `[0,1)`, **64 bits** de résolution |
| Endianness | **big-endian** pour tout entier entrant dans un hash ou dans un uniforme |
| Sérialisation | octets bruts uniquement ; aucun JSON, aucune locale, aucun formatage flottant nulle part |

### 4.2 Origine de l'entropie : indépendante, future, publiquement vérifiable

| Champ | Valeur |
|---|---|
| Source | **drand, League of Entropy — chaîne `quicknet`** |
| `chain_hash` | `52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971` |
| Schéma | `bls-unchained-g1-rfc9380` |
| Période | **3 s** · `genesis_time` **1692803367** (Unix) |
| Clé publique | `83cf0f2896adee7eb8b5f01fcad3912212c437e0073e911fb90022d3e760183c8c4b450b6a0a6c3ac6a5776a2d1064510d1fec758c921cc22b0e17e63aaf4bcb5ed66304de9cf809bd274ca73bab4af5a6e9c76a4bc09e76eae8991ef5ece45a` |
| **Règle de round** | le **premier** round dont l'instant `t(r) = genesis + (r−1)·période` est **au moins égal à `T`**, où `T` = timestamp de committer du commit de prérégistration accepté **+ 86 400 s** |
| Pourquoi la valeur est inconnaissable aujourd'hui | le beacon de ce round **n'existe pas** tant que le round n'est pas émis, ce qui est strictement postérieur à l'écriture et à l'ancrage du commit de prérégistration |
| Vérifiabilité publique | la signature du round se vérifie contre la clé publique fixe (BLS sur G1, RFC 9380) et `randomness = sha256(signature)` : **aucun secret n'est requis** |

La source, l'instant et la fonction de dérivation sont donc **figés prospectivement**, sans
que quiconque puisse connaître aujourd'hui la valeur qui en sortira.

### 4.3 Dérivation, unique

```
seed_root = sha256( "EDLAB/ROUTE_E/v1" ‖ 0x00 ‖ chain_hash(32) ‖ uint64_be(round)
                    ‖ beacon_randomness(32) ‖ preregistration_commit_sha1(20) )
```

Fail-closed sur chaque longueur et chaque type. Il n'existe **qu'une seule** fonction de
dérivation dans le module — pinné par test.

### 4.4 Ordre canonique de tous les tirages

1. **Lois** — pour `i = 0…66`, consommer des propositions du domaine `LAW` à des indices
   `j = 0, 1, 2, …` **strictement croissants** ; le compteur de propositions **n'est jamais
   remis à zéro** et les propositions rejetées sont **consommées**, jamais réordonnées ; la
   loi `i` est la `i`-ième proposition **acceptée**.
2. **Tailles** — `L_i = LATTICE_SIZES[⌊3·u(SIZE, i)⌋]`, `u` uniforme sur `[0,1)`.
3. **CI** — les deux indices de flux de la loi `i` sont `2i` et `2i+1` : **`2i` est `X_i1`
   et sert le primaire**, **`2i+1` est `X_i2` et sert le discriminateur seulement**.
4. **Mondes** — exécutés dans l'ordre lexicographique `(indice de loi, ordinal de CI)` :
   `(0,0), (0,1), (1,0), (1,1), …, (66,0), (66,1)` — **134 mondes**.

### 4.5 Comportement en cas de rejet du sampler

Une proposition rejetée est **consommée** : l'indice avance, l'indice de loi n'avance pas.
Aucun ré-échantillonnage, aucune permutation, aucune ré-utilisation d'un bloc. La séquence
d'indices acceptés est strictement croissante et sans doublon — pinné par test.

### 4.6 Mécanisme empêchant le reroll

Le `seed_root` lie **le hash du commit de prérégistration** et **un round de beacon qui
n'existe pas encore** au moment où ce commit est écrit. Tout reroll change soit le commit,
soit le round — l'un et l'autre publics — et donc **chaque octet dérivé**. Une seule
dérivation est permise et doit être enregistrée dans le manifeste de famille **avant le
premier pas moteur**. Le module ne contient **aucun** second chemin de dérivation.

### 4.7 Preuve que l'ordre ne dépend d'aucun résultat

`build_draw_plan` ne prend que `(seed_root, count)`. Il n'appelle aucun `engine.step`, ne lit
aucun monde, n'ouvre aucun fichier et ne reçoit aucun outcome. L'admissibilité est un
**prédicat pur sur une proposition**, évalué avant qu'aucune simulation n'existe. Aucun
`Y_i`, aucun `k`, aucun état terminal, aucune mesure ne peut donc influencer quelle loi,
quelle taille ou quelle condition initiale est tirée, ni dans quel ordre.

**Preuve mécanique** (`test_prb_b_10`) : `LatticeBondEngine.step` est remplacé par une
fonction qui lève ; le plan se construit quand même, avec **0 appel**.
**Preuve mécanique** (`test_prb_c_10`) : `builtins.open` est remplacé par une fonction qui
lève ; le plan se construit quand même, avec **0 ouverture de fichier**.

---

## 5. PRB-C — le prédicat d'acceptation **est** le moteur

### 5.1 Architecture, en deux conjoints explicitement séparés

L'acceptation d'une proposition est **`in_proposal_box(fields) ∧ engine_accepts(fields)`**,
dans cet ordre et dans aucun autre.

- **Conjoint 1 — appartenance à la boîte de conception.** Le plafond d'affinité
  `θ̂_m + θ̂_n < 2·ln(H/4) = 11,090354888959125` est une contrainte de **résolvabilité
  déclarée par le design**, pas une borne de source : **le moteur n'en sait rien**. Le
  sampler doit donc la tester. Ce prédicat ne contient **aucune** réimplémentation de (B1)
  ni de (B2) — pinné par test (`test_prb_c_14` : ni `exp`, ni les coefficients de B1/B2 dans
  son source).
- **Conjoint 2 — admissibilité.** `engine_accepts` **construit le véritable
  `LatticeBondSpec`** et n'est rien d'autre que le verdict du moteur. `AdmissibilityError`,
  `ValueError`, `TypeError`, `OverflowError`, `ArithmeticError` sont **tous** des refus.
  Aucune exception ne s'échappe en acceptation ; aucune n'est avalée en défaut.

Il n'existe **aucun second moteur**. `algebraic_b1_b2` existe **uniquement** pour rapporter
une statistique d'accord ; elle n'est jamais sur le chemin d'acceptation — pinné par
`test_prb_c_07`, qui la remplace par une fonction qui lève et construit le plan quand même.

### 5.2 Preuves mécaniques

| Fait | Mesure |
|---|---|
| `objet moteur accepté → tirage accepté` et `validation refusée → tirage refusé` | **400 propositions**, **0 divergence** (`test_prb_c_02`) ; et **40 000 propositions** en mesure hors suite, **0 divergence** |
| NaN, +∞, −∞ sur `dt`, `kappa_m`, `theta_m`, `epsilon_b`, `resource_leak_floor` | **15 combinaisons, toutes refusées** (`test_prb_c_04`) |
| champ inconnu | refusé, `TypeError` (`test_prb_c_05`) |
| overflow (`θ = 1e308`) | refusé (`test_prb_c_06`) |
| loi inadmissible (`κ̂ = 10` à `dt = 1`) | refusée, `AdmissibilityError` (`test_prb_c_03`) |
| **frontières `nextafter`** | (B1) et (B2), **48 points** au voisinage représentable exact des deux coupures : **0 divergence** entre le chemin d'acceptation et le moteur |
| accord moteur ↔ prédicat algébrique | **40 000 / 40 000**, **0 désaccord** |
| aucune ouverture de fichier pendant la construction du plan | **0** (`test_prb_c_10`) |

**L'écart d'un ulp annoncé par RE-L1 de la revue humaine 01S disparaît** : puisque le gate
**est** la construction du moteur, l'ensemble échantillonné est **par définition** exactement
l'ensemble que le moteur admet. Le prédicat algébrique n'est plus qu'un témoin, et il est
d'accord partout où il a été mesuré.

### 5.3 Correction d'un défaut introduit puis attrapé dans cette mission

La première version du sampler tirait `θ̂_n` **conditionnellement** à `θ̂_m`
(`θ̂_n ~ U[0, cap − θ̂_m]`). C'est **faux** : cela donne sur le triangle admissible une
densité proportionnelle à `1/(cap − θ̂_m)`, donc **une autre loi que l'uniforme gelée**. Le
défaut a été trouvé et corrigé avant tout scellement : les neuf coordonnées sont désormais
tirées **indépendamment et uniformément sur la boîte produit**, et le plafond triangulaire
est imposé **par rejet**, ce qui préserve l'uniformité exactement.

Preuves mécaniques de la correction : marginale de `θ̂_m` plate sur 20 000 tirages
(`χ² = ` en dessous du quantile 0,999 à 9 degrés de liberté, `test_prb_c_12`) ; environ la
moitié de la masse tombe hors du triangle et est rejetée (`test_prb_c_13`) ; les deux
moitiés d'aire égale du triangle accepté reçoivent des masses à moins de 5 % l'une de
l'autre sur 20 000 tirages (`test_prb_c_17`).

### 5.4 Efficacité du sampler — **et uniquement cela**

Sur **40 000 propositions** issues d'une racine **synthétique** : appartenance à la boîte
**0,5016**, efficacité globale **0,1007**. Sur un plan complet à 67 lois issu de la même
racine synthétique : **735 propositions consommées**, efficacité **0,0912**, **19 ms**.

**Ces nombres sont l'efficacité estimée du sampler par rejet, et rien d'autre.** Ce ne sont
pas des constantes de normalisation, pas une mesure de `A`, pas des résultats scientifiques.
Ils ne remplacent ni ne contredisent le `0,099` de 01S, qui était l'estimation de 01S sous sa
propre paramétrisation de proposition, moins complètement épinglée que celle-ci. Leur seul
usage légitime est de dimensionner le coût du tirage à la prérégistration.

---

## 6. PRB-D — rupture de track par la porte d'association

### 6.1 Mécanisme, établi depuis la source acceptée

Quand **toutes** les arêtes candidates issues d'un composant de gauche sont refusées par la
porte d'association, le tracker émet un événement **`DISSOLUTION`** pour ce track au frame de
droite, tandis que la matière survivante est ré-enrôlée comme un track **`APPEARANCE`**
flambant neuf. L'état terminal est `DISSOLVED_DETECTED_TRACK` **alors qu'aucune matière n'a
disparu**. C'est exactement le mécanisme documenté par `fact20` de 01S.

### 6.2 Cause terminale prospective, explicite et non nulle

> **`ASSOCIATION_GATE_TRACK_BREAK`**

Un track reçoit cette cause **si et seulement si** les trois conditions tiennent :

1. son événement terminal est `DISSOLUTION` au frame `f` ;
2. **au moins une arête candidate** issue du composant dissous a été refusée avec une raison
   dans `{REJECT_CENTROID_DISTANCE, REJECT_AREA_RATIO}` — c'est-à-dire qu'un support
   géométrique **existait** et que la **porte** l'a refusé, par opposition à
   `REJECT_NO_GEOMETRIC_SUPPORT` ou à l'absence totale de candidat, qui sont de véritables
   disparitions ;
3. la cible de cette arête refusée est un composant du frame `f` qui a ouvert un **nouveau**
   track par un événement `APPEARANCE` en `f`.

La condition 2 est la discriminante : elle sépare mécaniquement « la porte a rompu le lien »
de « la matière a disparu ».

### 6.3 Les quatre interdits, tenus

- **Ne disparaît pas du dénominateur** — c'est une étiquette de cause posée sur un
  enregistrement terminal, pas une exclusion. Le dénominateur reste fixé à l'enrôlement.
- **N'est pas reclassée après observation** — la règle est une **fonction pure** de
  l'artefact de tracking, calculée une fois. Idempotence pinnée par `test_prb_d_04`.
- **N'est pas confondue avec une réussite** — `TrackTermination` **lève** si l'on tente de
  construire une cause avec `scores_one=True` (`test_prb_d_06`). Seul
  `RIGHT_CENSORED_AT_HORIZON` **avec** remplacement vérifié peut valoir 1.
- **N'est pas silencieusement imputée à une autre cause** — une disparition réelle garde
  `DISSOLVED_DETECTED_TRACK` sans étiquette de porte (`test_prb_d_02`), et un track qui
  continue ne produit aucune cause terminale (`test_prb_d_03`).

### 6.4 Preuves mécaniques, fixtures synthétiques uniquement

| Fixture (16×16, synthétique) | Résultat |
|---|---|
| blob 2×2 en `(0,0)` puis en `(0,8)` — distance périodique **8 > 3,0** | arête refusée `REJECT_CENTROID_DISTANCE` présente ; cause `ASSOCIATION_GATE_TRACK_BREAK` émise ; état terminal `DISSOLVED_DETECTED_TRACK` ; `scores_one = False` |
| blob puis frame vide | **aucune** étiquette de porte ; `DISSOLVED_DETECTED_TRACK` conservé |
| blob puis blob décalé d'une cellule | aucune cause terminale de porte ; le track continue |
| les trois fixtures | tout état terminal appartient aux **cinq** états gelés du contrat de cycle de vie |

Le lifecycle et le tracker acceptés ne sont ni modifiés ni contournés : le classificateur
**lit** `TrackingResult` et n'écrit rien.

---

## 7. PRB-E — ce que `Δ` signifie, et le plafond

### 7.1 Définition littérale

| Question | Réponse scellée |
|---|---|
| **Que compare `Δ`** | la proportion de tirages où le critère binaire déclaré tient, **contre les deux frontières gelées** `Δ₀ = 0,50` et `Δ₁ = 0,25`. Elle ne compare **rien** à un groupe contrôle, à une famille historique ou à une autre route |
| **À quel niveau** | **le tirage**, c'est-à-dire un triplet `(loi_i, L_i, X_i1)`. Jamais l'entité, jamais le composant, jamais le track, jamais la cellule |
| **Critère** | au moins un composant éligible du monde satisfait **persistance** (`RIGHT_CENSORED_AT_HORIZON`, observé continûment jusqu'au pas 1024) **et** **remplacement matériel vérifié** (`cohort_residual ≤ f`) |
| **Signe** | **non négatif par construction** : `Δ(f)` est une probabilité dans `[0,1]`. Elle n'a pas de direction et n'est pas une différence de deux quantités |
| **Unité** | probabilité sans dimension |
| **Agrégation** | un Bernoulli par loi, `k = Σ` de 67 indicateurs, estimée par `k/67` avec un intervalle Clopper–Pearson exact bilatéral à 95 %. **La seconde CI ne contribue en rien à `k`** |

### 7.2 De quel `Δ` parle le plafond — réparation de A18

`f` est `cohort_residual_fraction`, convention de mesure déclarée, ensemble de sensibilité
`{0,01 ; 0,05 ; 0,20}`. `Δ` est **monotone non décroissante en `f`** (un seuil plus permissif
ne peut pas retirer de succès). Donc, par emboîtement :

> **le bras POSITIF est lié par `Δ(0,01)`** · **le bras NÉGATIF est lié par `Δ(0,20)`**

Une conclusion doit tenir aux **trois** valeurs, sinon la famille rapporte
`INDÉTERMINÉ — CONVENTION_DE_REMPLACEMENT`. **Aucun « `Δ` » non qualifié ne peut être cité** :
un POSITIF autorise un énoncé sur `Δ(0,01)`, un NÉGATIF sur `Δ(0,20)`.

### 7.3 Lien avec le discriminateur de seconde CI

`ψ = P(Y_i1 ≠ Y_i2)` est une quantité **séparée**, avec sa propre attribution ternaire.
`ψ` **n'entre jamais** dans `Δ`, **n'entre jamais** dans `k`, et **ne peut jamais** retirer
une loi du dénominateur. Un `ψ` matériel **n'invalide pas** `Δ` : il **plafonne la lecture**
de `Δ` à la marginale sur les conditions initiales — ce que `Δ` est déjà. Il interdit en
particulier de reformuler `Δ` en « la fraction des lois qui répliquent ».

### 7.4 Ce que `Δ` permet de conclure — et ce qu'elle ne permettra jamais

**Autorisé, au maximum :**

> Dans le cadre déclaré — lattices carrées périodiques de `{16, 24, 32}`, échelles
> `dt = m_max = n_max = 1`, lois uniformes sur `A = Boîte ∩ (B1) ∩ (B2)` avec `ε̂_b ≤ 1`,
> conditions initiales i.i.d. `U[0,1]` avec `b ≡ 0`, horizon 1024, cadence 16 — la
> conjonction *persistance ∧ remplacement matériel vérifié* est instanciée dans une
> proportion `Δ(f)` des **tirages**, avec l'intervalle exact indiqué.

**Interdit, et refusé mécaniquement** par `check_claim_within_ceiling` :
ownership, ownership local, autonomie, individualité, reconstruction, auto-réparation,
reproduction, division, hérédité, agentivité, but — ainsi que les formulations vagues du type
« effet robuste » sans estimand ni domaine. Six phrases de test, toutes refusées ; la phrase
autorisée ci-dessus passe.

**Position sur l'échelle** : **en deçà du barreau 3**. Route E ne mesure aucune variable
d'état et n'inspecte rien d'interne à un composant. **Une fréquence n'est pas un mécanisme.**
Le premier article a déjà établi la persistance causale à travers le renouvellement matériel
sans preuve d'ownership local ; Route E mesure à quelle **fréquence** cette conjonction
survient sur une distribution de lois déclarée. Elle ne dit rien de plus.

---

## 8. PRB-F — refus par l'entrée publique réelle

### 8.1 Le fait qu'il faut regarder en face

`run_owned_future_pipeline` **n'a aucun paramètre d'autorisation** et ne peut pas en recevoir
un sans **modifier une source acceptée**, ce que l'allowlist gelée interdit. Il est donc
**déclaré hors protocole** comme entrée scientifique directe de Route E — c'est
explicitement l'alternative que le texte gelé de PRB-5 autorise (« fermer **ou déclarer hors
protocole**, avec un test épinglant le refus »). C'est enregistré comme limitation **RE-L2**.
Les cinq points d'entrée nommés par PRB-5 sont tous déclarés hors protocole dans le module.

### 8.2 Le refus, exercé sur la fonction publique réelle

`test_prb_f_05` appelle **exactement `run_owned_future_pipeline`** — pas un helper interne —
avec un répertoire de namespace Route E **non autorisé, donc inexistant**, une source
d'acquisition **espionne** qui lève si elle est appelée, et un `tmp_path` dont l'arbre est
digéré avant et après.

| Assertion | Résultat |
|---|---|
| exception | `OwnedPublicationError` : *« run_directory must already exist »* |
| **création de famille** | aucune |
| **création de seed ou de namespace** | aucune — le répertoire n'existe toujours pas |
| **construction d'une loi ou d'une CI concrète** | aucune |
| **appel moteur** | **0** — `LatticeBondEngine.step` remplacé par une fonction qui lève (`test_prb_f_06`) |
| **écriture de monde** | aucune — `tmp_path` est **vide** après le refus |
| **accès aux résultats** | aucun |
| **persistance d'un artefact scientifique** | aucune — digest d'arbre **identique** avant et après |
| invocations de la source d'acquisition | **0** |

Le refus intervient donc bien **avant les sept effets énumérés**, sur la vraie fonction
publique, et **sans effet de bord après refus**.

### 8.3 L'entrée scientifique in-protocol, fail-closed

`open_route_e_scientific_run` est l'unique entrée scientifique Route E in-protocol de ce
module. Elle **refuse toujours**, à trois niveaux successifs et dans cet ordre :

1. **aucune autorisation présentée** → refus ;
2. **autorisation mal formée** (`is_valid()` faux) → refus ;
3. **autorisation bien formée et accordée** → refus quand même, parce que
   `SCIENTIFIC_RUN_AUTHORIZED` est `False`, que les six `PRE_RUN_BLOCKER` gelés ne sont pas
   fermés, qu'aucune prérégistration n'existe et qu'aucune revue humaine n'a autorisé
   l'exécution.

Les trois refus sont pinnés, et chacun vérifie que l'arbre du système de fichiers est
**inchangé**. **Il n'existe aucune branche de ce module qui atteigne un chemin d'exécution.**

### 8.4 Portée exacte de ce qui est prouvé — et de ce qui ne l'est pas

**Prouvé** : `run_owned_future_pipeline` ne peut produire aucun artefact Route E sans un
répertoire autorisé préexistant, et refuse avant tout effet observable.

**Non prouvé, et il faut le dire** : que la fonction *inspecte un jeton d'autorisation*. Elle
n'en a pas. Le prédicat de refus effectif est *l'inexistence du répertoire autorisé*, plus la
barrière in-protocol en amont. Rendre le refus dépendant d'un jeton exigerait de modifier une
source acceptée. **RE-L2.**

---

## 9. Contrôle transversal de la seconde CI

| Question | Réponse, entièrement spécifiable à la prérégistration |
|---|---|
| Sortie du discriminateur | `ψ̂ = d/67`, avec `d` le compte de paires de lois discordantes |
| États possibles | `IC_DEPENDENCE_MATERIAL` · `IC_DEPENDENCE_NEGLIGIBLE` · `IC_DEPENDENCE_INDETERMINATE` — exhaustifs et mutuellement exclusifs |
| Conséquence d'une discordance `X_i1` / `X_i2` | c'est une **évidence sur `ψ` et rien d'autre**. Ne change pas `Y_i`, ni `k`, ni `Δ`, ni la décision ternaire |
| Effet sur le plafond d'interprétation | `IC_DEPENDENCE_MATERIAL` **plafonne** la lecture de `Δ` : interdit de la reformuler en énoncé sur les lois, la confine à la marginale sur les CI. **N'invalide jamais** le primaire |
| Exclusion d'une loi du dénominateur à cause de `X_i2` | **absolument interdite**. L'enrôlement est fixé par `X_i1` au tirage, et la règle gelée est : aucun remplacement, aucun retirage, aucun complément |

**Aucune ambiguïté ne reste ouverte sur ces cinq points**, donc aucun blocker n'est signalé
de ce chef. Aucune statistique principale nouvelle n'a été improvisée.

---

## 10. Matrice des six blockers

| Blocker | Formulation d'origine (record accepté §8) | Fermeture proposée | Preuve mécanique | Test frontière | Limitation | Statut |
|---|---|---|---|---|---|---|
| **PRB-A** | chiffrer la fraction de censure et la concordance inter-CI, repère non biaisé au sens de Jensen | `25/67` strict pour la censure, dérivé de `k ≥ 42` sur `n = 67` ; `ψ = P(Y_i1 ≠ Y_i2)` estimée sans biais par `d/67`, frontières `1/4` et `1/8` par la convention gelée du point milieu | CP reproduits à `1e-12` sur les quatre valeurs gelées ; régions `d ≥ 25` / `d ≤ 2` / `3..24` | 24 / **25** / 26 pour la censure ; `d = 2,3,24,25` et les bornes CP exactes | **RE-L1** : discriminateur sous-dimensionné à `n = 67` (demi-largeur 0,124721 > 0,0625) | **PASS** |
| **PRB-B** | générateur externe, ordre des tirages, stratégie de seed, sans créer de seed | SHA-256 compteur FIPS 180-4 ; beacon drand quicknet, round = premier round ≥ (commit + 24 h) ; ordre lois → tailles → CI → mondes ; rejet consommé ; anti-reroll par liaison commit + round futur | plan déterministe et seed-sensible ; indices acceptés strictement croissants ; **0 appel moteur** ; **0 ouverture de fichier** | round exact `t(r) ≥ T > t(r−1)` ; longueurs de seed 31/32, 19/20, round 0 | **RE-L6** : aucun accès réseau ; les octets du beacon sont un argument | **PASS** |
| **PRB-C** | l'acceptation passe par la construction fail-closed du véritable objet moteur | `in_proposal_box ∧ engine_accepts`, le second **étant** `LatticeBondSpec(**fields)` ; aucun second moteur | **400** et **40 000** propositions, **0 divergence** accept ↔ moteur ; **48** points `nextafter`, **0** divergence ; accord algébrique **40 000/40 000** | NaN/±∞ × 5 champs ; champ inconnu ; overflow ; `nextafter` des deux coupures | **RE-L3** : le prédicat algébrique est un témoin rapporté, jamais un gate | **PASS** |
| **PRB-D** | préenregistrer la rupture de track par la porte d'association comme cause d'un nul | cause `ASSOCIATION_GATE_TRACK_BREAK`, définie par arête refusée `REJECT_CENTROID_DISTANCE` / `REJECT_AREA_RATIO` + `APPEARANCE` au même frame | fixture 16×16, distance périodique 8 > 3,0 → cause émise ; disparition réelle → non étiquetée ; idempotence | continuation (1 cellule) / rupture de porte (8 cellules) / disparition totale | **RE-L4** : étiquette de cause, pas un sixième état terminal | **PASS** |
| **PRB-E** | dire de quel `Δ` parle le plafond sous la règle d'invariance de `cohort_residual_fraction` | `Δ(f)` définie sur les onze axes exigés ; POSITIF lié par `Δ(0,01)`, NÉGATIF par `Δ(0,20)` ; plafond machine-vérifiable | 6 phrases interdites refusées, phrase autorisée acceptée ; les onze clés présentes et non vides | `f ∈ {0,01 ; 0,05 ; 0,20}` et le binding monotone | — | **PASS** |
| **PRB-F** | nommer `run_owned_future_pipeline` dans le test de refus | déclaration hors protocole des cinq entrées + refus de la **vraie** fonction avant les sept effets ; entrée in-protocol fail-closed à trois niveaux | `OwnedPublicationError` avant tout effet ; **0** invocation de source, **0** appel moteur, **0** octet écrit, digest d'arbre inchangé | sans autorisation / autorisation invalide / autorisation bien formée | **RE-L2** : le refus n'est pas un contrôle de jeton en fonction ; la source acceptée est immuable | **PASS** |

**Six PASS, zéro FAIL.** La disposition de fermeture des obligations portées est donc
prononcée. Elle ne s'étend à rien d'autre.

---

## 11. Tests

| Catégorie | Compte | Détail |
|---|---|---|
| **Tests propres aux blockers** | **104** | `tests/test_future_route_e_pre_run_blocker_closure_00.py` — PRB-A 13, PRB-B 13, PRB-C 18, PRB-D 7, PRB-E 6, transversal 3, PRB-F 8, et les paramétrisations |
| **Tests de non-régression** | **673** | la suite 01S gelée, inchangée |
| **Total exécuté** | **777** | |
| **Échecs** | **0** | |
| **Skips** | **0** | |
| **Tests non exécutés** | **0** | aucun test du dépôt n'a été exclu, désélectionné ou marqué |

Environnement : Python 3.11.15, pytest 8.4.2, numpy 2.4.4. Aucun test n'ouvre un shard
Stage B, une archive `M_MINUS`, une trajectoire scientifique, une ancienne famille, un
candidat, un champion ou un résultat fermé. Aucun ne crée de seed, de namespace, de famille,
de loi, de CI ou de monde scientifique.

**Mesures hors suite** (racine synthétique, jetées, non committées) : 40 000 propositions →
appartenance boîte 0,5016, efficacité globale 0,1007, accord moteur/algébrique 40 000/40 000 ;
plan à 67 lois → 735 propositions consommées, 19 ms, réalisation de tailles 23/22/22. **Cette
réalisation de tailles n'est pas une allocation** : c'est un tirage i.i.d. uniforme sur une
racine synthétique, et le plan réel sera différent.

---

## 12. Limitations déclarées

| ID | Limitation |
|---|---|
| **RE-L1** | Le discriminateur inter-CI ne satisfait pas le principe de précision du paquet à `n = 67` : largeur d'indifférence 0,125, demi-largeur pire-cas 0,124721 contre 0,0625 exigés. `n` est gelé. Le discriminateur est secondaire et ne gouverne jamais la décision ternaire. Un `INDETERMINATE` ne doit pas être lu comme « pas de dépendance aux CI ». |
| **RE-L2** | `run_owned_future_pipeline` n'a pas de paramètre d'autorisation et ne peut pas en recevoir sans modifier une source acceptée. Déclaré hors protocole ; le refus pinné est un refus de la vraie fonction avant tout effet, pas un contrôle de jeton en fonction. |
| **RE-L3** | L'équivalence admissibilité ↔ (B1)∧(B2) est exacte en arithmétique réelle ; en IEEE-754 un écart d'un ulp reste concevable. Ce module ne gate jamais sur le prédicat algébrique : le gate est le moteur. L'accord mesuré est de 40 000/40 000 et de 48/48 aux frontières `nextafter`. |
| **RE-L4** | `ASSOCIATION_GATE_TRACK_BREAK` est une étiquette de cause, pas un sixième état terminal ; ne change aucun outcome, ne retire jamais un tirage du dénominateur. |
| **RE-L5** | Le seuil de censure est une règle d'attribution pour un nul. Il ne change pas la décision ternaire, dont les coupures restent gelées. |
| **RE-L6** | Le round de beacon est spécifié comme une règle sur un instant futur. Le module n'effectue aucun accès réseau ; les octets du beacon sont un argument. La disponibilité de drand au moment de la prérégistration devra être re-vérifiée alors. |
| **RE-L7** | Fermer les six obligations de cette mission **ne ferme pas** les six `PRE_RUN_BLOCKER` gelés `PRB-1 … PRB-6`. |
| **RE-L8** | `PRB-5` reste ouvert : le module déclare hors protocole les cinq points d'entrée nommés, mais seul `run_owned_future_pipeline` a un test de refus. Les quatre autres — `open_owned_analysis_access`, `future_lifecycle_runner.open_analysis_access`, `publish_future_family_completion`, `qualify_and_write_lifecycle_contract` — n'en ont pas dans cette mission, qui n'était mandatée que pour le premier. |

---

## 13. Ce qui reste non prouvé scientifiquement

**Tout.** Aucune famille n'a été exécutée. Il n'existe :

- aucune valeur de `Δ`, ni bornée ni ponctuelle ;
- aucune valeur de `ψ` ;
- aucune fraction de censure observée ;
- aucune fraction d'inéligibilité mécanique observée ;
- aucune distribution observée sur les cinq états terminaux ;
- aucun monde Route E, aucune loi tirée, aucune CI tirée, aucun seed scientifique.

Route E reste **un protocole sélectionné, non confirmé**. Le premier article
(https://doi.org/10.5281/zenodo.21403458) reste la seule source de résultat publié du
programme, et il n'établit **ni ownership local, ni autonomie, ni individualité complète, ni
reconstruction, ni reproduction, ni hérédité**.

Aucune donnée Stage B et aucun résultat `M_MINUS` n'a servi à calibrer ou à confirmer quoi
que ce soit ici. Route G reste fermée pour ce programme et n'a été rouverte sous aucun nom.
Route F n'est pas un backup automatique et n'a pas été invoquée.

---

## 14. Arrêt et prochaine mission

> ### `scientific_run_authorized = false`

`ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00` **n'est pas démarrée** et n'est pas
autorisée ici.

**Prochaine étape obligatoire, et seule autorisée :**

> **HUMAN REVIEW — `FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00`**

une revue humaine indépendante de la fermeture des obligations portées, qui devra au minimum
statuer sur : la dérivation des deux seuils et leurs digests ; l'acceptabilité de RE-L1 ; la
suffisance du refus PRB-F au regard de RE-L2 ; et le fait que `PRB-1 … PRB-6` restent ouverts.

Ce n'est qu'après cette revue **et** la fermeture des six `PRE_RUN_BLOCKER` gelés que
`ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00` pourra être envisagée, puis, seulement après
une seconde revue humaine, une exécution.

---

## 15. Firewall et remote

**Firewall tenu.** Chemins Git exacts uniquement pour toute lecture d'objet. Aucun parcours
de `results/`, aucun shard Stage B, aucune archive `M_MINUS`, aucune trajectoire scientifique,
aucune ancienne famille, aucun candidat, aucun champion, aucun résultat fermé. Aucun calage de
seuil sur une sortie mécanique ou historique : les deux seuils sont dérivés d'arithmétique
gelée et d'une convention déjà déclarée. `git status` a été utilisé une seule fois, en compte
seulement, ce que le mandat de cette mission autorise explicitement, et sans révéler aucun
chemin.

`main` est resté à `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77` avant et après. **Le working
tree sale de `main` a été intégralement préservé** : aucun `git add`, aucun `git add -A`,
aucun checkout, aucun stash. Le commit a été construit par plomberie sur un index temporaire
sous `/tmp`, sans jamais toucher l'index du dépôt.

**Résidu non supprimable, redivulgué.** Le montage de travail est en création seule (`rm`
renvoie `EPERM`) : subsistent, sans effet sur l'arbre committé ni sur aucun objet référencé,
un fichier sonde `.opr00_probe_delete_me` (6 octets) et des fichiers temporaires
`.git/objects/*/tmp_obj_*`.

**Remote.** Une tentative de push **normale**, unique. Aucun `--force`, aucun changement de
credentials, aucun retry en boucle. En cas d'échec, la branche locale est préservée intacte
et la commande exacte est rapportée.
