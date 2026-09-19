"""Regression scenarios use real short-lived subprocesses, without Unreal."""
import sys
import tempfile
from pathlib import Path
import unittest
from runtime_smoke import missing_markers, observe, read_log, required_markers


FAKE_EDITOR = r'''
import pathlib, signal, sys, time
log = pathlib.Path(sys.argv[1])
mode = sys.argv[2]
text = 'READY\n'
if mode == 'missing': text = 'not ready\n'
if mode == 'fatal': text += 'Fatal error: early crash\n'
log.write_text(text)
if mode == 'exit': sys.exit(0)
if mode == 'late':
    time.sleep(0.08)
    with log.open('a') as f: f.write('Ensure condition failed: delayed\n')
if mode == 'shutdown' and hasattr(signal, 'SIGTERM'):
    def stop(*unused):
        with log.open('a') as f: f.write('Assertion failed: during shutdown\n')
        sys.exit(0)
    signal.signal(signal.SIGTERM, stop)
time.sleep(10)
'''


class RuntimeSmokeTests(unittest.TestCase):
    def run_scenario(self, mode):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script, log = root / "fake.py", root / "runtime.log"
            script.write_text(FAKE_EDITOR)
            log.write_text("READY\n")  # stale evidence must not make the run pass
            return observe([sys.executable, str(script), str(log), mode], log,
                           ["READY"], timeout=0.9, observation=0.2, poll=0.01)

    def test_live_ready_process_passes_and_is_reaped(self):
        result = self.run_scenario("healthy")
        self.assertTrue(result["passed"], result)
        self.assertIsNotNone(result["exit_code"])

    def test_fatal_before_readiness_fails(self):
        self.assertFalse(self.run_scenario("fatal")["passed"])

    def test_failure_after_ready_markers_fails(self):
        self.assertFalse(self.run_scenario("late")["passed"])

    def test_spontaneous_clean_exit_is_not_a_healthy_game(self):
        self.assertFalse(self.run_scenario("exit")["passed"])

    def test_missing_markers_timeout_and_stale_log_rejected(self):
        result = self.run_scenario("missing")
        self.assertFalse(result["passed"])
        self.assertEqual(result["missing_markers"], ["READY"])
        self.assertIsNotNone(result["exit_code"])

    @unittest.skipIf(sys.platform == "win32", "Windows terminate does not deliver SIGTERM")
    def test_final_log_is_checked_after_termination(self):
        self.assertFalse(self.run_scenario("shutdown")["passed"])

    def test_marker_prefix_is_not_exact_chapter(self):
        self.assertEqual(missing_markers("chapter=P1C010", ["chapter=P1C01"]), ["chapter=P1C01"])

    def test_all_four_chapter_markers_are_required(self):
        markers = required_markers("P1C08", "chapters")
        self.assertEqual(len(markers), 4)
        for omitted in markers:
            text = "\n".join(m for m in markers if m != omitted)
            self.assertEqual(missing_markers(text, markers), [omitted])

    def test_startup_requires_both_markers(self):
        self.assertEqual(len(required_markers(None, "startup")), 2)

    def test_state_requires_roundtrip_marker(self):
        self.assertEqual(required_markers(None, "state"), [
            "ShirePlayableStartup: GameMode ready",
            "ShireStateAudit: route-roundtrip=PASS",
        ])

    def test_utf16_unreal_log(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "log"
            path.write_text("READY\n", encoding="utf-16")
            self.assertEqual(read_log(path), "READY\n")

    def test_invalid_timing_rejected_before_launch(self):
        with self.assertRaises(ValueError):
            observe(["not-an-editor"], Path("unused.log"), [], timeout=1, observation=2)


if __name__ == "__main__":
    unittest.main()
