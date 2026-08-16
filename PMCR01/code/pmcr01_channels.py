"""PMCR01 Gate 0 — find EVERY executable event that can change the count, or the continuation
probability, of Y. Static, over the COMMITTED blobs, not over a working copy.

The method is deliberately mechanical: parse the three files that make up the executable path,
find every write whose target is `self.n[<literal>]` for a Y-bearing species, walk up to the
enclosing method, read the scheduler order out of `_one_step`, and only then attach names. A
parameter that never reaches such a write is not a channel however suggestive its name.
"""
from __future__ import annotations

import ast
import json
import subprocess

REPO = "/home/claude/edl"
OUT = "/home/claude/PMCR01/out"

FILES = {
    "kinetics": "ORR01/code/kinetics.py",
    "lawspec_v2": "ORR01/code/lawspec_v2.py",
    "engine_obtc": "OBTC02/code/engine_obtc.py",
    "protocol_obtc02": "OBTC02/code/protocol_obtc02.py",
    "gate_obtc02": "OBTC02/code/gate_obtc02.py",
    # REPAIR F1: the observer was previously omitted from the analysed set. It defines no rate,
    # so it creates no Y channel -- but it records Q, the environmental exposure quantity the
    # disposition turned on, and omitting it produced a false conclusion about measurability.
    "observe": "ORR01/code/observe.py",
}
MANIFEST = "OBTC02/code/obtc02_protocol.yaml"
Y_SPECIES = ("Y", "WY", "SY")


def blob(path):
    r = subprocess.run(("git", "show", "HEAD:%s" % path), cwd=REPO,
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("missing blob %s" % path)
    return r.stdout


def blob_id(path):
    r = subprocess.run(("git", "rev-parse", "HEAD:%s" % path), cwd=REPO,
                       capture_output=True, text=True)
    return r.stdout.strip()


# --------------------------------------------------------------------- AST helpers
def is_self_n_sub(node):
    """self.n[<literal str>] ?"""
    if not isinstance(node, ast.Subscript):
        return None
    v = node.value
    if not (isinstance(v, ast.Attribute) and v.attr == "n"
            and isinstance(v.value, ast.Name) and v.value.id == "self"):
        return None
    s = node.slice
    if isinstance(s, ast.Constant) and isinstance(s.value, str):
        return s.value
    return "<DYNAMIC>"


def enclosing(tree):
    """map node -> (classname, funcname)"""
    out = {}
    for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
        for fn in [n for n in cls.body if isinstance(n, ast.FunctionDef)]:
            for n in ast.walk(fn):
                out[n] = (cls.name, fn.name)
    for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
        for n in ast.walk(fn):
            out.setdefault(n, ("<module>", fn.name))
    return out


def spec_attrs_read(fn_node):
    """sp.<attr> or self.sp.<attr> read anywhere in this function."""
    got = set()
    for n in ast.walk(fn_node):
        if isinstance(n, ast.Attribute):
            b = n.value
            if isinstance(b, ast.Name) and b.id == "sp":
                got.add(n.attr)
            if (isinstance(b, ast.Attribute) and b.attr == "sp"
                    and isinstance(b.value, ast.Name) and b.value.id == "self"):
                got.add(n.attr)
    return sorted(got)


def find_y_writes():
    """Every statement that assigns to self.n['Y'|'WY'|'SY'], with its enclosing method."""
    rows = []
    for mod, path in FILES.items():
        src = blob(path)
        tree = ast.parse(src)
        enc = enclosing(tree)
        fns = {}
        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            for fn in [n for n in cls.body if isinstance(n, ast.FunctionDef)]:
                fns[(cls.name, fn.name)] = fn
        for n in ast.walk(tree):
            if not isinstance(n, (ast.Assign, ast.AugAssign)):
                continue
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in targets:
                sp = is_self_n_sub(t)
                if sp is None:
                    continue
                cls, fn = enc.get(n, ("?", "?"))
                literal = sp if sp != "<DYNAMIC>" else None
                rows.append({
                    "module": mod, "path": path, "class": cls, "method": fn,
                    "line": n.lineno,
                    "species_literal": literal,
                    "dynamic_target": sp == "<DYNAMIC>",
                    "source": ast.get_source_segment(src, n),
                    "spec_attrs_in_scope": spec_attrs_read(fns[(cls, fn)])
                    if (cls, fn) in fns else [],
                })
    return rows


def dynamic_species_loops():
    """Writes whose species is a loop variable: resolve the literal tuples they iterate over.
    This is where the Y birth and Y death actually live, and a naive literal scan misses them."""
    got = []
    for mod, path in FILES.items():
        src = blob(path)
        tree = ast.parse(src)
        enc = enclosing(tree)
        for n in ast.walk(tree):
            if not isinstance(n, ast.For):
                continue
            it = n.iter
            if not isinstance(it, (ast.Tuple, ast.List)):
                continue
            tuples = []
            for el in it.elts:
                if isinstance(el, ast.Tuple):
                    vals = []
                    for e in el.elts:
                        if isinstance(e, ast.Constant):
                            vals.append(e.value)
                        elif isinstance(e, ast.Attribute):
                            vals.append("%s.%s" % (getattr(e.value, "id",
                                                           getattr(e.value, "attr", "?")),
                                                   e.attr))
                        else:
                            vals.append("<expr>")
                    tuples.append(vals)
            if not tuples:
                continue
            writes = [w for w in ast.walk(n)
                      if isinstance(w, (ast.Assign, ast.AugAssign))
                      and any(is_self_n_sub(t) is not None
                              for t in (w.targets if isinstance(w, ast.Assign) else [w.target]))]
            if not writes:
                continue
            cls, fn = enc.get(n, ("?", "?"))
            got.append({"module": mod, "path": path, "class": cls, "method": fn,
                        "line": n.lineno,
                        "loop_targets": [t.id for t in (n.target.elts
                                                        if isinstance(n.target, ast.Tuple)
                                                        else [n.target])
                                         if isinstance(t, ast.Name)],
                        "literal_tuples": tuples,
                        "n_writes_inside": len(writes),
                        "touches_Y": any(any(str(v) in ("Y", "WY", "SY") for v in t)
                                         for t in tuples)})
    return got


def scheduler_order():
    src = blob(FILES["kinetics"])
    tree = ast.parse(src)
    for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
        for fn in [n for n in cls.body if isinstance(n, ast.FunctionDef)]:
            if fn.name != "_one_step":
                continue
            order = []
            for st in fn.body:
                if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call):
                    c = st.value
                    if isinstance(c.func, ast.Attribute):
                        args = []
                        for a in c.args:
                            if isinstance(a, ast.Constant):
                                args.append(a.value)
                            elif isinstance(a, ast.Attribute):
                                args.append(a.attr)
                        order.append({"call": c.func.attr, "args": args})
            return {"class": cls.name, "order": order}
    return {}


