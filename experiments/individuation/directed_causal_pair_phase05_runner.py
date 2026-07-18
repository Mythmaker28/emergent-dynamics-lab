"""Fail-before-engine entry point for DIRECTED-CAUSAL-PAIR-00 Phase 0.5.

This module intentionally imports only the Python standard library.  It checks
the exact DEV authorization, pair assignments, paths, and SHA-256 bindings
before importing the mechanical executor.  It has no generic seed/range/input
arguments and cannot execute a prospective template.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import importlib
from importlib import machinery
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any


MISSION = "DIRECTED-CAUSAL-PAIR-00"
MANIFEST_SCHEMA = "DIRECTED-CAUSAL-PAIR-00-PHASE05-DEV-MANIFEST-v1"
PHASE0_COMMIT = "4bcb551092291b7383c4168f653818d4bade14f6"
OPEN_DEV_NAMESPACE = list(range(50001, 50011))
PLAN = [50002, 50004, 50005, 50007]
ASSIGNMENTS = {
    "50002": {"target_A": 0, "target_B": 2, "sentinel": 1},
    "50004": {"target_A": 0, "target_B": 1, "sentinel": 2},
    "50005": {"target_A": 1, "target_B": 0, "sentinel": 2},
    "50007": {"target_A": 1, "target_B": 0, "sentinel": 2},
}
SEED_58_RE = re.compile(r"(?<!\d)58\d{3}(?!\d)")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_RE = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_OUTPUT = Path("docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_RAW")
EXPECTED_MANIFEST = Path(
    "docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE05_DEV_MANIFEST.json"
)
NAMESPACE_IMPORT_ROOTS = ("experiments", "experiments/individuation")
EXPECTED_INPUT_PATHS = frozenset(
    {
        "AGENTS.md",
        "docs/DECISION_LOG.md",
        "docs/PROJECT_STATE.md",
        "docs/RESEARCH_CHARTER.md",
        "docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json",
        "docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_REPORT.md",
        "docs/individuation/DIRECTED_CAUSAL_PAIR_00_PREREGISTRATION_DRAFT.md",
    }
)
EXPECTED_CODE_PATHS = frozenset(
    {
        ".gitattributes",
        "docs/individuation/DIRECTED_CAUSAL_PAIR_00_FINAL_RAW_SCHEMA.json",
        "edlab/__init__.py",
        "edlab/entities/__init__.py",
        "edlab/entities/detection.py",
        "edlab/entities/tracking.py",
        "edlab/experiments/__init__.py",
        "edlab/experiments/analyze_streaming.py",
        "edlab/experiments/baseline.py",
        "edlab/experiments/exp_sc_00.py",
        "edlab/experiments/sc_hmc/__init__.py",
        "edlab/experiments/sc_hmc/config.py",
        "edlab/experiments/sc_iom/__init__.py",
        "edlab/experiments/sc_iom/config.py",
        "edlab/experiments/sc_iom/engine.py",
        "edlab/experiments/sc_mcm/__init__.py",
        "edlab/experiments/sc_mcm/config.py",
        "edlab/experiments/sc_mcm/engine.py",
        "edlab/experiments/streaming.py",
        "edlab/observables/__init__.py",
        "edlab/observables/continuity.py",
        "edlab/observables/phenotype.py",
        "edlab/specs.py",
        "edlab/state.py",
        "edlab/substrates/__init__.py",
        "edlab/substrates/chemotaxis/__init__.py",
        "edlab/substrates/chemotaxis/diagnostics.py",
        "edlab/substrates/chemotaxis/engine.py",
        "edlab/substrates/particle_dynamics/__init__.py",
        "edlab/substrates/particle_dynamics/engine.py",
        "edlab/substrates/reaction_diffusion/__init__.py",
        "edlab/substrates/reaction_diffusion/engine.py",
        "edlab/substrates/scaffold/__init__.py",
        "edlab/substrates/scaffold/engine.py",
        "edlab/substrates/scaffold/observables.py",
        "edlab/validation/__init__.py",
        "edlab/validation/forces.py",
        "edlab/validation/nulls.py",
        "experiments/individuation/access_structure_noswap_operators.py",
        "experiments/individuation/access_structure_operators.py",
        "experiments/individuation/bijective_tracker.py",
        "experiments/individuation/causal_confirm.py",
        "experiments/individuation/directed_causal_pair_phase05_executor.py",
        "experiments/individuation/directed_causal_pair_phase05_mechanics.py",
        "experiments/individuation/directed_causal_pair_phase05_reproduce.py",
        "experiments/individuation/directed_causal_pair_phase05_runner.py",
        "experiments/individuation/material_tracer.py",
        "experiments/individuation/test_directed_causal_pair_phase05_mechanics.py",
        "experiments/individuation/test_directed_causal_pair_phase05_reproduce.py",
        "experiments/individuation/turnover_diag_engine.py",
        "requirements-lock.txt",
    }
)


def _candidate_import_shadow_paths() -> frozenset[str]:
    """Enumerate explicit importable siblings that could bypass bound .py files."""
    source_suffixes = tuple(machinery.SOURCE_SUFFIXES)
    binary_suffixes = tuple(
        dict.fromkeys((*machinery.EXTENSION_SUFFIXES, *machinery.BYTECODE_SUFFIXES))
    )
    all_suffixes = tuple(dict.fromkeys((*source_suffixes, *binary_suffixes)))
    candidates: set[str] = set()
    for relative in EXPECTED_CODE_PATHS:
        if not relative.endswith(".py"):
            continue
        source = Path(relative)
        if source.name == "__init__.py":
            package = source.parent
            for suffix in all_suffixes:
                candidates.add(f"{package.as_posix()}{suffix}")
                candidates.add((package / f"__init__{suffix}").as_posix())
        else:
            for suffix in binary_suffixes:
                candidates.add(source.with_suffix(suffix).as_posix())
            package_shadow = source.with_suffix("")
            for suffix in all_suffixes:
                candidates.add(
                    (package_shadow / f"__init__{suffix}").as_posix()
                )
    for namespace in NAMESPACE_IMPORT_ROOTS:
        root = Path(namespace)
        for suffix in all_suffixes:
            candidates.add(f"{root.as_posix()}{suffix}")
            candidates.add((root / f"__init__{suffix}").as_posix())
    return frozenset(candidates - EXPECTED_CODE_PATHS)


FORBIDDEN_IMPORT_SHADOW_PATHS = _candidate_import_shadow_paths()
REQUIRED_KEYS = {
    "schema",
    "mission",
    "mode",
    "phase0_commit",
    "code_commit",
    "allowed_seed_namespace",
    "worlds",
    "pair_assignments",
    "prospective_namespace",
    "output_directory",
    "input_files",
    "code_files",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _contains_58(value: Any) -> bool:
    if isinstance(value, bool) or value is None:
        return False
    if isinstance(value, int):
        return 58000 <= value <= 58999
    if isinstance(value, str):
        # Cryptographic identities are opaque. A coincidental five-digit run
        # inside a bound 40/64-character hexadecimal digest is not a namespace.
        if GIT_RE.fullmatch(value) or SHA256_RE.fullmatch(value):
            return False
        return bool(SEED_58_RE.search(value))
    if isinstance(value, dict):
        return any(_contains_58(key) or _contains_58(child) for key, child in value.items())
    if isinstance(value, list):
        return any(_contains_58(child) for child in value)
    return False


def _strict_int_list(value: Any, expected: list[int], label: str) -> None:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    if any(isinstance(item, bool) or not isinstance(item, int) for item in value):
        raise ValueError(f"{label} must contain JSON integers only")
    if value != expected:
        raise ValueError(f"{label} does not match the frozen exact order")


def _is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return bool(path.is_symlink() or (is_junction is not None and is_junction()))


def _path_chain_has_link_or_junction(repo: Path, relative: Path) -> bool:
    current = repo
    for part in relative.parts:
        if part in ("", "."):
            continue
        if part == "..":
            return True
        current = current / part
        if current.exists() and _is_link_or_junction(current):
            return True
    return False


def _resolve_repo_file(repo: Path, raw: str, *, must_exist: bool = True) -> Path:
    if not isinstance(raw, str) or not raw or Path(raw).is_absolute():
        raise ValueError("manifest paths must be nonempty repository-relative strings")
    relative = Path(raw)
    if _path_chain_has_link_or_junction(repo, relative):
        raise ValueError(f"symlink, junction, or parent traversal refused: {raw}")
    unresolved = repo / relative
    candidate = unresolved.resolve(strict=False)
    try:
        candidate.relative_to(repo)
    except ValueError as exc:
        raise ValueError(f"path escapes the isolated repository: {raw}") from exc
    if must_exist and (not candidate.is_file() or _is_link_or_junction(unresolved)):
        raise ValueError(f"bound file is missing, not regular, or a symlink: {raw}")
    if _contains_58(str(candidate)):
        raise ValueError("forbidden namespace path refused")
    return candidate


def _git_blob_id(repo: Path, commit: str, relative: str) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", f"{commit}:{relative.replace('\\', '/')}"] ,
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    value = completed.stdout.strip()
    if not GIT_RE.fullmatch(value):
        raise ValueError(f"invalid Git blob identity for {relative}")
    return value


def _require_ancestor(repo: Path, ancestor: str, descendant: str) -> None:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=repo,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise ValueError(f"required Git ancestry is absent: {ancestor} -> {descendant}")


def _require_exact_clean_code_checkout(repo: Path, code_commit: str) -> None:
    """Bind imports to the exact committed tree, not an ancestor plus dirty files."""
    head_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    head = head_result.stdout.strip()
    if not GIT_RE.fullmatch(head) or head != code_commit:
        raise ValueError("code_commit must equal the exact checked-out HEAD")
    status_result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=no"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    if status_result.stdout:
        raise ValueError("tracked worktree/index must be clean at code_commit")
    for relative in sorted(FORBIDDEN_IMPORT_SHADOW_PATHS):
        if _resolve_repo_file(repo, relative, must_exist=False).exists():
            raise ValueError(f"unbound import-shadow path refused: {relative}")


@contextmanager
def _isolated_import_cache():
    """Keep ignored repository bytecode out of the bound executor import path."""
    previous_prefix = sys.pycache_prefix
    previous_dont_write = sys.dont_write_bytecode
    with tempfile.TemporaryDirectory(prefix="dcp05-bound-import-") as directory:
        sys.pycache_prefix = str(Path(directory).resolve())
        sys.dont_write_bytecode = True
        importlib.invalidate_caches()
        try:
            yield
        finally:
            sys.pycache_prefix = previous_prefix
            sys.dont_write_bytecode = previous_dont_write
            importlib.invalidate_caches()


def validate_preflight(repo: Path, manifest_path: Path) -> tuple[dict[str, Any], str, Path]:
    """Validate every authorization and binding before importing the executor."""
    repo = repo.resolve(strict=True)
    unresolved_manifest = manifest_path.absolute()
    if _is_link_or_junction(unresolved_manifest):
        raise ValueError("manifest symlink/junction refused")
    manifest_path = unresolved_manifest.resolve(strict=True)
    try:
        manifest_path.relative_to(repo)
    except ValueError as exc:
        raise ValueError("manifest must be inside the isolated repository") from exc
    try:
        manifest_relative = manifest_path.relative_to(repo)
    except ValueError as exc:
        raise ValueError("manifest must be inside the isolated repository") from exc
    if _path_chain_has_link_or_junction(repo, manifest_relative) or _contains_58(str(manifest_path)):
        raise ValueError("manifest symlink/forbidden namespace refused")
    if manifest_relative.as_posix() != EXPECTED_MANIFEST.as_posix():
        raise ValueError("manifest is not at the fixed Phase-0.5 path")
    raw_bytes = manifest_path.read_bytes()
    manifest = json.loads(raw_bytes.decode("utf-8"))
    try:
        canonical_manifest = (
            json.dumps(
                manifest,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("manifest contains a noncanonical value") from exc
    if raw_bytes != canonical_manifest:
        raise ValueError("manifest bytes must be canonical sorted compact JSON with one LF")
    if not isinstance(manifest, dict) or set(manifest) != REQUIRED_KEYS:
        raise ValueError("manifest fields are not the exact Phase-0.5 contract")
    if _contains_58(manifest):
        raise ValueError("manifest contains a forbidden namespace reference")
    if manifest["schema"] != MANIFEST_SCHEMA or manifest["mission"] != MISSION:
        raise ValueError("manifest schema/mission mismatch")
    if manifest["mode"] != "DEV_ONLY_MECHANICAL":
        raise ValueError("only DEV_ONLY_MECHANICAL is executable")
    if manifest["phase0_commit"] != PHASE0_COMMIT:
        raise ValueError("manifest is not bound to the accepted Phase-0 commit")
    if not isinstance(manifest["code_commit"], str) or not GIT_RE.fullmatch(manifest["code_commit"]):
        raise ValueError("code_commit must be one full Git object ID")
    _require_ancestor(repo, PHASE0_COMMIT, manifest["code_commit"])
    _require_exact_clean_code_checkout(repo, manifest["code_commit"])
    _strict_int_list(manifest["allowed_seed_namespace"], OPEN_DEV_NAMESPACE, "allowed_seed_namespace")
    _strict_int_list(manifest["worlds"], PLAN, "worlds")
    if manifest["pair_assignments"] != ASSIGNMENTS:
        raise ValueError("pair assignments do not match the frozen Phase-0 mapping")
    if manifest["prospective_namespace"] is not None:
        raise ValueError("prospective namespace must remain null")
    if (
        not isinstance(manifest["output_directory"], str)
        or manifest["output_directory"] != EXPECTED_OUTPUT.as_posix()
    ):
        raise ValueError("output directory is not the fixed Phase-0.5 raw directory")
    output = _resolve_repo_file(repo, manifest["output_directory"], must_exist=False)
    if output.exists() and (not output.is_dir() or output.is_symlink()):
        raise ValueError("output target exists but is not a regular directory")

    for section in ("input_files", "code_files"):
        bindings = manifest[section]
        if not isinstance(bindings, dict) or not bindings:
            raise ValueError(f"{section} must be a nonempty exact-path mapping")
        expected_paths = EXPECTED_INPUT_PATHS if section == "input_files" else EXPECTED_CODE_PATHS
        if set(bindings) != set(expected_paths):
            raise ValueError(f"{section} paths do not match the exact frozen binding set")
        binding_commit = PHASE0_COMMIT if section == "input_files" else manifest["code_commit"]
        for relative, binding in sorted(bindings.items()):
            if not isinstance(binding, dict) or set(binding) != {"sha256", "git_blob"}:
                raise ValueError(f"invalid hash/blob binding object for {relative}")
            expected_hash = binding["sha256"]
            expected_blob = binding["git_blob"]
            if not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(expected_hash):
                raise ValueError(f"invalid SHA-256 binding for {relative}")
            if not isinstance(expected_blob, str) or not GIT_RE.fullmatch(expected_blob):
                raise ValueError(f"invalid Git blob binding for {relative}")
            path = _resolve_repo_file(repo, relative)
            if _sha256(path) != expected_hash:
                raise ValueError(f"worktree SHA-256 mismatch for {relative}")
            if _git_blob_id(repo, binding_commit, relative) != expected_blob:
                raise ValueError(f"Git blob binding mismatch for {relative}")

    manifest_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    return manifest, manifest_sha256, output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default=EXPECTED_MANIFEST.as_posix(),
    )
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    manifest_path = repo / args.manifest
    manifest, manifest_sha256, output = validate_preflight(repo, manifest_path)

    # This is intentionally the first import of any mechanical/engine module.
    # A fresh cache prefix prevents ignored repository bytecode from replacing
    # the exact hash-bound sources after preflight.
    with _isolated_import_cache():
        executor = importlib.import_module(
            "experiments.individuation.directed_causal_pair_phase05_executor"
        )
        executor.execute(
            repo=repo,
            manifest=manifest,
            manifest_sha256=manifest_sha256,
            output_dir=output,
            resume=bool(args.resume),
        )


if __name__ == "__main__":
    main()
