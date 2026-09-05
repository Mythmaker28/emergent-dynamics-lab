"""Inventory every delivered file; optionally create and verify a deterministic ZIP.

No analysis, simulation or network call. Run after review reports are finalized.
"""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def sha(content):return hashlib.sha256(content).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--archive',action='store_true');args=ap.parse_args()
    required=['MANUSCRIPT.pdf','SUPPLEMENT.pdf','MANUSCRIPT.md','SUPPLEMENT.md','MANUSCRIPT_RESOLVED.md','SUPPLEMENT_RESOLVED.md',
              'CLAIM_EVIDENCE_MATRIX.csv','REPRODUCIBILITY_AUDIT.md','INDEPENDENT_REVIEW_LEDGER.md','DATA_PROVENANCE.md','CHANGED_FILES.txt','ASTRA_FINAL_HANDOFF_FR.md']
    for name in required:assert (ROOT/name).is_file(),name
    for name in ['results/REPRODUCTION.json','reviews/reproducibility/FINAL_REVIEW.json','reviews/statistics/FINAL_NUMERICAL_CHECK.json',
                 'reviews/complex_systems/FINAL_SOURCE_CONSTRUCT_CHECK.json','reviews/editorial/FINAL_EDITORIAL_CHECK.json']:
        d=json.loads((ROOT/name).read_text());assert d['status'].startswith('PASS'),name
    reviewed=json.loads((ROOT/'reviews/reproducibility/FINAL_REVIEW.json').read_text())
    assert reviewed['open_fatal_findings']==0 and reviewed['open_major_findings']==0
    check=json.loads((ROOT/'reviews/reproducibility'/reviewed['final_machine_check']).read_text())
    assert check['status']=='PASS' and len(check['artifact_comparisons'])==25
    for row in check['artifact_comparisons']:
        assert row['byte_identical'] and sha((ROOT/row['path']).read_bytes())==row['baseline_sha256'],row['path']
    for row in json.loads((ROOT/'INPUT_MANIFEST.json').read_text())['files']:
        assert sha((ROOT/row['path']).read_bytes())==row['sha256'],row['path']
    for name,digest in reviewed['pdf_sha256'].items():assert sha((ROOT/name).read_bytes())==digest,name
    files=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or '.pytest_cache' in p.parts or p.suffix=='.pyc' or p.name=='RELEASE_MANIFEST.json':continue
        files.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())})
    manifest={'schema':'EDL-PAPER-REVIEW-RELEASE-1','scientific_status':'FLAGSHIP_CLAIM_NOT_SUPPORTED_BUT_B_DELIVERED',
              'scope':'Complete B article, data/source export and internal reviews; separate multi-architecture audit remains in the repository.',
              'files':files,'file_count_excluding_this_manifest':len(files),'bytes_excluding_this_manifest':sum(r['bytes'] for r in files),
              'pdf_sha256':reviewed['pdf_sha256'],'science_worlds_run':0,'self_hash_excluded':True}
    path=ROOT/'RELEASE_MANIFEST.json';path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    out={'files':len(files),'bytes':manifest['bytes_excluding_this_manifest'],'manifest_sha256':sha(path.read_bytes())}
    if args.archive:
        dest=ROOT.parent/'EDL_PAPER_REVIEW_PACKAGE.zip'
        with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for row in files+[{'path':'RELEASE_MANIFEST.json'}]:
                name=row['path']; info=zipfile.ZipInfo(name,date_time=(2026,9,5,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o100644<<16;z.writestr(info,(ROOT/name).read_bytes(),compresslevel=9)
        with zipfile.ZipFile(dest) as z:
            assert z.testzip() is None
            assert len(z.namelist())==len(files)+1
            for row in files:assert sha(z.read(row['path']))==row['sha256'],row['path']
        out.update(archive=dest.name,archive_bytes=dest.stat().st_size,archive_sha256=sha(dest.read_bytes()))
        dest.with_suffix('.zip.sha256').write_text(out['archive_sha256']+'  '+dest.name+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(out))

if __name__=='__main__':main()
