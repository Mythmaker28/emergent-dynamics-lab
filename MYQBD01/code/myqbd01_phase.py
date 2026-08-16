"""MYQBD01 §5-§6 — Q scheduler-phase map and the six Q-like quantities.

Determined by reading observe.py and the scheduler, over the committed blobs. No trajectory
values are opened here; this is Gate 0.
"""
from __future__ import annotations

import ast
import json
import subprocess

REPO = "/home/claude/edl"
OUT = "/home/claude/MYQBD01/out"


def blob(path):
    return subprocess.run(("git", "show", "HEAD:%s" % path), cwd=REPO,
                          capture_output=True, text=True).stdout


def line_of(src, needle):
    for i, l in enumerate(src.splitlines(), 1):
        if needle in l:
            return i, l.strip()
    return None, None


def main():
    obs = blob("ORR01/code/observe.py")
    kin = blob("ORR01/code/kinetics.py")
    eng = blob("OBTC02/code/engine_obtc.py")

    # where does pre_react (which writes Q) sit relative to the Y-birth binomial?
    pre_react_ln, _ = line_of(obs, "def pre_react")
    q_ln, q_txt = line_of(obs, '"Q": float((nX[m] * cy).sum())')
    cy_ln, cy_txt = line_of(obs, "cy = np.minimum(nSY[m], free[m])")
    free_ln, _ = line_of(obs, "free = np.maximum(w.free(), 0)")

    # the engine's Y-birth candidate and probability, to compare EXACTLY
    react_free0, _ = line_of(kin, "free0 = np.maximum(self.free(), 0)")
    react_cand, _ = line_of(kin, "cand = np.minimum(self.n[res], free0)")
    react_p, _ = line_of(kin, "p = np.minimum(1.0, kk * pair)")
    # engine_obtc calls pre_react before _react_core
    call_pre, _ = line_of(eng, "self.rec.pre_react(self)")
    call_core, _ = line_of(eng, "b = self._react_core()")
    call_post, _ = line_of(eng, "self.rec.post_react(self)")

    # scheduler order from kinetics._one_step
    tree = ast.parse(kin)
    order = []
    for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
        for fn in [n for n in cls.body if isinstance(n, ast.FunctionDef)]:
            if fn.name == "_one_step":
                for st in fn.body:
                    if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call) \
                            and isinstance(st.value.func, ast.Attribute):
                        c = st.value
                        args = [a.value if isinstance(a, ast.Constant) else
                                (a.attr if isinstance(a, ast.Attribute) else "?")
                                for a in c.args]
                        order.append({"call": c.func.attr, "args": args})

    phase = {
        "SECTION": "MYQBD01 §5 Q phase map",
        "SCHEDULER_ORDER": order,
        "OBSERVER_WRITES_Q_IN": "Recorder.pre_react (observe.py:%d)" % pre_react_ln,
        "Q_DEFINITION": {"line": q_ln, "text": q_txt},
        "cand_Y_definition": {"line": cy_ln, "text": cy_txt},
        "free_snapshot": {"line": free_ln,
                          "text": "free = np.maximum(w.free(), 0) on the post-diffusion "
                                  "pre-reaction state"},
        "ENGINE_Y_BIRTH": {
            "free0": {"line": react_free0,
                      "text": "free0 = np.maximum(self.free(), 0)  -- computed ONCE at the top "
                              "of _react, shared by the X and Y loop iterations"},
            "cand_Y": {"line": react_cand, "text": "cand = np.minimum(self.n[res], free0), "
                                                   "res = SY for the Y iteration"},
            "p_Y": {"line": react_p, "text": "p = np.minimum(1.0, kk*pair), kk=kY, "
                                             "pair = nX*nY"}},
        "CALL_ORDER_IN_WorldOBTC._react": {
            "pre_react": call_pre, "react_core": call_core, "post_react": call_post,
            "reading": "pre_react runs BEFORE _react_core, on the identical state _react_core "
                       "then reads; free in pre_react is w.free() == free0 in _react_core"},
        "EXACT_IDENTITY": {
            "claim": "Q_recorded(t) == Q_reaction(t) exactly, per step, for the organiser cell",
            "why": ("pre_react reads free = max(w.free(),0) and nSY, nX on the post-diffusion "
                    "pre-reaction state; _react_core reads free0 = max(self.free(),0) and the "
                    "same nSY, nX at the top of the same _react call. cand_Y = min(nSY, free) "
                    "is the exact n-parameter of the Y-birth Binomial, and nX is the exact "
                    "multiplier in p_Y = min(1, kY*nX*nY). No random number is drawn between "
                    "pre_react and the Y binomial that changes nSY, nX or free."),
            "per_step": "the row is finalized in close_step every step; series has 11000 rows, "
                        "so the Q ledger is NOT subsampled (stride 1)",
            "CLASSIFICATION": "Q_LEDGER_EVENT_EXACT"},
        "ONE_CAVEAT_FOR_MULTI_Y": (
            "Q_recorded = sum_cells nX*min(nSY,free). The engine's expected Y births per cell "
            "are min(nSY,free)*min(1, kY*nX*nY). In the unclamped one-Y-per-cell regime the "
            "expected intensity is kY * nX * min(nSY,free) = kY * Q_cell, so Q_recorded * kY is "
            "the exact expected first-birth intensity. With nY >= 2 in a cell the true "
            "intensity carries an extra factor nY that Q_recorded omits, and once p clamps, the "
            "linear relation breaks entirely. Q_recorded is therefore the exact ONE-Y "
            "unclamped exposure and nothing wider."),
    }

    semantics = {
        "SECTION": "MYQBD01 §6 the six Q-like quantities",
        "DEFINITIONS": {
            "Q_ORGANISER_t": "nX * min(nSY, free) summed over cells with nY>0 (the original "
                             "organiser location(s))",
            "Q_REACTION_t": "the exact n*p-relevant exposure entering the Y-birth Binomial at "
                            "the reaction sub-step",
            "Q_POSITION_t_x": "nX(x) * min(nSY(x), free(x)) at an arbitrary cell x a Y particle "
                              "could occupy",
            "Q_LINEAGE_t": "Q_POSITION evaluated along a particular Y lineage's trajectory",
            "Q_AGGREGATE_t": "sum over all cells currently containing Y",
            "Q_RECORDED_t": "the scalar field 'Q' serialized by observe.py, index 20 of series"},
        "EQUALITIES_IN_THE_ONE_Y_BASELINE": {
            "Q_RECORDED == Q_REACTION": True,
            "Q_RECORDED == Q_ORGANISER": True,
            "Q_ORGANISER == Q_LINEAGE": ("True while the single Y sits at the organiser cell; "
                                         "at kY=0 (the archive) the Y never moves off its birth "
                                         "cell in the static branch and, in the mobile branch, "
                                         "the organiser IS the only Y, so Q_RECORDED tracks it"),
            "Q_ORGANISER == Q_AGGREGATE": "True while there is exactly one Y cell"},
        "WHERE_THEY_DIVERGE_AFTER_THE_FIRST_BIRTH": {
            "Q_RECORDED_vs_Q_REACTION": ("diverge if two Y become co-located: Q_RECORDED omits "
                                         "the nY multiplier in p_Y"),
            "Q_ORGANISER_vs_Q_POSITION": ("diverge as soon as a mobile descendant leaves the "
                                          "organiser cell: the exposure at the descendant's new "
                                          "cell is a DIFFERENT, unrecorded quantity"),
            "Q_ORGANISER_vs_Q_AGGREGATE": ("diverge once there are two Y cells"),
            "LOAD_BEARING": ("the recorded field is the same object as PMCR01's one-organiser "
                             "Q derivation. That does NOT make it the two-Y lineage "
                             "environment. Q_POSITION and Q_LINEAGE for a separated descendant "
                             "are never recorded per step.")},
    }
    json.dump({"PHASE": phase, "SEMANTICS": semantics},
              open(f"{OUT}/MYQBD01_Q_PHASE_MAP.json", "w"), indent=1, default=str)

    print("scheduler order:", [c["call"] + str(c["args"]) for c in order])
    print("Q written in pre_react (observe.py:%d), Q def line %d" % (pre_react_ln, q_ln))
    print("call order in _react: pre_react=%s core=%s post=%s" % (call_pre, call_core,
                                                                  call_post))
    print("CLASSIFICATION =", phase["EXACT_IDENTITY"]["CLASSIFICATION"])
    print("one-Y equalities: Q_RECORDED == Q_REACTION == Q_ORGANISER == Q_AGGREGATE (one Y)")
    print("divergence after first birth: Q_POSITION / Q_LINEAGE for a separated descendant are "
          "NEVER recorded per step")


if __name__ == "__main__":
    main()
