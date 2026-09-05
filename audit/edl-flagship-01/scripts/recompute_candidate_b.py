"""Verify pinned B sources; rerun historical raw-only 03M; newly cross-check core contrasts.

03M is reused transparently, not renamed a new independent implementation. The additional
causal/matrix computation below is written for this audit and imports no project analyzer.
"""
import importlib.util,json,sys
import numpy as np
from scipy.stats import t as student
from common import *
B=HERE/'candidate_b'
def interval(x):
 x=np.asarray(x);m=float(x.mean());d=float(student.ppf(.975,len(x)-1)*x.std(ddof=1)/np.sqrt(len(x)))
 return {'mean':m,'lower':m-d,'upper':m+d}
def main():
 snapshot=read(B/'SNAPSHOT_MANIFEST.json');assert len(snapshot)==191
 for row in snapshot:assert sha(B/row['path'])==row['sha256'],row['path']
 path=B/'analysis/lci-turnover-raw-reproduction-03m/independent_crosscheck_03m.py'
 spec=importlib.util.spec_from_file_location('verified_historical_03m',path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 # Input adapter only: exact bytes from verified pinned Git snapshot. Frozen algorithm unchanged.
 mod.committed_bytes=lambda repo,relative_path:(B/relative_path).read_bytes()
 result=mod.run(B);save('CANDIDATE_B_03M_RERUN.json',result)
 manifest=read(B/'results/LCI-TURNOVER-PROSPECTIVE-03G/raw_manifest_03g.json')
 records=[read(B/'results/LCI-TURNOVER-PROSPECTIVE-03G'/e['path']) for e in manifest['entries']]
 valid=[r for r in records if r['feasibility']['valid']]
 assert len(records)==50 and len(valid)==21
 causal={k:[] for k in ['own_t95','own_minus_sham_t95','own_minus_neighbour_t95','own_fixed_t95','own_under_lambda_plus_only_ablation_t95']}
 for r in valid:
  b=r['scientific']['causal_intervention_battery']['deep']
  intact=np.asarray(b['intact']['tracked']); erased=np.asarray([x['tracked'] for x in b['erase']]);own=intact-np.diag(erased)
  neighbour=intact-(erased.sum(axis=0)-np.diag(erased))/2
  causal['own_t95'].append(own.mean())
  causal['own_minus_sham_t95'].append((np.asarray(b['sham']['tracked'])-np.diag(erased)).mean())
  causal['own_minus_neighbour_t95'].append((own-neighbour).mean())
  causal['own_fixed_t95'].append((np.asarray(b['intact']['fixed'])-np.diag([x['fixed'] for x in b['erase']])).mean())
  causal['own_under_lambda_plus_only_ablation_t95'].append((np.asarray(b['ablate_plus']['tracked'])-np.diag([x['tracked'] for x in b['erase_ablate_plus']])).mean())
 causal={k:interval(v) for k,v in causal.items()}
 y=np.array([v for r in valid for v in r['scientific']['histories']['own_dose']]);world=np.repeat(np.arange(21),3)
 losses={};baseline=[]
 for scope in ['L','N','E','Gm','B']:
  X=np.array([v for r in valid for v in r['scientific']['scopes']['values'][scope]])
  per=[];base=[]
  for i in range(21):
   train=world!=i;test=~train;mu=X[train].mean(axis=0);sd=X[train].std(axis=0);keep=sd>1e-12
   A=(X[train][:,keep]-mu[keep])/sd[keep];T=(X[test][:,keep]-mu[keep])/sd[keep]
   ym=y[train].mean();scale=max(float(y[train].var()),1e-15)
   # Augmented least squares avoids the frozen implementation's normal-equation solve.
   coef=np.linalg.lstsq(np.vstack([A,np.eye(sum(keep))]),np.r_[y[train]-ym,np.zeros(sum(keep))],rcond=None)[0]
   pred=T@coef+ym;per.append(float(np.mean((y[test]-pred)**2)/scale));base.append(float(np.mean((y[test]-ym)**2)/scale))
  losses[scope]=np.array(per);baseline=np.array(base)
 ownership={k:interval(losses[k]-losses['L']) for k in ['N','E','Gm','B']}
 ownskill=interval(baseline-losses['L'])
 errors=[]
 for k,v in causal.items():
  for stat,x in v.items():errors.append(abs(x-result['causal'][k][stat]))
 for k,v in ownership.items():
  for stat,x in v.items():errors.append(abs(x-result['ownership']['G_LOCAL_EXCLUSION']['comparisons'][k]['t95'][stat]))
 errors.append(abs(ownskill['mean']-result['ownership']['G_OWN_PERM']['observed_mean_skill']))
 assert max(errors)<1e-10,max(errors)
 out={'source_commit':'06fd9524f5c7ffb329ee850a10bd9959f2f0bde5','snapshot_files_verified':191,
      'raw_worlds':50,'valid_worlds':21,'invalid_worlds':29,'reserve_worlds':0,
      'causal_new_implementation':causal,'ownership_new_implementation':ownership,'own_skill_new_implementation':ownskill,
      'max_absolute_difference_new_vs_03M':max(errors),'gates_from_03M':result['gates'],'outcome_from_03M':result['outcome'],
      'permutation_p_from_03M':result['ownership']['G_OWN_PERM'],
      'deep_material_fraction_min':min(v for r in valid for v in r['scientific']['material_tracer']['deep_M']),
      'deep_material_fraction_max':max(v for r in valid for v in r['scientific']['material_tracer']['deep_M']),
      'engine_imports':[x for x in sys.modules if x=='edlab' or x.startswith('edlab.')],'science_worlds_run':0,
      'epistemic_status':'Same-data reconstruction. 03M permutation reused; new core causal and LOWO ridge cross-check. No external validation or new-seed replication.'}
 save('CANDIDATE_B_INDEPENDENT.json',out);print(json.dumps({k:out[k] for k in ['raw_worlds','valid_worlds','max_absolute_difference_new_vs_03M','gates_from_03M','outcome_from_03M']}))
if __name__=='__main__':main()
