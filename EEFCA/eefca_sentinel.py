"""Engine-start sentinel. FAILS CLOSED: importing any runtime module that can advance state
raises immediately. Installed before any audit code runs."""
import sys, builtins
FORBIDDEN = {"ppai_engine","ppai_core","domc_core","etpc_core","etpc_run","etpc_gates",
             "chmr_core","chmr_run","edlab","edlab.substrates.scaffold.engine",
             "edlab.experiments.sc_mcm.engine","edlab.experiments.sc_iom.engine"}
STARTS = {"n": 0, "violations": []}
_real = builtins.__import__
def _guard(name, *a, **k):
    root = name.split(".")[0]
    if name in FORBIDDEN or root in {"edlab"} or name in FORBIDDEN:
        STARTS["violations"].append(name)
        raise RuntimeError(f"AUDIT_SCOPE_VIOLATION: forbidden runtime import '{name}'")
    return _real(name, *a, **k)
builtins.__import__ = _guard
def report():
    return {"NEW_ENGINE_STARTS": STARTS["n"], "forbidden_import_attempts": STARTS["violations"],
            "sentinel": "fails closed on any runtime/engine import"}
