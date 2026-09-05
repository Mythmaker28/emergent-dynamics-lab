"""Post hoc statistical review from the existing 03G JSON records; no simulator import.

Reimplements LOWO linear ridge as a label-to-prediction matrix. Deletes whole worlds
and refits every fold to expose fit dependence. Neither these perturbations nor
jackknife intervals replace the frozen decision rule or constitute new data.
"""
from pathlib import Path
import collections
import hashlib
import json
import sys
import numpy as np
from scipy.stats import t, binomtest, beta

HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[1]
SCOPES = ('L', 'N', 'E', 'Gm', 'B')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def select_inputs():
    """Prefer standalone article inputs; only use the audit fallback if absent."""
    relative = Path('results/LCI-TURNOVER-PROSPECTIVE-03G')
    local = PAPER/'data'/relative
    if local.exists():
        manifest_path = PAPER/'INPUT_MANIFEST.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        names = set()
        for row in manifest['files']:
            path = Path(row['path'])
            assert not path.is_absolute() and '..' not in path.parts and ':' not in row['path']
            assert row['path'].casefold() not in names, row['path']
            names.add(row['path'].casefold())
            target = PAPER/path
            assert target.stat().st_size == row['bytes'], row['path']
            assert digest(target) == row['sha256'], row['path']
        required = [local/'raw_manifest_03g.json', *sorted((local/'raw').glob('seed_*.json'))]
        assert len(required) == 51
        assert all(p.relative_to(PAPER).as_posix().casefold() in names for p in required)
        return local, PAPER, {'mode': 'STANDALONE_PAPER_INPUTS', 'manifest': 'INPUT_MANIFEST.json',
                             'manifest_sha256': digest(manifest_path),
                             'manifest_entries_verified': len(manifest['files'])}
    root = HERE.parents[3]
    fallback = root/'audit/edl-flagship-01/candidate_b'/relative
    assert fallback.is_dir(), 'No standalone paper raw inputs or repository audit fallback found'
    return fallback, root, {'mode': 'REPOSITORY_AUDIT_FALLBACK',
                           'manifest': 'audit/edl-flagship-01/candidate_b/results/LCI-TURNOVER-PROSPECTIVE-03G/raw_manifest_03g.json'}

def t_summary(values):
    values = np.asarray(values, dtype=float)
    m = float(values.mean())
    h = float(t.ppf(.975, len(values)-1) * values.std(ddof=1) / np.sqrt(len(values)))
    return {'mean': m, 'lower': m-h, 'upper': m+h}

def operator(x, groups, ridge=1.):
    n = len(x)
    p = np.zeros((n, n))
    b = np.zeros((n, n))
    for world in np.unique(groups):
        test = np.flatnonzero(groups == world)
        train = np.flatnonzero(groups != world)
        mu, sd = x[train].mean(0), x[train].std(0)
        keep = sd > 1e-12
        a = (x[train][:, keep]-mu[keep])/sd[keep]
        z = (x[test][:, keep]-mu[keep])/sd[keep]
        aug = np.vstack([a, np.sqrt(ridge)*np.eye(a.shape[1])])
        rhs = np.vstack([np.eye(len(train))-np.ones((len(train), len(train)))/len(train),
                         np.zeros((a.shape[1], len(train)))])
        h = z @ np.linalg.lstsq(aug, rhs, rcond=None)[0]
        p[np.ix_(test, train)] = h + 1/len(train)
        b[np.ix_(test, train)] = 1/len(train)
    return p, b

def analyze(xmap, y, groups, ridge=1.):
    scale = np.empty(len(y))
    worlds = np.unique(groups)
    for world in worlds:
        scale[groups == world] = max(y[groups != world].var(), 1e-15)
    losses, skills, matrices = {}, {}, {}
    for scope, x in xmap.items():
        p, b = operator(x, groups, ridge)
        row_loss = (y-p@y)**2/scale
        row_base = (y-b@y)**2/scale
        losses[scope] = np.array([row_loss[groups == w].mean() for w in worlds])
        skills[scope] = np.array([(row_base-row_loss)[groups == w].mean() for w in worlds])
        matrices[scope] = p, b
    contrasts = {s: losses[s]-losses['L'] for s in SCOPES[1:]}
    return {'own_skill': skills['L'], **contrasts}, losses, matrices, scale

