"""Independent verifier for EXACT_ENDPOINT_FUNCTIONAL_CONGRUENCE_AUDIT_00.

Re-derives every load-bearing claim from the committed parent artefacts, WITHOUT reading
eefca_audit.py's own derivations, then compares against eefca_audit.json. Runs under the same
fail-closed sentinel: zero engine starts.
"""
from __future__ import annotations
import eefca_sentinel                          # noqa: F401 -- fail-closed guard FIRST
import os, ast, json, pickle, hashlib

E = "/home/claude/sweep/ETPC"
ROWS, OK = [], True


def chk(name, cond, detail=""):
    global OK
    OK &= bool(cond)
    ROWS.append({"check": name, "PASS": bool(cond), "detail": detail})


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


B = pickle.load(open(f"{E}/etpc_PRIMARY.pkl", "rb"))
A = json.load(open(f"{E}/etpc_analysis_PRIMARY.json"))
G = json.load(open(f"{E}/etpc_gates.json"))
AUD = json.load(open("eefca_audit.json"))

# ---------------------------------------------------------------- V1 sentinel really fails closed
try:
    __import__("edlab")
    fired = False
except RuntimeError as e:
    fired = "AUDIT_SCOPE_VIOLATION" in str(e)
chk("V1 sentinel raises AUDIT_SCOPE_VIOLATION on a runtime import", fired)
chk("V1b audit recorded zero engine starts and zero trajectories",
    AUD["NEW_ENGINE_STARTS"] == 0 and AUD["NEW_TRAJECTORIES"] == 0)

# ---------------------------------------------------------------- V2 parent code seal
seal = json.load(open(f"{E}/etpc_protocol.json"))["code_sha256"]
bad = [f for f, v in seal.items() if sha(os.path.join(E, f)) != v]
chk("V2 parent code seal intact (4/4)", not bad, f"mismatched = {bad}")
chk("V2b parent protocol sha256 matches the value recorded in the audit",
    sha(f"{E}/etpc_protocol.json") == AUD["A_PROVENANCE"]["PARENT_PROTOCOL_SHA256_RESOLVED"])

# ---------------------------------------------------------------- V3 the 67-start ledger
led = AUD["B1_ENGINE_START_LEDGER"]
chk("V3 start ledger sums to its own total",
    led["qualification"]["subtotal"] + led["primary"]["subtotal"] == led["total"] == 67)
chk("V3b qualification subtotal equals the gates file's recorded starts",
    G["engine_starts"] == led["qualification"]["subtotal"] == 17, f"gates={G['engine_starts']}")
chk("V3c primary = 10 blocks x 5 starts", len(B) * 5 == led["primary"]["subtotal"] == 50)

# ---------------------------------------------------------------- V4 the executed map is not an involution
noninv, contr = [], []
for x in B:
    a, b = x["operator"]["a"], x["operator"]["b"]
    p, q, r, s = 1 - a, a, b, 1 - b
    p2, q2 = p * p + q * r, p * q + q * s
    r2, s2 = r * p + s * r, r * q + s * s
    is_id = abs(p2 - 1) < 1e-12 and abs(q2) < 1e-12 and abs(r2) < 1e-12 and abs(s2 - 1) < 1e-12
    noninv.append(not is_id)
    contr.append((1 - a - b) ** 2)
chk("V4 P(P(x)) != x in every one of the 10 blocks", all(noninv),
    f"contrast factor after two applications ranges {min(contr):.4f} .. {max(contr):.4f}")
chk("V4b the audit reports the same", AUD["C_MEAN_MAP_SUMMARY"]["P_squared_is_identity_in_any_block"] is False)

# ---------------------------------------------------------------- V5 a conservative involution DID exist
ok_inv = []
for x in B:
    MA, MB = x["operator"]["M_A"], x["operator"]["M_B"]
    # p = 0 case: P = [[0, MB/MA], [MA/MB, 0]]
    q, r = MB / MA, MA / MB
    p2, q2, r2, s2 = q * r, 0.0, 0.0, r * q
    invol = abs(p2 - 1) < 1e-12 and abs(s2 - 1) < 1e-12
    # conservation: (MA, MB) is a left eigenvector with eigenvalue 1
    cons = abs(MA * 0 + MB * r - MA) < 1e-9 and abs(MA * q + MB * 0 - MB) < 1e-9
    ok_inv.append(invol and cons)
chk("V5 an exactly conservative exact involution exists in every block", all(ok_inv),
    "P = [[0, M_B/M_A], [M_A/M_B, 0]] is involutive AND conserves M_A z_A + M_B z_B")
