import contextlib
import io
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import asset_quality_audit as audit


class AssetQualityAuditTests(unittest.TestCase):
    def run_audit(self, root):
        output = io.StringIO()
        with patch.object(audit, 'ROOT', root), patch.object(audit, 'PRODUCTION', root), \
                patch('sys.argv', ['audit', '--strict']), \
                patch.dict('os.environ', {'GITHUB_STEP_SUMMARY': ''}), \
                contextlib.redirect_stdout(output):
            result = audit.main()
        return result, output.getvalue()

    def test_large_texture_keeps_exact_byte_accounting_without_full_read(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / 'large.png'
            with path.open('wb') as source:
                source.write(b'\x89PNG\r\n\x1a\n' + struct.pack('>I', 13) + b'IHDR' + struct.pack('>II', 2048, 1024))
                source.truncate(64 * 1024 * 1024)
            original_open = Path.open

            class BoundedReader:
                def __enter__(self):
                    self.source = original_open(path, 'rb')
                    return self
                def __exit__(self, *args):
                    self.source.close()
                def read(self, size=-1):
                    self.assert_bounded(size)
                    return self.source.read(size)
                def assert_bounded(self, size):
                    if not 0 <= size <= 24:
                        raise AssertionError('Texture audit attempted an unbounded read')
                def fileno(self):
                    return self.source.fileno()

            with patch.object(Path, 'open', lambda item, *a, **kw: BoundedReader() if item == path else original_open(item, *a, **kw)):
                result, report = self.run_audit(root)
            self.assertEqual(result, 0)
            self.assertIn('67,108,864', report)
            self.assertIn('2048x1024=1', report)

    def test_truncated_texture_still_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'bad.png').write_bytes(b'\x89PNG')
            self.assertEqual(self.run_audit(root)[0], 1)

    def test_obj_streaming_preserves_invalid_face_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            obj = root / 'mesh.obj'
            obj.write_text('v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n')
            with patch.object(Path, 'read_text', side_effect=AssertionError('OBJ must be streamed')):
                self.assertEqual(self.run_audit(root)[0], 0)
            obj.write_text('v 0 0 0\nf 1 2 3\n')
            self.assertEqual(self.run_audit(root)[0], 1)


if __name__ == '__main__':
    unittest.main()
