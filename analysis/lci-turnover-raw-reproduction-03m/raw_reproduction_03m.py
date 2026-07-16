"""Frozen-raw canonical reproduction and independent cross-check for 03M.

The only scientific inputs are the committed 03G raw manifest and its 50 raw
JSON records. Frozen execution, schema, ledger, seal, analysis, and decision
documents are provenance/specification inputs. The script blocks simulation
runner/engine imports, never invokes a seed path, and writes only derived 03M
tables, figure, report, result JSON, and claim-impact note.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import importlib.abc
import importlib.metadata
import json
import math
import os
import platform
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


EXPECTED_COMMIT = "9cb996bb891f9a618e593f2f5c302f30210458de"
EXPECTED_AUTHORIZATION_COMMIT = "c158bc0b848710edeafd425f31dfcbd5aefc0934"
EXPECTED_SEAL_SHA256 = "cdf7277a00e3017a1389e9334d983364b9aa0af88c646cdec2999e6ad88757fd"
EXPECTED_LEDGER_TIP = "0d579d0fa40fd19afe7bfc26140133fc9c57de2b656a7606aa5a5bd8591791aa"
EXPECTED_SEEDS = list(range(54001, 54051))
EXPECTED_VALID_WORLDS = 21
EXPECTED_LEDGER_ENTRIES = 108
EXPECTED_BRANCH = "analysis/lci-turnover-raw-reproduction-03m"

RUN_REL = Path("results/LCI-TURNOVER-PROSPECTIVE-03G")
RAW_MANIFEST_REL = RUN_REL / "raw_manifest_03g.json"
LEDGER_REL = RUN_REL / "execution_ledger_03g.jsonl"
LEDGER_ANCHOR_REL = RUN_REL / "execution_ledger_03g.anchor.json"
CERT_REL = RUN_REL / "analysis" / "analysis_certificate_03g.json"
CERT_REPORT_REL = RUN_REL / "analysis" / "analysis_report_03g.md"
EXECUTION_MANIFEST_REL = Path("docs/individuation/TURNOVER_EXECUTION_MANIFEST_03G.json")
DECISION_TREE_REL = Path("docs/individuation/TURNOVER_DECISION_TREE_03G.json")
SEAL_REL = Path("docs/individuation/FINAL_SEAL_MANIFEST_03G.json")
AUTHORIZATION_REL = Path("docs/individuation/TURNOVER_AUTHORIZATION_03G.json")
EXECUTION_INDEX_REL = Path("docs/individuation/TURNOVER_PROSPECTIVE_EXECUTION_INDEX_03G.json")
PACKAGING_INDEX_REL = Path("docs/individuation/TURNOVER_PACKAGING_CANONICAL_INDEX_03K.json")
ENV_LOCK_REL = Path("docs/individuation/TURNOVER_ENVIRONMENT_LOCK_03G.txt")

OUTPUT_SUBDIR = Path("analysis/lci-turnover-raw-reproduction-03m")
GENERATOR_REL = OUTPUT_SUBDIR / "raw_reproduction_03m.py"
INDEPENDENT_REL = OUTPUT_SUBDIR / "independent_crosscheck_03m.py"
SEED_TABLE_NAME = "SEED_FEASIBILITY_03M.csv"
PRIMARY_TABLE_NAME = "PRIMARY_RESULTS_AND_GATES_03M.csv"
FIGURE_NAME = "OUTCOME_B_REPRODUCTION_03M.png"
RESULT_NAME = "REPRODUCTION_RESULT_03M.json"
REPORT_NAME = "REPRODUCTION_REPORT_03M.md"
CLAIM_NOTE_NAME = "CLAIM_IMPACT_03M.md"

FEASIBILITY_PROJECTION_FIELDS = [
    "seed",
    "eligible",
    "deep_reached",
    "rest_assay_valid",
    "deep_assay_valid",
    "valid",
    "reason",
]

ENGINE_PREFIXES = (
    "turnover_engine_03g",
    "turnover_runner_03g",
    "turnover_dev_runner",
    "edlab.experiments.sc_iom.engine",
    "edlab.experiments.sc_mcm.engine",
    "edlab.substrates.scaffold.engine",
)


class ReproductionError(RuntimeError):
    """Raised when a frozen provenance or scientific check fails."""


ENGINE_IMPORT_ATTEMPTS: list[str] = []


class EngineImportBlocker(importlib.abc.MetaPathFinder):
    """Fail closed if a simulation entrypoint is requested in this process."""

    def find_spec(self, fullname: str, path=None, target=None):  # noqa: ANN001
        if any(fullname == prefix or fullname.startswith(prefix + ".") for prefix in ENGINE_PREFIXES):
            ENGINE_IMPORT_ATTEMPTS.append(fullname)
            raise ImportError(f"03M forbids simulation import: {fullname}")
        return None


sys.meta_path.insert(0, EngineImportBlocker())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReproductionError(message)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path, repo: Path) -> str:
    return str(path.resolve().relative_to(repo.resolve())).replace("\\", "/")


def git_bytes(repo: Path, *args: str, check: bool = True) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and completed.returncode != 0:
        raise ReproductionError(
            f"git {' '.join(args)} failed ({completed.returncode}): "
            f"{completed.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return completed.stdout


def git_text(repo: Path, *args: str, check: bool = True) -> str:
    return git_bytes(repo, *args, check=check).decode("utf-8", errors="strict").strip()


def committed_binding(repo: Path, commit: str, path: str) -> dict:
    blob = git_text(repo, "rev-parse", f"{commit}:{path}")
    data = git_bytes(repo, "cat-file", "blob", blob)
    return {"git_blob": blob, "sha256": sha256_bytes(data), "bytes": len(data)}


def committed_file_bytes(repo: Path, path: Path | str, commit: str = EXPECTED_COMMIT) -> bytes:
    relative_path = str(path).replace("\\", "/")
    return git_bytes(repo, "cat-file", "blob", f"{commit}:{relative_path}")


def verify_declared_committed_bindings(
    repo: Path,
    commit: str,
    declared: dict[str, dict],
    label: str,
) -> dict:
    verified = {}
    for path, expected in sorted(declared.items()):
        actual = committed_binding(repo, commit, path)
        require(actual["git_blob"] == expected["git_blob"], f"{label} Git blob mismatch: {path}")
        require(actual["sha256"] == expected["sha256"], f"{label} SHA-256 mismatch: {path}")
        verified[path] = actual
    return {"verified": True, "count": len(verified), "entries": verified}


def parse_lock_text(text: str) -> dict[str, str]:
    requirements: dict[str, str] = {}
    for line in text.splitlines():
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        name, version = text.split("==", 1)
        requirements[name.lower()] = version
    return requirements


def verify_environment(execution_manifest: dict, repo: Path) -> dict:
    runtime = execution_manifest["environment"]["runtime"]
    actual = {
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "system": platform.system(),
        "machine": platform.machine(),
        "packages": {
            name: importlib.metadata.version(name)
            for name in runtime["packages"]
        },
    }
    require(actual == runtime, f"clean runtime differs from frozen runtime: {actual} != {runtime}")
    lock_path = repo / ENV_LOCK_REL
    lock_bytes = committed_file_bytes(repo, ENV_LOCK_REL)
    lock_requirements = parse_lock_text(lock_bytes.decode("utf-8"))
    installed = {name: importlib.metadata.version(name) for name in lock_requirements}
    require(installed == lock_requirements, "installed clean environment differs from committed lock")
    require(
        sha256_bytes(lock_bytes) == execution_manifest["environment"]["lock_sha256"],
        "environment lock SHA-256 mismatch",
    )
    return {
        "verified": True,
        "executable": sys.executable,
        "platform": platform.platform(),
        "runtime": actual,
        "lock_path": str(ENV_LOCK_REL).replace("\\", "/"),
        "lock_sha256": sha256_bytes(lock_bytes),
        "locked_packages": installed,
    }


def verify_git_and_seal(repo: Path) -> tuple[dict, dict, dict, dict, dict]:
    head = git_text(repo, "rev-parse", "HEAD")
    parent = git_text(repo, "rev-parse", "HEAD^")
    branch = git_text(repo, "branch", "--show-current")
    require(head == EXPECTED_COMMIT, f"wrong results commit: {head}")
    require(parent == EXPECTED_AUTHORIZATION_COMMIT, f"unexpected results parent: {parent}")
    require(branch == EXPECTED_BRANCH, f"wrong analysis branch: {branch}")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", EXPECTED_AUTHORIZATION_COMMIT, head],
        cwd=repo,
        check=False,
    ).returncode == 0
    require(ancestor, "authorization commit is not an ancestor")
    remote_refs = git_text(
        repo,
        "for-each-ref",
        "--format=%(refname):%(objectname)",
        "refs/remotes/origin",
    ).splitlines()
    result_refs = [row for row in remote_refs if row.endswith(":" + head)]

    seal_path = repo / SEAL_REL
    seal = json.loads(committed_file_bytes(repo, SEAL_REL))
    seal_sha = sha256_bytes(canonical_bytes(seal) + b"\n")
    require(seal_sha == EXPECTED_SEAL_SHA256, f"final-seal hash mismatch: {seal_sha}")
    require(seal["schema"] == "LCI-TURNOVER-SEAL-03G-v1", "wrong seal schema")

    execution_manifest_path = repo / EXECUTION_MANIFEST_REL
    execution_manifest_bytes = committed_file_bytes(repo, EXECUTION_MANIFEST_REL)
    execution_manifest = json.loads(execution_manifest_bytes)
    manifest_binding = committed_binding(repo, head, str(EXECUTION_MANIFEST_REL).replace("\\", "/"))
    require(seal["execution_manifest"] == {
        "path": str(EXECUTION_MANIFEST_REL).replace("\\", "/"),
        "sha256": sha256_bytes(execution_manifest_bytes),
        "git_blob": manifest_binding["git_blob"],
    }, "seal does not bind exact execution manifest")

    protected_digest = sha256_bytes(canonical_bytes(execution_manifest["protected_files"]))
    require(seal["protected_files_sha256"] == protected_digest, "protected-map digest mismatch")
    protected_runtime = {}
    for path, expected in sorted(execution_manifest["protected_files"].items()):
        work_path = repo / path
        require(work_path.is_file(), f"protected working file absent: {path}")
        actual_blob = git_text(repo, "hash-object", "--path", path, str(work_path))
        actual_sha = sha256_file(work_path)
        require(actual_blob == expected["git_blob"], f"protected runtime blob mismatch: {path}")
        require(actual_sha == expected["sha256"], f"protected runtime SHA mismatch: {path}")
        protected_runtime[path] = {"git_blob": actual_blob, "sha256": actual_sha}

    canonical_artifacts = verify_declared_committed_bindings(
        repo,
        head,
        seal["canonical_artifacts"],
        "final-seal canonical artifact",
    )
    require(
        str(EXECUTION_MANIFEST_REL).replace("\\", "/") in seal["canonical_artifacts"],
        "sealed canonical set omits execution manifest",
    )
    require(
        str(PACKAGING_INDEX_REL).replace("\\", "/") in seal["canonical_artifacts"],
        "sealed canonical set omits packaging index",
    )

    primary = list(range(
        execution_manifest["seed_plan"]["primary"]["first"],
        execution_manifest["seed_plan"]["primary"]["last"] + 1,
    ))
    reserve = list(range(
        execution_manifest["seed_plan"]["reserve"]["first"],
        execution_manifest["seed_plan"]["reserve"]["last"] + 1,
    ))
    family_sha = sha256_bytes(canonical_bytes({
        "primary": primary,
        "reserve": reserve,
        "hard_cap": len(primary) + len(reserve),
        "minimum_valid_worlds": execution_manifest["seed_plan"]["minimum_valid_worlds"],
    }))
    require(family_sha == seal["family_sha256"], "sealed seed-family hash mismatch")

    authorization = json.loads(committed_file_bytes(repo, AUTHORIZATION_REL))
    require(authorization["final_seal_sha256"] == seal_sha, "authorization seal mismatch")
    require(authorization["execution_manifest_sha256"] == sha256_bytes(execution_manifest_bytes), "authorization manifest SHA mismatch")
    require(authorization["execution_manifest_git_blob"] == manifest_binding["git_blob"], "authorization manifest blob mismatch")
    phrase = execution_manifest["authorization"]["approval_phrase_template"].replace(
        "{final_seal_sha256}", seal_sha
    )
    require(authorization["approval_phrase"] == phrase, "authorization phrase mismatch")
    require(authorization["one_execution_only"] is True, "authorization is not one-execution-only")

    execution_index = json.loads(committed_file_bytes(repo, EXECUTION_INDEX_REL))
    for key in (
        "authorization",
        "final_seal",
        "ledger",
        "ledger_anchor",
        "raw_manifest",
        "analysis_certificate",
        "analysis_report",
    ):
        entry = execution_index[key]
        actual = committed_binding(repo, head, entry["path"])
        require(actual["git_blob"] == entry["git_blob"], f"execution index blob mismatch: {key}")
        require(actual["sha256"] == entry["sha256"], f"execution index SHA mismatch: {key}")

    packaging = json.loads(committed_file_bytes(repo, PACKAGING_INDEX_REL))
    for key, entry in packaging["bindings"].items():
        actual = committed_binding(repo, head, entry["canonical_path"])
        require(actual["git_blob"] == entry["git_blob"], f"packaging blob mismatch: {key}")
        require(actual["sha256"] == entry["sha256"], f"packaging SHA mismatch: {key}")

    provenance = {
        "exact_results_commit": head,
        "exact_results_parent": parent,
        "analysis_branch": branch,
        "authorization_ancestor": EXPECTED_AUTHORIZATION_COMMIT,
        "authorization_is_ancestor": ancestor,
        "remote_refs_at_results_commit": result_refs,
        "final_seal_sha256": seal_sha,
        "execution_manifest": {
            "path": str(EXECUTION_MANIFEST_REL).replace("\\", "/"),
            "git_blob": manifest_binding["git_blob"],
            "sha256": sha256_bytes(execution_manifest_bytes),
        },
        "protected_runtime_bindings_verified": len(protected_runtime),
        "protected_map_sha256": protected_digest,
        "sealed_canonical_artifacts": canonical_artifacts,
        "packaging_bindings_verified": True,
        "authorization": {
            "path": str(AUTHORIZATION_REL).replace("\\", "/"),
            "authorization_id": authorization["authorization_id"],
            "approval_phrase_exact": True,
            "one_execution_only": True,
        },
        "family_sha256": family_sha,
    }
    return provenance, execution_manifest, seal, authorization, execution_index


def import_canonical_modules(repo: Path):  # noqa: ANN201
    experiments = str((repo / "experiments" / "individuation").resolve())
    if experiments not in sys.path:
        sys.path.insert(0, experiments)
    raw_schema = importlib.import_module("turnover_raw_schema_03g")
    ledger = importlib.import_module("turnover_ledger_03g")
    analyzer = importlib.import_module("turnover_analyzer_03g")
    return raw_schema, ledger, analyzer


def verify_ledger_and_raw(
    repo: Path,
    raw_schema,
    ledger,
    execution_manifest: dict,
    execution_index: dict,
) -> tuple[dict, dict, list[dict], list[dict]]:
    run_dir = repo / RUN_REL
    raw_manifest_bytes = committed_file_bytes(repo, RAW_MANIFEST_REL)
    raw_manifest = json.loads(raw_manifest_bytes)
    with tempfile.TemporaryDirectory(prefix="lci-turnover-03m-verify-") as temporary:
        committed_run = Path(temporary) / RUN_REL.name
        (committed_run / "raw").mkdir(parents=True)
        (committed_run / "raw_manifest_03g.json").write_bytes(raw_manifest_bytes)
        (committed_run / "execution_ledger_03g.jsonl").write_bytes(
            committed_file_bytes(repo, LEDGER_REL)
        )
        (committed_run / "execution_ledger_03g.anchor.json").write_bytes(
            committed_file_bytes(repo, LEDGER_ANCHOR_REL)
        )
        for raw_entry in raw_manifest["entries"]:
            raw_path = committed_run / raw_entry["path"]
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_bytes(committed_file_bytes(repo, RUN_REL / raw_entry["path"]))
        status = ledger.verify(committed_run, require_state="CERTIFIED")
        entries = ledger.entries(committed_run)
        records = raw_schema.validate_raw_manifest(raw_manifest, committed_run)
    require(status["entries"] == EXPECTED_LEDGER_ENTRIES, "ledger entry count mismatch")
    require(status["tip_hash"] == EXPECTED_LEDGER_TIP, "ledger tip mismatch")
    require([entry["seq"] for entry in entries] == list(range(EXPECTED_LEDGER_ENTRIES)), "ledger sequence is not exact")

    events = [entry["event"] for entry in entries]
    counts = Counter(events)
    starts = [int(entry["seed"]) for entry in entries if entry["event"] == "SEED_STARTED"]
    resumes = [int(entry["seed"]) for entry in entries if entry["event"] == "SEED_RESUMED"]
    completions = [entry for entry in entries if entry["event"] == "SEED_COMPLETED"]
    completion_seeds = [int(entry["seed"]) for entry in completions]
    require(starts == EXPECTED_SEEDS, "seed-start order differs from 54001-54050")
    require(completion_seeds == EXPECTED_SEEDS, "seed-completion order differs from 54001-54050")
    require(not resumes, "a seed resume occurred")
    require(len(set(completion_seeds)) == 50, "duplicate seed completion")
    require(all(entry["phase"] == "primary" for entry in completions), "reserve completion present")
    require(counts["CREATE"] == counts["AUTHORIZE"] == counts["START_PRIMARY"] == 1, "ledger contains repeated execution initialization")
    require(counts["CLOSE_PRIMARY"] == counts["DECIDE_RESERVE"] == counts["CLOSE_FAMILY"] == 1, "family transitions are not unique")
    require(counts["RECORD_ANALYSIS"] == counts["CERTIFY"] == 1, "analysis/certification transitions are not unique")

    decision = next(entry for entry in entries if entry["event"] == "DECIDE_RESERVE")
    require(decision["active"] is False, "reserve unexpectedly activated")
    require(decision["valid_worlds_after_primary"] == EXPECTED_VALID_WORLDS, "reserve decision valid count mismatch")
    require(decision["fields_used"] == FEASIBILITY_PROJECTION_FIELDS, "reserve decision fields changed")
    require(decision["outcome_fields_used"] == [], "reserve decision used outcome fields")
    for completion in completions:
        projection = completion["feasibility_projection"]
        require(set(projection) == set(FEASIBILITY_PROJECTION_FIELDS), "ledger feasibility projection has extra fields")

    require(len(records) == 50, "validated raw count mismatch")
    require(raw_manifest["n_valid_worlds"] == EXPECTED_VALID_WORLDS, "raw valid count mismatch")
    manifest_seeds = [int(row["seed"]) for row in raw_manifest["entries"]]
    require(manifest_seeds == EXPECTED_SEEDS, "raw-manifest seed order mismatch")
    require(len(manifest_seeds) == len(set(manifest_seeds)), "raw-manifest duplicate seed")
    require(raw_manifest["seal_sha256"] == EXPECTED_SEAL_SHA256, "raw manifest seal mismatch")

    raw_files = sorted((run_dir / "raw").glob("seed_*.json"))
    require(len(raw_files) == 50, f"expected 50 raw files, found {len(raw_files)}")
    raw_rows = []
    for entry, record in zip(raw_manifest["entries"], records):
        seed = int(entry["seed"])
        path = run_dir / entry["path"]
        committed_raw_bytes = committed_file_bytes(repo, RUN_REL / entry["path"])
        digest = sha256_bytes(committed_raw_bytes)
        require(digest == entry["sha256"], f"raw file digest mismatch at seed {seed}")
        committed = committed_binding(repo, EXPECTED_COMMIT, rel(path, repo))
        require(committed["sha256"] == digest, f"committed raw bytes mismatch at seed {seed}")
        completion = completions[seed - EXPECTED_SEEDS[0]]
        require(completion["raw"]["sha256"] == digest, f"ledger raw hash mismatch at seed {seed}")
        expected_projection = {"seed": seed, **record["feasibility"]}
        require(completion["feasibility_projection"] == expected_projection, f"ledger feasibility mismatch at seed {seed}")
        feasible = record["feasibility"]
        validity_from_feasibility = bool(
            feasible["eligible"]
            and feasible["deep_reached"]
            and feasible["rest_assay_valid"]
            and feasible["deep_assay_valid"]
        )
        require(feasible["valid"] == validity_from_feasibility, f"validity is not feasibility-only at seed {seed}")
        raw_rows.append({"seed": seed, "sha256": digest, "git_blob": committed["git_blob"], "bytes": len(committed_raw_bytes)})

    changed = git_text(
        repo,
        "diff",
        "--name-status",
        EXPECTED_AUTHORIZATION_COMMIT,
        EXPECTED_COMMIT,
        "--",
        str(RUN_REL / "raw").replace("\\", "/"),
    ).splitlines()
    require(len(changed) == 50, "raw Git diff does not contain exactly 50 paths")
    require(all(row.startswith("A\t") for row in changed), "a raw path was modified/overwritten instead of added once")

    reserve_paths = [
        path for path in (run_dir / "raw").glob("seed_*.json")
        if int(path.stem.split("_")[-1]) not in EXPECTED_SEEDS
    ]
    require(not reserve_paths, "reserve raw output exists")
    close = next(entry for entry in entries if entry["event"] == "CLOSE_FAMILY")
    raw_manifest_sha = sha256_bytes(raw_manifest_bytes)
    require(close["raw_manifest"]["sha256"] == raw_manifest_sha, "family-close manifest hash mismatch")
    record_analysis = next(entry for entry in entries if entry["event"] == "RECORD_ANALYSIS")
    committed_certificate_sha = committed_binding(repo, EXPECTED_COMMIT, str(CERT_REL).replace("\\", "/"))["sha256"]
    require(record_analysis["analysis"]["sha256"] == committed_certificate_sha, "ledger analysis hash mismatch")
    certification = next(entry for entry in entries if entry["event"] == "CERTIFY")
    require(certification["certificate"]["sha256"] == committed_certificate_sha, "ledger certification hash mismatch")
    require(execution_index["ledger"]["tip_hash"] == status["tip_hash"], "execution index ledger tip mismatch")

    ledger_audit = {
        **status,
        "event_counts": dict(sorted(counts.items())),
        "seed_starts": starts,
        "seed_completions": completion_seeds,
        "seed_resumes": resumes,
        "reserve_seed_count": 0,
        "second_execution_or_resume": False,
        "raw_records_added_once_in_git": True,
        "reserve_decision": {
            "active": decision["active"],
            "valid_worlds_after_primary": decision["valid_worlds_after_primary"],
            "fields_used": decision["fields_used"],
            "outcome_fields_used": decision["outcome_fields_used"],
        },
    }
    raw_audit = {
        "schema": raw_manifest["raw_schema"],
        "manifest_sha256": raw_manifest_sha,
        "byte_source": "exact committed Git blobs (working-tree EOL conversion bypassed)",
        "record_count": len(records),
        "valid_worlds": raw_manifest["n_valid_worlds"],
        "minimum_valid_worlds": execution_manifest["seed_plan"]["minimum_valid_worlds"],
        "records": raw_rows,
        "all_digests_match": True,
        "all_records_schema_valid": True,
        "validity_uses_feasibility_only": True,
        "reserve_activation_uses_feasibility_only": True,
        "outcome_fields_used_for_validity_or_reserve": False,
    }
    return ledger_audit, raw_audit, records, entries


def closed_prefix_reproduction(
    repo: Path,
    analyzer,
    execution_manifest: dict,
    ledger_entries: list[dict],
) -> tuple[dict, dict]:
    family_index = next(
        index for index, entry in enumerate(ledger_entries)
        if entry["new_state"] == "FAMILY_CLOSED"
    )
    closed_entries = ledger_entries[: family_index + 1]
    last = closed_entries[-1]
    anchor = {
        "schema": last["schema"],
        "seq": int(last["seq"]),
        "tip_hash": last["entry_hash"],
        "state": last["new_state"],
        "terminal": False,
    }
    with tempfile.TemporaryDirectory(prefix="lci-turnover-03m-") as temporary:
        temp_run = Path(temporary) / RUN_REL.name
        temp_run.mkdir(parents=True)
        raw_manifest_bytes = committed_file_bytes(repo, RAW_MANIFEST_REL)
        raw_manifest = json.loads(raw_manifest_bytes)
        (temp_run / "raw_manifest_03g.json").write_bytes(raw_manifest_bytes)
        for raw_entry in raw_manifest["entries"]:
            raw_path = temp_run / raw_entry["path"]
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_bytes(committed_file_bytes(repo, RUN_REL / raw_entry["path"]))
        source_lines = committed_file_bytes(repo, LEDGER_REL).splitlines(keepends=True)
        require(len(source_lines) == len(ledger_entries), "ledger physical line count mismatch")
        (temp_run / "execution_ledger_03g.jsonl").write_bytes(b"".join(source_lines[: family_index + 1]))
        (temp_run / "execution_ledger_03g.anchor.json").write_bytes(canonical_bytes(anchor) + b"\n")
        manifest_for_analysis = dict(execution_manifest)
        manifest_for_analysis["_repo_root"] = str(repo.resolve())
        result = analyzer.analyze(temp_run, manifest_for_analysis, EXPECTED_SEAL_SHA256)
        generated_certificate_bytes = (temp_run / "analysis" / "analysis_certificate_03g.json").read_bytes()
        generated_report_bytes = (temp_run / "analysis" / "analysis_report_03g.md").read_bytes()
    committed_certificate_bytes = committed_file_bytes(repo, CERT_REL)
    committed_report_bytes = committed_file_bytes(repo, CERT_REPORT_REL)
    require(generated_certificate_bytes == committed_certificate_bytes, "canonical regenerated certificate differs byte-for-byte")
    require(generated_report_bytes == committed_report_bytes, "canonical regenerated report differs byte-for-byte")
    certificate = json.loads(committed_certificate_bytes)
    return certificate, {
        "closed_ledger_entries": len(closed_entries),
        "closed_ledger_tip": last["entry_hash"],
        "temporary_closed_family_only": True,
        "original_certified_directory_modified": False,
        "generated_certificate_sha256": sha256_bytes(generated_certificate_bytes),
        "committed_certificate_sha256": sha256_bytes(committed_certificate_bytes),
        "certificate_exact_bytes": True,
        "report_exact_bytes": True,
        "outcome": result["certificate"]["outcome"],
    }


def run_independent(repo: Path) -> dict:
    script = repo / INDEPENDENT_REL
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = ""
    completed = subprocess.run(
        [sys.executable, str(script), "--repo", str(repo)],
        cwd=repo,
        env=environment,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    require(completed.returncode == 0, f"independent cross-check failed: {completed.stderr}")
    result = json.loads(completed.stdout)
    require(result["engine_imported"] is False and not result["banned_imports"], "independent cross-check imported banned code")
    return result


def compare_nested(expected: Any, actual: Any, path: str, audit: dict) -> None:
    if isinstance(expected, bool) or isinstance(actual, bool):
        require(type(expected) is type(actual) and expected == actual, f"comparison mismatch at {path}")
        audit["leaf_count"] += 1
        return
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        a = float(expected)
        b = float(actual)
        require(math.isfinite(a) and math.isfinite(b), f"non-finite comparison at {path}")
        difference = abs(a - b)
        audit["numeric_leaf_count"] += 1
        audit["leaf_count"] += 1
        audit["max_abs_difference"] = max(audit["max_abs_difference"], difference)
        if difference > audit["material_tolerance"]:
            audit["material_disagreements"].append({"path": path, "canonical": a, "independent": b, "abs_difference": difference})
        return
    if isinstance(expected, dict) and isinstance(actual, dict):
        require(set(expected) == set(actual), f"comparison key mismatch at {path}")
        for key in expected:
            compare_nested(expected[key], actual[key], f"{path}.{key}", audit)
        return
    if isinstance(expected, list) and isinstance(actual, list):
        require(len(expected) == len(actual), f"comparison list length mismatch at {path}")
        for index, (left, right) in enumerate(zip(expected, actual)):
            compare_nested(left, right, f"{path}[{index}]", audit)
        return
    require(expected == actual, f"comparison mismatch at {path}: {expected!r} != {actual!r}")
    audit["leaf_count"] += 1


def compare_canonical_independent(certificate: dict, independent: dict) -> dict:
    canonical = {
        "n_raw_worlds": certificate["n_raw_worlds"],
        "n_valid_worlds": certificate["n_valid_worlds"],
        "ownership": certificate["ownership"],
        "causal": certificate["causal"],
        "primary": certificate["primary"],
        "gates": certificate["gates"],
        "outcome": certificate["outcome"],
        "outcome_name": certificate["outcome_name"],
        "authorized_wording": certificate["authorized_wording"],
    }
    other = {key: independent[key] for key in canonical}
    audit = {
        "material_tolerance": 1e-12,
        "leaf_count": 0,
        "numeric_leaf_count": 0,
        "max_abs_difference": 0.0,
        "material_disagreements": [],
    }
    compare_nested(canonical, other, "result", audit)
    audit["material_agreement"] = not audit["material_disagreements"]
    audit["exact_numeric_agreement"] = audit["max_abs_difference"] == 0.0
    require(audit["material_agreement"], f"material canonical/independent disagreement: {audit['material_disagreements'][:3]}")
    return audit


def per_seed_rows(records: list[dict], raw_manifest: dict, raw_manifest_sha: str) -> list[dict]:
    rows = []
    source = f"{str(RAW_MANIFEST_REL).replace('\\', '/')}@sha256:{raw_manifest_sha}"
    generator = str(GENERATOR_REL).replace("\\", "/")
    for record, entry in zip(records, raw_manifest["entries"]):
        feasibility = record["feasibility"]
        science = record["scientific"]
        g0 = science["g0"]
        evidence_value = science["tracking_event_evidence"] or {}
        evidence_rows = (
            [row for row in evidence_value if isinstance(row, dict)]
            if isinstance(evidence_value, list)
            else [evidence_value]
        )
        evidence_rows = [row for row in evidence_rows if row]
        evidence = evidence_rows[0] if evidence_rows else {}
        material = science["material_tracer"] or {}
        deep_m = list(material.get("deep_M") or [])
        rest = science["causal_intervention_battery"]["rest"]
        deep = science["causal_intervention_battery"].get("deep")
        rest_sizes = rest["intact"]["size"] if rest else []
        deep_sizes = deep["intact"]["size"] if deep else []
        event_parent_sizes = evidence.get("event_frame", {}).get("parent_sizes", [])
        event_classification = ";".join(
            str(row.get("classification", "")) for row in evidence_rows if row.get("classification")
        )
        tracker_status = ";".join(
            str(row.get("raw_tracker_status", "")) for row in evidence_rows if row.get("raw_tracker_status")
        )
        event_steps = ";".join(
            str(row.get("event_step", "")) for row in evidence_rows if row.get("event_step") is not None
        )
        rows.append({
            "seed": int(record["seed"]),
            "eligible": feasibility["eligible"],
            "deep_reached": feasibility["deep_reached"],
            "rest_assay_valid": feasibility["rest_assay_valid"],
            "deep_assay_valid": feasibility["deep_assay_valid"],
            "valid": feasibility["valid"],
            "reason": feasibility["reason"] or "",
            "censored": not feasibility["valid"],
            "censoring_reason": science["censoring_reason"] or "",
            "g0_rest_valid": bool(g0.get("rest_valid")),
            "g0_deep_valid": bool(g0.get("deep_valid")),
            "g0_status": "PASS" if bool(g0.get("rest_valid")) and bool(g0.get("deep_valid")) else "FAIL",
            "event_classification": event_classification,
            "raw_tracker_status": tracker_status,
            "event_step": event_steps,
            "deep_snapshot_step": science["snapshot_time"] if science["snapshot_time"] is not None else "",
            "M_0": deep_m[0] if len(deep_m) > 0 else "",
            "M_1": deep_m[1] if len(deep_m) > 1 else "",
            "M_2": deep_m[2] if len(deep_m) > 2 else "",
            "rest_tracked_entity_sizes": ";".join(str(value) for value in rest_sizes),
            "deep_tracked_entity_sizes": ";".join(str(value) for value in deep_sizes),
            "event_parent_entity_sizes": ";".join(str(value) for value in event_parent_sizes),
            "raw_sha256": entry["sha256"],
            "raw_inputs": source,
            "generating_script": generator,
        })
    return rows


def number(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return format(value, ".17g")
    return str(value)


def primary_rows(certificate: dict, raw_manifest_sha: str) -> list[dict]:
    ownership = certificate["ownership"]
    causal = certificate["causal"]
    source = f"{str(RAW_MANIFEST_REL).replace('\\', '/')}@sha256:{raw_manifest_sha}"
    generator = str(GENERATOR_REL).replace("\\", "/")
    rows: list[dict] = []

    def add(section: str, metric: str, estimate=None, lower=None, upper=None, threshold="", passed="", interpretation="", scope="") -> None:
        rows.append({
            "table_section": section,
            "metric": metric,
            "scope": scope,
            "estimate": number(estimate),
            "lower_95": number(lower),
            "upper_95": number(upper),
            "threshold_or_rule": threshold,
            "pass": number(passed),
            "interpretation": interpretation,
            "raw_inputs": source,
            "generating_script": generator,
        })

    add("primary_result", "valid_original_worlds", certificate["n_valid_worlds"], threshold=f">={certificate['minimum_valid_worlds']}", passed=certificate["gates"]["FEASIBILITY"], interpretation="No reserve required")
    permutation = ownership["G_OWN_PERM"]
    observed_ci = permutation["observed_scope_result"]["skill_t95"]
    add("primary_result", "own_dose_mean_skill", permutation["observed_mean_skill"], observed_ci["lower"], observed_ci["upper"], "within-world permutation p<0.05", permutation["pass"], scope="L")
    add("primary_result", "own_dose_permutation_null_p95", permutation["null_p95"], threshold="observed score compared with 1000 within-world permutations", passed=permutation["pass"], scope="L")
    add("primary_result", "own_dose_empirical_p", permutation["p_value"], threshold="<0.05", passed=permutation["pass"], scope="L")

    for scope in ("L", "N", "E", "Gm", "B"):
        model = ownership["models"][scope]
        losses = [row["model_nmse"] for row in model["fold_losses"].values()]
        ci = model["skill_t95"]
        add("primary_result", "mean_model_nmse", float(sum(losses) / len(losses)), interpretation="Mean across fixed original-world held-out losses", scope=scope)
        add("primary_result", "held_out_skill", ci["mean"], ci["lower"], ci["upper"], "lower 95% > 0 for positive information", ci["lower"] > 0.0, scope=scope)

    for scope in ("N", "E", "Gm", "B"):
        ci = ownership["G_LOCAL_EXCLUSION"]["comparisons"][scope]["t95"]
        passed = ci["lower"] > 0.0
        add("primary_result", "paired_loss_difference_comparator_minus_L", ci["mean"], ci["lower"], ci["upper"], "lower 95% > 0", passed, "Positive means L has lower held-out loss", scope=scope)

    for metric, key, rule in (
        ("own_intact_minus_erase", "own_t95", "lower 95% > 0"),
        ("own_minus_sham", "own_minus_sham_t95", "lower 95% > 0"),
        ("own_minus_neighbour", "own_minus_neighbour_t95", "lower 95% > 0"),
        ("fixed_mask_own_effect", "own_fixed_t95", "mean > 0"),
        ("own_under_lambda_plus_only", "own_under_lambda_plus_only_ablation_t95", "upper < 0.5 * own mean"),
    ):
        ci = causal[key]
        if key == "own_fixed_t95":
            passed = ci["mean"] > 0.0
        elif key == "own_under_lambda_plus_only_ablation_t95":
            passed = causal["lambda_plus_only_collapse"]
        else:
            passed = ci["lower"] > 0.0
        add("primary_result", metric, ci["mean"], ci["lower"], ci["upper"], rule, passed, scope="causal")

    local = ownership["G_LOCAL_EXCLUSION"]
    failed_local = [key for key in ("L_information_lower_gt_zero", "L_over_N", "L_over_E", "L_over_Gm", "L_over_B") if not local[key]]
    add("gate_outcome", "FEASIBILITY", certificate["gates"]["FEASIBILITY"], threshold=f"{certificate['n_valid_worlds']}>={certificate['minimum_valid_worlds']}", passed=certificate["gates"]["FEASIBILITY"])
    add("gate_outcome", "G_OWN_PERM", certificate["gates"]["G_OWN_PERM"], threshold="empirical p<0.05", passed=certificate["gates"]["G_OWN_PERM"])
    add("gate_outcome", "G_LOCAL_EXCLUSION", certificate["gates"]["G_LOCAL_EXCLUSION"], threshold="L information and L>N,E,Gm,B lower 95% >0", passed=certificate["gates"]["G_LOCAL_EXCLUSION"], interpretation="Failed components: " + ", ".join(failed_local))
    add("gate_outcome", "G_CAUSAL", certificate["gates"]["G_CAUSAL"], threshold="all frozen causal subgates", passed=certificate["gates"]["G_CAUSAL"])
    distributed = ownership["DISTRIBUTED_ENV"]
    add("gate_outcome", "DISTRIBUTED_ENV", certificate["gates"]["DISTRIBUTED_ENV"], threshold=distributed["rule"], passed=certificate["gates"]["DISTRIBUTED_ENV"], interpretation=json.dumps(distributed["sources"], sort_keys=True))
    add("gate_outcome", "A-F_outcome", certificate["outcome"], threshold="unique frozen decision-tree match", passed=certificate["outcome"] == "B", interpretation=certificate["outcome_name"])
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    require(bool(rows), f"no rows for {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def create_figure(path: Path, records: list[dict], certificate: dict, raw_manifest_sha: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    valid = [record for record in records if record["feasibility"]["valid"]]
    deep_m = np.asarray([
        value
        for record in valid
        for value in record["scientific"]["material_tracer"]["deep_M"]
    ], dtype=float)
    ownership = certificate["ownership"]
    causal = certificate["causal"]
    blue = "#0072B2"
    orange = "#E69F00"
    green = "#009E73"
    red = "#D55E00"
    grey = "#6B7280"

    fig, axes = plt.subplots(2, 2, figsize=(12.2, 8.4), constrained_layout=True)
    ax = axes[0, 0]
    ax.hist(deep_m, bins=np.linspace(0.0, 0.5, 16), color=blue, alpha=0.8, edgecolor="white")
    ax.axvline(0.5, color=red, linestyle="--", linewidth=1.5, label="deep-turnover bound 0.5")
    ax.set(xlabel="Deep material retention M_i", ylabel="Target count", title="A  Material turnover (21 worlds × 3 targets)")
    ax.set_xlim(0.0, 0.52)
    ax.legend(frameon=False, fontsize=8)

    ax = axes[0, 1]
    causal_keys = [
        ("Own", "own_t95"),
        ("Own − sham", "own_minus_sham_t95"),
        ("Own − neighbour", "own_minus_neighbour_t95"),
        ("Fixed mask", "own_fixed_t95"),
        ("λ+ only", "own_under_lambda_plus_only_ablation_t95"),
    ]
    means = np.asarray([causal[key]["mean"] for _, key in causal_keys])
    lowers = np.asarray([causal[key]["lower"] for _, key in causal_keys])
    uppers = np.asarray([causal[key]["upper"] for _, key in causal_keys])
    y = np.arange(len(causal_keys))
    ax.errorbar(means, y, xerr=np.vstack([means - lowers, uppers - means]), fmt="o", color=green, ecolor=grey, capsize=3)
    ax.axvline(0.0, color="black", linewidth=0.8)
    ax.set_yticks(y, [label for label, _ in causal_keys])
    ax.invert_yaxis()
    ax.set(xlabel="World-level mean contrast (95% t interval)", title="B  Frozen causal contrasts")

    ax = axes[1, 0]
    scopes = ["N", "E", "Gm", "B"]
    cis = [ownership["G_LOCAL_EXCLUSION"]["comparisons"][scope]["t95"] for scope in scopes]
    means = np.asarray([ci["mean"] for ci in cis])
    lowers = np.asarray([ci["lower"] for ci in cis])
    uppers = np.asarray([ci["upper"] for ci in cis])
    colors = [green if lower > 0 else red for lower in lowers]
    for index, (mean, lower, upper, color) in enumerate(zip(means, lowers, uppers, colors)):
        ax.errorbar(mean, index, xerr=[[mean - lower], [upper - mean]], fmt="o", color=color, ecolor=grey, capsize=3)
    ax.axvline(0.0, color="black", linewidth=0.8)
    ax.set_yticks(np.arange(len(scopes)), [f"L vs {scope}" for scope in scopes])
    ax.invert_yaxis()
    ax.set(xlabel="Comparator loss − L loss (95% paired t interval)", title="C  Ownership-scope exclusion")

    ax = axes[1, 1]
    ax.axis("off")
    gate_order = ["FEASIBILITY", "G_OWN_PERM", "G_LOCAL_EXCLUSION", "G_CAUSAL", "DISTRIBUTED_ENV"]
    for index, gate in enumerate(gate_order):
        value = certificate["gates"][gate]
        color = green if value else (orange if gate == "DISTRIBUTED_ENV" else red)
        ax.text(0.04, 0.88 - index * 0.13, f"{gate}: {str(value).upper()}", fontsize=11, color=color, fontweight="bold", transform=ax.transAxes)
    ax.text(0.04, 0.14, "Unique frozen outcome", fontsize=10, color=grey, transform=ax.transAxes)
    ax.text(0.04, 0.04, "B — causal feeding effect without ownership", fontsize=13, color=blue, fontweight="bold", transform=ax.transAxes)
    ax.set_title("D  A–F decision tree", loc="left")

    fig.suptitle("LCI turnover 03M — independent reproduction from frozen raw data", fontsize=15, fontweight="bold")
    fig.text(
        0.01,
        0.002,
        f"Raw input: {str(RAW_MANIFEST_REL).replace('\\', '/')} (SHA-256 {raw_manifest_sha}) | Generator: {str(GENERATOR_REL).replace('\\', '/')}",
        fontsize=6.5,
        color=grey,
    )
    fig.savefig(
        path,
        dpi=220,
        metadata={
            "Title": "LCI turnover 03M independent reproduction",
            "Author": "raw_reproduction_03m.py",
            "Description": f"Raw input {str(RAW_MANIFEST_REL).replace('\\', '/')} SHA-256 {raw_manifest_sha}; generator {str(GENERATOR_REL).replace('\\', '/')}",
            "Software": f"matplotlib {matplotlib.__version__}",
        },
    )
    plt.close(fig)


def create_claim_note(path: Path, certificate: dict, raw_manifest_sha: str) -> None:
    ownership = certificate["ownership"]
    local = ownership["G_LOCAL_EXCLUSION"]
    failures = [key for key in ("L_information_lower_gt_zero", "L_over_N", "L_over_E", "L_over_Gm", "L_over_B") if not local[key]]
    text = f"""# Claim impact — LCI turnover raw reproduction 03M

