# ROUTE_E_DSC04_RAW_ONLY_CAUSAL_CLOSURE_04R — rapport

**2026-08-08** · parent `f4f0a936fbccea096e63a75de6c9e5b8ec7d1878` · **0 appel moteur** ·
0 graine · 0 trajectoire · 0 artefact parent modifié · toute donnée dérivée écrite dans
`CLOSURE_04R/` · 8/8 tests sans moteur.

Cette clôture renverse le résultat principal de sa propre mission parente.

---

## 1. Vérification matérielle

Commit `f4f0a93` existe, est un descendant vérifié de `5869283` et de `28dbf40`, et la chaîne
`ddbda94 → 86a258e → d276992 → 5e31527 → 72350f9 → 28dbf40 → 5869283 → f4f0a93` est intacte.
Archive `ca743415…`, bundle `49afa73e…` (`bundle verify: okay`). Les 14 fichiers annoncés sont
présents, et leur SHA-256 est inchangé avant et après cette clôture
(`RAW_DATA_IMMUTABLE = true`).

**Un artefact brut exigé par le cahier des charges de la mission parente n'a jamais été produit :
`dynamic_source_capture_event_ledger`.** Preuve d'absence : aucun fichier correspondant dans le
répertoire de travail, dans `DSC_DELIVERY/`, dans l'archive ni dans l'arbre git de `f4f0a93` ;
et `dsc_harness.branch()` lit `r["sites"]` uniquement à l'intérieur de l'assertion, sans jamais
l'écrire. La géométrie par injection est donc **non reconstructible sans re-run**.

```
PARENT_ARTIFACTS = INCOMPLETE      EVENT_LEDGER_STATUS = RAW_INSUFFICIENT
```

## 2. Preseal, et ce qui a réellement changé

Les neuf fichiers scellés — dont le harnais, les deux opérateurs, le tracker et la provenance —
sont **byte-identiques au sceau**. `dsc_final.py`, qui porte l'évaluateur d'endpoint, **n'a jamais
été scellé** et a été corrigé après le run (deux bugs de véracité Python). Les vingt conditions et
la règle d'agrégation 7/9 étaient, elles, scellées **en texte** dans le protocole avant tout appel
moteur.

```
PRESEAL_STATUS = ANALYSIS_IMPLEMENTATION_CORRECTED_POSTSEAL
```

Ce n'est pas un pipeline intégralement inchangé après scellement, et je retire cette formulation.
Un troisième évaluateur, écrit ici, n'utilisant que `is None`, `== 0` et `<= tolérance`, reproduit
**1/144**, sur la même trajectoire (L=24, `Q050`, graine 980002). Impact des deux bugs sur les
décisions d'endpoint : **0**.

**Les 36 « rejeux parents » sont 36 vraies trajectoires moteur**, pas des rejeux d'opérateur :
`dsc_audit.replay()` appelle `prephase()` puis `eng.step()` sur 2048 pas. Elles précèdent le sceau
et **leurs sorties ont choisi les bras, les distances et l'échelle de dose**.

```
PARENT_ENGINE_INVOCATIONS = 36   (pre-seal, design-selecting)
PARENT_OPERATOR_REPLAYS   = 0
MISSION_ENGINE_INVOCATIONS = 162
```

Les graines du pilote (960xxx) sont disjointes des graines de mission (980xxx), donc les 18 blocs
frais restent prospectifs pour leurs propres données ; le **design**, lui, est informé par pilote.
`SINK_ONLY`, `SOURCE_ONLY_LEGACY`, `SOURCE_ONLY_REDESIGNED` et `COUPLED_REDESIGNED_PULSE` n'ont
jamais été instanciés.

```
PROMPT_CONFORMANCE = PROSPECTIVE_BUT_OFF_PROMPT
SOURCE_ONLY_EFFECT = NOT_TESTED     SINK_ONLY_EFFECT = NOT_TESTED     PULSE_EFFECT = NOT_TESTED
```

**Je retire la phrase « un calendrier ne déplace pas un plafond de livraison ».** Elle est fausse :
la cadence fixe le temps de récupération entre événements, donc la capacité libérée par événement,
donc la résidence, la formation de satellites et les fusions.

## 3. Le résultat principal du parent est renversé

Le seul enregistrement par injection que le parent ait conservé est `reject_counts`, un histogramme
de **décisions** par trajectoire. Il suffit à trancher.

| voie d'injection | décisions | part |
|---|---|---|
| `ACCEPTED_SUBTHRESHOLD_ADJACENT` — distance de graphe **1** de la piste courante | **67 309** | **95,9 %** |
| `ACCEPTED` — distance ≥ 2, halo réellement distant | 2 892 | 4,1 % |

`D1_REDESIGNED` à L=24 : **100 % de coque, 0 décision de halo distant** — la masse de halo distant
y est **exactement nulle**, pas estimée.

`P2'` autorise un site adjacent à recevoir de la matière tant qu'il reste sous le seuil du
détecteur. Le composant ne grandit donc pas : **l'écart topologique est bien préservé**. Mais le
site porte alors une masse fraîche strictement positive à une cellule de la piste : il n'est
**pas** matériellement vide. C'est un `SHELL_PRELOAD`, et par définition gelée un préchargement de
coque ne peut produire ni `DYNAMICS_MEDIATED_CONTACT` ni `DYNAMICS_MEDIATED_CAPTURE`.

