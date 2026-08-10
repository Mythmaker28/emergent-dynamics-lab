"""SQDT00 independent closure verifier. Reloads the committed-so-far artifacts and asserts the
whole programme is internally consistent. Zero starts."""
from __future__ import annotations
import json, hashlib, math
from fractions import Fraction as Fr
import numpy as np
OUT = "/home/claude/sweep/SQDT00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
fails = []
def ck(name, cond):
    print(("  OK  " if cond else " FAIL ") + name)
    if not cond:
        fails.append(name)

FRZ = json.load(open(f"{OUT}/SQDT00_MASTER_FREEZE_HASHES.json"))
ck("master freeze hash stable", sha(f"{OUT}/SQDT00_MASTER_FREEZE.md") == FRZ["hashes"]["SQDT00_MASTER_FREEZE.md"])

C = json.load(open(f"{OUT}/SQDT00_OFFLINE_REDERIVATION_AND_BASIS_CERTIFICATE.json"))
ck("R0 exact matches parent", C["rederivation_matches_parent"]["R0_exact"])
ck("support sufficiency (sham+active)", C["support_restricted_sufficiency_certificate"]["sham_match"]
   and C["support_restricted_sufficiency_certificate"]["active_match"])
ck("all 8 basis gates pass", all(C["basis_gates"].values()))
ck("P2 license", C["P2_TRANSFER_LICENSE"])
ck("E2 license", C["E2_AXIS_TRANSFER_LICENSE"])
ck("duplication invariance", C["duplication_invariance"]["R0_exact_unchanged"] and C["duplication_invariance"]["I2_unchanged"])
ck("amplitude multiplier < 2", C["certified_multipliers"]["AMPLITUDE_MULTIPLIER_STRICTLY_BELOW_2"])
# enclosures ordered and disjoint
I1 = [Fr(x) for x in C["exact_values"]["I1_enclosure"]]
I2 = [Fr(x) for x in C["exact_values"]["I2_enclosure"]]
l3 = [Fr(x) for x in C["exact_values"]["lambda3_enclosure"]]
ck("lambda1 > lambda2 (disjoint)", I1[0] > I2[1])
ck("lambda2 > lambda3 (disjoint)", I2[0] > l3[1])
# multiplier arithmetic re-derived
E_TAU = Fr(json.load(open("/tmp/ctree/FWL2CF00/PARENT_LOCK_AND_ARM_BINDING_MANIFEST.json"))["E_TAU_exact"])
amp = math.sqrt(float(E_TAU)) / math.sqrt(float(I2[0]))
ck("amplitude multiplier ~1.754 re-derived", 1.74 < amp < 1.77)

# basis round-trip and reconstruction
B = np.load(f"{OUT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz")
BJ = json.load(open(f"{OUT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.json"))
ck("basis npz has real arrays", all(k in B.files for k in ("mu", "e1", "e2", "P1", "P2", "scores")))
ck("e1 unit norm", abs(float(B["e1"] @ B["e1"]) - 1) < 1e-9)
ck("e1 canonical sign (max-abs positive)", B["e1"][int(np.argmax(np.abs(B["e1"])))] > 0)
c = B["scores"]
R0f = float(Fr(C["exact_values"]["R0_exact"]))
recon = R0f - (c[:, 0] @ c[:, 0] + c[:, 1] @ c[:, 1]) / 32.0
R2mid = 0.5 * (float(Fr(C["exact_values"]["R2_enclosure"][0])) + float(Fr(C["exact_values"]["R2_enclosure"][1])))
ck("reconstruction R0 - scores^2/n == R2", abs(recon - R2mid) < 1e-9)

D = json.load(open(f"{OUT}/SQDT00_STATIC_DOSE_ADMISSIBILITY_AUDIT.json"))
ck("dose axis does not exist", D["VERDICT"]["DOSE_AXIS_EXISTS_WITHOUT_NEW_EXECUTABLE"] is False)
ck("carrier1 involution bitwise", D["C_involution"]["CARRIER_1_all_op_squared_identity_bitwise"])
ck("all dose negative controls fire", D["F_all_controls_fire"])
ck("dose disposition token", D["VERDICT"]["DISPOSITION"] == "DOSE_2X_STATICALLY_INADMISSIBLE_OR_UNRESOLVED")

O = json.load(open(f"{OUT}/SQDT00_PREEXECUTION_NONVACUOUS_ORACLE.json"))
ck("oracle 17 groups all non-vacuous", O["all_nonvacuous"] and O["n_groups"] == 17)

S = json.load(open(f"{OUT}/SQDT00_ENGINE_START_LEDGER.json"))
ck("zero engine starts", S["total_engine_starts_spent"] == 0)

DISP = json.load(open(f"{OUT}/SQDT00_FINAL_DISPOSITION.json"))
ck("disposition token present",
   DISP["DISPOSITION"] == "OFFLINE_QUOTIENT_BASIS_SERIALIZED_AND_TRANSFERABLE__DOSE_2X_STATICALLY_INADMISSIBLE__NO_FRESH_PANEL__ZERO_STARTS")

rep = open(f"{OUT}/SQDT00_FINAL_REPORT.md").read()
for line in ("GOOD_NEWS =", "LESS_GOOD_NEWS =", "WHAT_IT_CHANGES =", "NEXT_SCIENTIFIC_ELIGIBILITY ="):
    ck("report has %s" % line, line in rep)
ck("report is French (contains accented tokens)", "démarrage" in rep or "matérialité" in rep)

print("\nVERIFY:", "ALL PASS" if not fails else ("FAILURES: " + ", ".join(fails)))
