import hashlib,json,shutil,pathlib,datetime
S=pathlib.Path(__file__).parent
R=S.parent/'edl-astra-flagship-audit-01'
O=R/'audit/edl-flagship-01/recovery'
O.mkdir(parents=True,exist_ok=True)
def sha(p): return hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
def dump(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
ex=json.loads((S/'EXTRACTION_MANIFEST.json').read_text())
raw={p.name:p for p in (S/'quarantine').glob('TRIPLE*/*.npz')}
rows=[json.loads(l) for p in sorted((R/'TBRT02/work').glob('TBRT02_SEALED_LEDGER_*.jsonl')) for l in p.read_text().splitlines() if l.strip()]
adm=sorted((r for r in rows if r.get('ADMISSIBLE')),key=lambda r:r['index'])
assert len(adm)==41 and len(raw)==123
matches=[]
for r in adm:
 for arm,a in r['ARCHIVES'].items():
  name=pathlib.PurePosixPath(a['path']).name
  p=raw[name]; h=sha(p); assert h==a['sha256'],name
  matches.append({'name':name,'index':r['index'],'seed':r['seed'],'arm':arm,'sha256':h,'bytes':p.stat().st_size,'sealed_path':a['path']})
freeze=json.loads((R/'TBRT02/out/TBRT02_MASTER_FREEZE.json').read_text(encoding='utf-8'))
mh={p:sha(R/p) for p in freeze['METHODS_FILES']}
assert mh==freeze['METHODS_FILES']
digest=hashlib.sha256(json.dumps(mh,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
assert digest==freeze['METHODS_HASH']
sums=[]
for line in (R/'TBRT02/out/SHA256SUMS').read_text().splitlines():
 h,name=line.split(); got=sha(R/'TBRT02/out'/name)
 sums.append({'name':name,'expected':h,'actual':got,'match':h==got})
assert all(x['match'] for x in sums)
dump(O/'INTEGRITY_PRE_ANALYSIS.json',{'ledger_rows':len(rows),'triples':41,'archives':matches,'methods_files':mh,'METHODS_HASH':digest,'out_sidecar':sums,'science_worlds_run':0})
for name in ['EXTRACTION_MANIFEST.json','IMPORTED_BUNDLES.json','BUNDLE_SEARCH.json','extract_verified.py','scan_bundles.py']:
 shutil.copyfile(S/name,O/name)
dest=O/'TBRT02_raw'; dest.mkdir(exist_ok=True)
for p in raw.values(): shutil.copyfile(p,dest/p.name)
dest=O/'FDFLT01_core'; dest.mkdir(exist_ok=True)
for p in (S/'quarantine/fdflt-core/FDFLT01/core').glob('*.npz'): shutil.copyfile(p,dest/p.name)
for capsule in ['fdflt-methods','tbrt-methods','tbrt-state']:
 shutil.copytree(S/'quarantine'/capsule,O/'capsules'/capsule,dirs_exist_ok=True)
shutil.copyfile(__file__,O/'preserve_recovery.py')
j=R/'docs/agent_journals/2026-09-05/flagship-audit-01-recovery.md';j.parent.mkdir(parents=True,exist_ok=True)
j.write_text('''# EDL-ASTRA-FLAGSHIP-AUDIT-01 — recovery checkpoint

Role: Astra, primary agent. Scope: user-authorized read-only source search and isolated recovery; no scientific worlds.
Starting head: 5372fd86ba98b5b21a50143ca9c36b25d191daac, isolated recovery/astra-edl-tbrt02-20260905. Original dirty checkout preserved. Ending state: this recovery commit; see Git log for immutable hash.
Start/end: 2026-09-05; checkpoint time recorded in Git metadata. Scientific audit continues on a separate branch after durable push.

OBSERVED: 129 local bundle headers searched; announced Sept-4 b391a739 bundle absent. Recovered TBRT02_INCREMENT.bundle SHA256 7199a4603e8e387ca50326e5e270f852b6e291a8d182d6c65ee5a844f31c2541. All 123 TBRT02 NPZ files match sealed ledger; 192 FDFLT01 endpoint core archives recovered. Methods and 7 sidecar hashes match. Connectivity JSON is nonempty bytes with zero records.
INFERRED: sources suffice for existing-data audit, not verification of missing Claude Sept-4 CCRA/findings.
HYPOTHESIS: independent scoring may recover the positive endpoint; not yet computed.
WHAT WOULD FALSIFY THIS: raw/seal mismatch or independent endpoint discrepancy.
Actions: safe archive extraction in quarantine; bundle verify and import in owned bare repository; exact-byte copying and integrity manifest. Read AGENTS, charter, state/index/log, latest completed journal, TBRT02 freeze, OMLDCT03 results/methods and FDFLT01 endpoint. Historical central state documents are stale relative to recovered late-August mission artifacts; not authority for new simulations.
Failures: announced bundle absent on disk/remote/accessible prior task and Drive; old source repository has broken checkpoint refs and Windows-invalid paths. Neither repaired or deleted. Sparse checkout uses transient core.protectNTFS=false only for excluded historical paths.
Files: audit/edl-flagship-01/recovery, this journal, RUN_INDEX. No original scientific methods or results edited.
Reproduce integrity: manifests specify SHA256 and exact canonical JSON rule; independent portable verifier follows on audit branch. Extraction helper records original local source locations and is recovery-session specific.
Decision: preserve recovered input before analysis. Risk: full six-plane FDFLT01 NPZ files remain distinct from recovered X/endpoint core; cannot assert byte identity to full originals. Historical TBRT02 3-triplet reconstruction is not an independent-seed replication.
Handoff: push this recovery branch; then independently recompute existing data on astra/edl-flagship-audit-01. No scheduled-run lock: this is a manual audit, not an automation.
''',encoding='utf-8')
with (R/'docs/RUN_INDEX.md').open('a',encoding='utf-8') as f:f.write('\n| EDL-ASTRA-FLAGSHIP-AUDIT-01-RECOVERY | 2026-09-05 | isolated source recovery | 123 sealed TBRT02 archives and 192 FDFLT01 core archives | NO_NEW_WORLDS | see audit/edl-flagship-01/recovery |\n')
print(json.dumps({'TBRT02':len(raw),'FDFLT01':len(list(dest.glob('*.npz'))),'methods':digest,'sidecar':len(sums),'bytes':sum(p.stat().st_size for p in O.rglob('*') if p.is_file())}))
