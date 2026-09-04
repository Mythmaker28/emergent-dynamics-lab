"""Explicit V2 editorial claim map, including withdrawn and contextual claims."""
import csv
from paths import ROOT, PKG, PROV, digest

A='paper/organiser-bound-source-response-operator/provenance/AUDIT_RESULTS.json'
S='SEAL01/out/_seal_adjudication.json'
R='SEAL01/out/OBFOR01_SEAL_REPAIR_EVIDENCE.json'
F='OBFOR01/out/_freeze.json'
CTX='paper/organiser-bound-source-response-operator/provenance/context/'
# ID, location, final claim, file, pointer or code function, evidence level, limitation, editorial action
CLAIMS=[
('C01','Abstract; Results 3.1; Discussion','28 fresh arms, 14 per condition; all included',A,'fresh_arms','RAW_RECOMPUTED','One implementation and parameter point; not new V2 runs','RETAIN'),
('C02','Abstract; Methods 2.3; Discussion','Prediction is conditional on measured historical birth-flux law',S,'PREDICTION_MODE','SEALED_INTERPRETATION','Input conditioning remains even when sensitivity is weak','REDUCE_UNCONDITIONAL_CLAIM'),
('C03','Abstract; Results 3.1; Table 1','Static point deviation lies within frozen margin',A,'endpoints/static','RAW_RECOMPUTED','Point-rule success is not pre-registered interval equivalence','RETAIN_WITH_QUALIFICATION'),
('C04','Abstract; Results 3.1; Table 1','Mobile point deviation lies within frozen margin',A,'endpoints/mobile','RAW_RECOMPUTED','Same scope and predictor uncertainty','RETAIN_WITH_QUALIFICATION'),
('C05','Abstract; Results 3.1; Table 1','Ratio point deviation lies within frozen margin',A,'endpoints/ratio','RAW_RECOMPUTED','Disjoint seeds, not paired; diagnostic SE scale corrected','RETAIN_WITH_QUALIFICATION'),
('C06','Methods 2.4; Results 3.1','Pre-run decision used a point tolerance of 2.9 percent',F,'RESIDUAL_TOLERANCE/RULE','FROZEN_PROTOCOL','Not an interval rule or externally timestamped preregistration','CORRECT_PREREGISTRATION_SCOPE'),
('C07','Abstract; Results 3.2; Discussion; Figure 2','Historical-copy baseline passes all three point criteria',R,'R4_DISCRIMINATING_POWER/NULL_SCORED_ON_THE_THREE_FROZEN_ENDPOINTS','POST_OUTCOME_BASELINE_COMPARISON','Baseline evaluation is later; inputs existed earlier','ADD_LIMIT_ON_DISCRIMINATION'),
('C08','Abstract; Results 3.2; Figure 4','No-shared-path frozen variant misses mobile point tolerance',R,'R4_DISCRIMINATING_POWER/WHAT_THE_TEST_DOES_REJECT/the model with the shared trajectory removed','SEALED_COMPARISON_RECOMPUTABLE','Evidence within the examined constructions, not unique mechanism proof','REDUCE_CAUSAL_GENERALIZATION'),
('C09','Results 3.2; Figure 4','Ideal reference misses mobile point tolerance',R,'R4_DISCRIMINATING_POWER/WHAT_THE_TEST_DOES_REJECT/the uncorrected ideal operator','SEALED_COMPARISON_RECOMPUTABLE','Static ideal endpoint passes; no full operator validation','RETAIN_WITH_QUALIFICATION'),
('C10','Abstract; Results 3.3; Discussion','Large birth-flux-shape effect and sign are not sustained',A,'replicates','STORED_PREDICTOR_REPLICAS_RECOMPUTED','16 stored replicas per condition, not fresh engine arms','WITHDRAW_1P27_PP_MECHANISM'),
('C11','Results 3.3; Figure 4','Poisson variant also passes the point criterion','OBFOR01/out/_adjudication.json','ABLATION/predictions','FROZEN_PREDICTIONS_WITH_LATER_COMPARISON','A larger distance ratio does not imply rejection','WITHDRAW_4P5_DISTANCE_AS_REJECTION'),
('C12','Results 3.3','Birth-flux factorial effect and interaction are not supporting mechanisms',R,'R1_BIRTH_FLUX_ABLATION_REPLICATED/CONSEQUENCE','SEALED_WITHDRAWAL','Old numeric decomposition remains in frozen source only','WITHDRAW_FACTORIAL_CLAIM'),
('C13','Abstract; Results 3.4; Discussion; Table 2; Figure 3','Historical residual depends on terminal-population inclusion',A,'historical_levels','RAW_RECOMPUTED_DEVELOPMENTAL','Nested sets; even widest level requires final Y and finite radius','REDUCE_UNCONDITIONAL_HISTORICAL_DEFICIT'),
('C14','Results 3.4','Fresh sample has no historical population-selection filter',A,'fresh_arms','RAW_RECOMPUTED','All declared fresh arms included; no general claim for other experiments','RETAIN'),
('C15','Methods 2.1','Frozen lattice parameters and only source mobility differ',F,'FREEZE_MANIFEST','FROZEN_METHOD','Not a sweep or densely blocked regime','RETAIN'),
('C16','Methods 2.1; Supplement S1','Four sequential directed transport passes, reaction, decay and reservoir exchange','ORR01/code/kinetics.py','World._diffuse; World._one_step','SOURCE_CODE','Sequential passes are not one exclusive hop per step','CORRECT_METHOD_PRECISION'),
('C17','Methods 2.1; Supplement S1','Reservoir uses balanced exchange','ORR01/code/lawspec_v2.py','WorldV2._exchange','SOURCE_CODE','Exact pool and split-feed stream in code','CORRECT_METHOD_PRECISION'),
('C18','Methods 2.2; Supplement S1','Radius about source; arm median then condition mean; 180 post-burn frames','OBFOR01/code/run_obfor01.py','run_arm','FROZEN_METHOD_AND_RAW_CHECK','Intermediate lattice snapshots absent; final radius independently checked','RETAIN_WITH_LIMIT'),
('C19','Methods 2.3; Figure 1','Shared source path is simulated; birth law measured from 40 historical arms','OBFOR01/code/m6_obfor01.py','simulate_arm; empirical_birth_flux','FROZEN_PREDICTOR_SOURCE','No target-derived fresh outcomes enter; not unconditional first principles','CORRECT_INPUT_PROVENANCE'),
('C20','Results 3.1; Discussion; Table 1; Supplement S4','Predictor MC dispersion accompanies point predictions',A,'replicates/stats','STORED_PREDICTOR_REPLICAS_RECOMPUTED','Ratio uses propagated convention, not independent ratio simulation','ADD_UNCERTAINTY'),
('C21','Methods 2.4; Supplement S2','Fourteen load-bearing files match their pre-run Git blobs','paper/organiser-bound-source-response-operator/provenance/GIT_FREEZE_VERIFICATION.json','frozen_files_unchanged','GIT_OBJECT_VERIFIED','Adjudication and interval rules were later; no public timestamp proof','RETAIN_WITH_PRECISE_CHRONOLOGY'),
('C22','Methods 2.4; Discussion; Supplement S4','Whole-interval rules and inferential diagnostics are post-freeze','SEAL01/out/OBFOR01_HEADLINE_RECOMPUTATION.json','FRESH/WHOLE_INTERVAL_CRITERION_PROVENANCE','SEALED_PROVENANCE','Cannot be promoted to pre-registered success','WITHDRAW_FROZEN_INTERVAL_CLAIM'),
('C23','Supplement S4','Small-sample absolute diagnostic p values use t13',A,'endpoints','RAW_RECOMPUTED_POST_FREEZE','Conditional on fixed predictor; no predictor uncertainty integration','CORRECT_NORMAL_TAILS'),
('C24','Supplement S4','Ratio delta SE includes observed/predicted scale',A,'endpoints/ratio','ALGEBRAIC_DIAGNOSTIC_CORRECTION','No change to frozen point decision; old value retained for comparison','CORRECT_SCALE_FACTOR'),
('C25','Methods 2.3; Abstract; Discussion','No closed marginal density or full-state theory established',S,'MAXIMAL_AUTHORIZED_CLAIM','SEALED_SCOPE_LIMIT','Conditional exactness terminology removed from central claim','REDUCE_FULL_OPERATOR_CLAIM'),
('C26','Methods 2.1','Transport blocking is rare at tested point',A,'fresh_arms','RAW_LEDGER_RECOMPUTED','Capacity exists structurally; high-occupancy extrapolation not established','REDUCE_CAPACITY_GENERALIZATION'),
('C27','Related results; Supplement S6','MYQBD01 exposure insufficient for full descendant spatial operator','MYQBD01/out/MYQBD01_FINAL_DISPOSITION.json','FINAL_DISPOSITION','SEALED_CONTEXT_ONLY','Organiser-only first-birth information; not independent confirmation here','RETAIN_NEGATIVE'),
('C28','Related results; Supplement S6','PQEC01 has 128 raw worlds with developmental status','PQEC01/out/PQEC01_RAW_MANIFEST.json','N_ARCHIVES','MANIFEST_PLUS_EXTERNAL_RAW_HASH_AUDIT','Prospective status withdrawn by FLCR01; no raw analysis rerun for its region','RETAIN_NEGATIVE_SCOPE'),
('C29','Related results; Supplement S6','FLCR01 rejects founder necessity but leaves operator unidentified','FLCR01/out/FLCR01_FINAL_DISPOSITION.json','','SEALED_CONTEXT_ONLY','Founder, lineage and functional two-centre criteria are distinct','RETAIN_NEGATIVE'),
('C30','Related results; Supplement S6','IOM retains low-dimensional causal experience memory and INDIVIDUATION FAIL',CTX+'EXP_SC_IOM_00_ERRATUM.md','Correction 1','PINNED_DOCUMENTARY_CONTEXT','Separate architecture; raw simulation not reverified here','RETAIN_FAIL'),
('C31','Related results; Supplement S6','IOM high-dimensional internal variation is not established history storage',CTX+'EXP_SC_IOM_00_ERRATUM.md','Correction 2','PINNED_DOCUMENTARY_CONTEXT','No transfer to source-response results','WITHDRAW_STORAGE_UPGRADE'),
('C32','Abstract; Discussion','Reproduction/heredity not tested; autonomy/individuality not established',S,'NINE_REQUIREMENTS/9_no_reproduction_heredity_or_cohesion_upgrade','EXPLICIT_SCOPE_LIMIT','No biological or living-status inference','RETAIN_LIMIT'),
('C33','Methods 2.5; Data; Supplement S7','V2 uses no new scientific worlds or predictor simulations',A,'scientific_world_starts','EXECUTION_SCOPE','Recomputation is not independent full-engine replication','RETAIN'),
('C34','Data; Supplement S2','Historical run-budget compliance remains unknown',S,'ZERO_RUN_COMPLIANCE/ORIGINAL_ZERO_RUN_MISSION_COMPLIANCE','MISSING_DOCUMENTARY_EVIDENCE','Absence is not a finding of violation','REDUCE_COMPLIANCE_CLAIM'),
('C35','Discussion','No general theorem of downward quantile bias is derived','OBFOR01/out/_residual.json','DEFINITION','EXPLICIT_QUALIFICATION','Observed sign is distribution- and selection-dependent','WITHDRAW_UNIVERSAL_BIAS_CLAIM'),
('C36','Supplement S2','Observer inertness is a historical 1500-step fixture','OBFOR01/out/_validation.json','INERTNESS','HASH_VERIFIED_TEST_RECORD_NOT_RERUN','Does not prove inertness for all trajectories','REDUCE_PROOF_LANGUAGE')]

def main():
    fields=['CLAIM_ID','MANUSCRIPT_LOCATION','FINAL_CLAIM','EVIDENCE_FILE','JSON_PATH_OR_CODE','EVIDENCE_LEVEL','LIMIT_OR_CONTRADICTION','EDITORIAL_ACTION','SOURCE_SHA256','REPRODUCTION']
    with (PKG/'EVIDENCE_CLAIM_MATRIX.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for c in CLAIMS:
            row=dict(zip(fields,c));row['SOURCE_SHA256']=digest(ROOT/c[3]);row['REPRODUCTION']='code/reproduce.py; see REPRODUCIBILITY_AUDIT.md for verified vs documentary scope';w.writerow(row)
    print('Claims:',len(CLAIMS))

if __name__=='__main__':main()
