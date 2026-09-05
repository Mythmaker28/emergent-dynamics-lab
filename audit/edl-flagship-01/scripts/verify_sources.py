"""Portable byte, methods, branch-lineage, frozen binding and mission-output inventory audit."""
import json,subprocess,csv,sys,platform
from scipy.stats import binom
from common import *
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def canonical(x):return __import__('hashlib').sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def main():
 prior=read(REC/'INTEGRITY_PRE_ANALYSIS.json')
 for row in prior['archives']:assert sha(REC/'TBRT02_raw'/row['name'])==row['sha256']
 actual={p:__import__('hashlib').sha256(git('show','5372fd86:'+p)).hexdigest() for p in prior['methods_files']};assert actual==prior['methods_files']
 mh=canonical(actual);assert mh==prior['METHODS_HASH']
 for x in prior['out_sidecar']:assert sha(REPO/'TBRT02/out'/x['name'])==x['expected']
 cap=REC/'capsules/fdflt-methods'
 mm=read(REPO/'FDFLT01/out/FDFLT01_METHODS_MANIFEST.json');checks=[]
 for row in mm['MODULES']+mm['DATA_INPUTS']:
  path=cap/row['abs'].lstrip('/');got=sha(path);assert got==row['sha256'],row
  checks.append({'path':row['abs'],'sha256':got})
 blob='\n'.join(f"{m['sha256']} {m['abs']}" for m in sorted(mm['MODULES'],key=lambda m:m['abs']))
 blob+='\n'+'\n'.join(f"{m['sha256']} {m['abs']}" for m in sorted(mm['DATA_INPUTS'],key=lambda m:m['abs']))
 blob+='\npython='+mm['PYTHON']+'\n'+json.dumps(mm['PACKAGES'],sort_keys=True)
 fdhash=__import__('hashlib').sha256(blob.encode()).hexdigest();assert fdhash==mm['COMPLETE_PRE_RUN_METHODS_HASH']
 freeze='235226124f59efed0ae20fdedcf11f7de8fc9c41'
 unchanged={p:git('rev-parse',f'{freeze}:{p}').strip()==git('rev-parse',f'5372fd86:{p}').strip() for p in ['FDFLT01/code/fdflt01_endpoint.py','FDFLT01/code/fdflt01_score_B.py','FDFLT01/out/FDFLT01_SEED_MANIFEST.json','FDFLT01/out/FDFLT01_MASTER_FREEZE.json']}
 assert all(unchanged.values())
 refs={'main':'f382dbf077699aa65c80328b6519035d1cda4a57','PR34':'22ce04d50f2b3ab25b39cbdc1ec5c3c89570e3c6','persistence_v1':'06fd9524f5c7ffb329ee850a10bd9959f2f0bde5','OMLDCT02':'99b8044a037ccfb690131bdccbfa579985d73da8','recovered_history':'5372fd86ba98b5b21a50143ca9c36b25d191daac'}
 lineage=[]
 for name,tip in refs.items():
  base=git('merge-base',tip,refs['recovered_history']).decode().strip()
  counts=git('rev-list','--left-right','--count',tip+'...'+refs['recovered_history']).decode().strip().split()
  lineage.append({'ref':name,'commit':tip,'merge_base_with_recovered':base,'exclusive_commits_ref':int(counts[0]),'exclusive_commits_recovered':int(counts[1])})
 # Seal and raw source bytes for B; order proves Git ancestry, not inaccessible actor cognition.
 B=HERE/'candidate_b';seal=B/'docs/individuation/FINAL_SEAL_MANIFEST_03G.json'
 assert sha(seal)=='cdf7277a00e3017a1389e9334d983364b9aa0af88c646cdec2999e6ad88757fd'
 parent=git('rev-parse','9cb996bb891f9a618e593f2f5c302f30210458de^').decode().strip()
 assert parent=='c158bc0b848710edeafd425f31dfcbd5aefc0934'
 missions=['TBRT02','OMLDCT02','OMLDCT03','TLMR01','FMRCT01','FDFLT01','FDOT01','FMRT01','BPRTC01','MCTT01','FIMRCC02','RPP97','RPP98','GATE01','CLOSE01','ORR01','OBTC02','PQEC01']
 inventory=[]
 for name in missions:
  paths=git('ls-tree','-r','--name-only',refs['recovered_history'],name+'/out').decode().splitlines()
  inventory.append({'mission':name,'output_files':len(paths),'paths':paths})
 ext=read(REPO/'TBRT02/out/TBRT02_CONNECTIVITY_EXPOSURE.json')
 save('SOURCE_VERIFICATION.json',{'TBRT02_archives':123,'METHODS_HASH':mh,'methods_files':17,'out_sidecar':7,
       'FDFLT01_capsule_files':checks,'FDFLT01_METHODS_HASH':fdhash,'FDFLT01_freeze_bytes_unchanged':unchanged,
       'connectivity_bytes':(REPO/'TBRT02/out/TBRT02_CONNECTIVITY_EXPOSURE.json').stat().st_size,'connectivity_records':len(ext['RECORDS']),
       'B_seal_hash':sha(seal),'B_authorization_parent_of_result':parent,'branches':lineage,
       'announced_Sept4_bundle_status':'NOT_LOCATED','announced_b391a739_status':'NOT_LOCATED',
       'inventory':inventory,'CCRA_conditional_arithmetic':{'assumption':'17 adverse wins of 41 independent non-tied pairs, H0 p=0.5, alternative greater',
       'p':float(binom.sf(16,41,.5)),'reverse_tail_24':float(binom.sf(23,41,.5)),
       'status':'COUNT_CONDITIONAL_ONLY__ENDPOINT_COUNTS_BLINDING_CAPABILITY_POWER_UNVERIFIED'},
       'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__},'science_worlds_run':0})
 save('GIT_TIMELINES.json',{'FDFLT01':git('log','--format=%H %aI %s','--reverse','5372fd86','--','FDFLT01').decode(),
      'OMLDCT03':git('log','--format=%H %aI %s','--reverse','5372fd86','--','OMLDCT03').decode(),
      'B':git('log','--format=%H %aI %s','--reverse','06fd9524','--','docs/individuation/FINAL_SEAL_MANIFEST_03G.json','docs/individuation/TURNOVER_AUTHORIZATION_03G.json','results/LCI-TURNOVER-PROSPECTIVE-03G/raw_manifest_03g.json').decode()})
 print(json.dumps({'methods':mh,'FDFLT01_frozen_files':len(checks),'B_seal_verified':True,'CCRA_count_conditional_p':float(binom.sf(16,41,.5)),'branches':lineage}))
if __name__=='__main__':main()
