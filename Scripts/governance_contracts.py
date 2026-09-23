"""Shared semantic contracts for Project Governor validation.

This module deliberately validates structured Governor data rather than duplicating
phase allowlists or searching prose for evidence keywords.
"""


def validate_development_mode(governor):
    errors = []
    contract = governor.get("development_mode_contract", {})
    mode = governor.get("development_mode", {})

    if contract.get("authority") != "Data/ProjectGovernor.json":
        errors.append("development_mode_contract authority must remain Data/ProjectGovernor.json")

    modes = contract.get("modes", {})
    mode_id = str(mode.get("id") or "")
    if not mode_id or mode_id not in modes:
        errors.append("development mode is not registered in the Governor-owned contract")
        return errors

    expected_supersedes = modes[mode_id].get("supersedes")
    if mode.get("supersedes") != expected_supersedes:
        errors.append(
            "development mode supersedes value disagrees with the Governor-owned contract"
        )

    required_labels = set(contract.get("required_manual_only_labels", []))
    if not required_labels:
        errors.append("development_mode_contract has no manual-only acceptance labels")

    proof = mode.get("proof_boundary", {})
    if proof.get("machine_evidence_cannot_promote_manual_acceptance") is not True:
        errors.append("development mode lost the machine-vs-manual proof boundary")

    mode_labels = set(proof.get("manual_only_labels", []))
    missing = sorted(required_labels - mode_labels)
    if missing:
        errors.append("development mode is missing manual-only labels: " + ", ".join(missing))

    return errors
