# `WSCPL00` — inventaire des données et de l'oracle de redémarrage (Phase A)

## A1. Provenance

| élément | valeur |
|---|---|
| commit parent `ETCMNFC` (résolu, jamais deviné) | `c5171b72f3ed2cdaba1968bdbd9ebf3776eab8d7` |
| branche parent | `confirm/exact-twin-canonical-mf0-native-flux-00` |
| ascendance | `c5171b7 → d86d248 → de1524b → 3f8dae8 → ba92a16 → 586108f` |
| bundle `ETCMNFC` | `bd94d9ad88fc584de8aa53eedbc36f4e7e0017d7e18f8d749f257851348654d5` |
| bundle `ETNBFC` | `d13b38d992798f9212195e73c970afa19c1fa90853e0b2c4d8eb0b0995ef5937` |
| bundle `EEFCA` | `c752d185b3e79594ebbff91e1553113a377b4c986cba4ae44d94788239406ae6` |

**Espaces primaires et tenus à l'écart : toujours fermés.** Aucun artefact `62000–62009`,
aucun `etpc_HELDOUT.pkl`, aucun identifiant primaire alloué par `ETNBFC` ou `ETCMNFC` — les deux
se sont arrêtés en amont de l'allocation. Aucun n'est lu ici.

## A2. Artefacts de développement utilisables

| artefact | complet pour un redémarrage exact ? |
|---|---|
| `ETNBFC/checkpoints/dev_FAR_6100{0..3}.npz` | **OUI** — les huit champs canoniques `rho, U, V, c, N, C, uptake, Mf` plus le compteur de pas, avec manifeste de hachage commis |
| `ETPC/etpc_PRIMARY.pkl` | **NON — REJETÉ.** Ne contient que des moyennes sur support, des empreintes publiques et des vecteurs de réponse. **Aucun tableau spatial.** Impossible d'en redémarrer le moteur. |
| `CHMR/*.pkl`, `DOMC/*.pkl` | non audités ici ; non nécessaires, les quatre points de contrôle DEV suffisent |

## A3. Oracle causal exact

```
point de contrôle complet → intervention gelée → moteur repris → résultat macro
```

Établi et vérifié dans les programmes parents, revérifié ici par usage :

- **aller-retour bit-exact** du point de contrôle : `E.save` / `E.load`, hachage logique
  identique (`ETNBFC`, 4/4 blocs, y compris entre sessions et processus) ;
- **non-interrompu contre repris** : identique bit à bit sur la fenêtre (`ETCMNFC` T2) ;
- **jumeau sham** : le crochet identité est bit-identique à l'absence de crochet ;
- **absence d'aléa après le point de contrôle** : le pas moteur ne contient **aucun tirage** ;
  le seul objet stochastique est `seed_state(..., "random")`, évalué une fois à `t = 0` avant
  toute branche (audité en `ETPC`, réaudité en `EEFCA`).

`WSCPL00_DISPOSITION = NO_RESTARTABLE_CAUSAL_ORACLE` n'est **pas** déclenché : l'oracle existe et
fonctionne.

## A4. Opérateurs d'intervention déjà implémentés

Inventoriés, jamais inventés : `etcmnfc_core.transpose` (transposition appariée du porteur),
`ppai_core.state_cross` (réflexion intensive), `domc_core.reciprocal_cross` (réflexion
extensive), `ppai_core.erase_all` / `chmr_core.core_erase` (ablation totale du porteur),
`domc_core._perturb_N` (perturbation environnementale), plus `erase_half`, `halo_cross`,
`core_cross`, `double_cross`, `orphan_halo`, `reciprocal_cross_roll`, `reciprocal_cross_env`.

**Cinq familles structurellement distinctes** sont donc disponibles, au-delà du minimum de trois.
`INSUFFICIENT_INTERVENTION_FAMILY_DIVERSITY` n'est **pas** déclenché.
