#!/usr/bin/env python3
"""Builds PROVENANCE_LEDGER.csv / .md for the CONFIRM-02 deposit.

Rows are declared here; SHA-256 values are recomputed from the deposit copies at run time so the
ledger cannot silently drift from the files it describes. Status vocabulary:
  VERIFIED  = traced to an exact repository artefact (NOT "independently reproduced")
  NOT_FOUND = no exact source exists; value omitted or explicitly qualified
  DIFFERS   = an exact source exists and disagrees with the asserted value
"""
import csv, hashlib, json, os, sys

D = os.path.dirname(os.path.abspath(__file__)) + "/.."
def sha(rel):
    h = hashlib.sha256()
    with open(os.path.join(D, rel), "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()

# repo path -> (deposit copy, source commit)
SRC = {
 "docs/individuation/NONMERGING_CONFIRM_PRESEAL_02.json":      ("sources/docs/NONMERGING_CONFIRM_PRESEAL_02.json", "9b7580bc"),
 "docs/individuation/NONMERGING_CONFIRM_PROTOCOL_02.md":       ("sources/docs/NONMERGING_CONFIRM_PROTOCOL_02.md", "9b7580bc"),
 "docs/individuation/NONMERGING_CONFIRM_POWER_02.md":          ("sources/docs/NONMERGING_CONFIRM_POWER_02.md", "9b7580bc"),
 "docs/individuation/NONMERGING_CONFIRM_DETERMINISM_02.md":    ("sources/docs/NONMERGING_CONFIRM_DETERMINISM_02.md", "9b7580bc"),
 "docs/individuation/NONMERGING_CONFIRM_INDEPENDENT_VIEW.md":  ("sources/docs/NONMERGING_CONFIRM_INDEPENDENT_VIEW.md", "9b7580bc"),
 "docs/individuation/NONMERGING_CONFIRM_CERTIFICATE_02.json":  ("sources/docs/NONMERGING_CONFIRM_CERTIFICATE_02.json", "830c2d0"),
 "docs/individuation/NONMERGING_CONFIRM_VERDICT_02.md":        ("sources/docs/NONMERGING_CONFIRM_VERDICT_02.md", "830c2d0"),
 "docs/individuation/NONMERGING_CONFIRM_FIGURE_02.png":        ("sources/docs/NONMERGING_CONFIRM_FIGURE_02.png", "830c2d0"),
 "docs/individuation/NONMERGING_CONFIRM_RSTAR_SENSITIVITY_02.json": ("sources/docs/NONMERGING_CONFIRM_RSTAR_SENSITIVITY_02.json", "9c8a62c"),
 "docs/individuation/NONMERGING_CONFIRM_RSTAR_SENSITIVITY_02.md":   ("sources/docs/NONMERGING_CONFIRM_RSTAR_SENSITIVITY_02.md", "9c8a62c"),
 "docs/individuation/CLAIM_IMPACT_TABLE.md":                   ("sources/docs/CLAIM_IMPACT_TABLE.md", "6470513"),
 "docs/individuation/MERGE_INCIDENT_INDEPENDENT_VIEW.md":      ("sources/docs/MERGE_INCIDENT_INDEPENDENT_VIEW.md", "6470513"),
 "experiments/individuation/nonmerging_confirm.py":            ("sources/experiments/nonmerging_confirm.py", "9b7580bc"),
 "experiments/individuation/nonmerging_analyze.py":            ("sources/experiments/nonmerging_analyze.py", "9b7580bc"),
 "experiments/individuation/nonmerging_confirm_raw.json":      ("sources/experiments/nonmerging_confirm_raw.json", "830c2d0"),
 "experiments/individuation/bijective_tracker.py":             ("sources/experiments/bijective_tracker.py", "6470513"),
 "experiments/individuation/test_bijective_tracker.py":        ("sources/experiments/test_bijective_tracker.py", "6470513"),
 "experiments/individuation/geom_char.py":                     ("sources/experiments/geom_char.py", "9b7580bc"),
 "experiments/individuation/power_explore.py":                 ("sources/experiments/power_explore.py", "9b7580bc"),
 "experiments/individuation/dev_rstar_sensitivity.py":         ("sources/experiments/dev_rstar_sensitivity.py", "9c8a62c"),
 "edlab/experiments/sc_mcm/engine.py":                         ("sources/engine/sc_mcm_engine.py", "65582d0"),
 "edlab/experiments/sc_mcm/config.py":                         ("sources/engine/sc_mcm_config.py", "65582d0"),
 "AUTHOR_AUTHORISATION_02.md":                                 ("AUTHOR_AUTHORISATION_02.md", "author-declaration-2026-08-08"),
 "release/LICENSE-CODE":                                       ("sources/release/LICENSE-CODE", "4dfb73e+author-patch-2026-08-08"),
 "release/LICENSE-DATA-TEXT":                                  ("sources/release/LICENSE-DATA-TEXT", "4dfb73e+author-patch-2026-08-08"),
 "release/AUTHORS.md":                                         ("sources/release/AUTHORS.md", "4dfb73e+author-patch-2026-08-08"),
 "release/CITATION.cff":                                       ("sources/release/CITATION.cff", "23b53ae+author-patch-2026-08-08"),
 "verification/RECOMPUTED_CERTIFICATE_02.json":                ("verification/RECOMPUTED_CERTIFICATE_02.json", "(this deposit pass, not committed)"),
 "verification/certificate_diff.txt":                          ("verification/certificate_diff.txt", "(this deposit pass, not committed)"),
}

ROWS = []
def R(rid, symbol, value, path, locator, mode, status, note=""):
    dep, commit = SRC[path]
    ROWS.append(dict(id=rid, symbol=symbol, value=value, source_path=path, source_commit=commit,
                     source_sha256=sha(dep), locator=locator, verification_mode=mode,
                     status=status, note=note))
def RX(rid, symbol, value, path, commit, locator, mode, status, note=""):
    ROWS.append(dict(id=rid, symbol=symbol, value=value, source_path=path, source_commit=commit,
                     source_sha256="(n/a)", locator=locator, verification_mode=mode,
                     status=status, note=note))

P = "docs/individuation/NONMERGING_CONFIRM_PRESEAL_02.json"
C = "docs/individuation/NONMERGING_CONFIRM_CERTIFICATE_02.json"
A = "docs/individuation/NONMERGING_CONFIRM_RSTAR_SENSITIVITY_02.json"
W = "experiments/individuation/nonmerging_confirm_raw.json"
V = "docs/individuation/NONMERGING_CONFIRM_VERDICT_02.md"
KEY = "json-key lookup"
REC = "recomputation from committed raw record"
TXT = "document text locator"
CODE = "source-code line"

# ---- A. FROZEN PROSPECTIVE DESIGN (PRESEAL 9b7580bc) ----
R("D01","probe amplitude per step (STIM_AMP)","0.25",P,"$.probe.amp_per_step (= $.frozen_constants.STIM_AMP)",KEY,"VERIFIED")
R("D02","probe duration (STIM_DUR)","5 steps",P,"$.probe.n_steps (= $.frozen_constants.STIM_DUR)",KEY,"VERIFIED")
R("D03","cumulative injection","1.25 x N0",P,"$.probe.cumulative_injection_x_N0",KEY,"VERIFIED")
R("D04","behavioural horizon (HORIZON)","40 steps",P,"$.frozen_constants.HORIZON",KEY,"VERIFIED")
R("D05","targets per world (K)","3",P,"$.frozen_constants.K",KEY,"VERIFIED")
R("D06","fusion cap (COVER_CAP)","0.15 of grid",P,"$.frozen_constants.COVER_CAP",KEY,"VERIFIED")
R("D07","N-standardisation settle (SETTLE_STD)","40 steps",P,"$.frozen_constants.SETTLE_STD",KEY,"VERIFIED")
R("D08","warm-up (WARM)","800 steps",P,"$.frozen_constants.WARM",KEY,"VERIFIED")
R("D09","min target size / min pair separation","MINSIZE 45 / SEP 24.0",P,"$.frozen_constants.MINSIZE, $.frozen_constants.SEP",KEY,"VERIFIED")
R("D10","memory->uptake coupling constant (lambda_plus)","0.25",P,"$.frozen_constants.LAM_PLUS",KEY,"VERIFIED")
R("D11","memory->attractant coupling (lambda_minus)","0.15",P,"$.frozen_constants.LAM_MINUS",KEY,"VERIFIED")
R("D12","feasibility floor MIN_VALID_WORLDS","12",P,"$.feasibility_thresholds.MIN_VALID_WORLDS",KEY,"VERIFIED")
R("D13","feasibility floor MIN_NONFUSING_FRACTION","0.85",P,"$.feasibility_thresholds.MIN_NONFUSING_FRACTION",KEY,"VERIFIED")
R("D14","storage gate DD_MIN","10.0",P,"$.gate_thresholds.DD_MIN",KEY,"VERIFIED")
R("D15","storage gate OFF_MAX","0.05",P,"$.gate_thresholds.OFF_MAX",KEY,"VERIFIED")
R("D16","ablation manipulation-check bound ABL_RATIO_MAX","0.15",P,"$.gate_thresholds.ABL_RATIO_MAX",KEY,"VERIFIED")
R("D17","sealed seed family","53001-53032 (32 seeds, cap 32)",P,"$.seeds.FAMILY_SEALED, $.seeds.cap",KEY,"VERIFIED")
R("D18","bootstrap / null seed","20260715",P,"$.determinism_seed",KEY,"VERIFIED")
R("D19","sealed platform","Python 3.11.15 / NumPy 2.2.6 / SciPy 1.15.3 / Matplotlib 3.10.9",P,"$.environment.python|numpy|scipy|matplotlib",KEY,"VERIFIED")
R("D20","coupling statement (shorthand)","uptake proportional to N*rho*(1 + lambda_plus*m_plus)",P,"$.behavioural.coupling_note",KEY,"VERIFIED","Prompt-supplied formula matches the sealed artefact verbatim in shorthand form.")
R("D21","DEV power estimate own @H40 mean","+0.218",P,"$.power.own_H40.mean",KEY,"VERIFIED","DEV only; no positive claim drawn from DEV.")
R("D22","DEV power estimate own @H40 sd","0.063",P,"$.power.own_H40.sd",KEY,"VERIFIED","DEV only.")
R("D23","required valid worlds (need_n)","0.7",P,"$.power.own_H40.need_n",KEY,"VERIFIED","12-world floor is ~17x this.")
R("D24","DEV determinism run sha256","a45a860e0a8418e72f7fe904001e971556ac420e34914a6f243a18523dac6edb",P,"$.dev_determinism.nm_dev_run1_sha256",KEY,"VERIFIED","Also stated in NONMERGING_CONFIRM_DETERMINISM_02.md.")
R("D25","primary readout definition","integrated uptake t=1..40 on the bijectively tracked component",P,"$.behavioural.primary_readout, $.behavioural.readout_moment",KEY,"VERIFIED")
R("D26","transplant control","REMOVED from the mission at seal time (never run)",P,"$.transplant",KEY,"VERIFIED")

# ---- B. ENGINE / MODEL ----
R("E01","exact uptake update","g = dt*g0*rho*N*qq*(1+beta*sigma)*(1+lam_plus*m_plus)","edlab/experiments/sc_mcm/engine.py","line 79",CODE,"VERIFIED")
R("E02","engine default lam_plus / lam_minus","0.25 / 0.15","edlab/experiments/sc_mcm/engine.py","lines 31-32 (MCParams)",CODE,"VERIFIED")
R("E03","m_plus definition","m_plus = tanh(m[0] + m[1])","edlab/experiments/sc_mcm/engine.py","line 76",CODE,"VERIFIED")
R("E04","coupling statement in runner docstring","g proportional to N*rho*(1+lam_plus*m_plus)","experiments/individuation/nonmerging_confirm.py","module docstring, line 15",TXT,"VERIFIED")
RX("E05","grid size","64 x 64 = 4096 cells","edlab/substrates/scaffold/engine.py","659b2b7","line 26: 'size: int = 64'",CODE,"VERIFIED","Consistent with every max_cov value in the certificate being an exact multiple of 1/4096.")

# ---- C. RESULTS (CERTIFICATE 830c2d0; family run once) ----
R("R01","seeds run (n_seeds)","32",C,"$.n_seeds",KEY,"VERIFIED")
R("R02","eligible worlds (n_eligible)","23",C,"$.n_eligible",KEY,"VERIFIED","23/32 = 71.9%; VERDICT_02 rounds to 72%.")
R("R03","G0-valid worlds (n_g0_valid)","23",C,"$.n_g0_valid",KEY,"VERIFIED")
R("R04","non-fusing fraction of eligible","1.0",C,"$.nonfusing_fraction (= $.G0.nonfusing_fraction)",KEY,"VERIFIED")
R("R05","G0 feasibility gate","PASS",C,"$.G0.passed",KEY,"VERIFIED")
R("R06","own effect mean","+0.2236416257421648",C,"$.G3.own_mean",KEY,"VERIFIED","Units: integrated-uptake difference, dimensionless model units. NOT a percentage.")
R("R07","own effect world-bootstrap 2.5th pct","+0.19258340353198225",C,"$.G3.own_worldCI[0]",KEY,"VERIFIED")
R("R08","own effect world-bootstrap median","+0.2232705006888931",C,"$.G3.own_worldCI[1]",KEY,"VERIFIED")
R("R09","own effect world-bootstrap 97.5th pct","+0.25834348856712364",C,"$.G3.own_worldCI[2]",KEY,"VERIFIED")
R("R10","worlds with own effect > 0","23 of 23",C,"$.G3.worlds_own_pos, $.G3.nW",KEY,"VERIFIED")
R("R11","own - sham world-bootstrap lower bound","+0.19258340936897145",C,"$.G3.own_sham_worldCI[0]",KEY,"VERIFIED")
R("R12","own - neighbour world-bootstrap lower bound","+0.19258547407545254",C,"$.G3.own_neigh_worldCI[0] (= $.G4.own_neigh_worldCI[0])",KEY,"VERIFIED")
R("R13","sham contrast mean","-6.777303240351992e-09",C,"$.G3.sham_mean",KEY,"VERIFIED")
R("R14","neighbour contrast mean","-7.316792126109839e-06",C,"$.G3.neigh_mean (= $.G4.neigh_mean)",KEY,"VERIFIED")
R("R15","ablation contrast mean","0.0 (exactly)",C,"$.G3.ablation_mean",KEY,"VERIFIED","Manipulation check on a channel coupled by construction; NOT independent evidence.")
R("R16","ablation ratio |own_abl|/|own|","0.0",C,"$.G3.ablation_ratio",KEY,"VERIFIED","Frozen bound was < 0.15.")
R("R17","fixed-mask (tracker-free) effect mean","+0.20679489102504786",C,"$.G3.own_fixed_mean",KEY,"VERIFIED")
R("R18","fixed-mask world-bootstrap CI","[+0.1799347054467802, +0.23438471691982812]",C,"$.G5.own_fixed_worldCI[0], [2]",KEY,"VERIFIED")
R("R19","worlds with same sign tracked vs fixed","23 of 23",C,"$.G5.same_sign_worlds",KEY,"VERIFIED")
R("R20","tracked / fixed ratio","1.0814659135610676",C,"$.G5.tracked_over_fixed",KEY,"VERIFIED","Contrast with 4.80x under the earlier fused regime (row P01).")
R("R21","storage discriminability DD_mem","2590.0484470532206",C,"$.G1.DD_mem",KEY,"VERIFIED","Gate: >= 10.")
R("R22","storage mean |off-diagonal|","7.030993427940622e-05",C,"$.G1.off",KEY,"VERIFIED","Gate: < 0.05.")
R("R23","storage mean |diagonal|","0.18686203237973162",C,"$.G1.diag",KEY,"VERIFIED")
R("R24","dose decode R2","0.6908517710812216",C,"$.G2.dose_R2",KEY,"VERIFIED")
R("R25","dose within-null 95th percentile","0.15306406118017543",C,"$.G2.dose_null95",KEY,"VERIFIED")
R("R26","dose empirical p","0.0001999600079984003",C,"$.G2.dose_p",KEY,"VERIFIED")
R("R27","neighbour dose R2 (quoted as -0.014)","-0.014",C,"$.G2.neighbour_dose_R2",KEY,"VERIFIED","Quoted at 3 dp; full 16-digit value is ULP-unstable, see row X03.")
R("R28","order decode R2 (quoted as 0.376)","0.376",C,"$.G2.order_R2",KEY,"VERIFIED","Secondary, pre-declared. Quoted at 3 dp; see row X04.")
R("R29","order within-null 95th percentile (quoted as 0.106)","0.106",C,"$.G2.order_null95",KEY,"VERIFIED","See row X05.")
R("R30","order empirical p","0.0001999600079984003",C,"$.G2.order_p",KEY,"VERIFIED")
R("R31","dose bootstrap CI (quoted as [0.581, 0.824])","[0.581, 0.824]",C,"$.G2.dose_ci[0], [1]",KEY,"VERIFIED","Quoted at 3 dp; see rows X01, X02.")
R("R32","max grid coverage across valid worlds","1.1963% (seed 53032) to 5.6396% (seed 53010)",C,"$.per_seed[*].max_cov, min and max",KEY,"VERIFIED","Cap was 15%.")
R("R33","G6 composite gate","PASS",C,"$.G6.passed, $.G6.rule",KEY,"VERIFIED")
R("R34","droplet-targets analysed","69 (= 23 valid worlds x K=3)",W,"count over records with eligible=true and g0_valid=true, 3 targets each",REC,"VERIFIED","NESTED within 23 worlds; NOT 69 independent replications.")
R("R35","droplet-targets with own effect > 0","69 of 69",W,"beh.intact.tracked[i] - beh.erase[i].tracked[i], i=0..2, over the 23 valid records",REC,"VERIFIED","Also asserted in VERDICT_02 ('69/69 gouttelettes >0'). Descriptive only.")
R("R36","per-target own effect range","+0.029821403845065042 to +0.9021677835548552",W,"same locator as R35, min and max",REC,"VERIFIED")
R("R37","world-level corr(dose, own effect)","+0.173795 (VERDICT_02 quotes +0.17)",W,"corrcoef(mean(dose) per valid world, own effect per valid world)",REC,"VERIFIED","Graded decode is INDETERMINATE and non-gating.")
R("R38","eligibility rate","23/32 = 71.9%",C,"$.n_eligible / $.n_seeds",KEY,"VERIFIED","Geometric and outcome-independent.")

# ---- D. POST HOC ADDENDUM (9c8a62c) — NOT part of the frozen design ----
R("A01","sealed probe amplitude (addendum arm)","0.25",A,"$['seal_0.25x5'].amp",KEY,"VERIFIED")
R("A02","sealed probe cumulative injection","1.25",A,"$['seal_0.25x5'].cum",KEY,"VERIFIED")
R("A03","R* probe amplitude","0.2575",A,"$['rstar_0.2575x5'].amp",KEY,"VERIFIED","POST HOC.")
R("A04","R* cumulative injection","1.2875",A,"$['rstar_0.2575x5'].cum",KEY,"VERIFIED","POST HOC.")
R("A05","sealed probe worst coverage @H40","0.033203125 (3.3203%)",A,"$['seal_0.25x5'].worst_cov_H40",KEY,"VERIFIED","POST HOC.")
R("A06","R* probe worst coverage @H40","0.033447265625 (3.3447%)",A,"$['rstar_0.2575x5'].worst_cov_H40",KEY,"VERIFIED","POST HOC.")
R("A07","worst-coverage delta @H40","0.0244140625 percentage points",A,"$.worst_cov_delta_H40_pct",KEY,"VERIFIED","POST HOC. Reported as '+0.02 pp'.")
R("A08","DEV worlds in the addendum","8 per arm",A,"$['seal_0.25x5'].nW, $['rstar_0.2575x5'].nW",KEY,"VERIFIED","POST HOC. DEV seeds 50001-50009; no 53xxx seed used.")
R("A09","G0-valid @H40 per arm","8 of 8 (both arms)",A,"$['seal_0.25x5'].worlds_G0valid_H40, $['rstar_0.2575x5'].worlds_G0valid_H40",KEY,"VERIFIED","POST HOC.")
R("A10","both probes pass geometry","true",A,"$.both_pass",KEY,"VERIFIED","POST HOC. Decision: keep sealed 0.25x5.")
R("A11","anti-numerology outcome for R*","fails criteria 3,4,5,6; criteria 1,2 non-discriminating","docs/individuation/NONMERGING_CONFIRM_RSTAR_SENSITIVITY_02.md","section 2, criteria list; section 3 decision",TXT,"VERIFIED","POST HOC. Conclusion: R* has NO independent theoretical derivation.")

# ---- E. PRIOR-LINEAGE CONTEXT (superseded / invalidated values) ----
R("P01","tracker inflation factor under fusion","4.80x","docs/individuation/MERGE_INCIDENT_INDEPENDENT_VIEW.md","table row 'Facteur d'inflation tracke / masque-fixe', line 34",TXT,"VERIFIED","Prior incident, not this run. Quoted only as contrast.")
R("P02","prior own effect (superseded)","+2.03","docs/individuation/CLAIM_IMPACT_TABLE.md","line 23",TXT,"VERIFIED","Superseded/qualified by the merge-incident erratum. NOT a claim of this work.")
R("P03","prior '39/39 droplets' claim","INVALIDATED as 39 distinct entities; 24 unique final components; 17/39 survive under a bijective tracker","docs/individuation/CLAIM_IMPACT_TABLE.md","claim row 6, lines 20 and 37",TXT,"VERIFIED","Cited as the error this work avoids.")
R("P04","prior fusion incidence","11/13 worlds fused into a giant component covering 36-52% of the grid","docs/individuation/CLAIM_IMPACT_TABLE.md","claim row 5, line 36",TXT,"VERIFIED","Motivates the non-fusing re-run.")

# ---- F. SEAL INTEGRITY: PRESEAL sealed_file_sha256 re-hashed against the committed content ----
pres = json.load(open(os.path.join(D, SRC[P][0])))
LOC = {"experiments/individuation/nonmerging_confirm.py": "sources/experiments/nonmerging_confirm.py",
       "experiments/individuation/nonmerging_analyze.py": "sources/experiments/nonmerging_analyze.py",
       "experiments/individuation/bijective_tracker.py": "sources/experiments/bijective_tracker.py",
       "experiments/individuation/test_bijective_tracker.py": "sources/experiments/test_bijective_tracker.py",
       "experiments/individuation/geom_char.py": "sources/experiments/geom_char.py",
       "experiments/individuation/power_explore.py": "sources/experiments/power_explore.py",
       "docs/individuation/NONMERGING_CONFIRM_PROTOCOL_02.md": "sources/docs/NONMERGING_CONFIRM_PROTOCOL_02.md",
       "docs/individuation/NONMERGING_CONFIRM_INDEPENDENT_VIEW.md": "sources/docs/NONMERGING_CONFIRM_INDEPENDENT_VIEW.md"}
seal_ok = 0
for i, (path, declared) in enumerate(sorted(pres["sealed_file_sha256"].items()), 1):
    actual = sha(LOC[path])
    ok = (actual == declared)
    seal_ok += int(ok)
    ROWS.append(dict(id="SEAL-%02d" % i, symbol="sealed SHA-256 of %s" % path,
                     value=declared, source_path=P, source_commit="9b7580bc", source_sha256=sha(SRC[P][0]),
                     locator="$.sealed_file_sha256['%s']" % path,
                     verification_mode="re-hash of the committed content at branch tip 9c8a62c",
                     status="VERIFIED" if ok else "DIFFERS",
                     note="recomputed = %s" % actual))

# ---- G. REPRODUCTION OF THE ANALYSIS STAGE (this deposit pass) ----
R("V01","analysis-stage re-run wall clock","33.7 s","verification/RECOMPUTED_CERTIFICATE_02.json",
  "python3 nonmerging_analyze.py nonmerging_confirm_raw.json RECOMPUTED_CERTIFICATE_02.json",
  "re-execution of the committed analysis script on the committed raw record","VERIFIED",
  "Simulation stage NOT re-run (32 seeds x 5 branch families of a chaotic RD-PDE, 800-step warm-up).")
R("V02","gated statistics on re-run","all reproduce exactly (own mean+CI, own-sham, own-neigh, ablation, fixed-mask CI, same-sign, tracked/fixed, DD_mem, off, dose_R2, dose_null95, dose_p, every per_seed row)",
  "verification/certificate_diff.txt","whole-file structural diff vs the committed certificate",
  "byte/structural comparison","VERIFIED")

# DIFFERS rows are derived, not asserted: every leaf that actually disagrees gets its own row.
def leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, p + "." + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, p + "[%d]" % i)
    else:
        yield p, o
