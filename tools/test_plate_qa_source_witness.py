"""The opt-in diagnostic delta does not weaken earlier source conservation."""
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch
import public_source_witness as public

class PlateQaSourceWitnessTests(unittest.TestCase):
    def test_exact_diagnostic_delta_has_g81_preimage_and_g83_result(self):
        delta=public._main_delta('g83-main-reviewed-delta.json')
        before=public.expected_main_bytes((2,8,81))
        after=public.expected_main_bytes((2,8,83))
        self.assertEqual(hashlib.sha256(before).hexdigest(),delta['before_sha256'])
        self.assertEqual(hashlib.sha256(after).hexdigest(),delta['after_sha256'])
        current=json.loads((public.ROOT/'baseline.json').read_text())['version']
        self.assertEqual(public.expected_main_bytes(current),(public.ROOT/public.MAIN_PATH).read_bytes())
        self.assertNotEqual(before,after)
        self.assertIn(b"import {plateQaTrace} from './plate_qa_runtime.js';",after)

    def test_unrelated_source_bytes_and_removed_diagnostics_remain_rejected(self):
        path=public.ROOT/public.MAIN_PATH
        source=path.read_bytes()
        for changed in (source+b'\n',source.replace(b'MINIMUM_EAT_TICKS=25',b'MINIMUM_EAT_TICKS=1'),source.replace(b"import {plateQaTrace} from './plate_qa_runtime.js';\n",b'')):
            with patch.object(Path,'read_bytes',return_value=changed):
                self.assertNotEqual(path.read_bytes(),public.expected_main_bytes((2,8,83)))

    def test_native_stop_and_historical_g80_identities_are_unchanged(self):
        self.assertEqual(public.expected_main_bytes((2,8,80),proposal='checkpoint_stop'),public.expected_main_bytes((2,8,81)))
        self.assertEqual(public.expected_main_bytes((2,8,80),proposal='jar_projection'),public.expected_main_bytes((2,8,79)))

if __name__=='__main__':unittest.main()
