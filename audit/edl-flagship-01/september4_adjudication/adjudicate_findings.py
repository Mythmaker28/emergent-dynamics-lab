"""Build the reviewer disposition table; judgments are explicit, not automated science."""
from pathlib import Path
import csv, hashlib, json, re
ROOT=Path(__file__).resolve().parent
S=ROOT.parent/'september4/snapshot'
checker=S/'REVIEW01/out/REVIEW01_CHECKER_RETURN_VERBATIM.md'
text=checker.read_text(encoding='utf-8')
titles=re.findall(r'^### (F\d+) — ([^—]+) — (.+)$',text,re.M)
# A resolved original defect is not certification of the replacement manuscript.
J={
1:('RESOLVED','6c77300','RECOVERY/scripts/','Both verification scripts enter Git before the supplied final bundle. Git history and final presence verified; the first fe6b631 bundle omitted them.'),
2:('RESOLVED','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md:113','The erroneous 9-versus-0 event test is removed. Paired whole-world mortality 11/1/1/28 independently matches 82 raw reads; its two-sided sign p=.00634765625 is descriptive of that endpoint.'),
3:('RESOLVED','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md:336','The empty connectivity record set and need to re-read raw are explicitly stated. Original JSON remains 1186 bytes with no observations. Raw availability is now independently repaired in the parent audit.'),
4:('RESOLVED_WITH_LIMITS','23eb684','DELIVERABLES/RAPPORT_DECISION_EDL_20260904.md:434','Runtime mean89.3809/median85.1/max627.6 and batch proxy10.8514h reproduce. The105.4774h projection is conditional on historical throughput. The power estimate is separately limited; no future guarantee follows.'),
5:('ADDRESSED_NOT_EXHAUSTIVE','c363afd;0fdc550;23eb684','CCRA01/out/CCRA01_PREREGISTRATION.md','CCRA01 was specified and executed on existing data, and two additional raw-data routes are left open. This addresses the omitted route. It does not prove that every possible new experiment lacks value, nor that the replacement ordinal estimand resolves the mechanism.'),
6:('RESOLVED_WITH_SCOPE','23eb684','DELIVERABLES/CLAIM_EVIDENCE_MATRIX.md:C11','The uniqueness claim is withdrawn and a second recorded phenomenon is named. This is correction of an unwarranted superlative, not an exhaustive audit of all possible corroborations.'),
7:('RESOLVED_WITH_SCOPE','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md:84','The title uses suppresses and the text qualifies MERGE availability when only one component is present. The earlier33-pair profile is still cited, not independently reconstructed in this subtask. Current82 raw reads confirm the41-pair occupancy.'),
8:('PARTIAL','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md:237','Observed-effect power, uncertainty, and historical design assumptions are now disclosed. But no bootstrap script/RNG/output is supplied; monotone-of-one-p and compatible-truth probabilities overstate the calculation. Non-rejection does not prove the original assumed power false.'),
9:('PARTIAL','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md:302','Prior correlated-outcome exposure is disclosed. The unconditional claim that selection cannot inflate type-I error is not demonstrated; fixed-test arithmetic and selection-valid inference differ. The CCRA specifier blinding is declared, not independently logged.'),
10:('RESOLVED','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md:121','The paired four-cell mortality table replaces causal shorthand12vs2. Independently recovered indices give11/1/1/28.'),
11:('RESOLVED','23eb684','DELIVERABLES/CLAIM_EVIDENCE_MATRIX.md:A9','Sealed historical byte verification is distinguished from GATE01 missing123; absence is distinguished from mismatch. Parent recovery now supplies the123 originals/reconstructed historical same-seed archives.'),
12:('RESOLVED','23eb684','DELIVERABLES/RAPPORT_DECISION_EDL_20260904.md:236','The32-pair p=.0433 appears alongside its exclusion rule and limitation, matching manuscript disclosure. It is not substituted as confirmatory evidence.'),
13:('RESOLVED_WITH_SCOPE','23eb684','DELIVERABLES/RAPPORT_DECISION_EDL_20260904.md:245','The report now lists accrual, admissibility wording, prior information, integrity gate, inherited clauses, and endpoint correlation. The assertion one endpoint twice is rhetorical; the two variables are highly correlated but not identical.'),
14:('RESOLVED','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md','The four specifically cited phrases were changed. This was a local editorial vocabulary restriction, not an independent scientific objection.'),
15:('RESOLVED','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md:324','The original French token NON_INTERPRETABLES__CONFONDUS_PAR_LA_MORTALITE_DIFFERENTIELLE is preserved; the English translation is prose.'),
16:('RESOLVED_WITH_SCOPE','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md:321','Differential mortality and MERGE suppression now have separate attribution. This is programme-internal priority; no external novelty theorem is established.'),
17:('RESOLVED','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md:26','The33-pair abstract vector names split/merge/extinction explicitly, preventing order confusion with the41-pair vector.'),
18:('RESOLVED','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md:133','The years-apart wording is removed. v0.2 names seed-disjoint campaigns; dates are days apart in recovered metadata.'),
19:('RESOLVED','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md:91','NO_COMPONENT is correctly defined as no Y-occupied cell anywhere in the world; total local extinction is removed.'),
20:('RESOLVED_WITH_LIMITS','23eb684','DELIVERABLES/RAPPORT_DECISION_EDL_20260904.md:441','Observed41/885 and Jeffreys Beta41.5,844.5 quantiles reproduce. Future-accrual variability and cost-yield dependence are not fully propagated; rate quantiles alone are not a predictive success guarantee.'),
21:('RESOLVED','23eb684','DELIVERABLES/CLAIM_EVIDENCE_MATRIX.md:C1','The available classifier line ranges are now identified as the source. The combinatorial argument is directly inspectable without running the engine.'),
22:('RESOLVED_WITH_SCOPE','23eb684','DELIVERABLES/CLAIM_EVIDENCE_MATRIX.md:H','The three omitted source missions are acknowledged. Ten out-bearing missions refers to the original246-file recovery, not the enlarged final tree, which adds CCRA01 and REVIEW01.'),
23:('RESOLVED','23eb684','DELIVERABLES/RAPPORT_DECISION_EDL_20260904.md:95','Cell-count and Y-quanta summaries are distinguished along with their different time/object supports; the false contradiction is removed.'),
24:('PARTIAL','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md:307','The report and matrix print the16 exact states. The manuscript still abbreviates RPP97/RPP98/FIMRCC02 as WITHDRAWN under their recorded strings while claiming verbatim re-emission. Three exact values are absent from that manuscript block.'),
25:('RESOLVED','23eb684','DELIVERABLES/RAPPORT_DECISION_EDL_20260904.md:310','The old mismatched subtitle is superseded by the corrected manuscript title/subtitle; no stronger survival-endpoint label is justified by this edit.'),
26:('RESOLVED_WITH_SCOPE','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md:269','Unsupported rollback cadence is removed, largest ceiling is scoped to recovered records, and the previously unnamed publication is identified. This subtask did not independently evaluate its biology.'),
27:('RESOLVED_WITH_SCOPE','23eb684','DELIVERABLES/MS_EDL_NONEXCHANGEABILITY_v0.2.md:344','Zero technical failures replaces technically flawless. Recomputed versus quoted quantities are itemized, source-table attribution is improved, and33/805 source levels are distinguished.'),
28:('PARTIAL','178b26e;23eb684','RECOVERY/RECOVERY_REPORT_20260904.md:96','The payload3963075-byte correction is made and79-pair.20 is removed. The document still calls4053773 bytes the complete first-commit tree although that number is a manifest scope; direct root-tree byte count is recorded separately below.')
}
rows=[]
for fid,severity,title in titles:
 i=int(fid[1:]);status,commits,evidence,reason=J[i]
 line=next(j for j,s in enumerate(text.splitlines(),1) if s.startswith('### '+fid+' —'))
 rows.append({'finding':fid,'original_severity':severity.strip(),'title':title,
              'author_disposition':'ACCEPTED','independent_disposition':status,
              'correction_commits':commits,'original_evidence':f'REVIEW01/out/REVIEW01_CHECKER_RETURN_VERBATIM.md:{line}',
              'corrected_evidence':evidence,'independent_reasoning':reason})
assert len(rows)==28
with (ROOT/'FINDINGS_28_MATRIX.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
statuses={}
for r in rows:statuses[r['independent_disposition']]=statuses.get(r['independent_disposition'],0)+1
(ROOT/'FINDINGS_DISPOSITION.json').write_text(json.dumps({'count':28,'source_sha256':hashlib.sha256(checker.read_bytes()).hexdigest(),
 'counts':statuses,'first_five':[r for r in rows if int(r['finding'][1:])<=5],
 'scope':'Direct present-file inspection; original report/matrix versions are represented mainly by checker quotations. Preserved manuscript v0.1 can be compared directly. Accepted does not mean corrected or publishable.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(statuses)