```
TOPOLOGICAL_GAP_PRESERVED          = true
MATERIAL_GAP_PRESERVED             = false
CAUSAL_CONTACT_SEPARATION_PRESERVED = false
```

Mon « plus petit relâchement sûr » était sûr sur une seule des trois dimensions, et j'ai présenté
cette dimension comme les trois. La réparation « 18/18 blocs » est une réparation du
**préchargement de coque**, c'est-à-dire exactement ce que le prédicat `P2` interdisait.

Second point : le couplage atomique fait que, sans source, le puits ne tire pas non plus. Le bras
`D1_LEGACY` n'a donc **rien fait du tout** (L=32 : injection 0,000 *et* retrait 0,0000, comme le
SHAM). Le « contraste de filtre » oppose donc *aucune opération* à *un préchargement de coque*.

## 4. Les compteurs causaux sont invalides

Trois défauts structurels, prouvés par analyse du code, pas par échantillonnage :

- **`credited` n'est pas advecté alors que `fre` l'est.** Le crédit absorbant est statique par
  cellule et la matière fraîche se déplace dessous. Un simple transfert interne A→B produit
  0,600 de « capture » sans qu'aucune matière ne soit entrée dans le composant (test 3).
- **`contact` et `capture` sont deux crédits indépendants**, aucun ordre n'est imposé.
- **`incorporation_16` somme toute la matière fraîche de la piste**, toutes voies confondues.

Conséquence sur les invariants de chaîne, sur 144 trajectoires :

| invariant | respecté |
|---|---|
| `contact ≤ injection` | 142/144 |
| `capture ≤ contact` | 110/144 |
| `incorporation_16 ≤ capture` | **36/144** |
| `durable_128 ≤ incorporation_16` | 144/144 |
| `capture = 0` sur le bras d'insertion directe | **0/18** |

```
CAUSAL_SET_INVARIANTS = FAIL
```

Le bras d'interface directe, dont la capture dynamique doit valoir zéro par construction, affiche
10,5 (L=24) et 13,9 (L=32). `unique_capture_transport` ne mesure donc pas la capture médiée par la
dynamique ; il mesure « de la matière fraîche est apparue dans une cellule dont le crédit n'avait
pas suivi », sans égard à la provenance.

**Le plafond de 6 % est renversé.** Il était mesuré sur des bras fusionnants. Sur l'ensemble à
risque **jamais fusionné**, l'échelle de dose compte n = 9, 0, 2, 0 (L=24) et 5, 4, 1, 3 (L=32) :
deux points sur quatre sont **vides** à L=24. Aucun plateau non fusionnant n'est établi.

Ce qui **survit** à un test apparié : l'englobement dépasse le transport dans **9/9** trajectoires
à dose 1,00 aux deux tailles (delta médian +5,77 et +11,15) — mais pas à dose 0,05 à L=24 (4/9).
La provenance `INCUMBENT_256` est correcte : elle est construite à t256 depuis `cells256`, vaut
exactement 1 par construction, et le résidu d'identité de champ borne la dérive. `0,865` **est**
bien `INCUMBENT_256/M256` et non un traceur `t0`.

Enfin, `6,3·10⁻¹⁵` est un **résidu flottant d'identité de champ**, pas une « erreur algébrique
exacte ». Je renomme.

## 5. Ce qui survit

Le contrôle direct, intégralement, et il est le seul.

| | L=24 (min / médiane / max) | L=32 |
|---|---|---|
| masse / M₂₅₆ @2048 | 0,983 / 0,997 / 1,018 | 0,985 / 0,987 / 0,999 |
| fraction fraîche @2048 | 0,249 / **0,260** / 0,276 | 0,211 / **0,221** / 0,232 |
| résidu incumbent @2048 | 0,589 / 0,606 / 0,621 | 0,657 / 0,674 / 0,682 |
| rétention de dérive | 0,979 / 0,981 / 0,987 | 0,980 / 0,986 / 0,992 |
| jamais fusionné · piste continue | **9/9 · 9/9** | **9/9 · 9/9** |

```
DIRECT_INTERFACE_EXCHANGE_TOLERATED_DEV = true
```

Cela signifie exactement une chose : **le composant suivi tolère au moins la quantité observée
d'échange matériel imposé par l'opérateur.** Cela n'établit ni capture halo, ni renouvellement
autonome, ni remplacement à 80 %, ni identité, ni individuation, ni vie. Le compteur
`unique_capture_transport` de ce bras est à jeter ; aucune des mesures ci-dessus n'en dépend.

## 6. Portes globales — inchangées

`ROUTE_E_VERDICT = NONE` · `SCIENTIFIC_PRIMARY_RUN_AUTHORIZED = false` ·
`BOUNDED_ENTITY`, `IDENTITY`, `LIFE` = `NOT_ESTABLISHED` ·
`GENERALIZATION_BEYOND_LAW_16 = false`.
