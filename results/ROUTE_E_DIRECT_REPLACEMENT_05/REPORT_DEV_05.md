# ROUTE_E_DIRECT_INTERFACE_REPLACEMENT_FRONTIER_DEV_05 — rapport

**2026-08-09** · parent `7e418282` · 18 blocs t0 frais · **9 blocs indépendants par taille** ·
144 trajectoires logiques · 162 appels moteur · 0 échec technique · 0 fichier de production
modifié · **protocole des DEUX stages scellé avant la première préphase**
(`85d37725cd9c3bc859f7fb111c6765afeecec3d3c5262ae316eda7b38381d208`, garde exécutable).

---

## 1. Corrigendum du parent, enregistré sans le modifier

```
PARENT_DIRECT_RESULT = PROMISING_DESCRIPTIVE_SIGNAL_UNVERIFIED
```

`04R` concluait `DIRECT_INTERFACE_EXCHANGE_TOLERATED_DEV = true` **et** `DIRECT_CONTROL_ONLY_VALID`
alors que son ledger était absent, ses invariants causaux `FAIL` et son compteur de capture
directe `FAIL 0/18`. C'était incohérent. Le `95,9 %` est une part de **décisions de placement
acceptées à distance de graphe 1**, jamais une fraction de masse. `MERGER_CAPTURE`,
`DYNAMICS_MEDIATED_CAPTURE_FOUND` et `EP_1_OF_9` passent à **NOT_IDENTIFIABLE / NOT_AUDITABLE**.
Détail dans `parent_04r_claim_corrigendum.md`.

## 2. Porte zéro — échange physique, pas réétiquetage

8/8 contrôles, **0 appel moteur**. Les faits qui comptent :

- **Les sélecteurs ne peuvent pas lire la provenance** : `select_sink_sites`,
  `select_source_sites`, `sink_capacity` et `source_capacity` ne prennent pas `prov` en paramètre
  et ne nomment aucune cohorte. Ce n'est pas une convention, c'est une impossibilité de signature.
- **Delta physique réel** : `max|Δm| = 0,900 > 10⁻⁹`, masse déplacée 2,000 pour un événement de
  quota 1,0. Un pur réétiquetage laisse `m` **bit-identique** : le résultat n'est pas atteignable
  en ne changeant que les étiquettes.
- **Atomicité** : retiré ≡ injecté à 10⁻⁹ ; si un côté est impossible, l'événement entier est
  rejeté et **aucun** côté n'est muté.
- **Retrait proportionnel** : le rapport core/bnd d'une cellule est inchangé par le puits.
- **Identité exacte** `CORE+INTER+BOUNDARY+AMBIENT+FRESH = TOTAL`, résidu 0,0.
- **Aucun compteur `credited`/`credit`/`age` n'existe dans le code** (vérifié par AST). Le défaut
  structurel qui avait invalidé `04R` ne peut pas se reproduire : le champ n'existe pas.

```
OPERATOR_NONTRIVIALITY = PASS
PARENT_OPERATOR_REPLICATION = REDESIGNED_PRESEAL
```

La **physique** est celle du parent (même géométrie d'interface, même quantum, même calendrier,
même retrait proportionnel, même payload de matière nue). L'**instrumentation** est refaite. Donc
`REDESIGNED_PRESEAL`, pas `EXACT`. 28/28 fixtures sans moteur, dont advection des cinq cohortes
(résidu 1,1·10⁻¹⁶) et scission / fusion / perte / réacquisition.

## 3. Stage A — l'ancre réplique, cette fois avec ledger

`T256_VALID = 9/9` aux deux tailles, initialisation exacte 18/18, invariants 36/36.

```
STAGE_A_GATE = PASS      18/18 blocs passent les huit critères
```

Ce n'est pas rien : le signal descriptif de `04R` **se réplique sur graines fraîches**, avec un
ledger événementiel, une lignée continue et une provenance à identité exacte. À `Q100`,
`F/T = 0,238` (L=24) et `0,208` (L=32), contre `0,260` / `0,221` au parent.

## 4. Stage B — la frontière, et où elle s'arrête

Dose = **nombre d'événements**, quantum gelé à `M₂₅₆/80`. Médianes à l'horizon terminal.

| L=24 | I/I₀ | I/T | F/T | A/T | T/M₂₅₆ | rempl. apparié | lignée |
|---|---|---|---|---|---|---|---|
| SHAM | 0,695 | 0,727 | 0,000 | **0,273** | 0,952 | 0,000 | 9/9 |
| Q100 | 0,594 | 0,592 | 0,238 | 0,163 | 0,984 | 0,226 | 9/9 |
| Q200 | 0,498 | 0,501 | 0,314 | 0,178 | 0,987 | 0,288 | 9/9 |
| Q400 | 0,422 | 0,417 | 0,383 | 0,198 | 1,011 | 0,324 | 9/9 |
| **Q800** | **0,385** | 0,382 | 0,376 | 0,242 | 1,010 | 0,309 | **2/9** |
| SINK_ONLY Q800 | **0,262** | 0,651 | 0,000 | 0,349 | **0,404** | 0,000 | 9/9 |
| SOURCE_ONLY Q800 | — | — | — | — | — | — | **0/9** |