chk("V5b the audit reports the same",
    AUD["C_CONSERVATIVE_INVOLUTION_EXISTENCE"]["exists_in_every_block"] is True)

# ---------------------------------------------------------------- V6 invariants
drift = max(abs(x["ledger_after"]["sum_rho_z"] - x["ledger_before"]["sum_rho_z"]) for x in B)
bit = any(float(x["ledger_before"]["sum_rho_z"]).hex()
          == float(x["ledger_after"]["sum_rho_z"]).hex() for x in B)
chk("V6 Sigma rho z conserved to float precision only, never bitwise",
    drift < 1e-12 and not bit, f"max drift = {drift:.3e}, bitwise identical in any block = {bit}")
chk("V6b Sigma z is NOT conserved",
    max(abs(x["ledger_after"]["sum_z"] - x["ledger_before"]["sum_z"]) for x in B) > 1.0)
chk("V6c the raw z multiset is NOT preserved",
    all(x["ledger_before"]["raw_z_multiset_sha256"] != x["ledger_after"]["raw_z_multiset_sha256"]
        for x in B))

# ---------------------------------------------------------------- V7 boundary exposure is vacuous
same = all(x["ledger_before"]["z_exposure_at_material_bath_boundary"]
           == x["ledger_after"]["z_exposure_at_material_bath_boundary"] for x in B)
nb = {x["ledger_before"]["n_boundary_cells"] for x in B}
touched = {x["touchset"]["Mf"]["n_sites_changed"] for x in B if "touchset" in x}
chk("V7 boundary z exposure is bitwise identical before/after in every block", same)
chk("V7b the boundary mask is far larger than the intervened set, so the equality is vacuous",
    min(nb) > max(touched or {0}) if touched else min(nb) > 0,
    f"n_boundary_cells = {sorted(nb)}, Mf[0] sites changed = {sorted(touched)}")

# ---------------------------------------------------------------- V8 the Sigma z identity
res = []
for x in B:
    lb, la = x["ledger_before"], x["ledger_after"]
    pred = sum(lb["components"][n]["n_cells"]
               * (la["components"][n]["zbar"] - lb["components"][n]["zbar"]) for n in ("A", "B"))
    res.append(abs((la["sum_z"] - lb["sum_z"]) - pred))
chk("V8 d(Sigma z) = n_A dzbar_A + n_B dzbar_B (uniform additive shift, nothing else touched)",
    max(res) < 1e-9, f"max residual = {max(res):.3e}")

# ---------------------------------------------------------------- V9 endpoint scalars reconstruct
early, med = [], []
for x, row in zip(B, A["rows"]):
    sw = {p["t"]: p["c"] for p in x["arms"]["ON_SWAP"]["series"]}
    sh = {p["t"]: p["c"] for p in x["arms"]["ON_SHAM"]["series"]}
    ts = [t for t in range(1, 41) if t in sw]
    early.append(0.5 * sum(row["q"][k] * sum(sw[t][k] - sh[t][k] for t in ts) for k in ("A", "B")))
    med.append(0.5 * sum(row["q"][k] * (sw[200][k] - sh[200][k]) for k in ("A", "B")))
e_res = max(abs(u - v) for u, v in zip(early, A["early_flux"]["raw"]))
m_res = max(abs(u - v) for u, v in zip(med, A["delayed_mediator"]["raw"]))
chk("V9 early endpoint reconstructs exactly from the committed arrays", e_res == 0.0,
    f"max block residual = {e_res:.3e}")
chk("V9b delayed mediator reconstructs exactly", m_res == 0.0, f"max block residual = {m_res:.3e}")
chk("V9c means agree with the committed analysis",
    abs(sum(early) / len(early) - A["early_flux"]["mean"]) < 1e-18
    and abs(sum(med) / len(med) - A["delayed_mediator"]["mean"]) < 1e-18)

# ---------------------------------------------------------------- V10 the R7 oracle tested nothing
tree = ast.parse(open(f"{E}/etpc_gates.py").read())
fn = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "r67"][0]
found = None
for n in ast.walk(fn):
    if (isinstance(n, ast.Call) and getattr(n.func, "id", "") == "chk" and len(n.args) >= 3
            and isinstance(n.args[1], ast.Constant)
            and n.args[1].value == "test_swap_bijection_and_involution"):
        found = n.args[2]
