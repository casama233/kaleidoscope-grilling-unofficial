"""No network or mutations: fail-closed G66 publication/retry regressions."""
from contextlib import redirect_stdout
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import publish_test_release as publish
import package_current
import verify_current


class RequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Fresh CI has no ignored artifacts/review yet. Rebuild only in an
        # isolated fixture, never require or mutate the frozen local artifacts.
        cls.cache = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.cache.cleanup)
        cls.cached = Path(cls.cache.name)
        request = json.loads((publish.ROOT / publish.REQUEST).read_text())
        cls.fixture_report = {'schema': 1, 'version': publish.G66, 'git_sha': 'a' * 40,
                              'source_tree_sha256': request['expected_source_tree_sha256'],
                              'minecraft_tested': False, 'bds_tested': False, 'client_visuals_tested': False}
        for key, roots, excluded in (
            ('mcaddon', [('behavior_pack', package_current.BP), ('resource_pack', package_current.RP)], False),
            ('brproject', [('', package_current.PROJECT)], True),
        ):
            expected = request['expected_artifacts'][key]
            path = cls.cached / expected['name']
            package_current.make_zip(path, roots, exclude_project_builds=excluded)
            cls.fixture_report[key] = {'path': expected['name'], 'sha256': expected['sha256']}
        (cls.cached / 'build-report.json').write_text(json.dumps(cls.fixture_report))
        (cls.cached / 'SHA256SUMS.txt').write_text(''.join(
            f"{request['expected_artifacts'][key]['sha256']}  {request['expected_artifacts'][key]['name']}\n"
            for key in ('mcaddon', 'brproject')), newline='\n')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for relative in (publish.REQUEST, *publish.EVIDENCE):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((publish.ROOT / relative).read_bytes())
        out = self.root / 'artifacts/review'
        out.mkdir(parents=True)
        self.report = copy.deepcopy(self.fixture_report)
        self.assets = []
        for key in ('mcaddon', 'brproject'):
            source = self.cached / self.report[key]['path']
            target = out / source.name
            shutil.copyfile(source, target)
            self.assets.append(target)
        for name in ('SHA256SUMS.txt', 'build-report.json'):
            target = out / name
            shutil.copyfile(self.cached / name, target)
            self.assets.append(target)

    def change(self, key, value):
        path = self.root / publish.REQUEST
        request = json.loads(path.read_text())
        request[key] = value
        path.write_text(json.dumps(request))

    def validate(self, version=publish.G66):
        return publish.validate_request(version, self.report, self.assets, self.root)

    def test_known_frozen_request(self):
        self.assertEqual(self.validate()['tag'], 'A2.8.66-test')

    def test_missing_request_is_not_implicit_permission(self):
        (self.root / publish.REQUEST).unlink()
        with self.assertRaisesRegex(ValueError, 'explicit root'):
            self.validate()

    def test_wrong_version_cannot_be_authorized(self):
        with self.assertRaisesRegex(ValueError, 'another version'):
            self.validate('A2.8.65')
        self.change('version', 'A2.8.67')
        with self.assertRaisesRegex(ValueError, 'version/tag'):
            self.validate()

    def test_missing_hashes_or_wrong_repository_rejected(self):
        for key, value in (('expected_artifacts', {}), ('repository_id', 1),
                           ('expected_source_tree_sha256', '0' * 64), ('evidence_sha256', {})):
            with self.subTest(key=key):
                original = (self.root / publish.REQUEST).read_bytes()
                self.change(key, value)
                with self.assertRaises(ValueError):
                    self.validate()
                (self.root / publish.REQUEST).write_bytes(original)

    def test_archive_and_evidence_tamper_rejected(self):
        for path in (self.assets[0], self.assets[1], self.root / publish.EVIDENCE[1]):
            with self.subTest(path=path.name):
                original = path.read_bytes()
                path.write_bytes(original + b'tamper')
                with self.assertRaisesRegex(ValueError, 'hash mismatch|evidence changed'):
                    self.validate()
                path.write_bytes(original)

    def test_checksum_crlf_drift_rejected(self):
        path = self.assets[2]
        path.write_bytes(path.read_bytes().replace(b'\n', b'\r\n'))
        with self.assertRaisesRegex(ValueError, 'checksum manifest'):
            self.validate()

    def test_admission_or_latest_promotion_rejected(self):
        for key, value in (('prerelease', False), ('make_latest', 'true'),
                           ('require_functional_source_receipt', False),
                           ('complete_client_acceptance', True), ('java_all_view_parity', True),
                           ('production_ready', True), ('saved_world_migration', True)):
            with self.subTest(key=key):
                original = (self.root / publish.REQUEST).read_bytes()
                self.change(key, value)
                with self.assertRaises(ValueError):
                    self.validate()
                (self.root / publish.REQUEST).write_bytes(original)

    def test_packaging_report_cannot_promote_client_or_bds(self):
        for key in ('minecraft_tested', 'bds_tested', 'client_visuals_tested'):
            self.report[key] = True
            with self.assertRaisesRegex(ValueError, 'packaging report'):
                self.validate()
            self.report[key] = False

    def test_no_unbounded_evidence_asset_allowed(self):
        expected = self.validate()['evidence_sha256']
        expected['worlds/private.zip'] = 'a' * 64
        self.change('evidence_sha256', expected)
        with self.assertRaisesRegex(ValueError, 'bounded allowlist'):
            self.validate()

    def test_notes_disclose_bounded_acceptance_and_scope(self):
        notes = publish.g66_notes('a' * 40, 'historical snapshot')
        for phrase in ('500 ms', 'cropped', 'inconclusive', 'ALT is static-only', 'Continuous/full-use',
                       'device', 'full Java', 'cooked save was not reloaded', '8-pack', '16-pack',
                       'no Tavern/World Liquor (T/L) release', 'no live deployment', 'production readiness remain false'):
            self.assertIn(phrase, notes)


