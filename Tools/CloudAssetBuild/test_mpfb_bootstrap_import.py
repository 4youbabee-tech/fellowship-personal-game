"""Cheap regression for Blender's --python sibling-module import semantics."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class TestBootstrapImport(unittest.TestCase):
    def test_run_path_without_script_directory_or_blender(self):
        script = Path(__file__).with_name("mpfb_hosted_bootstrap.py").resolve()
        # Isolated Python + external cwd reproduces Blender's missing script path.
        # A bpy sentinel permits module loading but rejects any Blender API work.
        program = """
import runpy, sys, types
from pathlib import Path
script = Path(sys.argv[1])
assert str(script.parent) not in sys.path
sys.modules['bpy'] = types.ModuleType('bpy')
namespace = runpy.run_path(str(script), run_name='bootstrap_import_probe')
assert callable(namespace['main'])
assert callable(namespace['extract_verified_pack'])
assert Path(sys.modules['mpfb_pack_intake'].__file__).resolve() == script.with_name('mpfb_pack_intake.py')
print('MPFB_BOOTSTRAP_SIBLING_IMPORT_PASS')
"""
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run(
                [sys.executable, "-I", "-c", program, str(script)],
                cwd=cwd, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("MPFB_BOOTSTRAP_SIBLING_IMPORT_PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
