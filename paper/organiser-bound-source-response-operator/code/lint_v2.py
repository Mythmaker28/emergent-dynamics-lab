"""Fail closed on source drift, missing claim bindings or stale numerical macros."""
import csv
import json
import re
from paths import ROOT,PKG,PROV,read,digest,dump,require

def main():
    rows=list(csv.DictReader((PKG/'EVIDENCE_CLAIM_MATRIX.csv').open(encoding='utf-8')))
    require(len(rows)==36,'claim coverage count')
    for r in rows:
        p=ROOT/r['EVIDENCE_FILE'];require(digest(p)==r['SOURCE_SHA256'],'claim source drift '+r['CLAIM_ID'])
        if p.suffix=='.json' and r['JSON_PATH_OR_CODE']:
            v=json.loads(p.read_text(encoding='utf-8'))
            for k in r['JSON_PATH_OR_CODE'].split('/'):
                v=v[int(k)] if isinstance(v,list) else v[k]
    rec=json.loads((PROV/'PAPER_NUMERICAL_RECONCILIATION.json').read_text())
    for r in rec['ROWS']:
        require(digest(ROOT/r['SOURCE_FILE'])==r['SOURCE_SHA256'],'numerical source drift')
        v=read(r['SOURCE_FILE'])
        for k in r['JSON_PATH'].split('/'):v=v[int(k)] if isinstance(v,list) else v[k]
        require(v==r['VALUE'],'numerical value changed')
    text='\n'.join((PKG/p).read_text(encoding='utf-8-sig') for p in ['manuscript/MANUSCRIPT.tex','supplement/SUPPLEMENT.tex'])
    macros=json.loads((PROV/'PAPER_MACRO_INDEX.json').read_text())
    used=set(re.findall(r'\\(V[A-Z][A-Za-z]+)',text));require(used<=set(macros),'undefined numerical macros')
    for old in ['cellMobileMedian','mSixFactorial','freshStaticPredicted','NO_REFIT_AFTER_VIEWING_VALIDATION','no fitted parameter']:
        require(old not in text,'pre-seal claim or macro survived: '+old)
    for needed in ['INDIVIDUATION: FAIL','STOP__ARCHITECTURE_CHANGE_REQUIRED','CONDITIONAL_FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED','NOT TESTED','NOT ESTABLISHED']:
        require(needed in text,'missing scope boundary '+needed)
    bib=(PKG/'bibliography/references.bib').read_text(encoding='utf-8-sig')
    keys=set(re.findall(r'@\w+\{([^,]+),',bib));cites=set()
    for group in re.findall(r'\\cite\w*\{([^}]+)\}',text):cites.update(group.split(','))
    require(keys==cites,'bibliography mismatch')
    figs=json.loads((PROV/'PAPER_FIGURE_PROVENANCE.json').read_text());require(len(figs)==4,'figure count')
    for name,r in figs.items():
        require(digest(PKG/'figures'/(name+'.pdf'))==r['pdf_sha256'],'figure drift')
        require(digest(PKG/'figure_data'/(name+'.json'))==r['data_sha256'],'figure data drift')
    dump(PROV/'PAPER_CLAIM_LINT.json',dict(status='PASS',claim_rows=len(rows),numerical_rows=len(rec['ROWS']),used_numerical_macros=len(used),figures=len(figs),references=len(keys),independent_peer_review=False))
    print('Claim, number, reference and figure lint PASS.')

if __name__=='__main__':main()
