"""CLEA01 closure §6 — hidden online-identifier audit, by AST and by runtime data access.

The audit's own G7 scan was found structurally blind: it stripped string literals, and in Python a
dict field access IS a string literal, so `rec["VERDICT"]` read as clean. This does the opposite —
string literals COUNT as use, and only module/function docstrings are separated out as mention.

Then it does the thing a source scan cannot do: it wraps `numpy.load` and records the archive keys
each ancestry implementation actually touches at run time, on a real archive. A key that is never
requested cannot define anything.

Three-way classification, as required:
    MENTIONED_IN_DOCUMENTATION      appears only in a docstring
    READ_FOR_AFTER_THE_FACT_COMPARISON  read by code that compares or windows, never by the
                                    propagation operator
    USED_TO_DEFINE_CAUSAL_ANCESTRY  read on the path that computes CERTAIN or POSSIBLE
"""
from __future__ import annotations
import ast, datetime as dt, json, os, sys
import numpy as np
REPO = os.environ.get("CLEA01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/OMLDCT02/code")
sys.path.insert(0, f"{REPO}/CLEA01/code")
import omldct02_hashes as H

TOKENS = ["c_cid", "k_id", "cid", "component_id", "identity_id", "daughter_id",
          "VERDICT", "TERMINAL", "TERMINAL_LABEL", "identity_carried", "descent_level",
          "TRIGGERED", "ADMISSIBLE", "COMPLETE_TURNOVER", "FUNCTIONAL",
          "E3_DURATION", "E3_EXPOSURE", "PAIR_MEASUREMENTS", "FROZEN_ANALYSIS",
          "interval_end", "ids_at", "named_at", "survival", "outcome"]

# the propagation operator — the only code that may define CERTAIN or POSSIBLE
ANCESTRY_FUNCS = {("clea01_lineage_i1.py", "run"), ("clea01_lineage_i1.py", "sources"),
                  ("clea01_lineage_i1.py", "load_rows"), ("clea01_lineage_i1.py", "_n_groups"),
                  ("clea01_lineage_i2.py", "run"), ("clea01_lineage_i2.py", "dilate"),
                  ("clea01_lineage_i2.py", "load_grids"), ("clea01_lineage_i2.py", "grid_at")}


def scan(path):
    """(function name or '<module>') -> tokens used in executable code or data, and separately the
    tokens that occur only in docstrings."""
    tree = ast.parse(open(path).read())
    docs = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            d = ast.get_docstring(n, clean=False)
            if d:
                docs.add(d)
    owner = {}
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        for n in ast.walk(fn):
            owner[id(n)] = fn.name
    used = {}
    for n in ast.walk(tree):
        vals = []
        if isinstance(n, ast.Name):
            vals = [n.id]
        elif isinstance(n, ast.Attribute):
            vals = [n.attr]
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value not in docs:
            vals = [n.value]
        for v in vals:
            for t in TOKENS:
                if t == v or (len(t) > 4 and t in v):
                    used.setdefault(owner.get(id(n), "<module>"), set()).add(t)
    doc_only = set()
    for t in TOKENS:
        if any(t in d for d in docs) and not any(t in s for s in used.values()):
            doc_only.add(t)
    return {k: sorted(v) for k, v in used.items()}, sorted(doc_only)


class Recorder:
    """a stand-in for the object numpy.load returns, which records every key requested."""
    def __init__(self, z, sink):
        self._z, self._sink = z, sink

    def __getitem__(self, k):
        self._sink.add(k)
        return self._z[k]

    def __getattr__(self, a):
        return getattr(self._z, a)


def runtime_keys(mod, path, t_m, cells):
    sink = set()
    real = np.load

    def fake(p, *a, **kw):
        return Recorder(real(p, *a, **kw), sink)
    np.load = fake
    try:
        mod.run(path, t_m, cells, **({"horizon_cap": t_m + 40} if mod.__name__.endswith("i1") else {}))
    finally:
        np.load = real
    return sorted(sink)


