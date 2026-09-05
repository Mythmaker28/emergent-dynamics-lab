"""Read-only source audit, existing records + synthetic statistics; zero engine imports.

Run with the existing scientific Python. Outputs stay beside this file.
The raw endpoint table comes from the preceding independent cell-to-tracker audit;
this script additionally re-reads all 82 relevant NPZ files for hashes, component
occupancy and whole-world Y absence. Frozen CCRA source is executed only after
an AST import allowlist check, as a differential reference, never as the sole scorer.
"""
from pathlib import Path
import ast, collections, hashlib, itertools, json, math, statistics, subprocess, sys
from fractions import Fraction
import numpy as np
import scipy
from scipy.stats import beta, binom, rankdata, norm, spearmanr

HERE=Path(__file__).resolve().parent
AUDIT=HERE.parent
REPO=AUDIT.parents[1]
SNAP=AUDIT/'september4/snapshot'
REF='recovery/edl-state-20260904'
FREEZE='c363afd732109b21a41d6ebc20524cc05f0a7ca7'
RESULT='0fdc550b7fc6f1d3f51b6607ac96d4c6b434aec7'
RANK={'OUT_OF_RANGE':0,'NO_COMPONENT_AT_THE_NEXT_STEP':0,
      'SPLIT_OR_TIE':1,'MERGE':1,'REACHED_THE_WINDOW_HORIZON':2}

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,value):
 (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args])
def tail(n,k):return Fraction(sum(math.comb(n,j) for j in range(k,n+1)),2**n)
def score(records,key='duration',rank_only=False):
 rows=[]
 for r in records:
  values={a:(RANK[r[a+'_termination']],r[a+'_'+key]) for a in ('SELECTIVE','SHAM')}
  x,y=values['SELECTIVE'],values['SHAM']
  if rank_only:x,y=x[:1],y[:1]
  w=int(x>y)-int(x<y)
  rows.append({'index':r['index'],'W':w,'rank_decided':x[0]!=y[0],
               'SELECTIVE_rank':x[0],'SHAM_rank':y[0]})
 k=sum(r['W']==-1 for r in rows);l=sum(r['W']==1 for r in rows);m=k+l
 p=tail(m,k) if m else None
 critical=next((j for j in range(m+1) if tail(m,j)<=Fraction(1,40)),None)
 return {'worse':k,'better':l,'ties':len(rows)-m,'m':m,'critical':critical,
         'p_fraction':str(p),'p_one_sided':float(p) if p else (0.0 if p==0 else None),
         'theta_hat':(k-l)/len(rows),'rank_decided':sum(r['rank_decided'] for r in rows),
         'rows':rows}

def ncomponents(points):
 n=len(points)
 if n<2:return n
 p=list(range(n))
 def root(i):
  while p[i]!=i:p[i]=p[p[i]];i=p[i]
  return i
 d=np.abs(points[:,None,:]-points[None,:,:]);d=np.minimum(d,36-d)
 for i,j in np.argwhere(np.triu((d*d).sum(2)<=25,1)):
  a,b=root(int(i)),root(int(j))
  if a!=b:p[b]=a
 return len({root(i) for i in range(n)})

def bootstrap_rate(data,n,reps,rng):
 # Explicit diagnostic approximation: paired resampling, average ranks for ties,
 # variance = sum(ranks^2)/4, two-sided Gaussian tails, no continuity correction.
 # This is not represented as the unrecoverable original bootstrap execution.
 crossed=0
 for start in range(0,reps,250):
  b=min(250,reps-start);x=data[rng.integers(0,len(data),size=(b,n))]
  ps=[]
  for j in range(2):
   a=x[:,:,j];r=rankdata(np.abs(a),axis=1)
   z=((r*(a>0)).sum(1)-r.sum(1)/2)/np.sqrt((r*r).sum(1)/4)
   ps.append(2*norm.sf(abs(z)))
  ok=(ps[0]<.05)&(ps[1]<.05)&(np.sign(np.median(x[:,:,0],axis=1))==np.sign(np.median(x[:,:,1],axis=1)))
  crossed+=int(ok.sum())
 return {'n':n,'replicates':reps,'crossings':crossed,'probability':crossed/reps,
         'monte_carlo_95_interval':list(binomtest_interval(crossed,reps))}

