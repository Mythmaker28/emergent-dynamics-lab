"""Portable zero-simulation build; exits on any failed audit or rendering command."""
import argparse
import os
import subprocess
import sys
from pathlib import Path
from paths import PKG

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--tectonic');args=ap.parse_args()
    env=dict(os.environ,PYTHONUTF8='1',SOURCE_DATE_EPOCH='1788480000')
    for name in ['audit_final.py','reconcile.py','emit_numbers.py','make_figures.py','emit_supplement_tables.py','claim_matrix.py','paper_claim_lint.py']:
        subprocess.run([sys.executable,str(PKG/'code'/name)],check=True,env=env)
    if args.tectonic:
        exe=str(Path(args.tectonic).resolve())
        for folder,name in [('manuscript','MANUSCRIPT.tex'),('supplement','SUPPLEMENT.tex')]:
            subprocess.run([exe,'--keep-logs',name],cwd=PKG/folder,check=True,env=env)
    print('V2 build complete; no scientific simulations executed.')

if __name__=='__main__':main()
