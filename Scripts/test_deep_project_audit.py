import json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class DeepProjectAuditTests(unittest.TestCase):
 def test_static_audit(self):
  r=subprocess.run([sys.executable,str(ROOT/"Scripts"/"deep_project_audit.py")],cwd=ROOT,text=True,capture_output=True)
  self.assertEqual(r.returncode,0,r.stdout+"\n"+r.stderr)
  self.assertIn("DEEP PROJECT AUDIT PASSED",r.stdout)
 def test_unique_findings(self):
  d=json.loads((ROOT/"Data"/"DeepProjectAudit.json").read_text(encoding="utf-8"))
  ids=[x["id"] for x in d["findings"]]
  self.assertEqual(len(ids),len(set(ids)))
if __name__=="__main__": unittest.main()