chk("V10 the involution gate's asserted condition is a compile-time constant (it tested nothing)",
    found is not None and isinstance(found, ast.Constant) and found.value is True,
    f"asserted condition source = {ast.unparse(found) if found is not None else 'NOT FOUND'}")
row = [g for g in G["gates"] if g["fixture"] == "test_swap_bijection_and_involution"][0]
chk("V10b that gate was nevertheless recorded PASS", row["PASS"] is True)
chk("V10c its own detail string reports a non-zero P(P(x)) residual",
    "1.958e+00" in row["detail"], row["detail"][-90:])

# ---------------------------------------------------------------- V11 the endpoint never read N
src = open(f"{E}/etpc_analyse.py").read()
at = ast.parse(src)
subs = [ast.unparse(n) for n in ast.walk(at) if isinstance(n, ast.Subscript)]
reads_c = any("'c'" in s or '"c"' in s for s in subs)
reads_N = any("'N'" in s or '"N"' in s for s in subs)
chk("V11 the executed endpoint reads c", reads_c)
chk("V11b the executed endpoint never reads N, although the authorization named c AND N",
    not reads_N, "no subscript on 'N' anywhere in etpc_analyse.py")

# ---------------------------------------------------------------- V12 held-out untouched
chk("V12 no held-out artefact exists and none is read",
    not os.path.exists(f"{E}/etpc_HELDOUT.pkl"))
chk("V12b the audit records HELD_OUT_INTEGRITY = PRESERVED",
    AUD["G_ADJUDICATION"]["HELD_OUT_INTEGRITY"] == "PRESERVED")

# ---------------------------------------------------------------- V13 no forbidden phrasing
FORBIDDEN = ["the response did not move", "the effect replicated", "the derivative was right",
             "the exact-twin disposition was established"]
hits = []
for f in ("eefca_audit.json", "REPORT_EEFCA.md", "ETPC_CORRIGENDUM.md", "eefca_protocol.json"):
    if os.path.exists(f):
        t = open(f, encoding="utf-8").read()
        hits += [(f, p) for p in FORBIDDEN if p in t]
chk("V13 no forbidden phrasing appears in any deliverable", not hits, f"hits = {hits}")

# ---------------------------------------------------------------- V14 the reported statistics
chk("V14 tau_on is neither an effect nor a null under its own frozen two-sided test",
    abs(A["tau_on"]["randomisation_p"] - 0.09765625) < 1e-12
    and A["tau_on"]["ci95"][0] < 0 < A["tau_on"]["ci95"][1],
    f"p = {A['tau_on']['randomisation_p']}, CI = {A['tau_on']['ci95']}")
chk("V14b the one-sided public gates failed at their floor",
    A["early_flux"]["randomisation_p"] == 1.0 and A["delayed_mediator"]["randomisation_p"] == 1.0)
chk("V14c tau_off is exactly zero in every block", all(v == 0.0 for v in A["tau_off"]["raw"]))
chk("V14d the audit quotes tau_on exactly as committed",
    AUD["B_CORRECTED_DISPOSITIONS"]["delayed_response_numbers"]["tau_on_mean"] == A["tau_on"]["mean"])

# ---------------------------------------------------------------- V15 terminal stops
chk("V15 AUDIT_SCOPE_VIOLATION is NOT among the stops fired",
    "AUDIT_SCOPE_VIOLATION" not in AUD["TERMINAL_STOPS_FIRED"])
chk("V15b the two conformance stops did fire",
    "PROSPECTIVE_PROTOCOL_DEVIATION_NONINVOLUTIVE" in AUD["TERMINAL_STOPS_FIRED"]
    and "MATERIAL_ENDPOINT_SUBSTITUTION" in AUD["TERMINAL_STOPS_FIRED"])

rep = eefca_sentinel.report()
rep["note_on_forbidden_import_attempts"] = (
    "the single entry 'edlab' is check V1 DELIBERATELY probing the sentinel to prove it fires. "
    "The import was refused; no runtime module was ever loaded and no state was advanced. "
    "NEW_ENGINE_STARTS remains 0.")
json.dump({"rows": ROWS, "n": len(ROWS), "n_pass": sum(r["PASS"] for r in ROWS), "ALL_PASS": OK,
           "sentinel": rep}, open("eefca_verify.json", "w"), indent=1)
for r in ROWS:
    print(("PASS " if r["PASS"] else "FAIL ") + r["check"] + (f"  [{r['detail']}]" if r["detail"] else ""))
print(f"\n{sum(r['PASS'] for r in ROWS)}/{len(ROWS)} verification checks passed")
print("SENTINEL:", eefca_sentinel.report())
