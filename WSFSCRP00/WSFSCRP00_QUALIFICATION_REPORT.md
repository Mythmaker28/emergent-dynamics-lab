# `WSFSCRP00` — rapport de qualification

36 démarrages moteur sur un plafond de qualification de 48. TRAIN uniquement.

## Génération et allocation

| | |
|---|---|
| candidats générés | **12** sur une file de 16 |
| admissibles (exactement deux composantes éligibles) | **12 / 12** |
| rejets | 0 |
| fondateurs utilisés | 12 (plafond 12) |
| grappes d'ascendance TRAIN | **6** (minimum 6) |
| grappes d'ascendance LOCKED | **6** (minimum 6) |
| classes de géométrie par rôle | **2** (`FAR` et `NEAR`) dans chaque rôle — cible atteinte |
| accord lecteur production / référence | **12 / 12** sur la paire non ordonnée |
| `B_b > 0` | 12 / 12 |

TRAIN : `64006 FAR, 64002 FAR, 64010 FAR, 64009 NEAR, 64005 NEAR, 64001 NEAR`
LOCKED : `64000 FAR, 64004 FAR, 64008 FAR, 64007 NEAR, 64003 NEAR, 64011 NEAR`

## Q0 — oracle et exactitude du support : **PASS**

Jumeau sham 1 = jumeau sham 2 sur **tout l'horizon** : **6/6** fondateurs TRAIN, courbes des deux
canaux et empreinte d'état final identiques. Rechargement = octets sources 6/6. Masques immuables
6/6. Zéro structurel `r(h=0) = (0,0)` 12/12. Ensemble touché mesuré = `['Mf']` 12/12, `rho`
intacte 12/12. Domaine post-état 12/12.

## Q1 — signal matériel à deux canaux : **PASS, 12 cellules sentinelles sur 12**

`ETA_bu = max(ETA_ORACLE, 0,01·G_bu, ETA_SCI_b)`, où `ETA_SCI_b` est l'effet normalisé d'une
variation de 1 % de `ρ` sur un site représentatif du support de base — dérivé de l'échelle
**pré-intervention** seule.

| fondateur | S1 conservatrice | S2 non conservatrice | `ETA_bu` | marge min |
|---|---|---|---|---|
| 64006 FAR | 6,207e-03 | 9,567e-03 | 1,587e-03 | 3,91× |
| 64002 FAR | 5,731e-03 | 9,463e-03 | 1,555e-03 | 3,69× |
| 64010 FAR | 6,191e-03 | 9,624e-03 | 1,621e-03 | 3,82× |
| 64009 NEAR | 4,750e-03 | 9,642e-03 | 1,171e-03 | 4,06× |
| 64005 NEAR | 4,786e-03 | 9,676e-03 | 1,171e-03 | 4,09× |
| 64001 NEAR | 4,923e-03 | 9,700e-03 | 1,251e-03 | 3,94× |

**12/12**, marges de **3,69× à 8,26×** au-dessus de la borne. Le résultat `16/16` du parent n'a
joué aucun rôle : ces cellules sont des fondateurs frais.

## Q2 — rang de la réponse : **ÉCHEC**

Matrice 12 lignes (fondateur × superfamille) × 20 colonnes (`√w·δ_A` concaténé à `√w·δ_B`),
centrée par la moyenne TRAIN, sans autre projection de nuisance.

```
σ₂ / σ₁            = 0,1196     porte > 0,10      -> PASSE
σ₂² / Σ_j σ_j²     = 0,0140     porte >= 0,05     -> ÉCHOUE
```

Les deux critères étaient requis ; **le second échoue**. Après retrait de la courbe moyenne
TRAIN, le résidu vit à ~98,6 % dans **une seule** direction. Le second mode existe, mais il ne
porte que 1,4 % de l'énergie centrée.

```
WSFSCRP00_DISPOSITION = RANK_ONE_FIXED_SUPPORT_RESPONSE
```

La courbe n'est **pas** remplacée par son amplitude, et aucun autre point de mesure n'est essayé.

## Q3 et Q4 — diagnostics **secondaires** uniquement

L'ordre de précédence fixe la disposition à l'étape 4. Ce qui suit est enregistré parce que c'est
informatif et sans coût, **non** parce que cela pourrait changer le verdict.

**Q3, code trivial — aurait passé.** Validation groupée par exclusion d'une grappe d'ascendance,
perte primaire exacte, six plis :

| pli | `L_MEAN` | `L_NUIS` | fraction inexpliquée |
|---|---|---|---|
| 64001 | 8,810e-03 | 2,891e-03 | 0,328 |
| 64002 | 8,634e-03 | 2,172e-03 | 0,252 |
| 64005 | 8,849e-03 | 2,510e-03 | 0,284 |
| 64006 | 8,826e-03 | 2,011e-03 | 0,228 |
| 64009 | 8,776e-03 | 2,516e-03 | 0,287 |
| 64010 | 8,834e-03 | 1,930e-03 | 0,218 |

médiane **0,268** (≥ 0,25) · minimum **0,218** (≥ 0,10).

**Q4, apprenabilité dépendante de l'état — aurait passé.** Ridge multi-sorties depuis `Z_Q4`
standardisé, `λ` choisi en validation groupée imbriquée : `L_RIDGE / L_NUIS` médiane **0,393**
(≤ 0,90), inférieure à 1 dans **les six** plis, et positive dans **les deux** superfamilles TRAIN.

Autrement dit : la réponse à support figé est **matérielle, non triviale et apprenable depuis
l'état** — mais sa **forme**, une fois la moyenne retirée, est presque unidimensionnelle. C'est
exactement la structure que la porte Q2 existe pour écarter avant un concours de géométrie
fonctionnelle.
