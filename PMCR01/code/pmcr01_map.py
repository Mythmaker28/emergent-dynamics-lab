"""PMCR01 Gate 0 — the executable Y channel map, in the mandated field set.

Every field is filled from the static discovery or from a mutation oracle. Where a field
cannot be filled from evidence it says so; it is never filled from a parameter's name.
"""
from __future__ import annotations

import json

OUT = "/home/claude/PMCR01/out"

FIELDS = ("NAME", "DECLARATION_LOCATION", "MANIFEST_FIELD", "DEFAULT_VALUE",
          "ADMISSIBLE_RANGE", "CONSTRUCTOR_PATH", "SCHEDULER_EVENT", "STATE_DELTA",
          "RESOURCE_OR_CAPACITY_DEPENDENCE", "EVENT_ORDER",
          "CAN_BE_NONZERO_WITHOUT_CODE_CHANGE", "CAN_BE_VARIED_WITHOUT_CHANGING_X_BASELINE",
          "INDEPENDENTLY_CONTROLLABLE", "MUTATION_ORACLE_RESULT", "FINAL_CLASS")

PATH_KY = ("obtc02_protocol.yaml point.kY -> gate_obtc02.load() -> SPEC['point']['kY'] -> "
           "protocol_obtc02.spec_for() {k: PT[k] for k in (...,'kY')} -> "
           "lawspec_v2.spec_with() -> type('SpecVariant',(kinetics.Spec,),d) -> "
           "World.sp.kY -> engine_obtc.WorldOBTC._react_core")
PATH_MUY = PATH_KY.replace("kY", "muY").replace("_react_core", "_decay_core")

