# ROUTE_E_DYNAMIC_SOURCE_CAPTURE_DEV_04 — rapport

**2026-08-08** · parent `5869283d6662f8b4f983c9f6f33243754be72cd9` · 18 blocs t0 uniques ·
144 trajectoires logiques · 162 appels moteur · horizon 2048 · 0 échec technique ·
0 raffinement · 0 fichier de production modifié · **protocole scellé AVANT le premier appel
moteur de la mission** (`48888a9fb6879858a4e0931fe80865daede87004538d7f24e083bf8b156b0491`,
garde exécutable dans `dsc_harness.preseal_guard`).

---

## 1. Disposition du parent, et une correction

L'arithmétique du parent est vérifiée sur les lignes authentiques : le plancher de résidu **est**
le produit masse × composition, à 4,1·10⁻³ près (L=24) et 8,4·10⁻⁴ près (L=32). Donc

```
ABLATION_ONLY = PERSISTENCE_UNDER_EROSION      ABLATION_ONLY ≠ MATERIAL_RENEWAL
```

**Correction au parent.** La colonne « composition » de `AB_REPORT.md` était
`médiane(résidu) / médiane(masse)`, et non la médiane du rapport. Les deux ne sont pas égales.
La composition correcte par trajectoire à la dose 2,00 vaut **0,8626 (L=24)** et **0,9010 (L=32)**,
non 0,853 et 0,900. Le sens ne change pas — il se renforce : la composition est encore **plus
plate** que ce que j'avais rapporté (−0,010 au lieu de −0,019 à L=24).

**Et une rétractation.** J'avais écrit que « l'afflux est bloqué par le crédit d'ingression fondé
sur l'adjacence ». C'était une hypothèse présentée comme un fait. Elle est maintenant testée.

## 2. Audit mécanique du filtre source — `P2`, et rien d'autre

Rejouées verbatim, 36 trajectoires parentes de `REDESIGN_02` avec la boucle source instrumentée
(fichier `source_filter_audit.json`). Prédicat responsable, isolé :

```python
if any(n in track for n in nbrs(s, L)): continue      # od_ops.do_event, ligne 30 — P2
```

| halo | livré par le filtre legacy | si P1 retiré | si **P2** retiré | headroom géométrique |
|---|---|---|---|---|
| `gd = 1` | **0,98 / 208,2  (0,5 %)** | 0,98 | **208,2 (100 %)** | 22 312 |
| `gd = 2` | 171,5 / 208,2 (82,4 %) | 174,4 | **208,2 (100 %)** | 28 208 |

Le masque a **107× à 135× plus de place physique** que la dose n'en demande : il n'y a ni
saturation géométrique ni limite de capacité matérielle. `P3` ne retient rien. `P1` retient 1,7 %.
**`P2` retient tout le reste, et le retirer livre exactement 100 % du quota aux deux distances.**

**Le relâchement le plus petit qui reste sûr — `P2'`.** Un site adjacent à la piste *peut*
recevoir de la matière, mais plafonnée pour que sa valeur post-injection reste **strictement
sous le seuil** (0,45). Le site demeure vide au sens du détecteur, l'opérateur ne crée jamais de
pont sur-seuil, et l'intervalle vide survit à l'injection. Les sites non adjacents gardent la
capacité legacy. `P2'` livre **208,2, soit autant que supprimer `P2` entièrement** : la sûreté ne
coûte rien. L'ancien filtre est conservé, versionné, et exécuté par le bras `D1_LEGACY_Q005`.

```
SOURCE_FILTER_CAUSE = P2_TRACK_ADJACENCY_PREDICATE
SAFE_FILTER_REDESIGN = AVAILABLE   ·   DIRECT_INSERTION_PREVENTED = true
```

Les 17 fixtures obligatoires passent **17/17**, sans aucun appel au moteur scientifique. Deux
d'entre elles (3 et 12) ont d'abord **échoué** et ont attrapé un vrai défaut : l'opérateur
d'interface directe déposait de la matière dans la piste, et la comptabilité la relisait comme
capture dynamique. Corrigé avant le scellement en créditant le champ absorbant à l'injection.

