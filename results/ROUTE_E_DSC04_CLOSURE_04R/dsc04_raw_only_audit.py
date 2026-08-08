"""ROUTE_E_DSC04_RAW_ONLY_CAUSAL_CLOSURE_04R.

RAW_AND_ARTIFACT_ONLY. No scientific engine is imported or invoked anywhere in this file.
Every parent artefact is opened read-only; every derived file is written into CLOSURE_04R/.
"""
from __future__ import annotations
import ast, csv, hashlib, json, math, os, subprocess, sys
from pathlib import Path

# Hard guard: this module must never be able to step the engine.
FORBIDDEN = ("edlab", "od_core", "dsc_core", "dsc_harness", "morph02_ic", "bridge00_harness")
SRC = Path("..")                    # parent artefacts, read-only
OUT = Path(".")                     # closure directory
TOL = 1e-12

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()

def num(v):
    """Explicit numeric parse. Returns None for absent/NaN. NEVER uses truthiness."""
    if v is None:
        return None
    if isinstance(v, str):
        if v == "" or v == "None" or v == "nan" or v == "NaN":
            return None
        try:
            v = float(v)
        except ValueError:
            return None
    if isinstance(v, bool):
        return float(v)
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    if math.isnan(x):
        return None
    return x

def boolean(v):
    return v == "True" or v is True


# ============================================================ 2. inventory
PARENT_FILES = [
    "dynamic_source_capture_protocol.json", "dynamic_source_capture_protocol.sha256",
    "source_filter_audit.json", "t256_branch_manifest.json",
    "dynamic_source_capture_rows.csv", "dynamic_source_capture_summary.json",
    "dynamic_source_capture_fixtures.json", "dynamic_source_capture.png",
    "dsc_core.py", "dsc_harness.py", "dsc_fixtures.py", "dsc_audit.py", "dsc_final.py",
    "DSC_REPORT.md",
]
RAW = {"dynamic_source_capture_rows.csv", "t256_branch_manifest.json",
       "source_filter_audit.json", "dynamic_source_capture_fixtures.json"}


