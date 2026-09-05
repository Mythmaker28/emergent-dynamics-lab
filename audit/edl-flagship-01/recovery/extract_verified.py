"""Read-only archive verification and safe extraction to new quarantine destinations."""
from pathlib import Path,PurePosixPath
import hashlib,json,subprocess,tarfile,shutil
stage=Path('C:/Users/tommy/Documents/edl-astra-flagship-recovery-staging')
source=Path('C:/Users/tommy/Documents/ising v3')
quar=stage/'quarantine';quar.mkdir(exist_ok=True)
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def safe(name):
    p=PurePosixPath(name)
    assert not p.is_absolute() and '..' not in p.parts and '\\' not in name and ':' not in name,name
    return p
rows=[]
def extract(src,dest,expected=None):
    actual=sha(src)
    if expected:assert actual==expected,(src,actual,expected)
    assert not dest.exists(),dest
    dest.mkdir(parents=True)
    files=[]
    if src.suffix=='.zst':
        names=subprocess.check_output(['tar','-tf',str(src)],text=True).splitlines()
        verbose=subprocess.check_output(['tar','-tvf',str(src)],text=True).splitlines()
        assert len(names)==len(set(n.casefold() for n in names))
        assert all(s and s[0] in '-d' for s in verbose),'link or special archive member'
        for n in names:safe(n)
        subprocess.run(['tar','-xf',str(src),'-C',str(dest)],check=True)
        for p in dest.rglob('*'):
            if p.is_file():files.append(dict(name=p.relative_to(dest).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
    else:
        with tarfile.open(src,'r:') as t:
            members=t.getmembers();seen=set()
            for m in members:
                safe(m.name);key=m.name.casefold();assert key not in seen;seen.add(key)
                assert m.isfile() or m.isdir(),'special member'
            for m in members:
                p=dest.joinpath(*PurePosixPath(m.name).parts)
                if m.isdir():p.mkdir(parents=True,exist_ok=True);continue
                p.parent.mkdir(parents=True,exist_ok=True)
                with t.extractfile(m) as r,p.open('xb') as w:shutil.copyfileobj(r,w)
                assert p.stat().st_size==m.size
                files.append(dict(name=m.name,bytes=m.size,sha256=sha(p)))
    rows.append(dict(archive=str(src),archive_bytes=src.stat().st_size,sha256=actual,expected_outer_sha256=expected,quarantine=str(dest),files=files))
fd=source/'ISING_LIFE_AUTHORITATIVE_RECOVERY/FDFLT01'
extract(fd/'rawcore/FDFLT01_RAW_CORE.tar.zst',quar/'fdflt-core','936fac7c7d61df1a1bedf2d94e5e933930aa55f66de2e057e41202b467f04467')
extract(fd/'prerun/FDFLT01_PRE_RUN_METHODS_CAPSULE.tar.zst',quar/'fdflt-methods','ec550be75428dbc5d257cfc980a33fe3d55887b6ab811992d717738a1bd1859b')
extract(source/'TBRT02/TBRT02_METHODS_C1.tar',quar/'tbrt-methods')
extract(source/'TBRT02/TBRT02_state.tar',quar/'tbrt-state')
for p in sorted((source/'TBRT02').glob('TRIPLE_*.tar')):extract(p,quar/p.stem)
(stage/'EXTRACTION_MANIFEST.json').write_text(json.dumps(rows,indent=2)+'\n')
print('Archives:',len(rows),'files:',sum(len(r['files']) for r in rows),'TBRT triples:',sum('TRIPLE_' in r['archive'] for r in rows))
