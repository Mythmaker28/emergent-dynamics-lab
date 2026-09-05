from pathlib import Path
import json
base=Path('C:/Users/tommy/Documents/edl-astra-flagship-recovery-staging')
rows=[]
for name in (base/'bundle_candidates.txt').read_text(encoding='utf-8-sig').splitlines():
    p=Path(name)
    try:
        with p.open('rb') as f:
            lines=[]
            for _ in range(1000):
                line=f.readline()
                if line==b'\n':break
                lines.append(line.decode('utf-8',errors='replace').strip())
        rows.append(dict(path=name,bytes=p.stat().st_size,header=lines))
    except OSError as e:rows.append(dict(path=name,error=str(e)))
(base/'BUNDLE_SEARCH.json').write_text(json.dumps(rows,indent=2)+'\n')
found=[r for r in rows if 'recovery/edl-state-20260904' in str(r) or 'b391a739' in str(r)]
print('Bundle headers checked:',len(rows),'matching announced recovery:',len(found))
for r in found:print(json.dumps(r))
