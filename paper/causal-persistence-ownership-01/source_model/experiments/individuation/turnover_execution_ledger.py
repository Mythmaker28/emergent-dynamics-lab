"""LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03E — one-shot, hash-chained execution ledger (red-team blocker B1 / AUTH/LEDGER).

The 03C runner bound approval only to the execution-manifest blob, checked a Boolean `one_execution_only` without any
consumption state, and keyed resumption to the chosen output file — so one approval could start multiple fresh output
paths and a resume could not be distinguished from a prohibited second execution. This module adds:

  * final-seal binding: approval must carry `final_seal_sha256` equal to the sealed manifest's SHA-256.
  * an atomic EXCLUSIVE-CREATE canonical-run start: `open(..., O_CREAT|O_EXCL)`; a second FRESH start is refused when a
    start/completion ledger already exists.
  * an append-only, HASH-CHAINED JSONL ledger: each entry stores prev_hash and entry_hash = sha256(prev_hash + canon).
    Tampering, reordering, duplication, or truncation break the chain and are rejected by `verify_chain`.
  * one-use authorization CONSUMPTION: the start entry records the authorization id + seal; a resume must reuse the
    exact same authorization id + seal + code/env hashes, and may only run seeds not already recorded complete.
  * per-raw-output SHA-256 recorded per seed; a completion entry closes the ledger with the full raw manifest.

HONEST BOUNDARY (documented, not hidden): this enforces one execution WITHIN the canonical run directory. It cannot
prevent a malicious actor from copying the repository elsewhere and running an unbound fork — that is a procedural,
not cryptographic, guarantee. `verify_chain` detects tampering of THIS ledger; it cannot bind an external copy.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

LEDGER_NAME = "execution_ledger.jsonl"
GENESIS = "0" * 64


class LedgerError(RuntimeError):
    pass


def _canon(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _entry_hash(prev_hash: str, payload: dict) -> str:
    return hashlib.sha256(prev_hash.encode("ascii") + b"\n" + _canon(payload)).hexdigest()


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _read_entries(ledger_path: Path) -> list[dict]:
    if not ledger_path.exists():
        return []
    return [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def verify_chain(run_dir) -> dict:
    ledger_path = Path(run_dir) / LEDGER_NAME
    entries = _read_entries(ledger_path)
    prev = GENESIS
    for i, e in enumerate(entries):
        if e.get("seq") != i:
            raise LedgerError(f"ledger sequence break at {i}: seq={e.get('seq')}")
        if e.get("prev_hash") != prev:
            raise LedgerError(f"ledger chain break at seq {i}: prev_hash mismatch")
        payload = {k: e[k] for k in e if k not in ("entry_hash",)}
        recomputed = _entry_hash(prev, payload)
        if recomputed != e.get("entry_hash"):
            raise LedgerError(f"ledger tamper at seq {i}: entry_hash mismatch")
        prev = e["entry_hash"]
    return {"entries": len(entries), "tip_hash": prev, "verified": True}


def _append(run_dir: Path, event: str, body: dict) -> str:
    ledger_path = run_dir / LEDGER_NAME
    entries = _read_entries(ledger_path)
    prev = entries[-1]["entry_hash"] if entries else GENESIS
    payload = {"seq": len(entries), "prev_hash": prev, "event": event, **body}
    payload["entry_hash"] = _entry_hash(prev, {k: payload[k] for k in payload if k != "entry_hash"})
    with open(ledger_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True) + "\n")
    return payload["entry_hash"]


def validate_authorization(approval: dict, expected_seal_sha256: str, expected_manifest_blob: str,
                           expected_phrase: str) -> None:
    if approval.get("authorized") is not True:
        raise LedgerError("prospective execution is NOT AUTHORIZED")
    if approval.get("one_execution_only") is not True:
        raise LedgerError("approval must be explicitly limited to one execution")
    if approval.get("final_seal_sha256") != expected_seal_sha256:
        raise LedgerError("approval is not bound to the exact FINAL_SEAL sha256")
    if approval.get("execution_manifest_git_blob") != expected_manifest_blob:
        raise LedgerError("approval is not bound to the exact execution-manifest Git blob")
    if approval.get("approval_phrase") != expected_phrase:
        raise LedgerError("human approval phrase mismatch")
    for field in ("authorization_id", "approved_by", "approved_at_utc"):
        if not str(approval.get(field, "")).strip():
            raise LedgerError(f"approval field is required: {field}")


def start_or_resume(run_dir, start_record: dict) -> dict:
    """Atomically begin the canonical run, or resume an existing one with identical binding.

    start_record must include: authorization_id, final_seal_sha256, execution_manifest_git_blob, code_hashes (dict),
    environment_hash, seed_family (dict). A FRESH start uses O_EXCL to atomically create the ledger; if it already
    exists this is a RESUME and every binding field must match exactly.
    """
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = run_dir / LEDGER_NAME
    bind = {k: start_record[k] for k in ("authorization_id", "final_seal_sha256", "execution_manifest_git_blob",
                                         "environment_hash")}
    genesis_body = {"authorization_id": start_record["authorization_id"],
                    "final_seal_sha256": start_record["final_seal_sha256"],
                    "execution_manifest_git_blob": start_record["execution_manifest_git_blob"],
                    "code_hashes": start_record["code_hashes"], "environment_hash": start_record["environment_hash"],
                    "seed_family": start_record["seed_family"]}
    try:
        fd = os.open(ledger_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)  # atomic exclusive create
    except FileExistsError:
        verify_chain(run_dir)
        existing = _read_entries(ledger_path)[0]
        for k, v in bind.items():
            if existing.get(k) != v:
                raise LedgerError(f"resume binding mismatch on {k}: cannot reuse another authorization/seal/env")
        if existing.get("code_hashes") != start_record["code_hashes"]:
            raise LedgerError("resume code-hash mismatch: frozen code changed")
        if any(e["event"] == "completion" for e in _read_entries(ledger_path)):
            raise LedgerError("run already completed; a second fresh or extended execution is refused")
        return {"mode": "resume", "run_dir": str(run_dir), "completed_seeds": sorted(completed_seeds(run_dir))}
    else:
        payload = {"seq": 0, "prev_hash": GENESIS, "event": "start", **genesis_body}
        payload["entry_hash"] = _entry_hash(GENESIS, {k: payload[k] for k in payload if k != "entry_hash"})
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")
        return {"mode": "fresh", "run_dir": str(run_dir), "completed_seeds": []}


def completed_seeds(run_dir) -> set[int]:
    return {int(e["seed"]) for e in _read_entries(Path(run_dir) / LEDGER_NAME) if e.get("event") == "seed_result"}


def record_seed(run_dir, seed: int, raw_path, feasibility_projection: dict) -> str:
    """Append a hash-chained seed_result with the raw output's SHA-256. Completed seeds are never overwritten."""
    if int(seed) in completed_seeds(run_dir):
        raise LedgerError(f"seed {seed} already recorded complete; refusing to overwrite/rerun")
    return _append(Path(run_dir), "seed_result",
                   {"seed": int(seed), "raw_sha256": sha256_file(raw_path),
                    "feasibility_projection": feasibility_projection})


def close_run(run_dir, raw_manifest: dict) -> str:
    entries = _read_entries(Path(run_dir) / LEDGER_NAME)
    if any(e["event"] == "completion" for e in entries):
        raise LedgerError("run already completed")
    return _append(Path(run_dir), "completion",
                   {"raw_manifest": raw_manifest, "n_seed_results": sum(1 for e in entries if e["event"] == "seed_result")})
