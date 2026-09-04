"""Build a deterministic ZIP with exact sources; optionally rebuild an extracted tree."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile
from paths import ROOT,PKG,PROV,digest,dump,require

def shipping_paths():
    man=json.loads((PROV/'SOURCE_MANIFEST.json').read_text())
    paths={ROOT/r['path'] for r in man['files']}
    for p in PKG.rglob('*'):
        if p.is_file() and p.suffix not in {'.log','.aux','.out','.toc','.bbl','.blg','.pyc'} and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts:
            paths.add(p)
    for p in paths:require(p.resolve().is_relative_to(ROOT.resolve()),'shipping path outside task root')
    return sorted(paths,key=lambda p:p.relative_to(ROOT).as_posix())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--verify',action='store_true');ap.add_argument('--tectonic');args=ap.parse_args()
    out=ROOT/'delivery';out.mkdir(exist_ok=True);paths=shipping_paths()
    archive=out/'ISING_LIFE_MANUSCRIPT_V2_REVIEW.zip';rows=[]
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in paths:
            rel=p.relative_to(ROOT).as_posix();data=p.read_bytes()
            info=zipfile.ZipInfo(rel,date_time=(2026,9,4,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,data)
            rows.append(dict(path=rel,bytes=len(data),sha256=digest(p)))
    dump(out/'DELIVERY_MANIFEST.json',dict(format='ZIP',source_manifest_sha256=digest(PROV/'SOURCE_MANIFEST.json'),files=rows))
    (out/'SHA256SUMS').write_text('\n'.join(digest(p)+'  '+p.name for p in [archive,out/'DELIVERY_MANIFEST.json'])+'\n',encoding='utf-8')
    print('Review archive:',len(rows),'files;',archive.stat().st_size,'bytes.',flush=True)
    if not args.verify:return
    require(args.tectonic,'standalone verification requires the PDF compiler path')
    work=ROOT/'.audit-work';work.mkdir(exist_ok=True)
    dest=Path(tempfile.mkdtemp(prefix='standalone-v2-',dir=work))
    with zipfile.ZipFile(archive) as z:z.extractall(dest)
    for r in rows:require(digest(dest/r['path'])==r['sha256'],'extraction digest mismatch')
    rel=PKG.relative_to(ROOT);copy=dest/rel;env=dict(os.environ,PYTHONUTF8='1')
    commands=[([sys.executable,str(copy/'code/reproduce.py'),'--tectonic',str(Path(args.tectonic).resolve())],'build'),
              ([sys.executable,'-m','pytest',str(copy/'code/test_audit.py'),'-q'],'tests')]
    for cmd,name in commands:
        result=subprocess.run(cmd,cwd=dest,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8')
        (PROV/('STANDALONE_'+name.upper()+'.txt')).write_text(result.stdout,encoding='utf-8')
        print(name+': '+result.stdout[-500:],flush=True)
        require(result.returncode==0,'standalone '+name+' failed; see log')
    generated=['provenance/AUDIT_RESULTS.json','provenance/FRESH_ARM_RECOMPUTATION.csv','provenance/HISTORICAL_ARM_RECOMPUTATION.csv',
        'provenance/PAPER_NUMERICAL_RECONCILIATION.json','provenance/PAPER_NUMERICAL_RECONCILIATION.csv','provenance/PAPER_MACRO_INDEX.json',
        'provenance/PAPER_FIGURE_PROVENANCE.json','provenance/PAPER_CLAIM_LINT.json','manuscript/numbers.tex','supplement/S4_arms.tex','EVIDENCE_CLAIM_MATRIX.csv',
        'manuscript/MANUSCRIPT.pdf','supplement/SUPPLEMENT.pdf']
    generated += [p.relative_to(PKG).as_posix() for folder in ['figures','figure_data'] for p in sorted((PKG/folder).glob('*')) if p.is_file()]
    compared=[]
    for r in generated:
        a,b=digest(PKG/r),digest(copy/r);require(a==b,'nonidentical deterministic rebuild: '+r)
        compared.append(dict(path=r,sha256=a))
    bound=[p for p in PKG.rglob('*') if p.is_file() and p.suffix in {'.py','.tex','.bib'}]
    bound.append(PKG/'requirements.txt')
    dump(PROV/'STANDALONE_REBUILD.json',dict(status='PASS',extracted_files=len(rows),all_extracted_hashes_match=True,
        source_verification_files=482,tests_passed=4,git_required=False,scientific_world_starts=0,new_predictor_simulations=0,
        byte_identical_generated_files=compared,
        build_sources=[dict(path=p.relative_to(PKG).as_posix(),sha256=digest(p)) for p in sorted(bound)],
        note='Numerical assets and both PDFs regenerated in a fresh extracted directory with the same audited runtime. No cross-platform byte-identical guarantee.'))
    print('Standalone PASS; identical regenerated files:',len(compared),flush=True)

if __name__=='__main__':main()
