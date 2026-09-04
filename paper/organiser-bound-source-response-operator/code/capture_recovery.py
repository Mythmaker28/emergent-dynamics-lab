"""One-time recovery into this task's isolated clone, from pinned Git objects.
Refuses to replace an existing manifest. Never use this to refresh failing hashes.
"""
import hashlib
import subprocess
from paths import ROOT, PKG, PROV, digest, dump, require

BASE='06c592313df96601de8d2a89676d5a5cf79fc414'
IOM='4282fc6ead915639711f5096c7825d3880a640d4'
def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args])

def main():
    require(not (PROV/'SOURCE_MANIFEST.json').exists(),'manifest already exists; refusing rebinding')
    programmes=['ORR01','OBTC02','OBDI02','OBTR01','OBFOR01','SEAL01','MYQBD01','PQEC01','FLCR01']
    allpaths=git('ls-tree','-r','--name-only',BASE,*programmes).decode().splitlines()
    paths=[p for p in allpaths if '/code/' in p or '/out/' in p or '/prefix_outputs/' in p or
           (('/raw/' in p) and p.split('/')[0] in ['OBTC02','OBDI02','OBFOR01'])]
    paths=[p for p in paths if not p.endswith(('.log','.png','.pdf','.pyc'))]
    rows=[]
    for rel in paths:
        raw=git('show',BASE+':'+rel)
        p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        rows.append(dict(path=rel,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
                         git_commit=BASE,git_blob=git('rev-parse',BASE+':'+rel).decode().strip()))
    for rel in ['docs/EXP_SC_IOM_00_FINAL_REPORT.md','docs/EXP_SC_IOM_00_ERRATUM.md','docs/EXP_SC_IOM_00_FREEZE_MANIFEST.json']:
        raw=git('show',IOM+':'+rel);p=PROV/'context'/rel.split('/')[-1];p.write_bytes(raw)
        rows.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(raw),sha256=digest(p),git_commit=IOM,
                         git_source_path=rel,git_blob=git('rev-parse',IOM+':'+rel).decode().strip()))
    dump(PROV/'SOURCE_MANIFEST.json',dict(base_commit=BASE,context_commit=IOM,files=rows))
    seal=__import__('json').loads((ROOT/'SEAL01/out/_seal_provenance.json').read_text())
    freeze=seal['TIPS']['OBFOR01_FREEZE_TIP']['actual']
    first=seal['TIPS']['OBFOR01_FIRST_FRESH_ARMS_COMMIT']['actual']
    require(subprocess.run(['git','-C',str(ROOT),'merge-base','--is-ancestor',freeze,first]).returncode==0,'freeze not ancestor')
    binding=[]
    for rel,r in seal['LOAD_BEARING_FILES'].items():
        before=git('rev-parse',freeze+':'+rel).decode().strip()
        now=git('rev-parse',BASE+':'+rel).decode().strip()
        require(before==now==r['blob_at_freeze'],'frozen method changed: '+rel)
        binding.append(dict(path=rel,blob=before))
    dump(PROV/'GIT_FREEZE_VERIFICATION.json',dict(status='PASS',freeze_commit=freeze,first_raw_commit=first,
        freeze_is_ancestor=True,frozen_files_unchanged=binding,
        note='Decision rule is pre-run; adjudication code and interval diagnostics are post-run. Git ancestry establishes recorded order, not an externally timestamped preregistration.'))
    print('Captured',len(rows),'sources;',len(binding),'frozen files unchanged.')

if __name__=='__main__':main()