class FakeGitHub:
    def __init__(self, sha, title, notes, assets):
        self.sha = sha
        self.title = title
        self.notes = notes
        self.assets = {p.name: p for p in assets}
        self.release = None
        self.tag_sha = None
        self.head = sha
        self.identity = {'full_name': publish.REPO, 'id': publish.REPO_ID}
        self.commit_sha = sha
        self.remote_assets = {}
        self.events = []
        self.corrupt = None

    def metadata(self):
        return {'id': 123, 'tag_name': 'A2.8.66-test', 'target_commitish': self.sha,
                'name': self.title, 'body': self.notes, 'draft': True, 'prerelease': True}

    def add_assets(self, names):
        for name in names:
            path = self.assets[name]
            self.remote_assets[name] = {'id': len(self.remote_assets) + 1, 'name': name,
                'state': 'uploaded', 'size': path.stat().st_size, 'digest': 'sha256:' + publish.sha256(path)}

    def api(self, endpoint, *, method='GET', payload=None, allow_missing=False):
        self.events.append((method, endpoint, payload))
        base = f'repos/{publish.REPO}'
        if endpoint == base:
            return copy.deepcopy(self.identity)
        if endpoint == base + '/commits/' + self.sha:
            return {'sha': self.commit_sha}
        if endpoint == base + '/git/ref/heads/main':
            return {'object': {'sha': self.head, 'type': 'commit'}}
        if endpoint == base + '/git/ref/tags/A2.8.66-test':
            return None if self.tag_sha is None else {'ref': 'refs/tags/A2.8.66-test', 'object': {'sha': self.tag_sha, 'type': 'commit'}}
        if endpoint == base + '/releases/tags/A2.8.66-test':
            return copy.deepcopy(self.release)
        if endpoint == base + '/releases/123/assets?per_page=100':
            return copy.deepcopy(list(self.remote_assets.values()))
        if endpoint == base + '/git/refs' and method == 'POST':
            self.tag_sha = payload['sha']
            return {'ref': payload['ref'], 'object': {'sha': self.tag_sha}}
        if endpoint == base + '/releases/123' and method == 'PATCH':
            self.release.update({k: v for k, v in payload.items() if k != 'make_latest'})
            return copy.deepcopy(self.release)
        if endpoint == base + '/releases/latest':
            return {'id': 42}
        raise AssertionError((endpoint, method, payload))

    def run(self, *args):
        self.events.append(('RUN', args))
        if args[:3] == ('gh', 'release', 'create'):
            self.release = self.metadata()
            self.add_assets(self.assets)
        elif args[:3] == ('gh', 'release', 'upload'):
            self.add_assets(Path(p).name for p in args[4:-2])
        else:
            raise AssertionError(args)

    def download(self, asset_id):
        asset = next(p for p in self.remote_assets.values() if p['id'] == asset_id)
        self.events.append(('DOWNLOAD', asset['name']))
        return b'corrupt' if self.corrupt == asset['name'] else self.assets[asset['name']].read_bytes()

    def writes(self):
        return [e for e in self.events if e[0] in ('RUN', 'POST', 'PATCH')]


class PublicationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / '.repo-target.json').write_text(json.dumps({'repository': publish.REPO, 'repository_id': publish.REPO_ID}))
        self.assets = []
        for name in ('g66.mcaddon', 'g66.brproject', 'SHA256SUMS.txt', 'build-report.json', 'bounded-evidence.json'):
            path = root / name
            path.write_bytes((name + '\n').encode())
            self.assets.append(path)
        self.sha = 'a' * 40
        self.notes = root / 'release-notes.md'
        self.notes.write_text('G66 bounded native evidence only\n')
        self.assets.append(self.notes)
        self.source = root / 'source.json'
        self.source.write_text('{}')
        copied = root / 'grilling-source-validation.json'
        copied.write_bytes(self.source.read_bytes())
        self.assets.append(copied)
        title = 'Kaleidoscope Grilling A2.8.66 Integrated Test'
        self.remote = FakeGitHub(self.sha, title, self.notes.read_text(), self.assets)
        self.enterContext(patch.object(publish, 'ROOT', root))
        self.enterContext(patch.object(publish, 'api', side_effect=self.remote.api))
        self.enterContext(patch.object(publish, 'run', side_effect=self.remote.run))
        self.enterContext(patch.object(publish, 'download_asset', side_effect=self.remote.download))
        self.enterContext(patch.object(publish, 'prepare_g66_assets', return_value=({'tag': 'A2.8.66-test'}, self.assets, self.notes)))
        self.validate = self.enterContext(patch.object(verify_current, 'require_source_validation',
            return_value={'version': [2, 8, 66], 'source': {'head': self.sha}}))
        self.enterContext(redirect_stdout(io.StringIO()))

    def publish(self):
        publish.publish_g66(self.sha, {}, self.assets, self.source)

    def test_draft_readback_and_exact_tag_before_publish(self):
        self.publish()
        self.assertFalse(self.remote.release['draft'])
        writes = self.remote.writes()
        self.assertEqual([p[0] for p in writes], ['RUN', 'POST', 'PATCH'])
        self.assertIn('--draft', writes[0][1])
        self.assertIn('--prerelease', writes[0][1])
        self.assertIn('--latest=false', writes[0][1])
        self.assertEqual(writes[-1][2], {'draft': False, 'prerelease': True, 'make_latest': 'false'})
        patch_index = self.remote.events.index(writes[-1])
        before_publish = self.remote.events[:patch_index]
        downloaded = [event[1] for event in before_publish if event[0] == 'DOWNLOAD']
        self.assertEqual(set(downloaded), {p.name for p in self.assets})
        self.assertEqual(len(downloaded), len(self.assets) * 2)
        self.assertEqual(self.remote.tag_sha, self.sha)
        self.validate.assert_called_once_with(self.source)

    def test_published_matching_release_is_never_overwritten(self):
        self.remote.release = self.remote.metadata()
        self.remote.release['draft'] = False
        with self.assertRaisesRegex(ValueError, 'published'):
            self.publish()
        self.assertEqual(self.remote.writes(), [])

    def test_differing_draft_metadata_refused(self):
        for key, value in (('body', 'other notes'), ('target_commitish', 'b' * 40), ('name', 'another release'), ('prerelease', False)):
            with self.subTest(key=key):
                self.remote.release = self.remote.metadata()
                self.remote.release[key] = value
                with self.assertRaises(ValueError):
                    self.publish()
                self.assertEqual(self.remote.writes(), [])

    def test_differing_draft_asset_refused_before_upload(self):
        self.remote.release = self.remote.metadata()
        self.remote.add_assets([self.assets[0].name])
        self.remote.corrupt = self.assets[0].name
        with self.assertRaisesRegex(ValueError, 'readback SHA256'):
            self.publish()
        self.assertEqual(self.remote.writes(), [])

    def test_matching_partial_draft_fills_only_missing_assets_without_clobber(self):
        self.remote.release = self.remote.metadata()
        self.remote.add_assets([self.assets[0].name])
        self.publish()
        upload = self.remote.writes()[0][1]
        self.assertEqual(upload[:3], ('gh', 'release', 'upload'))
        self.assertNotIn(str(self.assets[0]), upload)
        self.assertNotIn('--clobber', upload)
        self.assertFalse(self.remote.release['draft'])

    def test_corrupted_readback_never_publishes_or_creates_tag(self):
        self.remote.corrupt = self.assets[1].name
        with self.assertRaisesRegex(ValueError, 'readback SHA256'):
            self.publish()
        self.assertEqual([p[0] for p in self.remote.writes()], ['RUN'])
        self.assertTrue(self.remote.release['draft'])
        self.assertIsNone(self.remote.tag_sha)

    def test_wrong_remote_identity_head_commit_or_tag_never_writes(self):
        for key, value in (('identity', {'full_name': publish.REPO, 'id': 1}),
                           ('head', 'b' * 40), ('commit_sha', 'b' * 40), ('tag_sha', 'b' * 40)):
            with self.subTest(key=key):
                original = getattr(self.remote, key)
                setattr(self.remote, key, value)
                with self.assertRaises(ValueError):
                    self.publish()
                self.assertEqual(self.remote.writes(), [])
                setattr(self.remote, key, original)

    def test_source_receipt_changed_before_publish_leaves_draft(self):
        self.validate.side_effect = AssertionError('source/HEAD changed')
        with self.assertRaisesRegex(AssertionError, 'source/HEAD'):
            self.publish()
        self.assertTrue(self.remote.release['draft'])
        self.assertNotIn('PATCH', [p[0] for p in self.remote.writes()])

    def test_local_asset_changed_during_readback_never_publishes(self):
        def mutate_receipt_check(*args):
            self.assets[0].write_bytes(b'changed after upload')
            return {'version': [2, 8, 66], 'source': {'head': self.sha}}
        self.validate.side_effect = mutate_receipt_check
        with self.assertRaisesRegex(ValueError, 'Local staged release assets changed'):
            self.publish()
        self.assertTrue(self.remote.release['draft'])
        self.assertNotIn('PATCH', [p[0] for p in self.remote.writes()])

    def test_functional_receipt_bytes_changed_during_staging_keeps_draft(self):
        def changed_receipt(*args):
            self.source.write_bytes(b'{"changed": true}')
            return {'version': [2, 8, 66], 'source': {'head': self.sha}}
        self.validate.side_effect = changed_receipt
        with self.assertRaisesRegex(ValueError, 'receipt bytes changed'):
            self.publish()
        self.assertTrue(self.remote.release['draft'])
        self.assertNotIn('PATCH', [p[0] for p in self.remote.writes()])

    def test_main_moving_during_staging_keeps_draft(self):
        original = self.remote.run
        def moved_main(*args):
            original(*args)
            self.remote.head = 'b' * 40
        with patch.object(publish, 'run', side_effect=moved_main):
            with self.assertRaisesRegex(ValueError, 'main changed'):
                self.publish()
        self.assertTrue(self.remote.release['draft'])
        self.assertNotIn('PATCH', [p[0] for p in self.remote.writes()])

    def test_unknown_or_extra_draft_asset_is_refused(self):
        self.remote.release = self.remote.metadata()
        self.remote.remote_assets['private-world.zip'] = {'name': 'private-world.zip'}
        with self.assertRaisesRegex(ValueError, 'Differing or duplicate'):
            self.publish()
        self.assertEqual(self.remote.writes(), [])


class PreparationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.assets = []
        for name in ('G66.mcaddon', 'G66.brproject', 'SHA256SUMS.txt', 'build-report.json'):
            path = self.root / 'artifacts/review' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(name.encode())
            self.assets.append(path)
        for relative in (*publish.EVIDENCE, publish.REQUEST):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('bounded snapshot')
        self.sha = 'a' * 40
        self.source = self.root / 'external-source-validation.json'
        self.source.write_bytes(b'{"bound": "functional receipt"}\n')
        self.enterContext(patch.object(publish, 'ROOT', self.root))
        self.enterContext(patch.object(publish, 'validate_request', return_value={'tag': 'A2.8.66-test'}))
        self.receipt = self.enterContext(patch.object(verify_current, 'require_source_validation',
            return_value={'version': [2, 8, 66], 'source': {'head': self.sha}}))

    def test_all_bounded_assets_receipt_and_notes_have_hash_manifest(self):
        request, assets, notes = publish.prepare_g66_assets(self.sha, {}, self.assets, self.source)
        self.receipt.assert_called_once_with(self.source)
        by_name = {p.name: p for p in assets}
        self.assertEqual(len(assets), 13)
        self.assertEqual(by_name['grilling-source-validation.json'].read_bytes(), self.source.read_bytes())
        manifest = by_name['RELEASE-ASSET-SHA256SUMS.txt'].read_text()
        for name, path in by_name.items():
            if name != 'RELEASE-ASSET-SHA256SUMS.txt':
                self.assertIn(publish.sha256(path) + '  ' + name + '\n', manifest)
        self.assertIn(self.sha, notes.read_text())
        self.assertNotIn(b'\r', notes.read_bytes())
        self.assertNotIn(b'\r', by_name['RELEASE-ASSET-SHA256SUMS.txt'].read_bytes())

    def test_missing_receipt_refused_before_any_publication(self):
        self.source.unlink()
        with self.assertRaisesRegex(ValueError, 'receipt is missing'):
            publish.prepare_g66_assets(self.sha, {}, self.assets, self.source)
        self.receipt.assert_not_called()

    def test_wrong_receipt_version_or_head_refused(self):
        for receipt in ({'version': [2, 8, 65], 'source': {'head': self.sha}},
                        {'version': [2, 8, 66], 'source': {'head': 'b' * 40}}):
            self.receipt.return_value = receipt
            with self.assertRaisesRegex(ValueError, 'receipt version/HEAD'):
                publish.prepare_g66_assets(self.sha, {}, self.assets, self.source)