def binomtest_interval(k,n):
 return (float(beta.ppf(.025,k,n-k+1)) if k else 0.,
         float(beta.ppf(.975,k+1,n-k)) if k<n else 1.)

def main():
 source=read(AUDIT/'results/OMLDCT03_PER_PAIR.json')
 records=[]
 for row in source:
  r={'index':row['index'],'t_m':row['arms']['SELECTIVE']['t_m']}
  for a in ('SELECTIVE','SHAM'):
   r[a+'_duration']=row['arms'][a]['E3_DURATION'];r[a+'_exposure']=row['arms'][a]['E3_EXPOSURE']
   r[a+'_termination']=row['arms'][a]['identity_termination_type']
  for f in ('duration','exposure'):
   r['log_'+f+'_difference']=math.log(r['SELECTIVE_'+f])-math.log(r['SHAM_'+f])
  records.append(r)
 save('CCRA_INPUT_FROM_INDEPENDENT_RAW_ENDPOINTS.json',records)
 historical=read(SNAP/'OMLDCT03/out/OMLDCT03_FROZEN_TEST_RESULT.json')['PER_PAIR']
 differences=[{'index':r['index'],'field':k,'independent':r[k],'historical':h[k]}
              for r,h in zip(records,historical) for k in r if r[k]!=h[k]]
 assert not differences,differences
 primary=score(records);secondary=score(records,'exposure');rank_only=score(records,rank_only=True)
 ref=read(SNAP/'CCRA01/out/CCRA01_RESULT.json')
 assert all(x[k]==y[k] for x,y in zip(primary['rows'],ref['PER_PAIR_SCORES'])
            for k in ('index','W','rank_decided','SELECTIVE_rank','SHAM_rank'))
 assert (primary['worse'],primary['better'],primary['ties'])==(17,24,0)
 assert primary['p_one_sided']==ref['PRIMARY']['p_one_sided_float']
 ci=binomtest_interval(primary['worse'],41)
 save('CCRA_INDEPENDENT.json',{'primary':primary,'secondary_exposure':secondary,
      'retained_pairs':len(records),'input_field_comparisons':len(records)*len(records[0]),
      'input_mismatches':differences,'outcome_score_mismatches':0,
      'theta_95_CP_interval_no_ties_descriptive':[2*ci[0]-1,2*ci[1]-1],
      'rank_only_POSTHOC_DIAGNOSTIC_NOT_NEW_PRIMARY':rank_only,
      'same_rank_duration_worse':sum(r['W']==-1 and not r['rank_decided'] for r in primary['rows']),
      'same_rank_duration_better':sum(r['W']==1 and not r['rank_decided'] for r in primary['rows']),
      'science_worlds_run':0})

 frozen=SNAP/'CCRA01/code/ccra01_frozen.py'
 imports={n.module.split('.')[0] for n in ast.walk(ast.parse(frozen.read_text(encoding='utf-8'))) if isinstance(n,ast.ImportFrom)}
 imports|={a.name.split('.')[0] for n in ast.walk(ast.parse(frozen.read_text(encoding='utf-8'))) if isinstance(n,ast.Import) for a in n.names}
 assert imports<={'__future__','argparse','itertools','json','math','random','sys','fractions'}
 replay={}
 for mode,args in [('capability',['--capability']),('run',['--run',str(HERE/'CCRA_INPUT_FROM_INDEPENDENT_RAW_ENDPOINTS.json')])]:
  p=subprocess.run([sys.executable,str(frozen),*args],capture_output=True,text=True,encoding='utf-8')
  assert p.returncode==0,(p.returncode,p.stderr)
  replay[mode]=json.loads(p.stdout)
  original=read(SNAP/('CCRA01/out/CCRA01_CAPABILITY.json' if mode=='capability' else 'CCRA01/out/CCRA01_RESULT.json'))
  assert replay[mode]==original,mode
 save('FROZEN_DIFFERENTIAL_REPLAY.json',{'allowed_imports':sorted(imports),'full_json_equal_to_original':True,**replay})

 tests=[]
 for m in range(0,15):
  hist=collections.Counter(sum(s) for s in itertools.product((0,1),repeat=m))
  for k in range(m+1):assert tail(m,k)==Fraction(sum(v for j,v in hist.items() if j>=k),2**m)
 tests.append('exact binomial tail versus complete sign enumeration, m=0..14')
 swaps=[dict(r,SELECTIVE_duration=r['SHAM_duration'],SHAM_duration=r['SELECTIVE_duration'],
             SELECTIVE_termination=r['SHAM_termination'],SHAM_termination=r['SELECTIVE_termination']) for r in records]
 assert all(a['W']==-b['W'] for a,b in zip(primary['rows'],score(swaps)['rows']))
 tests.append('all real pair signs reverse when arms swap')
 renamed=[{k:('NO_COMPONENT_AT_THE_NEXT_STEP' if v=='OUT_OF_RANGE' else v) for k,v in r.items()} for r in records]
 assert score(renamed)==primary
 tests.append('all real pair scores invariant under zero-successor string coarsening')
 selfpaired=[dict(r,SELECTIVE_duration=r['SHAM_duration'],SELECTIVE_termination=r['SHAM_termination']) for r in records]
 assert score(selfpaired)['ties']==41 and score(selfpaired)['critical'] is None
 tests.append('identical paired outcomes give 41 ties and no resolvable test')
 assert tail(41,28)<=Fraction(1,40)<tail(41,27)
 tests.append('critical count 28, exact achieved null size '+str(float(tail(41,28))))
 save('ANALYTIC_TESTS.json',{'tests':tests,'n_pass':len(tests),'science_worlds_run':0})

 history=[]
 for commit in git('rev-list','--reverse',REF).decode().split():
  history.append({'commit':commit,'metadata':git('show','-s','--format=%aI%n%cI%n%P%n%s',commit).decode().strip().splitlines(),
                  'changes':git('diff-tree','--root','--no-commit-id','--name-status','-r',commit).decode().splitlines()})
 bindings=[]
 for p in ('CCRA01/code/ccra01_frozen.py','CCRA01/out/CCRA01_PREREGISTRATION.md','CCRA01/out/CCRA01_CAPABILITY.json'):
  b=git('show',FREEZE+':'+p)
  assert b==git('show',REF+':'+p)==(SNAP/p).read_bytes()
  bindings.append({'path':p,'sha256':hashlib.sha256(b).hexdigest(),'freeze_to_tip_byte_identical':True})
 initial_tree=git('ls-tree','-rl','fe6b6311a38a90dfe1be43a0b0ed71ed87fdf051').decode().splitlines()
 save('HISTORY_AND_BINDINGS.json',{'ref':REF,'tip':git('rev-parse',REF).decode().strip(),
      'initial_commit_n_files':len(initial_tree),'initial_commit_total_blob_bytes':sum(int(x.split()[3]) for x in initial_tree),
      'history':history,'ccra_bindings':bindings,
      'caveats':['Git order and timestamps are recorded metadata, not an independently timestamped preregistration.',
                 'Freeze commit also includes REVIEW01 adjudication; it is not literally a freeze-only commit.',
                 'Author blind status is declared in the protocol; no agent transcript or access log is present.',
                 'All 41 outcomes existed in ancestors before CCRA01; this is retrospective data reanalysis.']})

 ledger=sorted([json.loads(line) for p in (SNAP/'TBRT02/work').glob('TBRT02_SEALED_LEDGER_*.jsonl') for line in p.read_text().splitlines() if line],key=lambda r:r['index'])
 adm={r['index']:r for r in ledger if r['ADMISSIBLE']}
 occupancy=collections.defaultdict(lambda:collections.Counter());mortality=collections.defaultdict(list);raw_records=[]
 for r in records:
  for arm in ('SELECTIVE','SHAM'):
   entry=adm[r['index']]['ARCHIVES'][arm];path=AUDIT/'recovery/TBRT02_raw'/Path(entry['path']).name
   assert sha(path)==entry['sha256']
   with np.load(path,allow_pickle=False) as z:
    ct=z['c_t'].astype(int);coords=np.column_stack((z['c_y'],z['c_x'])).astype(int)
    meta=json.loads(str(z['meta'][0]));T=meta['steps_executed'];tm=r['t_m'];end=tm+r[arm+'_duration']
    present=np.bincount(ct,minlength=T)>0
    if np.any(~present[tm:]):mortality[arm].append(r['index'])
    counts=collections.Counter();multi_times=[]
    for t in range(tm,end+1):
     a,b=np.searchsorted(ct,[t,t+1]);nc=ncomponents(coords[a:b]);counts[nc]+=1
     if nc>1:multi_times.append(t)
    if arm=='SELECTIVE':assert multi_times==[tm]
    occupancy[arm].update(counts)
    raw_records.append({'index':r['index'],'arm':arm,'sha256':entry['sha256'],
                        'window_inclusive':[tm,end],'component_count_histogram':dict(counts),
                        'multi_component_steps_relative_to_trigger':[t-tm for t in multi_times],
                        'any_empty_Y_step_post_trigger':bool(np.any(~present[tm:]))})
 expected=read(SNAP/'FIMRCC02/out/FIMRCC02_POWER.json')['MORTALITE_PAR_BRAS']
 assert all(mortality[a]==expected['Y_eteint_'+a] for a in ('SELECTIVE','SHAM'))
 s,h=map(set,[mortality['SELECTIVE'],mortality['SHAM']])
 table=[len(s-h),len(h-s),len(s&h),41-len(s|h)]
 save('RAW_OCCUPANCY_AND_MORTALITY.json',{'n_archives_rehashed_and_read':82,
      'inclusive_window_component_counts':dict(occupancy),'whole_world_Y_absence_indices':dict(mortality),
      'mortality_paired_table_SEL_only_SHAM_only_both_neither':table,
      'mortality_sign_p_two_sided':float(2*tail(table[0]+table[1],max(table[:2]))),
      'records':raw_records,'science_worlds_run':0})
 print('CCRA, frozen replay, history, 82 raw reads pass',flush=True)

 runtimes=[r['runtime_s'] for r in ledger]
 batches=[read(p)['batch_seconds'] for p in sorted((SNAP/'TBRT02/work').glob('TBRT02_RUN_STATE.json.*'))]
 q=beta.ppf([.05,.5,.95],41.5,844.5);hours_per_seed=max(batches)/3600/885
 # TRIGGERED is not sufficient: 12 triggers stop before branching. Their only
 # cost is the prefix. ARCHIVES identifies the 41 actually forked triples.
 cost2=0.;admitted=0;first_crossing=None;pre_crossing=None
 for r in ledger:
  before={'last_completed_index':r['index']-1,'spent':cost2,'pairs':admitted}
  cost2+=r['prefix_steps']/r['horizon']+(2*(r['horizon']-r['prefix_steps'])/r['horizon'] if 'ARCHIVES' in r else 0)
  admitted+=bool(r['ADMISSIBLE'])
  if cost2>=512 and first_crossing is None:
   first_crossing={'index':r['index'],'spent':cost2,'pairs':admitted};pre_crossing=before
 rounded_recost=sum(r['instance_cost']-((r['horizon']-r['prefix_steps'])/r['horizon'] if 'ARCHIVES' in r else 0) for r in ledger)
 save('PRIOR_ASTRA_COST_ERRATUM.json',{'prior_script':'audit/edl-flagship-01/scripts/recompute_omldct.py',
      'error':'Used TRIGGERED to charge two complete continuations, even for 12 triggers rejected before the fork.',
      'n_triggers_without_archives':sum(r['TRIGGERED'] and 'ARCHIVES' not in r for r in ledger),
      'example':next(r for r in ledger if r['TRIGGERED'] and 'ARCHIVES' not in r),
      'correct_exact_two_arm_prefix_cost':cost2,'rounded_recorded_cost_minus_one_real_arm':rounded_recost,
      'first_seed_crossing_512':first_crossing,'completed_before_that_seed':pre_crossing,
      'historical_checker_511_535_is_cost_before_index789':True,
      'withdraw_prior_astra_claims':['593.509909 two-arm total','index 760 with 36 pairs as the two-arm stopping point'],
      'unchanged_conclusion':'41 pairs still exceed the frozen two-arm accrual; only 38 admissible pairs are available when the budget binds.'})
 data=np.array([[r['log_duration_difference'],r['log_exposure_difference']] for r in records])
 rng=np.random.default_rng(2026090501)
 rows=[]
 for n in (41,45,100,200,400):
  p=bootstrap_rate(data,n,10000,rng)
  rows.append({**p,'seeds_median_rate':n/q[1],'seeds_unfavorable_q05_rate':n/q[0],
               'wall_hours_observed_throughput':n/q[1]*hours_per_seed,
               'two_arm_instances':n/q[1]*cost2/885})
 outer=[]
 for i in range(100):
  d=data[rng.integers(0,41,size=41)]
  outer.append(bootstrap_rate(d,400,200,rng)['probability'])
 save('POWER_AND_RUNTIME_DIAGNOSTIC.json',{'classification':'POSTHOC_PLUG_IN_DIAGNOSTIC_NOT_PROSPECTIVE_POWER',
      'method':'paired empirical bootstrap; Gaussian signed-rank approximation with mean ranks and tie-correct variance; AND of two two-sided p<.05 and median sign agreement',
      'original_sept4_bootstrap_code_rng_and_outputs':'NOT_PRESENT; exact original 34 percent cannot be reproduced as a sealed value',
      'rng':'numpy.default_rng PCG64 seed 2026090501','numpy':np.__version__,'scipy':scipy.__version__,
      'n_ledger':len(ledger),'n_triggered':sum(r['TRIGGERED'] for r in ledger),'n_admissible':len(adm),
      'runtime_seconds':{'mean':statistics.mean(runtimes),'median':statistics.median(runtimes),'sum':sum(runtimes),'sd_sample':statistics.stdev(runtimes),'min':min(runtimes),'max':max(runtimes)},
      'worker_batch_seconds':batches,'wall_hours_observed_max_batch':max(batches)/3600,
      'wall_hours_sum_runtime_divided_by_two':sum(runtimes)/7200,
      'wall_hours_per_seed':hours_per_seed,'Jeffreys_rate_q05_q50_q95':q.tolist(),
      'twelve_hours':{'seeds':12/hours_per_seed,'expected_pairs_at_q50_rate':12/hours_per_seed*q[1],
                      'expected_pairs_at_q05_rate':12/hours_per_seed*q[0]},
      'table':rows,'double_bootstrap_diagnostic':{'outer':100,'inner':200,'powers':outer,
          'q05_q50_q95':np.quantile(outer,[.05,.5,.95]).tolist(),'fraction_below_half':float(np.mean(np.array(outer)<.5))},
      'co_primary_spearman_rho':float(spearmanr(data[:,0],data[:,1]).statistic),
      'co_primary_pearson_rho':float(np.corrcoef(data.T)[0,1]),
      'limits':['Timing is extrapolation of historical host throughput, not a current-machine benchmark.',
                'Rate quantiles alone omit future binomial acquisition variance and runtime-yield dependence.',
                'Empirical bootstrap power for a composite of two tests is not solely a monotone transform of one observed p-value.',
                'Double-bootstrap frequencies are not probabilities that empirical worlds are compatible truths.',
                'These are OMLDCT03 calculations, not power of the different CCRA01 endpoint.'],
      'science_worlds_run':0})
 print('Power diagnostics complete; no worlds launched',flush=True)

if __name__=='__main__':main()
