# HUMAN REVIEW — FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00

> ## Disposition : `HUMAN_REVIEW_REVISE`
>
> **Candidat audité :** `c6d4acf037d4e51d59e5b75dc91b977b9eb83dbd`
> **Disposition candidate refusée en l'état :** `ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_CARRIED_OBLIGATIONS_CLOSED`
>
> Les vérifications Git, l'arithmétique, le prédicat moteur et les tests **passent et sont
> reproduits**. La revue est bloquée sur une **question de mandat** : les textes gelés attribuent à
> cette mission les `PRE_RUN_BLOCKER` **PRB-1 … PRB-6**, et attribuent les six obligations
> **A – F à la prérégistration**. Le candidat a fermé la seconde couche et n'a pas touché la
> première.
>
> **`scientific_run_authorized = false`**

---

## 0. Les quatre catégories, tenues séparées

1. **Preuves mécaniques** — reproduites indépendamment ci-dessous, sur une racine synthétique
   *différente* de celle du candidat.
2. **Décisions de gouvernance** — auditées, dont trois refusées.
3. **Limitations** — celles déclarées par le candidat, plus celles qu'il n'a pas déclarées.
4. **Résultats scientifiques** — **catégorie vide. Aucun n'existe, aucun n'a été produit, aucun n'a
   été utilisé.**

---

## 1. Git et change set — **PASS**

`GIT_INDEX_FILE` explicitement neutralisé (`GIT_INDEX_FILE=[]`) avant chaque vérification ; le seul
index temporaire employé l'a été sous `/tmp` pour la preuve inverse, puis désactivé.

| Vérification | Résultat |
|---|---|
| `refs/heads/codex/future-route-e-pre-run-blocker-closure-00` | `c6d4acf037d4e51d59e5b75dc91b977b9eb83dbd` |
| `rev-list --parents -n1` | `c6d4acf0… 00afcdd1aacbdf32bb030d85ced735a2920421f6` |
| Lignes `^parent ` dans l'objet commit | **1** — aucun merge |
| `00afcdd1…` / `63c371d5…` | 1 parent chacun — chaîne linéaire |
| Arbre du candidat | `62202e61f6376f3df5290a9a2ef9cc9922f66b22` |
| Message | `docs: close route e carried pre-run obligations` |
| `refs/heads/main` | `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77` — **inchangée** |
| `.git/HEAD` | `ref: refs/heads/main` |
| **Véritable `.git/index`** | 135 281 octets, mtime `2026-08-03 23:45:06` — **antérieur à la mission, inchangé** |
| Checkout sale | **23 entrées, préservé** |

### 1.1 Change set complet, découvert et non présumé

`git diff-tree -r --name-status --no-renames 00afcdd1… c6d4acf0…` donne **quatre lignes, toutes
`A`**, et rien d'autre. Décompte par statut : `4 A`. **Aucun cinquième changement, zéro
modification, zéro suppression.**

Les deux noms de `docs/individuation/` ont été **découverts** par ce diff, pas présumés, et sont
écrits ici en toutes lettres, sans abréviation :

| Chemin exact (complet) | Mode | Octets | sha256 du contenu | Chez le parent |
|---|---|---|---|---|
| `docs/individuation/FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_DECISION.json` | `100644` | 18 955 | `5ceaeb89f3b52c19c0d0a5bd11a211ed5d9321116c9d2d9137191344ab6dbd4f` | **ABSENT** |
| `docs/individuation/FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00_REPORT.md` | `100644` | 43 875 | `77e1f4dba5f0bd4dde6ff9d55397ee99ce4e3b0cc6a602373b766fbc6bf90da7` | **ABSENT** |
| `edlab/substrates/lattice_bond/future_route_e_pre_run_frame.py` | `100644` | 48 289 | `0364185144452f598740cf3db46721aa42ff9368792b4e1b81e8cd0bec921232` | **ABSENT** |
| `tests/test_future_route_e_pre_run_blocker_closure_00.py` | `100644` | 34 823 | `47ac5ea8c7c3dc640a3e6f71c4cf8ffeb5ffc536f4d3dc9e59f7a5f3055786bc` | **ABSENT** |

Blobs : `b10bf580a7d574c86ae96dbdae46ce8d5b1f2fc3`, `faf9419b1cdc441f06f7b846f9889ff2ba544d07`,
`12a19658de1cbcf9567754ee708b40cc81c02294`, `9b9560b98f6738984aa49340d51b18686ba8335e`.

**Preuve inverse.** Index temporaire initialisé sur l'arbre du candidat, les quatre chemins retirés
par `--force-remove` : `write-tree` produit `d9163d22001a79d7be4f6a61c16f00a983f5dd76`, qui **est**
`00afcdd1…^{tree}`. Le change set est donc exactement ces quatre ajouts.

### 1.2 Résidus

`.opr00_probe_delete_me` : **absent des arbres** de `c6d4acf0`, `00afcdd1` et `f3921a4d`
(`cat-file -e` échoue sur les trois). Les `tmp_obj_*` vivent sous `.git/objects/` ; `.git` n'est pas
une entrée d'arbre du candidat (vérifié), donc aucun `tmp_obj_*` ne peut être référencé par un tree.
**Rien n'a été supprimé, aucun `git gc` n'a été lancé, et aucun de ces artefacts n'est utilisé comme
preuve.** L'affichage antérieur de « 1011 entrées » n'est pas repris : il provenait d'un
`GIT_INDEX_FILE` temporaire encore exporté, et le compte réel reproduit ici est **23**.

