"""Independent, offline consistency audit for allowlisted ETCMNFC Git blobs.

This script imports no repository module and never materializes a source tree.  It
reads only the explicit ETCMNFC paths below from one immutable Git commit.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from collections import Counter


COMMIT = "c5171b72f3ed2cdaba1968bdbd9ebf3776eab8d7"
PREFIX = "ETCMNFC/"
JSON_PATHS = {
    "offline": "etcmnfc_gates_offline.json",
    "phase_c": "etcmnfc_phaseC.json",
    "phase_c2": "etcmnfc_phaseC2.json",
    "protocol": "etcmnfc_protocol.json",
    "verify": "etcmnfc_verify.json",
    "topology": "probe_alive_topology.json",
    "attribution": "probe_attribution.json",
    "depth": "probe_depth.json",
}


def blob(relative_path: str) -> bytes:
    if any(token in relative_path.lower() for token in ("held", "near", "checkpoint", "trajectory", "engine")):
        raise RuntimeError(f"path rejected by local firewall: {relative_path}")
    return subprocess.check_output(
        ["git", "show", f"{COMMIT}:{PREFIX}{relative_path}"],
        stderr=subprocess.DEVNULL,
    )


def load_json(relative_path: str):
    return json.loads(blob(relative_path).decode("utf-8"))


def check(condition: bool, label: str, failures: list[str]) -> None:
    if not condition:
        failures.append(label)


def main() -> None:
    data = {name: load_json(path) for name, path in JSON_PATHS.items()}
    failures: list[str] = []

    sums_lines = blob("SHA256SUMS").decode("utf-8").splitlines()
    sum_entries: dict[str, str] = {}
    for line in sums_lines:
        digest, path = line.split(maxsplit=1)
        relative = path.removeprefix("./")
        sum_entries[relative] = digest
    sum_mismatches = []
    for relative, expected in sorted(sum_entries.items()):
        observed = hashlib.sha256(blob(relative)).hexdigest()
        if observed != expected:
            sum_mismatches.append(relative)
    check(not sum_mismatches, "SHA256SUMS mismatch", failures)

    protocol_bytes = blob("etcmnfc_protocol.json")
    protocol_digest = hashlib.sha256(protocol_bytes).hexdigest()
    protocol_seal = blob("etcmnfc_protocol.sha256").decode("utf-8").strip().split()[0]
    check(protocol_digest == protocol_seal, "protocol seal mismatch", failures)

    offline_rows = data["offline"]["rows"]
    offline_passes = sum(row.get("PASS") is True for row in offline_rows)
    check(len(offline_rows) == 60, "offline row count is not 60", failures)
    check(offline_passes == 60, "offline pass count is not 60", failures)
    offline_gate_counts = Counter(row["gate"] for row in offline_rows)

    manifests = data["offline"]["MANIFESTS"]
    manifest_keys = sorted(manifests, key=int)
    check(len(manifest_keys) == 4, "development manifest count is not four", failures)
    pair_lists = []
    site_a_lists = []
    site_b_lists = []
    manifest_checks = []
    for key in manifest_keys:
        item = manifests[key]
        pairs = [tuple(pair) for pair in item["pairs_by_immutable_id"]]
        flat_ids = [value for pair in pairs for value in pair]
        sites_a = [tuple(site) for site in item["sites_A"]]
        sites_b = [tuple(site) for site in item["sites_B"]]
        manifest_base_keys = (
            "eligible_edge_fraction",
            "max_cardinality",
            "n_pairs",
            "n_sites_A",
            "n_sites_B",
            "pairs_by_immutable_id",
            "sites_A",
            "sites_B",
        )
        manifest_base = {name: item[name] for name in manifest_base_keys}
        recomputed_manifest_hash = hashlib.sha256(
            json.dumps(manifest_base, sort_keys=True).encode()
        ).hexdigest()
        row = {
            "block_redacted": f"DEV-{len(manifest_checks) + 1}",
            "pair_count_consistent": len(pairs) == item["n_pairs"] == item["max_cardinality"],
            "pair_ids_disjoint": len(flat_ids) == len(set(flat_ids)),
            "site_sets_disjoint": not (set(sites_a) & set(sites_b)),
            "all_reported_pairs_unequal_rho": item["n_unequal_rho_pairs"] == len(pairs),
            "reciprocal_float_summary_exact": item["delta_Q_A"] + item["delta_Q_B"] == 0.0,
            "full_support_reported": len(pairs) == len(sites_a) == len(sites_b),
            "pair_ids_match_site_coordinates": all(
                aid == ay * 64 + ax and bid == by * 64 + bx
                for (aid, bid), (ay, ax), (by, bx) in zip(pairs, sites_a, sites_b)
            ),
            "manifest_hash_recomputed": recomputed_manifest_hash == item["hash"],
        }
        manifest_checks.append(row)
        pair_lists.append(pairs)
        site_a_lists.append(sites_a)
        site_b_lists.append(sites_b)
        check(all(row.values()), f"manifest consistency failed for {key}", failures)
    geometry_reused = len({tuple(x) for x in site_a_lists}) == 1 and len({tuple(x) for x in site_b_lists}) == 1
    pair_manifest_reused = len({tuple(x) for x in pair_lists}) == 1
    check(geometry_reused, "reported common geometry is not common", failures)

    phase_c2_rows = data["phase_c2"]["rows"]
    check(len(phase_c2_rows) == 14, "phase C2 row count is not 14", failures)
    check(all(row.get("PASS") is True for row in phase_c2_rows), "phase C2 contains a non-pass", failures)
    check(len(data["phase_c2"]["SUPERSEDED_VACUOUS_ORACLES"]) == 3, "superseded oracle count is not three", failures)

    verify_rows = data["verify"]["rows"]
    check(data["verify"]["n"] == len(verify_rows) == 19, "verify count mismatch", failures)
    check(data["verify"]["n_pass"] == sum(row.get("PASS") is True for row in verify_rows), "verify pass count mismatch", failures)

    topology = data["topology"]
    attribution = data["attribution"]
    depth = data["depth"]
    check(len(topology) == len(attribution) == len(depth) == 4, "probe block count mismatch", failures)
    probe_rows = []
    for index, (topo, attr, dep) in enumerate(zip(topology, attribution, depth), start=1):
        same_key = topo["seed"] == attr["seed"] == dep["seed"]
        ratio = attr["rho_min_in_A_or_B"] / attr["rho_at_material_endpoints"]["median"]
        ratio_match = math.isclose(
            ratio,
            dep["rho_ratio_component_min_over_boundary_median"],
            rel_tol=1e-15,
            abs_tol=0.0,
        )
        row = {
            "block_redacted": f"DEV-{index}",
            "keys_align": same_key,
            "one_material_region": topo["n_alive_components"] == 1,
            "both_components_same_region": topo["A_and_B_same_blob"] is True,
            "boundary_link_counts_align": topo["n_material_bath_links"] == attr["material_bath_links"],
            "attributable_support_empty": attr["links_whose_material_endpoint_is_in_A_or_B"] == 0,
            "component_boundary_contact_empty": attr["component_cells_adjacent_to_a_non_alive_cell"] == 0,
            "reported_ratio_recomputed": ratio_match,
            "strict_positive_depth": dep["min_lattice_distance_component_to_bath"] > 0,
        }
        probe_rows.append(row)
        check(all(row.values()), f"probe consistency failed at row {index}", failures)

    protocol = data["protocol"]
    stop = protocol["stop_evidence"]
    check(stop["native_material_regions"] == 1, "protocol material-region summary mismatch", failures)
    check(stop["material_bath_links"] == 172, "protocol link summary mismatch", failures)
    check(stop["links_attributable_to_A_or_B"] == 0, "protocol support summary mismatch", failures)
    check(stop["generality_limit"].startswith("the four development blocks share IDENTICAL"), "protocol omits geometry reuse", failures)

    output = {
        "audit": "IPRR00R independent offline Git-blob consistency audit",
        "commit": COMMIT,
        "repository_modules_imported": 0,
        "scientific_engine_starts": 0,
        "sha256_manifest": {
            "entry_count": len(sum_entries),
            "mismatches": sum_mismatches,
            "self_covered": "SHA256SUMS" in sum_entries,
        },
        "protocol_seal": {
            "observed_sha256": protocol_digest,
            "seal_matches": protocol_digest == protocol_seal,
        },
        "offline_gate_ledger": {
            "rows": len(offline_rows),
            "passes": offline_passes,
            "gate_counts": dict(sorted(offline_gate_counts.items())),
            "scope": "internal consistency and source audit only; raw DEV arrays were not opened",
        },
        "manifest_consistency": manifest_checks,
        "same_geometry_across_four_rows": geometry_reused,
        "same_pair_manifest_across_four_rows": pair_manifest_reused,
        "phase_c2": {
            "rows": len(phase_c2_rows),
            "passes": sum(row.get("PASS") is True for row in phase_c2_rows),
            "superseded_vacuous_oracles": len(data["phase_c2"]["SUPERSEDED_VACUOUS_ORACLES"]),
        },
        "verification_ledger": {
            "rows": len(verify_rows),
            "passes": sum(row.get("PASS") is True for row in verify_rows),
            "warning": "a verifier ledger is not independent evidence merely because all stored booleans are true",
        },
        "endpoint_probe_consistency": probe_rows,
        "geometry_level_effective_n": 1 if geometry_reused else None,
        "limitations": [
            "Exact carrier conservation and byte involution cannot be recomputed from the JSON summaries alone.",
            "The raw DEV checkpoint paths were denied by the frozen sentinel and were not opened.",
            "Negative-control prose in JSON is not a raw adversarial witness; source logic must be audited separately.",
            "Held-out allocation was exposed at L1; the dependent held-out audit is NOT_AUDITABLE.",
        ],
        "failures": failures,
        "overall_internal_consistency": not failures,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
