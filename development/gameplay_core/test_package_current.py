"""ZIP bytes must retain the frozen Linux host metadata on Windows CI."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import package_current as pack


class PackageDeterminismTests(unittest.TestCase):
    def test_implicit_windows_host_cannot_change_frozen_zip_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'fixture.txt'
            source.write_bytes(b'canonical review fixture\n')
            def archive():
                output = io.BytesIO()
                with zipfile.ZipFile(output, 'w') as handle:
                    pack.add_file(handle, source, 'behavior_pack/fixture.txt')
                return output.getvalue()
            linux = archive()
            original = zipfile.ZipInfo
            class WindowsDefault(original):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.create_system = 0
            with patch.object(pack.zipfile, 'ZipInfo', WindowsDefault):
                windows = archive()
            self.assertEqual(windows, linux)
            with zipfile.ZipFile(io.BytesIO(windows)) as handle:
                entry = handle.infolist()[0]
                self.assertEqual(entry.create_system, 3)
                self.assertEqual(entry.external_attr, 0o100644 << 16)
                self.assertEqual(entry.date_time, pack.ZIP_TIME)
                self.assertEqual(handle.read(entry), source.read_bytes())

    @unittest.skipUnless(json.loads((pack.BP / "manifest.json").read_text())["header"]["version"] == [2, 8, 66], "Frozen hash regression only applies to G66")
    def test_frozen_archives_regenerate_exactly_without_mutating_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            pairs = (
                ('mcaddon', [('behavior_pack', pack.BP), ('resource_pack', pack.RP)], False),
                ('brproject', [('', pack.PROJECT)], True),
            )
            expected = {
                'mcaddon': '95030437902beccc885d922f14069b19126337ddb80c98c0f743f087c1353b41',
                'brproject': 'b005188194dba24e3ebe0a5fbdd5a2fc9641ea41ffb817d9d6f25b217bf9a01f',
            }
            for suffix, roots, excluded in pairs:
                path = output / ('G66.' + suffix)
                pack.make_zip(path, roots, exclude_project_builds=excluded)
                self.assertEqual(pack.sha256(path), expected[suffix])


if __name__ == '__main__':
    unittest.main()
