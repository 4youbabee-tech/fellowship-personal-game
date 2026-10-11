"""Static guard: local preview is lightweight and never claims acceptance."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class FastPIEPreviewContract(unittest.TestCase):
    def test_preview_uses_editor_and_never_packages_or_syncs(self):
        text = (ROOT / "SHIRE_FAST_PIE_PREVIEW.bat").read_text(encoding="utf-8")
        self.assertIn("ShireJourney.uproject", text)
        self.assertIn("UE_4.27", text)
        self.assertIn("UE4Editor.exe", text)
        self.assertIn("UE4Editor-ShireJourney.dll", text)
        self.assertIn(" -d3d11 -ResX=1280 -ResY=720 -log", text)
        self.assertIn("NOTICE: session metadata only, not PIE-TESTED", text)
        self.assertIn("if not exist \"%EDITOR_DLL%\"", text)
        self.assertIn("exit /b 12", text)
        for forbidden in ("git pull", "git reset --hard", "ci_package_w00.cmd",
                          "SHIRE_UPDATE_BUILD_LAUNCH.bat", "CookRun", "RunUAT"):
            self.assertNotIn(forbidden.lower(), "\n".join(
                ln.lower() for ln in text.splitlines()
                if not ln.lstrip().lower().startswith(("echo ", "rem "))
            ))
if __name__ == "__main__":
    unittest.main()
