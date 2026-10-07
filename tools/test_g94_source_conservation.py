"""Immutable G93 foundation for fail-closed exact G94 source admission."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import g94_source_conservation as witness
import g95_source_conservation as current


class FrozenG93Foundation(unittest.TestCase):
    def test_public_g93_tree_and_unchanged_reviewed_fixtures(self):
        historical = witness.previous.previous.previous.previous
        self.assertEqual(historical.git('rev-parse', witness.FROZEN_SOURCE_BASE + '^{tree}').decode().strip(), witness.FROZEN_TREE)
        result = witness.previous.verify_snapshot(witness.FROZEN_SOURCE_BASE)
        self.assertEqual(result['runtime_files'], 4156)
        self.assertEqual(result['reviewed_release'], [2, 8, 93])
        self.assertEqual(result['reviewed_paths'], 3)
        for release in (92, 93):
            path = f'tools/fixtures/g{release}-runtime-reviewed-delta.json'
            self.assertEqual((witness.ROOT / path).read_bytes(), witness.source(path))

    def test_immutable_snapshot_never_uses_future_current_expectations(self):
        previous = witness.previous
        with patch.object(previous, 'expected_runtime_bytes', side_effect=AssertionError('Future release expectations used')):
            result = previous.verify_snapshot(witness.FROZEN_SOURCE_BASE)
        self.assertEqual(result['reviewed_release'], [2, 8, 93])
        for path in previous.DELTA_PATHS:
            self.assertEqual(previous.expected_frozen_runtime_bytes(path), witness.source(path))

    def test_frozen_g93_blob_mutation_fails_closed(self):
        historical = witness.previous.previous.previous.previous
        original_files = historical.files
        frozen = dict(original_files(witness.FROZEN_SOURCE_BASE))
        frozen[witness.previous.ATTACHABLE_PATH] = '0' * 40
        with patch.object(historical, 'files', lambda ref, *args:
            frozen if ref == witness.FROZEN_SOURCE_BASE else original_files(ref, *args)):
            with self.assertRaisesRegex(AssertionError, 'Frozen G93 source drift'):
                witness.previous.verify_snapshot(witness.FROZEN_SOURCE_BASE)

    def test_predecessor_failure_blocks_g93_metadata(self):
        previous = witness.previous
        with patch.object(previous.previous, 'verify_snapshot', side_effect=AssertionError('Frozen G92 source drift')) as frozen:
            with patch.object(previous, 'metadata') as metadata:
                with self.assertRaisesRegex(AssertionError, 'Frozen G92 source drift'):
                    previous.verify_snapshot(witness.FROZEN_SOURCE_BASE)
                frozen.assert_called_once_with(previous.FROZEN_SOURCE_BASE)
                metadata.assert_not_called()


class BinaryBoardSourceConservation(unittest.TestCase):
    def patch_metadata(self, data):
        original = Path.read_text
        return patch.object(Path, 'read_text', lambda path, *args, **kwargs:
            json.dumps(data) if path.name == 'g94-runtime-reviewed-delta.json'
            else original(path, *args, **kwargs))

    def test_exact_five_paths_one_addition_and_frozen_g93_before_current(self):
        result = witness.verify_snapshot(current.FROZEN_SOURCE_BASE)
        self.assertEqual(result['runtime_files'], 4157)
        self.assertEqual(result['reviewed_release'], [2, 8, 94])
        self.assertEqual(result['reviewed_paths'], 5)
        latest = witness.verify_current()
        self.assertEqual(latest['runtime_files'], 4157)
        self.assertEqual(latest['reviewed_release'], [2, 8, 96])
        self.assertEqual(latest['reviewed_paths'], 3)
        self.assertEqual(set(witness.metadata()['files']), witness.MANIFESTS | set(witness.REVIEWED_AFTER))
        self.assertEqual(witness.ADDED_PATHS, {witness.QA_GEOMETRY_PATH})
        self.assertNotIn(witness.QA_GEOMETRY_PATH, witness.files())
        for path, identity in witness.REVIEWED_AFTER.items():
            after = witness.apply_delta(path)
            self.assertEqual(witness.sha(after), identity)
            self.assertEqual(current.source(path), after)

    def test_frozen_g93_failure_blocks_current_metadata(self):
        with patch.object(witness.previous, 'verify_snapshot', side_effect=AssertionError('Frozen G93 source drift')) as frozen:
            with patch.object(witness, 'metadata') as metadata:
                with self.assertRaisesRegex(AssertionError, 'Frozen G93 source drift'):
                    witness.verify_current()
                frozen.assert_called_once_with(witness.FROZEN_SOURCE_BASE)
                metadata.assert_not_called()

    def test_historical_current_delegation_keeps_g93_frozen_bytes(self):
        path = witness.ATTACHABLE_PATH
        self.assertEqual(witness.previous.expected_frozen_runtime_bytes(path), witness.source(path))
        self.assertNotEqual(witness.previous.expected_frozen_runtime_bytes(path), witness.expected_runtime_bytes(path))
        for historical in (witness.previous, witness.previous.previous,
                           witness.previous.previous.previous, witness.previous.previous.previous.previous):
            with patch.object(witness, 'verify_current', return_value={'g94': True}) as current:
                self.assertEqual(historical.verify_current(), {'g94': True})
                current.assert_called_once_with()
            for path in witness.DELTA_PATHS:
                self.assertEqual(historical.expected_runtime_bytes(path), witness.expected_runtime_bytes(path))

    def test_all_prior_scripts_controllers_geometry_animation_and_bp_remain_exact(self):
        before = json.loads(witness.source(witness.ATTACHABLE_PATH))['minecraft:attachable']['description']
        after = json.loads(witness.apply_delta(witness.ATTACHABLE_PATH))['minecraft:attachable']['description']
        self.assertEqual(after['scripts'], before['scripts'])
        self.assertEqual(after['animations'], before['animations'])
        old = json.loads(witness.source(witness.CONTROLLERS_PATH))['render_controllers']
        new = json.loads(witness.apply_delta(witness.CONTROLLERS_PATH))['render_controllers']
        self.assertEqual(len(old), 33)
        self.assertEqual(list(new), list(old) + [witness.QA_CONTROLLER])
        for name, value in old.items(): self.assertEqual(new[name], value)
        conserved = [path for path in witness.files() if path not in witness.DELTA_PATHS and (
            '/behavior_pack/' in path or '/models/' in path or '/animations/' in path)]
        self.assertTrue(conserved)
        for path in conserved:
            actual = current.source(path) if path in current.DELTA_PATHS else (witness.ROOT / path).read_bytes()
            self.assertEqual(actual, witness.source(path), path)

    def test_reviewed_and_unchanged_runtime_mutations_fail_closed(self):
        original = Path.read_bytes
        paths = sorted(witness.DELTA_PATHS) + [witness.PROJECT + relative for relative in (
            'behavior_pack/scripts/main.js', 'behavior_pack/scripts/bottle_held_visual_runtime.js',
            'behavior_pack/entities/player.json', 'resource_pack/models/entity/plate_held.geo.json',
            'resource_pack/models/entity/plate_held_qa.geo.json', 'resource_pack/animations/plate_held.animation.json')]
        for target in paths:
            with self.subTest(target=target):
                with patch.object(Path, 'read_bytes', lambda path:
                    original(path) + b'\n' if path == witness.ROOT / target else original(path)):
                    with self.assertRaisesRegex(AssertionError, 'Runtime source drift'):
                        witness.verify_current()

    def test_missing_existing_added_or_extra_runtime_paths_fail_closed(self):
        original_glob, original_is_file = Path.rglob, Path.is_file
        pack = witness.ROOT / witness.PROJECT / 'resource_pack'
        extra = pack / 'models/entity/unreviewed_probe.geo.json'
        for target in (witness.ROOT / witness.QA_GEOMETRY_PATH,
                       pack / 'models/entity/plate_held_qa.geo.json', extra):
            def glob(path, pattern):
                rows = list(original_glob(path, pattern))
                if path == pack:
                    rows = rows + [extra] if target == extra else [row for row in rows if row != target]
                return iter(rows)
            with patch.object(Path, 'rglob', glob), patch.object(Path, 'is_file',
                lambda path: True if path == extra else original_is_file(path)):
                with self.assertRaisesRegex(AssertionError, 'Missing/extra G(?:94|95|96) runtime file'):
                    witness.verify_current()

    def test_metadata_rejects_base_tree_patch_hash_scope_and_reviewed_bytes(self):
        metadata = witness.metadata(); variants = []
        for key in ('base_commit', 'base_tree'):
            changed = copy.deepcopy(metadata); changed[key] = '0' * 40; variants.append(changed)
        changed = copy.deepcopy(metadata); changed['held_review']['patch_sha256'] = '0' * 64; variants.append(changed)
        for path in witness.REVIEWED_AFTER:
            for location in ('files', 'held_review'):
                changed = copy.deepcopy(metadata)
                if location == 'files': changed['files'][path]['after_sha256'] = '0' * 64
                else: changed['held_review']['after_sha256'][path] = '0' * 64
                variants.append(changed)
        changed = copy.deepcopy(metadata)
        changed['files'][witness.PROJECT + 'behavior_pack/scripts/main.js'] = copy.deepcopy(changed['files'][witness.ATTACHABLE_PATH])
        variants.append(changed)
        changed = copy.deepcopy(metadata); changed['files'].pop(witness.QA_GEOMETRY_PATH); variants.append(changed)
        for changed in variants:
            with self.patch_metadata(changed):
                with self.assertRaises(AssertionError): witness.apply_delta(witness.ATTACHABLE_PATH)

    def test_operations_reject_preimage_overlap_and_changed_result(self):
        for path in (witness.ATTACHABLE_PATH, witness.QA_GEOMETRY_PATH):
            metadata = witness.metadata(); variants = []
            changed = copy.deepcopy(metadata); changed['files'][path]['before_sha256'] = '0' * 64; variants.append(changed)
            changed = copy.deepcopy(metadata); changed['files'][path]['operations'].append(dict(changed['files'][path]['operations'][0])); variants.append(changed)
            for field in ('before', 'after'):
                changed = copy.deepcopy(metadata); changed['files'][path]['operations'][0][field] += 'x'; variants.append(changed)
            for changed in variants:
                with self.patch_metadata(changed):
                    with self.assertRaises(AssertionError): witness.apply_delta(path)

    def test_manifest_only_paired_version_bump_is_permitted(self):
        for path in witness.MANIFESTS:
            metadata = copy.deepcopy(witness.metadata()); before = witness.source(path)
            after = json.loads(witness.apply_delta(path)); after['header']['uuid'] = '00000000-0000-0000-0000-000000000000'
            text = json.dumps(after, ensure_ascii=False, indent=2) + '\n'
            metadata['files'][path]['operations'] = [{'start': 0, 'end': len(before.decode()), 'before': before.decode(), 'after': text}]
            metadata['files'][path]['after_sha256'] = witness.sha(text.encode())
            with self.patch_metadata(metadata):
                with self.assertRaisesRegex(AssertionError, 'paired G94 identity'): witness.apply_delta(path)

    def test_semantics_reject_script_old_controller_binary_gate_and_geometry_scope_drift(self):
        path = witness.ATTACHABLE_PATH; before = witness.source(path)
        after = json.loads(witness.apply_delta(path))
        after['minecraft:attachable']['description']['scripts']['pre_animation'].append('v.kg_plate_count = 1;')
        with self.assertRaisesRegex(AssertionError, 'decoder or log statements changed'):
            witness.assert_held_preservation(path, before, json.dumps(after).encode())
        for fault in ('old_controller', 'binary_gate', 'binary_bit'):
            path = witness.CONTROLLERS_PATH; before = witness.source(path)
            after = json.loads(witness.apply_delta(path)); controllers = after['render_controllers']
            if fault == 'old_controller':
                controllers[next(iter(controllers))]['geometry'] = 'Geometry.qa_binary'
                error = 'Production/prior QA controller changed'
            else:
                row = controllers[witness.QA_CONTROLLER]['part_visibility'][2]
                bone, value = next(iter(row.items()))
                row[bone] = value.replace('v.kg_plate_qa_enabled == 1', '1') if fault == 'binary_gate' else value.replace('/8388608', '/4194304')
                error = 'Binary QA bit layout/gating changed'
            with self.assertRaisesRegex(AssertionError, error):
                witness.assert_held_preservation(path, before, json.dumps(after).encode())
        path = witness.QA_GEOMETRY_PATH; after = json.loads(witness.apply_delta(path))
        after['minecraft:geometry'][0]['bones'].append({'name': 'unreviewed_geometry'})
        with self.assertRaisesRegex(AssertionError, 'board bone scope/order changed'):
            witness.assert_held_preservation(path, b'', json.dumps(after).encode())

    def test_unchanged_old_fixtures_and_all_g93_history_rows_fail_closed(self):
        original_bytes = Path.read_bytes
        for release in (92, 93):
            target = witness.ROOT / f'tools/fixtures/g{release}-runtime-reviewed-delta.json'
            with patch.object(Path, 'read_bytes', lambda path:
                original_bytes(path) + b'\n' if path == target else original_bytes(path)):
                with self.assertRaisesRegex(AssertionError, 'Frozen reviewed fixture drift'):
                    witness.verify_current()
        original_text = Path.read_text
        history = json.loads((witness.ROOT / 'release-history.json').read_text())
        history['2.8.93']['BP']['sha256'] = '0' * 64
        with patch.object(Path, 'read_text', lambda path, *args, **kwargs:
            json.dumps(history) if path == witness.ROOT / 'release-history.json' else original_text(path, *args, **kwargs)):
            with self.assertRaisesRegex(AssertionError, '(?:G93|Diagnostic G94|Diagnostic G95) history drift'): witness.verify_current()


if __name__ == '__main__': unittest.main()
