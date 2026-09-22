"""Regression scenarios use real short-lived subprocesses, without Unreal."""
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
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
    def test_separate_chapter_success_does_not_prove_continuous_transitions(self):
        markers = required_markers(None, "transitions")
        separate = "\n".join(required_markers("P1C%02d" % i, "chapters")[0] for i in range(1, 9))
        self.assertEqual(missing_markers(separate, markers), markers)
        self.assertEqual(missing_markers(markers[0], markers), [])

    def test_runner_pause_past_deadline_cannot_pass_ready_observation(self):
        clock = [0.0]
        process = Mock()
        process.poll.return_value = None
        process.returncode = 1
        def pause(_):
            clock[0] += 80.0
        with tempfile.TemporaryDirectory() as directory:
            with patch("runtime_smoke.subprocess.Popen", return_value=process), \
                 patch("runtime_smoke.read_log", return_value="READY\n"), \
                 patch("runtime_smoke.time.monotonic", side_effect=lambda: clock[0]), \
                 patch("runtime_smoke.time.sleep", side_effect=pause):
                result = observe(["fake-editor"], Path(directory) / "runtime.log",
                                 ["READY"], timeout=45, observation=4)
        self.assertFalse(result["passed"])
        self.assertEqual(result["error"], "runtime readiness/observation timed out")
        self.assertEqual(result["max_poll_gap_seconds"], 80.0)
        self.assertEqual(result["timeout_seconds"], 45)
        process.terminate.assert_called_once()
        process.wait.assert_called_once()

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

    def test_all_five_chapter_markers_are_required(self):
        markers = required_markers("P1C08", "chapters")
        self.assertEqual(len(markers), 5)
        for omitted in markers:
            text = "\n".join(m for m in markers if m != omitted)
            self.assertEqual(missing_markers(text, markers), [omitted])

    def test_startup_requires_grounding_marker(self):
        markers = required_markers(None, "startup")
        self.assertEqual(len(markers), 3)
        self.assertIn("ShireStartupGrounding: PASS chapter=P1C01", markers)

    def test_state_requires_roundtrip_marker(self):
        self.assertEqual(required_markers(None, "state"), [
            "ShirePlayableStartup: GameMode ready",
            "ShireStartupGrounding: PASS chapter=P1C03",
            "ShireStateAudit: route-roundtrip=PASS",
            "ShireStateAudit: ring-core=PASS",
            "ShireStateAudit: discovery-core=PASS",
            "ShireStateAudit: progression-core=PASS",
            "ShireStateAudit: knowledge-core=PASS",
            "ShireStateAudit: disk-save-roundtrip=PASS",
        ])

    def test_in_memory_success_cannot_prove_disk_save(self):
        markers = required_markers(None, "state")
        memory_only = "\n".join(m for m in markers if "disk-save" not in m)
        self.assertEqual(missing_markers(memory_only, markers),
                         ["ShireStateAudit: disk-save-roundtrip=PASS"])

    def test_utf16_unreal_log(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "log"
            path.write_text("READY\n", encoding="utf-16")
            self.assertEqual(read_log(path), "READY\n")

    def test_invalid_timing_rejected_before_launch(self):
        with self.assertRaises(ValueError):
            observe(["not-an-editor"], Path("unused.log"), [], timeout=1, observation=2)

    def test_chapter_mode_does_not_fail_fast(self):
        source = Path(__file__).with_name("runtime_smoke.py").read_text(encoding="utf-8")
        loop_tail = source[source.find("for chapter in chapters:"):]
        self.assertNotIn('if not result["passed"]:\n            print(read_log(log)[-16000:], flush=True)\n            break', loop_tail)
        self.assertIn("RUNTIME_SWEEP_SUMMARY", source)


if __name__ == "__main__":
    unittest.main()