CH = [
    {"NAME": "kY  (minority birth coefficient)",
     "DECLARATION_LOCATION": "ORR01/code/kinetics.py, class Spec, line 44",
     "MANIFEST_FIELD": "obtc02_protocol.yaml -> point.kY",
     "DEFAULT_VALUE": "0.0 at the qualified point (1.9511206603301162e-05 in the inherited "
                      "MTW01 Spec, a different and non-portable point)",
     "ADMISSIBLE_RANGE": "[0, inf). p = min(1, kY nX nY) is clamped, so values above "
                         "1/(nX nY) only saturate. No assert or raise restricts it.",
     "CONSTRUCTOR_PATH": PATH_KY,
     "SCHEDULER_EVENT": "_react_core, loop tuple ('Y','SY',sp.kY): "
                        "p = min(1, kY * nX * nY) ; births = Binomial(min(nSY, free0), p)",
     "STATE_DELTA": "n['SY'] -= births ; n['Y'] += births   (occupancy conserved)",
     "RESOURCE_OR_CAPACITY_DEPENDENCE": "candidates are min(nSY, free) at the Y's OWN cell; "
                                        "free = CAP - occupancy; both must be >= 1",
     "EVENT_ORDER": "5th of 7: diffuse X, Y, SX, SY -> REACT -> decay -> exchange",
     "CAN_BE_NONZERO_WITHOUT_CODE_CHANGE": True,
     "CAN_BE_VARIED_WITHOUT_CHANGING_X_BASELINE":
         "PARTIAL. Same-step isolated (the X branch is drawn first, arguments bit-identical). "
         "NOT isolated across steps: p_X = min(1, kX nX nY) reads nY, and a surviving Y birth "
         "adds a source cell once it separates.",
     "INDEPENDENTLY_CONTROLLABLE": "yes, with respect to muY: different field, different "
                                   "operator, disjoint captured hazard arguments",
     "MUTATION_ORACLE_RESULT": "PASS (hazard 0 -> 1, dY 0 -> +4 = min(nSY,free), reversal "
                               "bit-exact)",
     "FINAL_CLASS": "DORMANT_BUT_REACHABLE_CHANNEL"},

    {"NAME": "muY (minority removal probability)",
     "DECLARATION_LOCATION": "ORR01/code/kinetics.py, class Spec, line 42",
     "MANIFEST_FIELD": "obtc02_protocol.yaml -> point.muY",
     "DEFAULT_VALUE": "0.0 at the qualified point (1.9511206603301160e-06 in MTW01)",
     "ADMISSIBLE_RANGE": "[0, 1]; it is the p of rng.binomial(n_Y, muY)",
     "CONSTRUCTOR_PATH": PATH_MUY,
     "SCHEDULER_EVENT": "_decay_core, loop tuple ('Y','WY',sp.muY): "
                        "d = Binomial(n['Y'], muY)",
     "STATE_DELTA": "n['Y'] -= d ; n['WY'] += d   (occupancy conserved)",
     "RESOURCE_OR_CAPACITY_DEPENDENCE": "none. It reads no resource, no capacity, no "
                                        "position, no age and no lineage label.",
     "EVENT_ORDER": "6th of 7, AFTER _react: newborns are exposed to decay in their birth step",
     "CAN_BE_NONZERO_WITHOUT_CODE_CHANGE": True,
     "CAN_BE_VARIED_WITHOUT_CHANGING_X_BASELINE":
         "PARTIAL, same reason as kY: removing a Y removes a source cell.",
     "INDEPENDENTLY_CONTROLLABLE": "yes with respect to kY; NO with respect to itself — it "
                                   "sets the founder clock and the newborn clock with one "
                                   "number (see the timescale-collapse finding)",
     "MUTATION_ORACLE_RESULT": "PASS (hazard 0 -> 1, dY 0 -> -1, reversal bit-exact)",
     "FINAL_CLASS": "DORMANT_BUT_REACHABLE_CHANNEL"},

    {"NAME": "p_hop_Y (minority transport)",
     "DECLARATION_LOCATION": "ORR01/code/kinetics.py, class Spec, line 40",
     "MANIFEST_FIELD": "NONE. There is no p_hop_Y key in obtc02_protocol.yaml.",
     "DEFAULT_VALUE": "protocol_obtc02.spec_for: 0.0 under the declared immobilisation "
                      "intervention, otherwise PT['p_hop'] = 0.10263340389897246",
     "ADMISSIBLE_RANGE": "[0, 1] at the engine level; {0, p_hop_X} at the protocol level",
     "CONSTRUCTOR_PATH": "obtc02_protocol.yaml point.p_hop -> spec_for -> d['p_hop_Y'] = "
                         "0.0 if immobile_organiser else PT['p_hop'] -> Spec.p_hop_Y -> "
                         "_diffuse('Y', sp.p_hop_Y)",
     "SCHEDULER_EVENT": "_diffuse('Y', p_hop_Y): four sequential passes in the frozen order "
                        "((1,0),(-1,0),(1,1),(-1,1)), each Binomial(n, p_hop/4), accepting "
                        "min(movers, dest_free) per cell",
     "STATE_DELTA": "n['Y'] redistributed; the COUNT is conserved",
     "RESOURCE_OR_CAPACITY_DEPENDENCE": "acceptance is capped by dest_free at the destination",
     "EVENT_ORDER": "2nd of 7",
     "CAN_BE_NONZERO_WITHOUT_CODE_CHANGE": "at the engine level yes; through the qualified "
                                           "protocol only 0 or p_hop_X",
     "CAN_BE_VARIED_WITHOUT_CHANGING_X_BASELINE":
         "NO as a continuous control. spec_for exposes exactly two values: 0.0 (condition S) "
         "and p_hop_X (condition M). It is NOT a blanket alias -- 0 != p_hop_X -- but only "
         "{0, p_hop_X} are reachable through the frozen protocol, and at the engine level it "
         "shifts the shared random stream so the X draws of the same step move with it.",
     "INDEPENDENTLY_CONTROLLABLE": "two protocol-fixed values only; not a continuous Y "
                                   "separation clock",
     "MUTATION_ORACLE_RESULT": "PASS as a transport channel (hazard 0 -> 0.25, count "
                               "conserved, configuration set changes, reversal bit-exact); "
                               "and spec_for(immobile=True/False) gives {0.0, p_hop_X}",
     "FINAL_CLASS": "PARTIALLY_WIRED",
     "CLASS_NOTE": "reachable but protocol-restricted to {0, p_hop_X}; not an independent "
                   "continuous timescale"},

    {"NAME": "organiser_off_at (declared intervention)",
     "DECLARATION_LOCATION": "OBTC02/code/engine_obtc.py, WorldOBTC._one_step, lines 222-229",
     "MANIFEST_FIELD": "window.SOURCE_OFF_AT, used only in condition R",
     "DEFAULT_VALUE": "None outside condition R; 4000 in condition R",
     "ADMISSIBLE_RANGE": "any step index, or None",
     "CONSTRUCTOR_PATH": "protocol_obtc02.run_arm -> EN.fresh_world(organiser_off_at=off)",
     "SCHEDULER_EVENT": "after _one_step: n['Y'] -= y ; n['WY'] += y, all Y at once",
     "STATE_DELTA": "the whole Y field is moved to WY, once",
     "RESOURCE_OR_CAPACITY_DEPENDENCE": "none",
     "EVENT_ORDER": "after the seven operators, once",
     "CAN_BE_NONZERO_WITHOUT_CODE_CHANGE": True,
     "CAN_BE_VARIED_WITHOUT_CHANGING_X_BASELINE": "NO — it is designed to abolish the source",
     "INDEPENDENTLY_CONTROLLABLE": "it is a one-shot removal, not a rate; it cannot define a "
                                   "timescale",
     "MUTATION_ORACLE_RESULT": "not run: it is a declared intervention already exercised by "
                               "condition R, and it is not a persistence control",
     "FINAL_CLASS": "ACTIVE_EXISTING_CHANNEL (intervention, not a rate)"},

    {"NAME": "S0 and phi (substrate set-point and exchange rate for SY)",
     "DECLARATION_LOCATION": "kinetics.Spec.S0, Spec.phi",
     "MANIFEST_FIELD": "point.S0 = 3, point.phi = 0.2",
     "DEFAULT_VALUE": "3 and 0.2",
     "ADMISSIBLE_RANGE": "S0 in [0, CAP]; phi in [0, 1]",
     "CONSTRUCTOR_PATH": "manifest -> spec_for -> spec_with -> Spec -> WorldV2._exchange",
     "SCHEDULER_EVENT": "_exchange: for s in ('SX','SY'): offers[s] = "
                        "Binomial(max(S0 - n[s], 0), phi)",
     "STATE_DELTA": "SY inserted and an equal number of units removed from {SX,SY,WX,WY}",
     "RESOURCE_OR_CAPACITY_DEPENDENCE": "it IS the resource operator",
     "EVENT_ORDER": "7th of 7",
     "CAN_BE_NONZERO_WITHOUT_CODE_CHANGE": True,
     "CAN_BE_VARIED_WITHOUT_CHANGING_X_BASELINE":
         "NO. The loop 'for s in (\"SX\",\"SY\")' applies the SAME S0 and the SAME phi to both "
         "substrates. The Y substrate supply cannot be moved without moving the X substrate "
         "supply identically.",
     "INDEPENDENTLY_CONTROLLABLE": False,
     "MUTATION_ORACLE_RESULT": "not applicable as a Y-specific control: it is provably shared",
     "FINAL_CLASS": "ALIASED_OR_NOT_INDEPENDENT"},

    {"NAME": "omega (waste outflow)",
     "DECLARATION_LOCATION": "kinetics.Spec.omega",
     "MANIFEST_FIELD": "point.omega = 0.05",
     "DEFAULT_VALUE": "0.05",
     "ADMISSIBLE_RANGE": "[0, 1]",
     "CONSTRUCTOR_PATH": "manifest -> spec_for -> spec_with -> Spec.omega",
     "SCHEDULER_EVENT": "read ONLY in kinetics.World._feed_and_outflow and in the v1 branch "
                        "of WorldV2._feed_and_outflow, both of which are bypassed under "
                        "LAWSPEC_V2_EXCHANGE",
     "STATE_DELTA": "none under the qualified LawSpec",
     "RESOURCE_OR_CAPACITY_DEPENDENCE": "n/a",
     "EVENT_ORDER": "n/a",
     "CAN_BE_NONZERO_WITHOUT_CODE_CHANGE": True,
     "CAN_BE_VARIED_WITHOUT_CHANGING_X_BASELINE": "trivially yes: it changes nothing at all",
     "INDEPENDENTLY_CONTROLLABLE": False,
     "MUTATION_ORACLE_RESULT": "PROVED INERT: omega 0.0 vs 0.9 gives an identical final state "
                               "hash and an identical captured hazard sequence",
     "FINAL_CLASS": "SCHEMA_ONLY_INERT"},

    {"NAME": "exchangeable-pool membership of Y (the chemostat's removal set)",
     "DECLARATION_LOCATION": "lawspec_v2.py EXCHANGEABLE_DEFAULT (38) / EXCHANGEABLE_WITH_BODY "
                             "(39); WorldV2.__init__ exchangeable= argument (74-79)",
     "MANIFEST_FIELD": "none; it is a CONSTRUCTOR ARGUMENT, bound at protocol_obtc02.py:79-81 "
                       "to V2.EXCHANGEABLE_DEFAULT = ('SX','SY','WX','WY')",
     "DEFAULT_VALUE": "('SX','SY','WX','WY') -- Y excluded",
     "ADMISSIBLE_RANGE": "any subset of the six species; EXCHANGEABLE_WITH_BODY additionally "
                         "includes X (a declared washout control)",
     "CONSTRUCTOR_PATH": "protocol_obtc02.run_arm -> EN.fresh_world(exchangeable=...) -> "
                         "WorldV2._exchange, _hyper_split over self.exchangeable",
     "SCHEDULER_EVENT": "_exchange removes k = min(want, avail) units without replacement from "
                        "the pool; a Y in the pool would be removed with per-Y hazard ~ k/avail",
     "STATE_DELTA": "if Y were in the pool: n['Y'] -= taken_Y (occupancy conserved)",
     "RESOURCE_OR_CAPACITY_DEPENDENCE": "reads local composition and crowding at the cell",
     "EVENT_ORDER": "7th of 7",
     "CAN_BE_NONZERO_WITHOUT_CODE_CHANGE": ("YES -- passing exchangeable=('SX','SY','WX','WY',"
                                            "'Y') is a legal constructor argument, zero code "
                                            "change. This is the SAME status (argument binding, "
                                            "not code fact) that p_hop_Y has."),
     "CAN_BE_VARIED_WITHOUT_CHANGING_X_BASELINE":
         "NO. _exchange treats the whole pool jointly; adding Y changes the hypergeometric "
         "split for SX and SY and therefore the X substrate supply.",
     "INDEPENDENTLY_CONTROLLABLE": False,
     "MUTATION_ORACLE_RESULT": "not run as a persistence control: its polarity is WRONG for a "
                               "minority window -- it removes Y fastest in the crowded source "
                               "cell, i.e. exactly where the lineage must persist",
     "FINAL_CLASS": "DORMANT_BUT_REACHABLE_CHANNEL",
     "CLASS_NOTE": "a removal, but polarity-wrong for a minority window; listed so Gate 0 is "
                   "not overclaimed as exhaustive over code FACTS -- it is exhaustive under "
                   "the frozen argument binding at protocol_obtc02.py:79-81"},

    {"NAME": "a Y-specific precursor pool, or a Y removal that reads age, position or contact",
     "DECLARATION_LOCATION": "does not exist",
     "MANIFEST_FIELD": "none",
     "DEFAULT_VALUE": "n/a",
     "ADMISSIBLE_RANGE": "n/a",
     "CONSTRUCTOR_PATH": "there is none",
     "SCHEDULER_EVENT": "_decay_core draws Binomial(n['Y'], muY) over the whole Y field. It "
                        "reads no age, no position, no contact and no lineage label. Y is "
                        "absent from EXCHANGEABLE_DEFAULT and from EXCHANGEABLE_WITH_BODY, so "
                        "the chemostat cannot remove it either.",
     "STATE_DELTA": "n/a",
     "RESOURCE_OR_CAPACITY_DEPENDENCE": "n/a",
     "EVENT_ORDER": "n/a",
     "CAN_BE_NONZERO_WITHOUT_CODE_CHANGE": False,
     "CAN_BE_VARIED_WITHOUT_CHANGING_X_BASELINE": "n/a",
     "INDEPENDENTLY_CONTROLLABLE": False,
     "MUTATION_ORACLE_RESULT": "n/a — there is nothing to perturb",
     "FINAL_CLASS": "ABSENT_REQUIRES_ARCHITECTURE_CHANGE"},
]


