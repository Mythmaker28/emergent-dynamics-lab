"""One command: verify sources, recompute existing data, run analytic tests, emit output hashes."""
import subprocess,sys
from common import *
def main():
 scripts=['verify_sources.py','recompute_fdflt.py','recompute_omldct.py','check_interval.py','recompute_candidate_b.py','build_inventory.py','test_audit.py']
 completed=[]
 for name in scripts:
  p=subprocess.run([sys.executable,str(HERE/'scripts'/name)],cwd=REPO,capture_output=True,text=True,encoding='utf-8')
  completed.append({'script':name,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
  print(name,'PASS' if p.returncode==0 else 'FAIL',flush=True)
  if p.returncode:save('VALIDATION.json',{'status':'FAIL','steps':completed});raise SystemExit(p.returncode)
 files=sorted(p for p in OUT.glob('*.json') if p.name!='VALIDATION.json')
 save('VALIDATION.json',{'status':'PASS','steps':completed,'outputs':[{'path':str(p.relative_to(HERE)).replace('\\','/'),'sha256':sha(p)} for p in files],
      'science_worlds_run':0,'note':'Analytic fixtures and existing-data recomputation only. Sept-4 artifacts are separately verified by september4_adjudication/audit_september4.py; no new worlds.'})
if __name__=='__main__':main()