def causal(record):
    b = record['scientific']['causal_intervention_battery']['deep']
    a = np.array(b['intact']['tracked'])
    er = np.array([r['tracked'] for r in b['erase']])
    own = a-np.diag(er)
    neighbour = a-(er.sum(0)-np.diag(er))/2
    plus = np.array(b['ablate_plus']['tracked'])-np.diag([r['tracked'] for r in b['erase_ablate_plus']])
    fixed = np.array(b['intact']['fixed'])-np.diag([r['fixed'] for r in b['erase']])
    return {'own': float(own.mean()), 'own_minus_neighbour': float((own-neighbour).mean()),
            'own_minus_sham': float((np.array(b['sham']['tracked'])-np.diag(er)).mean()),
            'fixed': float(fixed.mean()), 'plus_ablation_residual': float(plus.mean()),
            'half_own_minus_residual': float((.5*own-plus).mean())}

def validate_prediction_matrices(xmap, y, groups, matrices):
    """Real-data crosscheck against direct normal equations, plus leakage invariants."""
    max_error = 0.
    for scope, x in xmap.items():
        p, b = matrices[scope]
        assert np.allclose(p.sum(1), 1., atol=1e-12, rtol=0)
        for world in np.unique(groups):
            held = groups == world
            train = ~held
            assert not np.any(p[np.ix_(held, held)])
            assert not np.any(b[np.ix_(held, held)])
            mu, sd = x[train].mean(0), x[train].std(0)
            keep = sd > 1e-12
            a = (x[train][:,keep]-mu[keep])/sd[keep]
            z = (x[held][:,keep]-mu[keep])/sd[keep]
            coef = np.linalg.solve(a.T@a+np.eye(a.shape[1]), a.T@(y[train]-y[train].mean()))
            direct = z@coef+y[train].mean()
            max_error = max(max_error, float(np.max(np.abs(direct-(p@y)[held]))))
    assert max_error < 1e-12, max_error
    return {'max_prediction_difference_matrix_vs_direct_solve': max_error,
            'held_world_coefficients_all_zero': True,
            'prediction_intercept_rows_sum_to_one': True,
            'scope_count': len(xmap), 'world_count': len(np.unique(groups))}

