"""Publish tested main; G66 requires an explicit immutable draft/readback gate."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
REPO = 'casama233/kaleidoscope-grilling-unofficial'
REPO_ID = 1377218440
G66 = 'A2.8.66'
REQUEST = '.github/g66-test-release-request.json'
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


def release_by_tag(tag):
    return api(f'repos/{REPO}/releases/tags/{tag}', allow_missing=True)


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


def validate_request(version, report, assets, root=ROOT):
    require(version == G66, 'G66 request cannot authorize another version')
    path = root / REQUEST
    require(path.is_file(), 'G66 needs an explicit root publication request')
    request = json.loads(path.read_text(encoding='utf-8-sig'))
    require(type(request.get('schema')) is int and request['schema'] == 1, 'Unsupported G66 request schema')
    require(request.get('repository') == REPO and request.get('repository_id') == REPO_ID,
            'Wrong G66 publication repository')
    require(request.get('version') == version and request.get('tag') == 'A2.8.66-test', 'Wrong G66 version/tag')
    require(request.get('mode') == 'exact-g66-only-prerelease', 'G66 publication is not explicitly requested')
    require(request.get('prerelease') is True and request.get('make_latest') == 'false', 'G66 must stay prerelease/non-latest')
    require(request.get('require_functional_source_receipt') is True, 'G66 requires a functional source receipt')
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


def g66_notes(sha, status):
    return (
        f'# Kaleidoscope Grilling {G66} test prerelease\n\n'
        f'Built and functionally checked from exact GitHub main commit `{sha}`. '
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
    notes.write_text(g66_notes(sha, (ROOT / EVIDENCE[0]).read_text(encoding='utf-8')), encoding='utf-8', newline='\n')
    assets = assets + [ROOT / p for p in EVIDENCE] + [ROOT / REQUEST, copied, notes]
    require(len({p.name for p in assets}) == len(assets), 'Duplicate G66 asset names')
    manifest = out / 'RELEASE-ASSET-SHA256SUMS.txt'
    manifest.write_text(''.join(f'{sha256(p)}  {p.name}\n' for p in sorted(assets, key=lambda p: p.name)), encoding='utf-8', newline='\n')
    return request, assets + [manifest], notes


def verify_release_metadata(release, tag, sha, title, notes, *, draft):
    require(release.get('draft') is draft, 'Refusing to overwrite a published release or unexpected draft state')
    require(release.get('tag_name') == tag and release.get('target_commitish') == sha, 'Differing release tag/target')
    require(release.get('name') == title and release.get('body') == notes, 'Differing release title/notes')
    require(release.get('prerelease') is True, 'Release is not a prerelease')
    require(type(release.get('id')) is int, 'Missing release ID')


def asset_snapshot(assets):
    return {p.name: {'sha256': sha256(p), 'size': p.stat().st_size} for p in assets}


def require_asset_snapshot(assets, snapshot):
    require(asset_snapshot(assets) == snapshot, 'Local staged release assets changed')


def verify_release_assets(release, assets, *, complete, snapshot=None):
    expected = {p.name: p for p in assets}
    snapshot = asset_snapshot(assets) if snapshot is None else snapshot
    remote = api(f"repos/{REPO}/releases/{release['id']}/assets?per_page=100")
    require(isinstance(remote, list) and len(remote) < 100, 'Unexpected/paginated release asset inventory')
    names = [p['name'] for p in remote]
    require(len(set(names)) == len(names) and set(names) <= set(expected), 'Differing or duplicate draft assets')
    if complete:
        require(set(names) == set(expected), 'Staged release has missing assets')
    for asset in remote:
        local = expected[asset['name']]
        pinned = snapshot[local.name]
        require(asset.get('state') == 'uploaded' and asset.get('size') == pinned['size'], 'Remote asset size/state mismatch')
        digest = pinned['sha256']
        if asset.get('digest') is not None:
            require(asset['digest'] == 'sha256:' + digest, 'Remote reported asset digest mismatch')
        require(hashlib.sha256(download_asset(asset['id'])).hexdigest() == digest,
                f"Remote asset readback SHA256 mismatch: {asset['name']}")
    return set(expected) - set(names)


def publish_g66(sha, report, assets, source_validation):
    request, assets, notes_path = prepare_g66_assets(sha, report, assets, source_validation)
    snapshot = asset_snapshot(assets)
    tag = request['tag']
    title = f'Kaleidoscope Grilling {G66} Integrated Test'
    notes = notes_path.read_text(encoding='utf-8')
    target = json.loads((ROOT / '.repo-target.json').read_text(encoding='utf-8-sig'))
    require(target.get('repository') == REPO and target.get('repository_id') == REPO_ID, 'Checkout repository identity mismatch')
    identity = api(f'repos/{REPO}')
    require(identity.get('full_name') == REPO and identity.get('id') == REPO_ID, 'Authenticated GitHub repository identity mismatch')
    require(api(f'repos/{REPO}/commits/{sha}').get('sha') == sha, 'Tested SHA is absent from actual GitHub')
    require(api(f'repos/{REPO}/git/ref/heads/main')['object']['sha'] == sha, 'Actual GitHub main is not the tested SHA')
    actual_tag = tag_target(tag)
    require(actual_tag is None or actual_tag == sha, 'Refusing to overwrite a differing remote tag')
    release = release_by_tag(tag)
    if release is not None:
        # Published releases are immutable here, even if their bytes happen to match.
        verify_release_metadata(release, tag, sha, title, notes, draft=True)
        missing = verify_release_assets(release, assets, complete=False, snapshot=snapshot)
        if missing:
            require_asset_snapshot(assets, snapshot)
            run('gh', 'release', 'upload', tag, *[str(p) for p in assets if p.name in missing], '--repo', REPO)
    else:
        require_asset_snapshot(assets, snapshot)
        run('gh', 'release', 'create', tag, *map(str, assets), '--repo', REPO, '--target', sha,
            '--title', title, '--notes-file', str(notes_path), '--draft', '--prerelease', '--latest=false')
    # Always fetch/download the staged assets, rather than trusting upload success.
    release = release_by_tag(tag)
    require(release is not None, 'Created draft is missing on readback')
    verify_release_metadata(release, tag, sha, title, notes, draft=True)
    verify_release_assets(release, assets, complete=True, snapshot=snapshot)
    actual_tag = tag_target(tag)
    if actual_tag is None:
        require_asset_snapshot(assets, snapshot)
        # GitHub may defer a draft's tag creation until publish. Create this one exact
        # ref only after asset validation, so its actual remote target can be checked.
        api(f'repos/{REPO}/git/refs', method='POST', payload={'ref': f'refs/tags/{tag}', 'sha': sha})
    require(tag_target(tag) == sha, 'Actual remote tag target does not match tested GitHub SHA')
    require(api(f'repos/{REPO}/git/ref/heads/main')['object']['sha'] == sha, 'GitHub main changed before publication')
    # Refuse raced edits and revalidate the source receipt immediately before publish.
    release = release_by_tag(tag)
    verify_release_metadata(release, tag, sha, title, notes, draft=True)
    verify_release_assets(release, assets, complete=True, snapshot=snapshot)
    from verify_current import require_source_validation
    final_receipt = require_source_validation(source_validation)
    require(final_receipt.get('version') == [2, 8, 66] and final_receipt['source']['head'] == sha,
            'G66 final functional receipt version/HEAD mismatch')
    require(sha256(source_validation) == snapshot['grilling-source-validation.json']['sha256'],
            'G66 functional receipt bytes changed during staging')
    require_asset_snapshot(assets, snapshot)
    require(tag_target(tag) == sha, 'Remote tag changed before publication')
    api(f"repos/{REPO}/releases/{release['id']}", method='PATCH',
        payload={'draft': False, 'prerelease': True, 'make_latest': 'false'})
    published = release_by_tag(tag)
    verify_release_metadata(published, tag, sha, title, notes, draft=False)
    verify_release_assets(published, assets, complete=True, snapshot=snapshot)
    require(tag_target(tag) == sha, 'Published remote tag target mismatch')
    latest = api(f'repos/{REPO}/releases/latest', allow_missing=True)
    require(latest is None or latest.get('id') != published['id'], 'G66 was unexpectedly made latest')
    print('Published exact non-latest prerelease', tag, 'from tested GitHub main', sha)


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
    require(os.environ.get('GITHUB_REF') == 'refs/heads/main', 'Only tested main can publish')
    sha = call('git', 'rev-parse', 'HEAD')
    require(sha == os.environ['GITHUB_SHA'] and re.fullmatch(r'[0-9a-f]{40}', sha), 'GitHub tested SHA mismatch')
    out = ROOT / 'artifacts/review'
    report = json.loads((out / 'build-report.json').read_text(encoding='utf-8-sig'))
    require(report['git_sha'] == sha, 'Release tag and tested source must identify the same commit')
    version = report['version']
    require(re.fullmatch(r'A\d+\.\d+\.\d+', version), 'Invalid release version')
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
        receipt = args.source_validation
        if receipt is None and os.environ.get('RUNNER_TEMP'):
            receipt = Path(os.environ['RUNNER_TEMP']) / 'grilling-source-validation.json'
        publish_g66(sha, report, assets, receipt)
    else:
        publish_legacy(version, sha, assets)


if __name__ == '__main__':
    main()
