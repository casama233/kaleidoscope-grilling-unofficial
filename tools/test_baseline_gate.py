#!/usr/bin/env python3
"""Adversarial release tests in disposable Git repositories, never a game world."""
import copy,importlib.util,json,os,subprocess,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('gate',Path(__file__).with_name('baseline_gate.py'))
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
json_spec=importlib.util.spec_from_file_location('json_check',Path(__file__).with_name('check_json.py'))
json_check=importlib.util.module_from_spec(json_spec);json_spec.loader.exec_module(json_check)
class BaselineGateTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.previous=gate.ROOT;gate.ROOT=self.root
  self.config={'repository':'fixture/owned','repository_id':1,'version':[1,0,0],'runtime':{'BP':'runtime/BP','RP':'runtime/RP'},'packs':{'BP':{'uuid':'bp','dependencies':[]},'RP':{'uuid':'rp','dependencies':[]}}}
  for side in ['BP','RP']:
   root=self.root/'runtime'/side;root.mkdir(parents=True)
   (root/'manifest.json').write_text(json.dumps({'header':{'uuid':side.lower(),'version':[1,0,0]},'modules':[{'version':[1,0,0]}]}));(root/'content.json').write_text('{}')
  self.config['source_trees'],self.files=gate.validate(self.config)
  (self.root/'release-history.json').write_text(json.dumps({'1.0.0':self.config['source_trees']}))
  self.git('init','-q');self.git('config','user.email','fixture@example.invalid');self.git('config','user.name','Fixture');self.git('add','.');self.git('commit','-qm','Fixture')
  self.base=self.git('rev-parse','HEAD').strip()
  self.env={k:os.environ.pop(k) for k in ['GITHUB_REPOSITORY','GITHUB_REPOSITORY_ID'] if k in os.environ}
 def tearDown(self):
  gate.ROOT=self.previous;os.environ.update(self.env);self.tmp.cleanup()
 def git(self,*args):return subprocess.check_output(['git',*args],cwd=self.root,text=True)
 def reject(self,part,fn):
  with self.assertRaises(SystemExit) as caught:fn()
  self.assertIn(part,str(caught.exception))
 def test_valid_clean_release(self):gate.check(self.config,release=True,history_base=self.base)
 def test_readme_version_rejected(self):
  (self.root/'README.md').write_text('## Current maintained baseline: 0.0.1\n')
  self.reject('maintained version',lambda:gate.validate(self.config))
 def test_runtime_edit_rejected(self):
  (self.root/'runtime/BP/content.json').write_text('{"silent":"patch"}')
  self.reject('runtime changed',lambda:gate.check(self.config))
 def test_reused_version_rejected(self):
  (self.root/'runtime/BP/content.json').write_text('{"silent":"patch"}')
  config=copy.deepcopy(self.config);config['source_trees'],_=gate.validate(config)
  self.reject('release identity',lambda:gate.check(config))
 def test_history_tampering_rejected(self):
  (self.root/'release-history.json').write_text('{}')
  self.reject('historical release changed',lambda:gate.check(self.config,history_base=self.base))
 def test_bad_history_reference_rejected(self):self.reject('not a commit',lambda:gate.check(self.config,history_base='unknown-base'))
 def test_untracked_runtime_rejected(self):
  (self.root/'runtime/BP/hidden.json').write_text('{}');config=copy.deepcopy(self.config);config['source_trees'],_=gate.validate(config)
  (self.root/'release-history.json').write_text(json.dumps({'1.0.0':config['source_trees']}))
  self.reject('untracked runtime',lambda:gate.check(config))
 def test_dirty_release_rejected(self):
  (self.root/'release-history.json').write_text(json.dumps({'1.0.0':self.config['source_trees']},indent=2))
  self.reject('commit reviewed',lambda:gate.check(self.config,release=True))
 def test_patched_export_rejected(self):
  archive=self.root/'bad.mcaddon'
  with zipfile.ZipFile(archive,'w') as z:
   for side,rows in self.files.items():
    for path in rows:z.writestr(side+'/'+path,(self.root/self.config['runtime'][side]/path).read_bytes())
   z.writestr('BP/install-only.js','hidden patch')
  self.reject('archive differs',lambda:gate.verify_export(self.config,archive,self.files))
 def test_wrong_repository_rejected(self):
  os.environ['GITHUB_REPOSITORY']='wrong/repo'
  try:self.reject('wrong repository',lambda:gate.check(self.config))
  finally:os.environ.pop('GITHUB_REPOSITORY')

class JsonValidationTests(unittest.TestCase):
 def test_official_reference_header_parses_without_rewriting_original_bytes(self):
  path=json_check.ROOT/json_check.REFERENCE;before=path.read_bytes()
  parsed=json_check.load_json(path)
  self.assertEqual(len(parsed),83);self.assertEqual(parsed[0]['atlas_tile'],'fire_0');self.assertEqual(path.read_bytes(),before)
 def test_ordinary_json_is_strict_and_renamed_reference_comments_reject(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);ordinary=root/'runtime.json';ordinary.write_text('{"label":"// literal"}')
   self.assertEqual(json_check.load_json(ordinary),{'label':'// literal'})
   ordinary.write_text('// unregistered comment\n{"valid":true}')
   with self.assertRaises(json.JSONDecodeError):json_check.load_json(ordinary)
   renamed=root/'renamed.json';renamed.write_bytes((json_check.ROOT/json_check.REFERENCE).read_bytes())
   with self.assertRaises(json.JSONDecodeError):json_check.load_json(renamed)
 def test_reference_byte_hash_and_registered_source_identity_are_required(self):
  raw=(json_check.ROOT/json_check.REFERENCE).read_bytes();source=json.loads((json_check.ROOT/json_check.FIXTURE/'source-manifest.json').read_text())
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);path=root/json_check.REFERENCE;path.parent.mkdir(parents=True);manifest=root/json_check.FIXTURE/'source-manifest.json';manifest.write_text(json.dumps(source))
   with patch.object(json_check,'ROOT',root):
    path.write_bytes(raw+b'\n')
    with self.assertRaisesRegex(ValueError,'fixture bytes changed'):json_check.load_json(path)
    path.write_bytes(raw);wrong=copy.deepcopy(source);wrong['minecraft_bedrock']='1.26.51.1';manifest.write_text(json.dumps(wrong))
    with self.assertRaisesRegex(ValueError,'source identity changed'):json_check.load_json(path)
    wrong=copy.deepcopy(source);next(row for row in wrong['files'] if row['path']=='resource_pack/textures/flipbook_textures.json')['sha256']='unregistered';manifest.write_text(json.dumps(wrong))
    with self.assertRaisesRegex(ValueError,'fixture record changed'):json_check.load_json(path)
if __name__=='__main__':unittest.main()
