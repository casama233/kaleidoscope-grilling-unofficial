"""Independent diagnostic G95 foundation and exact count-only G96 admission."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import g96_source_conservation as witness


class FrozenG95Foundation(unittest.TestCase):
    def test_exact_public_g95_commit_tree_and_all_predecessor_snapshots(self):
        result = witness.verify_frozen_foundation()
        self.assertEqual(result, {'runtime_files': 4157, 'sources': 3, 'collision_labels': 2,
            'reviewed_release': [2, 8, 95], 'reviewed_paths': 3})
        self.assertEqual(witness.FROZEN_SOURCE_BASE, 'ca6a2d0777066b4bcdce278d1d0f501a39fbc2c5')
        self.assertEqual(witness.FROZEN_TREE, '25e5d0aee047092302f9973c5420bd789a090c3d')
        for path in witness.FROZEN_FIXTURES:
            self.assertEqual((witness.ROOT / path).read_bytes(), witness.source(path))

    def test_frozen_g95_never_uses_current_expectations_or_current_generator_bytes(self):
        previous = witness.previous
        original = Path.read_bytes
        with patch.object(previous, 'expected_runtime_bytes', side_effect=AssertionError('Current G95 expectation used')):
            with patch.object(witness, 'expected_runtime_bytes', side_effect=AssertionError('Future G96 expectation used')):
                with patch.object(Path, 'read_bytes', lambda path: b'future source drift' if
                    path.relative_to(witness.ROOT).as_posix() in previous.REVIEWED_SOURCE_AFTER else original(path)):
                    result = previous.verify_snapshot(witness.FROZEN_SOURCE_BASE)
        self.assertEqual(result['reviewed_release'], [2, 8, 95])
        for path in previous.DELTA_PATHS:
            self.assertEqual(previous.expected_frozen_runtime_bytes(path), witness.source(path))

    def test_predecessor_failure_blocks_g95_and_g96_metadata(self):
        previous = witness.previous
        with patch.object(previous.previous, 'verify_snapshot', side_effect=AssertionError('Frozen G94 source drift')) as frozen:
            with patch.object(previous, 'metadata') as old_metadata, patch.object(witness, 'metadata') as new_metadata:
                with self.assertRaisesRegex(AssertionError, 'Frozen G94 source drift'):
                    witness.verify_current()
                frozen.assert_called_once_with(previous.FROZEN_SOURCE_BASE)
                old_metadata.assert_not_called()
                new_metadata.assert_not_called()

    def test_frozen_g95_blob_missing_and_extra_paths_fail_closed(self):
        original = witness.HISTORICAL.files
        for fault in ('blob', 'missing', 'extra'):
            frozen = dict(original(witness.FROZEN_SOURCE_BASE))
            target = witness.ATTACHABLE_PATH
            if fault == 'blob': frozen[target] = '0' * 40
            elif fault == 'missing': frozen.pop(target)
            else: frozen[witness.PROJECT + 'resource_pack/models/entity/unreviewed.geo.json'] = '0' * 40
            with self.subTest(fault=fault), patch.object(witness.HISTORICAL, 'files', lambda ref, *args:
                frozen if ref == witness.FROZEN_SOURCE_BASE else original(ref, *args)):
                with self.assertRaisesRegex(AssertionError, 'Frozen G95 (?:source drift|missing/extra runtime file)'):
                    witness.verify_frozen_foundation()

    def test_every_frozen_fixture_and_g95_snapshot_history_are_exact(self):
        original_bytes = Path.read_bytes
        for path in witness.FROZEN_FIXTURES:
            target = witness.ROOT / path
            with self.subTest(path=path), patch.object(Path, 'read_bytes', lambda path:
                original_bytes(path) + b'\n' if path == target else original_bytes(path)):
                with self.assertRaisesRegex(AssertionError, 'Frozen reviewed fixture drift'):
                    witness.verify_frozen_foundation()
        original_source = witness.HISTORICAL.source
        history = json.loads(witness.source('release-history.json'))
        history['2.8.94']['BP']['sha256'] = '0' * 64
        with patch.object(witness.HISTORICAL, 'source', lambda ref, path:
            json.dumps(history).encode() if ref == witness.FROZEN_SOURCE_BASE and path == 'release-history.json'
            else original_source(ref, path)):
            with self.assertRaisesRegex(AssertionError, 'Frozen diagnostic G94 history drift'):
                witness.verify_frozen_foundation()

    def test_diagnostic_g95_tree_drift_fails_before_snapshot_and_metadata(self):
        original = witness.HISTORICAL.git
        target = witness.FROZEN_SOURCE_BASE + '^{tree}'
        with patch.object(witness.HISTORICAL, 'git', lambda *args:
            b'0' * 40 if args == ('rev-parse', target) else original(*args)):
            with patch.object(witness.previous, 'verify_snapshot') as frozen, patch.object(witness, 'metadata') as metadata:
                with self.assertRaisesRegex(AssertionError, 'Diagnostic G95 tree drift'):
                    witness.verify_current()
                frozen.assert_not_called()
                metadata.assert_not_called()


class CountMidpointSourceAdmission(unittest.TestCase):
    def patch_metadata(self, data):
        original = Path.read_text
        return patch.object(Path, 'read_text', lambda path, *args, **kwargs:
            json.dumps(data) if path.name == 'g96-runtime-reviewed-delta.json'
            else original(path, *args, **kwargs))

    def test_exact_three_paths_no_additions_and_all_current_bytes(self):
        result = witness.verify_current()
        self.assertEqual(result, {'runtime_files': 4157, 'sources': 3, 'collision_labels': 2,
            'reviewed_release': [2, 8, 96], 'reviewed_paths': 3})
        self.assertEqual(witness.DELTA_PATHS, witness.MANIFESTS | {witness.ATTACHABLE_PATH})
        self.assertEqual(witness.ADDED_PATHS, set())
        self.assertEqual(set(witness.metadata()['files']), witness.DELTA_PATHS)
        for path in witness.DELTA_PATHS:
            self.assertEqual(witness.apply_delta(path), (witness.ROOT / path).read_bytes())
        for path, identity in witness.REVIEWED_SOURCE_AFTER.items():
            self.assertEqual(witness.sha((witness.ROOT / path).read_bytes()), identity)

    def test_all_historical_entrypoints_delegate_and_g95_frozen_bytes_stay_exact(self):
        previous = witness.previous
        self.assertEqual(previous.expected_frozen_runtime_bytes(witness.ATTACHABLE_PATH), witness.source(witness.ATTACHABLE_PATH))
        self.assertNotEqual(previous.expected_frozen_runtime_bytes(witness.ATTACHABLE_PATH), witness.expected_runtime_bytes(witness.ATTACHABLE_PATH))
        while previous is not None:
            with patch.object(witness, 'verify_current', return_value={'g96': True}) as current:
                self.assertEqual(previous.verify_current(), {'g96': True})
                current.assert_called_once_with()
            for path in witness.DELTA_PATHS:
                self.assertEqual(previous.expected_runtime_bytes(path), witness.expected_runtime_bytes(path))
            previous = getattr(previous, 'previous', None)

    def test_all_bp_schema_storage_guards_qa_board_and_production_frames_are_exact(self):
        bp = [path for path in witness.files() if '/behavior_pack/' in path and path not in witness.MANIFESTS]
        self.assertTrue(bp)
        for path in bp:
            self.assertEqual((witness.ROOT / path).read_bytes(), witness.source(path), path)
        for relative in ('resource_pack/render_controllers/plate_held.render_controllers.json',
                'resource_pack/models/entity/plate_held.geo.json', 'resource_pack/models/entity/plate_held_qa.geo.json',
                'resource_pack/models/entity/plate_held_binary_qa.geo.json', 'resource_pack/animations/plate_held.animation.json',
                'resource_pack/textures/held/bottle_shell_palette.png'):
            path = witness.PROJECT + relative
            self.assertNotIn(path, witness.DELTA_PATHS)
            self.assertEqual((witness.ROOT / path).read_bytes(), witness.source(path), path)
        witness.assert_held_preservation(witness.ATTACHABLE_PATH, witness.source(witness.ATTACHABLE_PATH),
                                        (witness.ROOT / witness.ATTACHABLE_PATH).read_bytes())

    def test_reviewed_runtime_unchanged_assets_and_generator_mutations_fail_closed(self):
        original = Path.read_bytes
        paths = sorted(witness.DELTA_PATHS) + [witness.PROJECT + relative for relative in (
            'behavior_pack/scripts/bottle_held_visual_runtime.js', 'behavior_pack/entities/player.json',
            'resource_pack/models/entity/plate_held_binary_qa.geo.json',
            'resource_pack/render_controllers/plate_held.render_controllers.json',
            'resource_pack/animations/plate_held.animation.json')]
        for target in paths:
            with self.subTest(target=target), patch.object(Path, 'read_bytes', lambda path:
                original(path) + b'\n' if path == witness.ROOT / target else original(path)):
                with self.assertRaisesRegex(AssertionError, 'Runtime source drift'):
                    witness.verify_current()
        for target in witness.REVIEWED_SOURCE_AFTER:
            with self.subTest(target=target), patch.object(Path, 'read_bytes', lambda path:
                original(path) + b'\n' if path == witness.ROOT / target else original(path)):
                with self.assertRaisesRegex(AssertionError, 'Reviewed count midpoint source drift'):
                    witness.metadata()

    def test_missing_existing_or_extra_runtime_file_fails_closed(self):
        original_glob, original_is_file = Path.rglob, Path.is_file
        pack = witness.ROOT / witness.PROJECT / 'resource_pack'
        extra = pack / 'models/entity/unreviewed_probe.geo.json'
        for target in (witness.ROOT / witness.ATTACHABLE_PATH, extra):
            def glob(path, pattern):
                rows = list(original_glob(path, pattern))
                if path == pack:
                    rows = rows + [extra] if target == extra else [row for row in rows if row != target]
                return iter(rows)
            with patch.object(Path, 'rglob', glob), patch.object(Path, 'is_file',
                lambda path: True if path == extra else original_is_file(path)):
                with self.assertRaisesRegex(AssertionError, 'Missing/extra G96 runtime file'):
                    witness.verify_current()

    def test_metadata_rejects_wrong_lineage_patch_scope_and_source_postimages(self):
        metadata = witness.metadata(); variants = []
        for key in ('base_commit', 'base_tree'):
            changed = copy.deepcopy(metadata); changed[key] = '0' * 40; variants.append(changed)
        changed = copy.deepcopy(metadata); changed['held_review']['patch_sha256'] = '0' * 64; variants.append(changed)
        for path in witness.REVIEWED_SOURCE_AFTER:
            changed = copy.deepcopy(metadata); changed['held_review']['source_after_sha256'][path] = '0' * 64; variants.append(changed)
        changed = copy.deepcopy(metadata); changed['files'][witness.ATTACHABLE_PATH]['after_sha256'] = '0' * 64; variants.append(changed)
        changed = copy.deepcopy(metadata); changed['files'][witness.PROJECT + 'behavior_pack/scripts/main.js'] = copy.deepcopy(changed['files'][witness.ATTACHABLE_PATH]); variants.append(changed)
        changed = copy.deepcopy(metadata); changed['files'].pop(witness.ATTACHABLE_PATH); variants.append(changed)
        changed = copy.deepcopy(metadata); changed['held_review']['source_after_sha256']['tools/unreviewed.py'] = '0' * 64; variants.append(changed)
        for changed in variants:
            with self.patch_metadata(changed), self.assertRaises(AssertionError):
                witness.apply_delta(witness.ATTACHABLE_PATH)
        with patch.object(witness, 'REVIEWED_PATCH_SHA256', None), self.assertRaisesRegex(AssertionError, 'not yet admitted'):
            witness.metadata()

    def test_changed_preimage_overlap_and_postimage_fail_after_prior_expectation(self):
        path = witness.ATTACHABLE_PATH
        witness.expected_runtime_bytes(path)
        metadata = witness.metadata(); variants = []
        changed = copy.deepcopy(metadata); changed['files'][path]['before_sha256'] = '0' * 64; variants.append(changed)
        changed = copy.deepcopy(metadata); changed['files'][path]['operations'].append(dict(changed['files'][path]['operations'][0])); variants.append(changed)
        for field in ('before', 'after'):
            changed = copy.deepcopy(metadata); changed['files'][path]['operations'][0][field] += 'x'; variants.append(changed)
        for changed in variants:
            with self.patch_metadata(changed), self.assertRaises(AssertionError):
                witness.expected_runtime_bytes(path)

    def test_only_paired_manifest_version96_bump_is_allowed(self):
        for path in witness.MANIFESTS:
            changed = copy.deepcopy(witness.metadata()); before = witness.source(path)
            after = json.loads(witness.apply_delta(path)); after['header']['uuid'] = '00000000-0000-0000-0000-000000000000'
            text = json.dumps(after, ensure_ascii=False, indent=2) + '\n'
            changed['files'][path]['operations'] = [{'start': 0, 'end': len(before.decode()), 'before': before.decode(), 'after': text}]
            changed['files'][path]['after_sha256'] = witness.sha(text.encode())
            with self.patch_metadata(changed), self.assertRaisesRegex(AssertionError, 'paired G96 identity'):
                witness.apply_delta(path)

    def test_semantic_byte_guard_rejects_other_decoder_guards_order_and_count_edits(self):
        path = witness.ATTACHABLE_PATH; before = witness.source(path); after = witness.apply_delta(path)
        original = json.loads(after)
        for fault in ('count', 'palette', 'food', 'descriptor', 'owner', 'order', 'formatting'):
            current = copy.deepcopy(original)
            rows = current['minecraft:attachable']['description']['scripts']['pre_animation']
            if fault == 'formatting': changed = json.dumps(current).encode()
            else:
                if fault == 'order': rows[0], rows[1] = rows[1], rows[0]
                else:
                    prefix = {'count': 'v.kg_plate_count = math.floor', 'palette': 'v.kg_plate_word_0 = ',
                        'food': 'v.kg_plate_food_0_0 = ', 'descriptor': 'v.kg_plate_desc_0 = ',
                        'owner': 'v.kg_plate_owner_occupied = '}[fault]
                    index = next(i for i, row in enumerate(rows) if row.startswith(prefix))
                    rows[index] += ' 0;'
                changed = json.dumps(current).encode()
            with self.subTest(fault=fault), self.assertRaises(AssertionError):
                witness.assert_held_preservation(path, before, changed)

    def test_every_public_g95_history_row_remains_exact(self):
        original = Path.read_text
        history = json.loads((witness.ROOT / 'release-history.json').read_text())
        history['2.8.95']['BP']['sha256'] = '0' * 64
        with patch.object(Path, 'read_text', lambda path, *args, **kwargs:
            json.dumps(history) if path == witness.ROOT / 'release-history.json' else original(path, *args, **kwargs)):
            with self.assertRaisesRegex(AssertionError, 'Diagnostic G95 history drift'):
                witness.verify_current()


if __name__ == '__main__': unittest.main()
