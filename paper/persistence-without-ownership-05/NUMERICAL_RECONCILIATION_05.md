# Numerical reconciliation 05

All values below were recomputed from exact committed bytes by `scripts/recompute_and_figures_05.py`. No engine module was imported and no seed was initialized. The machine-readable companion is `NUMERICAL_RECONCILIATION_05.csv`.

## Headline reconciliation

| Family | Quantity | Recomputed value | Unit/status |
|---|---:|---:|---|
| V4.1 | Deep h1 grouped R² | 0.69469387421633 | 3 original worlds; corrected point estimate, no certification |
| V4.1 | Deep h2 grouped R² | -1.1183408783037767 | 3 original worlds; not established |
| V4.1 | Deep mean M | 0.1902034032455061 | 36 rows; 34/36 ≤0.25 |
| CONFIRM-02 | Own feeding mean | 0.2236416257421648 | 23 valid original worlds; prospective |
| 03G | Own-scope skill | 0.39544573811628886 | 21 valid original worlds; `G_OWN_PERM=true` |
| 03G | Causal own contrast | 0.1648449906580111 | 21 valid original worlds; `G_CAUSAL=true` |
| 03G | L over E | 0.20716772718764476 | t95 lower -0.0220630992; fails |
| 03G | L over B | 0.14460985825989336 | t95 lower -0.0226050984; fails |
| 03G | Decision | Outcome B | causal feeding effect without ownership |
| 03M | Numeric comparison | max absolute difference 0 | 9,283 numeric of 9,357 terminal leaves |

## Exact 03G intervals

| Quantity | Lower | Mean | Upper | Frozen disposition |
|---|---:|---:|---:|---|
| Own-scope skill | 0.1753227144 | 0.3954457381 | 0.6155687618 | own information passes; p=0.000999 |
| Causal own | 0.1443216429 | 0.1648449907 | 0.1853683384 | positive |
| Own minus sham | 0.1443216481 | 0.1648449958 | 0.1853683436 | positive |
| Own minus neighbour | 0.1443216714 | 0.1648450303 | 0.1853683892 | positive |
| Fixed original mask | 0.1246094899 | 0.1421574828 | 0.1597054758 | positive |
| λ-plus-only ablation | 0.0132184414 | 0.0181412477 | 0.0230640539 | collapse ratio upper/own=0.1399136<0.5 |
| L over N | 0.2363236263 | 0.5304158891 | 0.8245081520 | passes |
| L over E | -0.0220630992 | 0.2071677272 | 0.4363985536 | fails |
| L over G-minus-target | 0.0796802251 | 0.4894835471 | 0.8992868691 | passes |
| L over B | -0.0226050984 | 0.1446098583 | 0.3118248150 | fails |

## Exact source binding checks

- V4.1 raw: commit `847d51ef78d0d55d30f05df275d97aa4af0c558f`, blob `664ae553c95387f177d3e218797b161ba71c681b`, SHA-256 `dbb5a2bb3017dbe60d188109319a5939d1601b1bd0b5295bfb804c1253bffd57`.
- CONFIRM-02 raw: commit `830c2d006f5278295e965887f8ccedee34d47e67`, blob `01fb1193961aeda10689adda714cea290f29628d`, SHA-256 `aedb0acf90affe3b7b872852191a67ab0ec849e2892b2669cffc2d63e965b1f0`.
- 03G raw manifest: commit `9cb996bb891f9a618e593f2f5c302f30210458de`, blob `3740c4e1d3d8b338d8a744b672093b58a2666ab5`, SHA-256 `ce8d2cb0b6158965acaeef3553f44c7f9bf0ef9b9567c858ff5cbb27f903a328`.
- 03M independent result: commit `a8d6446fade6dbeb984e269fab27ddd5ebf75286`, blob `10582705734799e08515c468456b97cd3b84fae9`, SHA-256 `d8e4d500b22e7720a21af2533716e6e87abf59c1ab13e7831ebdb26c472ea3af`.

The full 17-object binding map is `SOURCE_BINDINGS_05.json`; the family-level raw registry is `RAW_DATA_REGISTRY_05.json`.