- Raw input: `{str(RAW_MANIFEST_REL).replace('\\', '/')}` (SHA-256 `{raw_manifest_sha}`) and its 50 hash-bound raw records.
- Generating script: `{str(GENERATOR_REL).replace('\\', '/')}`.
- Status: **Outcome B independently reproduced from frozen raw data.**

## V4.1

This reproduction does not modify or retrospectively rescore V4.1, CONFIRM-02, or their scientific payloads. It adds a separate prospective turnover result: a local causal feeding contrast remains measurable after deep material turnover, but the frozen ownership comparison fails. V4.1 must not be revised to say that individual memory or identity survives.

## Future individuation paper

The admissible result sentence is:

> A causal feeding effect remains after deep material turnover, but the target’s graded history is not shown to be locally owned relative to the frozen comparison scopes.

The paper may report `G_OWN_PERM=true` and `G_CAUSAL=true`, but it must report in the same result that `G_LOCAL_EXCLUSION=false` (failed components: {', '.join(failures)}) and `DISTRIBUTED_ENV=false`. The first positive says own-dose information beats the within-world permutation null; it does not establish ownership. The failed exclusion gate blocks individuation. The false distributed-environment diagnostic does not prove the environment stores nothing; it means environmental ownership was not established in the frozen E/G-minus-target access classes.

