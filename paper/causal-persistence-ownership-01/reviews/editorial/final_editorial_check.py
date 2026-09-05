"""Read-only final editorial artifact checks; only the review JSON is written."""
from pathlib import Path
import csv
import hashlib
import json
import re
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
files = ['MANUSCRIPT.md', 'SUPPLEMENT.md', 'MANUSCRIPT_RESOLVED.md',
         'SUPPLEMENT_RESOLVED.md', 'CLAIM_EVIDENCE_MATRIX.csv', 'results/SUMMARY.json',
         'MANUSCRIPT.pdf', 'SUPPLEMENT.pdf']
hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files}
texts = {p: (ROOT / p).read_text(encoding='utf-8') for p in files if p.endswith('_RESOLVED.md')}
assert all('{{' not in t for t in texts.values())
pdfs = {}
for name in ['MANUSCRIPT', 'SUPPLEMENT']:
    reader = PdfReader(ROOT / (name + '.pdf'))
    extracted = '\n'.join(page.extract_text() or '' for page in reader.pages)
    assert '{{' not in extracted
    assert 'Bengio' in extracted and 'Grandvalet' in extracted
    pdfs[name] = {'pages': len(reader.pages), 'extracted_text_sha256': hashlib.sha256(extracted.encode()).hexdigest(),
                  'reference_numbers': sorted(set(re.findall(r'^\[(\d+)\]', extracted, re.M)))}
    assert pdfs[name]['reference_numbers'] == [str(i) for i in range(1, 9)]
claims = list(csv.DictReader((ROOT / 'CLAIM_EVIDENCE_MATRIX.csv').open(encoding='utf-8', newline='')))
assert [r['claim_id'] for r in claims] == [f'C{i:02}' for i in range(1, 26)]
missing_evidence = []
for row in claims:
    for p in row['evidence'].split(';'):
        if not (ROOT / p).exists():
            missing_evidence.append({'claim': row['claim_id'], 'path': p})
result = {'status': 'PASS' if not missing_evidence else 'PENDING_EVIDENCE_PATHS', 'sha256': hashes,
          'pdf_content': pdfs, 'claim_count': len(claims), 'missing_evidence_paths': missing_evidence,
          'scope': 'Editorial text, reference numbering and claim-path checks; not clean full simulation reproduction.'}
(OUT / 'FINAL_EDITORIAL_CHECK.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(result, indent=2))
