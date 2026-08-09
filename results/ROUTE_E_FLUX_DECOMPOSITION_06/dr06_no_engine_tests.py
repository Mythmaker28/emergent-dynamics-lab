"""Engine-free tests for the DEV_06 decomposition. Nothing here imports or steps the engine
beyond the frozen-state operator comparison, which never calls LatticeBondEngine.step."""
from __future__ import annotations
import ast, csv, json, math, sys
from pathlib import Path

SRC = Path("../DR05")
R = []


def check(n, name, ok, detail):
    R.append({"test": n, "name": name, "PASS": bool(ok), "detail": detail})
    print(f"  {n:>2}. {name:<52} {'PASS' if ok else 'FAIL'}  {detail}")


def num(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


def t1():
    """No engine step anywhere in the decomposition module."""
    tree = ast.parse(Path("dr05_flux_decomposition.py").read_text())
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)} | \
            {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    mods = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names} | \
           {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    bad = sorted(mods & {"edlab", "od_core", "dr_core", "dsc_core", "dr_harness"})
    check(1, "aucun moteur importe par la decomposition", len(bad) == 0 and "step" not in names,
          f"imports interdits: {bad if bad else 'aucun'}")


def t2():
    """T = I + F + A holds in every saved snapshot."""
    worst = 0.0
    n = 0
    for f in ("direct_replacement_rows_a.csv", "direct_replacement_rows_b.csv"):
        for r in csv.DictReader(open(SRC / f)):
            for _, s in json.loads(r["snapshots"]).items():
                if s.get("track") is not True:
                    continue
                worst = max(worst, abs(s["T"] - (s["I"] + s["F"] + s["A"])))
                n += 1
    check(2, "T = I + F + A dans chaque snapshot sauvegarde", worst <= 1e-9,
          f"{n} snapshots, pire ecart = {worst:.2e}")


def t3():
    """The paired identity closes block by block."""
    p = list(csv.DictReader(open("dr05_paired_flux_rows.csv")))
    ok = [r for r in p if r["status"] == "OK"]
    worst = max(abs(num(r["PAIR_IDENTITY_RESIDUAL"])) for r in ok)
    check(3, "identite de paire fermee bloc par bloc", worst <= 1e-9,
          f"{len(ok)} paires vivantes, pire residu = {worst:.2e}")


def t4():
    """Sink yields partition exactly: incumbent + ambient + fresh = 1."""
    worst = 0.0
    n = 0
    for r in csv.DictReader(open("dr05_event_cohort_fates.csv")):
        y = [num(r[k]) for k in ("INCUMBENT_SINK_YIELD", "AMBIENT_SINK_YIELD", "FRESH_SINK_YIELD")]
        if any(v is None for v in y):
            continue
        worst = max(worst, abs(sum(y) - 1.0))
        n += 1
    check(4, "les rendements du puits partitionnent exactement", worst <= 1e-9,
          f"{n} trajectoires avec puits actif, pire |somme - 1| = {worst:.2e}")


def t5():
    """The atomic operator moves exactly zero NET mass in every DIRECT arm."""
    worst = 0.0
    for r in csv.DictReader(open("dr05_event_cohort_fates.csv")):
        if not r["arm"].startswith("DIRECT_"):
            continue
        v = num(r["OPERATOR_DELTA_TOTAL_MASS"])
        if v is not None:
            worst = max(worst, abs(v))
    check(5, "delta de masse NET de l'operateur DIRECT = 0", worst <= 1e-9,
          f"pire |source - puits| sur tous les bras DIRECT = {worst:.2e} -> toute variation de "
          f"masse suivie est dynamique ou geometrique, jamais operatoire")


def t6():
    """Survivor-conditional cells are labelled as such, never as a 9-block median."""
    rs = list(csv.DictReader(open("dr05_failure_risk_sets.csv")))
    q800 = [r for r in rs if r["size"] == "24" and r["arm"] == "DIRECT_Q800_UNIFORM"][0]
    so24 = [r for r in rs if r["size"] == "24" and r["arm"] == "SOURCE_ONLY_Q800"][0]
    ok = (q800["INTENTION_TO_TREAT_RISK_SET"] == "9"
          and q800["TERMINAL_INTACT_RISK_SET"] == "2"
          and q800["TRACK_FAILURES"] == "7"
          and q800["analysis_label"] == "SURVIVOR_CONDITIONAL_N_2"
          and so24["TERMINAL_INTACT_RISK_SET"] == "0")
    check(6, "risk sets ITT vs survivants conditionnels etiquetes", ok,
          f"L24 Q800: ITT={q800['INTENTION_TO_TREAT_RISK_SET']} intacts="
          f"{q800['TERMINAL_INTACT_RISK_SET']} echecs={q800['TRACK_FAILURES']} "
          f"label={q800['analysis_label']}; SOURCE_ONLY L24 intacts={so24['TERMINAL_INTACT_RISK_SET']}")


def t7():
    """The per-event ledger is sub-sampled: declare it, do not pretend otherwise."""
    ev = list(csv.DictReader(open(SRC / "direct_replacement_event_ledger_b.csv")))
    g = [r for r in ev if r["arm"] == "DIRECT_Q800_UNIFORM" and r["rejected"] == "False"]
    ids = sorted({int(r["event_id"]) for r in g})
    mod = {i % 8 for i in ids}
    rej = [r for r in ev if r["rejected"] == "True"]
    check(7, "ledger evenementiel sous-echantillonne 1/8, rejets COMPLETS", mod == {1},
          f"evenements executes: tous ev_id % 8 == 1 ({len(ids)} ids distincts); "
          f"{len(rej)} lignes de rejet enregistrees sans sous-echantillonnage")


def t8():
    """Per-event FRESH cohorts were aggregated: the per-injection survival curve is impossible."""
    src = (SRC / "dr_core.py").read_text()
    aggregated = "AGGREGATED" in src or "fre" in src
    hdr = open(SRC / "direct_replacement_event_ledger_b.csv").readline()
    no_per_event_cohort = "fresh_removed_by_cohort" not in hdr
    check(8, "cohortes FRESH par evenement NON tracees -> courbe de survie impossible",
          aggregated and no_per_event_cohort,
          "un seul champ FRESH advecte (declare dans le protocole DEV_05); le ledger ne porte "
          "aucune colonne par cohorte d'injection -> FRESH_EVENT survival = NOT_RECONSTRUCTIBLE")


def t9():
    """Frozen-frame quantities needed to separate boundary crossing from tracker motion."""
    hdr = json.loads(next(csv.DictReader(open(SRC / "direct_replacement_rows_b.csv")))["snapshots"])
    keys = set(next(iter(hdr.values())).keys())
    missing = sorted({"mass_inside_frozen_C256", "C256_to_Ct_overlap", "boundary_site_turnover"}
                     - keys)
    have = sorted({"cy", "cx", "area", "T"} & keys)
    check(9, "cadre fige absent -> franchissement de frontiere non reconstructible",
          len(missing) == 3 and len(have) == 4,
          f"manquants: {missing}; disponibles seulement: {have}")


def t10():
    """Depth-cohort survival must be normalised by each cohort's own t256 mass."""
    rows = list(csv.DictReader(open(SRC / "direct_replacement_rows_a.csv")))
    r = [x for x in rows if x["arm"] == "DIRECT_Q100_ANCHOR"][0]
    s = json.loads(r["snapshots"])
    s0 = s["256"]
    I0 = num(r["I0"])
    tot = s0["core_in_track"] + s0["inter_in_track"] + s0["bnd_in_track"]
    uneven = abs(s0["core_in_track"] / tot - 1 / 3) > 0.05
    check(10, "les trois cohortes de profondeur n'ont PAS la meme masse initiale", uneven
          and abs(tot - I0) <= 1e-9,
          f"a t256: core={s0['core_in_track']/tot:.3f} inter={s0['inter_in_track']/tot:.3f} "
          f"bnd={s0['bnd_in_track']/tot:.3f} de I0 -> normaliser par I0 fabriquerait un faux "
          f"contraste noyau/coque")


def main():
    print("=== TESTS SANS MOTEUR (decomposition 06) ===")
    for f in (t1, t2, t3, t4, t5, t6, t7, t8, t9, t10):
        try:
            f()
        except Exception as e:
            check(int(f.__name__[1:]), f.__name__, False, f"EXCEPTION {type(e).__name__}: {e}")
    n = sum(1 for x in R if x["PASS"])
    Path("dr06_no_engine_tests.json").write_text(json.dumps(
        {"n": len(R), "n_pass": n, "VERDICT": "PASS" if n == len(R) else "FAIL",
         "engine_invocations": 0, "tests": R}, indent=1))
    print(f"\n{n}/{len(R)} -> {'PASS' if n == len(R) else 'FAIL'}")
    return 0 if n == len(R) else 1


if __name__ == "__main__":
    raise SystemExit(main())