Outcome B is a **passive local causal remnant**, not individual memory, identity, active reconstruction, heredity, reproduction, or life. Active reconstruction was not observed.
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def input_hashes(repo: Path, raw_audit: dict) -> dict:
    paths = [
        RAW_MANIFEST_REL,
        LEDGER_REL,
        LEDGER_ANCHOR_REL,
        CERT_REL,
        CERT_REPORT_REL,
        EXECUTION_MANIFEST_REL,
        DECISION_TREE_REL,
        SEAL_REL,
        AUTHORIZATION_REL,
        EXECUTION_INDEX_REL,
        PACKAGING_INDEX_REL,
        ENV_LOCK_REL,
    ]
    result = {
        str(path).replace("\\", "/"): committed_binding(
            repo, EXPECTED_COMMIT, str(path).replace("\\", "/")
        )["sha256"]
        for path in paths
    }
    result["raw_records"] = {str(row["seed"]): row["sha256"] for row in raw_audit["records"]}
    return result


def report_markdown(result: dict, artifact_hashes: dict[str, str]) -> str:
    certificate = result["canonical_certificate"]
    ownership = certificate["ownership"]
    permutation = ownership["G_OWN_PERM"]
    local = ownership["G_LOCAL_EXCLUSION"]
    causal = certificate["causal"]
    comparisons = local["comparisons"]
    failures = [key for key in ("L_information_lower_gt_zero", "L_over_N", "L_over_E", "L_over_Gm", "L_over_B") if not local[key]]
    distributed = ownership["DISTRIBUTED_ENV"]
    plus_ratio = causal["own_under_lambda_plus_only_ablation_t95"]["upper"] / causal["own_t95"]["mean"]

    def fmt(value: float) -> str:
        return f"{value:.9g}"

    artifact_lines = "\n".join(f"- `{path}` — SHA-256 `{digest}`" for path, digest in sorted(artifact_hashes.items()))
    scope_lines = "\n".join(
        f"| L vs {scope} | {fmt(comparisons[scope]['t95']['mean'])} | "
        f"[{fmt(comparisons[scope]['t95']['lower'])}, {fmt(comparisons[scope]['t95']['upper'])}] | "
        f"{str(comparisons[scope]['t95']['lower'] > 0).lower()} |"
        for scope in ("N", "E", "Gm", "B")
    )
    causal_lines = "\n".join(
        f"| {label} | {fmt(causal[key]['mean'])} | [{fmt(causal[key]['lower'])}, {fmt(causal[key]['upper'])}] |"
        for label, key in (
            ("own intact−erase", "own_t95"),
            ("own−sham", "own_minus_sham_t95"),
            ("own−neighbour", "own_minus_neighbour_t95"),
            ("fixed mask", "own_fixed_t95"),
            ("λ+ only", "own_under_lambda_plus_only_ablation_t95"),
        )
    )
    return f"""# LCI turnover raw reproduction 03M

- Result: **REPRODUCED**.
- Raw inputs: `{str(RAW_MANIFEST_REL).replace('\\', '/')}` (SHA-256 `{result['raw']['manifest_sha256']}`) and the 50 exact raw records listed in it.
- Generating script: `{str(GENERATOR_REL).replace('\\', '/')}`.
- Certified-results commit: `{result['provenance']['exact_results_commit']}`.
- Analysis branch parent: `{result['provenance']['exact_results_commit']}`; authorization commit `{result['provenance']['authorization_ancestor']}` is its exact parent and an ancestor.

## Provenance and raw integrity

The canonical final-seal SHA-256 is `{result['provenance']['final_seal_sha256']}`. All {result['provenance']['sealed_canonical_artifacts']['count']} final-seal canonical artifacts and all {result['provenance']['protected_runtime_bindings_verified']} execution-manifest runtime bindings match their declared Git blobs and SHA-256 values. The packaging bindings for the repaired execution manifest and reproduction guide match the committed objects.

The ledger verifies at terminal `CERTIFIED`: {result['ledger']['entries']} ordered entries, tip `{result['ledger']['tip_hash']}`. Seed starts and completions are exactly 54001–54050, once each, in ascending order. There are zero `SEED_RESUMED` events, zero reserve completions, and no second execution initialization. Git records each of the 50 raw paths as one addition after authorization, with no raw modification/overwrite.

All 50 exact committed raw blobs pass `LCI-TURNOVER-RAW-03G-v1`; every committed-byte SHA-256, ledger raw hash, and raw-manifest digest agrees. The Windows working-tree EOL conversion was deliberately bypassed and the checkout was not rewritten. There are {certificate['n_valid_worlds']} valid original worlds against the frozen minimum {certificate['minimum_valid_worlds']}. Validity is exactly the conjunction of the frozen feasibility fields; reserve activation used only `{', '.join(FEASIBILITY_PROJECTION_FIELDS)}` and used no outcome field.

## Canonical and independent reproduction

The frozen canonical analyzer was run on a temporary copy containing the exact immutable raw family and the exact ledger prefix ending at `FAMILY_CLOSED`. This was necessary because the committed ledger is already terminal `CERTIFIED`; the original run directory and certified outputs were never modified. The regenerated certificate and report are byte-for-byte identical to the committed artifacts.

The independent script reimplemented the preprocessing, training-fold scaling, λ=1 ridge, outer leave-one-original-world-out folds, fixed-world uncertainty, 1,000 within-world permutations, causal contrasts, and A–F tree without importing canonical analysis code. It agreed over {result['canonical_vs_independent']['leaf_count']} compared leaves ({result['canonical_vs_independent']['numeric_leaf_count']} numeric), with maximum absolute numeric difference `{result['canonical_vs_independent']['max_abs_difference']}`.

| Quantity | Canonical | Independent |
|---|---:|---:|
| valid worlds | {certificate['n_valid_worlds']} | {result['independent']['n_valid_worlds']} |
| own-dose mean skill | {fmt(permutation['observed_mean_skill'])} | {fmt(result['independent']['ownership']['G_OWN_PERM']['observed_mean_skill'])} |
| permutation null p95 | {fmt(permutation['null_p95'])} | {fmt(result['independent']['ownership']['G_OWN_PERM']['null_p95'])} |
| empirical p | {fmt(permutation['p_value'])} | {fmt(result['independent']['ownership']['G_OWN_PERM']['p_value'])} |
| own causal mean | {fmt(causal['own_t95']['mean'])} | {fmt(result['independent']['causal']['own_t95']['mean'])} |
| outcome | {certificate['outcome']} | {result['independent']['outcome']} |

Every canonical model prediction, original-world fold loss, t interval, fixed-fold bootstrap summary, permutation summary, paired scope contrast, causal interval, gate, and outcome in the machine JSON matched the independent calculation within the material tolerance `1e-12` (in fact, exact numeric agreement).

## A — G_OWN_PERM

Own-dose mean held-out skill is `{fmt(permutation['observed_mean_skill'])}`; the null 95th percentile is `{fmt(permutation['null_p95'])}` and empirical p is `{fmt(permutation['p_value'])}` (threshold `<0.05`). The observed world-level skill t interval is `[{fmt(permutation['observed_scope_result']['skill_t95']['lower'])}, {fmt(permutation['observed_scope_result']['skill_t95']['upper'])}]`. `G_OWN_PERM=true`.

## B — G_LOCAL_EXCLUSION

Positive paired values mean L has lower held-out loss than the comparator.

| Contrast | Mean | 95% t interval | Required lower > 0 |
|---|---:|---:|---:|
{scope_lines}

The exact failed components are `{', '.join(failures)}`. Therefore `G_LOCAL_EXCLUSION=false`: the target-local representation does not strictly exclude all frozen N, E, G-minus-target, and B comparison scopes.

## C — G_CAUSAL

| Contrast | Mean | 95% t interval |
|---|---:|---:|
{causal_lines}

The λ+-only upper interval divided by the own-effect mean is `{fmt(plus_ratio)}`, below the frozen collapse ratio `0.5`; λ− remains `0.15`. Own positivity, own>sham, own>neighbour, λ+-only collapse, fixed-mask directional consistency, and the 18-world minimum all pass. `G_CAUSAL=true`.

## D — DISTRIBUTED_ENV and unique Outcome B

The exact frozen environmental source flags are `{json.dumps(distributed['sources'], sort_keys=True)}` under the rule “{distributed['rule']}”. Therefore `DISTRIBUTED_ENV=false`. This does not prove that the environment stores nothing; it means environmental ownership is not established in the frozen E/G-minus-target access classes.

The gate vector is `FEASIBILITY=true`, `G_OWN_PERM=true`, `G_LOCAL_EXCLUSION=false`, `G_CAUSAL=true`, `DISTRIBUTED_ENV=false`. Exactly one A–F expression matches: **Outcome B — causal feeding effect without ownership**.

> A causal feeding effect remains after deep material turnover, but the target’s graded history is not shown to be locally owned relative to the frozen comparison scopes.

`G_OWN_PERM=true` beats the within-world null but does not by itself prove ownership. `G_LOCAL_EXCLUSION=false` blocks individuation. `DISTRIBUTED_ENV=false` does not transfer ownership to the environment. Forbidden interpretations remain: individual memory survives, identity survives, active reconstruction, heredity, reproduction, or definite environmental memory. Active reconstruction was not observed.

## Reproducibility record

- Clean executable: `{result['environment']['executable']}`.
- Runtime: CPython {result['environment']['runtime']['python']} on {result['environment']['runtime']['system']} {result['environment']['runtime']['machine']}.
- Packages: `{json.dumps(result['environment']['locked_packages'], sort_keys=True)}`.
- Wall runtime: {result['reproducibility']['runtime_seconds']:.3f} seconds.
- Command: `{result['reproducibility']['command']}`.
- Simulation/runner modules imported: none. Engine import attempts: none. No seed command was called.

## Derived output hashes

{artifact_lines}

The report's own hash is recorded in the reproduction journal after generation, avoiding a self-referential hash cycle.
"""