---

## 2. Question centrale — matrice A–F ↔ PRB-1…6 — **ÉCHEC DE MANDAT**

### 2.1 Les deux textes gelés, cités littéralement

**a) `…_01S_DECISION.json` → `pre_run_blockers`** (lu depuis l'objet Git de `00afcdd1`) :

| ID | `obligation` | `closure` |
|---|---|---|
| PRB-1 | persist the track-component join | write (frame, canonical cell-set digest, track_id) into root-bound evidence |
| PRB-2 | mandatory receipt | the supported scientific entry point refuses without a verified receipt |
| PRB-3 | frozen check order | pin by test: local evidence -> root digest -> verifier |
| PRB-4 | replay binding | bind run identity and family enrolment into the root |
| PRB-5 | single supported entry point | close or declare out of protocol, with a refusal test: `open_owned_analysis_access`, `future_lifecycle_runner.open_analysis_access`, `publish_future_family_completion`, `qualify_and_write_lifecycle_contract` (and, per B15, `run_owned_future_pipeline`) |
| PRB-6 | external anchoring of the final root | public immutable or append-only commitment, verifiable without a secret |

**b) `…_01S_HUMAN_REVIEW.md` §8**, le record accepté qui autorise cette mission, **mot pour mot** :

> `FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00` **pourra** fermer les six `PRE_RUN_BLOCKER`.

et, plus bas, en titre du bloc dont le candidat tire ses six obligations :

> **Obligations portées à la prérégistration** (`ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00`), à
> n'exécuter qu'après fermeture **et** revue humaine des blockers : 1. … 6. …

### 2.2 La matrice exigée

| Obligation 01S littérale | A–F correspondant | PRB-1…6 correspondant | Relation exacte | Fermé maintenant ? | Étape future |
|---|---|---|---|---|---|
| « Chiffrer les deux seuils non chiffrés (A16/B16) » | **A** | *aucun* | obligation de **prérégistration**, sans contrepartie dans PRB-1…6 | traitée, mais **avec défauts** (§3) | prérégistration |
| « Nommer le générateur externe, l'ordre des tirages et la stratégie de seed (L-HR2) » | **B** | *aucun* ; **dépend** de PRB-6 pour l'anti-reroll | obligation de prérégistration, **conditionnée** par PRB-6 | traitée, **anti-reroll non établi** (§4) | prérégistration, après PRB-6 |
| « Faire du prédicat d'acceptation le `LatticeBondSpec` du moteur (L-HR1) » | **C** | *aucun* | obligation de prérégistration | **traitée et reproduite** (§5) | prérégistration |
| « Préenregistrer la rupture par la porte d'association (B17) » | **D** | *aucun* ; touche l'instrumentation gelée | obligation de prérégistration | **convention seulement**, non intégrée (§6) | prérégistration |
| « Dire de quel `Δ` parle le plafond (A18) » | **E** | *aucun* | obligation de prérégistration | traitée, **incomplète** (§7) | prérégistration |
| « Nommer `run_owned_future_pipeline` dans le test de refus (B15) » | **F** | **PRB-5**, partiellement | **sous-obligation** de PRB-5 : une entrée sur cinq | **la sous-partie seulement** (§8) | PRB-5 reste ouvert |
| persist the track-component join | — | **PRB-1** | mandat propre de la mission 00 | **NON** | mission 00 |
| mandatory receipt | — | **PRB-2** | mandat propre de la mission 00 | **NON** | mission 00 |
| frozen check order | — | **PRB-3** | mandat propre de la mission 00 | **NON** | mission 00 |
| replay binding | — | **PRB-4** | mandat propre de la mission 00 | **NON** | mission 00 |
| single supported entry point | **F** (1/5) | **PRB-5** | recouvrement partiel | **NON** | mission 00 |
| external anchoring of the final root | — | **PRB-6** | mandat propre ; **prérequis de B** | **NON** | mission 00 |

### 2.3 Quelle des quatre relations tient

- **Ce ne sont pas les mêmes obligations** (cas 1 exclu) : les deux listes sont textuellement et
  matériellement disjointes, à la seule exception de `F ⊂ PRB-5`. Il n'y a donc **pas** deux statuts
  incompatibles sur une même obligation, et **pas** de motif `STOP` de ce chef.
- **Ce ne sont pas globalement des sous-obligations** (cas 2 exclu) : seul `F` est une
  sous-obligation, et de `PRB-5` uniquement.
- **Ce sont deux couches distinctes** (cas 3) — mais avec une **inversion d'attribution** que les
  sources tranchent sans ambiguïté : le record accepté assigne **A–F à la prérégistration** et
  **PRB-1…6 à la mission 00**. Le candidat a fait l'inverse.

### 2.4 Conséquence sur la décision

La règle d'acceptation de cette revue est explicite : *« ACCEPT n'est possible que si les textes
gelés prouvent que la mission 00 portait seulement sur les obligations transportées A–F et que
PRB-1…6 devaient volontairement rester ouverts jusqu'à la prérégistration. »*

Les textes gelés prouvent **le contraire sur les deux points** :