class ApiTests(unittest.TestCase):
    def test_only_http_404_is_absence(self):
        for stderr, absent in (('gh: Not Found (HTTP 404)\n', True), ('gh: Forbidden (HTTP 403)\n', False), ('network unavailable', False)):
            result = subprocess.CompletedProcess([], 1, '', stderr)
            with self.subTest(stderr=stderr), patch.object(publish.subprocess, 'run', return_value=result):
                if absent:
                    self.assertIsNone(publish.api('repos/example', allow_missing=True))
                else:
                    with self.assertRaises(RuntimeError):
                        publish.api('repos/example', allow_missing=True)

    def test_annotated_tag_resolves_actual_commit(self):
        responses = [{'ref': 'refs/tags/A2.8.66-test', 'object': {'sha': 'b' * 40, 'type': 'tag'}},
                     {'object': {'sha': 'a' * 40, 'type': 'commit'}}]
        with patch.object(publish, 'api', side_effect=responses):
            self.assertEqual(publish.tag_target('A2.8.66-test'), 'a' * 40)

    def test_cyclic_or_noncommit_tag_refused(self):
        ref = {'ref': 'refs/tags/A2.8.66-test', 'object': {'sha': 'b' * 40, 'type': 'tag'}}
        with patch.object(publish, 'api', side_effect=[ref, {'object': ref['object']}]), self.assertRaisesRegex(ValueError, 'Cyclic'):
            publish.tag_target('A2.8.66-test')
        ref['object']['type'] = 'tree'
        with patch.object(publish, 'api', return_value=ref), self.assertRaisesRegex(ValueError, 'commit'):
            publish.tag_target('A2.8.66-test')

    def test_older_version_keeps_historical_unique_attempt_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            asset = root / 'review.mcaddon'
            asset.write_bytes(b'fixture')
            with patch.object(publish, 'ROOT', root), patch.dict(publish.os.environ, {'GITHUB_RUN_NUMBER': '72', 'GITHUB_RUN_ATTEMPT': '3'}), patch.object(publish, 'run') as command, redirect_stdout(io.StringIO()):
                publish.publish_legacy('A2.8.65', 'a' * 40, [asset])
            args = command.call_args.args
            self.assertIn('A2.8.65-test.72.3', args)
            self.assertIn('--prerelease', args)
            self.assertNotIn('--draft', args)


if __name__ == '__main__':
    unittest.main()
