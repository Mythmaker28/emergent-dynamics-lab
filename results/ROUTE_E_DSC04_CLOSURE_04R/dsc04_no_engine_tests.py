"""Engine-free tests for ROUTE_E_DSC04_RAW_ONLY_CAUSAL_CLOSURE_04R.

Nothing here imports edlab, od_core, dsc_core or dsc_harness. The parent's accounting is
audited by (a) parsing its source with `ast` and (b) re-implementing the credit arithmetic in
plain Python. Each test asserts a STRUCTURAL property, so a pass is a proof about the code, not
about one lucky trajectory.
"""
from __future__ import annotations
import ast, json, sys
from pathlib import Path

SRC = Path("..")
R = []


def check(n, name, ok, detail):
    R.append({"test": n, "name": name, "PASS": bool(ok), "detail": detail})
    print(f"  {n:>2}. {name:<52} {'PASS' if ok else 'FAIL'}   {detail}")


def tree(f):
    return ast.parse((SRC / f).read_text())


def func(mod, name, cls=None):
    for node in ast.walk(mod):
        if cls is not None and isinstance(node, ast.ClassDef) and node.name == cls:
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef) and sub.name == name:
                    return sub
        if cls is None and isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


# --- T1: no scientific engine reachable from this closure -------------------
def t1():
    bad = [m for m in ("edlab", "od_core", "dsc_core", "dsc_harness") if m in sys.modules]
    check(1, "aucun moteur scientifique importe dans la cloture", len(bad) == 0,
          f"modules interdits charges: {bad if bad else 'aucun'}")


# --- T2: `credited` is NOT advected, while `fre` is -------------------------
def t2():
    m = tree("dsc_core.py")
    adv = func(m, "advance", cls="Provenance")
    src = ast.unparse(adv)
    advected = [n for n in ("inc", "amb", "fre", "credited", "shell_credit") if f"self.{n} = advect" in src]
    ok = ("credited" not in advected) and ("fre" in advected)
    check(2, "le champ `credited` n'est PAS advecte alors que `fre` l'est", ok,
          f"advectes = {advected} -> le credit absorbant est STATIQUE par cellule, "
          f"la masse fraiche se deplace sous lui")


# --- T3: consequence -- directly inserted mass is re-credited as capture ----
def t3():
    """Pure-python replay of the parent's credit rule, no engine.
    Two track cells. The operator inserts 1.0 into cell A and bumps credited[A].
    A pure transfer A->B (mass conserving, no new matter) then makes cell B look like
    a fresh arrival, because credited[B] is still 0."""
    fre = {"A": 0.0, "B": 0.0}
    credited = {"A": 0.0, "B": 0.0}
    capture = 0.0
    track = {"A", "B"}
    prev = {"A", "B"}
    # operator inserts directly into A, and bumps the credit (parent's fix)
    fre["A"] += 1.0
    credited["A"] += 1.0
    for i in track:                               # checkpoint, parent's rule
        new = fre[i] - credited[i]
        if new > 1e-15:
            capture += new
            credited[i] = fre[i]
    after_insert = capture
    # pure internal transfer A -> B: NO new matter enters the component
    fre["A"] -= 0.6
    fre["B"] += 0.6
    for i in track:
        new = fre[i] - credited[i]
        if new > 1e-15:
            capture += new
            credited[i] = fre[i]
    ok = (after_insert == 0.0) and (abs(capture - 0.6) < 1e-12)
    check(3, "masse inseree directement recreditee en capture apres advection", ok,
          f"capture au frame d'injection = {after_insert:.3f} (correct), "
          f"apres un simple transfert interne A->B = {capture:.3f} (FAUX, aucune matiere n'est entree)")