1. la mission 00 **pouvait fermer les six `PRE_RUN_BLOCKER`** — c'est son mandat nommé ;
2. A–F devaient être exécutées **après** fermeture et revue humaine des blockers, donc PRB-1…6
   devaient être fermés **d'abord**, non laissés ouverts.

**ACCEPT est donc interdit.** Aucun déclencheur `STOP` ne s'applique (lignée saine, allowlist propre,
loi gelée intacte, aucun beacon révélé, aucune donnée historique, aucune entité scientifique, aucune
correction n'exige de rouvrir 01S). La disposition est **`REVISE`**.

### 2.5 Aggravant : citation tronquée

Le rapport candidat §1 introduit A–F par : *« Les six obligations, telles que le record accepté les
nomme (§8, littéral) »*, puis les recopie fidèlement — **en omettant le titre du bloc**, qui est
« Obligations portées **à la prérégistration** ». Le contenu est cité exactement ; **la portée ne
l'est pas**. C'est le point unique qui, corrigé, change la nature du package : il ne s'agit pas d'une
erreur de calcul mais d'une erreur d'assignation.

À la décharge du candidat : il **ne prétend nulle part** avoir fermé PRB-1…6. Son §1 les énumère
comme ouverts, RE-L7 et RE-L8 les déclarent ouverts, et le JSON porte
`frozen_pre_run_blockers_closed = "0/6"`. La transparence est réelle ; c'est le **mandat** qui est
manqué, pas la véracité.

### 2.6 Formulation qui fait foi

```
Les obligations transportées PRB-A…PRB-F ne sont PAS acceptées comme fermées.
Les PRE_RUN_BLOCKER PRB-1…PRB-6 ne sont pas déclarés fermés.
Aucun run n'est autorisé.
```

Il est **interdit** de résumer ce package par « tous les pre-run blockers sont fermés ».

---

## 3. PRB-A — censure et seconde CI — **REVISE**

### 3.1 Frontières de censure — arithmétique **correcte**, reproduite

| `C` | `67 − C` = max de `k` atteignable | POSITIF (`k ≥ 42`) atteignable | Verdict du candidat |
|---|---|---|---|
| 24 | 43 | oui | `HORIZON_CENSORING_NOT_SUFFICIENT` |
| **25** | **42** | **oui, à la limite** | `HORIZON_CENSORING_NOT_SUFFICIENT` |
| 26 | 41 | **non** | `HORIZON_CENSORING_SUFFICIENT` |

La frontière est **strictement supérieure** et tombe exactement là où le bras POSITIF cesse d'être
atteignable. Fail-closed vérifié sur `-1`, `68`, `True`, `25.0`, `"25"`, `None` : tous lèvent.
`NaN`/`±inf` ne peuvent pas atteindre le calcul, l'entrée étant un `int` strict — **fail-closed par
typage**, ce qui est plus fort qu'un contrôle a posteriori. **Cette partie passe.**

### 3.2 Défaut décisif — la quantité mesurée ne discrimine rien

Le `quantity` scellé est, mot pour mot :

> *fraction of the 67 primary draws whose eligible component **never reaches verified material
> replacement** before step 1024 (right-censored on turnover)*

Or, sous le mapping gelé des états terminaux, **quatre** états valent 0 (`DISSOLVED_DETECTED_TRACK`,
`SPLIT_INTO_TRACKS`, `MERGED_INTO_TRACK`, `UNRESOLVED_HANDOFF`) et le cinquième
(`RIGHT_CENSORED_AT_HORIZON`) ne vaut 1 qu'avec remplacement vérifié. Un composant dissous au pas 40
**n'atteint jamais** le remplacement vérifié : il tombe donc dans la quantité telle qu'écrite. Idem
pour un split, un merge, un handoff non résolu, et pour un monde sans composant éligible.

Conséquence : `C` ≈ tous les tirages non-succès, donc `C/67 ≈ 1 − Δ̂`, et
« `C/67 > 25/67` » devient **quasi équivalent à « `k ≤ 41` »**. Le seuil se déclenche alors sur
**presque tout nul, quelle qu'en soit la cause** — c'est-à-dire qu'il **n'attribue rien**. C'est
exactement l'inverse du rôle que A16 lui assigne (« l'attribution de cause d'un nul »).

Le bloc de seuil ne nomme **aucun** des cinq états terminaux gelés (vérifié : zéro occurrence de
`DISSOLVED`, `SPLIT_INTO`, `MERGED_INTO`, `UNRESOLVED_HANDOFF`, `RIGHT_CENSORED`).

**À corriger :** définir la censure comme un événement **disjoint**, en termes des états gelés — par
exemple *« état terminal `RIGHT_CENSORED_AT_HORIZON` et `cohort_residual > f` à toute frame
échantillonnée »* — distinct de la dissolution, du split, du merge, du handoff et de
l'inéligibilité mécanique, chacun gardant sa propre fraction co-primaire.

### 3.3 Deuxième défaut — observé ou inconnu, jamais dit

Le package ne dit **nulle part** si un tirage censuré est :

- un **échec observé** de la conjonction *à l'intérieur de l'horizon déclaré* — auquel cas `Y = 0`
  est une observation légitime et l'estimand est explicitement relatif à `H = 1024` ; ou
- une **valeur inconnue** — auquel cas coder implicitement `Y = 0` est un biais.

