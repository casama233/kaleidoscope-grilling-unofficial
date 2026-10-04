"""Publish tested source; G66 requires an explicit immutable draft/readback gate."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
REPO = 'casama233/kaleidoscope-grilling-unofficial'
REPO_ID = 1377218440
G66 = 'A2.8.66'
REQUEST = '.github/g66-test-release-request.json'
CHECKPOINT = '.github/g66-staging-checkpoint.json'
CHECKPOINT_ID = 403153035
CHECKPOINT_TARGET = '15439bb80b74254a33fa98e823b2f2809ef07523'
CHECKPOINT_TAG = 'A2.8.66-test-staging-15439bb'
MAIN_MODE = 'exact-g66-only-prerelease'
HISTORICAL_MODE = 'exact-g66-historical-prerelease'
HISTORICAL_REF = 'refs/heads/release/g66-historical-recovery-20261004'
EVIDENCE = (
    'docs/STATUS-A2.8.66.md',
    'docs/NATIVE-SECRET-6504-20261004.json',
    'docs/G66-SOURCE-PROVENANCE-20261004.json',
    'docs/BDS-G66-T98-L63-20261004.json',
    '.github/local-test-release-2.8.66.json',
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)


def api(endpoint, *, method='GET', payload=None, allow_missing=False):
    args = ['gh', 'api', endpoint, '--method', method]
    if payload is not None:
        args += ['--input', '-']
    result = subprocess.run(args, cwd=ROOT, input=None if payload is None else json.dumps(payload),
                            text=True, capture_output=True)
    if result.returncode:
        # Only a genuine 404 means absence; permissions/network errors fail closed.
        if allow_missing and re.search(r'\bHTTP 404\b', result.stderr):
            return None
        raise RuntimeError(f'GitHub API failed for {endpoint}: {result.stderr.strip()}')
    return json.loads(result.stdout)


def download_asset(asset_id):
    return subprocess.check_output(
        ['gh', 'api', f'repos/{REPO}/releases/assets/{asset_id}',
         '-H', 'Accept: application/octet-stream'], cwd=ROOT)


def upload_missing_asset(release_id, asset):
    require(type(release_id) is int and release_id > 0, 'Invalid pinned upload release ID')
    # gh authenticates uploads.github.com with its existing github.com token.
    # A duplicate name returns 422; this route never deletes or overwrites.
    endpoint = (f'https://uploads.github.com/repos/{REPO}/releases/{release_id}/assets'
                f'?name={quote(asset.name, safe="")}')
    run('gh', 'api', endpoint, '--method', 'POST', '-H', 'Content-Type: application/octet-stream',
        '--input', str(asset), '--silent')


def release_by_tag(tag):
    # The REST tag endpoint returns published releases only. Authenticated
    # listing includes drafts; scan every page before deciding absence/uniqueness.
    found = []
    seen = set()
    page = 1
    while True:
        releases = api(f'repos/{REPO}/releases?per_page=100&page={page}')
        require(isinstance(releases, list) and len(releases) <= 100, 'Malformed release inventory page')
        for release in releases:
            require(isinstance(release, dict) and type(release.get('id')) is int
                    and release['id'] > 0 and isinstance(release.get('tag_name'), str)
                    and type(release.get('draft')) is bool, 'Malformed release inventory entry')
            require(release['id'] not in seen, 'Repeated release ID in paginated inventory')
            seen.add(release['id'])
            if release['tag_name'] == tag:
                found.append(release)
        if len(releases) < 100:
            break
        page += 1
    require(len(found) <= 1, 'Duplicate releases for exact tag')
    return found[0] if found else None


def release_by_id(release_id):
    require(type(release_id) is int and release_id > 0, 'Invalid pinned release ID')
    release = api(f'repos/{REPO}/releases/{release_id}')
    require(isinstance(release, dict) and type(release.get('id')) is int
            and release['id'] == release_id, 'Pinned release ID drift or malformed readback')
    return release


def require_response_id(release, release_id):
    require(isinstance(release, dict) and type(release.get('id')) is int
            and release['id'] == release_id, 'Pinned release ID drift or malformed mutation response')


def require_unique_release(tag, release_id):
    release = release_by_tag(tag)
    require(release is not None and release['id'] == release_id, 'Exact tag release ID changed or disappeared')


def tag_target(tag):
    ref = api(f'repos/{REPO}/git/ref/tags/{tag}', allow_missing=True)
    if ref is None:
        return None
    require(ref.get('ref') == f'refs/tags/{tag}', 'Unexpected remote tag ref')
    obj = ref['object']
    seen = set()
    while obj.get('type') == 'tag':
        oid = obj['sha']
        require(oid not in seen and len(seen) < 5, 'Cyclic/deep annotated remote tag')
        seen.add(oid)
        obj = api(f'repos/{REPO}/git/tags/{oid}')['object']
    require(obj.get('type') == 'commit', 'Remote tag does not resolve to a commit')
    return obj['sha']


def g66_source_ref(request):
    mode = request.get('mode')
    require(mode in (MAIN_MODE, HISTORICAL_MODE), 'G66 publication is not explicitly requested')
    if mode == HISTORICAL_MODE:
        require(request.get('source_ref') == HISTORICAL_REF
                and request.get('public_source_base') == CHECKPOINT_TARGET, 'Wrong historical G66 source ref/base')
        return HISTORICAL_REF
    require(request.get('source_ref', 'refs/heads/main') == 'refs/heads/main', 'Wrong main G66 source ref')
    return 'refs/heads/main'


def require_source_ref(sha, source_ref, message):
    remote = api(f'repos/{REPO}/git/ref/{source_ref.removeprefix("refs/")}')
    require(isinstance(remote, dict) and remote.get('ref') == source_ref
            and isinstance(remote.get('object'), dict) and remote['object'].get('type') == 'commit'
            and remote['object'].get('sha') == sha, message)


def require_historical_ancestry(sha, commit):
    parents = commit.get('parents')
    require(isinstance(parents, list) and len(parents) == 1 and isinstance(parents[0], dict)
            and parents[0].get('sha') == CHECKPOINT_TARGET, 'Historical G66 source must have exact public-base parent')
    comparison = api(f'repos/{REPO}/compare/{CHECKPOINT_TARGET}...{sha}')
    require(isinstance(comparison, dict) and comparison.get('status') == 'ahead'
            and comparison.get('base_commit', {}).get('sha') == CHECKPOINT_TARGET
            and comparison.get('merge_base_commit', {}).get('sha') == CHECKPOINT_TARGET
            and comparison.get('behind_by') == 0 and type(comparison.get('ahead_by')) is int
            and comparison['ahead_by'] == 1, 'Historical G66 source does not descend from exact public base')


def validate_request(version, report, assets, root=ROOT):
    require(version == G66, 'G66 request cannot authorize another version')
    path = root / REQUEST
    require(path.is_file(), 'G66 needs an explicit root publication request')
    request = json.loads(path.read_text(encoding='utf-8-sig'))
    require(type(request.get('schema')) is int and request['schema'] == 1, 'Unsupported G66 request schema')
    require(request.get('repository') == REPO and request.get('repository_id') == REPO_ID,
            'Wrong G66 publication repository')
    require(request.get('version') == version and request.get('tag') == 'A2.8.66-test', 'Wrong G66 version/tag')
    g66_source_ref(request)
    require(request.get('prerelease') is True and request.get('make_latest') == 'false', 'G66 must stay prerelease/non-latest')
    require(request.get('require_functional_source_receipt') is True, 'G66 requires a functional source receipt')
    if 'staging_checkpoint' in request:
        require(request['staging_checkpoint'] == CHECKPOINT, 'Unexpected G66 staging checkpoint pointer')
    for key in ('complete_client_acceptance', 'java_all_view_parity', 'production_ready', 'saved_world_migration'):
        require(request.get(key) is False, f'G66 cannot promote {key}')
    require(report.get('source_tree_sha256') == request.get('expected_source_tree_sha256')
            and re.fullmatch(r'[0-9a-f]{64}', request.get('expected_source_tree_sha256', '')),
            'Frozen G66 source tree mismatch')
    for key in ('minecraft_tested', 'bds_tested', 'client_visuals_tested'):
        require(report.get(key) is False, f'G66 packaging report cannot promote {key}')
    require(set(request.get('expected_artifacts', {})) == {'mcaddon', 'brproject'}, 'Missing exact G66 artifact expectations')
    for key, asset in zip(('mcaddon', 'brproject'), assets[:2]):
        expected = request['expected_artifacts'][key]
        require(expected.get('name') == f'Kaleidoscope_Grilling_{G66}_Review.{key}', 'Unexpected G66 artifact name')
        require(asset.name == expected['name'] and sha256(asset) == expected.get('sha256')
                and report[key]['sha256'] == expected['sha256'], f'Frozen G66 {key} hash mismatch')
    sums = ''.join(f"{request['expected_artifacts'][key]['sha256']}  {request['expected_artifacts'][key]['name']}\n"
                   for key in ('mcaddon', 'brproject'))
    require((assets[0].parent / 'SHA256SUMS.txt').read_bytes() == sums.encode('utf-8'), 'G66 archive checksum manifest mismatch')
    require(set(request.get('evidence_sha256', {})) == set(EVIDENCE), 'G66 evidence must use the exact bounded allowlist')
    for relative in EVIDENCE:
        require(sha256(root / relative) == request['evidence_sha256'][relative], f'G66 evidence changed: {relative}')
    return request


def g66_notes(sha, status, *, historical=False):
    source = (f'Historical frozen G66, built and functionally checked from validated GitHub source commit `{sha}` '
              f'on `{HISTORICAL_REF}`, descended from public source base `{CHECKPOINT_TARGET}`. '
              'Current main and its newer G67 runtime are untouched. '
              if historical else f'Built and functionally checked from exact GitHub main commit `{sha}`. ')
    return (
        f'# Kaleidoscope Grilling {G66} test prerelease\n\n'
        + source +
        'Only Grilling G66 is published; no Tavern/World Liquor (T/L) release and no live deployment. '
        'This remains a test prerelease, never latest or production-ready. Back up the test world before installation.\n\n'
        'Install the `.mcaddon` with public Cookery 1.0.8. The guide is in the existing Cookery guide; '
        'no separate guide pack is needed, and private Cookery UUIDs cannot be substituted.\n\n'
        'Frozen G66 archives retain the exact reviewed hashes. All assets, including the functional source receipt '
        'and bounded evidence, are downloaded from the staged draft and SHA256-checked before publication. '
        'The release tag must resolve to the actual tested GitHub commit. Private images, worlds and raw logs are excluded.\n\n'
        'Bounded native 6504 witnesses: survival threading, Apple/Carrot artwork in main/offhand, '
        'oil/four flips/seasoning/cook-extract, preserved ordered lore and cooked owner properties 174/180/184, '
        'and a reported 500 ms short-use cancellation with return-to-idle/3-of-3 retention. '
        'These are not continuous active-use, bite timing, or full-use acceptance.\n\n'
        'Limits: lower ingredient remains cropped at FOV 60; third-person edge-on view is inconclusive; '
        'ALT is static-only, with no native ALT active-use witness. Continuous/full-use, broader posture/player/device, '
        'full Java/model/palette/GUI parity and full-family acceptance remain pending. '
        'The cooked world was saved/backed up but that cooked save was not reloaded; saved-world migration is unaccepted. '
        'BDS evidence covers only an isolated 8-pack G66/T98/L63 plus public Cookery 1.0.8 stack, '
        'two successful load/save/restart cycles and marker persistence. It does not certify the 16-pack family, '
        'client gameplay, or rendered parity. Complete client acceptance and production readiness remain false.\n\n'
        '## Frozen pre-publication status snapshot\n\n'
        'The attached status below records the earlier local-only preparation stage. '
        'Its historical no-publication statement is not a claim about the release currently being staged.\n\n'
        + status + '\n'
    )


def prepare_g66_assets(sha, report, assets, source_validation):
    request = validate_request(G66, report, assets)
    require(source_validation is not None and source_validation.is_file(), 'G66 functional source receipt is missing')
    from verify_current import require_source_validation
    receipt = require_source_validation(source_validation)
    require(receipt.get('version') == [2, 8, 66] and receipt['source']['head'] == sha, 'G66 functional receipt version/HEAD mismatch')
    out = assets[0].parent
    copied = out / 'grilling-source-validation.json'
    copied.write_bytes(source_validation.read_bytes())
    notes = out / 'release-notes.md'
    notes.write_text(g66_notes(sha, (ROOT / EVIDENCE[0]).read_text(encoding='utf-8'),
                              historical=request.get('mode') == HISTORICAL_MODE), encoding='utf-8', newline='\n')
    assets = assets + [ROOT / p for p in EVIDENCE] + [ROOT / REQUEST, copied, notes]
    require(len({p.name for p in assets}) == len(assets), 'Duplicate G66 asset names')
    manifest = out / 'RELEASE-ASSET-SHA256SUMS.txt'
    manifest.write_text(''.join(f'{sha256(p)}  {p.name}\n' for p in sorted(assets, key=lambda p: p.name)), encoding='utf-8', newline='\n')
    return request, assets + [manifest], notes


def verify_release_metadata(release, tag, sha, title, notes, *, draft):
    require(isinstance(release, dict), 'Malformed release metadata')
    require(release.get('draft') is draft, 'Refusing to overwrite a published release or unexpected draft state')
    require(release.get('tag_name') == tag and release.get('target_commitish') == sha, 'Differing release tag/target')
    require(release.get('name') == title and release.get('body') == notes, 'Differing release title/notes')
    require(release.get('prerelease') is True, 'Release is not a prerelease')
    require(type(release.get('id')) is int and release['id'] > 0, 'Missing release ID')


def asset_snapshot(assets):
    return {p.name: {'sha256': sha256(p), 'size': p.stat().st_size} for p in assets}


def require_asset_snapshot(assets, snapshot):
    require(asset_snapshot(assets) == snapshot, 'Local staged release assets changed')


def preserve_staging_checkpoint(request):
    """Rename one frozen, unpublished checkpoint; never upload or publish it."""
    if 'staging_checkpoint' not in request:
        return
    require(request['staging_checkpoint'] == CHECKPOINT, 'Unexpected G66 staging checkpoint pointer')
    fixture = json.loads((ROOT / CHECKPOINT).read_text(encoding='utf-8-sig'))
    require(isinstance(fixture, dict) and type(fixture.get('schema')) is int and fixture['schema'] == 1,
            'Unsupported G66 staging checkpoint schema')
    require(fixture.get('repository') == REPO and type(fixture.get('repository_id')) is int
            and fixture['repository_id'] == REPO_ID, 'Wrong staging checkpoint repository')
    require(type(fixture.get('release_id')) is int and fixture['release_id'] == CHECKPOINT_ID
            and fixture.get('original_tag') == 'A2.8.66-test'
            and fixture.get('target_sha') == CHECKPOINT_TARGET
            and fixture.get('checkpoint_tag') == CHECKPOINT_TAG, 'Unexpected staging checkpoint identity')
    require(all(isinstance(fixture.get(key), str) and fixture[key] for key in ('original_name', 'checkpoint_name'))
            and fixture['original_name'] != fixture['checkpoint_name'], 'Invalid staging checkpoint names')
    require(isinstance(fixture.get('body_sha256'), str) and re.fullmatch(r'[0-9a-f]{64}', fixture['body_sha256']),
            'Invalid staging checkpoint body digest')
    expected = fixture.get('assets')
    require(isinstance(expected, dict) and len(expected) == 13, 'Staging checkpoint requires exactly 13 assets')
    ids = set()
    for name, asset in expected.items():
        require(isinstance(name, str) and name and isinstance(asset, dict)
                and type(asset.get('id')) is int and asset['id'] > 0
                and type(asset.get('bytes')) is int and asset['bytes'] >= 0
                and isinstance(asset.get('sha256'), str) and re.fullmatch(r'[0-9a-f]{64}', asset['sha256']),
                'Invalid staging checkpoint asset guard')
        require(asset['id'] not in ids, 'Duplicate staging checkpoint asset ID')
        ids.add(asset['id'])

    def metadata(release, renamed):
        tag = fixture['checkpoint_tag'] if renamed else fixture['original_tag']
        name = fixture['checkpoint_name'] if renamed else fixture['original_name']
        require(release.get('draft') is True and release.get('prerelease') is True,
                'Staging checkpoint must remain an unpublished prerelease')
        require(release.get('tag_name') == tag and release.get('name') == name
                and release.get('target_commitish') == fixture['target_sha'], 'Staging checkpoint metadata changed')
        require(isinstance(release.get('body'), str)
                and hashlib.sha256(release['body'].encode('utf-8')).hexdigest() == fixture['body_sha256'],
                'Staging checkpoint body changed')

    def assets(*, download=True):
        remote = api(f'repos/{REPO}/releases/{CHECKPOINT_ID}/assets?per_page=100')
        require(isinstance(remote, list) and len(remote) == 13
                and all(isinstance(asset, dict) and isinstance(asset.get('name'), str) for asset in remote),
                'Staging checkpoint asset inventory changed')
        names = [asset['name'] for asset in remote]
        require(len(set(names)) == 13 and set(names) == set(expected), 'Staging checkpoint asset names changed')
        for asset in remote:
            pinned = expected[asset['name']]
            require(type(asset.get('id')) is int and asset['id'] == pinned['id']
                    and asset.get('state') == 'uploaded' and type(asset.get('size')) is int
                    and asset['size'] == pinned['bytes'] and asset.get('digest') == 'sha256:' + pinned['sha256'],
                    'Staging checkpoint asset identity/size/digest changed')
            if download:
                data = download_asset(pinned['id'])
                require(len(data) == pinned['bytes'] and hashlib.sha256(data).hexdigest() == pinned['sha256'],
                        'Staging checkpoint asset bytes changed')

    release = release_by_id(CHECKPOINT_ID)
    renamed = release.get('tag_name') == fixture['checkpoint_tag']
    metadata(release, renamed)
    require_unique_release(release['tag_name'], CHECKPOINT_ID)
    if not renamed:
        require(release_by_tag(fixture['checkpoint_tag']) is None, 'Staging checkpoint tag already has a release')
        require(tag_target(fixture['original_tag']) is None and tag_target(fixture['checkpoint_tag']) is None,
                'Staging checkpoint rename requires absent canonical/staging Git refs')
    assets()
    # Asset bytes are immutable for an ID. Catch deletion/replacement after the
    # downloads, then recheck metadata immediately before the bounded PATCH.
    assets(download=False)
    metadata(release_by_id(CHECKPOINT_ID), renamed)
    require_unique_release(release['tag_name'], CHECKPOINT_ID)
    if not renamed:
        require(release_by_tag(fixture['checkpoint_tag']) is None, 'Staging checkpoint tag raced')
        require(tag_target(fixture['original_tag']) is None and tag_target(fixture['checkpoint_tag']) is None,
                'Staging checkpoint Git refs raced')
        patched = api(f'repos/{REPO}/releases/{CHECKPOINT_ID}', method='PATCH', payload={
            'tag_name': fixture['checkpoint_tag'], 'name': fixture['checkpoint_name'],
            'draft': True, 'prerelease': True, 'make_latest': 'false'})
        require_response_id(patched, CHECKPOINT_ID)
        metadata(patched, True)
    metadata(release_by_id(CHECKPOINT_ID), True)
    require_unique_release(fixture['checkpoint_tag'], CHECKPOINT_ID)
    assets()
    metadata(release_by_id(CHECKPOINT_ID), True)


def verify_release_assets(release, assets, *, complete, snapshot=None, remote_ids=None):
    expected = {p.name: p for p in assets}
    snapshot = asset_snapshot(assets) if snapshot is None else snapshot
    remote = api(f"repos/{REPO}/releases/{release['id']}/assets?per_page=100")
    require(isinstance(remote, list) and len(remote) < 100
            and all(isinstance(p, dict) and isinstance(p.get('name'), str) for p in remote),
            'Unexpected/paginated release asset inventory')
    names = [p['name'] for p in remote]
    require(len(set(names)) == len(names) and set(names) <= set(expected), 'Differing or duplicate draft assets')
    require(all(type(p.get('id')) is int and p['id'] > 0 for p in remote)
            and len({p['id'] for p in remote}) == len(remote), 'Missing or duplicate remote asset ID')
    if complete:
        require(set(names) == set(expected), 'Staged release has missing assets')
    if remote_ids is not None:
        require(set(remote_ids) <= set(names), 'Pinned staged release asset disappeared')
    for asset in remote:
        local = expected[asset['name']]
        pinned = snapshot[local.name]
        require(type(asset.get('id')) is int and asset['id'] > 0, 'Missing remote asset ID')
        if remote_ids is not None:
            require(remote_ids.setdefault(local.name, asset['id']) == asset['id'], 'Pinned staged release asset ID drift')
        require(asset.get('state') == 'uploaded' and type(asset.get('size')) is int
                and asset['size'] == pinned['size'], 'Remote asset size/state mismatch')
        digest = pinned['sha256']
        if asset.get('digest') is not None:
            require(asset['digest'] == 'sha256:' + digest, 'Remote reported asset digest mismatch')
        require(hashlib.sha256(download_asset(asset['id'])).hexdigest() == digest,
                f"Remote asset readback SHA256 mismatch: {asset['name']}")
    return set(expected) - set(names)


def publish_g66(sha, report, assets, source_validation):
    request, assets, notes_path = prepare_g66_assets(sha, report, assets, source_validation)
    source_ref = g66_source_ref(request)
    historical = request['mode'] == HISTORICAL_MODE
    if historical:
        require(request.get('version') == G66 and os.environ.get('GITHUB_REF') == HISTORICAL_REF
                and os.environ.get('GITHUB_EVENT_NAME') == 'push', 'Historical G66 needs the exact recovery branch push')
    snapshot = asset_snapshot(assets)
    tag = request['tag']
    title = f'Kaleidoscope Grilling {G66} Integrated Test'
    notes = notes_path.read_text(encoding='utf-8')
    target = json.loads((ROOT / '.repo-target.json').read_text(encoding='utf-8-sig'))
    require(target.get('repository') == REPO and target.get('repository_id') == REPO_ID, 'Checkout repository identity mismatch')
    identity = api(f'repos/{REPO}')
    require(identity.get('full_name') == REPO and identity.get('id') == REPO_ID, 'Authenticated GitHub repository identity mismatch')
    commit = api(f'repos/{REPO}/commits/{sha}')
    require(isinstance(commit, dict) and commit.get('sha') == sha, 'Tested SHA is absent from actual GitHub')
    if historical:
        require_historical_ancestry(sha, commit)
    require_source_ref(sha, source_ref, 'Actual GitHub source branch is not the tested SHA' if historical
                       else 'Actual GitHub main is not the tested SHA')
    preserve_staging_checkpoint(request)
    require_source_ref(sha, source_ref, 'GitHub source branch changed during checkpoint staging' if historical
                       else 'GitHub main changed during checkpoint staging')
    actual_tag = tag_target(tag)
    require(actual_tag is None or actual_tag == sha, 'Refusing to overwrite a differing remote tag')
    release = release_by_tag(tag)
    remote_ids = {}
    if release is not None:
        release_id = release['id']
        release = release_by_id(release_id)
        # Published releases are immutable here, even if their bytes happen to match.
        verify_release_metadata(release, tag, sha, title, notes, draft=True)
        missing = verify_release_assets(release, assets, complete=False, snapshot=snapshot, remote_ids=remote_ids)
        if missing:
            require_asset_snapshot(assets, snapshot)
            require_unique_release(tag, release_id)
            verify_release_metadata(release_by_id(release_id), tag, sha, title, notes, draft=True)
            for asset in assets:
                if asset.name in missing:
                    upload_missing_asset(release_id, asset)
    else:
        require_asset_snapshot(assets, snapshot)
        run('gh', 'release', 'create', tag, *map(str, assets), '--repo', REPO, '--target', sha,
            '--title', title, '--notes-file', str(notes_path), '--draft', '--prerelease', '--latest=false')
        release = release_by_tag(tag)
        require(release is not None, 'Created draft is missing on readback')
        release_id = release['id']
    # Always fetch/download the staged assets, rather than trusting upload success.
    require_unique_release(tag, release_id)
    release = release_by_id(release_id)
    verify_release_metadata(release, tag, sha, title, notes, draft=True)
    verify_release_assets(release, assets, complete=True, snapshot=snapshot, remote_ids=remote_ids)
    require_unique_release(tag, release_id)
    verify_release_metadata(release_by_id(release_id), tag, sha, title, notes, draft=True)
    actual_tag = tag_target(tag)
    if actual_tag is None:
        require_asset_snapshot(assets, snapshot)
        # GitHub may defer a draft's tag creation until publish. Create this one exact
        # ref only after asset validation, so its actual remote target can be checked.
        api(f'repos/{REPO}/git/refs', method='POST', payload={'ref': f'refs/tags/{tag}', 'sha': sha})
    require(tag_target(tag) == sha, 'Actual remote tag target does not match tested GitHub SHA')
    require_source_ref(sha, source_ref, 'GitHub source branch changed before publication' if historical
                       else 'GitHub main changed before publication')
    # Refuse raced edits and revalidate the source receipt immediately before publish.
    require_unique_release(tag, release_id)
    release = release_by_id(release_id)
    verify_release_metadata(release, tag, sha, title, notes, draft=True)
    verify_release_assets(release, assets, complete=True, snapshot=snapshot, remote_ids=remote_ids)
    from verify_current import require_source_validation
    final_receipt = require_source_validation(source_validation)
    require(final_receipt.get('version') == [2, 8, 66] and final_receipt['source']['head'] == sha,
            'G66 final functional receipt version/HEAD mismatch')
    require(sha256(source_validation) == snapshot['grilling-source-validation.json']['sha256'],
            'G66 functional receipt bytes changed during staging')
    require_asset_snapshot(assets, snapshot)
    require_unique_release(tag, release_id)
    verify_release_metadata(release_by_id(release_id), tag, sha, title, notes, draft=True)
    require_source_ref(sha, source_ref, 'GitHub source branch changed before publication' if historical
                       else 'GitHub main changed before publication')
    require(tag_target(tag) == sha, 'Remote tag changed before publication')
    patched = api(f'repos/{REPO}/releases/{release_id}', method='PATCH',
        payload={'draft': False, 'prerelease': True, 'make_latest': 'false'})
    require_response_id(patched, release_id)
    verify_release_metadata(patched, tag, sha, title, notes, draft=False)
    published = release_by_id(release_id)
    verify_release_metadata(published, tag, sha, title, notes, draft=False)
    require_unique_release(tag, release_id)
    verify_release_assets(published, assets, complete=True, snapshot=snapshot, remote_ids=remote_ids)
    require(tag_target(tag) == sha, 'Published remote tag target mismatch')
    latest = api(f'repos/{REPO}/releases/latest', allow_missing=True)
    require(latest is None or (isinstance(latest, dict) and type(latest.get('id')) is int and latest['id'] > 0),
            'Malformed latest release readback')
    require(latest is None or latest.get('id') != published['id'], 'G66 was unexpectedly made latest')
    print('Published exact non-latest prerelease', tag, 'from tested GitHub source', source_ref, sha)


def publish_legacy(version, sha, assets):
    """Keep the pre-G66 unique-per-attempt publication workflow unchanged."""
    tag = f"{version}-test.{os.environ['GITHUB_RUN_NUMBER']}.{os.environ['GITHUB_RUN_ATTEMPT']}"
    out = assets[0].parent
    notes = out / 'release-notes.md'
    status = ROOT / 'docs' / f'STATUS-{version}.md'
    notes.write_text(f'# {version} 整合測試版\n\n此包直接由合併後 main 的 `{sha}` 建置並校驗。\n\n'
        'Minecraft 客戶端操作／畫面及正式存檔遷移：**尚未驗收**。隔離 BDS 測試範圍以本版狀態文件與證據為準。請先備份測試世界。\n\n'
        '安裝 `.mcaddon`；需要公開版 Cookery 1.0.8（私人版 UUID 不可直接替換），煙火指南已在本體內，不需另外安裝指南包。\n\n'
        + (status.read_text(encoding='utf-8') if status.exists() else '') + '\n', encoding='utf-8')
    run('gh', 'release', 'create', tag, *map(str, assets), '--repo', REPO, '--target', sha,
        '--title', f'Kaleidoscope Grilling {version} Integrated Test', '--notes-file', str(notes), '--prerelease')
    print('Published', tag, 'from tested main', sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-validation', type=Path)
    args = parser.parse_args()
    require(os.environ.get('GITHUB_REPOSITORY') == REPO, 'Wrong GitHub repository')
    require(os.environ.get('GITHUB_REPOSITORY_ID') == str(REPO_ID), 'Wrong GitHub repository ID')
    sha = call('git', 'rev-parse', 'HEAD')
    require(sha == os.environ['GITHUB_SHA'] and re.fullmatch(r'[0-9a-f]{40}', sha), 'GitHub tested SHA mismatch')
    out = ROOT / 'artifacts/review'
    report = json.loads((out / 'build-report.json').read_text(encoding='utf-8-sig'))
    require(report['git_sha'] == sha, 'Release tag and tested source must identify the same commit')
    version = report['version']
    require(re.fullmatch(r'A\d+\.\d+\.\d+', version), 'Invalid release version')
    if version != G66:
        require(os.environ.get('GITHUB_REF') == 'refs/heads/main', 'Only tested main can publish another version')
    assets = []
    for key, ext in [('mcaddon', '.mcaddon'), ('brproject', '.brproject')]:
        matches = list(out.glob('*' + ext))
        require(len(matches) == 1, 'Expected one exact current archive per format')
        asset = matches[0]
        require(sha256(asset) == report[key]['sha256'], 'Build report/archive SHA256 mismatch')
        assets.append(asset)
    assets += [out / 'SHA256SUMS.txt', out / 'build-report.json']
    require(all(p.is_file() for p in assets), 'Missing release asset')
    if version == G66:
        request = validate_request(version, report, assets)
        require(os.environ.get('GITHUB_REF') == g66_source_ref(request), 'G66 publication ref/mode mismatch')
        if request['mode'] == HISTORICAL_MODE:
            require(os.environ.get('GITHUB_EVENT_NAME') == 'push', 'Historical G66 needs the exact recovery branch push')
        receipt = args.source_validation
        if receipt is None and os.environ.get('RUNNER_TEMP'):
            receipt = Path(os.environ['RUNNER_TEMP']) / 'grilling-source-validation.json'
        publish_g66(sha, report, assets, receipt)
    else:
        publish_legacy(version, sha, assets)


if __name__ == '__main__':
    main()
