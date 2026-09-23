import unittest
from pathlib import Path

from runtime_audit_contracts import (
    ALL_MODES,
    CHAPTER_EVIDENCE_KINDS,
    CHAPTER_SOURCE_ANCHORS,
    EVIDENCE_MARKERS,
    EVIDENCE_SOURCE_ANCHORS,
    MODE_EVIDENCE_IDS,
    MODE_EXTRA_ARGS,
    MODE_LOG_NAMES,
    MODE_MARKERS,
    STATE_SEQUENCE_MODES,
    chapters_for_mode,
    evidence_marker,
    extra_args_for,
    log_name_for,
    mode_has_evidence,
    required_markers,
)

ROOT = Path(__file__).resolve().parents[1]


class RuntimeAuditContractTests(unittest.TestCase):
    def test_registry_owns_every_runtime_mode(self):
        self.assertEqual(set(MODE_MARKERS), set(ALL_MODES) - {"chapters"})
        self.assertEqual(set(MODE_EVIDENCE_IDS), set(MODE_MARKERS))
        self.assertEqual(set(MODE_EXTRA_ARGS), set(ALL_MODES))
        self.assertEqual(set(MODE_LOG_NAMES), set(ALL_MODES) - {"chapters"})
        self.assertEqual(chapters_for_mode("chapters"), [f"P1C{i:02d}" for i in range(1, 9)])
        for mode, ids in MODE_EVIDENCE_IDS.items():
            self.assertEqual(required_markers(None, mode), [evidence_marker(i) for i in ids])
            for evidence_id in ids:
                self.assertTrue(mode_has_evidence(mode, evidence_id))

    def test_every_static_evidence_id_has_one_source_anchor(self):
        referenced = {evidence_id for ids in MODE_EVIDENCE_IDS.values() for evidence_id in ids}
        self.assertEqual(referenced, set(EVIDENCE_MARKERS))
        self.assertEqual(referenced, set(EVIDENCE_SOURCE_ANCHORS))
        cache = {}
        for evidence_id, (relative, anchor) in EVIDENCE_SOURCE_ANCHORS.items():
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            text = cache.setdefault(relative, path.read_text(encoding="utf-8"))
            self.assertIn(anchor, text, f"{evidence_id} -> {relative}")

    def test_chapter_dynamic_evidence_is_complete_and_sourced(self):
        self.assertEqual(set(CHAPTER_EVIDENCE_KINDS), set(CHAPTER_SOURCE_ANCHORS))
        markers = required_markers("P1C08", "chapters")
        self.assertEqual(len(markers), len(CHAPTER_EVIDENCE_KINDS))
        for relative, anchor in CHAPTER_SOURCE_ANCHORS.values():
            self.assertIn(anchor, (ROOT / relative).read_text(encoding="utf-8"), relative)

    def test_contract_consumers_do_not_copy_evidence_text(self):
        consumers = [
            ROOT / "Scripts" / "runtime_smoke.py",
            ROOT / "Scripts" / "test_runtime_smoke.py",
            ROOT / "Scripts" / "pre_unreal_validate.py",
            ROOT / "Scripts" / "deep_project_audit.py",
            ROOT / "Scripts" / "warning_debt_guard.py",
        ]
        for evidence_id, marker in EVIDENCE_MARKERS.items():
            for path in consumers:
                self.assertNotIn(marker, path.read_text(encoding="utf-8"),
                                 f"{path.name} duplicates {evidence_id}")

    def test_state_ci_executes_every_registered_transaction_mode_once(self):
        text = (ROOT / "Scripts" / "ci_runtime_state.cmd").read_text(encoding="utf-8")
        for mode in STATE_SEQUENCE_MODES:
            self.assertEqual(text.count(f"--mode {mode}"), 1, mode)


if __name__ == "__main__":
    unittest.main()
