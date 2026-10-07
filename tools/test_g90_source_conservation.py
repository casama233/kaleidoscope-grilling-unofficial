"""Negative source-admission checks for the exact three-lineage integration."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import g90_source_conservation as witness
import public_source_witness as public

class SourceUnionTests(unittest.TestCase):
    def test_all_runtime_bytes_and_three_sources_are_exact(self):
        result = witness.verify_current()
        self.assertEqual(result['sources'],3)
        self.assertEqual(result['collision_labels'],2)
        self.assertEqual(set(witness.metadata()['files']),witness.DELTA_PATHS)

    def test_colliding_histories_and_archived_main_snapshots_are_source_exact(self):
        meta = witness.verify_lineages()
        for version in witness.COLLISIONS:
            self.assertNotEqual(meta['collisions'][version]['main'],meta['collisions'][version]['plate'])
        current = json.loads((witness.ROOT/'release-history.json').read_text())
        witness.assert_history(self,current,witness.PLATE_SOURCE_BASE)

    def test_ambiguous_historical_main_versions_require_a_lineage(self):
        for version in [(2,8,83),(2,8,84)]:
            with self.assertRaisesRegex(AssertionError,'explicit source lineage'):
                public.expected_main_bytes(version)
            plate = public.expected_main_bytes(version,lineage='plate')
            oil = public.expected_main_bytes(version,lineage='cookery_damage')
            self.assertNotEqual(plate,oil)
            ref = witness.MERGED_MAIN_SOURCE_BASE if version[-1]==84 else witness.COOKERY_DAMAGE_SOURCE_BASE
            self.assertEqual(oil,witness.source(ref,witness.MAIN_PATH))

    def test_lineage_tree_snapshot_and_collision_mutations_fail_closed(self):
        original = Path.read_text
        meta = witness.verify_lineages()
        variants=[]
        for key in ['main_commit','plate_commit','main_tree','plate_tree']:
            changed=copy.deepcopy(meta);changed[key]='0'*40;variants.append(changed)
        changed=copy.deepcopy(meta);changed['collisions']['2.8.83']['plate']['BP']['sha256']='0'*64;variants.append(changed)
        changed=copy.deepcopy(meta);changed['main_snapshots'].pop(next(iter(changed['main_snapshots'])));variants.append(changed)
        for changed in variants:
            def read(path,*args,**kwargs):
                return json.dumps(changed) if path.name=='g90-source-lineages.json' else original(path,*args,**kwargs)
            with patch.object(Path,'read_text',read):
                with self.assertRaises(AssertionError):witness.verify_lineages()
        snapshot = witness.ROOT/meta['main_snapshots']['tools/public_source_witness.py']['snapshot']
        original_bytes=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda p:original_bytes(p)+b'\n' if p==snapshot else original_bytes(p)):
            with self.assertRaisesRegex(AssertionError,'snapshot bytes'):witness.verify_lineages()

    def test_current_main_held_assets_and_unchanged_source_mutations_are_rejected(self):
        original=Path.read_bytes
        targets=[witness.MAIN_PATH,witness.PROJECT+'behavior_pack/entities/player.json',
                 witness.PROJECT+'behavior_pack/scripts/oil_api_client.js',
                 witness.PROJECT+'behavior_pack/scripts/secret_held_runtime.js',
                 witness.PROJECT+'resource_pack/attachables/skewer_plate.attachable.json',
                 witness.PROJECT+'resource_pack/render_controllers/bottle_held_contents.render_controllers.json']
        for target in targets:
            with patch.object(Path,'read_bytes',lambda p:original(p)+b'\n' if p==witness.ROOT/target else original(p)):
                with self.assertRaisesRegex(AssertionError,'Runtime source drift'):witness.verify_current()

    def test_reviewed_delta_rejects_wrong_preimage_overlap_and_extra_scope(self):
        original=Path.read_text;meta=witness.metadata();before=witness.source(witness.PLATE_SOURCE_BASE,witness.MAIN_PATH)
        variants=[]
        changed=copy.deepcopy(meta);changed['files'][witness.MAIN_PATH]['before_sha256']='0'*64;variants.append(changed)
        changed=copy.deepcopy(meta);changed['files'][witness.MAIN_PATH]['operations'].append(dict(changed['files'][witness.MAIN_PATH]['operations'][0]));variants.append(changed)
        changed=copy.deepcopy(meta);changed['files'][witness.MAIN_PATH]['operations'][0]['before']+='x';variants.append(changed)
        changed=copy.deepcopy(meta);changed['files'][witness.MAIN_PATH]['operations'][0]['after']+='x';variants.append(changed)
        changed=copy.deepcopy(meta);changed['files'][witness.PROJECT+'behavior_pack/scripts/secret_held_runtime.js']=copy.deepcopy(changed['files'][witness.MAIN_PATH]);variants.append(changed)
        for changed in variants:
            def read(path,*args,**kwargs):
                return json.dumps(changed) if path.name=='g90-runtime-reviewed-delta.json' else original(path,*args,**kwargs)
            with patch.object(Path,'read_text',read):
                with self.assertRaises(AssertionError):witness.apply_delta(before,witness.MAIN_PATH)

    def test_missing_and_extra_runtime_paths_fail_closed(self):
        original_glob=Path.rglob;original_is_file=Path.is_file
        prefix=witness.ROOT/witness.PROJECT/'behavior_pack'
        missing=prefix/'scripts/main.js';extra=prefix/'scripts/unreviewed_runtime.js'
        for fault in ['missing','extra']:
            def glob(path,pattern):
                rows=list(original_glob(path,pattern))
                if path==prefix:
                    rows=[row for row in rows if row!=missing] if fault=='missing' else rows+[extra]
                return iter(rows)
            with patch.object(Path,'rglob',glob),patch.object(Path,'is_file',lambda p:True if p==extra else original_is_file(p)):
                with self.assertRaisesRegex(AssertionError,'Missing/extra G(?:90|91) runtime file'):witness.verify_current()

    def test_manifest_delta_cannot_change_fields_outside_version_identity(self):
        original=Path.read_text;meta=copy.deepcopy(witness.metadata())
        path=next(iter(witness.MANIFESTS));before=witness.source(witness.PLATE_SOURCE_BASE,path)
        wrong=json.loads((witness.ROOT/path).read_text());wrong['header']['uuid']='00000000-0000-0000-0000-000000000000'
        after=(json.dumps(wrong,ensure_ascii=False,indent=2)+'\n').encode()
        meta['files'][path]['operations']=[{'start':0,'end':len(before.decode()),'before':before.decode(),'after':after.decode()}]
        meta['files'][path]['after_sha256']=witness.sha(after)
        def read(p,*args,**kwargs):
            return json.dumps(meta) if p.name=='g90-runtime-reviewed-delta.json' else original(p,*args,**kwargs)
        witness.expected_frozen_runtime_bytes.cache_clear()
        try:
            with patch.object(Path,'read_text',read):
                with self.assertRaisesRegex(AssertionError,'fresh paired release identity'):witness.expected_frozen_runtime_bytes(path)
        finally:witness.expected_frozen_runtime_bytes.cache_clear()

    def test_current_main_and_player_entrypoints_have_exact_union_expectations(self):
        for path in [witness.MAIN_PATH,witness.PROJECT+'behavior_pack/entities/player.json']:
            public.assert_public_bytes(self,path)
        self.assertEqual(public.expected_main_bytes((2,8,90)),witness.expected_runtime_bytes(witness.MAIN_PATH))

if __name__=='__main__':unittest.main()
