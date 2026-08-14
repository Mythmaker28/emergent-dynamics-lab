# OBTR01 — notes append-only

Ce fichier est **append-only**. Aucune entrée n'est modifiée ni supprimée après écriture. Aucun
artefact d'une mission antérieure n'est réécrit : les entrées ci-dessous ne font que *lire* les
artefacts livrés et *ajouter* un enregistrement daté.

---

## A-1 — 2026-08-14 — clôture de la déviation d'adjudication post-run d'OBDI02

**Concerne** la violation de protocole qu'OBDCA01 a établie contre OBDI02, et elle seule.
`OBDI02/out/_adjudication.json`, `OBDI02/out/_results.json`, `OBDI02/out/_freeze.json`,
`OBDCA01/out/_adjudication.json` et `OBDCA01/out/_recompute.json` **ne sont pas modifiés**.

### Ce qui s'est passé

Le protocole gelé d'OBDI02 lie la décision primaire à `equivalence_margin = 0.25` et lie la
qualification globale à la conjonction de deux conditions, et de deux seulement :

> *« the global qualification requires BOTH the population support gate AND the conditional
> equivalence test »* — `obdi02_protocol.yaml`, `population_support_gate.qualification`

Les deux ont été satisfaites. Le fichier `OBDI02/code/analysis_obdi02.py`, qui est un fichier
**POST_RUN de rang 7** dans la hiérarchie des sources de vérité établie par OBDCA01 §3, a
néanmoins ajouté après ouverture des résultats une troisième condition,
`primary_interval_inside_[-0.042, +0.042]`, et c'est elle qui a sélectionné la disposition
rapportée. Or le gel lui-même qualifie ce chiffre de *« reported, never decisive »* et le
déclare **sous-puissant avant tout run** (puissance 0,314 à la taille d'échantillon gelée).

### Les quatre vérifications imposées par le mandat

Le mandat n'autorise cette note que si la déviation n'a touché **ni les données, ni le gate, ni
le gel, ni les trajectoires**. Chacun de ces quatre points a été vérifié contre les artefacts,
et non supposé. Le détail chiffré est dans `OBTR01/out/_obdi02_deviation_closure.json`.

| Catégorie | Vérification effectuée | Résultat |
|---|---|---|
| **Gel** | les 16 fichiers de `METHODS_CORE` re-hachés depuis leurs octets ; `METHODS_CORE_HASH` recalculé par la construction lue dans `freeze_obdi02.py` (`nom \| NUL \| empreinte \| LF`, noms triés) | 16/16 identiques au bit près ; le hachage reproduit `59b19169…d525f1b` — **UNTOUCHED** |
| **Trajectoires** | autorité d'empreinte = les identifiants de blob git de la branche livrée ; `git hash-object` recalculé sur les octets des 138 fichiers bruts ; les graines présentes comparées à `FRESH_FLAT` | 138/138 blobs recalculés, 0 modifié, 138 graines déclarées = 138 présentes, aucune en double — **UNTOUCHED** |
| **Gate** | la règle de qualification gelée ré-évaluée ; les trois exigences de validité technique par bras réévaluées sur les 138 bras depuis le bloc `technical` enregistré (identité flux/table des comptes de trames et des deux empreintes, accord en ligne/post-hoc) | les deux conditions gelées satisfaites ; 0 bras en échec sur les trois exigences ; 138/138 bras planifiés exécutés — **UNTOUCHED** |
| **Données** | l'estimand primaire recalculé indépendamment par OBDCA01 comparé à la valeur enregistrée par OBDI02 | `β = 0.082194877633092259` des deux côtés, **identique au bit près** ; `se` également ; test gelé à la marge 0,25 : **PASS** — **LABEL_ONLY** |

### Cause structurelle, et non seuil déplacé

Le protocole gelé d'OBDI02 énumère neuf dispositions admissibles mais **ne gèle aucune règle**
qui associe le vecteur d'issues à l'une d'elles. C'est ce vide, et non un seuil déplacé, qui a
laissé un fichier post-run choisir l'étiquette. La leçon est un défaut de conception de
protocole ; elle n'est pas une mesure corrompue. La conséquence opérationnelle pour OBTR01 est
enregistrée en §24 : la règle de sélection de la disposition est gelée **avant** tout résultat.

### Direction de la déviation

`0.042 < 0.25`. La condition ajoutée est donc **strictement plus forte** que la condition
gelée. Une condition strictement plus forte ne peut que *retenir* une qualification ; elle ne
peut jamais en accorder une. La déviation est par conséquent conservatrice : elle a refusé une
qualification que le gel accordait. Elle n'a fabriqué aucun résultat, n'a déplacé aucun seuil
dans le sens permissif, n'a écarté aucun bras et n'a remplacé aucune graine. Elle reste une
violation et est enregistrée comme telle.

### Statuts consignés

```
OBDI02_POSTRUN_ADJUDICATION_DEVIATION = CONFIRMED
DEVIATION_DIRECTION                   = CONSERVATIVE_FALSE_NONQUALIFICATION
FROZEN_EVIDENCE_STATUS                = UNAFFECTED
CUMULATIVE_CLOUD_EVIDENCE_STATUS      = VALID
OBDCA01_FORMAL_LIMITATION             = QUALIFICATION_SUPPORTED_DESPITE_RECORDED_POSTRUN_ADJUDICATION_DEVIATION
CLOSURE                               = CLOSED_APPEND_ONLY
```

Aucune catégorie bloquante n'est atteinte, donc la mission **ne** s'arrête **pas** à
`INHERITED_EVIDENCE_NOT_CLOSED` et peut se poursuivre.

Ce que cette note **ne** fait **pas** : elle ne remplace pas la disposition rapportée par
OBDI02, elle ne réécrit pas son rapport et elle ne prétend pas que la disposition conforme
`ORGANIZER_BOUND_TURNOVER_CLOUD_QUALIFIED_BY_DOMAIN_PRECISION_CLOSURE` a été prononcée. Elle
enregistre que la preuve gelée la supportait et que l'étiquette publiée ne l'a pas suivie.

---

## A-2 — 2026-08-14 — récupération, vérifiée par empreinte, des artefacts MTW01

**Concerne** `MINCORE-TIMESCALE-WINDOW-01` (MTW01), dont le répertoire est **absent du dépôt
livré**. OBDCA01 et les missions antérieures ne pouvaient citer ses quantités que par empreinte,
via `MCM01/out/MCM01_APPEND_ONLY_CORRECTIONS.md` §C-2.

Les artefacts ont été retrouvés hors dépôt et **vérifiés contre les empreintes gelées avant
cette mission** :

- `MTW01/out/_window.json` → `3a1b7ae50a6ea82730d7b33f15aeacca31c457a3ae6b77483b71895964216342`,
  dont le préfixe `3a1b7ae5` et le suffixe `216342` sont exactement ceux que C-2 enregistre ;
- les 19 fichiers de `MTW01_SHA256SUMS` vérifient **OK**, sans exception ;
- l'unique tête du paquet `MTW01_gen2_branch.bundle` est
  `85ba2d8892b82e2d0060b1b174b63fc1b950b43f`, soit le commit `85ba2d8` que C-2 et
  `MCM01_FINAL_REPORT.md` désignent tous deux.

**Statut attribué** : `HISTORICAL_ARTEFACTS_RECOVERED_AND_DIGEST_VERIFIED`, hors dépôt livré.
Ces fichiers sont traités comme **source primaire pour la reconstruction de la question
historique** (§5) et **jamais** comme source d'une décision de cette mission : aucun seuil,
aucune marge, aucune disposition d'OBTR01 n'en dérive. Ils sont copiés tels quels, sans
modification, sous `OBTR01/verify/mtw01/`, et leurs empreintes sont réenregistrées dans
`OBTR01/out/_provenance.json`.

---
