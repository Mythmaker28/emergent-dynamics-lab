# ROUTE_E_NONMERGING_CAUSAL_BRIDGE_DEV_00 — rapport

**2026-08-07** · 144 mondes moteur (budget exact) · 0 run primaire · 0 reproduction · holdout fermé
· 0 fichier de production modifié · 0 nouveau document d'audit.

---

## 1. Phase 1 — la question posée n'est pas exécutable

`NONMERGING_CONFIRM_02` **n'est pas une autre loi de Route E**. Les deux tournent sur des
**substrats différents à espaces d'états disjoints** :

| | Route E | NONMERGING_CONFIRM_02 |
|---|---|---|
| Moteur | `lattice_bond.engine.LatticeBondEngine` | `scaffold.engine.ScaffoldEngine` (pilote `sc_mcm`) |
| État | `LatticeBondState(m, n, b, step)` — **3 champs** | `SCState(rho, U, V, c, N, C, uptake, step)` — **7 champs** |
| `dt` | 1,0 | 0,1 |
| Géométrie | périodique L×L, L ∈ {16, 24, 32} | `size = 64` |
| Dynamique interne | aucune | réseau bascule interne (`a=2,0`, `K=0,5`, `D_int=0,008`, `τ=0,20`, `β=0,6`) |
| Cohorte | traceur passif sur l'union enrôlée | cohortes exactes, `Σ_c C == rho` |
| Lecture | résidu de cohorte | `uptake`, couplée à `m₊` par construction |

Aucun microétat initial n'est partagé : on ne peut pas donner un `LatticeBondState` à
`ScaffoldEngine.step`. Le contraste demandé — « même microétat, on remplace la dynamique » —
**n'a pas de domaine**.

```
CAUSAL_FACTOR (tel que posé) = SUBSTRATE
```

Ce n'est donc ni `LAW` ni même `DYNAMICS_PACKAGE` : ces deux étiquettes supposent un
substrat commun. L'effet ne doit être attribué à aucune loi.

## 2. Le substitut exécutable

Contenu scientifique de la question qui **est** testable : l'échec de `SWEEP_00` (aucun
composant borné non enroulé persistant) appartient-il à la loi unique utilisée, ou est-il
générique sur la mesure de lois gelée de Route E ?

Substrat **et microétat initial** tenus bit-identiques ; seule la `LawSpec` varie.

- 6 bras : `BASELINE_SWEEP00` + 5 lois tirées de `propose_law_fields` (la mesure gelée),
  chacune acceptée par `in_proposal_box()` **et** `engine_accepts()` — indices 15, 16, 19, 29, 35.
- 2 tailles (24, 32) × 12 graines `DEV_CAUSAL_BRIDGE_00` (910000-910011), **mêmes graines
  dans chaque paire causale** ⇒ 6 × 2 × 12 = **144 mondes**, le budget exact.
- Frames 0, 16, 32, 64, 128, 256, 512, 1024. Pont de mesure de production non modifié.

**Contrôles de mesure : 3/3 PASS** — composant compact borné détecté sans enroulement ;
bande enveloppante détectée comme enroulée ; champ vide → 0 composant.

**Vérification de l'appariement : 24/24.** À `(L, graine)` fixé, `labelled_fraction` mesurée
à la frame 0 est identique à 10⁻¹² sur les six bras — preuve directe que le microétat initial
était bit-identique avant toute dynamique.

## 3. Résultat

| Bras | L=24 survie | L=32 survie | paires discordantes (issue) | paires discordantes (cinétique) |
|---|---|---|---|---|
| `BASELINE_SWEEP00` | 0/12 | 0/12 | — | — |
| `LAW_15` | 0/12 | 0/12 | 0 | **0/24** |
| `LAW_16` | 0/12 | 0/12 | 0 | **12/24**, médiane +8, max **+112** |
| `LAW_19` | 0/12 | 0/12 | 0 | **0/24** |
| `LAW_29` | 0/12 | 0/12 | 0 | **11/24**, max **+112** |
| `LAW_35` | 0/12 | 0/12 | 0 | 1/24 |

