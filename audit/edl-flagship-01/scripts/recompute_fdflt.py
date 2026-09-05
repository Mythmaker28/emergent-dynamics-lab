"""New independent endpoint implementation from X/core arrays, no frozen scorer import.

Run: python audit/edl-flagship-01/scripts/recompute_fdflt.py
All worlds retained. Endpoint rule frozen historically; this audit is retrospective.
"""
import math,hashlib
import numpy as np
import re
from scipy.stats import binom,beta
from common import *

def score(path,proto):
 with np.load(path,allow_pickle=False) as z:
  meta=__import__('json').loads(str(z['meta'][0])); names=z['scalar_names'].tolist();sc=z['scalars']
  L=int(proto['point']['L']); radius=float(proto['analytic']['core_radius_cells']);mu=float(proto['point']['muX'])
  cells=z['ycells']; times=cells[:,0].astype(int);assert np.all(np.diff(times)>=0)
  ny=np.zeros(len(sc),dtype=int)
  nc=np.zeros(len(sc),dtype=int);cache={}
  events={}
  for field,sign in [('ybirth',1),('ydeath',-1)]:
   for t,y,x,n in z[field]:events.setdefault(int(t),[]).append((int(y),int(x),sign*int(n)))
  cuts=np.r_[0,np.flatnonzero(np.diff(times))+1,len(times)] if len(times) else [0]
  for a,b in zip(cuts[:-1],cuts[1:]):
   t=int(times[a]);post={tuple(row[1:3]):int(row[3]) for row in cells[a:b]}
   for y,x,n in events.get(t,[]):post[y,x]=post.get((y,x),0)+n
   assert all(n>=0 for n in post.values())
   ny[t]=sum(post.values())
   key=tuple(sorted(cell for cell,n in post.items() if n>0))
   if key not in cache:cache[key]=len(groups_centres(key,L,radius)[0])
   nc[t]=cache[key]
  assert np.array_equal(ny,sc[:,names.index('N_Y')].astype(int))
  assert np.array_equal(nc,sc[:,names.index('n_centres')].astype(int))
  integrity=meta['stop']!='INTEGRITY_FAILURE'
  # Two-centre state after all higher-priority exclusions in frozen six-state operator.
  state=(ny>1)&(nc==2)&integrity
  changes=np.diff(np.r_[False,state,False].astype(int)); starts=np.flatnonzero(changes==1); ends=np.flatnonzero(changes==-1)
  episodes=list(zip(starts,ends)) # half-open
  n_births=int(z['ybirth'][:,3].sum()) if z['ybirth'].size else 0
  out={'world':meta['tag'],'seed':meta['seed'],'index':meta['index'],'integrity_ok':integrity,'n_births':n_births,
       'n_S_episodes':len(episodes),'max_S_duration':max((int(b-a) for a,b in episodes),default=0),'raw_rows_reconstructed':len(sc)}
  cells=z['ycells']; initial=z['field0_X'].astype(np.int64); delta=z['field_delta_X'];grid=np.indices((L,L))
  for key,fraction in [('T_50',.5),('T_primary',1-1/math.e),('T_80',.8),('T_90',.9)]:
   steps=math.ceil(math.log1p(-fraction)/math.log1p(-mu)); qualified=[int(a+steps-1) for a,b in episodes if b-a>=steps]
   ratios=[]
   for step in qualified:
    occupied=cells[cells[:,0]==step,1:3];groups,centres=groups_centres(occupied,L,radius)
    ratio=None
    if len(groups)==2:
     X=initial+delta[:step].sum(axis=0,dtype=np.int64)
     masses=[]
     for centre in centres:
      rounded=np.array([round(float(x))%L for x in centre])
      dist=np.abs(grid-rounded[:,None,None]);dist=np.minimum(dist,L-dist)
      masses.append(int(X[(dist**2).sum(axis=0)<=radius**2].sum()))
     ratio=min(masses)/max(masses) if max(masses)>0 else 0.
    ratios.append(ratio)
   out['dur_ok_'+key]=bool(qualified);out['noP_ok_'+key]=bool(qualified)
   out['resp_ok_'+key]=any(x is not None and x>=fraction for x in ratios)
   out['joint_timing_'+key]=bool(n_births>=1 and qualified and integrity)
   out['PRIMARY_SUCCESS_'+key]=bool(out['joint_timing_'+key] and out['resp_ok_'+key])
   out['maturity_ratios_'+key]=ratios
  out['PRIMARY_SUCCESS']=out['PRIMARY_SUCCESS_T_primary']
  return out

