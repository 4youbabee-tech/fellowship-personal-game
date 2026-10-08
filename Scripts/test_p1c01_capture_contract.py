import pathlib
import unittest

class P1C01CaptureContractTests(unittest.TestCase):
    def test_capture_has_lifecycle_safety_contract(self):
        path = pathlib.Path(__file__).with_name("ci_capture_p1c01_visuals.cmd")
        text = path.read_text(encoding="utf-8")
        self.assertIn('set "CAPTURE_WAIT_SECONDS=150"', text)
        self.assertIn('set "PROCESS_DRAIN_SECONDS=30"', text)
        self.assertIn('P1C01_RENDER_CAPTURE_PROCESS_DRAIN_PASS', text)
        self.assertIn('reason=ue4_process_drain_timeout', text)
        self.assertIn('waitSeconds=%CAPTURE_WAIT_SECONDS%', text)
        self.assertIn('Format-List', text)

if __name__ == "__main__":
    unittest.main()