La lecture correcte est la première : l'estimand gelé est inconditionnel et le critère de `Δ` est
explicitement borné à `H = 1024`. Mais **cela doit être écrit**, et la règle robuste doit être
écrite avec, pour tout ce qui resterait réellement inconnu (erreur technique, famille échouée) :

```
POSITIF robuste  si S ≥ 42
NÉGATIF robuste  si S + C ≤ 9
sinon             INDÉTERMINÉ ou TECHNICAL_FAIL
```

`ASSOCIATION_GATE_TRACK_BREAK` est bien de l'autre nature : c'est un **échec observé** contractuel,
il vaut zéro et reste au dénominateur — le candidat le pose correctement (§6).

### 3.4 Discriminateur inter-CI — **structure correcte**, borne d'interprétation à durcir

Bornes Clopper–Pearson recalculées **indépendamment** (`scipy.stats.beta.ppf`, implémentation
étrangère à la bissection du candidat) :

| `d` | borne | recalcul indépendant | candidat | attendu par le mandat | écart |
|---|---|---|---|---|---|
| 2 | haute | `0.103707507648` | `0.103707507648` | ≈ 0,103707508 | `1.4e-17` |
| 3 | haute | `0.125327035994` | `0.125327035994` | ≈ 0,125327036 | `0` |
| 24 | basse | `0.244694901810` | `0.244694901810` | ≈ 0,244694902 | `5.6e-17` |
| 25 | basse | `0.257974162704` | `0.257974162704` | ≈ 0,257974163 | `5.6e-17` |

et, en contrôle, `CP inf(42,67) = 0.500104744020`, `CP sup(9,67) = 0.239741752063`. **Les quatre
frontières exigées sont confirmées** : `d ≤ 2` ⇒ NÉGLIGEABLE, `d ≥ 25` ⇒ MATÉRIEL, `3 ≤ d ≤ 24` ⇒
INDÉTERMINÉ.

**Appariement vérifié dans le code** : `build_draw_plan` produit **une** loi et **une** taille par
indice `i`, les deux indices de CI sont `2i` et `2i+1`, et l'ordre des mondes est
`(0,0),(0,1),(1,0),(1,1),…`. `H` et `Δf` sont des constantes globales. Le moteur est **déterministe
et sans RNG**. Donc les deux mondes d'une paire partagent **exactement** loi, taille, horizon et
cadence, et **seule la CI varie**. `ψ` mesure bien la sensibilité aux CI et rien d'autre. **PASS.**

**`d` ne peut pas toucher `k`** — vérifié structurellement : `classify_ic_dependence` ne prend qu'un
compte de discordances, ne retourne que trois étiquettes, ne référence ni `Δ` ni `134`, et aucun
chemin du module ne réécrit `k`, n'exclut une loi, ne substitue `X_i2` à `X_i1`, ni ne sélectionne le
meilleur des deux mondes. **PASS.**

**Borne d'interprétation.** Une faible discordance **ne prouve pas** l'indépendance aux CI : sous
`q_L = P(Y = 1 \mid L)`, `ψ` mesure essentiellement `E[2 q_L (1 − q_L)]`, qui est petit dès que `q_L`
est proche de 0 ou de 1 pour presque toute loi. RE-L1 est déclarée et doit **rester** explicite ; le
candidat la déclare correctement, mais elle doit être répétée dans le libellé du discriminateur
lui-même, pas seulement au registre.

**Hypothèse binomiale.** Les tailles sont tirées **i.i.d. uniformes** par loi (domaine `SIZE`, indice
`i`), non allouées de façon déterministe ni stratifiée. Les 67 unités sont donc i.i.d. sous le
mélange gelé et l'usage de Clopper–Pearson est licite. **PASS.**

---

## 4. PRB-B — drand et distribution — **REVISE**

### 4.1 Ce qui est correct

Chain hash `52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971` complet ; schéma
`bls-unchained-g1-rfc9380` ; période 3 s ; genesis 1692803367 ; clé publique épinglée en entier.
Formule du round vérifiée : `t(r) = genesis + (r−1)·période`, premier `r` tel que `t(r) ≥ T` est
`1 + ceil((T − genesis)/période)`, et le test épingle `t(r) ≥ T > t(r−1)`. Séparation de domaines
(`LAW`, `SIZE`, `IC`) présente ; compteur SHA-256 conforme à sa définition écrite ; big-endian
partout ; octets bruts, aucun JSON ni formatage flottant ; propositions rejetées **consommées**,
indices acceptés strictement croissants et sans doublon ; aucun accès réseau dans le module.

**Le commit d'ancrage est le futur commit de prérégistration**, pas `c6d4acf…` — c'est le cas
explicitement qualifié d'acceptable, et il écarte le risque d'adaptation. **Ce point passe.**

### 4.2 Défaut 1 — l'anti-reroll n'est pas établi

`ANTI_REROLL` affirme : *« Any reroll changes either the commit or the round, **both of which are
public** »*. Or **rien** dans le package n'exige que le commit de prérégistration soit
**publiquement horodaté avant** `T`. Un hash local n'est pas un horodatage public. La stratégie
suivante reste ouverte :

> préparer un commit A à `t₀` → attendre `t₀ + 24 h` → lire le beacon → calculer le plan → s'il
> déplaît, **jeter A**, préparer un commit B à `t₁` → recommencer.

