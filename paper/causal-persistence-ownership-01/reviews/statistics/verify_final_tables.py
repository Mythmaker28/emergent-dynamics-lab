"""Independently compare article tables with existing raw observations and matrix fits."""
import csv
import json
import sys
from pathlib import Path
import numpy as np
from scipy.stats import binomtest
sys.dont_write_bytecode = True
import recompute_sensitivity as independent

HERE = Path(__file__).resolve().parent
PAPER = HERE.parents[1]

def rows(name):
    with (PAPER/'results'/name).open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))

def main():
    raw, _, source = independent.select_inputs()
    manifest = json.loads((raw/'raw_manifest_03g.json').read_text())
    records = []
    for row in manifest['entries']:
        p = raw/row['path']
        assert independent.digest(p) == row['sha256']
        records.append(json.loads(p.read_text()))
    valid = [r for r in records if r['feasibility']['valid']]
    groups = np.repeat([r['world_id'] for r in valid],3)
    y = np.array([d for r in valid for d in r['scientific']['histories']['own_dose']])
    scopes = ('L','N','E','Gm','B','P','Gf')
    xmap = {s:np.array([v for r in valid for v in r['scientific']['scopes']['values'][s]]) for s in scopes}
    scores, losses, matrices, scale = independent.analyze(xmap,y,groups)
    predictions = rows('PREDICTIONS.csv')
    assert len(predictions) == 63
    errors = []
    for i, row in enumerate(predictions):
        assert int(row['seed']) == groups[i] and int(row['target']) == i%3
        assert float(row['own_dose']) == y[i]
        for s in scopes:
            errors.append(abs(float(row[s])-(matrices[s][0]@y)[i]))
    prediction_error = max(errors)
    errors=[]
    fold = rows('FOLD_LOSSES.csv')
    assert len(fold) == 21
    for i,row in enumerate(fold):
        assert int(row['seed']) == valid[i]['seed']
        for s in scopes:
            errors.append(abs(float(row[s])-losses[s][i]))
    loss_error=max(errors)
    world = rows('WORLD_LEVEL_DATA.csv')
    assert len(world)==21
    crows=[];errors=[];intact_means=[];fraction_means=[];full_target_contrasts=[]
    for row, r in zip(world,valid):
        assert int(row['seed'])==r['seed']
        assert int(row['deep_step'])==r['scientific']['snapshot_time']
        assert float(row['M_min'])==min(r['scientific']['material_tracer']['deep_M'])
        assert float(row['M_max'])==max(r['scientific']['material_tracer']['deep_M'])
        effects=independent.causal(r)
        effects['fixed_within_branch']=effects.pop('fixed')
        battery=r['scientific']['causal_intervention_battery']['deep']
        intact=np.array(battery['intact']['tracked'])
        own=intact-np.diag([v['tracked'] for v in battery['erase']])
        full=np.array(battery['ablate_full']['tracked'])-np.diag([v['tracked'] for v in battery['erase_ablate_full']])
        effects['full_ablation_residual']=float(full.mean())
        full_target_contrasts.extend(full.tolist())
        intact_means.append(float(intact.mean()))
        fraction_means.append(float((own/intact).mean()))
        assert float(row['intact_uptake'])==intact_means[-1]
        assert float(row['fractional_own_reduction'])==fraction_means[-1]
        crows.append(effects)
        errors.extend(abs(float(row[k])-v) for k,v in effects.items())
    world_error=max(errors)
    cohort=rows('COHORT_ACCOUNTING.csv')
    assert len(cohort)==50
    for row,r in zip(cohort,records):
        assert int(row['seed'])==r['seed']
        for key,value in r['feasibility'].items():
            assert row[key]==('' if value is None else str(value))
    summary=json.loads((PAPER/'results/SUMMARY.json').read_text())
    assert np.count_nonzero(full_target_contrasts)==0
    assert summary['intact_uptake_mean']==float(np.mean(intact_means))
    assert summary['fractional_own_reduction_mean']==float(np.mean(fraction_means))
    assert summary['fractional_own_reduction_world_min']==min(fraction_means)
    assert summary['fractional_own_reduction_world_max']==max(fraction_means)
    errors=[]
    for s in ('N','E','Gm','B'):
        check=independent.t_summary(scores[s])
        errors.extend(abs(check[k]-summary['fold_descriptive_comparisons'][s][k]) for k in check)
    for key in crows[0]:
        v=np.array([r[key] for r in crows]);check=independent.t_summary(v)
        errors.extend(abs(check[k]-summary['causal'][key][k]) for k in check)
        assert summary['causal'][key]['n_positive']==int((v>0).sum())
        nz=int(np.count_nonzero(v))
        assert summary['causal'][key]['n_nonzero']==nz
        p=binomtest(int((v>0).sum()),nz,.5,alternative='greater').pvalue if nz else 1.
        assert summary['causal'][key]['sign_test_p_one_sided']==p
    summary_error=max(errors)
    assert max(prediction_error,loss_error,world_error,summary_error)<1e-12
    out={'status':'PASS_SAME_DATA_FINAL_TABLE_CHECK','input_status':source,
         'cohort_rows':50,'world_rows':21,'prediction_rows':63,'scopes':list(scopes),
         'max_prediction_difference':prediction_error,'max_loss_difference':loss_error,
         'max_world_contrast_difference':world_error,'max_summary_difference':summary_error,
         'one_sided_sign_probabilities_checked':True,'science_worlds_run':0,
         'full_ablation_target_contrasts_exactly_zero':len(full_target_contrasts),
         'intact_uptake_mean':float(np.mean(intact_means)),
         'mean_target_then_world_fractional_reduction':float(np.mean(fraction_means)),
         'reviewed_file_hashes':{p:independent.digest(PAPER/p) for p in ['MANUSCRIPT.md','SUPPLEMENT.md','MANUSCRIPT_RESOLVED.md','SUPPLEMENT_RESOLVED.md','scripts/analyze.py','results/SUMMARY.json','CLAIM_EVIDENCE_MATRIX.csv']}}
    (HERE/'FINAL_NUMERICAL_CHECK.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':
    main()
