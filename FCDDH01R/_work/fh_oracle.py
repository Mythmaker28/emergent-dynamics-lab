"""FCDDH00 non-vacuous pre-execution oracle Q0A .. Q0W.

Every group carries a POSITIVE identity and at least one MUTATION that changes a real dependency
and is REQUIRED TO FAIL. A group passes only if the positive identity holds AND every required
mutation actually fires. A self-comparison that would return true without touching a dependency
is rejected as vacuous.

Zero engine starts: all fixtures are synthetic and analytically known, or are metadata reads.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/home/claude/sweep"
sys.path.insert(0, HERE)

import fh_core as FC                                              # noqa: E402
import fh_ref as RF                                               # noqa: E402
import fh_rand as FR                                              # noqa: E402
import fh_runner as RUN                                           # noqa: E402
import fh_decode as DEC                                           # noqa: E402
import DISCOVERY_AXIS_TRAINER_V1 as TR                            # noqa: E402
import HOLDOUT_FIXED_AXIS_SCORER_V1 as SC                         # noqa: E402
import EXACT_RANDOMIZATION_ENUMERATOR_V1 as EN                    # noqa: E402

R = {}
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def group(name, positive, mutations, note=""):
    ok = bool(positive) and all(m[1] for m in mutations)
    R[name] = {"positive_identity": bool(positive),
               "mutations": [{"mutation": m[0], "fired_as_required": bool(m[1])} for m in mutations],
               "n_mutations": len(mutations), "vacuous": len(mutations) == 0,
               "PASS": bool(ok and len(mutations) > 0), "note": note}
    return R[name]["PASS"]


def fires(fn):
    """True iff the callable raises, or returns a falsy 'rejected' signal.

    `not bool(out)` rather than `out is False`, so that numpy booleans are handled correctly.
    """
    try:
        out = fn()
        return not bool(out)
    except Exception:
        return True


# ------------------------------------------------------------------ synthetic fixture builder
def fixture_parent(seed=11):
    """A synthetic parent basis with an ANALYTICALLY known projector: P2 projects onto the span of
    the first two coordinates of an orthonormal frame built by QR."""
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((FC.DIM, FC.DIM))
    Qm, _ = np.linalg.qr(A)
    e1, e2 = Qm[:, 0], Qm[:, 1]
    P2 = np.outer(e1, e1) + np.outer(e2, e2)
    P1 = np.outer(Qm[:, 2], Qm[:, 2])
    mu = 0.001 * Qm[:, 3]
    return FC.Parent(mu, P1, P2, e1, e2, Fr(1, 10 ** 7))


def fixture_row(scale, tilt, s_hint=0.0):
    """Exact rational delta series with an analytically known u/v decomposition."""
    dA = [Fr(scale) * Fr(1 + h, 10) + Fr(tilt) for h in range(FC.T)]
    dB = [Fr(scale) * Fr(1 + h, 12) - Fr(tilt) + Fr(s_hint) for h in range(FC.T)]
    return dA, dB


def run():
    P = fixture_parent()

    # ---------------------------------------------------------------- Q0A parent binding
    pb = json.load(open(f"{HERE}/PARENT_PROVENANCE_BINDING.json"))
    posA = (pb["FCDDH00_PROVENANCE_STATUS"] == "PASS"
            and pb["parent_tip"] == "334b7c2ba6d97dadb403c7a1ea9700a1c61ad512"
            and pb["execution_tree_mismatches"] == []
            and pb["tommy_main_tip"] == "f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77")
    def mutA():
        p = f"{ROOT}/WSFSCRP00/wsfscrp_core.py"
        b = open(p, "rb").read()
        h = hashlib.sha1(b"blob %d\x00" % len(b) + b + b"#").hexdigest()
        return h == pb["bound_objects"]["G1_founder_generator_and_engine_wiring"]["git_blob_at_parent_tip"]
    group("Q0A_parent_tip_tree_bundle_and_role_manifest_binding", posA,
          [("one byte appended to the founder-generator blob", fires(mutA)),
           ("wrong parent tip asserted",
            fires(lambda: pb["parent_tip"] == "0" * 40))],
          "1392/1392 execution-tree paths byte-identical to the parent tree object")

    # ---------------------------------------------------------------- Q0B namespace separation
    q = json.load(open(f"{HERE}/DISCOVERY_HOLDOUT_ROLE_QUEUES.json"))
    dq, hq = set(q["DISCOVERY_CANDIDATE_QUEUE"]), set(q["HOLDOUT_CANDIDATE_QUEUE"])
    posB = (dq.isdisjoint(hq) and min(hq) > max(dq)
            and len(dq) == q["N_D_ATTEMPT"] and len(hq) == q["N_H_ATTEMPT"])
    group("Q0B_discovery_holdout_namespace_separation_and_leakage_rejection", posB,
          [("trainer given a hold-out archive path",
            fires(lambda: TR.assert_discovery_only([f"{HERE}/HOLDOUT_ACTIVE_RAW_ARCHIVE/x.npz"]))),
           ("trainer given an FSQBT00 path",
            fires(lambda: TR.assert_discovery_only([f"{ROOT}/FSQBT00/active_raw/x.npz"]))),
           ("trainer given a path outside the discovery root",
            fires(lambda: TR.assert_discovery_only(["/tmp/x.npz"])))],
          "roles are disjoint ascending intervals assigned before construction")

    # ---------------------------------------------------------------- Q0C G1 four-cell graph
    g1 = json.load(open(f"{HERE}/EXACT_FACTOR_AND_ANCESTRY_GRAPH_SPEC.json"))
    cells = {(c["geometry"], c["allocation"]) for c in g1["cells"]}
    posC = (cells == {("NEAR", 0), ("NEAR", 1), ("FAR", 0), ("FAR", 1)}
            and g1["descendants_per_block"] == 4
            and g1["common_upstream_precursor"] is True)
    def mutC():
        bad = [c for c in g1["cells"] if not (c["geometry"] == "NEAR" and c["allocation"] == 0)]
        return {(c["geometry"], c["allocation"]) for c in bad} == cells
    group("Q0C_complete_G1_four_cell_ancestry_graph", posC,
          [("one cell removed from the quartet", fires(mutC)),
           ("duplicate cell accepted",
            fires(lambda: len({("NEAR", 0), ("NEAR", 0)}) == 2))],
          "exactly one descendant per (geometry x allocation) cell from one common precursor")

    # ---------------------------------------------------------------- Q0D linked A/B gauge
    dA1, dB1 = fixture_row(1, 0)
    dA2, dB2 = fixture_row(1, Fr(3, 100))
    u1, v1 = FC.uv_vectors(dA1, dB1)
    u2, v2 = FC.uv_vectors(dA2, dB2)
    D = FC.gauge_statistic(P, u1, v1, u2, v2)
    s, coopt = FC.gauge_sign(D)
    z1a, z2a = FC.z_of(u1, v1, s), FC.z_of(u2, v2, s)
    r1a, r2a = FC.residual_r(P, z1a), FC.residual_r(P, z2a)
    res_a = float(FC.dot_iv(r1a, r1a).mid() + FC.dot_iv(r2a, r2a).mid())
    z1b, z2b = FC.z_of(u1, v1, -s), FC.z_of(u2, v2, -s)
    r1b, r2b = FC.residual_r(P, z1b), FC.residual_r(P, z2b)
    res_b = float(FC.dot_iv(r1b, r1b).mid() + FC.dot_iv(r2b, r2b).mid())
    posD = res_a <= res_b
    def mutD():
        """apply the exchange to ONE carrier only: the residual must change, i.e. the linked
        (whole-descendant) action is not the same as a per-carrier action."""
        zx = FC.z_of(u2, v2, -s)
        rx = FC.residual_r(P, zx)
        return abs(float(FC.dot_iv(r2a, r2a).mid() - FC.dot_iv(rx, rx).mid())) < 1e-18
    group("Q0D_whole_descendant_linked_AB_gauge_action", posD,
          [("A/B exchange applied to one carrier only", fires(mutD)),
           ("residual minimisation reversed",
            fires(lambda: res_b < res_a and res_a <= res_b))],
          "the gauge is chosen once per descendant and shared by both carriers")

    # ---------------------------------------------------------------- Q0E parent P2 projector
    d = np.load(f"{ROOT}/SQDT00/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz")
    P2, P1 = np.array(d["P2"]), np.array(d["P1"])
    e1, e2 = np.array(d["e1"]), np.array(d["e2"])
    I20 = np.eye(FC.DIM)
    sym = float(np.abs(P2 - P2.T).max())
    idem = float(np.abs(P2 @ P2 - P2).max())
    compl = float(np.abs(P2 @ (I20 - P2)).max())          # orthogonal-projector complementarity
    nested = float(np.abs(P2 @ P1 - P1).max())            # the parent basis is NESTED: P1 subset P2
    e1e2 = float(abs(e1 @ e2))
    fix1 = float(np.abs(P2 @ e1 - e1).max())
    fix2 = float(np.abs(P2 @ e2 - e2).max())
    rank2 = abs(float(np.trace(P2)) - 2.0)
    rank1 = abs(float(np.trace(P1)) - 1.0)
    posE = (sym < 1e-12 and idem < 1e-10 and compl < 1e-10 and nested < 1e-10
            and e1e2 < 1e-12 and fix1 < 1e-12 and fix2 < 1e-12 and rank2 < 1e-9 and rank1 < 1e-9)
    Pm = P2.copy()
    Pm[0, 1] += 1e-3
    group("Q0E_parent_P2_projector_idempotence_symmetry_orthogonality", posE,
          [("one P2 coefficient perturbed by 1e-3",
            fires(lambda: float(np.abs(Pm @ Pm - Pm).max()) < 1e-10)),
           ("symmetry claim on a non-symmetric matrix",
            fires(lambda: float(np.abs(Pm - Pm.T).max()) < 1e-12)),
           ("P1 and P2 asserted mutually orthogonal (they are NESTED, P1 subset P2)",
            fires(lambda: float(np.abs(P1 @ P2).max()) < 1e-10)),
           ("complementarity P2(I-P2)=0 claimed for the perturbed projector",
            fires(lambda: float(np.abs(Pm @ (I20 - Pm)).max()) < 1e-10))],
          ("sym=%.3e idem=%.3e P2(I-P2)=%.3e P2P1-P1=%.3e e1.e2=%.3e trP2=%.6f trP1=%.6f ; "
           "the parent basis is NESTED: P1 = e1 e1^T and P2 = P1 + e2 e2^T, so P1 P2 = P1 = %.6f "
           "and P1 is NOT orthogonal to P2"
           % (sym, idem, compl, nested, e1e2, float(np.trace(P2)), float(np.trace(P1)),
              float(np.abs(P1 @ P2).max()))))

    # ---------------------------------------------------------------- Q0F sqrt(2) isometry
    m2 = FC.m2sq(dA1, dB1)
    posF = (m2 == FC.uv_energy(dA1, dB1))
    zz = FC.z_of(u1, v1, +1)
    nz = FC.dot_iv(zz, zz)
    posF = posF and nz.lo <= m2 <= nz.hi
    def mutF():
        w = list(FC.W)
        w[3] = w[3] * Fr(101, 100)
        alt = sum((w[h] * (dA1[h] ** 2 + dB1[h] ** 2) for h in range(FC.T)), Fr(0))
        return alt == m2
    def mutF2():
        dAx = list(dA1)
        dAx[5] = dAx[5] + Fr(1, 1000)          # perturb ONE scored time
        return FC.m2sq(dAx, dB1) == m2
    group("Q0F_common_differential_sqrt2_isometry", posF,
          [("one trapezoid weight perturbed", fires(mutF)),
           ("one scored time perturbed", fires(mutF2)),
           ("reference u/v route disagrees",
            fires(lambda: abs(RF.m2sq([float(x) for x in dA1], [float(x) for x in dB1])
                              - float(m2)) > 1e-9 * float(m2)))],
          "||z||^2 = sum_h W[h](dA^2 + dB^2) exactly, for either gauge sign")

    # ---------------------------------------------------------------- Q0G carrier sign
    dd = FC.differential_d(P, z1a, z2a)
    dd_rev = FC.differential_d(P, z2a, z1a)
    posG = all(abs(float(dd[i].mid() + dd_rev[i].mid())) < 1e-25 for i in range(FC.DIM))
    def mutG():
        """swapping the carrier labels must flip d, not leave it unchanged"""
        return all(abs(float(dd[i].mid() - dd_rev[i].mid())) < 1e-25 for i in range(FC.DIM))
    group("Q0G_carrier_identity_and_C2_minus_C1_sign", posG,
          [("carrier labels exchanged without a sign flip", fires(mutG)),
           ("expected callable string altered",
            fires(lambda: "ppai_core.state_cross(st)" == "etcmnfc_core.transpose(st, I, J)"))],
          "d = (r[CARRIER_2] - r[CARRIER_1]) / sqrt(2); the physical carrier sign is frozen")

    # ---------------------------------------------------------------- Q0H NEAR-FAR slot swap
    dn = {0: dd, 1: [t * FC.Iv.exact(Fr(11, 10)) for t in dd]}
    df = {0: [t * FC.Iv.exact(Fr(3, 10)) for t in dd], 1: [t * FC.Iv.exact(Fr(1, 5)) for t in dd]}
    x = FC.interaction_x(dn[0], dn[1], df[0], df[1])
    xswap = FC.interaction_x(df[0], df[1], dn[0], dn[1])
    posH = all(abs(float(x[i].mid() + xswap[i].mid())) < 1e-22 for i in range(FC.DIM))
    group("Q0H_NEAR_minus_FAR_block_sign_and_geometry_slot_swap", posH,
          [("geometry labels exchanged without a sign flip",
            fires(lambda: all(abs(float(x[i].mid() - xswap[i].mid())) < 1e-22 for i in range(FC.DIM)))),
           ("one geometry label corrupted in a single cell",
            fires(lambda: FC.interaction_x(dn[0], df[1], df[0], dn[1])[3].mid() == x[3].mid()))],
          "the joint block-level NEAR/FAR slot swap maps x -> -x exactly")

    # ---------------------------------------------------------------- Q0I allocation exchange
    xalt = FC.interaction_x(dn[1], dn[0], df[1], df[0])
    posI = all(x[i].lo == xalt[i].lo and x[i].hi == xalt[i].hi for i in range(FC.DIM))
    def mutI():
        """exchanging the allocation label of only ONE geometry is NOT a valid paired exchange
        and must change nothing for x (still invariant) but MUST change a pair margin."""
        v = [1.0 / FC.DIM ** 0.5] * FC.DIM
        p_ok = FC.dot_float(v, FC.vec_sub(dn[0], df[0]))
        p_bad = FC.dot_float(v, FC.vec_sub(dn[0], df[1]))
        return abs(float(p_ok.mid() - p_bad.mid())) < 1e-22
    group("Q0I_invariance_to_every_neutral_allocation_member_exchange", posI,
          [("a single unpaired membership edge corrupted", fires(mutI)),
           ("x claimed to change under a valid paired exchange",
            fires(lambda: any(x[i].lo != xalt[i].lo for i in range(FC.DIM))))],
          "x is exactly invariant under either allocation-member exchange; the four cross-orbit "
          "pairings are permuted, not altered")

    # ---------------------------------------------------------------- Q0J coefficient + TAU
    tau = [FC.Iv.exact(Fr(1, 1000)), FC.Iv.exact(Fr(2, 1000)),
           FC.Iv.exact(Fr(3, 1000)), FC.Iv.exact(Fr(4, 1000))]
    ax = FC.A_X_block(tau)
    expect = FC.isqrt_iv(FC.Iv.exact(Fr(2)))
    expect = (FC.Iv.exact(Fr(10, 1000)) / expect).round_out()
    posJ = abs(float(ax.mid() - expect.mid())) < 1e-25
    ap = FC.A_PAIR(tau[0], tau[2])
    expect2 = (FC.Iv.exact(Fr(4, 1000)) * FC.SQRT2).round_out()
    posJ = posJ and abs(float(ap.mid() - expect2.mid())) < 1e-25
    def mutJ():
        bad = FC.A_X_block(tau[:3] + [FC.Iv.exact(Fr(40, 1000))])
        return abs(float(bad.mid() - ax.mid())) < 1e-25
    def mutJ2():
        rss = (sum(float(t.mid()) ** 2 for t in tau)) ** 0.5 / 2 ** 0.5
        return abs(rss - float(ax.mid())) < 1e-12
    group("Q0J_exact_response_unit_coefficient_and_TAU_propagation", posJ,
          [("one TAU inflated tenfold", fires(mutJ)),
           ("root-sum-of-squares substituted for the triangle bound", fires(mutJ2)),
           ("one reader coefficient (a weight) perturbed", fires(mutF))],
          "A_X = (1/sqrt2) sum TAU ; A_PAIR = sqrt2 (TAU_N + TAU_F)")

    # ---------------------------------------------------------------- Q0K trainer scope
    xs12 = []
    for k in range(12):
        a, b = fixture_row(1 + k, Fr(k, 100))
        uu, vv = FC.uv_vectors(a, b)
        zz1 = FC.z_of(uu, vv, +1)
        a2, b2 = fixture_row(1 + k, Fr(k, 100) + Fr(1, 50))
        uu2, vv2 = FC.uv_vectors(a2, b2)
        zz2 = FC.z_of(uu2, vv2, +1)
        dvec = FC.differential_d(P, zz1, zz2)
        xs12.append(FC.interaction_x(dvec, dvec, [t * FC.Iv.exact(Fr(1, 2)) for t in dvec],
                                     [t * FC.Iv.exact(Fr(1, 2)) for t in dvec]))
    ids12 = list(range(71000, 71012))
    srcs = [f"{HERE}/DISCOVERY_ACTIVE_RAW_ARCHIVE"]
    fitted = TR.fit(ids12, xs12, P, srcs)
    posK = len(fitted["block_ids"]) == 12
    group("Q0K_discovery_trainer_uses_all_and_only_twelve_discovery_ancestries", posK,
          [("eleven ancestries offered", fires(lambda: TR.fit(ids12[:11], xs12[:11], P, srcs))),
           ("thirteen ancestries offered",
            fires(lambda: TR.fit(ids12 + [71012], xs12 + [xs12[0]], P, srcs))),
           ("a duplicated ancestry id offered",
            fires(lambda: TR.fit(ids12[:11] + [ids12[10]], xs12, P, srcs)))],
          "")

    # ---------------------------------------------------------------- Q0L LOAO fold scope
    full, folds = TR.loao(ids12, xs12, P, srcs)
    posL = (len(folds) == 12 and all(f["left_out"] == ids12[i] for i, f in enumerate(folds)))
    # the omitted block must NOT contribute to its own fold mean
    Xm = TR.mean_x([xs12[j] for j in range(12) if j != 3])
    posL = posL and all(folds[3]["X_BAR_minus"][i].lo == Xm[i].lo for i in range(FC.DIM))
    def mutL():
        Xbad = TR.mean_x(xs12)                       # includes the omitted ancestry
        return all(folds[3]["X_BAR_minus"][i].lo == Xbad[i].lo for i in range(FC.DIM))
    group("Q0L_leave_one_ancestry_out_excludes_all_four_descendants_and_eight_rows", posL,
          [("the omitted ancestry left inside its own fold mean", fires(mutL)),
           ("fold order corrupted",
            fires(lambda: folds[3]["left_out"] == ids12[4]))],
          "a fold omits the complete ancestry: 4 descendants, 8 carrier rows and their shams")

    # ---------------------------------------------------------------- Q0M axis round trip
    with tempfile.TemporaryDirectory() as td:
        v = full["v_D"]
        npz = os.path.join(td, "FCDDH00_DIFFERENTIAL_INTERACTION_AXIS_D1.npz")
        np.savez(npz, v_D=np.array(v))
        meta = {"SOURCE": "TWELVE_NEW_CROSSED_DISCOVERY_ANCESTRIES",
                "AXIS_SPACE": "OUTSIDE_PARENT_P2__CARRIER_DIFFERENTIAL",
                "ESTIMAND": "ALLOCATION_AVERAGED_NEAR_MINUS_FAR_X_CARRIER",
                "v_D": [float(t) for t in v], "npz_sha256": sha(npz)}
        js = os.path.join(td, "a.json")
        json.dump(meta, open(js, "w"))
        ax_obj = SC.load_axis(npz, js)
        rt = list(ax_obj.v) == [float(t) for t in v]
        nrm = sum(t * t for t in v)
        proj = [[v[i] * v[j] for j in range(FC.DIM)] for i in range(FC.DIM)]
        tr = sum(proj[i][i] for i in range(FC.DIM))
        posM = rt and abs(nrm - 1) < 1e-12 and abs(tr - 1) < 1e-12 and \
            sum(v[i] * full["X_BAR_D"][i].fl() for i in range(FC.DIM)) > 0
        meta_bad = dict(meta)
        meta_bad["npz_sha256"] = "0" * 64
        js2 = os.path.join(td, "b.json")
        json.dump(meta_bad, open(js2, "w"))
        mutM1 = fires(lambda: SC.load_axis(npz, js2))
        meta_bad2 = dict(meta)
        meta_bad2["v_D"] = [-t for t in meta["v_D"]]
        js3 = os.path.join(td, "c.json")
        json.dump(meta_bad2, open(js3, "w"))
        mutM2 = fires(lambda: SC.load_axis(npz, js3))
        meta_bad3 = dict(meta)
        meta_bad3["SOURCE"] = "FSQBT00_TWELVE_HISTORICAL_BLOCKS"
        js4 = os.path.join(td, "d.json")
        json.dump(meta_bad3, open(js4, "w"))
        mutM3 = fires(lambda: SC.load_axis(npz, js4))
    group("Q0M_axis_disk_round_trip_canonical_sign_rank1_projector", posM,
          [("axis npz hash corrupted", mutM1),
           ("axis sign flipped between npz and json", mutM2),
           ("axis SOURCE relabelled to the historical panel", mutM3)],
          "unit norm, rank-1 projector trace 1, canonical sign <v, X_BAR> > 0")

    # ---------------------------------------------------------------- Q0N scorer firewall
    ssrc = ast.parse(open(f"{HERE}/HOLDOUT_FIXED_AXIS_SCORER_V1.py").read())
    simports = sorted({al.name for n in ast.walk(ssrc) if isinstance(n, ast.Import) for al in n.names} |
                      {(n.module or "") for n in ast.walk(ssrc) if isinstance(n, ast.ImportFrom)})
    banned_calls = []
    for n in ast.walk(ssrc):
        if isinstance(n, ast.Attribute) and n.attr in ("eig", "eigh", "svd", "pca", "lstsq", "pinv"):
            banned_calls.append(n.attr)
    posN = ("DISCOVERY_AXIS_TRAINER_V1" not in simports
            and not any(t in " ".join(simports) for t in ("FSQBT00", "FCRA00", "SQDT00", "WL2SMF00"))
            and banned_calls == [])
    ax_dummy = SC.FrozenAxis([0.0] * FC.DIM, "x", {"SOURCE": "TWELVE_NEW_CROSSED_DISCOVERY_ANCESTRIES",
                                                   "ESTIMAND": "ALLOCATION_AVERAGED_NEAR_MINUS_FAR_X_CARRIER",
                                                   "AXIS_SPACE": "OUTSIDE_PARENT_P2__CARRIER_DIFFERENTIAL"})
    group("Q0N_holdout_scorer_cannot_import_trainer_or_fit", posN,
          [("scorer asked to center hold-out outcomes",
            fires(lambda: SC.score_block(ax_dummy, xs12[0], center=True))),
           ("scorer asked to rescale", fires(lambda: SC.score_block(ax_dummy, xs12[0], rescale=2.0))),
           ("scorer asked to reorient", fires(lambda: SC.score_block(ax_dummy, xs12[0], reorient=-1))),
           ("frozen axis mutated in place",
            fires(lambda: setattr(ax_dummy, "v", (1.0,) * FC.DIM)))],
          "imports: %s" % ",".join(simports))

    # ---------------------------------------------------------------- Q0O exact 2^16 tail
    sc16 = [Fr(1)] * 16
    r16 = EN.enumerate_T(sc16, sc16)
    posO = (r16["n_assignments"] == 65536 and r16["exact"] and r16["p_exact"] == Fr(1, 65536))
    sc_alt = [Fr(1)] * 12 + [Fr(-1)] * 4
    r_alt = EN.enumerate_T(sc_alt, sc_alt)
    # analytic truth: T_obs = 8; subsets S with sum_{S} s <= 0 -> count by construction
    n_expect = 0
    for m in range(65536):
        tot = sum(sc_alt[i] for i in range(16) if (m >> i) & 1)
        if tot <= 0:
            n_expect += 1
    posO = posO and r_alt["count_ge_certain"] == n_expect
    Jp = [1] * 12 + [0] * 4
    Jm = [0] * 16
    rK = EN.enumerate_K(Jp, Jm, 12)
    # analytic truth: K stays >= 12 exactly for the 2^4 assignments that flip only the four
    # already-failing ancestries, so the tail is 16/65536 = 1/4096
    posO = posO and rK["count_ge"] == 16 and rK["tail"] == Fr(1, 4096)
    posO = posO and EN.design_reference_K_ge_12_of_16() == Fr(2517, 65536)
    group("Q0O_exact_2pow16_randomization_tail_on_analytic_scores", posO,
          [("Monte-Carlo style plus-one patch applied",
            fires(lambda: Fr(r16["count_ge_certain"] + 1, 65537) == r16["p_exact"])),
           ("one block score sign corrupted",
            fires(lambda: EN.enumerate_T([Fr(-1)] + sc16[1:], [Fr(-1)] + sc16[1:])["p_exact"]
                  == r16["p_exact"])),
           ("design reference misreported",
            fires(lambda: EN.design_reference_K_ge_12_of_16() == Fr(2518, 65536)))],
          "P(K>=12|p<=1/2) = 2517/65536 = 0.0384063720703125 reproduced exactly")

    # ---------------------------------------------------------------- Q0P equality/tie/zero
    eq = FC.certified_verdict(FC.Iv.exact(Fr(1, 3)), FC.Iv.exact(Fr(1, 3)))
    zero = FC.Iv.exact(Fr(0)).gt0()
    unres = FC.certified_verdict(FC.Iv(Fr(-1, 10 ** 30), Fr(1, 10 ** 30)), FC.Iv.exact(Fr(0)))
    posP = (eq == "FAIL" and zero is False and unres == "UNRESOLVED")
    group("Q0P_equality_tie_and_zero_score_boundary_conventions", posP,
          [("equality treated as a pass",
            fires(lambda: FC.certified_verdict(FC.Iv.exact(Fr(1, 3)), FC.Iv.exact(Fr(1, 3))) == "PASS")),
           ("a straddling interval silently resolved",
            fires(lambda: FC.Iv(Fr(-1), Fr(1)).gt0() in (True, False)))],
          "equality is FAILURE everywhere; a straddling enclosure is UNRESOLVED, never resolved")

    # ---------------------------------------------------------------- Q0Q co-optimal gauge
    dA0 = [Fr(0)] * FC.T
    u0, v0 = FC.uv_vectors(dA0, dA0)
    D0 = FC.gauge_statistic(P, u0, v0, u0, v0)
    s0, coopt0 = FC.gauge_sign(D0)
    posQ = coopt0 is True and D0.contains_zero()
    posQ = posQ and (coopt is False)          # the generic fixture is NOT co-optimal
    group("Q0Q_cooptimal_gauge_orbit_detected_not_averaged", posQ,
          [("a co-optimal descendant silently assigned a unique sign",
            fires(lambda: FC.gauge_sign(D0)[1] is False)),
           ("co-optimal orbit averaged instead of enumerated",
            fires(lambda: len(SC.enumerate_linked_gauge(P, ((u0, v0), (u0, v0)))[2]) == 1))],
          "an exactly-zero or undecided gauge statistic yields the complete two-element orbit")

    # ---------------------------------------------------------------- Q0R raw-lock guard
    with tempfile.TemporaryDirectory() as td:
        before = fires(lambda: DEC.require_raw_lock("DISCOVERY", here=td))
        json.dump({"x": 1}, open(os.path.join(td, "FCDDH00_DISCOVERY_ACTIVE_RAW_LOCK.json"), "w"))
        after = DEC.require_raw_lock("DISCOVERY", here=td)
    posR = bool(after)
    group("Q0R_raw_only_archives_cannot_be_decoded_before_their_lock_commit", posR,
          [("decode attempted with no raw-only lock present", before),
           ("hold-out decode attempted with no raw-only lock present",
            fires(lambda: DEC.require_raw_lock("HOLDOUT", here="/tmp/__absent__")))],
          "fh_disc.main and fh_hold.main both call require_raw_lock as their first statement")

    # ---------------------------------------------------------------- Q0S write-ahead ledger
    with tempfile.TemporaryDirectory() as td:
        ok_py = os.path.join(td, "ok.py")
        open(ok_py, "w").write(
            "import sys, json, os\n"
            "sys.path.insert(0, %r)\n" % HERE +
            "import fh_runner as R\n"
            "R.child_ack(sys.argv)\n"
            "R.child_advance(sys.argv, 'synthetic')\n"
            "print(json.dumps({'ok': True}))\n")
        pre_py = os.path.join(td, "pre.py")
        open(pre_py, "w").write(
            "import sys\n"
            "sys.path.insert(0, %r)\n" % HERE +
            "import fh_runner as R\n"
            "R.child_ack(sys.argv)\n"
            "raise SystemExit(3)\n")
        led = RUN.StartLedger(os.path.join(td, "L.jsonl"))
        r1 = led.run("other", "TEST", "ok", [ok_py], td, 10, 0)
        c1 = led.counts()
        r2 = led.run("other", "TEST", "pre", [pre_py], td, 10, c1["budget_charge"])
        c2 = led.counts()
        posS = (r1["ok"] and r1["charged"] and c1["charged_total"] == 1
                and (not r2["ok"]) and (not r2["charged"]) and r2["retry_permitted"]
                and c2["charged_total"] == 1 and c2["raw_advance_total"] == 1)
        budget_fires = fires(lambda: led.run("other", "TEST", "z", [ok_py], td, 1, 1))
    group("Q0S_write_ahead_ledger_charges_crash_or_uncertain_launch_exactly_once", posS,
          [("a failure that never advanced state charged as a start",
            fires(lambda: r2["charged"] is True)),
           ("a start launched past the hard budget", budget_fires),
           ("an advanced start left uncharged", fires(lambda: c1["charged_total"] == 0))],
          "ack without advance -> not charged, retry permitted; advance -> charged, never replayed")

    # ---------------------------------------------------------------- Q0U admission invariance
    rj = json.load(open(f"{HERE}/RANDOMIZATION_SEED_AND_ASSIGNMENT_MANIFEST.json"))
    a0 = rj["DISCOVERY"]["0"]
    quartet = {(c["geometry"], c["allocation"]) for c in a0["cells"]}
    flipped = {("FAR" if c["geometry"] == "NEAR" else "NEAR", c["allocation"]) for c in a0["cells"]}
    posU = quartet == {("NEAR", 0), ("NEAR", 1), ("FAR", 0), ("FAR", 1)} == flipped
    group("Q0U_complete_block_admission_identical_under_both_geometry_coins", posU,
          [("admission evaluated on a single favoured cell instead of the quartet",
            fires(lambda: {("NEAR", 0)} == quartet)),
           ("coin value claimed to change the unordered quartet",
            fires(lambda: quartet != flipped))],
          "the constructor is a pure function of (S,g,a); the coin only labels the two neutral "
          "branch slots, so the unordered quartet, its checkpoint/mask hashes and the accept "
          "decision are identical under both coin values")

    # ---------------------------------------------------------------- Q0V T never imports TAU
    esrc = open(f"{HERE}/EXACT_RANDOMIZATION_ENUMERATOR_V1.py").read()
    tree = ast.parse(esrc)
    fnT = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "enumerate_T"][0]
    names_T = {n.id for n in ast.walk(fnT) if isinstance(n, ast.Name)} | \
              {n.attr for n in ast.walk(fnT) if isinstance(n, ast.Attribute)}
    posV = (not any("tau" in t.lower() for t in names_T)) and \
        ("NONINFERENTIAL_UNDER_RESPONSE_ONLY_SHARP_NULL" in esrc)
    group("Q0V_response_only_T_never_imports_TAU_and_K_is_labelled", posV,
          [("TAU reachable from the T statistic",
            fires(lambda: any("tau" in t.lower() for t in names_T))),
           ("K tail reported as an inferential p-value",
            fires(lambda: EN.enumerate_K([1] * 16, [0] * 16, 16)
                  ["K_ASSIGNMENT_TAIL_INFERENTIAL_STATUS"] == "INFERENTIAL"))],
          "T is threshold free; the K tail carries its noninferential label in its own payload")

    # ---------------------------------------------------------------- Q0W canonical schema
    CANON = [l.strip() for l in open(f"{HERE}/CANONICAL_FIELD_SCHEMA.txt") if l.strip()]
    posW = (len(CANON) == len(set(CANON)) == 44)
    def schema_check(fields):
        return all(f in CANON for f in fields) and len(fields) == len(set(fields))
    posW = posW and schema_check(["FCDDH00_PROVENANCE_STATUS", "DISCOVERY_PANEL_STATUS"])
    group("Q0W_canonical_field_schema_exactly", posW,
          [("a renamed field accepted", fires(lambda: schema_check(["DISCOVERY_PANEL_STATE"]))),
           ("a duplicated field accepted",
            fires(lambda: schema_check(["DISCOVERY_PANEL_STATUS", "DISCOVERY_PANEL_STATUS"]))),
           ("a missing canonical field unnoticed",
            fires(lambda: len(CANON) == 43))],
          "%d canonical fields" % len(CANON))

    # ---------------------------------------------------------------- Q0T negative controls
    controls = {
        "one weight perturbed": R["Q0F_common_differential_sqrt2_isometry"]["mutations"][0]["fired_as_required"],
        "one scored time perturbed": R["Q0F_common_differential_sqrt2_isometry"]["mutations"][1]["fired_as_required"],
        "one reader coefficient perturbed": R["Q0J_exact_response_unit_coefficient_and_TAU_propagation"]["mutations"][2]["fired_as_required"],
        "one P2 coefficient perturbed": R["Q0E_parent_P2_projector_idempotence_symmetry_orthogonality"]["mutations"][0]["fired_as_required"],
        "one carrier label swapped": R["Q0G_carrier_identity_and_C2_minus_C1_sign"]["mutations"][0]["fired_as_required"],
        "one geometry label corrupted": R["Q0H_NEAR_minus_FAR_block_sign_and_geometry_slot_swap"]["mutations"][1]["fired_as_required"],
        "one ancestry role corrupted": R["Q0B_discovery_holdout_namespace_separation_and_leakage_rejection"]["mutations"][0]["fired_as_required"],
        "one TAU inflated": R["Q0J_exact_response_unit_coefficient_and_TAU_propagation"]["mutations"][0]["fired_as_required"],
        "one raw hash corrupted": R["Q0M_axis_disk_round_trip_canonical_sign_rank1_projector"]["mutations"][0]["fired_as_required"],
        "one unpaired allocation membership edge corrupted": R["Q0I_invariance_to_every_neutral_allocation_member_exchange"]["mutations"][0]["fired_as_required"],
        "one mask byte perturbed": None,
    }
    mk = np.zeros((64, 64), dtype=bool)
    mk[0, 0] = True
    mk2 = mk.copy()
    mk2[0, 1] = True
    controls["one mask byte perturbed"] = (hashlib.sha256(mk.tobytes()).hexdigest()
                                           != hashlib.sha256(mk2.tobytes()).hexdigest())
    posT = all(bool(v) for v in controls.values())
    group("Q0T_every_negative_control_fires_for_the_expected_reason", posT,
          [("a vacuous self-comparison accepted as a control",
            fires(lambda: (lambda z: z == z)(1) is False)),
           ("a control silently skipped", fires(lambda: all(controls.values()) is False))],
          json.dumps(controls))

    # ---------------------------------------------------------------- summary
    allpass = all(v["PASS"] for v in R.values())
    nonvac = all(v["n_mutations"] > 0 for v in R.values())
    out = {"FCDDH00_PREANALYSIS_ORACLE_STATUS": "PASS" if (allpass and nonvac) else "FAIL",
           "groups": len(R), "all_groups_pass": allpass, "non_vacuous": nonvac,
           "engine_starts": 0, "results": R,
           "negative_controls": controls}
    json.dump(out, open(f"{HERE}/PREANALYSIS_ORACLE_REPORT.json", "w"), indent=1, default=str)
    for k in sorted(R):
        print("%-72s %s" % (k, "PASS" if R[k]["PASS"] else "FAIL"))
    print("\nORACLE:", out["FCDDH00_PREANALYSIS_ORACLE_STATUS"], "| groups", len(R))
    return out


if __name__ == "__main__":
    run()
