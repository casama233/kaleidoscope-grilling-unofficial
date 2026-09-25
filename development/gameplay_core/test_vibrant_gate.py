"""Manifest data regressions, not simulated-player tests."""
import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from vibrant_gate import check_pair, check_archive

class Tests(unittest.TestCase):
    def setUp(self):
        self.bp={'header':{'version':[2,7,68]},'modules':[{'version':[2,7,68]}],
                 'dependencies':[{'uuid':'resource','version':[2,7,68]},{'module_name':'@minecraft/server','version':'2.9.0'}]}
        self.rp={'header':{'uuid':'resource','version':[2,7,68],'min_engine_version':[1,26,50]},'modules':[{'version':[2,7,68]}],'capabilities':['pbr']}
    def test_current_pair(self):self.assertTrue(check_pair(self.bp,self.rp)['pbr'])
    def test_missing_pbr(self):
        self.rp.pop('capabilities')
        with self.assertRaises(ValueError):check_pair(self.bp,self.rp)
    def test_low_engine(self):
        self.rp['header']['min_engine_version']=[1,21,119]
        with self.assertRaises(ValueError):check_pair(self.bp,self.rp)
    def test_stale_dependency(self):
        self.bp['dependencies'][0]['version']=[2,7,67]
        with self.assertRaises(ValueError):check_pair(self.bp,self.rp)
    def test_module_version(self):
        self.rp['modules'][0]['version']=[2,7,67]
        with self.assertRaises(ValueError):check_pair(self.bp,self.rp)
    def test_versions_differ(self):
        self.rp['header']['version']=[2,7,67]
        with self.assertRaises(ValueError):check_pair(self.bp,self.rp)
    def test_api_version_preserved(self):
        before=copy.deepcopy(self.bp);check_pair(self.bp,self.rp);self.assertEqual(before,self.bp)
    def test_export_loss(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'bad.mcaddon';bad=copy.deepcopy(self.rp);bad.pop('capabilities')
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('behavior_pack/manifest.json',json.dumps(self.bp));z.writestr('resource_pack/manifest.json',json.dumps(bad))
            with self.assertRaises(ValueError):check_archive(path,[self.bp,self.rp])

if __name__=='__main__':unittest.main()
