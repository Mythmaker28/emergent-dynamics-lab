# ROUTE_E_REDESIGN_SOURCE_CAPTURE_DEV_02 — rapport

**2026-08-07** · 18 blocs t0 frais · 144 trajectoires · protocole scellé **avant** le premier appel
moteur (`bcdc06e6…`) · 0 échec technique · 0 modification du moteur.

---

## 1. Le probe est invalide, et je l'ai détecté par ses propres instruments

Les six bras à distance de graphe 1 affichent `realized_source_injection = 0,00` alors que le
retrait est normal. Cause mécanique : le filtre d'admissibilité gelé refuse **tout site source
ayant un 4-voisin dans le track** — or à distance 1, *tout* candidat est adjacent par définition.
**Le filtre de non-adjacence et le masque D1 sont logiquement incompatibles.**

Détecté par : `lattice_balance_error` égale à la masse retirée entière (0,104 à 2,219) alors que le
bilan lattice + réservoirs reste exact (**1,1 × 10⁻¹³**). Les six bras D1 sont donc **mal
étiquetés** : ce sont des bras `SINK_ONLY` à trois doses.

```
DECISION = PROBE_INVALID   (portée : les six bras D1 uniquement)
```

`REFINEMENT_PASSES = 0` était gelé : **aucun re-run n'a été tenté.**

## 2. Ce qui reste valide, et c'est substantiel

**Réplication du bras de référence D2 sur graines fraîches.** Ingress **2,97** (L=24) et **4,95**
(L=32) contre **3,09** et **5,01** dans DECOMPOSE_01 — soit 4 % et 1 % d'écart. La mesure de capture
est reproductible.

**Série dose-réponse d'ablation pure** — accidentelle mais parfaitement valide, puisque les bras D1
sont en réalité du retrait seul :

| L | dose | egress délivré | résidu initial à 2048 | survie |
|---|---|---|---|---|
| 24 | sham | 0,00 | 0,869 | 9/9 |
| 24 | 0,05·M₂₅₆ | 6,92 | 0,814 | 9/9 |
| 24 | 0,10·M₂₅₆ | 14,81 | 0,748 | 9/9 |
| 24 | **0,15·M₂₅₆** | 22,81 | **0,679** | **9/9** |
| 32 | sham | 0,00 | 0,899 | 9/9 |
| 32 | 0,05·M₂₅₆ | 12,99 | 0,845 | 9/9 |
| 32 | 0,10·M₂₅₆ | 27,29 | 0,776 | 9/9 |
| 32 | **0,15·M₂₅₆** | 41,81 | **0,706** | **9/9** |

**144/144 survivent à 2048**, coast comprise, à toutes les doses. Le retrait pur à 0,15·M₂₅₆ conduit
le résidu initial `PER_TRACK` à **0,679 / 0,706** : c'est le **renouvellement matériel le plus profond
atteint dans ce projet**, et il ne nécessite **aucune source externe**.

## 3. La leçon de conception

**C'est le filtre de non-adjacence qui plafonne la capture.** Il avait une raison correcte — une
cellule injectée directement dans le track ne doit pas compter comme ingress — mais il oblige la
matière fraîche à traverser un anneau vide, et la dynamique ne l'y transporte pas. Toute conception
de capture ultérieure doit soit **créditer l'ingress par le mélange plutôt que par l'adjacence**,
soit **mesurer directement la longueur de transport** au lieu de la supposer.

## 4. Portée

Aucune sortie n'établit `80_PERCENT_REPLACEMENT`, `AUTONOMOUS_TURNOVER`, `SELF_MAINTENANCE`,
`INDIVIDUATION`, `IDENTITY` ni `LIFE`. Le forçage reste externe et imposé. DEV uniquement,
`LAW_16` uniquement, sélectionnée post hoc ; aucune généralisation à d'autres lois.