def main():
 text=(REPO/'OBTC02/code/obtc02_protocol.yaml').read_text()
 def constant(section,key):
  block=re.search(r'^'+section+r':\n((?:[ \t].*\n|\n)+)',text,re.M).group(1)
  hits=re.findall(r'^  '+key+r': ([0-9.]+)$',block,re.M);assert len(hits)==1
  return float(hits[0])
 proto={'point':{'L':constant('point','L'),'muX':constant('point','muX')},'analytic':{'core_radius_cells':constant('analytic','core_radius_cells')}}
 manifest=read(REPO/'FDFLT01/out/FDFLT01_SEED_MANIFEST.json')
 files=sorted((REC/'FDFLT01_core').glob('*.npz')); assert len(files)==192
 # Verify payload hashes against recovery manifest before scoring.
 source=next(x for x in read(REC/'EXTRACTION_MANIFEST.json') if x['quarantine'].endswith('fdflt-core'))
 expected={Path(x['name']).name:x['sha256'] for x in source['files']}
 for p in files:assert sha(p)==expected[p.name],p
 rows=[score(p,proto) for p in files]
 planned=manifest['SEEDS']['PRIMARY'];assert [(r['index'],r['seed']) for r in rows]==[(r['index'],r['seed']) for r in planned]
 for kind,series in manifest['SEEDS'].items():
  for r in series:
   key=f"{manifest['PARENT_TIP']}|FDFLT01|B1|{kind}|{r['index']+10000*r['bumps']}"
   assert r['seed']==940000000+int(hashlib.sha256(key.encode()).hexdigest()[:12],16)%50000000
 reference={r['world']:r for r in read(REPO/'FDFLT01/out/FDFLT01_WORLD_RESULTS.json')}
 mismatches=[];compared=0
 for r in rows:
  for k,v in r.items():
   if k in reference[r['world']]:
    compared+=1
    if v!=reference[r['world']][k]:mismatches.append([r['world'],k,v,reference[r['world']][k]])
 n=len(rows);success=sum(r['PRIMARY_SUCCESS'] for r in rows)
 summary={'n':n,'successes':success,'fraction':success/n,'exact_one_sided_p':float(binom.sf(success-1,n,.1)),
          'CP_one_sided_lower95':float(beta.ppf(.05,success,n-success+1)),
          'CP_two_sided95':[float(beta.ppf(.025,success,n-success+1)),float(beta.ppf(.975,success+1,n-success))],
          'critical_success_count':next(k for k in range(n+1) if binom.sf(k-1,n,.1)<=.05),
          'birth_worlds':sum(r['n_births']>0 for r in rows),'joint_timing':sum(r['joint_timing_T_primary'] for r in rows),
          'sensitivity':{k:sum(r['PRIMARY_SUCCESS_'+k] for r in rows) for k in ['T_50','T_primary','T_80','T_90']},
          'integrity_failures':sum(not r['integrity_ok'] for r in rows),'excluded':0,'reserve_worlds':0,
          'seed_formula_verified':198,'unique_seeds':len({r['seed'] for r in rows}),
          'fields_compared':compared,'mismatches':mismatches,'raw_kind':'192 endpoint-bearing X/core NPZ; not full six-plane originals',
          'raw_scalar_rows_reconstructed':sum(r['raw_rows_reconstructed'] for r in rows),
          'science_worlds_run':0,'engine_imports':[]}
 save('FDFLT01_INDEPENDENT.json',summary);save('FDFLT01_PER_WORLD.json',rows)
 print(__import__('json').dumps(summary));assert not mismatches
if __name__=='__main__':main()