À chaque itération, le round reste futur **au moment du commit courant**, donc la propriété « le
beacon n'existe pas quand le commit est écrit » est vraie à chaque fois et n'empêche rien. Ce qui
l'empêcherait est un **engagement public immuable antérieur à la révélation** — c'est-à-dire
**PRB-6**, qui est ouvert.

**À corriger :** écrire la précondition explicitement — *le commit de prérégistration doit être
ancré publiquement (PRB-6) avant `T`, faute de quoi le seed dérivé est nul et non avenu* — et
retirer l'affirmation « both of which are public ».

### 4.3 Défaut 2 — la signature du beacon n'est vérifiée nulle part

`derive_seed_root` prend `beacon_randomness: bytes` (32 octets) et **rien d'autre** : aucun
paramètre de signature, aucun contrôle. Le module contient **zéro** occurrence de `verify`. Une
simple réponse HTTP satisferait la fonction. `public_verifiability` **décrit** la vérifiabilité BLS
sans **exiger** la vérification.

**À corriger :** exiger, comme condition d'emploi, la vérification cryptographique de la signature du
round contre la chaîne et la clé publique épinglées, et faire de `randomness = sha256(signature)` un
contrôle, pas une note.

### 4.4 Défaut 3 — aucun comportement en cas d'indisponibilité

Zéro occurrence de `unavailab`, `WAIT`, `STOP`, `next round`, `fallback`, `endpoint`. Rien n'interdit
donc de prendre le round suivant, un autre endpoint ou une autre source — ce qui rouvrirait
entièrement le choix opportuniste.

**À corriger :** round indisponible ⇒ **WAIT**, puis **STOP**. Jamais de round suivant, jamais
d'endpoint alternatif, jamais de nouvelle source.

### 4.5 Uniformité — construction **correcte**, revendication **trop forte**

La construction est la bonne, et la correction du défaut antérieur est réelle : les neuf coordonnées
sont tirées **indépendamment et uniformément sur la boîte produit** (`base = index·9`, neuf uniformes
du même domaine), le plafond triangulaire est imposé **par rejet** dans `in_proposal_box`, et le
tirage conditionnel `θ̂_n ~ U[0, cap − θ̂_m]` a **entièrement disparu** (vérifié : aucun domaine
`LEAK` résiduel, aucune dépendance entre coordonnées). Le rejet est définitif, sans reroll adaptatif.

**Preuve analytique attendue, absente.** Le package s'appuie sur trois tests statistiques ; ceux-ci
ne sont que des **diagnostics**. L'argument analytique — *si `X ~ Unif(B)` et que l'on rejette
jusqu'à `X ∈ A ⊆ B`, la loi de la sortie est `Unif(A)`, car `P(X ∈ S | X ∈ A) = |S|/|A|` pour tout
`S ⊆ A` mesurable* — n'est écrit nulle part comme preuve.

**Revendication littérale non bornée.** `propose_law_fields` affirme que le rejet
*« preserves uniformity on the accepted region **exactly** »*. C'est faux au sens littéral : le
générateur produit une **grille dyadique finie** de `2⁶⁴` points par coordonnée. Pas de doute
numérique — le pas mesuré vaut `6.01e-19` sur `θ̂` et `3.34e-21` sur les taux — mais **aucune borne
d'approximation n'est fournie**, et la revendication est posée comme une égalité.

De même, le tirage de taille `LATTICE_SIZES[⌊3·u⌋]` porte un **biais modulo** exact : les effectifs
de seaux sur `2⁶⁴` valeurs sont `6148914691236517205`, `6148914691236517205`, `6148914691236517206`,
soit un écart à `1/3` de `1/(3·2⁶⁴) ≈ 1,8·10⁻²⁰`. Négligeable, mais **présent**, alors que le package
écrit « tirage uniforme, donc `1/3` chacune » sans borne.

**À corriger :** distinguer explicitement (i) l'uniforme continue idéale, (ii) la loi numérique finie
réellement produite, (iii) la borne d'approximation de l'une par l'autre — et énoncer la preuve
analytique du rejet.

---

## 5. PRB-C — prédicat unique du moteur — **PASS, reproduit**

`engine_accepts` importe `LatticeBondSpec` depuis
`edlab.substrates.lattice_bond.engine`, c'est-à-dire **la classe de production acceptée**, et
n'utilise aucun wrapper. Le chemin d'acceptation est
`in_proposal_box(fields) ∧ engine_accepts(fields)`, sans autre conjonct.

Reproduction **indépendante**, sur une racine synthétique différente de celle du candidat :

| Épreuve | Résultat reproduit |
|---|---|
| 40 000 propositions : chemin d'acceptation vs `LatticeBondSpec(**fields)` | **0 divergence / 40 000** |
| 40 000 propositions : moteur vs oracle algébrique | **40 000 / 40 000 d'accord** |
| 48 points `nextafter` de part et d'autre des coupures (B1) et (B2) | **0 divergence / 48** |
| Taux d'appartenance à la boîte / efficacité globale | `0,4999` / `0,1027` |

Neuf champs sans dimension + les trois échelles à `1.0` ; champ inconnu ⇒ `TypeError` ⇒ refus ; NaN,
`±inf`, overflow, booléens ⇒ refus ; **toute** exception est un refus ; aucun défaut caché n'est
introduit par le module (les défauts éventuels sont ceux du moteur, ce qui est le comportement
voulu). L'oracle algébrique est prouvé **jamais** sur le chemin d'acceptation : remplacé par une
fonction qui lève, le plan se construit quand même.

