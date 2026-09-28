"""One-time, checksum-guarded import of the user's delivered A2.8.8 source patch."""
from pathlib import Path, PurePosixPath
import hashlib, io, json, lzma, os, subprocess, tarfile, tempfile

REPO = 'casama233/kaleidoscope-grilling-unofficial'
RID = '1377218440'
BRANCH = 'codex/grilling-a288-local-review'
BASE = '707d28edab4ea9af76878e0e29d8244848971db3'
PAYLOAD_HASH = '5db3c9b3f2f7ca6109474bfa718ad34fa9204d3d639cbbcd29e4c1d27d132ec2'
LEDGER = 'projects/grilling/gameplay_core/review/baseline-pack-sha256.json'
ROOT = Path.cwd().resolve()

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(*args, **kwargs):
    return subprocess.check_output(['git', *args], **kwargs)

def target(relative):
    p = PurePosixPath(relative)
    require(not p.is_absolute() and '..' not in p.parts and '\\' not in relative, 'Unsafe path: ' + relative)
    require(relative.startswith(('projects/grilling/gameplay_core/', 'development/gameplay_core/', 'docs/STATUS-A2.8.8-')), 'Out-of-scope path: ' + relative)
    path = ROOT / relative
    require(path.resolve().is_relative_to(ROOT) and not path.is_symlink() and not path.is_dir(), 'Unsafe target: ' + relative)
    return path

require(os.environ.get('GITHUB_REPOSITORY') == REPO, 'Wrong repository')
require(os.environ.get('GITHUB_REPOSITORY_ID') == RID, 'Wrong repository ID')
require(os.environ.get('GITHUB_REF') == 'refs/heads/' + BRANCH, 'Ref is not the authorized review branch')
require(git('status', '--porcelain') == b'', 'Checkout is not clean')
scope = json.loads((ROOT / '.repo-target.json').read_text(encoding='utf-8-sig'))
require(scope.get('repository') == REPO and str(scope.get('repository_id')) == RID, 'Repository marker mismatch')
raw = b''.join((ROOT / f'.a288-upload/payload.{i}').read_bytes() for i in (1, 2, 3))
require(sha(raw) == PAYLOAD_HASH, 'Payload checksum mismatch')
payload = json.loads(lzma.decompress(raw))
require(set(payload) == {'source.patch', 'changes.json', 'additional_files'}, 'Unexpected payload keys')
manifest = json.loads(payload['changes.json'])
require(manifest['repository'] == REPO and str(manifest['repository_id']) == RID and manifest['baseline_commit'] == BASE, 'Baseline identity mismatch')
files = manifest['files']
transforms = manifest['text_transforms']
require(len(files) == 25 and len(transforms) == 1, 'Unexpected change count')
paths = [entry['path'] for entry in files] + [entry['path'] for entry in transforms]
require(len(set(paths)) == len(paths), 'Duplicate change paths')
planned_transforms = {}
for entry in files:
    path = target(entry['path'])
    before = path.read_bytes() if path.exists() else None
    expected = entry['before_sha256']
    require((before is None and expected is None) or (before is not None and sha(before) == expected), 'Baseline differs: ' + entry['path'])
for entry in transforms:
    path = target(entry['path'])
    before = path.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(before)).encode() + b'\0' + before).hexdigest()
    require(blob == entry['before_git_blob_sha1'], 'Registration baseline differs')
    text = before.decode('utf-8')
    require(text.count(entry['old']) == 1, 'Registration anchor is not unique')
    planned_transforms[entry['path']] = text.replace(entry['old'], entry['new']).encode('utf-8')

archive = git('archive', BASE + ':projects/grilling/gameplay_core', 'behavior_pack', 'resource_pack')
ledger = {}
with tarfile.open(fileobj=io.BytesIO(archive), mode='r:') as tar:
    for member in tar:
        if member.isdir():
            continue
        require(member.isfile() and member.name.startswith(('behavior_pack/', 'resource_pack/')), 'Unexpected archive member')
        require(member.name not in ledger, 'Duplicate archive member')
        ledger[member.name] = sha(tar.extractfile(member).read())
ledger_bytes = (json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')
require(len(ledger) == 1905 and sha(ledger_bytes) == '0a11097fcca89c03cea8df2f5e929120f40f3037460fb53e10caf0187d15b636', 'Canonical baseline does not match delivered artifact ledger')
extras = payload['additional_files']
require(set(extras) == {'development/gameplay_core/verify_a288_local.py', 'docs/STATUS-A2.8.8-LOCAL.md'}, 'Unexpected additional files')
expected_patch_paths = set(paths) - set(extras) - {LEDGER} - set(planned_transforms)
with tempfile.TemporaryDirectory() as temp:
    patch = Path(temp) / 'source.patch'
    patch.write_bytes(payload['source.patch'].encode('utf-8'))
    stats = git('apply', '--numstat', str(patch)).decode('utf-8').splitlines()
    patch_paths = [line.split('\t', 2)[2] for line in stats]
    require(len(patch_paths) == 22 and set(patch_paths) == expected_patch_paths, 'Patch path allowlist mismatch')
    subprocess.run(['git', 'apply', '--check', str(patch)], check=True)
    subprocess.run(['git', 'apply', str(patch)], check=True)
for relative, content in {LEDGER: ledger_bytes, **{p: text.encode('utf-8') for p, text in extras.items()}, **planned_transforms}.items():
    path = target(relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
for entry in files:
    require(sha(target(entry['path']).read_bytes()) == entry['after_sha256'], 'Post-write checksum differs: ' + entry['path'])
for relative, content in planned_transforms.items():
    require(target(relative).read_bytes() == content, 'Registration readback differs')
subprocess.run(['git', 'add', '--', *paths], check=True)
staged = git('diff', '--cached', '--name-only', '-z').decode('utf-8').strip('\0').split('\0')
require(set(staged) == set(paths) and len(staged) == 26, 'Unexpected staged changes')
print('Verified exact source import: 25 delivered files and 1 guarded verifier registration; 1905 baseline pack hashes. No gameplay test or release claimed.')
if os.environ.get('GITHUB_STEP_SUMMARY'):
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as out:
        out.write('## A2.8.8 source import\n\nAll 25 delivered files match their SHA-256 checksums. The verifier registration matched its frozen baseline before modification. All 1905 baseline pack hashes match the delivery ledger. Exactly 26 source/doc/test files staged. This is a source-transfer check, not Minecraft or full CI validation. Main, Releases and servers are untouched.\n')