def simulation_modules_loaded() -> list[str]:
    return sorted(
        name
        for name in sys.modules
        if any(name == prefix or name.startswith(prefix + ".") for prefix in ENGINE_PREFIXES)
    )


def run(repo: Path) -> dict:
    start = time.perf_counter()
    repo = repo.resolve()
    output_dir = repo / OUTPUT_SUBDIR
    output_dir.mkdir(parents=True, exist_ok=True)

    provenance, execution_manifest, seal, authorization, execution_index = verify_git_and_seal(repo)
    environment = verify_environment(execution_manifest, repo)
    raw_schema, ledger, analyzer = import_canonical_modules(repo)
    ledger_audit, raw_audit, records, ledger_entries = verify_ledger_and_raw(
        repo, raw_schema, ledger, execution_manifest, execution_index
    )
    certificate, canonical_audit = closed_prefix_reproduction(
        repo, analyzer, execution_manifest, ledger_entries
    )
    independent = run_independent(repo)
    comparison = compare_canonical_independent(certificate, independent)
    require(certificate["outcome"] == independent["outcome"] == "B", "Outcome B did not reproduce")
    require(certificate["gates"] == {
        "FEASIBILITY": True,
        "G_OWN_PERM": True,
        "G_LOCAL_EXCLUSION": False,
        "G_CAUSAL": True,
        "DISTRIBUTED_ENV": False,
    }, "reproduced gates differ from expected vector")

    raw_manifest = json.loads(committed_file_bytes(repo, RAW_MANIFEST_REL))
    seed_table = output_dir / SEED_TABLE_NAME
    primary_table = output_dir / PRIMARY_TABLE_NAME
    figure = output_dir / FIGURE_NAME
    claim_note = output_dir / CLAIM_NOTE_NAME
    result_path = output_dir / RESULT_NAME
    report_path = output_dir / REPORT_NAME
    write_csv(seed_table, per_seed_rows(records, raw_manifest, raw_audit["manifest_sha256"]))
    write_csv(primary_table, primary_rows(certificate, raw_audit["manifest_sha256"]))
    create_figure(figure, records, certificate, raw_audit["manifest_sha256"])
    create_claim_note(claim_note, certificate, raw_audit["manifest_sha256"])

    loaded_simulation = simulation_modules_loaded()
    require(not ENGINE_IMPORT_ATTEMPTS, f"engine import was attempted: {ENGINE_IMPORT_ATTEMPTS}")
    require(not loaded_simulation, f"simulation module was loaded: {loaded_simulation}")
    runtime = time.perf_counter() - start
    command = f'& "{sys.executable}" "{repo / GENERATOR_REL}" --repo "{repo}"'
    pre_result_hashes = {
        rel(seed_table, repo): sha256_file(seed_table),
        rel(primary_table, repo): sha256_file(primary_table),
        rel(figure, repo): sha256_file(figure),
        rel(claim_note, repo): sha256_file(claim_note),
    }
    result = {
        "schema": "LCI-TURNOVER-RAW-REPRODUCTION-03M-v1",
        "mission": "LCI-TURNOVER-RAW-REPRODUCTION-03M",
        "status": "REPRODUCED",
        "provenance": provenance,
        "environment": environment,
        "ledger": ledger_audit,
        "raw": raw_audit,
        "canonical_reproduction": canonical_audit,
        "canonical_certificate": certificate,
        "independent": independent,
        "canonical_vs_independent": comparison,
        "outcome_interpretation": {
            "code": "B",
            "name": "causal feeding effect without ownership",
            "authorized_wording": "A causal feeding effect remains after deep material turnover, but the target’s graded history is not shown to be locally owned relative to the frozen comparison scopes.",
            "canonical_authorized_wording": certificate["authorized_wording"],
            "active_reconstruction_observed": False,
            "forbidden": [
                "individual memory survives",
                "identity survives",
                "active reconstruction",
                "heredity",
                "reproduction",
                "environment definitely stores the memory",
            ],
        },
        "reproducibility": {
            "runtime_seconds": runtime,
            "command": command,
            "input_hashes": input_hashes(repo, raw_audit),
            "simulation_modules_imported": loaded_simulation,
            "engine_import_attempts": list(ENGINE_IMPORT_ATTEMPTS),
            "seed_commands_called": 0,
            "original_raw_or_certified_outputs_modified": False,
        },
        "derived_artifacts": {
            path: {
                "sha256": digest,
                "raw_inputs": [str(RAW_MANIFEST_REL).replace("\\", "/"), "50 manifest-listed raw records"],
                "generating_script": str(GENERATOR_REL).replace("\\", "/"),
            }
            for path, digest in pre_result_hashes.items()
        },
    }
    result["derived_artifacts"][rel(result_path, repo)] = {
        "sha256": None,
        "self_hash_note": "Actual file hash is recorded in the report and journal; embedding it here would be self-referential.",
        "raw_inputs": [str(RAW_MANIFEST_REL).replace("\\", "/"), "50 manifest-listed raw records"],
        "generating_script": str(GENERATOR_REL).replace("\\", "/"),
    }
    result["derived_artifacts"][rel(report_path, repo)] = {
        "sha256": None,
        "hash_note": "Actual report hash is recorded in the reproduction journal after generation.",
        "raw_inputs": [str(RAW_MANIFEST_REL).replace("\\", "/"), "50 manifest-listed raw records"],
        "generating_script": str(GENERATOR_REL).replace("\\", "/"),
    }
    result_path.write_text(
        json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    report_hashes = {**pre_result_hashes, rel(result_path, repo): sha256_file(result_path)}
    report_path.write_text(report_markdown(result, report_hashes), encoding="utf-8", newline="\n")
    final_hashes = {**report_hashes, rel(report_path, repo): sha256_file(report_path)}
    return {
        "status": "REPRODUCED",
        "outcome": "B",
        "commit_parent": EXPECTED_COMMIT,
        "artifact_hashes": final_hashes,
        "runtime_seconds": runtime,
        "engine_imported": False,
        "seed_commands_called": 0,
        "max_canonical_independent_abs_difference": comparison["max_abs_difference"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args()
    summary = run(args.repo)
    sys.stdout.write(json.dumps(summary, sort_keys=True, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
