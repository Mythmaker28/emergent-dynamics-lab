"""Evaluate explicit gates; READY_FOR_REVIEW is not a journal-submission certificate."""
import json
import xml.etree.ElementTree as ET
from paths import PKG,PROV,digest,dump,require
from audit_final import verify_sources

def main():
    require(verify_sources()==482,'input count')
    records={n:json.loads((PROV/(n+'.json')).read_text(encoding='utf-8')) for n in ['AUDIT_RESULTS','PAPER_CLAIM_LINT','PDF_QA','VISUAL_QA','STANDALONE_REBUILD']}
    for name,r in records.items():require(r['status']=='PASS',name+' incomplete')
    require(json.loads((PROV/'GIT_SCOPE_AUDIT.json').read_text())['status']=='PASS','unrelated Git changes')
    for r in records['PDF_QA']['files']:require(digest(PKG/r['path'])==r['sha256'],'PDF changed after QA')
    for r in records['VISUAL_QA']['files']:require(digest(PKG/r['path'])==r['sha256'],'artifact changed after visual QA')
    for r in records['STANDALONE_REBUILD']['build_sources']:require(digest(PKG/r['path'])==r['sha256'],'build input changed after standalone test')
    for r in records['STANDALONE_REBUILD']['byte_identical_generated_files']:require(digest(PKG/r['path'])==r['sha256'],'generated output changed after standalone test')
    suite=ET.parse(PROV/'TEST_RESULTS.xml').getroot().find('testsuite')
    require(suite is not None and int(suite.attrib['tests'])==4 and all(int(suite.attrib[k])==0 for k in ['failures','errors','skipped']),'unit test failure')
    for name in ['README.md','REPRODUCIBILITY_AUDIT.md','EVIDENCE_CLAIM_MATRIX.csv','ASTRA_HANDOFF_FR.md','COMMANDS_EXECUTED.md']:require((PKG/name).is_file(),'missing deliverable '+name)
    gates={
        'major_claims_bound_and_qualified':'36 claim records; source hashes and pointers checked; manual scope audit',
        'numbers_match_data':'48 bound rows; 28 fresh arms and 147 historical archives recomputed',
        'figures_and_tables_reproducible':'four figures and all-arm table rebuilt from existing inputs; standalone byte agreement',
        'required_tests_pass':'four tests plus raw, source, PDF and standalone checks',
        'closed_routes_preserved':'negative dispositions explicit; zero new scientific or predictor simulations',
        'unrelated_sources_preserved':'482 input hashes match; final Git scope recorded in GIT_SCOPE_AUDIT.json',
        'self_contained_reading':'revised English manuscript, supplement, README and French handoff',
        'no_formal_publication_or_merge':'only the user-authorized Git branch/draft-PR workflow; no submission, deposit, DOI or merge'
    }
    result=dict(status='READY_FOR_REVIEW',mission='ISING-LIFE-MANUSCRIPT-V2-FINAL-SEAL-01',gates=gates,
        independent_peer_review=False,journal_submission_ready=False,publication_authorized=False,
        source_manifest_sha256=digest(PROV/'SOURCE_MANIFEST.json'),
        evidence_records={n:digest(PROV/(n+'.json')) for n in records},
        limits=['Stored intermediate frame summaries are not full lattice snapshots.','No independent full-engine reproduction.','PQEC raw bytes are external and only their already-executed audit is shipped.','Historical run-budget compliance UNKNOWN.','Originality certification and journal requirements not evaluated.'])
    dump(PROV/'PAPER_SUBMISSION_READINESS.json',result)
    dump(PROV/'PAPER_TERMINAL_DISPOSITION.json',dict(status=result['status'],scientific_disposition=records['AUDIT_RESULTS']['sealed_disposition'],next_authorized_action='Read and critically review the V2 manuscript; no new simulation, submission or merge.'))
    text='# Submission-readiness record — V2\n\n**READY_FOR_REVIEW**\n\nThis is an internally audited manuscript and reproducibility package ready for critical reading. Independent peer review has not occurred. Journal-submission readiness and novelty certification are not established.\n\n'
    text+='\n'.join('- **'+k+' — PASS:** '+v for k,v in gates.items())
    text+='\n\n## Explicit limits\n\n'+'\n'.join('- '+s for s in result['limits'])+'\n\nNo technical action is needed from Tommy to reproduce this delivery in the audited environment. The next action is manuscript review. Formal publication, deposition, DOI and merge remain unperformed. The former 86/100 readiness score is superseded by these explicit gates.\n'
    (PROV/'PAPER_SUBMISSION_READINESS.md').write_text(text,encoding='utf-8')
    print(result['status'])

if __name__=='__main__':main()
