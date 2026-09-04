# TBRT02 — BALAYAGE D'ANTÉRIORITÉ

> **Rien de ce qui suit n'agit sur la campagne.** Aucun critère, aucun seuil, aucune graine n'est
> touché. Ceci alimente la discussion de l'adjudication finale, jamais les critères. Écrit pendant
> que la campagne tourne, sans l'interrompre.
>
> Le balayage a été demandé via un connecteur arXiv/alphaXiv. Ce connecteur n'est pas disponible
> dans cette session ; j'ai utilisé la recherche web. **Chaque référence a été vérifiée comme
> existante avant d'être écrite ici** — une suggestion externe peut contenir des citations
> plausibles mais fausses, et une référence inventée dans un dépôt scientifique est pire que pas de
> référence du tout. Ce que j'ai lu et ce que j'ai seulement vérifié sont distingués à chaque fois.

---

## 1. Hintze & Bohm (2026) — **VÉRIFIÉE, LUE**

*Rethinking self-replication: detecting distributed selfhood in the outlier cellular automaton*,
npj Complexity, doi:10.1038/s44260-026-00074-2 ; préprint arXiv:2508.08047.

**Ce qu'elle établit.** Une « formation » est *toute collection d'amas*, pas nécessairement
contiguë. L'individualité est définie par **cohésion causale** et non par continuité spatiale : une
entité est « un ensemble évolutif d'états de cellules dont chaque pas dépend causalement d'états
antérieurs de cette entité, sans influence externe ». Ils construisent un **graphe d'ascendance
causale** au niveau des cellules, puis l'agrègent aux amas et aux formations. Ils disent
explicitement : « plusieurs amas disjoints peuvent ensemble former une entité qui se réplique ».

**Ce qu'elle NE fait pas** : aucune ablation, aucun retrait, aucun déplacement. Ils s'appuient
entièrement sur le traçage causal de la fonction de transition, et rejettent explicitement l'analyse
contrefactuelle — « ce qui contribue activement, pas ce qui aurait pu se produire dans des
histoires contrefactuelles ».

**Effet sur TBRT02 — le plus important du balayage, et il coupe dans les deux sens :**

- **MENACE le modèle A.** Définir un centre comme une composante connexe est bien une hypothèse
  contestée par la littérature actuelle. C'est exactement le point de la tâche 2, et il est fondé.
- **CONFORTE le modèle C.** Leur méthode et la nôtre sont de la même famille : fermeture causale sur
  un graphe d'ascendance. CLEA01 y est arrivé indépendamment. Une convergence de méthode obtenue
  sans se lire est un argument de solidité, pas de redondance.
- **LAISSE INTACTE la conception de TBRT02, et lui donne même sa raison d'être la plus forte.**
  CLEA01 a montré que le traçage causal *seul* devient dégénéré quand l'intervention supprime la
  seule source concurrente : dans le bras traité, « tout descend de la fille » est vrai par
  construction et n'explique rien — 0 cellule-ligne rejetée sur 43 742 251. **La méthode de Hintze
  et Bohm, appliquée au bras SELECTIVE d'OMLDCT02, aurait heurté exactement cette dégénérescence.**
  Leur rejet du contrefactuel est un choix méthodologique, pas une démonstration que l'intervention
  est illégitime. TBRT02 fait les deux : traçage causal *et* intervention qui laisse un concurrent
  avec provenance connue. C'est complémentaire, et c'est défendable.

## 2. Sayama & Nehaniv — **VÉRIFIÉE EXISTANTE, NON LUE INTÉGRALEMENT**

*Self-Reproduction and Evolution in Cellular Automata: 25 Years After Evoloops*, Artificial Life
31(1):81, doi:10.1162/artl_a_00451 ; arXiv:2402.03961.

**Statut honnête :** je n'ai obtenu que le résumé. Il établit que l'évolution darwinienne de
structures auto-reproductrices est possible dans des automates cellulaires déterministes, et annonce
un bilan des accomplissements, des difficultés et des directions futures — sans que le résumé
détaille lesquelles. **Je n'ai pas lu les 21 pages et je ne prétendrai pas savoir ce qu'elles
disent.** À reprendre avant toute rédaction d'un article : c'est la revue de référence du domaine et
elle décidera de ce qui est réellement nouveau.

**Effet sur TBRT02 : indéterminé pour l'instant.** Ni menace ni appui établis.

## 3. Reynolds, Ponce-Dawson & Pearson (1997) — **VÉRIFIÉE EXISTANTE, NON LUE**

*Self-replicating spots in reaction-diffusion systems*, Phys. Rev. E **56**(1):185–198,
doi:10.1103/PhysRevE.56.185.

**Pourquoi c'est la menace la plus sérieuse du balayage.** Des taches qui se divisent par
appauvrissement du cœur en réaction-diffusion sont un phénomène connu depuis presque trente ans. Si
la « fille » que ce programme détecte n'est qu'une division de tache par appauvrissement — le
substrat SY se vide au centre, la tache se scinde — alors le phénomène n'est pas nouveau et
l'ordonnanceur `decay → feed_and_outflow` en est le mécanisme.

**Ce que le balayage ne peut PAS trancher.** Cela ne se règle pas par une recherche web. Il faut
comparer les mécanismes : mesurer si la scission observée est précédée d'une déplétion du cœur en
SY, comme chez Reynolds et al., ou si elle procède autrement. **C'est mesurable sur les archives
existantes, sans nouveau monde**, et c'est consigné ici comme travail à faire — pas fait, pas
esquivé.

**Effet sur TBRT02 : menace non résolue sur l'interprétation, aucune sur la validité.** La
conception, les bras et la condition de réfutation restent corrects quelle que soit la réponse.
Ce qui changerait, c'est ce que le phénomène *est*, pas si TBRT02 le mesure bien.

## 4. Un contrôle par DÉPLACEMENT plutôt que par ablation — **NON TROUVÉ**

Deux recherches distinctes, aucune antériorité trouvée pour un contrôle qui *relocalise* un composant
au lieu de le supprimer, dans ce domaine.

**Je n'en conclus pas que c'est nouveau.** Une absence de résultat dans deux recherches web n'est pas
une preuve de nouveauté : le connecteur arXiv n'était pas disponible, je n'ai pas interrogé les
bases bibliographiques, et l'idée est assez simple pour exister sous un autre nom (« translocation »,
« relocation control », « transplantation »). À reprendre avec un vrai outil bibliographique avant
toute revendication de nouveauté dans un article.

---

## Ce que le balayage change à la campagne

**Rien.** C'est délibéré et c'est la règle.

Ce qu'il change, c'est ce que l'adjudication finale devra discuter :

1. l'hypothèse de connexité du modèle A est contestée par la littérature de 2026 — l'instrument
   post-hoc `tbrt02_connectivity_posthoc.py` enregistre déjà de quoi la tester ;
2. le modèle C converge avec une méthode publiée indépendamment, ce qui est un appui ;
3. la division de tache par appauvrissement du cœur est l'explication alternative la plus sérieuse
   et elle n'est pas écartée ;
4. le contrôle par déplacement n'a pas d'antériorité connue, sans que cela vaille preuve.

```
REPRODUCTION_STATUS           = NOT_TESTED
H3_STATUS                     = NOT_TESTED
AUTONOMOUS_COHESION_STATUS    = NOT_ESTABLISHED
X_LAWSPEC_BASELINE            = UNCHANGED
COMPANION_PAPER_V1_1_STATUS   = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED
```
