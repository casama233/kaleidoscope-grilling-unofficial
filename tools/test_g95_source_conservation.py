"""Independent diagnostic G94 foundation and fail-closed G95 admission."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import g95_source_conservation as witness


class FrozenG94Foundation(unittest.TestCase):
    def test_exact_diagnostic_commit_tree_and_all_predecessor_snapshots(self):
        result = witness.verify_frozen_foundation()
        self.assertEqual(result['runtime_files'], 4157)
        self.assertEqual(result['reviewed_release'], [2, 8, 94])
        self.assertEqual(result['reviewed_paths'], 5)
        self.assertEqual(result['sources'], 3)
        self.assertEqual(result['collision_labels'], 2)
        self.assertEqual(witness.FROZEN_SOURCE_BASE, '4014645d132ec676791b2aa39752db37d84abb2e')
        self.assertEqual(witness.FROZEN_TREE, 'd641b145893e802265751229df9f415a3a6e2d27')
        for release in (92, 93, 94):
            path = f'tools/fixtures/g{release}-runtime-reviewed-delta.json'
            self.assertEqual((witness.ROOT / path).read_bytes(), witness.source(path))

    def test_frozen_g94_never_uses_current_g94_or_g95_expectations(self):
        previous = witness.previous
        with patch.object(previous, 'expected_runtime_bytes', side_effect=AssertionError('Current G94 expectation used')):
            with patch.object(witness, 'expected_runtime_bytes', side_effect=AssertionError('Future G95 expectation used')):
                result = previous.verify_snapshot(witness.FROZEN_SOURCE_BASE)
        self.assertEqual(result['reviewed_release'], [2, 8, 94])
        for path in previous.DELTA_PATHS:
            self.assertEqual(previous.expected_frozen_runtime_bytes(path), witness.source(path))

    def test_predecessor_failure_blocks_g94_and_g95_metadata(self):
        previous = witness.previous
        with patch.object(previous.previous, 'verify_snapshot', side_effect=AssertionError('Frozen G93 source drift')) as frozen:
            with patch.object(previous, 'metadata') as old_metadata, patch.object(witness, 'metadata') as new_metadata:
                with self.assertRaisesRegex(AssertionError, 'Frozen G93 source drift'):
                    witness.verify_current()
                frozen.assert_called_once_with(previous.FROZEN_SOURCE_BASE)
                old_metadata.assert_not_called()
                new_metadata.assert_not_called()

    def test_frozen_g94_blob_and_missing_or_extra_path_mutations_fail_closed(self):
        original = witness.HISTORICAL.files
        for fault in ('blob', 'missing', 'extra'):
            frozen = dict(original(witness.FROZEN_SOURCE_BASE))
            target = witness.previous.ATTACHABLE_PATH
            if fault == 'blob': frozen[target] = '0' * 40
            elif fault == 'missing': frozen.pop(target)
            else: frozen[witness.PROJECT + 'resource_pack/models/entity/unreviewed.geo.json'] = '0' * 40
            with self.subTest(fault=fault), patch.object(witness.HISTORICAL, 'files', lambda ref, *args:
                frozen if ref == witness.FROZEN_SOURCE_BASE else original(ref, *args)):
                with self.assertRaisesRegex(AssertionError, 'Frozen G94 (?:source drift|missing/extra runtime file)'):
                    witness.verify_frozen_foundation()

    def test_g94_fixture_and_history_mutations_fail_closed(self):
        original_bytes = Path.read_bytes
        for release in (92, 93, 94):
            target = witness.ROOT / f'tools/fixtures/g{release}-runtime-reviewed-delta.json'
            with patch.object(Path, 'read_bytes', lambda path:
                original_bytes(path) + b'\n' if path == target else original_bytes(path)):
                with self.assertRaisesRegex(AssertionError, 'Frozen reviewed fixture drift'):
                    witness.verify_frozen_foundation()
        original_source = witness.HISTORICAL.source
        history = json.loads(witness.source('release-history.json'))
        history['2.8.93']['BP']['sha256'] = '0' * 64
        with patch.object(witness.HISTORICAL, 'source', lambda ref, path:
            json.dumps(history).encode() if ref == witness.FROZEN_SOURCE_BASE and path == 'release-history.json'
            else original_source(ref, path)):
            with self.assertRaisesRegex(AssertionError, 'Frozen G93 history drift'):
                witness.verify_frozen_foundation()

    def test_diagnostic_g94_tree_drift_fails_before_snapshot_or_metadata(self):
        original = witness.HISTORICAL.git
        target = witness.FROZEN_SOURCE_BASE + '^{tree}'
        with patch.object(witness.HISTORICAL, 'git', lambda *args:
            b'0' * 40 if args == ('rev-parse', target) else original(*args)):
            with patch.object(witness.previous, 'verify_snapshot') as frozen, patch.object(witness, 'metadata') as metadata:
                with self.assertRaisesRegex(AssertionError, 'Diagnostic G94 tree drift'):
                    witness.verify_current()
                frozen.assert_not_called()
                metadata.assert_not_called()


class QARenderSourceAdmission(unittest.TestCase):
    def patch_metadata(self, data):
        original = Path.read_text
        return patch.object(Path, 'read_text', lambda path, *args, **kwargs:
            json.dumps(data) if path.name == 'g95-runtime-reviewed-delta.json'
            else original(path, *args, **kwargs))

    def test_exact_three_paths_no_additions_and_all_current_bytes(self):
        result = witness.verify_current()
        self.assertEqual(result, {'runtime_files': 4157, 'sources': 3, 'collision_labels': 2,
            'reviewed_release': [2, 8, 95], 'reviewed_paths': 3})
        self.assertEqual(witness.DELTA_PATHS, witness.MANIFESTS | {witness.QA_GEOMETRY_PATH})
        self.assertEqual(witness.ADDED_PATHS, set())
        self.assertEqual(set(witness.metadata()['files']), witness.DELTA_PATHS)
        for path in witness.DELTA_PATHS:
            self.assertEqual(witness.apply_delta(path), (witness.ROOT / path).read_bytes())
        for path, identity in witness.REVIEWED_SOURCE_AFTER.items():
            self.assertEqual(witness.sha((witness.ROOT / path).read_bytes()), identity)

    def test_all_historical_current_entrypoints_delegate_but_g94_frozen_bytes_stay_exact(self):
        previous = witness.previous
        self.assertEqual(previous.expected_frozen_runtime_bytes(witness.QA_GEOMETRY_PATH), witness.source(witness.QA_GEOMETRY_PATH))
        self.assertNotEqual(previous.expected_frozen_runtime_bytes(witness.QA_GEOMETRY_PATH), witness.expected_runtime_bytes(witness.QA_GEOMETRY_PATH))
        while previous is not None:
            with patch.object(witness, 'verify_current', return_value={'g95': True}) as current:
                self.assertEqual(previous.verify_current(), {'g95': True})
                current.assert_called_once_with()
            for path in witness.DELTA_PATHS:
                self.assertEqual(previous.expected_runtime_bytes(path), witness.expected_runtime_bytes(path))
            previous = getattr(previous, 'previous', None)

    def test_production_arithmetic_schema_storage_frames_controllers_and_texture_are_exact(self):
        for relative in ('behavior_pack/scripts/main.js', 'behavior_pack/scripts/bottle_held_visual_runtime.js',
                'behavior_pack/scripts/plate_visual_core.js', 'behavior_pack/entities/player.json',
                'resource_pack/attachables/skewer_plate.attachable.json',
                'resource_pack/render_controllers/plate_held.render_controllers.json',
                'resource_pack/models/entity/plate_held.geo.json', 'resource_pack/models/entity/plate_held_qa.geo.json',
                'resource_pack/animations/plate_held.animation.json', 'resource_pack/textures/held/bottle_shell_palette.png'):
            path = witness.PROJECT + relative
            self.assertNotIn(path, witness.DELTA_PATHS)
            self.assertEqual((witness.ROOT / path).read_bytes(), witness.source(path), path)

    def test_reviewed_runtime_and_unchanged_production_mutations_fail_closed(self):
        original = Path.read_bytes
        paths = sorted(witness.DELTA_PATHS) + [witness.PROJECT + relative for relative in (
            'behavior_pack/scripts/bottle_held_visual_runtime.js', 'behavior_pack/entities/player.json',
            'resource_pack/attachables/skewer_plate.attachable.json',
            'resource_pack/render_controllers/plate_held.render_controllers.json',
            'resource_pack/animations/plate_held.animation.json')]
        for target in paths:
            with self.subTest(target=target), patch.object(Path, 'read_bytes', lambda path:
                original(path) + b'\n' if path == witness.ROOT / target else original(path)):
                with self.assertRaisesRegex(AssertionError, 'Runtime source drift'):
                    witness.verify_current()
        for target in witness.REVIEWED_SOURCE_AFTER:
            with patch.object(Path, 'read_bytes', lambda path:
                original(path) + b'\n' if path == witness.ROOT / target else original(path)):
                with self.assertRaisesRegex(AssertionError, 'Reviewed QA-render source drift'):
                    witness.metadata()

    def test_missing_existing_geometry_or_extra_runtime_file_fails_closed(self):
        original_glob, original_is_file = Path.rglob, Path.is_file
        pack = witness.ROOT / witness.PROJECT / 'resource_pack'
        extra = pack / 'models/entity/unreviewed_probe.geo.json'
        for target in (witness.ROOT / witness.QA_GEOMETRY_PATH, extra):
            def glob(path, pattern):
                rows = list(original_glob(path, pattern))
                if path == pack:
                    rows = rows + [extra] if target == extra else [row for row in rows if row != target]
                return iter(rows)
            with patch.object(Path, 'rglob', glob), patch.object(Path, 'is_file',
                lambda path: True if path == extra else original_is_file(path)):
                with self.assertRaisesRegex(AssertionError, 'Missing/extra G95 runtime file'):
                    witness.verify_current()

    def test_metadata_rejects_wrong_lineage_patch_hash_scope_and_source_postimages(self):
        metadata = witness.metadata(); variants = []
        for key in ('base_commit', 'base_tree'):
            changed = copy.deepcopy(metadata); changed[key] = '0' * 40; variants.append(changed)
        changed = copy.deepcopy(metadata); changed['held_review']['patch_sha256'] = '0' * 64; variants.append(changed)
        for path in witness.REVIEWED_SOURCE_AFTER:
            changed = copy.deepcopy(metadata); changed['held_review']['source_after_sha256'][path] = '0' * 64; variants.append(changed)
        changed = copy.deepcopy(metadata); changed['files'][witness.QA_GEOMETRY_PATH]['after_sha256'] = '0' * 64; variants.append(changed)
        changed = copy.deepcopy(metadata); changed['files'][witness.PROJECT + 'behavior_pack/scripts/main.js'] = copy.deepcopy(changed['files'][witness.QA_GEOMETRY_PATH]); variants.append(changed)
        changed = copy.deepcopy(metadata); changed['files'].pop(witness.QA_GEOMETRY_PATH); variants.append(changed)
        for changed in variants:
            with self.patch_metadata(changed), self.assertRaises(AssertionError):
                witness.apply_delta(witness.QA_GEOMETRY_PATH)
        with patch.object(witness, 'REVIEWED_PATCH_SHA256', None), self.assertRaisesRegex(AssertionError, 'not yet admitted'):
            witness.metadata()

    def test_changed_preimage_overlap_and_result_fail_even_after_current_expectation(self):
        path = witness.QA_GEOMETRY_PATH
        witness.expected_runtime_bytes(path)
        metadata = witness.metadata(); variants = []
        changed = copy.deepcopy(metadata); changed['files'][path]['before_sha256'] = '0' * 64; variants.append(changed)
        changed = copy.deepcopy(metadata); changed['files'][path]['operations'].append(dict(changed['files'][path]['operations'][0])); variants.append(changed)
        for field in ('before', 'after'):
            changed = copy.deepcopy(metadata); changed['files'][path]['operations'][0][field] += 'x'; variants.append(changed)
        for changed in variants:
            with self.patch_metadata(changed), self.assertRaises(AssertionError):
                witness.expected_runtime_bytes(path)

    def test_only_paired_manifest_version_bump_is_allowed(self):
        for path in witness.MANIFESTS:
            changed = copy.deepcopy(witness.metadata()); before = witness.source(path)
            after = json.loads(witness.apply_delta(path)); after['header']['uuid'] = '00000000-0000-0000-0000-000000000000'
            text = json.dumps(after, ensure_ascii=False, indent=2) + '\n'
            changed['files'][path]['operations'] = [{'start': 0, 'end': len(before.decode()), 'before': before.decode(), 'after': text}]
            changed['files'][path]['after_sha256'] = witness.sha(text.encode())
            with self.patch_metadata(changed), self.assertRaisesRegex(AssertionError, 'paired G95 identity'):
                witness.apply_delta(path)

    def test_semantic_guard_rejects_rig_bones_bounds_uv_and_text_planes(self):
        path = witness.QA_GEOMETRY_PATH; before = witness.source(path)
        original = json.loads(witness.apply_delta(path))
        for fault in ('rig', 'bone', 'bounds', 'sampling', 'plane', 'mirror'):
            after = copy.deepcopy(original); geometry = after['minecraft:geometry'][0]
            if fault == 'rig': geometry['bones'][0]['pivot'][0] = 1
            elif fault == 'bone': geometry['bones'][-1]['name'] = 'unreviewed_bone'
            elif fault == 'bounds': geometry['description']['visible_bounds_width'] = 99
            elif fault == 'sampling': geometry['bones'][3]['cubes'][0]['uv']['north']['uv'] = [0, 32]
            elif fault == 'plane': geometry['bones'][3]['cubes'][0]['origin'][2] = -10.17
            else: geometry['bones'][3]['cubes'][-1]['origin'][0] += 1
            with self.subTest(fault=fault), self.assertRaises(AssertionError):
                witness.assert_held_preservation(path, before, json.dumps(after).encode())

    def test_every_frozen_g94_history_row_remains_exact(self):
        original = Path.read_text
        history = json.loads((witness.ROOT / 'release-history.json').read_text())
        history['2.8.94']['BP']['sha256'] = '0' * 64
        with patch.object(Path, 'read_text', lambda path, *args, **kwargs:
            json.dumps(history) if path == witness.ROOT / 'release-history.json' else original(path, *args, **kwargs)):
            with self.assertRaisesRegex(AssertionError, 'Diagnostic G94 history drift'):
                witness.verify_current()


if __name__ == '__main__': unittest.main()
