# Registre de nouveauté des programmes antérieurs

| programme | intervention exacte | exécutable / LawSpec | unité | point de mesure | horizon | statut des données | revendication maximale |
|---|---|---|---|---|---|---|---|
| **CHMR** | permutations conservatives cœur/halo (`halo_cross`, `core_cross`, `double_cross`), `core_erase`, `orphan_halo` | `sc_mcm` + `ScaffoldEngine` gelé | bloc fondateur | `CORE_DEPENDENT_HALO_RECONSTRUCTION` | 350 pas d'imposition + 700 de renouvellement | 256 trajectoires, DEV et confirmatoire disjoints, `NEAR` tenu à l'écart utilisé | voir la résolution ci-dessous |
| **PPAI** | aucune : construction d'un LawSpec | **nouveau** `PPAIEngine`, `κ(z) = 1 + g·tanh z` | — | fenêtre de lavage public | — | arrêt `NO_WASH_WINDOW` | le gain nul reproduit **bit à bit** la référence expurgée construite |
| **ETPC** | transfert affine de moyennes sur `(z̄_A, z̄_B)` | `PPAIEngine`, `g = 1/3` | bloc fondateur | moyenne de `c` sur un disque de rayon 8, intégrée | 40 / 200 pas | 10 blocs, **développement définitivement** | infrastructure de jumeaux valide ; **exécution confirmatoire invalide** |
| **EEFCA** | aucune (`AUDIT_ONLY`, 0 démarrage moteur) | — | — | audit de conformité | — | rétrospectif sur ETPC | l'opérateur n'était pas involutif ; le point de mesure n'était pas celui autorisé |
| **ETNBFC** | transposition d'octets sur paires à `ρ` **byte-identique** | `PPAIEngine` | bloc fondateur | flux natif réalisé `c`/`N` | 1 cycle | 4 blocs DEV | support d'appariement **vide** ; registre par face absent à gain nul |
| **ETCMNFC** | transposition d'octets sur paires à **poids** identiques | `PPAIEngine` | bloc fondateur | flux natif réalisé `c`/`N` **par composante** | 1 pas natif | 4 blocs DEV | opérateur **qualifié** ; point de mesure à **support vide** |
| **WSCPL00** | 5 familles déjà implémentées, dont l'ablation totale du porteur | `PPAIEngine`, inchangé | bloc fondateur | **branche macro** (dominance de masse A/B) | 400 pas | 3 blocs de formulation | **le point de mesure n'est pas réactif à l'intervention** |

## Résolution de la revendication `CHMR`, depuis ses artefacts gelés

Les slogans « le halo écrase le cœur » et « le cœur ne peut pas reconstruire le halo » sont
remplacés par ce que l'adjudication scellée dit réellement :

```
DISPOSITION                    = HALO_OVERWRITES_CORE
                                 (critère du cœur ATTEINT ; critère de la RÉPONSE NON atteint)
CORE_REBUILDS_HALO             = REFUTED       (G5 échoue, aux deux géométries)
PASSIVE_ENVIRONMENTAL_TRACE    = REFUTED       (le halo apparié retient 1,7-2,0x l'orphelin)
STATIC_ENVIRONMENTAL_CONTROL   = PARTIAL
MUTUAL_CORE_HALO_ATTRACTOR     = REFUTED
TRANSIENT_MIXED                = REFUTED       (p = 0,00049, deux géométries)
WRITER_CAUSATION               = IDENTIFIABLE et mesurée : +0,024 de maintenance
STRONG_PAPER_GATE              = FAIL
```

Formulation soutenue par les artefacts, et la seule à réutiliser : *dans cette `LawSpec`, la
couche externe locale gouverne la couche interne ; un état environnemental local transitoire,
imposé par une permutation exactement conservative pendant 350 pas puis retiré, détruit
durablement 85 à 91 % du marqueur interne d'une matière qui se renouvelle à 80 %.*
Le **critère de réponse n'a pas été atteint** et `STRONG_PAPER_GATE = FAIL` : cela doit
accompagner la citation, pas être laissé de côté. L'arithmétique reconciliée et le résultat exact
de renouvellement sont préservés ; la revendication `CORE_TO_HALO_0.97_PERCENT` reste **RETIRÉE**.

## Pourquoi ne pas relancer le même point de mesure de transport

- une coupe native cœur→matière environnante serait identifiable, mais vérifierait surtout la
  conséquence locale immédiate du `κ(z)` construit — un fait de conception, pas une découverte ;
- la propagation totale à la frontière externe est un estimand systémique **sans attribution
  A/B**, dont l'horizon est vulnérable à la sélection rétrospective ;
- deux corps disjoints seraient une **nouvelle fondation**, pas une réplication.

`WSCPL00` pose une question différente : la structure causale se transfère-t-elle entre échelles,
et prédit-elle des familles d'interventions non vues ?
