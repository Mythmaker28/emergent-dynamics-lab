# ROUTE_E_ABLATION_DEPTH_DEV_03 — rapport

**2026-08-07** · protocole scellé **avant** le premier appel moteur (`531849b4…`) · 18 blocs t0 frais ·
144 trajectoires · 18/18 `T256_VALID` · 0 échec technique.

---

## 1. Ce qui était testé

`REDESIGN_CAPTURE_02` avait montré que le **retrait pur** faisait descendre le résidu sans coûter
une seule survie. Cette mission pousse l'échelle de dose jusqu'à **2,00 × M₂₅₆** pour voir si on
atteint la porte gelée de Route E — **résidu ≤ 0,20** sur un composant borné suivi en continu,
coast comprise. C'est un tir direct sur le critère lui-même, pas sur un substitut.

## 2. Résultats bruts

**144/144 survivent à 2048**, à *toutes* les doses, coast comprise. Aucun enroulement, aucune
dissolution, aucune perte de piste. Le retrait pur ne tue jamais le disque.

| dose × M₂₅₆ | résidu L=24 | résidu L=32 | egress L=24 | survie |
|---|---|---|---|---|
| 0,00 (sham) | 0,865 | 0,901 | 0,00 | 9/9 |
| 0,15 | 0,676 | 0,711 | 22,8 | 9/9 |
| 0,30 | 0,504 | 0,510 | 46,8 | 9/9 |
| **0,50** | **0,422** | **0,433** | 56,1 | 9/9 |
| 0,70 | 0,404 | 0,431 | 63,4 | 9/9 |
| 1,00 | 0,398 | 0,429 | 66,4 | 9/9 |
| 1,40 | 0,394 | 0,426 | 67,5 | 9/9 |
| 2,00 | 0,392 | 0,425 | 68,7 | 9/9 |

**Plancher de résidu ≈ 0,39 (L=24) et ≈ 0,43 (L=32), atteint dès la dose 0,50.** Quadrupler la
dose ensuite déplace le résidu de moins de 0,03 : le puits sature (egress 56 → 69 pour une dose ×4).

```
PORTE ROUTE E (résidu ≤ 0,20) : 0 / 144
DECISION = RESIDUAL_FLOOR_ABOVE_GATE
```

## 3. Le point qui compte — et il change la lecture de toute la chaîne

Le résidu est mesuré **par rapport à M₂₅₆**, la masse initiale. Il baisse donc aussi quand le
composant **rétrécit**, sans aucun renouvellement. En divisant plutôt par la **masse actuelle** du
track, on obtient la vraie composition :

| dose × M₂₅₆ | masse/M₂₅₆ L=24 | **composition** L=24 | masse/M₂₅₆ L=32 | **composition** L=32 |
|---|---|---|---|---|
| 0,00 | 0,991 | **0,872** | 0,996 | **0,904** |
| 0,50 | 0,488 | 0,866 | 0,480 | 0,902 |
| 2,00 | 0,460 | **0,853** | 0,472 | **0,900** |

**La composition ne bouge pratiquement pas : 0,872 → 0,853 et 0,904 → 0,900.** Le disque qui
survit reste fait à **85–90 % de sa matière d'origine**, exactement comme le sham.

Autrement dit : **le retrait pur ne renouvelle pas, il rétrécit.** Toute la chute apparente du
résidu est un artefact de perte de masse — précisément le confondant que `AGENTS.md` nomme pour le
cas miroir (« un objet ayant seulement grossi ») ; ici c'est un objet qui a seulement maigri.

## 4. Conséquence pour la suite

Le renouvellement exige un **afflux** de matière étrangère dans le composant. Or c'est exactement
ce que les deux missions de capture ont montré bloqué : la matière fraîche n'arrive pas à traverser
l'anneau vide qui sépare la source du track. Retirer davantage ne remplacera jamais ce manque —
c'est arithmétiquement impossible, puisque la composition est bornée par ce qui entre.

La question n'est donc plus « quelle dose de retrait », elle est **« comment faire entrer de la
matière étrangère dans un composant compact »**, et le verrou identifié est le crédit d'ingress
par adjacence plutôt que par mélange.

## 5. Portée

Aucune sortie n'établit `80_PERCENT_REPLACEMENT`, `AUTONOMOUS_TURNOVER`, `SELF_MAINTENANCE`,
`INDIVIDUATION`, `IDENTITY` ni `LIFE`. Le forçage reste externe et imposé. DEV uniquement,
`LAW_16` uniquement, sélectionnée post hoc ; aucune généralisation à d'autres lois. Graines
970000-970108, exclues à jamais de tout primary, reproduction ou holdout.
