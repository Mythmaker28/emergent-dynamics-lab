# ROUTE_E_LAW16_OCCUPANCY_FRONTIER_PAIRED_DEV_01 — rapport

**2026-08-07** · 72 blocs initiaux uniques · 144 trajectoires appariées · horizon 2048 ·
0 run primaire · 0 reproduction · holdout fermé · 0 fichier de production modifié ·
0 raffinement · 0 échec technique.

---

## 1. Disposition honnête du pont précédent

Le `REPORTED_TIP` transmis (`ddbda94c…`) est **le commit du balayage parent**, pas celui du
pont. Résolution séparée :

```
AUTHENTIC_SWEEP_TIP    = ddbda94c2edb6b35d89e1a1203ff08702b9803fc
BRIDGE_ARTIFACT_COMMIT = 86a258e5051b30c36c542f94695208c96abd62e3
```

**Je n'adopte pas l'étiquette suggérée `BRIDGE_NOT_IDENTIFIABLE_ON_RECOVERED_SUBSTRATE` :
elle est fausse.** Le pont *a* été identifié — `NONMERGING_CONFIRM_02` a été localisé
exactement (`scaffold.ScaffoldEngine` piloté par `sc_mcm`, `SCState` à 7 champs, `dt=0,1`,
`size=64`, réseau bascule interne). Il est inexécutable parce que les espaces d'états sont
**disjoints**, pas parce qu'il serait introuvable. Disposition inscrite :

```
ORIGINAL_CAUSAL_BRIDGE_EXECUTED = false
ORIGINAL_BRIDGE_STATUS = BRIDGE_IDENTIFIED_AND_NOT_EXECUTABLE_DISJOINT_SUBSTRATES
```

### Corrections au parent

| Point | Statut |
|---|---|
| « une fraction enrôlée identique prouve un microétat bit-identique » | **RÉTRACTÉ** — non sequitur : un scalaire ne contraint ni l'organisation spatiale, ni les champs internes, ni l'égalité octet à octet |
| `PARENT_MICROSTATE_PAIRING` | **`CODE_PATH_ONLY`** — chaque bras appelle le même `initial_state(L, seed)` ; régénération déterministe confirmée 24/24 champ par champ, mais **aucun hash de microétat n'a été écrit dans les sorties** ⇒ `HASH_VERIFIED` non revendicable |
| `PARENT_UNIQUE_INITIAL_BLOCKS` | **24** (pas 144) — L=24 utilise 910000-910011, L=32 utilise 911000-911011, **aucune graine partagée** ⇒ 24 clusters conservateurs |
| `PARENT_INITIAL_GATE_FAILS` | **6** (2 à L=24, 4 à L=32) ⇒ risk set causal = **18 blocs**, pas 24 |
| `PARENT_POST_STEP_RANDOMNESS` | **`NONE`** — moteur vérifié déterministe (deux runs identiques, digest de composants identique) |
| « médiane +8 frames » | **checkpoints censurés par intervalle** : les deltas bruts sont `{0:12, +16:6, +48:5, +112:1}` sur une grille espacée de 16. Ce n'est **pas** une résolution temporelle observée de 8 frames |

`PARENT_KINETIC_INTERPRETATION` = **`POST_HOC_LAW_DEPENDENT_KINETIC_ASSOCIATION`**, pas un
contrefactuel bit-identique démontré.

## 2. Frontière localisée sur les lignes authentiques

Règle gelée appliquée aux lignes de `ROUTE_E_DEV_SWEEP_00` (tailles 24 et 32) :

- **`p_D = 0,35`** — plus haut niveau à H=1024 avec 0 survivant borné et 6/6 blocs en
  dissolution-avant-enroulement aux deux tailles.
- **`p_W = 0,55`** — plus bas niveau > `p_D` avec ≥80 % d'enroulement-avant-dissolution aux
  deux tailles (taux 1,00 / 1,00). **0,45 échoue la règle** : taux 0,75 / 0,75, sous le seuil
  de 0,80.
- ⇒ `OCCUPANCY_GRID = [0,35 · 0,45 · 0,55]`

**La grille attendue `[0,35 · 0,40 · 0,45]` n'est pas utilisée** : `0,40` n'a jamais été un
niveau testé, et l'inventer serait une calibration non gelée.

## 3. Appariement — cette fois prouvé

Pour chacun des 72 blocs : état généré une seule fois ; `m`, `n`, `b` hachés séparément
(sha256 des octets en ordre C, avec dtype, shape, contiguïté, somme) ; deux copies profondes ;
**`np.array_equal` champ par champ avant le premier pas (assertion)** ; re-hachage des deux
copies et égalité assertée ; `initial_microstate_sha256` identique écrit dans les deux bras.

