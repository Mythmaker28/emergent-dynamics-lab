# RPP97 — comparaison de mécanisme. **CE N'EST PAS UN PRÉ-ENREGISTREMENT.**

## THIS_IS_NOT_A_PREREGISTRATION__THE_FIRST_NUMBERS_WERE_ALREADY_SEEN

Il faut le dire avant tout le reste, parce que c'est ce qui détermine ce que ce document peut
prétendre.

RPP97 a d'abord existé le 28 août 2026 à 06:25 UTC sous la forme d'un vrai pré-enregistrement,
écrit et commité (`ae9c9cb`) **avant** qu'un seul chiffre soit calculé, suivi d'un test de
capacité commité seul (`4978c12`) avant qu'une seule archive soit ouverte. La mesure a été lancée
à 06:38. Le vingt-troisième retour arrière du conteneur a tout emporté : le pré-enregistrement,
le test, le code et la mesure. Ils vivaient uniquement dans git, à l'intérieur du conteneur,
parce que la liste de chemins du packer du Projet nommait `TBRT02` et rien d'autre. C'est une
faute d'opérateur, pas un aléa : le gel de TBRT02 énonçait déjà qu'un commit n'est pas une
sauvegarde ici.

**Ce qui avait été vu avant la perte**, et qui ne peut plus être désappris :

- **S1 revenait indéfini** sur les premières archives — les composantes comptaient moins de
  quatre cellules dans les fenêtres, donc il n'y avait pas de cœur à distinguer d'une périphérie ;
- **S2 ressortait positif**, c'est-à-dire **de signe contraire à la prédiction** du mécanisme.

Reconstruire les mêmes statistiques aujourd'hui ne restitue donc pas leur statut. Une statistique
n'est pré-enregistrée que si elle est fixée avant les données ; celles-ci sont désormais fixées
**après** un premier regard. RPP97 est **post-hoc**. Elle peut décrire ce que portent les
archives. Elle ne peut adjuger ni soutenir ni réfuter le mécanisme.

**Ce qu'il faudrait pour un vrai test :** un pré-enregistrement neuf, écrit avant tout chiffre,
sur des archives que ces yeux n'ont pas encore regardées. C'est exactement le legs de TBRT02/C5,
et il s'applique d'abord à moi.

---

## 1. Le mécanisme comparé

La réplication de taches par **épuisement du cœur** décrite pour les systèmes de
réaction-diffusion (Reynolds, Ponce-Dawson & Pearson, 1997, sur le modèle de Gray-Scott) : le
substrat est consommé le plus vite au centre de la tache, là où l'autocatalyseur est le plus
dense ; le centre s'appauvrit, la croissance ne se poursuit qu'à la périphérie, la tache s'allonge
et s'étrangle en deux.

**Aucun monde neuf n'est lancé.** Tout se lit sur les 123 archives TBRT02 déjà scellées et
revérifiées au sha256 après la restauration.

## 2. Traduction dans les variables de ce système

**X joue le rôle du substrat.** Ce n'est pas une analogie choisie : la naissance de Y est
autocatalytique et sa propension locale gelée vaut `kY · nX · nY` par cellule, archivée telle
quelle dans `c_cand`. Le mécanisme prédit donc un appauvrissement de X au cœur du corps avant la
séparation.

## 3. Les deux statistiques

Toutes deux ne lisent que des champs **gelés** déjà présents dans les archives.

**S1 — contraste cœur/périphérie INTRA-CORPS.** Pour une composante au pas t : le centroïde est
recalculé par l'expression gelée à partir de `(k_a0y, k_a0x, k_soy, k_sox)`, dans le même ordre,
donc bit-identique à la valeur en ligne. Chaque cellule reçoit sa distance euclidienne torique r
au centroïde ; partage à la médiane en `CŒUR = {r ≤ médiane}` et `PÉRIPHÉRIE = {r > médiane}`.

    S1(t) = moyenne(nX | PÉRIPHÉRIE) − moyenne(nX | CŒUR)

Prédiction : **S1 > 0**, croissant à l'approche de t_m. Composantes de moins de **4 cellules** :
S1 non défini, **exclues et comptées** — le décompte est un résultat, pas un détail de mise en
œuvre.

**S2 — appauvrissement du VOISINAGE par rapport à l'ambiant.** `k_xd` est la masse de X dans le
disque gelé (CORE_R = 5,0) centré sur le centroïde. Avec A l'aire du disque **lue depuis
`fmrt01_identity.disc_mask`, jamais supposée**, et L² = 1296 :

    S2(t) = (k_xd / A) − (nX_total / L²)

Prédiction : **S2 < 0**.

## 4. Le contrôle, sans lequel rien n'est mesuré

Un corps dense appauvrit X autour de lui **qu'il se divise ou non**. Trouver S1 > 0 ou S2 < 0 sur
les seules composantes qui se divisent ne prouverait donc rien du mécanisme : cela prouverait
qu'il y a un corps. D'où deux fenêtres :

- **FAR** `[t_m − 2000, t_m − 1000]` — loin de la division ;
- **PRE** `[t_m − 250, t_m − 1]` — juste avant.

Et les trois bras SHAM / SELECTIVE / DISPLACED, appariés par index. **Le mécanisme n'est soutenu
que si le contraste s'accentue de FAR à PRE**, pas s'il est seulement présent.

## 5. Ce qui compterait comme incompatible

S1 ≤ 0 de façon soutenue en fenêtre PRE ; ou S1 en PRE indistinguable de S1 en FAR ; ou S2 ≥ 0
en PRE ; ou le contraste maximal survenant **après** t_m plutôt qu'avant.

## 6. Test de capacité — obligatoire avant d'ouvrir une archive

S1 et S2 doivent pouvoir prendre **les deux signes**, et cela se vérifie plutôt que de se
supposer : cœur appauvri → S1 > 0 ; **cœur enrichi → S1 < 0** — c'est ce signe-là qui compte,
puisque c'est celui qui contredirait le mécanisme ; corps uniforme → S1 ≈ 0. Si le cas enrichi ne
produit pas un S1 négatif, la statistique est incapable d'exprimer l'observation réfutante et la
mesure ne se fait pas.

## 7. Ce que ces archives ne peuvent pas mesurer

`c_nX` n'existe que pour les cellules **occupées par Y**. Donc :

- S1 mesure l'appauvrissement **à l'intérieur du corps**, pas le gradient de substrat dans le
  milieu environnant ; la « périphérie » est celle du support de Y, pas la couronne extérieure ;
- S2 est la seule fenêtre sur le milieu, et elle est grossière : un total de disque, pas un profil ;
- **aucun profil radial hors du corps n'est reconstructible**, donc **aucune comparaison
  quantitative aux profils publiés de Gray-Scott ne sera tentée**.

Ce qui reste à portée : la présence, la direction et la **chronologie** du contraste par rapport
à la division — et seulement à titre descriptif, vu le §0.

## 8. Statuts inchangés

H3_STATUS = NOT_TESTED ; REPRODUCTION_STATUS = NOT_TESTED ; HEREDITY_STATUS = NOT_TESTED ;
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED ; X_LAWSPEC_BASELINE = UNCHANGED ;
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED ;
COMPANION_PAPER_V1_1_STATUS = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED ;
OMLDCT02_STATUS = INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED ;
CLEA01_STATUS = CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED ;
TBRT02_STATUS = CLOSED__RAW_COMPLETE__PRIMARY_ADJUDICATION_INCONCLUSIVE_BY_CONSTRUCTION.

Une ressemblance de mécanisme, si elle est décrite, sera une ressemblance de mécanisme — pas un
argument sur ce que ces objets sont.