## 3. Ce que la mission a mesuré

Huit bras appariés sur le même microétat t256 (hash + `array_equal` vérifiés avant le premier
pas), 9 blocs frais par taille, graines 980000-980108, jamais réutilisées. `T256_VALID = 9/9` aux
deux tailles. **144/144 survivent à 2048**, y compris le SHAM.
Conservation : erreur algébrique maximale **6,3·10⁻¹⁵**, erreur système maximale **1,7·10⁻¹³**
(tolérance 1,7·10⁻¹⁰). Aucune insertion directe hors du bras de contrôle.

### (a) Le filtre était bien le verrou — et il cède

| halo `gd=1`, dose 0,05 × M₂₅₆ | L=24 | L=32 |
|---|---|---|
| filtre `P2` (legacy), livré sur 9 blocs | **0,62** | **0,00** |
| filtre `P2'`, livré sur 9 blocs | **48,75** | **68,30** |
| blocs améliorés / dégradés | **9 / 0** | **9 / 0** |

C'est le résultat le plus net de la mission : un prédicat, identifié par audit, remplacé par sa
version sûre, fait passer la livraison de zéro à la totalité, dans **18 blocs sur 18**.

### (b) Mais la source sature, et la porte reste hors d'atteinte

| dose planifiée × M₂₅₆ | 0,05 | 0,20 | 0,50 | 1,00 | facteur |
|---|---|---|---|---|---|
| livré, L=24 | 0,050 | 0,097 | 0,105 | **0,115** | dose ×20 → **×2,3** |
| capturé (transport), L=24 | 0,017 | 0,034 | 0,039 | **0,044** | ×2,6 |
| fraction fraîche @2048, L=24 | 0,022 | 0,048 | 0,055 | **0,062** | ×2,8 |
| livré, L=32 | 0,050 | 0,076 | 0,082 | **0,087** | dose ×20 → **×1,7** |
| fraction fraîche @2048, L=32 | 0,022 | 0,036 | 0,043 | **0,049** | ×2,2 |

Multiplier la dose par 20 multiplie la matière étrangère retenue par moins de 3. La courbe
s'aplatit. **Plafond observé : ≈ 6 % de matière fraîche.** La porte gelée de Route E demande
**80 %**. On est court d'un facteur **13**, et la pente va dans le mauvais sens.

L'efficacité de capture, elle, est remarquablement stable : **0,34 → 0,38** (L=24) et
**0,34 → 0,40** (L=32). Un tiers de tout ce qui est injecté au halo finit capturé, quelle que
soit la dose. Ce n'est donc pas l'assimilation qui échoue — c'est la quantité que le halo accepte
de porter.

### (c) Deux faits mécanistiques que la décomposition rend visibles

**La capture est majoritairement de l'englobement, pas du transport.** À dose 1,00, le transport
vaut 0,044 × M₂₅₆ et l'englobement 0,079 × M₂₅₆ : le plus gros de la matière fraîche entre dans
la piste **parce que la frontière avance sur elle**, pas parce qu'elle est transportée vers
l'intérieur. Le protocole proposé ne distinguait pas les deux ; seul le transport alimente le
point d'aboutissement primaire.

**À dose élevée, l'injection fabrique des satellites qui fusionnent.**

| fusion (`capture_by_merger` > 0) | dose 0,05 | 0,20 | 0,50 | 1,00 |
|---|---|---|---|---|
| L=24 | 0/9 | **9/9** | 7/9 | **9/9** |
| L=32 | 4/9 | 5/9 | 8/9 | 6/9 |

C'est exactement le confondant que `NONMERGING_CONFIRM_02` a coûté des mois à éliminer.
Il est ici **exclu du signal**, et il est la raison d'échec dominante du bras primaire.

### (d) Le contrôle positif, et la vraie nouvelle

À dose planifiée identique (1,00 × M₂₅₆), en court-circuitant complètement le transport :