```
NEW_PAIRING = HASH_AND_ARRAY_EQUAL_VERIFIED
FACTOR_NAME = LAW          (moteur déterministe, aucune innovation stochastique post-pas)
MEASUREMENT_CONTROLS = PASS (3/3 : borné persistant, bande enroulante, série dissoute)
COHORT_RESIDUAL_SCOPE = GLOBAL_UNION
INDIVIDUAL_REPLACEMENT_INTERPRETATION = NOT_AUTHORIZED
```

## 4. Résultats

72 blocs, **63 admissibles à t0**, 9 `INITIAL_GATE_FAIL` (tous à p=0,55 : 6 à L=24, 3 à L=32).

| p | L | adm. | survie 2048 base / LAW_16 | b / c / both | enroulement perdu / gagné | Δ vie : non nuls, médiane, max |
|---|---|---|---|---|---|---|
| 0,35 | 24 | 12 | 0 / **3** | **3 / 0 / 0** | 0 / 0 | 6, +0, **+2032** |
| 0,35 | 32 | 12 | 0 / 0 | 0 / 0 / 0 | 0 / 0 | 7, +0, +80 |
| 0,45 | 24 | 12 | 0 / 0 | 0 / 0 / 0 | **7 / 0** | 2, +0, +48 |
| 0,45 | 32 | 12 | 0 / 0 | 0 / 0 / 0 | **6 / 0** | 2, +0, +48 |
| 0,55 | 24 | 6 | 0 / 0 | 0 / 0 / 0 | 1 / 0 | 2, +0, +16 |
| 0,55 | 32 | 9 | 0 / 0 | 0 / 0 / 0 | 4 / 0 | 0, +0, +0 |

### Deux faits à ne pas perdre

**(a) Trois mondes survivent à 2048 sous LAW_16, aucun sous la baseline**, à p=0,35 / L=24
(graines 920004, 920006, 920009). C'est la première persistance d'un composant borné non
enroulé jusqu'à 2048 dans ce projet. Elle **n'atteint pas la barre préenregistrée**
(b≥4 par taille aux deux tailles ; test exact apparié p = 0,25) et **ne réplique pas à L=32**.
Et leur résidu à 2048 vaut 0,598 / 0,612 / 0,633 pour un plancher `labelled_fraction` de
0,449 / 0,501 / 0,476 : **ils échouent la porte de résidu**, cohérent avec le plancher
d'union globale établi par `SWEEP_00`.

**(b) Défaut de spécification de la règle 4.** La règle nomme `WRAPPING_FIRST` et
`DISSOLUTION_FIRST` comme premiers échecs *seuls* — or dans ce régime la perte de piste
co-survient dans **tous** les mondes, donc aucune de ces deux étiquettes n'apparaît jamais
seule et la règle **ne peut pas se déclencher**. Le motif qu'elle visait est pourtant présent
et **répliqué aux deux tailles** : à p=0,45, l'implication de l'enroulement dans le premier
échec est **perdue** sous LAW_16 dans 7/12 paires à L=24 et 6/12 à L=32, et **gagnée dans
0/12** aux deux tailles. Rapporté, **non utilisé pour changer la décision**.

**(c)** `TRACK_LOSS` est l'échec liant presque partout : c'est le **proxy de continuité
déclaré**, pas l'enroulement ni la dissolution, qui fixe la métrique primaire dans ce régime.
`ComponentMeasurement` ne porte pas de `track_id`, donc l'identité stricte de piste n'est pas
observable depuis la sortie du pont de production.

## 5. Décision

Règles gelées appliquées dans l'ordre : R1 échoue (b=[3,0], c=[0,0], p=0,25) · R2 échoue ·
R3 échoue (both = 0 partout) · R4 échoue (littéralement inapplicable, voir 4b) · R5 échoue à
`p_W` (2 et 0 deltas non nuls, il en faut ≥5) ⇒

```
DECISION = NO_LAW16_FRONTIER_EFFECT
```

`INITIAL_GATE_YIELD_INSUFFICIENT` ne s'applique pas : p=0,35 et p=0,45 conservent 12/12 blocs
admissibles aux deux tailles. En revanche **le test cinétique prospectif de R5 était condamné
d'avance** : il devait être évalué à `p_W = 0,55`, où la porte initiale ne laisse que 6 blocs
à L=24 et où les durées de vie sont écrasées contre le plancher.

Aucune sortie n'établit `INDIVIDUATION`, `IDENTITY`, `BOUNDED_ENTITY`, `GLOBAL_IDENTITY`,
`DISTAL_BEHAVIOR`, `GRADED_METROLOGY`, `TURING`, ni ne réfute Route E ou
`NONMERGING_CONFIRM_02`. Une durée de vie accrue n'est pas une survie ; une survie DEV à 2048
n'est pas une confirmation.
