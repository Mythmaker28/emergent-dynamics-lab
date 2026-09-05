"""Independent cell-to-identity reconstruction and signed-rank analysis, no frozen classifier import."""
import json,math
from collections import Counter
import numpy as np
from common import *

def endpoint(path,L,radius):
 with np.load(path,allow_pickle=False) as z:
  m=json.loads(str(z['meta'][0]));T=int(m['steps_executed']);tm=int(m['t_m'])
  ct=z['c_t'].astype(int);cy=z['c_y'].astype(int);cx=z['c_x'].astype(int);ny=z['c_nY'].astype(int)
  s=z['s'].astype(np.int64)
 assert len(s)==T and np.all(np.diff(s[:,0])==1) and m['integrity_ok']
 assert np.all(np.diff(ct)>=0)
 def frame(t):
  a,b=np.searchsorted(ct,[t,t+1]); cells=np.column_stack((cy[a:b],cx[a:b])); g,c=groups_centres(cells,L,radius)
  return g,c,cells,ny[a:b]
 groups,centres,cells,counts=frame(tm)
 locked={tuple(x) for x in m['intervention']['daughter_cells']}
 hit=[i for i,g in enumerate(groups) if {tuple(cells[j]) for j in g}==locked]; assert len(hit)==1
 current=hit[0]; exposure=int(counts[groups[current]].sum());end=tm
 for t in range(tm+1,T):
  g,c,_,mass=frame(t)
  if len(c)==0:termination='NO_COMPONENT_AT_THE_NEXT_STEP';break
  distances=np.abs(centres[:,None]-c[None,:]);distances=np.minimum(distances,L-distances)
  edges=(distances**2).sum(axis=2)<=radius**2
  successors=np.flatnonzero(edges[current])
  if len(successors)==0:termination='OUT_OF_RANGE';break
  if len(successors)>1:termination='SPLIT_OR_TIE';break
  nxt=int(successors[0])
  if edges[:,nxt].sum()!=1:termination='MERGE';break
  exposure+=int(mass[g[nxt]].sum());end=t;current=nxt;centres=c
 else:termination='REACHED_THE_WINDOW_HORIZON'
 return {'E3_DURATION':end-tm,'E3_EXPOSURE':exposure,'identity_termination_type':termination,'t_m':tm,
         'steps_executed':T}

def main():
 ledger=[readline for p in sorted((REPO/'TBRT02/work').glob('TBRT02_SEALED_LEDGER_*.jsonl')) for line in p.read_text().splitlines() if line.strip() for readline in [json.loads(line)]]
 selected=sorted((r for r in ledger if r.get('ADMISSIBLE')),key=lambda r:r['index'])
 assert len(selected)==41 and len({r['seed'] for r in selected})==41
 freeze=read(REPO/'TBRT02/out/TBRT02_MASTER_FREEZE.json')['FROZEN_PHYSICS'];L=freeze['L'];radius=freeze['CORE_R']
 archived={r['index']:r for r in read(REPO/'OMLDCT03/work/omldct03_pairs.json')}
 table=[];mismatches=[];integrity=0
 for r in selected:
  row={'index':r['index'],'seed':r['seed'],'arms':{}}
  for arm,entry in r['ARCHIVES'].items():
   path=REC/'TBRT02_raw'/Path(entry['path']).name
   assert sha(path)==entry['sha256'];integrity+=1
   if arm not in ['SELECTIVE','SHAM']:
    with np.load(path,allow_pickle=False) as z:
     meta=json.loads(str(z['meta'][0]));s=z['s'];assert len(s)==meta['steps_executed'] and meta['integrity_ok'] and np.all(np.diff(s[:,0])==1)
    continue
   result=endpoint(path,L,radius);row['arms'][arm]=result
   for classifier in ['_A','_B']:
    ref=archived[r['index']]['ARMS'][arm][classifier]
    for k in ['E3_DURATION','E3_EXPOSURE','identity_termination_type']:
     if result[k]!=ref[k]:mismatches.append([r['index'],arm,classifier,k,result[k],ref[k]])
  table.append(row)
  if len(table)%10==0:print('reconstructed pairs',len(table),flush=True)
 result={'n_pairs':len(table),'archive_hash_and_content_pass':integrity,'raw_endpoint_comparisons':41*2*2*3,'endpoint_mismatches':mismatches}
 historical=read(REPO/'OMLDCT03/out/OMLDCT03_FROZEN_TEST_RESULT.json')['DECISION']
 for label,key in [('duration','E3_DURATION'),('exposure','E3_EXPOSURE')]:
  diffs=[math.log(r['arms']['SELECTIVE'][key])-math.log(r['arms']['SHAM'][key]) for r in table]
  result[label]=signed_rank(diffs)
  for k in ['W_plus','exact_two_sided_p','median_difference','hodges_lehmann','hl_interval']:
   assert np.allclose(result[label][k],historical[label][k],rtol=0,atol=1e-12),(label,k)
 result['12_statistics_match']=True
 result['termination_counts']={a:dict(Counter(r['arms'][a]['identity_termination_type'] for r in table)) for a in ['SELECTIVE','SHAM']}
 result['frozen_statistical_AND_pass']=all(result[k]['exact_two_sided_p']<.05 for k in ['duration','exposure']) and np.sign(result['duration']['median_difference'])==np.sign(result['exposure']['median_difference'])
 # Literal prefix/H cost convention disclosed by author, independently accumulated in index order.
 cost=0.;admitted=0;cross=None
 for r in sorted(ledger,key=lambda x:x['index']):
  cost+=float(r.get('instance_cost',0))
  admitted+=bool(r.get('ADMISSIBLE'))
  if cost>=512 and cross is None:cross={'index':r['index'],'admissible':admitted,'cost':cost}
 result['recorded_instance_cost_first_crossing_512']=cross
 result['recorded_total_instance_cost']=cost
 # OMLDCT02-equivalent two-arm accounting, not TBRT02's three-arm recorded cost.
 cost2=0.;admitted2=0;cross2=None
 for r in sorted(ledger,key=lambda x:x['index']):
  H=r['horizon'];prefix=r['prefix_steps']
  cost2+=prefix/H+(2*(H-prefix)/H if r.get('TRIGGERED') else 0)
  admitted2+=bool(r.get('ADMISSIBLE'))
  if cost2>=512 and cross2 is None:cross2={'index':r['index'],'admissible':admitted2,'cost':cost2}
 result['two_arm_prefix_accounting_first_crossing_512']=cross2
 result['two_arm_prefix_accounting_total']=cost2
 result['status']='RECOMPUTED_SAME_DATA__OUTSIDE_OMLDCT02_FROZEN_ACCRUAL__INCONCLUSIVE'
 result['interval_caveat']='Frozen Walsh interval uses untied null order indices even with ties/zeros. Numerical reproduction is not a proof of nominal coverage.'
 result['science_worlds_run']=0
 save('OMLDCT03_INDEPENDENT.json',result);save('OMLDCT03_PER_PAIR.json',table)
 print(json.dumps(result));assert not mismatches
if __name__=='__main__':main()