def main():
    static = json.load(open(f"{OUT}/_gate0_static.json"))
    orc = json.load(open(f"{OUT}/PMCR01_MUTATION_ORACLE_REPORT.json"))
    out = {
        "SECTION": "PMCR01 Gate 0 — executable Y channel map",
        "METHOD": ("AST walk over the COMMITTED blobs for every write to self.n[species], "
                   "including species-loop writes; then a deterministic mutation oracle per "
                   "alleged channel on a NON_SCIENTIFIC_SEMANTIC_FIXTURE."),
        "SCOPE_OF_EXHAUSTIVENESS": (
            "the Y-changing EVENTS are exhaustive over the code. Which of them is ACTIVE also "
            "depends on two constructor argument bindings fixed at protocol_obtc02.py:79-81: "
            "lawspec = LAWSPEC_V2_EXCHANGE (which bypasses omega) and exchangeable = "
            "EXCHANGEABLE_DEFAULT (which excludes Y from chemostat removal). Both are argument "
            "values, not code facts, and both are listed as channels so nothing is hidden."),
        "ANALYSED_BLOBS": static["ANALYSED_BLOBS"],
        "SCHEDULER_ORDER": static["SCHEDULER_ORDER"],
        "MANIFEST_POINT": static["MANIFEST_POINT"],
        "ADMISSIBILITY_CHECKS_MENTIONING_Y": static["ADMISSIBILITY_CHECKS_MENTIONING_Y"],
        "NO_GUARD_REFUSES_A_NONZERO_kY_OR_muY":
            len(static["ADMISSIBILITY_CHECKS_MENTIONING_Y"]) == 0,
        "CHANNELS": CH,
        "CLASS_COUNTS": {},
        "K_Y_PATH": "ACTIVE_CONSTRUCTOR_TO_SCHEDULER (rate zero at the qualified point) "
                    "= DORMANT_BUT_REACHABLE_CHANNEL",
        "MU_Y_PATH": "ACTIVE_CONSTRUCTOR_TO_SCHEDULER (rate zero at the qualified point) "
                     "= DORMANT_BUT_REACHABLE_CHANNEL",
        "ORACLE_SUMMARY": [{k: o[k] for k in ("CHANNEL", "FIELD", "KIND", "PASS")}
                           for o in orc["ORACLES"]],
        "SENTINEL": orc["SENTINEL"],
    }
    for c in CH:
        out["CLASS_COUNTS"][c["FINAL_CLASS"]] = out["CLASS_COUNTS"].get(c["FINAL_CLASS"], 0) + 1
    json.dump(out, open(f"{OUT}/PMCR01_EXECUTABLE_Y_CHANNEL_MAP.json", "w"), indent=1,
              default=str)

    md = ["# PMCR01 — carte des canaux `Y` exécutables", "",
          "> Méthode : parcours AST des **blobs committés** pour toute écriture sur",
          "> `self.n[espèce]`, y compris celles dont l'espèce est une variable de boucle —",
          "> c'est précisément là que vivent la naissance et la mort de `Y`. Puis un oracle de",
          "> mutation déterministe par canal allégué, sur `NON_SCIENTIFIC_SEMANTIC_FIXTURE`.", "",
          "```", "ordre de l'ordonnanceur (kinetics.World._one_step) :"]
    for c in static["SCHEDULER_ORDER"]["order"]:
        md.append("   %-18s %s" % (c["call"], c["args"]))
    md += ["```", "",
           "Aucun `assert` ni `raise` de la chaîne exécutable ne mentionne `kY`, `muY` ou",
           "`p_hop_Y` : **rien dans le code ne refuse une valeur non nulle**.", ""]
    for c in CH:
        md += ["## %s" % c["NAME"], "", "| champ | valeur |", "|---|---|"]
        for f in FIELDS[1:]:
            v = str(c[f]).replace("\n", " ")
            md.append("| `%s` | %s |" % (f, v))
        md.append("")
    md += ["## Décompte des classes", "", "| classe | n |", "|---|---|"]
    for k, v in sorted(out["CLASS_COUNTS"].items()):
        md.append("| `%s` | %d |" % (k, v))
    md += ["", "```", "K_Y_PATH  = %s" % out["K_Y_PATH"], "MU_Y_PATH = %s" % out["MU_Y_PATH"],
           "```", ""]
    open(f"{OUT}/PMCR01_EXECUTABLE_Y_CHANNEL_MAP.md", "w").write("\n".join(md) + "\n")

    print("channels mapped: %d" % len(CH))
    for k, v in sorted(out["CLASS_COUNTS"].items()):
        print("   %-42s %d" % (k, v))
    print("K_Y_PATH  = %s" % out["K_Y_PATH"])
    print("MU_Y_PATH = %s" % out["MU_Y_PATH"])


if __name__ == "__main__":
    main()
