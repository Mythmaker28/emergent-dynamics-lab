# RCD01 §4 — REPRODUCTION N'EST PAS HEREDITE

## Deux definitions, deliberement separees

**REPRODUCTION** — production d'une nouvelle organisation independamment fonctionnelle
de la meme classe operationnelle.

**HEREDITE** — transmission d'un etat ou d'un trait VARIABLE de l'organisation parente a
l'organisation descendante, telle que la ressemblance soit causalement attribuable a la
descendance.

L'architecture actuelle peut soutenir la premiere sans la seconde. Exiger l'heredite pour
definir la reproduction confondrait deux questions distinctes et rendrait la premiere
intestable ici.

## Existe-t-il un trait variable capable de porter une heredite ?

Non. Inventaire des etats qui distinguent un centre d'un autre dans cette architecture :

| Etat | Variable entre centres ? | Peut-il porter une heredite ? |
|---|---|---|
| `kY`, `muY`, `muX`, `kX`, `phi`, `omega`, `CAP`, `S0`, `p_hop` | non — globaux, imposes | **non** |
| occupation locale X, Y, SX, SY, WX, WY | oui, mais purement quantitative | non — un nombre de molecules n'est pas un etat transmissible |
| position du centre | oui | non — la loi est invariante par translation sur le tore |
| nombre de cellules Y occupees | oui | non — pas d'etat interne attache |
| identite de particule | oui en principe | **rejetee** : FLCR01 a montre qu'elle n'est pas l'identite organisationnelle |

Les parametres du LawSpec sont **identiques pour tous les centres par construction**. Ce sont
des lois environnementales globales, pas de l'information heritee. Les appeler « heredite »
serait une erreur de categorie : deux cristaux qui poussent dans la meme solution ne s'heritent
pas l'un de l'autre leur structure.

**Aucun genome n'est invente ici.** Il n'y a, dans cette architecture, aucun degre de liberte
interne au centre qui puisse etre a la fois variable, persistant et transmis.

`HEREDITY_STATUS = NOT_TESTED` — et, plus precisement, **pas encore definissable** faute d'un
porteur de variation. Si l'heredite devient un objectif, il faudra d'abord montrer qu'un tel
porteur peut exister, ce qui serait une question d'architecture et non de mesure.