cert_c = json.load(open(os.path.join(D, SRC[C][0])))
cert_r = json.load(open(os.path.join(D, SRC["verification/RECOMPUTED_CERTIFICATE_02.json"][0])))
dc, dr = dict(leaves(cert_c)), dict(leaves(cert_r))
n_diff = 0
for k in dc:
    if k in dr and dc[k] != dr[k]:
        n_diff += 1
        rel = abs(dr[k] - dc[k]) / max(abs(dc[k]), 1e-300) if isinstance(dc[k], float) else float("nan")
        ROWS.append(dict(id="X%02d" % n_diff, symbol="full-precision value at %s" % k, value=repr(dc[k]),
                         source_path=C, source_commit="830c2d0", source_sha256=sha(SRC[C][0]),
                         locator="$" + k,
                         verification_mode="re-derivation with the committed analysis script on the committed raw record",
                         status="DIFFERS",
                         note="re-derived = %r; relative difference %.2e (1-3 ULP); non-gating; NOT quoted at this precision in the manuscript" % (dr[k], rel)))

# ---- H. IDENTITY / LICENCE / IDENTIFIERS: nothing invented ----
R("N01","copyright holder","Tommy Lepesteur","release/LICENSE-CODE","line 1: 'Copyright 2026 Tommy Lepesteur'",
  "corresponding author's declaration of record, 2026-08-08, then literal-marker inspection of the patched file","VERIFIED",
  "RESOLVED 2026-08-08. The value originates in the author's declaration, NOT in any pre-existing repository artefact; the artefact was written to match the declaration. Prior state at 4dfb73e was the literal marker.")