**Bornes de la preuve, à énoncer.** Un accord fini ne prouve pas l'équivalence universelle. La
dérivation algébrique acceptée en 01S — à `dt = m_max = n_max = 1`,
`admissible ⟺ 1 < min(matter_dt_bound, resource_bond_dt_bound) ⟺ (B1) ∧ (B2)`, le `nextafter`
transformant `≤` en `<` — reste la preuve, et sa portée est **bornée au validateur inspecté** :
`LatticeBondSpec.__post_init__` du blob `0980525690ff38d84aa494581b2a68c6f8f44d8e`. Toute
modification future du moteur invalide la reproduction, non le principe.

**Note mineure :** `in_proposal_box` re-teste `resource_leak_floor ∈ [0,1]`, que le moteur teste
aussi. Ce n'est **pas** une réimplémentation de (B1)/(B2) — la revendication du rapport est donc
exacte — mais c'est une duplication d'une contrainte moteur. Sans effet : le chemin étant une
conjonction, la duplication ne peut qu'être plus stricte, jamais plus permissive.

---

## 6. PRB-D — rupture d'association — **REVISE (convention, non intégration)**

La cause `ASSOCIATION_GATE_TRACK_BREAK` est correctement définie : `DISSOLUTION` au frame `f`, **et**
au moins une arête candidate refusée avec `REJECT_CENTROID_DISTANCE` ou `REJECT_AREA_RATIO`, **et**
une cible de cette arête ouvrant un nouveau track par `APPEARANCE` au même frame `f`. La condition
discriminante — un support géométrique **existait** et la **porte** l'a refusé, par opposition à
`REJECT_NO_GEOMETRIC_SUPPORT` ou à l'absence de candidat — est la bonne.

Reproduit sur la fixture synthétique 16×16 : blob 2×2 en `(0,0)` puis en `(0,8)`, distance périodique
**8 > 3,0**, arête `REJECT_CENTROID_DISTANCE` présente, cause émise, état terminal
`DISSOLVED_DETECTED_TRACK`, `scores_one = False`. Contrôles opposés : disparition réelle **non**
étiquetée ; continuation d'une cellule **aucune** cause terminale ; idempotence vérifiée. Les cinq
états terminaux gelés sont respectés. `TrackTermination` **lève** si l'on tente `scores_one=True`.
La cause vaut zéro, reste au dénominateur, n'est pas une censure silencieuse et n'est pas
reclassable.

**Ce qui doit être dit et ne l'est pas.** `lifecycle.py`, `instrumentation.py`,
`future_lifecycle_owned_pipeline.py` et le pont de mesure sont **inchangés**, et
`classify_track_terminations` **n'est appelée par aucun d'eux**. Le commit définit donc une
**convention prospective plus un classificateur autonome**, et **non une intégration effective** :
aucun chemin de production n'émet aujourd'hui `ASSOCIATION_GATE_TRACK_BREAK`. Le rapport dit
correctement que le classificateur « lit `TrackingResult` et n'écrit rien », mais **n'énonce pas**
qu'il n'est pas branché. Cette cause ne doit **pas** être attribuée au tracker de production.

**Manque également** une branche explicite « motif ambigu ⇒ fail-closed » : le classificateur étiquette
dès qu'une arête de porte refusée coexiste avec une `APPEARANCE` au même frame, sans traiter le cas
où plusieurs motifs de refus hétérogènes coexistent.

---

## 7. PRB-E — `Δ` et plafond de claim — **REVISE**

### 7.1 Les onze axes

`DELTA_DEFINITION` porte bien onze clés : `symbol`, `compares`, `level`, `criterion`, `sign`, `unit`,
`aggregation`, `parameter_f`, `which_delta_the_ceiling_speaks_of`, `link_to_second_ic_discriminator`,
`estimand_is_marginal_over_size`.

