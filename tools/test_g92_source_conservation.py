"""Exact G92 probe admission and negative checks for every conserved boundary."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import g92_source_conservation as witness
import g93_source_conservation as current


class HeldClientProbeConservation(unittest.TestCase):
    def patch_metadata(self, data):
        original = Path.read_text
        return patch.object(Path, 'read_text', lambda path, *args, **kwargs:
            json.dumps(data) if path.name == 'g92-runtime-reviewed-delta.json'
            else original(path, *args, **kwargs))

    def test_frozen_g91_and_all_current_runtime_bytes_are_conserved(self):
        frozen = witness.previous.verify_snapshot(witness.FROZEN_SOURCE_BASE)
        self.assertEqual(frozen['runtime_files'], 4155)
        self.assertEqual(frozen['reviewed_release'], [2, 8, 91])
        self.assertEqual(frozen['reviewed_paths'], 5)
        frozen_g92 = witness.verify_snapshot(current.FROZEN_SOURCE_BASE)
        self.assertEqual(frozen_g92['runtime_files'], 4156)
        self.assertEqual(frozen_g92['reviewed_release'], [2, 8, 92])
        self.assertEqual(frozen_g92['reviewed_paths'], 6)
        latest = witness.verify_current()
        self.assertEqual(latest['runtime_files'], 4157)
        self.assertEqual(latest['reviewed_release'], [2, 8, 94])
        self.assertEqual(latest['reviewed_paths'], 5)
        self.assertEqual(set(witness.metadata()['files']), witness.DELTA_PATHS)
        self.assertEqual(witness.ADDED_PATHS, {witness.QA_GEOMETRY_PATH})

    def test_frozen_g91_validation_precedes_current_admission(self):
        with patch.object(witness.previous, 'verify_snapshot', side_effect=AssertionError('Frozen G91 source drift')) as frozen:
            with patch.object(witness, 'metadata') as metadata:
                with self.assertRaisesRegex(AssertionError, 'Frozen G91 source drift'):
                    witness.verify_current()
                frozen.assert_called_once_with(witness.FROZEN_SOURCE_BASE)
                metadata.assert_not_called()

    def test_historical_current_delegation_preserves_independent_frozen_g91_bytes(self):
        self.assertNotEqual(witness.previous.expected_frozen_runtime_bytes(witness.WRITER_PATH),
                            witness.expected_runtime_bytes(witness.WRITER_PATH))
        self.assertEqual(witness.previous.expected_frozen_runtime_bytes(witness.WRITER_PATH),
                         witness.source(witness.WRITER_PATH))
        for historical in (witness.previous, witness.previous.previous):
            with patch.object(witness, 'verify_current', return_value={'g92': True}) as current:
                self.assertEqual(historical.verify_current(), {'g92': True})
                current.assert_called_once_with()
            for path in witness.DELTA_PATHS:
                self.assertEqual(historical.expected_runtime_bytes(path), witness.expected_runtime_bytes(path))

    def test_exact_reviewed_probe_and_all_31_production_controllers_are_preserved(self):
        for path, identity in witness.REVIEWED_AFTER.items():
            after = witness.apply_delta(path)
            self.assertEqual(witness.sha(after), identity)
            self.assertEqual(current.source(path), after)
        for relative in ('resource_pack/models/entity/plate_held.geo.json',
                         'resource_pack/animations/plate_held.animation.json',
                         'behavior_pack/entities/player.json',
                         'resource_pack/particles/feedback_cloud.json'):
            path = witness.PROJECT + relative
            self.assertEqual((witness.ROOT / path).read_bytes(), witness.source(path))
        old = json.loads(witness.source(witness.CONTROLLERS_PATH))['render_controllers']
        new = json.loads(current.source(witness.CONTROLLERS_PATH))['render_controllers']
        self.assertEqual(len(old), 31)
        self.assertEqual(list(new), list(old) + list(witness.QA_CONTROLLERS))
        for name, controller in old.items():
            self.assertEqual(new[name], controller)
        before = witness.source(witness.ATTACHABLE_PATH)
        after = current.source(witness.ATTACHABLE_PATH)
        witness.assert_held_preservation(witness.ATTACHABLE_PATH, before, after)

    def test_all_six_delta_paths_and_unchanged_runtime_mutations_are_rejected(self):
        original = Path.read_bytes
        paths = sorted(witness.DELTA_PATHS) + [witness.PROJECT + relative for relative in (
            'behavior_pack/scripts/main.js', 'behavior_pack/entities/player.json',
            'behavior_pack/scripts/secret_held_runtime.js',
            'resource_pack/models/entity/plate_held.geo.json',
            'resource_pack/animations/plate_held.animation.json',
            'resource_pack/particles/feedback_cloud.json')]
        for target in paths:
            with self.subTest(target=target):
                with patch.object(Path, 'read_bytes', lambda path:
                    original(path) + b'\n' if path == witness.ROOT / target else original(path)):
                    with self.assertRaisesRegex(AssertionError, 'Runtime source drift'):
                        witness.verify_current()

    def test_missing_existing_new_or_extra_runtime_files_fail_closed(self):
        original_glob, original_is_file = Path.rglob, Path.is_file
        pack = witness.ROOT / witness.PROJECT / 'resource_pack'
        extra = pack / 'models/entity/unreviewed_probe.geo.json'
        missing = [witness.ROOT / witness.QA_GEOMETRY_PATH,
                   pack / 'models/entity/plate_held.geo.json']
        for target in missing + [extra]:
            def glob(path, pattern):
                rows = list(original_glob(path, pattern))
                if path == pack:
                    rows = rows + [extra] if target == extra else [row for row in rows if row != target]
                return iter(rows)
            with patch.object(Path, 'rglob', glob), patch.object(Path, 'is_file',
                lambda path: True if path == extra else original_is_file(path)):
                with self.assertRaisesRegex(AssertionError, 'Missing/extra G(?:92|93|94) runtime file'):
                    witness.verify_current()

    def test_metadata_rejects_wrong_base_tree_patch_hash_scope_or_probe_bytes(self):
        metadata = witness.metadata()
        variants = []
        for key in ('base_commit', 'base_tree'):
            changed = copy.deepcopy(metadata)
            changed[key] = '0' * 40
            variants.append(changed)
        changed = copy.deepcopy(metadata)
        changed['held_review']['patch_sha256'] = '0' * 64
        variants.append(changed)
        changed = copy.deepcopy(metadata)
        changed['held_review']['after_sha256'][witness.WRITER_PATH] = '0' * 64
        variants.append(changed)
        for path in witness.REVIEWED_AFTER:
            changed = copy.deepcopy(metadata)
            changed['files'][path]['after_sha256'] = '0' * 64
            variants.append(changed)
        changed = copy.deepcopy(metadata)
        changed['files'][witness.PROJECT + 'behavior_pack/scripts/main.js'] = copy.deepcopy(changed['files'][witness.WRITER_PATH])
        variants.append(changed)
        changed = copy.deepcopy(metadata)
        changed['files'].pop(witness.QA_GEOMETRY_PATH)
        variants.append(changed)
        for changed in variants:
            with self.patch_metadata(changed):
                with self.assertRaises(AssertionError):
                    witness.apply_delta(witness.WRITER_PATH)

    def test_reviewed_operations_reject_wrong_preimage_overlap_and_result(self):
        metadata = witness.metadata()
        path = witness.WRITER_PATH
        variants = []
        changed = copy.deepcopy(metadata)
        changed['files'][path]['before_sha256'] = '0' * 64
        variants.append(changed)
        changed = copy.deepcopy(metadata)
        changed['files'][path]['operations'].append(dict(changed['files'][path]['operations'][0]))
        variants.append(changed)
        for field in ('before', 'after'):
            changed = copy.deepcopy(metadata)
            changed['files'][path]['operations'][0][field] += 'x'
            variants.append(changed)
        for changed in variants:
            with self.patch_metadata(changed):
                with self.assertRaises(AssertionError):
                    witness.apply_delta(path)

    def test_manifest_delta_rejects_nonversion_fields_even_with_recomputed_hash(self):
        for path in witness.MANIFESTS:
            metadata = copy.deepcopy(witness.metadata())
            before = witness.source(path)
            after = json.loads(witness.apply_delta(path))
            after['header']['uuid'] = '00000000-0000-0000-0000-000000000000'
            text = json.dumps(after, ensure_ascii=False, indent=2) + '\n'
            metadata['files'][path]['operations'] = [{'start': 0, 'end': len(before.decode()),
                'before': before.decode(), 'after': text}]
            metadata['files'][path]['after_sha256'] = witness.sha(text.encode())
            with self.patch_metadata(metadata):
                with self.assertRaisesRegex(AssertionError, 'paired G92 identity'):
                    witness.apply_delta(path)

    def test_direct_preservation_checks_reject_decoder_order_and_controller_drift(self):
        before = witness.source(witness.ATTACHABLE_PATH)
        after = json.loads(witness.apply_delta(witness.ATTACHABLE_PATH))
        script = after['minecraft:attachable']['description']['scripts']['pre_animation']
        production = [index for index, row in enumerate(script) if not row.startswith('v.kg_plate_qa_')]
        a, b = production[:2]
        script[a], script[b] = script[b], script[a]
        with self.assertRaisesRegex(AssertionError, 'Production decoder ordering changed'):
            witness.assert_held_preservation(witness.ATTACHABLE_PATH, before, json.dumps(after).encode())
        before = witness.source(witness.CONTROLLERS_PATH)
        after = json.loads(witness.apply_delta(witness.CONTROLLERS_PATH))
        controller = next(iter(after['render_controllers']))
        after['render_controllers'][controller]['geometry'] = 'Geometry.qa_probe'
        with self.assertRaisesRegex(AssertionError, 'Production controller changed'):
            witness.assert_held_preservation(witness.CONTROLLERS_PATH, before, json.dumps(after).encode())

    def test_frozen_g91_tree_blob_and_history_mutations_fail_closed(self):
        original_files = witness.previous.previous.files
        rows = dict(original_files(witness.FROZEN_SOURCE_BASE))
        rows[witness.WRITER_PATH] = '0' * 40
        with patch.object(witness.previous.previous, 'files', lambda ref, *args:
            rows if ref == witness.FROZEN_SOURCE_BASE else original_files(ref, *args)):
            with self.assertRaisesRegex(AssertionError, 'Frozen G91 source drift'):
                witness.previous.verify_snapshot(witness.FROZEN_SOURCE_BASE)
        original = Path.read_text
        history = json.loads((witness.ROOT / 'release-history.json').read_text())
        history['2.8.91']['BP']['sha256'] = '0' * 64
        with patch.object(Path, 'read_text', lambda path, *args, **kwargs:
            json.dumps(history) if path == witness.ROOT / 'release-history.json'
            else original(path, *args, **kwargs)):
            with self.assertRaisesRegex(AssertionError, 'G(?:91|92|93) history drift'):
                witness.verify_current()


if __name__ == '__main__':
    unittest.main()