R("N02","copyright holder for data/text licence","Tommy Lepesteur","release/LICENSE-DATA-TEXT","line 1: 'Copyright 2026 Tommy Lepesteur'",
  "corresponding author's declaration of record, 2026-08-08, then literal-marker inspection of the patched file","VERIFIED",
  "RESOLVED 2026-08-08. Same declared holder as N01. The CC-BY-4.0 legal code is unchanged; only the holder line and the attribution sentence were added.")
R("N03","author name","Lepesteur, Tommy","release/AUTHORS.md","'Corresponding author' block: 'Tommy Lepesteur'",
  "corresponding author's declaration of record, 2026-08-08","VERIFIED",
  "RESOLVED 2026-08-08. Also written to release/CITATION.cff as family-names: Lepesteur, given-names: Tommy.")
R("N04","author affiliation","NOT_FOUND","release/AUTHORS.md","'Corresponding author' block: 'affiliation: NOT_DECLARED'",
  "literal-marker inspection","NOT_FOUND","STILL UNRESOLVED. The author declared a name only. No affiliation invented.")
R("N05","author ORCID","NOT_FOUND","release/CITATION.cff","authors[0]: 'orcid: NOT_DECLARED' comment, never filled",
  "repository-wide search for an ORCID identifier","NOT_FOUND","No ORCID exists anywhere in the repository; placeholders only. None invented.")
