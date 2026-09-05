"""Generate reviewable provenance gap matrix from verified source inventory."""
import csv,collections
from common import *
def main():
 rows=[]
 def row(item,status,source,unit,verification,limit):rows.append(dict(item=item,status=status,source=source,unit=unit,verification=verification,remaining_limit=limit))
 row('Claude Sept-4 recovery bundle','VERIFIED_COMPLETE_GIT_BUNDLE','september4/EDL_RECOVERY_20260904.bundle; SHA256 8c43b31d9311fa2cb51bab9fd055c1286eafe0b091d96bcd3ec0e106d934d46f','263 final snapshot files','git bundle verify; b391a739; exact blob manifest; eight commits inspected','Recorded history verifies order, not actual outcome blinding')
 row('TBRT02 raw','VERIFIED_SEALED_BYTES','recovery/TBRT02_raw; original Documents/ising v3/TBRT02/TRIPLE_*.tar','123 NPZ / 41 triples','123 hashes match sealed ledger; content checks pass','9 files at indices 793 827 866 historically reconstructed from same seeds; not independent replication')
 row('FDFLT01 endpoint core','VERIFIED_FROM_RAW_CORE','recovery/FDFLT01_core; original ISING_LIFE_AUTHORITATIVE_RECOVERY/FDFLT01/rawcore/FDFLT01_RAW_CORE.tar.zst','192 worlds / 1291322 recorded rows','53 successes; cell/event reconstruction; 5184 field comparisons all match','Five non-X intermediate field planes absent; operational two-centre endpoint only')
 row('FDFLT01 full original NPZ','FULL_PACKAGE_NOT_RECOVERED','FDFLT01/out/FDFLT01_RAW_MANIFEST.json','192 full NPZ / 1166057316 bytes','Manifest available; not byte identity to core','Full-array manifest cannot be used as hash of reduced core')
 row('FDFLT01 methods capsule','VERIFIED_WITH_DOCUMENTARY_DISCREPANCY','recovery/capsules/fdflt-methods; FDFLT01/out/FDFLT01_METHODS_MANIFEST.json','20 modules + 8 inputs','28 hashes and methods digest pass','Durability JSON outer capsule hash disagrees with actual bytes and sidecar')
 row('OMLDCT03','VERIFIED_SAME_DATA_OUTSIDE_ACCRUAL','results/OMLDCT03_INDEPENDENT.json','41 paired original worlds','492 endpoint comparisons and 12 statistics match','ERRATUM: 512 two-arm ceiling crossed at index 789 with 38 pairs; 12 pre-fork triggers excluded from continuation cost; CI index error; competing terminations')
 row('TBRT02 connectivity exposure','PRESENT_WITH_ZERO_OBSERVATIONS','TBRT02/out/TBRT02_CONNECTIVITY_EXPOSURE.json','1186 bytes / 0 records','7 sidecar hashes pass','No connectivity observations support an exposure claim')
 row('Candidate B','VERIFIED_CORE_RESULTS','candidate_b/SNAPSHOT_MANIFEST.json; results/CANDIDATE_B_INDEPENDENT.json','50 primary / 21 valid worlds','191 source hashes; 50 raw hashes; 03M rerun plus new causal/ridge implementation','Engineered passive copy; finite scopes; no proof of absent ownership; no external validation')
 row('Candidate A / PR34','VERIFIED_PRIOR_PHASE_SAME_CONVERSATION','22ce04d50f2b3ab25b39cbdc1ec5c3c89570e3c6','28 arms plus historical inputs','Earlier complete V2 audit retained; current pinned source read','Conditional point compatibility; baseline also passes; no new A reanalysis here')
 for item,status,limit in [
  ('CCRA01 specification and blinding','ORDER_VERIFIED_BLINDING_UNKNOWN','Separate pre-result commit; blinding declaration not independently verified'),
  ('CCRA01 raw classifications','RECOMPUTED_SAME_DATA','17 losses 24 wins zero ties; 30 of 41 decided by duration'),
  ('CCRA01 capability 5/5','ANALYTIC_IMPLEMENTATION_TESTS_PASS','Does not establish scientific power or privileged endpoint'),
  ('CCRA01 12h / 105h power','ORIGINAL_POWER_NOT_REPRODUCIBLE_DIAGNOSTIC_PROVIDED','Original code and RNG missing; new specified OMLDCT diagnostic not power of CCRA'),
  ('28 Sept-4 checker findings','INDIVIDUALLY_ADJUDICATED','14 resolved, 9 scoped, F5 nonexhaustive, F8/F9/F24/F28 partial in historical C'),
  ('Five Sept-4 fatal findings resolution','FOUR_CORRECTED_FIFTH_SCOPED','Routes addressed; no exhaustive no-experiment conclusion')]:
  row(item,status,'september4_adjudication/SEPTEMBER4_ADJUDICATION_FR.md','41 paired worlds / historical documents','Raw recomputation, differential replay, commit-by-commit matrix',limit)
 row('Historical missing mission inventory','SOURCE_SCOPE_DOCUMENTED','september4/snapshot/RECOVERY; SOURCE_VERIFICATION.json','Separate recovery snapshots','Exact snapshot manifest and historical recovery claims inspected','Historical full tree versus payload counts differ; see F28')
 for m in read(OUT/'SOURCE_VERIFICATION.json')['inventory']:
  row(m['mission']+' outputs','PRESENT_IN_RECOVERED_GIT','5372fd86:'+m['mission']+'/out',str(m['output_files'])+' files','Git tree inventory; complete paths in SOURCE_VERIFICATION.json','Presence does not verify every scientific conclusion or identify Claude missing subset')
 with (HERE/'DATA_PROVENANCE_GAP_MATRIX.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 B=HERE/'candidate_b/results/LCI-TURNOVER-PROSPECTIVE-03G';manifest=read(B/'raw_manifest_03g.json');invalid=[]
 for e in manifest['entries']:
  r=read(B/e['path'])
  if not r['feasibility']['valid']:invalid.append({'seed':r['seed'],**r['feasibility']})
 save('CANDIDATE_B_INVALIDITY.json',{'invalid':invalid,'counts':dict(collections.Counter(x['reason'] for x in invalid))})
 print('provenance matrix rows',len(rows),'invalid B worlds',len(invalid))
if __name__=='__main__':main()
