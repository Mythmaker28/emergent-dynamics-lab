# RCD01 §6 — AUDIT DES INTERVENTIONS CAUSALES EXECUTABLES

## Ce qui existe

**`organiser_off_at`** — `OBTC02/code/engine_obtc.py:126` (constructeur), `:220-229` (`_one_step`).

Effet exact :

```python
y = self.n["Y"].copy()
self.n["Y"] = self.n["Y"] - y
self.n["WY"] = self.n["WY"] + y
```

**Portee spatiale : GLOBALE.** Ces trois lignes mettent a zero le champ Y **entier** en une
operation. Rien dans le chemin de controle ne permet de designer une cellule, une region ou
un centre.

Ce que l'intervention ne touche pas : l'occupation est conservee exactement, aucune molecule X
n'est deplacee, creee ou detruite, aucune ressource n'est modifiee, et Y sort par le meme canal
`Y -> WY` qu'une desintegration spontanee. C'est une intervention propre — mais globale.

Elle est deja utilisee : les bras R du test de dependance causale a la source d'OBTC02
(`protocol_obtc02.py:81`) l'emploient pour retirer l'unique organiseur et mesurer la decroissance
du nuage X.

## Ce qui n'existe pas

["any per-cell or per-centre Y removal", "any selective source suppression", "any spatially scoped inactivation", "any per-centre resource gate"]

`CLASSIFICATION = GLOBAL_ORGANISER_OFF_ONLY`

## Consequence

R2 functional independence cannot be tested with the engine as it stands. Removing the parent with organiser_off_at removes the daughter at the same instant, because the operation is a single global zeroing of the Y field.

## La plus petite capacite manquante

**`selective_organiser_off`** — at a declared step, remove Y only from the cells belonging to one named spatial centre under the frozen toroidal single-linkage partition, through the same Y->WY channel, conserving occupancy exactly, touching no X and no resource.

**Pourquoi ce n'est pas un changement d'architecture :** it manipulates the experiment at a declared instant. It adds no term to the autonomous law: between interventions every rate, every candidate rule and every update remains bit-identical. The existing global organiser_off already establishes the precedent and the channel; only the spatial scope changes.

Qualification exigee avant tout usage scientifique :

- bit-identical trajectories when the intervention is not armed
- occupancy conservation at the intervention step
- no X molecule moved, created or destroyed
- no resource field touched
- the untouched centre's cells provably unaffected at that step
- a deterministic parent/daughter tie-break declared in advance