def main():
    raw, input_base, input_status = select_inputs()
    manifest = json.loads((raw/'raw_manifest_03g.json').read_text())
    records, hash_rows = [], []
    for entry in manifest['entries']:
        p = raw/entry['path']
        assert digest(p) == entry['sha256'], entry['path']
        record = json.loads(p.read_text())
        assert record['world_id'] == entry['seed']
        records.append(record)
        hash_rows.append({'path': p.relative_to(input_base).as_posix(), 'sha256': digest(p)})
    valid = [r for r in records if r['feasibility']['valid']]
    n = len(valid)
    assert n == 21 and len(records) == 50
    groups = np.repeat([r['world_id'] for r in valid], 3)
    y = np.array([d for r in valid for d in r['scientific']['histories']['own_dose']])
    xmap = {s: np.array([v for r in valid for v in r['scientific']['scopes']['values'][s]]) for s in SCOPES}
    scores, losses, matrices, scale = analyze(xmap, y, groups)
    validation = validate_prediction_matrices(xmap, y, groups, matrices)
    frozen = {s: t_summary(v) for s, v in scores.items()}
    # All alternative lambda values are reported, never selected or gated.
    ridge = {}
    for lam in (.1, 1., 10.):
        vals, _, _, _ = analyze(xmap, y, groups, lam)
        ridge[str(lam)] = {s: t_summary(v) for s, v in vals.items()}
    delete = []
    for world in np.unique(groups):
        keep = groups != world
        vals, _, _, _ = analyze({s: x[keep] for s, x in xmap.items()}, y[keep], groups[keep])
        delete.append({'omitted_world': int(world), 'frozen_style_summaries': {s: t_summary(v) for s,v in vals.items()}})
    jackknife = {}
    for s in scores:
        values = np.array([d['frozen_style_summaries'][s]['mean'] for d in delete])
        se = float(np.sqrt((n-1)/n * ((values-values.mean())**2).sum()))
        half = float(t.ppf(.975,n-1)*se)
        jackknife[s] = {'mean': frozen[s]['mean'], 'jackknife_se': se,
                        'diagnostic_lower': frozen[s]['mean']-half,
                        'diagnostic_upper': frozen[s]['mean']+half,
                        'deletion_mean_min': float(values.min()), 'deletion_mean_max': float(values.max()),
                        'deletion_frozen_lower_gt_zero_count': sum(d['frozen_style_summaries'][s]['lower']>0 for d in delete)}
    # Conditional permutation statistic, not claimed an exact randomized design test.
    rng = np.random.default_rng(20260715)
    permuted = np.empty((len(y), 1000))
    for rep in range(1000):
        for world in np.unique(groups):
            rows = np.flatnonzero(groups == world)
            permuted[rows, rep] = y[rows][rng.permutation(3)]
    p,b = matrices['L']
    for world in np.unique(groups):
        rows = np.flatnonzero(groups == world)
        assert np.all(np.sort(permuted[rows], axis=0) == np.sort(y[rows])[:,None])
        assert np.allclose(permuted[groups != world].var(axis=0), y[groups != world].var(), atol=1e-15, rtol=0)
    validation['all_permutations_preserve_world_label_multisets_and_train_variance'] = True
    null = (((permuted-b@permuted)**2-(permuted-p@permuted)**2)/scale[:,None]).mean(0)
    observed = frozen['own_skill']['mean']
    permutation = {'observed': observed, 'n_ge_observed': int((null>=observed).sum()),
                   'p_plus_one': float((1+(null>=observed).sum())/1001),
                   'null_p95': float(np.percentile(null,95)), 'reps': 1000, 'seed': 20260715}
    crows = [causal(r) for r in valid]
    cstats = {}
    for key in crows[0]:
        values = np.array([r[key] for r in crows])
        pos, neg, zero = int((values>0).sum()), int((values<0).sum()), int((values==0).sum())
        cstats[key] = {**t_summary(values), 'minimum': float(values.min()), 'maximum': float(values.max()),
                      'worlds_positive': pos, 'worlds_negative': neg, 'worlds_zero': zero,
                      'sign_test_two_sided': float(binomtest(pos, pos+neg, .5).pvalue),
                      'scope': 'conditional valid-world directional consistency; post hoc, median/sign target'}
    out = {'status': 'POST_HOC_EXISTING_DATA_SENSITIVITY_NOT_A_NEW_EXPERIMENT',
           'input_status': input_status,
           'input_raw_hashes_verified': hash_rows, 'raw_worlds': len(records), 'valid_worlds': n,
           'valid_worlds_interval_cp95': [float(beta.ppf(.025,n,51-n)), float(beta.ppf(.975,n+1,50-n))],
           'invalid_reasons': dict(collections.Counter(r['feasibility']['reason'] for r in records if not r['feasibility']['valid'])),
           'eligible_worlds': sum(r['feasibility']['eligible'] for r in records),
           'deep_reached_worlds': sum(r['feasibility']['deep_reached'] for r in records),
           'frozen_style_recalculation': frozen, 'independent_permutation': permutation,
           'ridge_sensitivity_all_values': ridge, 'delete_one_full_refit': delete,
           'jackknife_full_refit_diagnostic': jackknife,
           'jackknife_warning': 'Diagnostic first-order delete-world jackknife; coverage is not validated for this small-sample CV statistic. Do not relabel as a calibrated replacement confidence interval.',
           'causal_independent_world_checks': cstats,
           'analytic_validation': validation,
           'science_worlds_run': 0,
           'project_modules_imported': [s for s in sys.modules if s=='edlab' or s.startswith('edlab.')],
           'python': sys.version.split()[0], 'numpy': np.__version__}
    assert not out['project_modules_imported']
    (HERE/'STATISTICAL_SENSITIVITY.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:out[k] for k in ('raw_worlds','valid_worlds','invalid_reasons','independent_permutation','jackknife_full_refit_diagnostic','causal_independent_world_checks')},indent=2))

if __name__ == '__main__':
    main()