Sont **corrects et suffisants** : quantités comparées (contre `Δ₀ = 0,50` et `Δ₁ = 0,25`, sans
groupe contrôle ni comparaison à une famille historique) ; niveau (**le tirage**, jamais l'entité) ;
signe (probabilité dans `[0,1]`, sans direction, non différence) ; unité ; agrégation (un Bernoulli
par loi, `k` sur 67, CP exact bilatéral 95 %, la seconde CI ne contribuant en rien) ; frontières ;
justification de `f` : `Δ` est monotone non décroissante en `f`, donc le bras POSITIF est lié par
`Δ(0,01)` et le bras NÉGATIF par `Δ(0,20)`, avec invariance exigée sur les trois valeurs, sinon
`INDÉTERMINÉ — CONVENTION_DE_REMPLACEMENT`. **`Δ` ne modifie jamais rétroactivement le verdict
primaire** — vérifié : aucun chemin ne réécrit `k`.

**Sont absents** : une entrée explicite de **dénominateur** (il n'est déductible que de
`aggregation`) ; la disposition des **cas invalides** (erreur technique, famille échouée, monde
non produit) ; et la **relation à la censure et à l'inéligibilité mécanique** — le lien n'est écrit
que vers le discriminateur de seconde CI.

### 7.2 Le garde-fou de plafond est lexical et présenté comme mécanique

Le rapport parle de « plafond machine-vérifiable » et d'inférences interdites « refusées
mécaniquement ». `check_claim_within_ceiling` est une **recherche de sous-chaînes** sur quinze
termes. Six sur-revendications testées ici **passent toutes** :

| Phrase testée | Verdict du garde-fou |
|---|---|
| *The component owns its internal information.* | **acceptée** |
| *Each entity governs its own repair after damage.* | **acceptée** |
| *This generalises to every law distribution.* | **acceptée** |
| *Evidence of complex life in the lattice.* | **acceptée** |
| *We found no dependence on initial conditions.* | **acceptée** |
| *The blob is self-maintaining and self-producing.* | **acceptée** |

La liste interdite omet en outre **« vie complexe »**, **« généralisation à d'autres
distributions »** et **« absence de dépendance aux CI »**, que le mandat exige explicitement.

**À corriger :** requalifier le garde-fou en **aide logicielle limitée**, jamais en garantie
sémantique, et compléter la liste. Le plafond réel reste **textuel et humain** : la densité, dans la
distribution gelée, de `persistance ∧ renouvellement matériel vérifié`, au niveau du tirage.

---

## 8. PRB-F — refus public — **PASS au sens étroit**

Le test importe et appelle **exactement**
`edlab.substrates.lattice_bond.future_lifecycle_owned_pipeline.run_owned_future_pipeline`, la
fonction publique réelle, et non un helper. Le refus survient à sa **première** vérification, avec
`OwnedPublicationError: run_directory must already exist`, donc avant : entropie ; seed, famille ou
namespace ; loi ou CI concrète ; appel moteur ; création de fichier ou de monde ; lecture de
résultat ; artefact persistant. Preuves associées : source d'acquisition espionne **0 invocation** ;
`LatticeBondEngine.step` remplacée par une fonction qui lève ⇒ **0 appel** ; `tmp_path` **vide**
après refus ; digest d'arbre identique avant/après.

**Bornes de la preuve, à énoncer.** Un digest d'arbre sur `tmp_path` ne prouve **ni** l'absence
d'accès réseau, **ni** l'absence de sous-processus, **ni** l'absence d'écriture hors de cette racine.
Ce qui est prouvé est : *aucun octet écrit sous la racine observée, aucune invocation de la source,
aucun pas moteur*. C'est suffisant pour la sous-obligation B15 ; ce n'est pas une preuve d'innocuité
globale.

**Ce que PRB-F ne prouve pas**, et que le rapport reconnaît déjà (RE-L2) : un contrôle réel de jeton
d'autorisation ; l'absence de contournement ; la sûreté des quatre autres entrées déclarées hors
protocole ; l'existence d'un futur chemin autorisé.

**Résolution dans la matrice §2.2 :** `PRB-5` exige un test de refus pour **cinq** points d'entrée.
Un seul en a un. **`PRB-5` reste ouvert**, même si `PRB-F` passe.

---

## 9. Tests réellement exécutés

Exécutés ici, séparément, dans un clean-room vérifié blob pour blob contre le candidat
(les quatre `hash-object` locaux reproduisent `12a19658…`, `9b9560b9…`, `faf9419b…`, `b10bf580…`) :

| Exécution | Résultat |
|---|---|
| `tests/test_future_route_e_pre_run_blocker_closure_00.py` seul | **104 passed** |
| Suite entière **moins** ce fichier | **673 passed** |
| Suite entière | **777 passed** |
| Collecte du fichier blockers | **104 collected** |
| Collecte totale | **777 collected** |

`104 + 673 = 777` : les groupes sont **disjoints**, **aucun double comptage**. **0 failed, 0 skipped,
0 xfail, 0 xpass, 0 deselected, 0 erreur de collection.** Environnement reproduit : Python
**3.11.15**, pytest **8.4.2**, numpy **2.4.4** — identique à l'annonce.

Les tests d'uniformité sont **déterministes** (racines synthétiques fixes, `SEED_A`/`SEED_B` dérivées
par SHA-256 de littéraux) : deux exécutions successives donnent le même résultat. Aucune donnée
scientifique n'est ouverte ; aucun round de beacon n'est interrogé (aucun accès réseau dans le
module) ; aucun artefact scientifique n'est produit. Des appels `engine.step` réels ont lieu — mais
**uniquement** dans les 673 tests mécaniques déjà acceptés en 01S, sur fixtures fabriquées ; les 104
tests de blockers n'en font **aucun**.

**Aucun chiffre non reproduit n'est repris dans ce record.**

---

## 10. Limitations

### 10.1 Déclarées par le candidat, et acceptées comme telles

