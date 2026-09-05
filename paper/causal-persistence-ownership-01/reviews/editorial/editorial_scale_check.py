"""Independent descriptive context for the primary uptake effect; no simulator."""
from pathlib import Path
import hashlib
import json
import statistics

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
rows = []
for path in sorted((ROOT / 'data/results/LCI-TURNOVER-PROSPECTIVE-03G/raw').glob('seed_*.json')):
    raw = json.loads(path.read_text(encoding='utf-8'))
    if not raw['feasibility']['valid']:
        continue
    b = raw['scientific']['causal_intervention_battery']['deep']
    intact = b['intact']['tracked']
    erased = [b['erase'][i]['tracked'][i] for i in range(3)]
    full = [b['ablate_full']['tracked'][i] - b['erase_ablate_full'][i]['tracked'][i] for i in range(3)]
    own = [a - e for a, e in zip(intact, erased)]
    rows.append({'seed': raw['seed'], 'intact_mean': statistics.mean(intact),
                 'own_mean': statistics.mean(own),
                 'mean_target_relative_reduction': statistics.mean([o / a for o, a in zip(own, intact)]),
                 'full_ablation_own_mean': statistics.mean(full),
                 'full_ablation_max_abs_target_contrast': max(map(abs, full))})
assert len(rows) == 21
out = {'definition': 'Descriptive effect-size context on the same 21 valid worlds; no new gate or interval.',
       'input_text_hashes': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                            for p in ['MANUSCRIPT.md', 'SUPPLEMENT.md', 'results/SUMMARY.json']},
       'world_count': len(rows),
       'mean_intact_uptake': statistics.mean([r['intact_mean'] for r in rows]),
       'mean_own_effect': statistics.mean([r['own_mean'] for r in rows]),
       'ratio_of_world_means': statistics.mean([r['own_mean'] for r in rows]) / statistics.mean([r['intact_mean'] for r in rows]),
       'mean_of_world_mean_target_ratios': statistics.mean([r['mean_target_relative_reduction'] for r in rows]),
       'max_abs_full_ablation_target_effect': max(r['full_ablation_max_abs_target_contrast'] for r in rows),
       'worlds': rows}
(OUT / 'EDITORIAL_SCALE_CHECK.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({k: v for k, v in out.items() if k != 'worlds'}, indent=2))
