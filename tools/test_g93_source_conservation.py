"""Exact G93 diagnostic admission with fail-closed source boundaries."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import g93_source_conservation as witness
import g94_source_conservation as current


class RawClientSourceConservation(unittest.TestCase):
    def patch_metadata(self, data):
        original = Path.read_text
        return patch.object(Path, 'read_text', lambda path, *args, **kwargs:
            json.dumps(data) if path.name == 'g93-runtime-reviewed-delta.json'
            else original(path, *args, **kwargs))

    def test_frozen_g92_g93_precede_exact_five_path_current_admission(self):
        frozen = witness.previous.verify_snapshot(witness.FROZEN_SOURCE_BASE)
        self.assertEqual(frozen['runtime_files'], 4156)
        self.assertEqual(frozen['reviewed_release'], [2, 8, 92])
        self.assertEqual(frozen['reviewed_paths'], 6)
        frozen_g93 = witness.verify_snapshot(current.FROZEN_SOURCE_BASE)
        self.assertEqual(frozen_g93['runtime_files'], 4156)
        self.assertEqual(frozen_g93['reviewed_release'], [2, 8, 93])
        self.assertEqual(frozen_g93['reviewed_paths'], 3)
        latest = witness.verify_current()
        self.assertEqual(latest['runtime_files'], 4157)
        self.assertEqual(latest['reviewed_release'], [2, 8, 95])
        self.assertEqual(latest['reviewed_paths'], 3)
        self.assertEqual(set(witness.metadata()['files']), witness.MANIFESTS | {witness.ATTACHABLE_PATH})
        self.assertEqual(witness.ADDED_PATHS, set())
        path = 'tools/fixtures/g92-runtime-reviewed-delta.json'
        self.assertEqual((witness.ROOT / path).read_bytes(), witness.source(path))

    def test_frozen_g92_validation_failure_blocks_g93_metadata(self):
        with patch.object(witness.previous, 'verify_snapshot', side_effect=AssertionError('Frozen G92 source drift')) as frozen:
            with patch.object(witness, 'metadata') as metadata:
                with self.assertRaisesRegex(AssertionError, 'Frozen G92 source drift'):
                    witness.verify_current()
                frozen.assert_called_once_with(witness.FROZEN_SOURCE_BASE)
                metadata.assert_not_called()

    def test_historical_delegation_keeps_g92_frozen_expectations_independent(self):
        path = witness.ATTACHABLE_PATH
        self.assertEqual(witness.previous.expected_frozen_runtime_bytes(path), witness.source(path))
        self.assertNotEqual(witness.previous.expected_frozen_runtime_bytes(path), witness.expected_runtime_bytes(path))
        for historical in (witness.previous, witness.previous.previous, witness.previous.previous.previous):
            with patch.object(witness, 'verify_current', return_value={'g93': True}) as current:
                self.assertEqual(historical.verify_current(), {'g93': True})
                current.assert_called_once_with()
            for path in witness.DELTA_PATHS:
                self.assertEqual(historical.expected_runtime_bytes(path), witness.expected_runtime_bytes(path))

    def test_exact_attachable_and_all_bp_controller_geometry_animation_bytes(self):
        after = witness.apply_delta(witness.ATTACHABLE_PATH)
        self.assertEqual(witness.sha(after), witness.REVIEWED_AFTER[witness.ATTACHABLE_PATH])
        self.assertEqual(current.source(witness.ATTACHABLE_PATH), after)
        witness.assert_held_preservation(witness.source(witness.ATTACHABLE_PATH), after)
        conserved = [path for path in witness.files() if path not in witness.DELTA_PATHS and (
            '/behavior_pack/' in path or '/render_controllers/' in path or
            '/models/' in path or '/animations/' in path)]
        self.assertTrue(conserved)
        for path in conserved:
            actual = current.source(path) if path in current.DELTA_PATHS else (witness.ROOT / path).read_bytes()
            self.assertEqual(actual, witness.source(path), path)
        controllers = json.loads(witness.source(witness.previous.CONTROLLERS_PATH))['render_controllers']
        self.assertEqual(len(controllers), 33)

    def test_reviewed_and_unchanged_runtime_byte_mutations_fail_closed(self):
        original = Path.read_bytes
        paths = sorted(witness.DELTA_PATHS) + [witness.PROJECT + relative for relative in (
            'behavior_pack/scripts/main.js', 'behavior_pack/scripts/bottle_held_visual_runtime.js',
            'behavior_pack/entities/player.json', 'resource_pack/models/entity/plate_held.geo.json',
            'resource_pack/models/entity/plate_held_qa.geo.json', 'resource_pack/animations/plate_held.animation.json',
            'resource_pack/render_controllers/plate_held.render_controllers.json')]
        for target in paths:
            with self.subTest(target=target):
                with patch.object(Path, 'read_bytes', lambda path:
                    original(path) + b'\n' if path == witness.ROOT / target else original(path)):
                    with self.assertRaisesRegex(AssertionError, 'Runtime source drift'):
                        witness.verify_current()

    def test_missing_or_added_runtime_paths_fail_closed(self):
        original_glob, original_is_file = Path.rglob, Path.is_file
        pack = witness.ROOT / witness.PROJECT / 'resource_pack'
        missing = pack / 'models/entity/plate_held_qa.geo.json'
        extra = pack / 'models/entity/unreviewed_probe.geo.json'
        for fault in ('missing', 'extra'):
            def glob(path, pattern):
                rows = list(original_glob(path, pattern))
                if path == pack:
                    rows = [row for row in rows if row != missing] if fault == 'missing' else rows + [extra]
                return iter(rows)
            with patch.object(Path, 'rglob', glob), patch.object(Path, 'is_file',
                lambda path: True if path == extra else original_is_file(path)):
                with self.assertRaisesRegex(AssertionError, 'Missing/extra G(?:93|94|95) runtime file'):
                    witness.verify_current()

    def test_metadata_rejects_base_tree_patch_hash_scope_and_probe_bytes(self):
        metadata = witness.metadata()
        variants = []
        for key in ('base_commit', 'base_tree'):
            changed = copy.deepcopy(metadata); changed[key] = '0' * 40; variants.append(changed)
        changed = copy.deepcopy(metadata); changed['held_review']['patch_sha256'] = '0' * 64; variants.append(changed)
        for location in ('files', 'held_review'):
            changed = copy.deepcopy(metadata)
            if location == 'files': changed['files'][witness.ATTACHABLE_PATH]['after_sha256'] = '0' * 64
            else: changed['held_review']['after_sha256'][witness.ATTACHABLE_PATH] = '0' * 64
            variants.append(changed)
        changed = copy.deepcopy(metadata)
        changed['files'][witness.PROJECT + 'behavior_pack/scripts/main.js'] = copy.deepcopy(changed['files'][witness.ATTACHABLE_PATH])
        variants.append(changed)
        changed = copy.deepcopy(metadata); changed['files'].pop(witness.ATTACHABLE_PATH); variants.append(changed)
        for changed in variants:
            with self.patch_metadata(changed):
                with self.assertRaises(AssertionError): witness.apply_delta(witness.ATTACHABLE_PATH)

    def test_operations_reject_changed_preimage_overlap_and_result(self):
        metadata = witness.metadata(); path = witness.ATTACHABLE_PATH; variants = []
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
                with self.assertRaisesRegex(AssertionError, 'paired G93 identity'): witness.apply_delta(path)

    def test_semantic_checks_reject_production_order_and_unreviewed_qa_or_mapping(self):
        before = witness.source(witness.ATTACHABLE_PATH)
        for target in ('production', 'qa', 'controller'):
            after = json.loads(witness.apply_delta(witness.ATTACHABLE_PATH))
            desc = after['minecraft:attachable']['description']; rows = desc['scripts']['pre_animation']
            if target == 'production':
                indices = [i for i, row in enumerate(rows) if not row.startswith('v.kg_plate_qa_')]
                a, b = indices[:2]; rows[a], rows[b] = rows[b], rows[a]
                error = 'Production decoder ordering changed'
            elif target == 'qa':
                rows.insert(0, 'v.kg_plate_qa_unreviewed = 1;'); error = 'outside exact raw-client QA statements'
            else:
                desc['render_controllers'].reverse(); error = 'outside exact raw-client QA statements'
            with self.assertRaisesRegex(AssertionError, error):
                witness.assert_held_preservation(before, json.dumps(after).encode())

    def test_frozen_g92_blob_and_current_history_mutations_fail_closed(self):
        git_witness = witness.previous.previous.previous
        original_files = git_witness.files; frozen = dict(original_files(witness.FROZEN_SOURCE_BASE))
        frozen[witness.ATTACHABLE_PATH] = '0' * 40
        with patch.object(git_witness, 'files', lambda ref, *args:
            frozen if ref == witness.FROZEN_SOURCE_BASE else original_files(ref, *args)):
            with self.assertRaisesRegex(AssertionError, 'Frozen G92 source drift'):
                witness.verify_current()
        original = Path.read_text; history = json.loads((witness.ROOT / 'release-history.json').read_text())
        history['2.8.92']['BP']['sha256'] = '0' * 64
        with patch.object(Path, 'read_text', lambda path, *args, **kwargs:
            json.dumps(history) if path == witness.ROOT / 'release-history.json' else original(path, *args, **kwargs)):
            with self.assertRaisesRegex(AssertionError, 'G(?:92|93) history drift'): witness.verify_current()


if __name__ == '__main__': unittest.main()
