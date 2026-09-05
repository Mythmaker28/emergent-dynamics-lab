"""Independent relocated-copy check; never changes the article being reviewed.

Every invocation creates fresh owned directories. Installed scientific libraries
are reused explicitly; this is not a dependency reinstallation or world rerun.
"""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row(path, base):
    return {"path":path.relative_to(base).as_posix(), "bytes":path.stat().st_size, "sha256":sha(path)}


def selected_inputs(paper):
    names=["INPUT_MANIFEST.json", "MANUSCRIPT.md", "SUPPLEMENT.md", "requirements.txt",
           "reviews/statistics/recompute_sensitivity.py", "reviews/complex_systems/source_check.py",
           "reviews/complex_systems/VERIFIED_REFERENCES.json"]
    files=[paper/n for n in names]
    for folder in ("data", "source_model", "scripts", "fonts", "assets"):
        files.extend(p for p in (paper/folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix!=".pyc")
    return sorted(set(files))


def copy_inputs(files, paper, dest):
    dest.mkdir(parents=True,exist_ok=False)
    for p in files:
        q=dest/p.relative_to(paper);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)


def run(cmd, cwd, env):
    start=time.monotonic()
    p=subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,text=True,encoding="utf-8",errors="replace")
    return {"command":cmd,"exit_code":p.returncode,"elapsed_seconds":time.monotonic()-start,"stdout":p.stdout,"stderr":p.stderr}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--paper",required=True);ap.add_argument("--staging-parent",required=True)
    ap.add_argument("--science-python",required=True);ap.add_argument("--pdf-python",required=True)
    args=ap.parse_args();paper=Path(args.paper).resolve()
    output=Path(__file__).resolve().parent;output.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    stage=Path(args.staging_parent).resolve()/stamp
    clean=stage/"clean article";negative=stage/"corrupted article"
    files=selected_inputs(paper)
    inputs=[row(p,paper) for p in files]
    # Baseline output bytes are held for comparison, never copied into clean input.
    generated=[p for folder in ("results","figures") for p in (paper/folder).glob("*") if p.is_file() and p.name!="REPRODUCTION.json"]
    generated += [paper/n for n in ("MANUSCRIPT.pdf","SUPPLEMENT.pdf","MANUSCRIPT_RESOLVED.md","SUPPLEMENT_RESOLVED.md","reviews/statistics/STATISTICAL_SENSITIVITY.json","reviews/complex_systems/SOURCE_CHECK.json")]
    baseline={p.relative_to(paper).as_posix():p.read_bytes() for p in generated if p.exists()}
    copy_inputs(files,paper,clean)
    assert not (clean/"results").exists() and not (clean/"figures").exists()
    assert not list(clean.rglob("*.pdf")), "Pre-existing PDFs would compromise clean reconstruction"
    env=os.environ.copy();env.update({"PATH":"","PYTHONPATH":"","PYTHONNOUSERSITE":"1","PYTHONDONTWRITEBYTECODE":"1","PYTHONUTF8":"1","MPLCONFIGDIR":str(stage/"fresh_matplotlib_config")})
    envcheck=[]
    for exe,packages in [(args.science_python,["numpy","scipy","matplotlib"]),(args.pdf_python,["reportlab","pypdf"])]:
        script="import importlib.metadata,json,sys;print(json.dumps({'python':sys.version,'executable':sys.executable,'packages':{p:importlib.metadata.version(p) for p in "+repr(packages)+"}}))"
        envcheck.append(run([exe,"-I","-c",script],clean,env))
    positive=run([args.science_python,"-I",str(clean/"scripts/reproduce.py"),"--pdf-python",args.pdf_python],clean,env)
    comparisons=[]
    for name,original in sorted(baseline.items()):
        p=clean/name
        same=p.exists() and p.read_bytes()==original
        semantic=None
        if p.exists() and name.endswith(".json"):
            semantic=json.loads(p.read_bytes())==json.loads(original)
        comparisons.append({"path":name,"baseline_sha256":hashlib.sha256(original).hexdigest(),"rebuilt_sha256":sha(p) if p.exists() else None,"byte_identical":same,"json_equal":semantic})
    # Fresh corrupted tree ensures failure precedes creation of analysis outputs.
    copy_inputs(files,paper,negative)
    raw=negative/"data/results/LCI-TURNOVER-PROSPECTIVE-03G/raw/seed_54001.json"
    content=bytearray(raw.read_bytes());index=content.index(b"54001");content[index]=ord("6");raw.write_bytes(content)
    negative_run=run([args.science_python,"-I",str(negative/"scripts/analyze.py")],negative,env)
    negative_wrapper=run([args.science_python,"-I",str(negative/"scripts/reproduce.py"),"--pdf-python",args.pdf_python],negative,env)
    negative_files=[p.relative_to(negative).as_posix() for folder in ("results","figures") for p in (negative/folder).rglob("*") if p.is_file()]
    manifest=json.loads((clean/"INPUT_MANIFEST.json").read_text())
    names=[r["path"] for r in manifest["files"]]
    input_source_duplicates=len(names)!=len(set(n.casefold() for n in names))
    unchanged=[r["path"] for r in inputs if sha(paper/r["path"])!=r["sha256"]]
    complete=positive["exit_code"]==0 and all(c["byte_identical"] or c["json_equal"] for c in comparisons) and negative_run["exit_code"]!=0 and negative_wrapper["exit_code"]!=0 and not negative_files and not input_source_duplicates and not unchanged
    result={"status":"PASS" if complete else "REVIEW_REQUIRED", "utc":stamp,"paper_source_directory":str(paper),"clean_directory":str(clean),"corruption_directory":str(negative),
            "tested_inputs":inputs,"manifest_input_count":len(names),"manifest_casefold_duplicates":input_source_duplicates,
            "preexisting_generated_files_copied":0,"execution_environment":envcheck,"environment_scope":"Fresh processes and relocated complete input copy; existing installed dependency libraries reused. No fresh dependency installation, no fresh simulation.",
            "external_path_controls":{"PATH":"empty","PYTHONPATH":"empty","PYTHONNOUSERSITE":"1","top_level_python_isolated_flag":True,"MPLCONFIGDIR":"fresh owned staging directory"},
            "positive_rebuild":positive,"artifact_comparisons":comparisons,
            "raw_one_byte_corruption":{"relative_path":raw.relative_to(negative).as_posix(),"byte_index":index,"byte_before":"5","byte_after":"6","run":negative_run,"reproduction_wrapper_run":negative_wrapper,"generated_files_after_failure":negative_files,"rejected_before_analysis":negative_run["exit_code"]!=0 and negative_wrapper["exit_code"]!=0 and not negative_files},
            "source_inputs_changed_during_test":unchanged,"science_worlds_run":0}
    path=output/("CLEAN_REPRO_CHECK_"+stamp+".json")
    path.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":result["status"],"report":str(path),"stage":str(stage),"rebuild_exit":positive["exit_code"],"comparisons":len(comparisons),"mismatches":[c["path"] for c in comparisons if not c["byte_identical"] and not c["json_equal"]],"changed_during_test":unchanged,"negative_pass":result["raw_one_byte_corruption"]["rejected_before_analysis"]},indent=2))


if __name__=="__main__":main()