- **144/144 mondes s'enroulent. 0 survivant borné. 0 PASS à f = 0,01 / 0,05 / 0,20.**
  Borne de Wilson conservatrice sur le taux de survie : **0,0000**. 0 échec technique.
- **Discordance appariée sur l'issue : 0 sur les 120 comparaisons.** Aucune loi ne retourne
  le sort d'un seul monde.
- **Mais la loi est causalement active sur la cinétique.** `LAW_16` et `LAW_29` retardent le
  premier enroulement dans la moitié des paires, jusqu'à **+112 pas**. `LAW_15` et `LAW_19`
  sont **exactement superposées** à la baseline.

Cohérence interne : les mondes enroulés dès la frame 0 (2 à L=24, 4 à L=32) sont **les mêmes
dans les six bras** — l'enroulement à t0 est une propriété de l'IC seule, avant tout pas.

```
DECISION = LAW_NOT_CAUSAL_FOR_SURVIVAL_WITHIN_FROZEN_MEASURE_AT_PRODUCTION_OCCUPANCY
```

Lecture : **la loi module le rythme, pas le sort.** À l'occupation de production, l'enroulement
est déterminé par la condition initiale, pas par la loi.

Piste corrélative, à n = 5 donc **non concluante** : les deux lois retardatrices ont les
`theta_m` les plus élevés (4,450 et 2,034) contre ≤ 1,299 pour les trois lois inertes.

## 4. Limitation dominante — et l'expérience qui manque

**Les 144 mondes sont à l'occupation de production (≈ 0,55), c'est-à-dire dans le régime que
`SWEEP_00` a déjà montré 100 % enroulant.** Le résultat ferme donc « la loi sauve-t-elle Route E
dans le régime enroulant ? » et rien d'autre.

La cellule informative reste **non testée** : `SWEEP_00` a montré qu'en régime dilué
(p ≈ 0,20-0,35) l'échec n'est plus l'enroulement mais la **dissolution totale**. Personne n'a
encore croisé *occupation diluée* × *variation de loi*. C'est exactement l'expérience suivante,
et elle tient dans le même budget.

Autres limitations : 5 lois sont un échantillon de la mesure, pas la mesure ; schedule non
uniforme à 8 frames (l'enroulement est une fonction en escalier, donc cela ne peut pas changer
le signe d'un nul, mais un transitoire entre deux frames échantillonnées serait manqué) ;
aucun monde scaffold n'a été couru — le budget `MAX_ENGINE_WORLDS = 144` était intégralement
consommé, et une mesure scaffold aurait été une **référence**, jamais un contraste apparié.

## 5. Sortie positive en parallèle — `CONFIRM02_PUBLICATION_PACKAGE_00`

Livré par un agent distinct, en parallèle, sans interrompre le pont. Manuscrit, métadonnées
Zenodo, registre de provenance et manifeste de dépôt. **71 chiffres tracés : 69 VÉRIFIÉS,
1 NOT_FOUND, 1 DIFFERS.** La chaîne `6470513 → 9b7580bc → 830c2d0 → 9c8a62c` existe localement
et les 8 hachages du PRESEAL sont intacts au sceau **et** au tip.

Deux corrections importantes remontées :

- **« reproduit bit-identique » ne doit pas être affirmé du run de confirmation.** La
  bit-identité documentée est un contrôle DEV à deux runs sur les graines 50001-50010. Le run
  prospectif a été exécuté une seule fois, par conception.
- Une reproduction exacte de l'**étage d'analyse** a été exécutée : tous les chiffres de tête
  reproduisent bit-à-bit ; 5 flottants de G2 diffèrent de 1 à 3 ULP hors de la plateforme
  scellée, ce que le sceau prévoit explicitement. Aucun chiffre rapporté ne change.
- **Bloquant avant tout dépôt** : `release/LICENSE-CODE` et `release/LICENSE-DATA-TEXT`
  contiennent encore le marqueur `[COPYRIGHT HOLDER — to be confirmed by the author]`.

Fait annexe, non interprété : `origin/exp/lci-causal-nonmerging-confirm-02` pointe sur
`9c8a62c`, alors que le dossier indique « rien poussé ».