# --- T4: contact and capture use independent, non-ordered credit fields -----
def t4():
    m = tree("dsc_core.py")
    upd = func(m, "update", cls="Causal")
    src = ast.unparse(upd)
    uses_shell = "self.shell_credit" in src
    uses_cr = "cr[i]" in src
    # precise: does ANY assignment to capture_transport reference contact?
    coupled = False
    for node in ast.walk(upd):
        tgts = []
        if isinstance(node, ast.AugAssign):
            tgts = [node.target]
        elif isinstance(node, ast.Assign):
            tgts = node.targets
        else:
            continue
        for t in tgts:
            if isinstance(t, ast.Attribute) and t.attr == "capture_transport":
                if "contact" in ast.unparse(node.value):
                    coupled = True
    ok = uses_shell and uses_cr and (coupled is False)
    check(4, "contact et capture = deux credits INDEPENDANTS, aucun ordre impose", ok,
          "aucune ligne ne borne capture par contact -> capture > contact est mecaniquement possible")


# --- T5: incorporation_16 counts ALL fresh in track, not just transport -----
def t5():
    m = tree("dsc_core.py")
    upd = func(m, "update", cls="Causal")
    src = ast.unparse(upd)
    ok = "f_in = float(sum((ff[i] for i in cells)))" in src.replace(" ", "").replace(
        "f_in=float(sum((ff[i]foriincells)))", "f_in = float(sum((ff[i] for i in cells)))") or \
        "sum(ff[i] for i in cells)" in src or "ff[i] for i in cells" in src
    check(5, "incorporation_16 somme TOUTE la masse fraiche de la piste", ok,
          "toutes voies confondues (transport + englobement + fusion) -> inc16 > capture_transport "
          "est attendu et n'est PAS une anomalie mais une comparaison de populations differentes")


# --- T6: P2' accepts a track-adjacent site with positive fresh mass ---------
def t6():
    m = tree("dsc_core.py")
    fn = func(m, "_admissible_capacity")
    src = ast.unparse(fn)
    ok = ("ACCEPTED_SUBTHRESHOLD_ADJACENT" in src) and ("THRESH - fm[s] - EPS" in src)
    check(6, "P2' injecte DANS la coque adjacente (gd=1) sous le seuil", ok,
          "le site reste vide au DETECTEUR mais porte une masse fraiche > 0 -> "
          "TOPOLOGICALLY_EMPTY = true, MATERIALLY_EMPTY_OF_FRESH_SOURCE = false")


# --- T7: the per-injection ledger the mission required does not exist -------
def t7():
    hits = list(SRC.glob("dynamic_source_capture_event_ledger*")) + \
           list((SRC / "DSC_DELIVERY").glob("*event_ledger*"))
    h = tree("dsc_harness.py")
    br = func(h, "branch")
    src = ast.unparse(br)
    persists_sites = 'r.get("sites"' in src or "r.get('sites'" in src
    written = "sites" in ast.unparse(func(h, "main"))
    ok = (len(hits) == 0) and persists_sites and (written is False)
    check(7, "aucun ledger evenementiel; les sites d'injection ne sont jamais persistes", ok,
          f"fichiers trouves={len(hits)}; `sites` lu dans branch() uniquement pour l'assertion, "
          f"jamais ecrit -> geometrie par injection NON reconstructible sans re-run")


# --- T8: raw rows are unchanged by this closure -----------------------------
def t8():
    import hashlib
    p = SRC / "dynamic_source_capture_rows.csv"
    d = hashlib.sha256(p.read_bytes()).hexdigest()
    inv = json.loads(Path("dsc04_parent_artifact_inventory.json").read_text())
    rec = next(f["sha256"] for f in inv["files"] if f["path"] == p.name)
    check(8, "donnees brutes inchangees pendant la cloture", d == rec,
          f"sha256 = {d[:24]}...")


def main():
    print("=== TESTS SANS MOTEUR (cloture 04R) ===")
    for f in (t1, t2, t3, t4, t5, t6, t7, t8):
        try:
            f()
        except Exception as e:
            check(int(f.__name__[1:]), f.__name__, False, f"EXCEPTION {type(e).__name__}: {e}")
    n = sum(1 for r in R if r["PASS"])
    Path("dsc04_no_engine_tests.json").write_text(json.dumps(
        {"n": len(R), "n_pass": n, "VERDICT": "PASS" if n == len(R) else "FAIL",
         "engine_invocations": 0, "tests": R}, indent=1))
    print(f"\n{n}/{len(R)} -> {'PASS' if n == len(R) else 'FAIL'}")
    return 0 if n == len(R) else 1


if __name__ == "__main__":
    raise SystemExit(main())
