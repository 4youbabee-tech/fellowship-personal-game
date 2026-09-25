import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = str(Path(__file__).with_name("operation_recovery.py"))


class OperationRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = Path(self.tmp.name) / "state.json"

    def tearDown(self):
        self.tmp.cleanup()

    def runop(self, *args, check=True):
        proc = subprocess.run(
            ["python", SCRIPT, "--state", str(self.state), *args],
            text=True,
            capture_output=True,
        )
        if check and proc.returncode != 0:
            self.fail((proc.returncode, proc.stdout, proc.stderr))
        return proc

    def test_completed_step_is_not_repeated(self):
        sha = "a" * 40
        self.runop("begin", "--operation", "X", "--target-sha", sha, "--step", "A", "--timeout-seconds", "60")
        self.runop("complete", "--operation", "X", "--target-sha", sha, "--step", "A", "--evidence", "ok")
        proc = self.runop("begin", "--operation", "X", "--target-sha", sha, "--step", "A", "--timeout-seconds", "60")
        self.assertIn("RECOVERY_SKIP_COMPLETED", proc.stdout)

    def test_stuck_step_requires_audit(self):
        sha = "a" * 40
        self.runop("begin", "--operation", "X", "--target-sha", sha, "--step", "A", "--timeout-seconds", "1")
        state = json.loads(self.state.read_text())
        key = "X@" + sha
        state["operations"][key]["steps"]["A"]["started_at"] = "2000-01-01T00:00:00+00:00"
        self.state.write_text(json.dumps(state))
        proc = self.runop("begin", "--operation", "X", "--target-sha", sha, "--step", "A", "--timeout-seconds", "1", check=False)
        self.assertEqual(proc.returncode, 2)
        state = json.loads(self.state.read_text())
        self.assertTrue(state["operations"][key]["audit_required"])
        self.assertEqual(state["operations"][key]["steps"]["A"]["status"], "STUCK")

    def test_checkpoint_reuse_is_exact_sha_scoped(self):
        sha_a = "a" * 40
        sha_b = "b" * 40
        self.runop("begin", "--operation", "X", "--target-sha", sha_a, "--step", "A", "--timeout-seconds", "60")
        self.runop("complete", "--operation", "X", "--target-sha", sha_a, "--step", "A")
        proc = self.runop("begin", "--operation", "X", "--target-sha", sha_b, "--step", "A", "--timeout-seconds", "60")
        self.assertIn("RECOVERY_BEGIN", proc.stdout)

    def test_failure_requires_audit(self):
        sha = "a" * 40
        self.runop("fail", "--operation", "X", "--target-sha", sha, "--step", "A", "--reason", "timeout")
        state = json.loads(self.state.read_text())
        self.assertTrue(state["operations"]["X@" + sha]["audit_required"])


if __name__ == "__main__":
    unittest.main()
