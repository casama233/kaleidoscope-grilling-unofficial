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
from urllib.parse import parse_qs, urlsplit

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

    def test_only_exact_optional_staging_checkpoint_pointer_allowed(self):
        self.change('staging_checkpoint', publish.CHECKPOINT)
        self.assertEqual(self.validate()['staging_checkpoint'], publish.CHECKPOINT)
        for value in ('../private.json', '.github/other.json', None, True):
            self.change('staging_checkpoint', value)
            with self.assertRaisesRegex(ValueError, 'checkpoint pointer'):
                self.validate()

    def test_wrong_version_cannot_be_authorized(self):
        with self.assertRaisesRegex(ValueError, 'another version'):
            self.validate('A2.8.65')
        self.change('version', 'A2.8.67')
        with self.assertRaisesRegex(ValueError, 'version/tag'):
            self.validate()

    def test_historical_mode_requires_one_exact_source_ref_and_public_base(self):
        self.change('mode', publish.HISTORICAL_MODE)
        self.change('source_ref', publish.HISTORICAL_REF)
        self.change('public_source_base', publish.CHECKPOINT_TARGET)
        self.assertEqual(self.validate()['mode'], publish.HISTORICAL_MODE)
        for key, value in (('source_ref', 'refs/heads/main'), ('source_ref', 'refs/heads/other'),
                           ('public_source_base', 'b' * 40), ('version', 'A2.8.67')):
            with self.subTest(key=key):
                original = json.loads((self.root / publish.REQUEST).read_text())[key]
                self.change(key, value)
                with self.assertRaises(ValueError):
                    self.validate()
                self.change(key, original)
        self.change('mode', publish.MAIN_MODE)
        with self.assertRaisesRegex(ValueError, 'Wrong main G66 source ref'):
            self.validate()

    def test_historical_notes_identify_frozen_validated_source_without_main_claim(self):
        notes = publish.g66_notes('a' * 40, 'historical snapshot', historical=True)
        self.assertIn('Historical frozen G66', notes)
        self.assertIn('validated GitHub source commit', notes)
        self.assertIn(publish.HISTORICAL_REF, notes)
        self.assertIn(publish.CHECKPOINT_TARGET, notes)
        self.assertNotIn('exact GitHub main commit', notes)

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
        self.recovery_head = sha
        self.parents = [{'sha': publish.CHECKPOINT_TARGET}]
        self.comparison = {'status': 'ahead', 'ahead_by': 1, 'behind_by': 0,
                           'base_commit': {'sha': publish.CHECKPOINT_TARGET},
                           'merge_base_commit': {'sha': publish.CHECKPOINT_TARGET}}
        self.identity = {'full_name': publish.REPO, 'id': publish.REPO_ID}
        self.commit_sha = sha
        self.remote_assets = {}
        self.other_releases = []
        self.other_assets = {}
        self.other_bytes = {}
        self.tags = {}
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
            return {'sha': self.commit_sha, 'parents': copy.deepcopy(self.parents)}
        if endpoint == base + '/compare/' + publish.CHECKPOINT_TARGET + '...' + self.sha:
            return copy.deepcopy(self.comparison)
        if endpoint == base + '/git/ref/heads/main':
            return {'ref': 'refs/heads/main', 'object': {'sha': self.head, 'type': 'commit'}}
        if endpoint == base + '/git/ref/' + publish.HISTORICAL_REF.removeprefix('refs/'):
            return {'ref': publish.HISTORICAL_REF, 'object': {'sha': self.recovery_head, 'type': 'commit'}}
        if endpoint.startswith(base + '/git/ref/tags/'):
            tag = endpoint.split('/git/ref/tags/', 1)[1]
            sha = self.tag_sha if tag == 'A2.8.66-test' else self.tags.get(tag)
            return None if sha is None else {'ref': 'refs/tags/' + tag, 'object': {'sha': sha, 'type': 'commit'}}
        releases = self.other_releases + ([self.release] if self.release is not None else [])
        if endpoint.startswith(base + '/releases?per_page=100&page='):
            page = int(endpoint.rsplit('=', 1)[1])
            return copy.deepcopy(releases[(page - 1) * 100:page * 100])
        if endpoint.startswith(base + '/releases/tags/'):
            tag = endpoint.rsplit('/', 1)[1]
            release = next((p for p in releases if p['tag_name'] == tag and not p['draft']), None)
            if release is None and not allow_missing:
                raise RuntimeError('GitHub API failed: HTTP 404')
            return copy.deepcopy(release)
        if endpoint.startswith(base + '/releases/') and endpoint.endswith('/assets?per_page=100'):
            release_id = int(endpoint.split('/releases/', 1)[1].split('/', 1)[0])
            assets = self.remote_assets if release_id == 123 else self.other_assets[release_id]
            return copy.deepcopy(list(assets.values()))
        if endpoint == base + '/git/refs' and method == 'POST':
            self.tag_sha = payload['sha']
            return {'ref': payload['ref'], 'object': {'sha': self.tag_sha}}
        if endpoint == base + '/releases/latest':
            return {'id': 42}
        if endpoint.startswith(base + '/releases/'):
            release_id = int(endpoint.rsplit('/', 1)[1])
            release = self.release if release_id == 123 else next(p for p in releases if p['id'] == release_id)
            if method == 'PATCH':
                release.update({k: v for k, v in payload.items() if k != 'make_latest'})
            return copy.deepcopy(release)
        raise AssertionError((endpoint, method, payload))

    def run(self, *args):
        self.events.append(('RUN', args))
        if args[:3] == ('gh', 'release', 'create'):
            self.release = self.metadata()
            self.add_assets(self.assets)
        elif args[:2] == ('gh', 'api'):
            endpoint = urlsplit(args[2])
            assert endpoint.scheme == 'https' and endpoint.netloc == 'uploads.github.com'
            assert endpoint.path == f'/repos/{publish.REPO}/releases/123/assets'
            assert args[3:8] == ('--method', 'POST', '-H', 'Content-Type: application/octet-stream', '--input')
            name = parse_qs(endpoint.query)['name'][0]
            assert name == Path(args[8]).name
            assert name not in self.remote_assets, 'Mock upload must not clobber'
            self.add_assets([name])
        else:
            raise AssertionError(args)

    def download(self, asset_id):
        if asset_id in self.other_bytes:
            self.events.append(('DOWNLOAD', asset_id))
            return self.other_bytes[asset_id]
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
        self.request = {'tag': 'A2.8.66-test', 'version': publish.G66, 'mode': publish.MAIN_MODE}
        self.preparation = self.enterContext(patch.object(publish, 'prepare_g66_assets', return_value=(self.request, self.assets, self.notes)))
        self.validate = self.enterContext(patch.object(verify_current, 'require_source_validation',
            return_value={'version': [2, 8, 66], 'source': {'head': self.sha}}))
        self.enterContext(redirect_stdout(io.StringIO()))

    def publish(self):
        publish.publish_g66(self.sha, {}, self.assets, self.source)

    def historical_request(self):
        return dict(self.request, mode=publish.HISTORICAL_MODE, source_ref=publish.HISTORICAL_REF,
                    public_source_base=publish.CHECKPOINT_TARGET)

    def test_exact_historical_recovery_publishes_when_main_is_newer_g67(self):
        self.preparation.return_value = (self.historical_request(), self.assets, self.notes)
        self.remote.head = 'c' * 40
        with patch.dict(publish.os.environ, {'GITHUB_REF': publish.HISTORICAL_REF, 'GITHUB_EVENT_NAME': 'push'}):
            self.publish()
        self.assertFalse(self.remote.release['draft'])
        self.assertEqual(self.remote.tag_sha, self.sha)
        self.assertEqual(self.remote.head, 'c' * 40)
        self.assertFalse(any(event[0] == 'GET' and event[1].endswith('/git/ref/heads/main') for event in self.remote.events))

    def test_historical_wrong_trigger_ref_event_version_or_base_never_writes(self):
        for key, value in (('ref', 'refs/heads/main'), ('ref', 'refs/heads/other'), ('event', 'workflow_dispatch'),
                           ('version', 'A2.8.67'), ('source_ref', 'refs/heads/other'), ('public_source_base', 'b' * 40)):
            with self.subTest(key=key):
                request = self.historical_request()
                if key not in ('ref', 'event'):
                    request[key] = value
                self.preparation.return_value = (request, self.assets, self.notes)
                env = {'GITHUB_REF': value if key == 'ref' else publish.HISTORICAL_REF,
                       'GITHUB_EVENT_NAME': value if key == 'event' else 'push'}
                with patch.dict(publish.os.environ, env), self.assertRaises(ValueError):
                    self.publish()
                self.assertEqual(self.remote.writes(), [])

    def test_historical_remote_source_requires_exact_ref_direct_public_parent_and_ahead(self):
        self.preparation.return_value = (self.historical_request(), self.assets, self.notes)
        cases = [('recovery_head', 'b' * 40), ('commit_sha', 'b' * 40), ('parents', []),
                 ('parents', [{'sha': 'b' * 40}]),
                 ('parents', [{'sha': publish.CHECKPOINT_TARGET}, {'sha': 'b' * 40}])]
        for key, value in (('status', 'identical'), ('status', 'diverged'), ('ahead_by', 2), ('behind_by', 1),
                           ('merge_base_commit', {'sha': 'b' * 40})):
            cases.append(('comparison', dict(self.remote.comparison, **{key: value})))
        with patch.dict(publish.os.environ, {'GITHUB_REF': publish.HISTORICAL_REF, 'GITHUB_EVENT_NAME': 'push'}):
            for key, value in cases:
                with self.subTest(key=key, value=value):
                    original = getattr(self.remote, key)
                    setattr(self.remote, key, value)
                    with self.assertRaises(ValueError):
                        self.publish()
                    self.assertEqual(self.remote.writes(), [])
                    setattr(self.remote, key, original)

    def test_historical_source_branch_race_before_publication_keeps_draft(self):
        self.preparation.return_value = (self.historical_request(), self.assets, self.notes)
        def moved_branch(*args):
            self.remote.recovery_head = 'b' * 40
            return {'version': [2, 8, 66], 'source': {'head': self.sha}}
        self.validate.side_effect = moved_branch
        with patch.dict(publish.os.environ, {'GITHUB_REF': publish.HISTORICAL_REF, 'GITHUB_EVENT_NAME': 'push'}):
            with self.assertRaisesRegex(ValueError, 'source branch changed before publication'):
                self.publish()
        self.assertTrue(self.remote.release['draft'])
        self.assertFalse(any(event[0] == 'PATCH' for event in self.remote.writes()))

    def test_main_entrypoint_limits_historical_mode_to_exact_g66_push(self):
        out = publish.ROOT / 'artifacts/review'
        out.mkdir(parents=True)
        report = {'git_sha': self.sha, 'version': publish.G66}
        for key in ('mcaddon', 'brproject'):
            path = out / ('G66.' + key)
            path.write_bytes(key.encode())
            report[key] = {'sha256': publish.sha256(path)}
        (out / 'SHA256SUMS.txt').write_text('fixture')
        cases = [(publish.G66, publish.HISTORICAL_MODE, publish.HISTORICAL_REF, 'push', True),
                 (publish.G66, publish.MAIN_MODE, 'refs/heads/main', 'push', True),
                 (publish.G66, publish.HISTORICAL_MODE, 'refs/heads/main', 'push', False),
                 (publish.G66, publish.HISTORICAL_MODE, publish.HISTORICAL_REF, 'workflow_dispatch', False),
                 (publish.G66, publish.MAIN_MODE, publish.HISTORICAL_REF, 'push', False),
                 ('A2.8.67', publish.HISTORICAL_MODE, publish.HISTORICAL_REF, 'push', False)]
        for version, mode, ref, event, accepted in cases:
            with self.subTest(version=version, mode=mode, ref=ref, event=event):
                report['version'] = version
                (out / 'build-report.json').write_text(json.dumps(report))
                request = self.historical_request() if mode == publish.HISTORICAL_MODE else self.request
                env = {'GITHUB_REPOSITORY': publish.REPO, 'GITHUB_REPOSITORY_ID': str(publish.REPO_ID),
                       'GITHUB_SHA': self.sha, 'GITHUB_REF': ref, 'GITHUB_EVENT_NAME': event, 'RUNNER_TEMP': ''}
                with patch.dict(publish.os.environ, env), patch('sys.argv', ['publish_test_release.py']), \
                     patch.object(publish, 'call', return_value=self.sha), \
                     patch.object(publish, 'validate_request', return_value=request), \
                     patch.object(publish, 'publish_g66') as command:
                    if accepted:
                        publish.main()
                        command.assert_called_once()
                    else:
                        with self.assertRaises(ValueError):
                            publish.main()
                        command.assert_not_called()

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
        self.assertFalse(any('/releases/tags/' in event[1] for event in self.remote.events if event[0] == 'GET'))

    def unrelated_releases(self, count=100):
        return [dict(self.remote.metadata(), id=1000 + n, tag_name=f'unrelated-{n}') for n in range(count)]

    def test_draft_tag_lookup_is_404_but_listing_and_id_readback_publish(self):
        self.remote.release = self.remote.metadata()
        self.remote.add_assets(self.remote.assets)
        self.assertIsNone(self.remote.api(f'repos/{publish.REPO}/releases/tags/A2.8.66-test', allow_missing=True))
        self.remote.events.clear()
        self.publish()
        self.assertFalse(self.remote.release['draft'])
        self.assertFalse(any('/releases/tags/' in event[1] for event in self.remote.events if event[0] == 'GET'))

    def test_matching_full_draft_resumes_without_create_or_upload(self):
        self.remote.release = self.remote.metadata()
        self.remote.add_assets(self.remote.assets)
        ids = {name: asset['id'] for name, asset in self.remote.remote_assets.items()}
        self.publish()
        self.assertEqual([event[0] for event in self.remote.writes()], ['POST', 'PATCH'])
        self.assertEqual({name: asset['id'] for name, asset in self.remote.remote_assets.items()}, ids)

    def test_paginated_draft_is_found_after_first_full_page(self):
        self.remote.other_releases = self.unrelated_releases()
        self.remote.release = self.remote.metadata()
        self.remote.add_assets(self.remote.assets)
        self.publish()
        self.assertTrue(any(event[1].endswith('releases?per_page=100&page=2') for event in self.remote.events if event[0] == 'GET'))
        self.assertFalse(any(event[0] == 'RUN' for event in self.remote.writes()))

    def test_duplicate_tag_on_later_page_never_writes(self):
        self.remote.other_releases = self.unrelated_releases()
        self.remote.other_releases[0] = dict(self.remote.metadata(), id=456)
        self.remote.release = self.remote.metadata()
        with self.assertRaisesRegex(ValueError, 'Duplicate releases'):
            self.publish()
        self.assertEqual(self.remote.writes(), [])

    def test_inventory_errors_malformed_pages_and_entries_never_imply_absence(self):
        for response in ({'message': 'Forbidden'}, None, [None], [{'id': True, 'tag_name': 'other', 'draft': True}],
                         [{'id': 12, 'tag_name': 'other'}]):
            with self.subTest(response=response):
                original = self.remote.api
                def malformed(endpoint, **kwargs):
                    return response if '/releases?per_page=' in endpoint else original(endpoint, **kwargs)
                with patch.object(publish, 'api', side_effect=malformed), self.assertRaisesRegex(ValueError, 'Malformed release inventory'):
                    self.publish()
                self.assertEqual(self.remote.writes(), [])
        with patch.object(publish, 'release_by_tag', side_effect=RuntimeError('HTTP 403')), self.assertRaisesRegex(RuntimeError, '403'):
            self.publish()
        self.assertEqual(self.remote.writes(), [])

    def test_repeated_id_across_inventory_pages_is_a_race_not_absence(self):
        self.remote.other_releases = self.unrelated_releases()
        self.remote.other_releases.append(copy.deepcopy(self.remote.other_releases[0]))
        with self.assertRaisesRegex(ValueError, 'Repeated release ID'):
            self.publish()
        self.assertEqual(self.remote.writes(), [])

    def test_checkpoint_is_reached_only_after_source_request_and_actual_main_gates(self):
        with patch.object(publish, 'preserve_staging_checkpoint') as checkpoint:
            with patch.object(publish, 'prepare_g66_assets', side_effect=ValueError('fresh source request rejected')):
                with self.assertRaisesRegex(ValueError, 'fresh source request'):
                    self.publish()
            checkpoint.assert_not_called()
            self.remote.head = 'b' * 40
            with self.assertRaisesRegex(ValueError, 'Actual GitHub main'):
                self.publish()
            checkpoint.assert_not_called()
            self.assertEqual(self.remote.writes(), [])

    def test_malformed_publication_patch_response_or_latest_readback_is_reported(self):
        for target in ('patch', 'latest'):
            with self.subTest(target=target):
                self.remote.release = None
                self.remote.remote_assets = {}
                self.remote.tag_sha = None
                self.remote.events = []
                original = self.remote.api
                def malformed(endpoint, **kwargs):
                    result = original(endpoint, **kwargs)
                    if (target == 'patch' and kwargs.get('method') == 'PATCH') or (target == 'latest' and endpoint.endswith('/releases/latest')):
                        return {'message': 'unexpected response'}
                    return result
                with patch.object(publish, 'api', side_effect=malformed), self.assertRaisesRegex(ValueError, 'malformed mutation|Malformed latest'):
                    self.publish()
                self.assertEqual(len([event for event in self.remote.writes() if event[0] == 'PATCH']), 1)

    def test_pinned_id_drift_or_malformed_readback_never_writes(self):
        self.remote.release = self.remote.metadata()
        original = self.remote.api
        for response in (None, [], {'id': True}, dict(self.remote.metadata(), id=456)):
            with self.subTest(response=response):
                def drift(endpoint, **kwargs):
                    return response if endpoint.endswith('/releases/123') else original(endpoint, **kwargs)
                with patch.object(publish, 'api', side_effect=drift), self.assertRaisesRegex(ValueError, 'Pinned release ID'):
                    self.publish()
                self.assertEqual(self.remote.writes(), [])

    def test_raced_tag_replacement_is_not_followed_to_another_release(self):
        self.remote.release = self.remote.metadata()
        self.remote.add_assets(self.remote.assets)
        original = self.remote.download
        def replace(asset_id):
            data = original(asset_id)
            self.remote.release['id'] = 456
            return data
        with patch.object(publish, 'download_asset', side_effect=replace), self.assertRaisesRegex(ValueError, 'ID changed|ID drift'):
            self.publish()
        self.assertFalse(any(event[0] == 'PATCH' for event in self.remote.writes()))

    def test_raced_duplicate_or_published_draft_never_publishes_again(self):
        for change in ('duplicate', 'published'):
            with self.subTest(change=change):
                self.remote.release = self.remote.metadata()
                self.remote.remote_assets = {}
                self.remote.other_releases = []
                self.remote.events = []
                self.remote.add_assets(self.remote.assets)
                original = self.remote.download
                def race(asset_id):
                    data = original(asset_id)
                    if change == 'duplicate' and not self.remote.other_releases:
                        self.remote.other_releases.append(dict(self.remote.metadata(), id=456))
                    elif change == 'published':
                        self.remote.release['draft'] = False
                    return data
                with patch.object(publish, 'download_asset', side_effect=race), self.assertRaises(ValueError):
                    self.publish()
                self.assertFalse(any(event[0] == 'PATCH' for event in self.remote.writes()))

    def test_asset_id_replacement_with_same_bytes_is_refused(self):
        self.remote.release = self.remote.metadata()
        self.remote.add_assets(self.remote.assets)
        original = self.remote.download
        changed = False
        def race(asset_id):
            nonlocal changed
            data = original(asset_id)
            if not changed:
                self.remote.remote_assets[self.assets[0].name]['id'] = 999
                changed = True
            return data
        with patch.object(publish, 'download_asset', side_effect=race), self.assertRaisesRegex(ValueError, 'asset ID drift'):
            self.publish()
        self.assertFalse(any(event[0] == 'PATCH' for event in self.remote.writes()))

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
        uploads = [event[1] for event in self.remote.writes() if event[0] == 'RUN']
        self.assertEqual(len(uploads), len(self.assets) - 1)
        self.assertEqual({args[8] for args in uploads}, {str(p) for p in self.assets[1:]})
        for upload in uploads:
            self.assertEqual(upload[:2], ('gh', 'api'))
            self.assertIn('/releases/123/assets?name=', upload[2])
            self.assertNotIn('--clobber', upload)
        self.assertFalse(self.remote.release['draft'])

    def test_upload_tag_race_cannot_redirect_missing_assets_to_other_release(self):
        self.remote.release = self.remote.metadata()
        self.remote.add_assets([self.assets[0].name])
        existing = copy.deepcopy(self.remote.remote_assets[self.assets[0].name])
        original = self.remote.run
        def raced_upload(*args):
            if not self.remote.other_releases:
                self.remote.other_releases.append(dict(self.remote.metadata(), id=456))
                self.remote.other_assets[456] = {}
            original(*args)
        with patch.object(publish, 'run', side_effect=raced_upload), self.assertRaisesRegex(ValueError, 'Duplicate releases'):
            self.publish()
        self.assertEqual(set(self.remote.remote_assets), set(self.remote.assets))
        self.assertEqual(self.remote.remote_assets[self.assets[0].name], existing)
        self.assertEqual(self.remote.other_assets[456], {})
        self.assertFalse(any(event[0] == 'PATCH' for event in self.remote.writes()))

    def test_duplicate_name_upload_error_is_not_retried_with_delete_or_clobber(self):
        self.remote.release = self.remote.metadata()
        self.remote.add_assets([self.assets[0].name])
        with patch.object(publish, 'run', side_effect=subprocess.CalledProcessError(1, 'gh api', stderr='HTTP 422')) as upload:
            with self.assertRaises(subprocess.CalledProcessError):
                self.publish()
        upload.assert_called_once()
        self.assertEqual(upload.call_args.args[:2], ('gh', 'api'))
        self.assertEqual(set(self.remote.remote_assets), {self.assets[0].name})
        self.assertFalse(any(event[0] in ('POST', 'PATCH') for event in self.remote.writes()))

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

    def test_main_moving_during_final_source_validation_keeps_draft(self):
        def moved_main(*args):
            self.remote.head = 'b' * 40
            return {'version': [2, 8, 66], 'source': {'head': self.sha}}
        self.validate.side_effect = moved_main
        with self.assertRaisesRegex(ValueError, 'main changed before publication'):
            self.publish()
        self.assertTrue(self.remote.release['draft'])
        self.assertNotIn('PATCH', [p[0] for p in self.remote.writes()])

    def test_unknown_or_extra_draft_asset_is_refused(self):
        self.remote.release = self.remote.metadata()
        self.remote.remote_assets['private-world.zip'] = {'name': 'private-world.zip'}
        with self.assertRaisesRegex(ValueError, 'Differing or duplicate'):
            self.publish()
        self.assertEqual(self.remote.writes(), [])


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.request = {'tag': 'A2.8.66-test', 'staging_checkpoint': publish.CHECKPOINT}
        self.remote = FakeGitHub('a' * 40, 'fresh title', 'fresh notes', [])
        self.checkpoint = {'id': publish.CHECKPOINT_ID, 'tag_name': 'A2.8.66-test',
                           'target_commitish': publish.CHECKPOINT_TARGET, 'name': 'original G66 draft',
                           'body': 'Frozen original unpublished notes\n', 'draft': True, 'prerelease': True}
        self.remote.other_releases.append(self.checkpoint)
        self.fixture = {'schema': 1, 'repository': publish.REPO, 'repository_id': publish.REPO_ID,
                        'release_id': publish.CHECKPOINT_ID, 'original_tag': 'A2.8.66-test',
                        'target_sha': publish.CHECKPOINT_TARGET, 'original_name': self.checkpoint['name'],
                        'body_sha256': hashlib.sha256(self.checkpoint['body'].encode()).hexdigest(),
                        'checkpoint_tag': publish.CHECKPOINT_TAG, 'checkpoint_name': 'G66 unpublished staging checkpoint',
                        'assets': {}}
        remote_assets = {}
        for n in range(13):
            name = f'bounded-{n}.json'
            data = (name + '\n').encode()
            digest = hashlib.sha256(data).hexdigest()
            asset_id = 2000 + n
            self.fixture['assets'][name] = {'id': asset_id, 'bytes': len(data), 'sha256': digest}
            remote_assets[name] = {'id': asset_id, 'name': name, 'size': len(data), 'state': 'uploaded', 'digest': 'sha256:' + digest}
            self.remote.other_bytes[asset_id] = data
        self.remote.other_assets[publish.CHECKPOINT_ID] = remote_assets
        self.inventory = remote_assets
        self.path = self.root / publish.CHECKPOINT
        self.path.parent.mkdir()
        self.write_fixture()
        self.enterContext(patch.object(publish, 'ROOT', self.root))
        self.enterContext(patch.object(publish, 'api', side_effect=self.remote.api))
        self.enterContext(patch.object(publish, 'download_asset', side_effect=self.remote.download))
        self.enterContext(patch.object(publish, 'run', side_effect=self.remote.run))

    def write_fixture(self):
        self.path.write_text(json.dumps(self.fixture))

    def preserve(self):
        publish.preserve_staging_checkpoint(self.request)

    def test_exact_draft_rename_preserves_target_body_asset_ids_and_bytes(self):
        original = copy.deepcopy(self.checkpoint)
        inventory = copy.deepcopy(self.inventory)
        data = copy.deepcopy(self.remote.other_bytes)
        self.preserve()
        writes = self.remote.writes()
        self.assertEqual(len(writes), 1)
        self.assertEqual(writes[0], ('PATCH', f'repos/{publish.REPO}/releases/{publish.CHECKPOINT_ID}', {
            'tag_name': publish.CHECKPOINT_TAG, 'name': self.fixture['checkpoint_name'],
            'draft': True, 'prerelease': True, 'make_latest': 'false'}))
        index = self.remote.events.index(writes[0])
        self.assertEqual(len([e for e in self.remote.events[:index] if e[0] == 'DOWNLOAD']), 13)
        self.assertEqual(len([e for e in self.remote.events[index:] if e[0] == 'DOWNLOAD']), 13)
        self.assertEqual(self.checkpoint['body'], original['body'])
        self.assertEqual(self.checkpoint['target_commitish'], original['target_commitish'])
        self.assertEqual(self.inventory, inventory)
        self.assertEqual(self.remote.other_bytes, data)
        self.assertTrue(self.checkpoint['draft'])
        self.assertIsNone(self.remote.release)
        self.assertIsNone(self.remote.tag_sha)
        self.assertEqual(self.remote.tags, {})

    def test_exact_already_renamed_checkpoint_resumes_without_another_patch(self):
        self.preserve()
        self.remote.events.clear()
        # A fresh canonical draft may already exist during a publication retry.
        self.remote.release = self.remote.metadata()
        self.remote.tag_sha = self.remote.sha
        self.preserve()
        self.assertEqual(self.remote.writes(), [])
        self.assertTrue(self.checkpoint['draft'])
        self.assertEqual(self.checkpoint['tag_name'], publish.CHECKPOINT_TAG)

    def test_no_pointer_is_no_action_and_other_pointer_is_rejected(self):
        publish.preserve_staging_checkpoint({'tag': 'A2.8.66-test'})
        self.assertEqual(self.remote.events, [])
        self.request['staging_checkpoint'] = '.github/other.json'
        with self.assertRaisesRegex(ValueError, 'checkpoint pointer'):
            self.preserve()
        self.assertEqual(self.remote.events, [])

    def test_guard_schema_repository_and_fixed_identity_cannot_be_repointed(self):
        for key, value in (('schema', True), ('repository', 'other/repo'), ('repository_id', 1),
                           ('release_id', 123), ('release_id', True), ('original_tag', 'another-tag'),
                           ('target_sha', 'b' * 40), ('checkpoint_tag', 'other-staging'),
                           ('body_sha256', 'bad'), ('original_name', ''), ('checkpoint_name', '')):
            with self.subTest(key=key, value=value):
                original = self.fixture[key]
                self.fixture[key] = value
                self.write_fixture()
                with self.assertRaises(ValueError):
                    self.preserve()
                self.assertEqual(self.remote.writes(), [])
                self.fixture[key] = original
        self.write_fixture()

    def test_guard_requires_exactly_13_well_formed_distinct_asset_ids(self):
        original = copy.deepcopy(self.fixture['assets'])
        variants = [dict(list(original.items())[:12]), dict(original, extra={'id': 9999, 'bytes': 1, 'sha256': 'a' * 64})]
        for key, value in (('id', True), ('id', 2001), ('bytes', -1), ('bytes', True), ('sha256', 'bad')):
            assets = copy.deepcopy(original)
            assets['bounded-0.json'][key] = value
            variants.append(assets)
        for assets in variants:
            with self.subTest(assets=assets):
                self.fixture['assets'] = assets
                self.write_fixture()
                with self.assertRaises(ValueError):
                    self.preserve()
                self.assertEqual(self.remote.writes(), [])

    def test_published_or_changed_checkpoint_metadata_is_never_renamed(self):
        for key, value in (('draft', False), ('prerelease', False), ('tag_name', 'other'),
                           ('target_commitish', 'b' * 40), ('name', 'edited'), ('body', 'edited')):
            with self.subTest(key=key):
                original = self.checkpoint[key]
                self.checkpoint[key] = value
                with self.assertRaises(ValueError):
                    self.preserve()
                self.assertEqual(self.remote.writes(), [])
                self.checkpoint[key] = original

    def test_existing_git_refs_or_destination_release_block_initial_rename(self):
        self.remote.tag_sha = publish.CHECKPOINT_TARGET
        with self.assertRaisesRegex(ValueError, 'absent canonical/staging Git refs'):
            self.preserve()
        self.remote.tag_sha = None
        self.remote.tags[publish.CHECKPOINT_TAG] = publish.CHECKPOINT_TARGET
        with self.assertRaisesRegex(ValueError, 'absent canonical/staging Git refs'):
            self.preserve()
        self.remote.tags.clear()
        self.remote.other_releases.append(dict(self.checkpoint, id=456, tag_name=publish.CHECKPOINT_TAG))
        with self.assertRaisesRegex(ValueError, 'already has a release'):
            self.preserve()
        self.assertEqual(self.remote.writes(), [])

    def test_duplicate_original_tag_blocks_initial_rename(self):
        self.remote.other_releases.append(dict(self.checkpoint, id=456))
        with self.assertRaisesRegex(ValueError, 'Duplicate releases'):
            self.preserve()
        self.assertEqual(self.remote.writes(), [])

    def test_remote_asset_metadata_or_bytes_mismatch_never_patches(self):
        asset = self.inventory['bounded-0.json']
        for key, value in (('id', 999), ('size', 999), ('digest', None), ('digest', 'sha256:' + 'b' * 64),
                           ('state', 'new'), ('name', 'other.json')):
            with self.subTest(key=key):
                original = asset[key]
                asset[key] = value
                with self.assertRaises(ValueError):
                    self.preserve()
                self.assertEqual(self.remote.writes(), [])
                asset[key] = original
        self.remote.other_bytes[2000] = b'tampered'
        with self.assertRaisesRegex(ValueError, 'asset bytes changed'):
            self.preserve()
        self.assertEqual(self.remote.writes(), [])

    def test_remote_missing_extra_duplicate_or_error_asset_inventory_is_rejected(self):
        original = self.remote.api
        expected = list(self.inventory.values())
        for response in (expected[:-1], expected + [dict(expected[0], name='extra')], expected[:-1] + [expected[0]],
                         None, {'message': 'error'}):
            with self.subTest(response=response):
                def malformed(endpoint, **kwargs):
                    return copy.deepcopy(response) if endpoint.endswith('/assets?per_page=100') else original(endpoint, **kwargs)
                with patch.object(publish, 'api', side_effect=malformed), self.assertRaises(ValueError):
                    self.preserve()
                self.assertEqual(self.remote.writes(), [])

    def test_metadata_or_ref_race_during_download_blocks_rename(self):
        original = self.remote.download
        for change in ('published', 'body', 'ref'):
            with self.subTest(change=change):
                self.remote.events.clear()
                self.checkpoint['draft'] = True
                self.checkpoint['body'] = 'Frozen original unpublished notes\n'
                self.remote.tag_sha = None
                def race(asset_id):
                    data = original(asset_id)
                    if change == 'published':
                        self.checkpoint['draft'] = False
                    elif change == 'body':
                        self.checkpoint['body'] = 'changed during download'
                    else:
                        self.remote.tag_sha = publish.CHECKPOINT_TARGET
                    return data
                with patch.object(publish, 'download_asset', side_effect=race), self.assertRaises(ValueError):
                    self.preserve()
                self.assertEqual(self.remote.writes(), [])

    def test_asset_replacement_during_download_blocks_rename(self):
        original = self.remote.download
        def race(asset_id):
            data = original(asset_id)
            self.inventory['bounded-0.json']['id'] = 9999
            return data
        with patch.object(publish, 'download_asset', side_effect=race), self.assertRaisesRegex(ValueError, 'asset identity'):
            self.preserve()
        self.assertEqual(self.remote.writes(), [])

    def test_checkpoint_id_readback_drift_or_malformed_patch_response_is_reported(self):
        original = self.remote.api
        def drift(endpoint, **kwargs):
            response = original(endpoint, **kwargs)
            if endpoint.endswith(f'/releases/{publish.CHECKPOINT_ID}'):
                response['id'] = 456
            return response
        with patch.object(publish, 'api', side_effect=drift), self.assertRaisesRegex(ValueError, 'Pinned release ID'):
            self.preserve()
        self.assertEqual(self.remote.writes(), [])
        def malformed(endpoint, **kwargs):
            response = original(endpoint, **kwargs)
            return None if kwargs.get('method') == 'PATCH' else response
        with patch.object(publish, 'api', side_effect=malformed), self.assertRaisesRegex(ValueError, 'malformed mutation'):
            self.preserve()
        self.assertEqual(len(self.remote.writes()), 1)
        self.assertTrue(self.checkpoint['draft'])

    def test_postrename_asset_race_is_reported_and_never_published(self):
        original = self.remote.api
        def race(endpoint, **kwargs):
            response = original(endpoint, **kwargs)
            if kwargs.get('method') == 'PATCH':
                self.remote.other_bytes[2000] = b'changed after rename'
            return response
        with patch.object(publish, 'api', side_effect=race), self.assertRaisesRegex(ValueError, 'asset bytes changed'):
            self.preserve()
        self.assertEqual(len(self.remote.writes()), 1)
        self.assertTrue(self.checkpoint['draft'])
        self.assertIsNone(self.remote.release)


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
    def test_missing_upload_uses_pinned_id_encoded_basename_and_binary_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            asset = Path(temporary) / 'expected #&?.bin'
            asset.write_bytes(b'binary\x00payload')
            with patch.object(publish, 'run') as command:
                publish.upload_missing_asset(123, asset)
            self.assertEqual(command.call_args.args, (
                'gh', 'api', f'https://uploads.github.com/repos/{publish.REPO}/releases/123/assets?name=expected%20%23%26%3F.bin',
                '--method', 'POST', '-H', 'Content-Type: application/octet-stream', '--input', str(asset), '--silent'))
            for release_id in (True, 0, -1, '123'):
                with patch.object(publish, 'run') as command, self.assertRaisesRegex(ValueError, 'pinned upload release ID'):
                    publish.upload_missing_asset(release_id, asset)
                command.assert_not_called()

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

    def test_success_status_with_malformed_json_is_not_absence(self):
        result = subprocess.CompletedProcess([], 0, '{not-json', '')
        with patch.object(publish.subprocess, 'run', return_value=result), self.assertRaises(ValueError):
            publish.api('repos/example/releases?per_page=100&page=1')

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
