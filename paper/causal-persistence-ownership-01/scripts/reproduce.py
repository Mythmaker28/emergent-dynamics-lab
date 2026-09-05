"""One-command article rebuild. Engines and network access are never required.

Use --pdf-python PATH if numerical and ReportLab dependencies are installed in
separate interpreters. Otherwise all steps use the calling Python environment.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--pdf-python",default=sys.executable);args=ap.parse_args()
    steps=[(sys.executable,"scripts/analyze.py"),(sys.executable,"reviews/statistics/recompute_sensitivity.py"),(sys.executable,"reviews/complex_systems/source_check.py"),(args.pdf_python,"scripts/build_documents.py")]
    results=[]
    for exe,path in steps:
        run=subprocess.run([exe,str(ROOT/path)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace")
        results.append({"script":path,"exit_code":run.returncode,"stdout":run.stdout.strip(),"stderr":run.stderr.strip()})
        if run.returncode:
            print(json.dumps(results,indent=2));raise SystemExit(run.returncode)
    outputs=[]
    for folder in [ROOT/"results",ROOT/"figures"]:
        for p in sorted(folder.glob("*")):
            if p.is_file() and p.name not in ["REPRODUCTION.json"]:
                outputs.append({"path":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size})
    for name in ["MANUSCRIPT.pdf","SUPPLEMENT.pdf","MANUSCRIPT_RESOLVED.md","SUPPLEMENT_RESOLVED.md"]:
        p=ROOT/name;outputs.append({"path":name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size})
    env={"python":platform.python_version(),"platform":platform.platform(),"packages":{x:importlib.metadata.version(x) for x in ["numpy","scipy","matplotlib"]}}
    out={"status":"PASS","science_worlds_run":0,"steps":results,"environment":env,"artifacts":outputs,"scope":"Same-data numerical reconstruction and document rendering; no regeneration of spatial trajectories."}
    (ROOT/"results/REPRODUCTION.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":"PASS","steps":len(results),"artifacts":len(outputs),"science_worlds_run":0}))


if __name__=="__main__":main()
