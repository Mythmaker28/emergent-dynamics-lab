"""FCDDH01R plan builder (engineering only). Builds a frozen JSON row queue for a phase."""
from __future__ import annotations
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sha_f = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
CODE_FILES = ["DURABLE_PHASE_SUPERVISOR.py", "EXACT_ONCE_PHASE_STATE_MACHINE.py"]
ENV_WHITELIST = ["PATH", "HOME", "LANG", "LC_ALL", "PYTHONHASHSEED",
                 "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "PYTHONDONTWRITEBYTECODE"]
FROZEN_ENV = {"PYTHONHASHSEED": "0", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
              "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
              "PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/local/bin:/usr/bin:/bin",
              "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "HOME": "/root"}
def code_sha():
    h = hashlib.sha256()
    for f in CODE_FILES:
        h.update(sha_f(os.path.join(HERE, f)).encode())
    return h.hexdigest()
def build(path, programme, phase, ledger_root, rows, phase_max, execution_class="REAL",
          required_prior_artifact=None):
    plan = {"programme": programme, "phase": phase, "ledger_root": ledger_root,
            "execution_class": execution_class, "phase_max_charged_starts": phase_max,
            "rows": rows, "code_sha256": code_sha(),
            "env_whitelist": ENV_WHITELIST, "frozen_env": FROZEN_ENV,
            "required_prior_artifact": required_prior_artifact, "plan_sha256": None}
    plan["plan_sha256"] = hashlib.sha256(
        json.dumps(plan, sort_keys=True).encode()).hexdigest()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.write(fd, json.dumps(plan, sort_keys=True, indent=1).encode()); os.fsync(fd); os.close(fd)
    return plan
def row(tag, ordinal, argv, outputs, operator_hash, input_hashes, schedule_position,
        interpreter="/usr/bin/python3", cwd=None, required_free_bytes=64 * 1024 * 1024):
    return {"tag": tag, "ordinal": ordinal, "argv": argv, "outputs": outputs,
            "operator_hash": operator_hash, "input_hashes": input_hashes,
            "schedule_position": schedule_position, "interpreter": interpreter,
            "cwd": cwd or HERE, "env_whitelist": ENV_WHITELIST, "env": FROZEN_ENV,
            "required_free_bytes": required_free_bytes}