| L=32 | I/I₀ | I/T | F/T | A/T | T/M₂₅₆ | rempl. apparié | lignée |
|---|---|---|---|---|---|---|---|
| SHAM | 0,763 | 0,773 | 0,000 | **0,227** | 0,984 | 0,000 | 9/9 |
| Q100 | 0,661 | 0,669 | 0,208 | 0,125 | 0,989 | 0,205 | 9/9 |
| Q400 | 0,493 | 0,499 | 0,337 | 0,167 | 0,987 | 0,317 | 9/9 |
| **Q800** | **0,419** | 0,415 | **0,396** | 0,189 | 1,006 | 0,339 | 9/9 |
| SINK_ONLY Q800 | **0,306** | 0,728 | 0,000 | 0,272 | **0,419** | 0,000 | 9/9 |
| SOURCE_ONLY Q800 | 0,892 | 0,544 | 0,272 | 0,185 | **1,642** | 0,000 | 9/9 |

```
FORCED_COMPONENT_TURNOVER_80 = 0/9 partout      DIRECT_SOURCE_REPLACEMENT_80 = 0/9 partout
DECISION = DOSE_RANGE_INSUFFICIENT
```

Multiplier la dose par **8** fait descendre `I/I₀` de 0,594 à 0,385 (L=24) et de 0,661 à 0,419
(L=32). La porte demande **0,20**. `F/T` sature vers **0,38–0,40** et le remplacement apparié vers
**0,31–0,34**, loin des 0,80 exigés. Le protocole interdit d'étendre au-delà de `Q800` après
inspection, et je ne l'étends pas.

## 5. Quatre faits mécanistiques qui, eux, tiennent

**(a) Le couplage atomique est ce qui préserve l'objet.** Les bras couplés tiennent
`T/M₂₅₆ = 0,98–1,01`, porte de masse 9/9. Découplés, les deux moitiés détruisent le composant
autrement : le **puits seul** descend `I/I₀` à 0,262 — le meilleur retrait de toute la mission —
mais avec `T/M₂₅₆ = 0,40` et `I/T = 0,651`, c'est-à-dire **un rétrécissement**, pas un
renouvellement (porte de masse 0/9) ; la **source seule** perd la piste **9/9 à L=24** et gonfle
la masse à `1,642` à L=32 (porte de masse 0/9).

**(b) L'ambiant fait une part du travail, sans aucun opérateur.** Le SHAM atteint
`A/T = 0,273` (L=24) et `0,227` (L=32) et perd déjà 24–30 % de sa cohorte initiale à t=12544.
Une partie du « turnover » mesuré n'est donc **pas attribuable à la source contrôlée** : c'est le
plus gros terme non contrôlé de toute la mission.

**(c) La cadence compte, et c'est apparié.** À dose, quantum, premier et dernier temps de force
**identiques**, le burst est **moins** efficace : `I/I₀` plus haut dans **7/9** paires à L=24
(médiane +0,011) et **9/9** paires à L=32 (médiane **+0,041**), avec `F/T` plus bas des deux côtés.
Direction cohérente aux deux tailles.
```
RATE_DEPENDENT_REPLACEMENT = OBSERVED (paired, both sizes)
```
Cela **réfute explicitement** la phrase que j'avais retirée en `04R` — « un calendrier ne déplace
pas un plafond de livraison ». Il le déplace : grouper les événements ne laisse pas la capacité du
puits se reconstituer entre eux.

**(d) L'échafaudage incumbent survit.** À `Q800`, le plus grand amas incumbent connecté fait encore
**44 cellules** (L=24) et **126 cellules** (L=32), et le noyau `CORE_256` garde `0,239` / `0,303`
de `I₀`. Même si la porte de 0,20 avait été franchie, il aurait fallu la qualifier
`BULK_TURNOVER_WITH_PERSISTENT_INCUMBENT_SCAFFOLD`.

**Frontière de rupture.** `Q400 → 9/9` intacts puis `Q800 → 2/9` à L=24, par perte de piste dans
7 blocs ; à L=32, `Q800` reste `9/9`. Le crochet est réel **et apparié à L=24**, mais **non
répliqué à L=32** : je ne l'adopte pas comme décision.

## 6. Ce que cela n'établit pas

```
AUTONOMOUS_RENEWAL = NOT_TESTED     IDENTITY = NOT_ESTABLISHED
INDIVIDUATION = NOT_ESTABLISHED     LIFE = NOT_ESTABLISHED
GENERALIZATION_BEYOND_LAW_16 = false    ROUTE_E_VERDICT = NONE
ORGANIZATION_PRESERVATION = NOT_TESTED
```

Aucun observable organisationnel validé n'existait avant cette mission ; je n'en ai pas inventé et
je n'ai créé aucun seuil après observation. Le plafond de revendication reste
`TRACKED_COMPONENT_CONTINUITY_UNDER_FORCED_TURNOVER`. L'inférence est **n = 9 blocs indépendants
par taille, une seule LawSpec** ; les 144 trajectoires ne sont **jamais** n = 144. Une rupture ne
réfute que le calendrier, la géométrie et la gamme testés.

## 7. Suite

Le terme dominant non contrôlé est l'**ambiant** : il fournit 0,23–0,27 de la piste sans aucun
opérateur, et il est du même ordre que tout ce que la source a gagné entre `Q400` et `Q800`.
Tant qu'il n'est pas partitionné — d'où vient-il, par quelle frontière, et peut-on le supprimer ou
le marquer — aucune montée en dose n'est interprétable, et la saturation observée à `F/T ≈ 0,39`
ne peut pas être attribuée.