| | halo `gd=2` | interface directe | rapport |
|---|---|---|---|
| livré / M₂₅₆, L=24 | 0,115 | **0,284** | ×2,5 |
| fraction fraîche @2048, L=24 | 0,062 | **0,260** | **×4,2** |
| fraction fraîche @2048, L=32 | 0,049 | **0,221** | **×4,5** |
| résidu incumbent @2048, L=24 | 0,779 | **0,606** (SHAM : 0,865) | — |
| masse / M₂₅₆, L=24 | 0,980 | **0,997** | — |
| survie 2048 | 9/9 | **9/9** | — |

**Le disque supporte 26 % de matière étrangère, à masse constante, et reste le même composant
suivi jusqu'à 2048, dans 18 cas sur 18.** Ce n'est pas de la capture dynamique — c'est de
l'insertion par l'opérateur, et le point d'aboutissement le rejette pour cette raison exacte.
Mais cela répond à une question distincte et réelle : *la tolérance au remplacement n'est pas le
verrou.* Et 0,284 n'est pas un plafond de tolérance, c'est le plafond du **puits** sous le
calendrier gelé — la limite n'a pas été atteinte.

## 4. Décision

```
DECISION = HALO_TRANSPORT_LIMITED
```

Contact médian au bras primaire : 0,044 × M₂₅₆ (L=24) et **0,031 × M₂₅₆ (L=32)**, sous le plancher
de porte de 0,04. La livraison passe la porte, le contact non. `ROUTE_E_GATE` : **1/144** au total
(une trajectoire, L=24, dose 0,50, graine 980002), très loin des 7/9 par taille exigés.

Mais la disposition seule sous-décrit les données. Le fait dominant est une **atténuation à chaque
étage avec une source qui sature** : planifié 1,00 → livré 0,115 → contact 0,044 → capture 0,044 →
fraction retenue 0,062. Et surtout : **même en supprimant entièrement le problème de transport, on
plafonne à 0,26.** Le verrou n'est donc ni le filtre (réparé), ni le calendrier, ni la dose : c'est
le débit de matière qui peut franchir la frontière du composant par unité de temps pendant qu'il
reste le même composant.

## 5. Ce que cela n'établit pas

Rien de : remplacement à 80 %, turnover autonome, auto-maintien, `INDIVIDUATION`, `IDENTITY`,
`LIFE`, généralisation au-delà de `LAW_16`. Statut inchangé : `PARENT_INFORMED_PROSPECTIVE_DEV`.
Ne réfute ni Route E ni `NONMERGING_CONFIRM_02`.

Limitations déclarées : une seule loi ; deux tailles ; une seule morphologie et un seul niveau
d'occupation ; `PULSE_DEPENDENT_CAPTURE_DEV` est **indisponible** dans cette mission (les bras
d'impulsion ont été remplacés par l'échelle de dose, parce que l'audit montre que c'est la
livraison, non le calendrier, qui lie — un calendrier ne déplace pas un plafond de livraison) ;
les champs de provenance par événement sont **agrégés** en un champ `FRESH` unique ;
`INCORPORATION_16` / `_128` utilisent un minimum glissant, donc **sous-estiment** ;
`DIRECT_INTERFACE` mesure une tolérance minimale, pas un maximum.

**Correction d'analyse déclarée.** Deux bugs de véracité Python (`x or défaut` lisant un `0.0`
exact comme absent) rendaient l'erreur de conservation nulle comme un échec de porte. Corrigés
après le run, dans le sens de *moins* d'échecs faux. Le nombre de points d'aboutissement atteints
est **inchangé** (1/144 avant comme après) et la décision ne bouge pas.

## 6. Ce que je retiens

L'expérience qui vaut le coût maintenant n'est plus au halo : elle est sur la voie directe, dont
le plafond n'a pas été atteint. Pousser le remplacement imposé jusqu'à ce que **soit** le résidu
passe sous 0,20, **soit** le composant casse, donnerait une réponse binaire à une question que ce
projet pose depuis le début : *le régime de résidu exigé par Route E existe-t-il dans ce substrat,
par un échange imposé quelconque ?* Aujourd'hui on sait qu'il ne s'atteint pas par la frontière ;
on ne sait pas encore s'il s'atteint du tout.
