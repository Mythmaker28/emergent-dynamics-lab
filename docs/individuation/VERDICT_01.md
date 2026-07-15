# VERDICT_01 — LOCAL-CAUSAL-INDIVIDUATION-00 (independent re-audit)

**VERDICT EN UNE LIGNE**
À l'arrêt, l'individuation **de stockage et de lecture** de l'histoire locale propre est **établie et robuste** ; mais l'individuation **causale/comportementale** n'est **pas** démontrée (jamais décodée), le maintien à travers le turnover profond est **indéterminé pour la dose** (significatif mais non certifié) et **négatif pour l'ordre** — donc **NE PAS** escalader vers ACTIVE-RECONSTRUCTION : **RÉPLIQUER/RÉPARER** d'abord.

**CE QUI EST ÉTABLI**
- K1 — stockage local individué : matrice d'influence diagonale en **valeur absolue** (|diag|≈0.180 ≈ 11× la mémoire de base ; |off|≈1.8×10⁻⁵ ; DD≈9018 robuste jusqu'à ε=10⁻⁶).
- Lecture spécifique de l'histoire propre au repos depuis la mémoire : ordre R²=0.654, dose R²=0.450 ; ≫ voisin (−0.31) ; ≫ baselines taille/position/taille+position (−0.17/−0.17/−0.22) ; bat le null intra-monde (p=2×10⁻⁴ et 7×10⁻³) ; stable au jackknife inter-mondes.

**CE QUI EST QUALIFIÉ (SUPPORTED WITH QUALIFICATION)**
- Ce décodage mémoire est une preuve *vers* l'expression causale, mais reste un **readout de stockage**, pas une expression comportementale ; le seul signal comportemental est un **ratio** DD(Δuptake)≈1629 dont l'effet diagonal absolu (2.7×10⁻⁴) n'est pas converti en décodage et non vérifié en substantialité.

**CE QUI RESTE INDÉTERMINÉ (NOT ESTABLISHED / INDETERMINATE)**
- K2 expression causale comportementale : **jamais testée comme préinscrite** (aucun décodage comportemental > 0.50).
- K3 maintien de la **dose** au turnover profond : R²=0.368, IC [0.14, 0.72] — significatif vs null (p=1.2×10⁻³) mais **< 0.50** non certifié ; **>0.50 n'est ni prouvé ni réfuté**.
- K5 indépendance au tracker : **non exécutée**.

**CE QUI EST FALSIFIÉ**
- Le null fort « des gouttelettes coexistantes ne peuvent pas être individuées localement du tout » : **rejeté** au repos.
- Aucune revendication porteuse n'est falsifiée. Le maintien profond n'est **pas** falsifié (IC larges).

**RÉSULTAT NÉGATIF**
- Maintien de la coordonnée **ordre** au turnover profond : R²=−0.659, p=0.92 vs null → **absence de signal** (l'individuation d'ordre ne survit pas au turnover).

**ALTERNATIVES ENCORE PLAUSIBLES**
- La dose pourrait dépasser 0.50 au turnover (n=9 sous-puissant) — testable par la confirmation 52xxx.
- Le « maintien » de la dose pourrait être une **copie passive lente** plutôt qu'une reconstruction active — indiscernable sans le contrôle canal-inerte + ablation lecture.
- L'expression comportementale pourrait être réelle mais faible — testable par un décodage Δuptake dédié.

**RÉSULTATS PAR SEED (held-out LOGO, 3 points/fold → bruités ; le jackknife inter-mondes est la mesure de stabilité)**

| seed | min dist | DD_mem | rest ordre (held) | rest dose (held) | deep dose (held) |
|---|---|---|---|---|---|
| 51002 | 26.8 | 2188 | −0.87 | +0.31 | +0.36 |
| 51003 | 29.2 | 2028 | +0.56 | −0.12 | +0.49 |
| 51004 | 31.6 | 29315 | +0.57 | +0.63 | +0.19 |
| 51005 | 24.8 | 30191 | +0.82 | −0.02 | −0.58 |
| 51007 | 25.5 | 31964 | +0.70 | +0.81 | +0.60 |
| 51009 | 25.1 | 32395 | +0.84 | +0.69 | +0.87 |
| 51010 | 25.3 | 8508 | −0.24 | +0.58 | +0.57 |
| 51011 | 24.6 | 5011 | +0.57 | −0.03 | +0.59 |
| 51012 | 26.4 | 9018 | +0.94 | +0.60 | +0.44 |
| **POOLED** | — | **9018 (med)** | **+0.654** | **+0.450** | **+0.368** |