`RE-L1` (discriminateur sous-dimensionné à `n = 67` : demi-largeur pire-cas `0,124721` contre
`0,0625` exigés par le principe de précision) ; `RE-L2` (le refus PRB-F n'est pas un contrôle de
jeton) ; `RE-L3` (écart d'un ulp concevable en IEEE-754, jamais utilisé comme gate) ; `RE-L4`
(étiquette de cause, pas un sixième état terminal) ; `RE-L5` (règle d'attribution, pas une coupure de
décision) ; `RE-L6` (aucun accès réseau) ; `RE-L7` et `RE-L8` (`PRB-1…PRB-6` ouverts, `PRB-5` en
particulier).

### 10.2 Non déclarées, relevées par cette revue

| ID | Limitation non déclarée |
|---|---|
| **HR-1** | La quantité de censure ne discrimine pas les causes ; telle qu'écrite elle recouvre les quatre états terminaux d'échec et l'inéligibilité (§3.2). |
| **HR-2** | Rien ne dit si un tirage censuré est un échec observé ou une valeur inconnue (§3.3). |
| **HR-3** | L'anti-reroll dépend d'un ancrage public antérieur au round, c'est-à-dire de `PRB-6`, ouvert (§4.2). |
| **HR-4** | Aucune exigence de vérification cryptographique de la signature du beacon (§4.3). |
| **HR-5** | Aucun comportement défini en cas d'indisponibilité du round (§4.4). |
| **HR-6** | Uniformité revendiquée « exactement » alors que le générateur produit une grille dyadique finie, sans borne d'approximation ; biais modulo de `1,8·10⁻²⁰` sur le tirage de taille, non borné (§4.5). |
| **HR-7** | Preuve analytique du rejection sampling absente ; seuls trois diagnostics statistiques sont fournis (§4.5). |
| **HR-8** | `Δ` sans entrée de dénominateur explicite, sans disposition des cas invalides, sans relation écrite à la censure et à l'inéligibilité (§7.1). |
| **HR-9** | Le garde-fou de plafond est lexical et trivialement contournable, mais présenté comme mécanique (§7.2). |
| **HR-10** | `ASSOCIATION_GATE_TRACK_BREAK` n'est branchée sur aucun chemin de production ; convention, non intégration ; pas de branche fail-closed pour un motif ambigu (§6). |
| **HR-11** | Le rapport cite le bloc §8 du record accepté en omettant son titre, donc sa portée (§2.5). |

---

## 11. Ce qui reste scientifiquement inconnu

**Tout.** Il n'existe aucune valeur de `Δ(f)`, aucune de `ψ`, aucune fraction de censure observée,
aucune fraction d'inéligibilité mécanique observée, aucune répartition observée sur les cinq états
terminaux, aucun monde Route E, aucune loi tirée, aucune condition initiale tirée, aucun seed
scientifique, aucun namespace, aucune famille.

Route E demeure **un protocole sélectionné, non confirmé**. Le seul résultat publié du programme
reste le premier article (`https://doi.org/10.5281/zenodo.21403458`), qui établit la persistance
causale à travers le renouvellement matériel **sans** ownership local, **sans** autonomie, **sans**
individualité complète, **sans** reconstruction, **sans** reproduction et **sans** hérédité.

Aucune donnée Stage B, `M_MINUS`, trajectoire, shard, candidat ou résultat historique n'a été ouverte
pendant cette revue. Aucune calibration à partir de données. Aucun seed ni round scientifique.
Aucune prérégistration commencée. Aucune autorisation d'exécution.

---

## 12. Prochaine mission conditionnelle

Les sources **n'autorisent aucun identifiant nouveau** pour une révision, et ce record n'en invente
aucun.

- **`ROUTE_E_REPLICATION_DENSITY_PREREGISTRATION_00` n'est PAS autorisée.** Le record accepté la
  conditionne littéralement à « fermeture **et** revue humaine des blockers », qui n'a pas eu lieu.
- La seule mission autorisée par les records reste **`FUTURE_ROUTE_E_PRE_RUN_BLOCKER_CLOSURE_00`**,
  dont le mandat — fermer `PRB-1 … PRB-6` — **n'est pas consommé**. La révision doit être conduite
  sous cet identifiant, et doit :
  1. traiter `PRB-1`, `PRB-2`, `PRB-3`, `PRB-4`, `PRB-5` et `PRB-6`, qui sont son objet ;
  2. corriger `HR-1` … `HR-11` sur le travail A–F déjà produit, qui reste **valide comme
     anticipation d'obligations de prérégistration** et n'a pas à être refait ;
  3. rétablir la portée exacte du bloc §8 du record accepté ;
  4. ne rien rouvrir de 01S, ne consulter aucune donnée, ne choisir aucun seed ni round.

Ce qui est **acquis et n'a pas à être refait** : la vérification Git complète ; l'arithmétique CP et
les frontières de censure ; la structure d'appariement des deux CI ; le prédicat d'acceptation moteur
et ses 40 048 points de reproduction ; la correction du tirage conditionnel ; le refus étroit de
`run_owned_future_pipeline` ; les 777 tests.

---

## 13. Firewall, remote et déclaration finale

**Firewall tenu.** Chemins Git exacts et `diff-tree` borné au couple parent–candidat, exigé par le
mandat de cette revue pour prouver l'absence de cinquième changement. `GIT_INDEX_FILE` neutralisé
explicitement. Aucun `git gc`, aucune suppression de résidu. **Aucun des quatre livrables candidats
n'a été modifié** — vérifié après coup : les quatre blobs du candidat sont inchangés. `main`
immobile, working tree sale préservé, véritable `.git/index` intact.

**Remote.** Une tentative de push **normale**, unique, de la seule branche de revue. Aucun `--force`,
aucun push de `main`, aucun `git add -A`, aucun changement de credentials, aucun retry.

> ## `scientific_run_authorized = false`
>
> Les obligations transportées PRB-A…PRB-F ne sont pas acceptées comme fermées.
> Les `PRE_RUN_BLOCKER` PRB-1…PRB-6 ne sont pas déclarés fermés.
> Aucun run n'est autorisé.
