import unittest
from pathlib import Path

from runtime_audit_contracts import (
    ALL_MODES,
    CHAPTER_SOURCE_ANCHORS,
    DEDUP_MODES,
    MODE_EXTRA_ARGS,
    MODE_LOG_NAMES,
    MODE_MARKERS,
    SOURCE_MARKER_ANCHORS,
    STATE_SEQUENCE_MODES,
    chapters_for_mode,
    extra_args_for,
    log_name_for,
    required_markers,
)

ROOT = Path(__file__).resolve().parents[1]

class RuntimeAuditContractTests(unittest.TestCase):
    def test_registry_owns_every_runtime_mode(self):
        self.assertEqual(set(MODE_MARKERS), set(ALL_MODES) - {"chapters"})
        self.assertEqual(set(MODE_EXTRA_ARGS), set(ALL_MODES))
        self.assertEqual(set(MODE_LOG_NAMES), set(ALL_MODES) - {"chapters"})
        self.assertEqual(chapters_for_mode("chapters"), [f"P1C{i:02d}" for i in range(1, 9)])
        for mode in MODE_MARKERS:
            self.assertEqual(chapters_for_mode(mode), [None])
            self.assertEqual(required_markers(None, mode), list(MODE_MARKERS[mode]))
            self.assertEqual(extra_args_for(mode), list(MODE_EXTRA_ARGS[mode]))
            self.assertEqual(log_name_for(None, mode), MODE_LOG_NAMES[mode])

    def test_every_static_marker_has_a_source_anchor(self):
        cache = {}
        for mode, markers in MODE_MARKERS.items():
            anchors = SOURCE_MARKER_ANCHORS.get(mode, ())
            self.assertEqual({entry[0] for entry in anchors}, set(range(len(markers))), mode)
            for marker_index, relative, anchor in anchors:
                path = ROOT / relative
                self.assertTrue(path.is_file(), relative)
                text = cache.setdefault(relative, path.read_text(encoding="utf-8"))
                self.assertIn(anchor, text, f"{mode}[{marker_index}] -> {relative}")

    def test_chapter_dynamic_marker_sources_exist(self):
        for relative, anchor in CHAPTER_SOURCE_ANCHORS:
            self.assertIn(anchor, (ROOT / relative).read_text(encoding="utf-8"), relative)

    def test_contract_consumers_do_not_copy_transaction_marker_text(self):
        consumers = [
            ROOT / "Scripts" / "runtime_smoke.py",
            ROOT / "Scripts" / "test_runtime_smoke.py",
            ROOT / "Scripts" / "pre_unreal_validate.py",
        ]
        for mode in DEDUP_MODES:
            for marker in MODE_MARKERS[mode]:
                for path in consumers:
                    self.assertNotIn(marker, path.read_text(encoding="utf-8"),
                                     f"{path.name} duplicates {mode} marker")

    def test_state_ci_executes_every_registered_transaction_mode_once(self):
        text = (ROOT / "Scripts" / "ci_runtime_state.cmd").read_text(encoding="utf-8")
        for mode in STATE_SEQUENCE_MODES:
            self.assertEqual(text.count(f"--mode {mode}"), 1, mode)

if __name__ == "__main__":
    unittest.main()
