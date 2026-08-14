# OBTC01 §5 — note append-only : cinq notions à ne plus confondre

Append-only. Aucun rapport gelé n'est modifié. Cette note fixe le vocabulaire que la suite du
projet doit employer, parce que trois missions consécutives ont buté sur le fait que le mot
« localisation » recouvrait au moins cinq propriétés distinctes.

---

## 1. Les cinq notions

### `SPATIAL_LOCALIZATION`

La population occupe une région bornée du domaine, petite devant le domaine. C'est une propriété
**de la distribution**, mesurable à un instant, sans référence à une cause. Elle se teste contre
un nul de hasard spatial complet.

**Établie pour le chémostat équilibré** : quantile observé du rayon `r80` égal à 0.000 contre le
nul de hasard spatial complet et contre le nul de permutation d'étiquettes, dans les six bras
hérités.

### `AUTONOMOUS_COHESION`

Il existe une interaction entre les molécules `X` qui les maintient ensemble : sans elle, la
distribution serait plus étalée. C'est une propriété **du mécanisme**, pas de la distribution.
Elle se teste contre un nul qui contient la source mais **aucune** interaction.

**Non établie.** CSC01 a mesuré un excès nul contre ce type de nul, et son unique mécanisme
candidat gelé, `C3_NEIGHBOUR_PROTECTED_DECAY`, a échoué 0 fois sur 6 contre un critère gelé de 5
sur 6.

### `SOURCE_ATTACHMENT`

La position de la population est déterminée par celle d'une source, et la suit quand elle bouge.
C'est encore une propriété du mécanisme, mais d'un mécanisme **externe** à la population.

**Observée** dans les données héritées — corrélation cœur–organisateur de 0.90 à 0.97, distance
typique de 2.6 à 3.3 cellules — mais **jamais qualifiée de façon confirmatoire** : elle n'a jamais
été le critère d'un gate gelé exécuté sur des graines fraîches. C'est l'objet de cette mission.

### `MATERIAL_TURNOVER`

Les unités qui composent la population à la fin ne sont pas celles du début : il y a un flux de
naissances et de morts qui traverse la structure. C'est une propriété **du flux**, indépendante de
toute question de forme ou de cause.

**Observée** — environ 36 renouvellements complets sur la fenêtre héritée — mais mesurée comme un
rapport de compteurs, jamais comme un suivi d'unités individuelles. OBTC01 l'enregistre au niveau
moléculaire.

### `ORGANIZATIONAL_PERSISTENCE`

La même structure identifiable persiste dans le temps, malgré le renouvellement de sa matière.
C'est une propriété **de la continuité**, qui se teste contre un nul détruisant la continuité
temporelle tout en préservant les distributions marginales.

**Partiellement observée** : le cœur se déplace de 0.23 à 0.29 cellule par intervalle de 10 pas
contre 8 à 12 pour des trames décorrélées, mais la chaîne d'identité par composante connexe se
rompt quelques fois par fenêtre.

---

## 2. Ce que la note affirme, explicitement

1. **Un nuage peut être localisé sans aucune interaction cohésive `X-X`.** Une source ponctuelle
   plus une durée de vie finie suffisent : la distribution stationnaire est la fonction de Green
   du marcheur amorti, de portée `ℓ = √(D/µ)`, sans qu'aucune molécule n'ait jamais « vu » une
   autre.

2. **Une source mobile suffit à produire une distribution bornée.** Elle borne la distribution
   *relativement à elle-même*. Le nuage peut alors parcourir tout le domaine sans jamais cesser
   d'être borné : « localisé » et « immobile » sont deux choses différentes.

3. **« Compatible avec le nul de source » ne veut pas dire « inexistant ».** C'est l'erreur de
   lecture la plus coûteuse disponible ici. Que les données soient compatibles avec un nul de
   source **identifie le mécanisme** ; elle ne dit pas que le phénomène est absent. Le nuage
   existe, il est mesurable, il est borné, il est renouvelé — et son mécanisme est la source, pas
   une cohésion.

4. **La localisation autour de l'organisateur n'établit pas un corps autonome.** Retirer la
   source doit faire disparaître le nuage. C'est ce qui distingue un nuage dissipatif lié d'un
   objet auto-lié, et c'est une expérience, pas une définition.

5. **L'échec de `C3` ne réfute pas le nuage lié à l'organisateur.** `C3` testait
   `AUTONOMOUS_COHESION`. Son échec laisse `SOURCE_ATTACHMENT` exactement où il était : observé,
   non qualifié. Les deux propositions sont indépendantes, et lire l'échec de la première comme un
   échec de la seconde serait une erreur de portée.

---

## 3. Ce que la note interdit

* Appeler `self-bound` un nuage dont la borne est portée par une source externe.
* Traiter « plus compact que le hasard » comme une preuve de cohésion.
* Traiter « compatible avec le nul de source » comme une preuve d'absence de structure.
* Traiter un test des signes secondaire comme compensant un résultat primaire de 0 sur 6.
* Utiliser l'indicateur d'étendue historique comme test d'enroulement topologique.

---

```
SPATIAL_LOCALIZATION           ÉTABLIE (contre le nul de hasard spatial complet)
AUTONOMOUS_COHESION            NON ÉTABLIE
SOURCE_ATTACHMENT              OBSERVÉE, NON QUALIFIÉE DE FAÇON CONFIRMATOIRE  -> objet d'OBTC01
MATERIAL_TURNOVER              OBSERVÉE au niveau des compteurs                -> à établir au niveau moléculaire
ORGANIZATIONAL_PERSISTENCE     PARTIELLEMENT OBSERVÉE
octets gelés édités            AUCUN
```