R("N06","DOI","NOT_FOUND","release/CITATION.cff","no DOI field; no DOI minted or reserved anywhere in the repository",
  "repository-wide search","NOT_FOUND","None invented. Nothing has been submitted.")
R("N07","funder / grant","NOT_FOUND","release/AUTHORS.md","no funding section; release/README_RELEASE.md records funding as an unfilled placeholder",
  "repository-wide search","NOT_FOUND","None invented.")
R("N08","related identifiers","NOT_FOUND","release/CITATION.cff","no verified related identifier",
  "repository-wide search","NOT_FOUND","None invented.")
R("N09","author approval of the CC-BY-4.0 / Apache-2.0 licence choice","APPROVED 2026-08-08","release/CITATION.cff","'notes' block: licence split recorded as confirmed by the corresponding author",
  "corresponding author's declaration of record, 2026-08-08","VERIFIED",
  "RESOLVED 2026-08-08. DEPOSIT_METADATA.json now carries a machine-actionable 'license': 'cc-by-4.0' plus a 'license_decision' block. Approving the licence is NOT authorisation to deposit: 'submission_status' remains NOT_SUBMITTED and N06 (DOI) remains NOT_FOUND.")
R("N10","authorisation to deposit on Zenodo","NOT_FOUND","AUTHOR_AUTHORISATION_02.md","'What this authorisation is not': DEPOSIT_AUTHORISED_BY_AUTHOR = false",
  "document text locator","NOT_FOUND","Nothing has been submitted, reserved or published. Deliberately kept as a separate decision from the licence approval.")

# ---- emit ----
FIELDS = ["id","symbol","value","source_path","source_commit","source_sha256","locator","verification_mode","status","note"]
with open(os.path.join(D, "PROVENANCE_LEDGER.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
    for r in ROWS: w.writerow(r)

counts = {s: sum(1 for r in ROWS if r["status"] == s) for s in ("VERIFIED","NOT_FOUND","DIFFERS")}
print("ROWS=%d  VERIFIED=%d  NOT_FOUND=%d  DIFFERS=%d  seal_ok=%d/8"
      % (len(ROWS), counts["VERIFIED"], counts["NOT_FOUND"], counts["DIFFERS"], seal_ok))
json.dump({"rows": len(ROWS), "counts": counts, "seal_manifest_entries": 8, "seal_manifest_matching": seal_ok},
          open(os.path.join(D, "verification/ledger_counts.json"), "w"), indent=2)