def manifest_point():
    txt = blob(MANIFEST)
    out, inblock = {}, False
    for ln in txt.splitlines():
        if ln.startswith("point:"):
            inblock = True
            continue
        if inblock:
            if ln and not ln.startswith(" "):
                break
            if ":" in ln:
                k, v = ln.strip().split(":", 1)
                out[k.strip()] = v.strip()
    return out


def spec_for_source():
    src = blob(FILES["protocol_obtc02"])
    tree = ast.parse(src)
    for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
        if fn.name == "spec_for":
            return ast.get_source_segment(src, fn)
    return None


def admissibility_checks():
    """Does anything in the executable path refuse a nonzero kY or muY?"""
    hits = []
    for mod, path in FILES.items():
        src = blob(path)
        tree = ast.parse(src)
        for n in ast.walk(tree):
            if isinstance(n, (ast.Assert, ast.Raise)):
                seg = ast.get_source_segment(src, n) or ""
                if any(t in seg for t in ("kY", "muY", "p_hop_Y", "Y")):
                    hits.append({"module": mod, "line": n.lineno, "source": seg[:200]})
    return hits


def main():
    rows = find_y_writes()
    loops = dynamic_species_loops()
    order = scheduler_order()
    pt = manifest_point()
    checks = admissibility_checks()

    out = {
        "SECTION": "PMCR01 Gate 0 — static discovery",
        "ANALYSED_BLOBS": {p: blob_id(p) for p in list(FILES.values()) + [MANIFEST]},
        "SCHEDULER_ORDER": order,
        "MANIFEST_POINT": pt,
        "SPEC_FOR_SOURCE": spec_for_source(),
        "LITERAL_WRITES_TO_Y_BEARING_SPECIES": [r for r in rows
                                                if r["species_literal"] in Y_SPECIES],
        "DYNAMIC_WRITES_TO_self_n": [r for r in rows if r["dynamic_target"]],
        "SPECIES_LOOPS_CARRYING_THE_DYNAMIC_WRITES": loops,
        "ADMISSIBILITY_CHECKS_MENTIONING_Y": checks,
        "N_LITERAL_Y_WRITES": len([r for r in rows if r["species_literal"] in Y_SPECIES]),
        "N_DYNAMIC_WRITES": len([r for r in rows if r["dynamic_target"]]),
    }
    json.dump(out, open(f"{OUT}/_gate0_static.json", "w"), indent=1, default=str)

    print("scheduler order (kinetics.World._one_step):")
    for c in order["order"]:
        print("   %-22s %s" % (c["call"], c["args"]))
    print("\nliteral writes to Y / WY / SY:")
    for r in out["LITERAL_WRITES_TO_Y_BEARING_SPECIES"]:
        print("   %-14s %-12s %-22s L%-4d  %s"
              % (r["module"], r["class"], r["method"], r["line"],
                 (r["source"] or "").replace("\n", " ")[:70]))
    print("\ndynamic self.n[...] writes (species is a loop variable):")
    for r in out["DYNAMIC_WRITES_TO_self_n"]:
        print("   %-14s %-12s %-22s L%-4d  %s"
              % (r["module"], r["class"], r["method"], r["line"],
                 (r["source"] or "").replace("\n", " ")[:70]))
    print("\nspecies loops that carry them:")
    for l in loops:
        print("   %-14s %-12s %-16s L%-4d  targets %s  tuples %s  touches_Y=%s"
              % (l["module"], l["class"], l["method"], l["line"], l["loop_targets"],
                 l["literal_tuples"], l["touches_Y"]))
    print("\nadmissibility checks mentioning Y: %s"
          % (checks if checks else "NONE — no guard refuses a nonzero kY or muY"))
    print("\nmanifest point block: %s" % pt)


if __name__ == "__main__":
    main()