IC (world-bootstrap, n=3000): rest ordre [0.517, 0.856] ; rest dose [0.380, 0.752] ; deep dose [0.140, 0.722] ; deep ordre [−0.867, 0.528]. Jackknife (leave-1-world) : rest ordre 0.556–0.689 ; rest dose 0.390–0.495 ; deep dose 0.271–0.430.

**CONTRÔLES PASS/FAIL**
- PASS : K1 stockage ; K4 non-trivialité ; contrefactuel apparié (baseline C_ij) ; détection+tracking longitudinal (3/3 vivants à M=0.21).
- PARTIAL : signaux permutés (fait en analyse via null intra-monde + voisin, pas re-simulé) ; baselines corps/environnement (taille/position seulement).
- PENDING/FAIL-TO-RUN : K5 tracker-indépendance ; histoire globale commune ; impulsions factices ; canal mémoire inerte ; ablation lecture ; confirmation 52xxx.

**DÉCISION : REPLICATE / REPAIR**  *(pas STOP ; pas DESIGN EXP 2)*
Réparer le gate K2 (définir un décodage **comportemental**, figer la règle de coordonnée), committer `exp1_reaudit.py` (comble le gap null+deep), exécuter les contrôles manquants + K5, puis lancer **52001–52012 une seule fois** sous le gate réparé **gelé avant** toute donnée 52xxx. DESIGN EXP 2 reste **non autorisé** tant que l'expression causale au repos n'est pas établie et que la confirmation n'a pas répliqué le repos et tranché la dose profonde.

**TON POINT DE VUE INDÉPENDANT**
Le travail précédent est solide sur le fond du repos (et, à son crédit, reproductible — contrairement à l'incident V3), mais il **sur-vend** trois choses : le mot « causal », le PASS de K2 (bascule de coordonnée post-hoc ; le code committé imprime `CHECK`), et le « non maintenu » du turnover (la dose est significativement positive). Escalader vers une nouvelle architecture pour « réparer » le turnover avant d'avoir (a) démontré l'expression causale au repos et (b) répliqué en 52xxx serait exactement le biais de confirmation que la mission proscrit. La meilleure prochaine décision est la réplication scellée sous gate réparé, pas la conception d'Expérience 2.

**PROVENANCE**
- Branche : `exp/local-causal-individuation-00` ; tip `6806f1f` ; Phase 0 `3def3df` (ancêtre) ; V4 `23b53ae` (ancêtre).
- Hashes : FREEZE_SEAL — 4 hashes de documents scellés **OK** ; `combined_seal_sha256` non reproductible (non porteur). Working tree == blobs scellés (16/16 OK).
- Seeds : DEV 50001–50010 ; PROSPECTIF 51001–51012 (9 retenus : 51002/3/4/5/7/9/10/11/12 ; exclus 51001/51006/51008) ; CONFIRMATION 52001–52012 (non exécutés).
- Fichiers produits : `docs/individuation/INDEPENDENT_JUDGMENT_01.md`, `STATISTICAL_REAUDIT_01.md`, `GATE_CERTIFICATE_01.json`, `VERDICT_01.md`, `CONFIRMATION_PREREGISTRATION_ADDENDUM_01.md`, `REPRODUCTION_COMMANDS.md`, `figure_individuation_audit.png`, `reaudit_summary.json` ; script `experiments/individuation/exp1_reaudit.py`.
- **main / V4 / release : INTACTS.** Rien poussé, tagué, publié ni soumis. h2-sur-C1c non rouvert. Aucune revendication d'identité/vie/agence.