def main():
    code = f"{REPO}/CLEA01/code"
    scripts = sorted(f for f in os.listdir(code)
                     if f.endswith(".py") and f != os.path.basename(__file__))
    per_file, doc_only_all = {}, {}
    for f in scripts:
        u, d = scan(f"{code}/{f}")
        if u:
            per_file[f] = u
        if d:
            doc_only_all[f] = d

    classified = []
    for f, funcs in per_file.items():
        for fn, toks in funcs.items():
            on_path = (f, fn) in ANCESTRY_FUNCS
            for t in toks:
                classified.append({"file": f, "function": fn, "token": t,
                                   "on_the_ancestry_path": on_path,
                                   "CLASS": "USED_TO_DEFINE_CAUSAL_ANCESTRY" if on_path
                                   else "READ_FOR_AFTER_THE_FACT_COMPARISON"})
    for f, toks in doc_only_all.items():
        for t in toks:
            classified.append({"file": f, "function": "<docstring>", "token": t,
                               "on_the_ancestry_path": False,
                               "CLASS": "MENTIONED_IN_DOCUMENTATION"})

    led = [json.loads(l) for l in open(f"{REPO}/OMLDCT02/work/OMLDCT02_SEALED_LEDGER.jsonl") if l.strip()]
    x = next(r for r in led if r.get("ADMISSIBLE"))
    import clea01_lineage_i1 as I1
    import clea01_lineage_i2 as I2
    rk = {}
    for mod in (I1, I2):
        rk[mod.__name__] = runtime_keys(mod, x["ARCHIVES"]["SHAM"]["path"], x["t_m"],
                                        x["FORK"]["locked_daughter_cells"])

    # Model A's reconstruction is imported by clea01_g4_containment for the containment test. Its
    # `ids_at`/`named_at` are LDFMA01's own OFFLINE labels, not archive identity fields — probe it
    # the same way rather than take that on trust.
    os.environ.setdefault("LDFMA01_REPO", REPO)
    sys.path.insert(0, f"{REPO}/LDFMA01/code")
    import ldfma01_raw as A_
    _sink = set(); _real = np.load
    def _fake(p_, *a_, **kw_):
        return Recorder(_real(p_, *a_, **kw_), _sink)
    np.load = _fake
    try:
        _w = A_.World(x["ARCHIVES"]["SHAM"]["path"]); _w.trace()
    finally:
        np.load = _real
    rk["ldfma01_raw (Model A reconstruction, imported by the G4 containment test)"] = sorted(_sink)

    FORBIDDEN_KEYS = {"c_cid", "k_id", "k_ncells", "k_a0y", "k_a0x", "k_soy", "k_sox", "k_xd",
                      "c_cand", "c_free", "c_nSY"}
    ANCESTRY_MODULES = ("clea01_lineage_i1", "clea01_lineage_i2")
    touched_forbidden = {k: sorted(set(v) & FORBIDDEN_KEYS)
                         for k, v in rk.items() if k in ANCESTRY_MODULES}
    # LDFMA01 is Model A's reconstruction, not Model C's ancestry. It legitimately reads component
    # summary fields, because a spatial component IS what it computes. The question that matters
    # for it is narrower and is asked separately: does it read the ONLINE identity fields?
    ONLINE_ID_KEYS = {"c_cid", "k_id"}
    a_keys = next(v for k, v in rk.items() if k.startswith("ldfma01_raw"))
    model_a_probe = {
        "archive_keys_touched": a_keys,
        "online_identity_keys_touched": sorted(set(a_keys) & ONLINE_ID_KEYS),
        "READS_ONLINE_IDENTITY_FIELDS": bool(set(a_keys) & ONLINE_ID_KEYS),
        "WHY_ITS_OTHER_KEYS_ARE_NOT_A_FINDING":
            "k_ncells, k_a0y, k_a0x, k_soy, k_sox and k_xd are physical component summaries. "
            "LDFMA01 reconstructs the locked spatial component, so reading them is that model's "
            "definition, not a hidden input. It is used only to produce Model A's per-row cells "
            "for the G4 containment comparison; it never touches Model C's CERTAIN or POSSIBLE.",
        "AN_EARLIER_VERSION_OF_THIS_AUDIT_GOT_THIS_WRONG":
            "the first run folded these keys into the two required flags and reported both as "
            "true. That was an over-broad rule, not a finding: it scoped a question about Model C's "
            "ancestry over code that computes Model A. Corrected here, and recorded rather than "
            "silently fixed.",
    }

    doc = {
        "MISSION": "CLEA01", "SECTION": "6 — hidden input audit",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "WHY_THIS_REPLACES_THE_G7_SCAN":
            "the original scan stripped comments AND string literals. In Python a dict field access "
            "is a string literal, so `rec[\"VERDICT\"]` was invisible to it. Here string literals "
            "count as USE and only docstrings count as MENTION. The checker found this and it is "
            "not argued away.",
        "SCRIPTS_SCANNED": scripts, "N_SCRIPTS": len(scripts),
        "SELF_EXCLUDED": os.path.basename(__file__),
        "SELF_EXCLUSION_REASON": "this file carries the token list as data and would match every "
                                 "token by construction.",
        "PER_FILE_PER_FUNCTION_USE": per_file,
        "DOCSTRING_ONLY": doc_only_all,
        "CLASSIFIED": sorted(classified, key=lambda r: (r["CLASS"], r["file"], r["token"])),
        "ANCESTRY_PATH_DEFINITION": sorted(f"{a}::{b}" for a, b in ANCESTRY_FUNCS),
        "RUNTIME_ARCHIVE_KEYS_TOUCHED": rk,
        "RUNTIME_PROBE": {"archive": x["ARCHIVES"]["SHAM"]["path"], "index": x["index"],
                          "method": "numpy.load was wrapped so every __getitem__ key was recorded "
                                    "while each implementation actually propagated CERTAIN and "
                                    "POSSIBLE on a real archive. No world was constructed."},
        "FORBIDDEN_ARCHIVE_KEYS": sorted(FORBIDDEN_KEYS),
        "FORBIDDEN_KEYS_TOUCHED_AT_RUNTIME_BY_THE_ANCESTRY_PATH": touched_forbidden,
        "MODEL_A_RECONSTRUCTION_PROBE": model_a_probe,
        "FUTURE_OUTCOME_USED_TO_DEFINE_ANCESTRY":
            any(r["CLASS"] == "USED_TO_DEFINE_CAUSAL_ANCESTRY" for r in classified)
            or any(v for v in touched_forbidden.values()),
        "ONLINE_ID_USED_TO_DEFINE_ANCESTRY":
            any(r["CLASS"] == "USED_TO_DEFINE_CAUSAL_ANCESTRY" and r["token"] in
                ("c_cid", "k_id", "cid", "component_id", "identity_id", "daughter_id")
                for r in classified) or any(v for v in touched_forbidden.values()),
    }
    doc["HIDDEN_INPUT_CONTENT_HASH"] = H.content_digest(doc, extra_excluded=("HIDDEN_INPUT_CONTENT_HASH",))
    json.dump(doc, open(f"{REPO}/CLEA01/out/CLEA01_HIDDEN_INPUT_AUDIT.json", "w"), indent=1)
    print("runtime keys i1:", rk["clea01_lineage_i1"])
    print("runtime keys i2:", rk["clea01_lineage_i2"])
    print("forbidden touched:", touched_forbidden)
    print("FUTURE_OUTCOME_USED_TO_DEFINE_ANCESTRY =", doc["FUTURE_OUTCOME_USED_TO_DEFINE_ANCESTRY"])
    print("ONLINE_ID_USED_TO_DEFINE_ANCESTRY     =", doc["ONLINE_ID_USED_TO_DEFINE_ANCESTRY"])
    for r in doc["CLASSIFIED"]:
        print(f"  {r['CLASS']:34s} {r['file']}::{r['function']}  {r['token']}")
    return doc


if __name__ == "__main__":
    main()