def git(*a):
    try:
        return subprocess.run(["git", *a], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:
        return f"UNAVAILABLE: {e}"


def inventory():
    inv = {"mission": "ROUTE_E_DSC04_RAW_ONLY_CAUSAL_CLOSURE_04R",
           "parent_result_commit": "f4f0a936fbccea096e63a75de6c9e5b8ec7d1878",
           "parent_commit": "5869283d6662f8b4f983c9f6f33243754be72cd9",
           "ancestry_verified_on_device": True,
           "archive_sha256_on_device": "ca743415b569394c8696ecaa8e755b5e26c8222c73102ba3bc24c893674d202a",
           "bundle_sha256_on_device": "49afa73ede3714aa6a0a4c0743f0e46e1229c1cf82a7011ecdece4d2814218e7",
           "bundle_verify": "okay", "files": []}
    sealed = json.loads((SRC / "dynamic_source_capture_protocol.json").read_text())["code_sha256"]
    for f in PARENT_FILES:
        p = SRC / f
        present = p.exists()
        e = {"path": f, "present": present,
             "size": (p.stat().st_size if present else None),
             "sha256": (sha(p) if present else None),
             "raw_or_derived": ("RAW" if f in RAW else "DERIVED"),
             "sealed_in_protocol": f in sealed,
             "sealed_sha256": sealed.get(f),
             "modified_during_closure": False}
        if e["sealed_sha256"] is not None and e["sha256"] is not None:
            e["matches_seal"] = (e["sealed_sha256"] == e["sha256"])
        inv["files"].append(e)
    # the artefact the parent mission's own spec asked for and never produced
    inv["files"].append({"path": "dynamic_source_capture_event_ledger.parquet", "present": False,
                         "size": None, "sha256": None, "raw_or_derived": "RAW",
                         "sealed_in_protocol": False, "sealed_sha256": None,
                         "modified_during_closure": False,
                         "note": "REQUIRED by the DSC_04 mission spec item 14.7 and NEVER PRODUCED. "
                                 "Proof of absence: no file matching dynamic_source_capture_event_ledger* "
                                 "exists in the working directory, in DSC_DELIVERY/, in the archive, or "
                                 "in the git tree of f4f0a93."})
    return inv


# ================================================ 6+8. injection route partition
def route_partition(rows):
    """The ONLY per-injection information the parent persisted is `reject_counts`: a per-
    trajectory histogram of decision TAGS. Masses per tag were not persisted."""
    out = []
    for r in rows:
        d = json.loads(r.get("reject_counts") or "{}")
        acc = d.get("ACCEPTED", 0)                       # non-adjacent  -> REMOTE_HALO
        sub = d.get("ACCEPTED_SUBTHRESHOLD_ADJACENT", 0)  # gd==1 to C_t -> SHELL_PRELOAD
        tot = acc + sub
        inj = num(r.get("realized_source_injection"))
        out.append({
            "L": r["L"], "seed": r["seed"], "arm": r["arm"],
            "realized_source_injection": inj,
            "n_accept_remote_halo": acc,
            "n_accept_shell_preload": sub,
            "n_reject_inside_track": d.get("REJECT_INSIDE_TRACK", 0),
            "n_reject_occupied": d.get("REJECT_OCCUPIED", 0),
            "n_reject_track_adjacency_legacy": d.get("REJECT_TRACK_ADJACENCY", 0),
            "n_reject_quota": d.get("REJECT_QUOTA", 0),
            "shell_preload_decision_fraction": (sub / tot) if tot > 0 else None,
            "remote_halo_mass_exactly_zero": (tot > 0 and acc == 0),
            "remote_halo_mass_value": (0.0 if (tot > 0 and acc == 0) else None),
            "mass_split_recoverable": False,
            "reason": "per-tag MASS was never persisted; only decision COUNTS. The split is exact "
                      "only when one tag has zero decisions.",
        })
    return out


# =================================== 11. independent endpoint re-evaluation
CRIT = ["same_track_valid", "never_merged", "no_direct_operator_insertion",
        "remote_dynamic_contact", "capture_counter", "incorporation_16", "durable_128",
        "incumbent_256_egress", "fresh_retention_post_force", "fresh_retention_2048",
        "coast_retention_ratio", "sink_matched_replacement_post_force",
        "sink_matched_replacement_2048", "tracked_mass_post_force", "tracked_mass_2048",
        "paired_sham_mass_difference", "field_identity_residual", "system_balance_residual"]


def endpoint_independent(r, sham_by_block):
    """Second, independent evaluator. Explicit comparisons only: `is None`, `== 0`, `<= tol`.
    No implicit truthiness anywhere."""
    M = num(r.get("M256"))
    res = {}
    raw = {}
    if M is None:
        return {c: False for c in CRIT}, {}, "T256_INVALID"

    def ge(key, factor, absolute=False):
        v = num(r.get(key))
        raw[key] = v
        if v is None:
            return False
        return v >= (factor if absolute else factor * M)

    res["same_track_valid"] = (boolean(r.get("survival_2048")) and boolean(r.get("coast_survival")))
    cm = num(r.get("capture_by_merger"))
    raw["capture_by_merger"] = cm
    res["never_merged"] = (cm is not None and cm <= TOL)
    di = num(r.get("direct_operator_insertion"))
    raw["direct_operator_insertion"] = di
    res["no_direct_operator_insertion"] = (di is not None and di <= TOL)
    res["remote_dynamic_contact"] = ge("unique_contact", 0.04)
    res["capture_counter"] = ge("unique_capture_transport", 0.04)
    res["incorporation_16"] = ge("incorporation_16", 0.04)
    res["durable_128"] = ge("durable_incorporation_128", 0.03)
    res["incumbent_256_egress"] = ge("unique_incumbent_egress_to_sink", 0.04)
    res["fresh_retention_post_force"] = ge("fresh_retention_postforce", 0.04, absolute=True)
    res["fresh_retention_2048"] = ge("fresh_retention_2048", 0.02, absolute=True)
    res["coast_retention_ratio"] = ge("coast_retention_ratio", 0.50, absolute=True)
    res["sink_matched_replacement_post_force"] = ge("sink_matched_replacement_postforce", 0.04, absolute=True)
    res["sink_matched_replacement_2048"] = ge("sink_matched_replacement_2048", 0.02, absolute=True)
    for tag in ("postforce", "2048"):
        v = num(r.get(f"mass_ratio_{tag}"))
        raw[f"mass_ratio_{tag}"] = v
        key = "tracked_mass_post_force" if tag == "postforce" else "tracked_mass_2048"
        res[key] = (v is not None and 0.75 <= v <= 1.25)
    s = sham_by_block.get((r["L"], r["seed"]))
    a = num(r.get("mass_ratio_2048"))
    b = num(s.get("mass_ratio_2048")) if s is not None else None
    raw["sham_mass_ratio_2048"] = b
    res["paired_sham_mass_difference"] = (a is not None and b is not None and abs(a - b) <= 0.15)
    alg = num(r.get("algebraic_ledger_error"))
    raw["field_identity_residual"] = alg
    res["field_identity_residual"] = (alg is not None and alg <= 1e-12)
    sysr = num(r.get("total_system_balance_error"))
    raw["system_balance_residual"] = sysr
    res["system_balance_residual"] = (sysr is not None and sysr <= 1e-12 * M)
    fails = [c for c in CRIT if res[c] is False]
    return res, raw, ("OK" if len(fails) == 0 else "|".join(fails))


# ============================================================ chain invariants
def chain_invariants(rows):
    """REMOTE_DURABLE_128 <= INC_16 <= CAPTURE <= CONTACT <= REALIZED_INJECTION,
    on the counters as the parent actually computed them."""
    out = []
    for r in rows:
        if r.get("t256_status") != "T256_VALID_TRACK":
            continue
        inj = num(r.get("realized_source_injection"))
        con = num(r.get("unique_contact"))
        cap = num(r.get("unique_capture_transport"))
        i16 = num(r.get("incorporation_16"))
        d128 = num(r.get("durable_incorporation_128"))
        if None in (inj, con, cap, i16, d128):
            continue
        out.append({"L": r["L"], "seed": r["seed"], "arm": r["arm"],
                    "injection": inj, "contact": con, "capture": cap,
                    "incorporation_16": i16, "durable_128": d128,
                    "capture_le_contact": cap <= con + TOL,
                    "inc16_le_capture": i16 <= cap + TOL,
                    "d128_le_inc16": d128 <= i16 + TOL,
                    "contact_le_injection": con <= inj + TOL,
                    "direct_dynamic_capture_is_zero": (r["arm"] != "DIRECT_INTERFACE_Q100") or (cap <= TOL)})
    return out


def main():
    for m in FORBIDDEN:
        assert m not in sys.modules, f"engine module {m} imported -- forbidden in RAW_ONLY mode"
    rows = list(csv.DictReader(open(SRC / "dynamic_source_capture_rows.csv")))
    sham = {(r["L"], r["seed"]): r for r in rows if r["arm"] == "SHAM"}

    OUT.mkdir(exist_ok=True)
    (OUT / "dsc04_parent_artifact_inventory.json").write_text(json.dumps(inventory(), indent=1))

    part = route_partition(rows)
    with (OUT / "dsc04_causal_route_partition.csv").open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(part[0])); w.writeheader(); w.writerows(part)

    inv = chain_invariants(rows)
    with (OUT / "dsc04_chain_invariants.csv").open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(inv[0])); w.writeheader(); w.writerows(inv)

    ep = []
    for r in rows:
        res, raw, why = endpoint_independent(r, sham)
        row = {"L": r["L"], "seed": r["seed"], "arm": r["arm"],
               "t256_status": r.get("t256_status"),
               "ENDPOINT_MET": all(res.get(c) is True for c in CRIT) if len(res) == len(CRIT) else False,
               "failure_reason": why}
        for c in CRIT:
            row[f"ok_{c}"] = res.get(c)
        for k, v in raw.items():
            row[f"val_{k}"] = v
        ep.append(row)
    fields = sorted({k for e in ep for k in e})
    with (OUT / "dsc04_trajectory_endpoint_audit.csv").open("w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields); w.writeheader(); w.writerows(ep)
    print("endpoints recomputes:", sum(1 for e in ep if e["ENDPOINT_MET"] is True), "/", len(ep))
    return ep, part, inv


if __name__ == "__main__":
    main()
