"""G65 source invariants with explicit bounded native evidence, never full admission."""
from pathlib import Path
import hashlib,json,subprocess,sys
from verify_a2862 import main as previous
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from baseline_gate import fingerprint
VERSION=(2,8,65)

def validate_local_pending_receipt(root=ROOT):
    receipt=json.loads((root/'.github/local-test-release-2.8.65.json').read_text())
    assert receipt['schema']==1 and receipt['version']==list(VERSION)
    assert receipt['mode']=='local-pending-native-test' and receipt['publication_status']=='not_published'
    for key in ('complete_client_acceptance','java_all_view_parity','production_ready','saved_world_migration'):
        assert receipt[key] is False,key
    assert receipt['bounded_native_evidence']=='docs/G65-SEASONING-NATIVE-EVIDENCE.json'
    raw=(root/receipt['bounded_native_evidence']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==receipt['bounded_native_evidence_sha256']
    witness=json.loads(raw)
    assert witness['public_base_commit']==receipt['public_base_commit']
    assert witness['release_runtime_fingerprints']==receipt['source_trees']
    assert witness['verdict']['complete_client_acceptance'] is False and witness['verdict']['production_ready'] is False
    config=json.loads((root/'baseline.json').read_text())
    assert config['version']==list(VERSION)
    assert receipt['source_trees']=={side:fingerprint(root/relative)[0] for side,relative in config['runtime'].items()}
    return receipt

def main():
    validate_local_pending_receipt()
    subprocess.run([sys.executable,str(ROOT/'development/gameplay_core/test_g65_local_release_receipt.py')],cwd=ROOT,check=True)
    # Every inherited source assertion remains in the registered .62 chain;
    # only the current compiler name is passed explicitly. Historical .62 callers
    # retain their exact original default identity.
    previous(expected_version=VERSION)
    for script in ('test_held_motion_expression.py','test_seasoning_animation.py','test_seasoning_sprinkle_anchor.py'):
        subprocess.run([sys.executable,str(ROOT/'development/gameplay_core'/script)],cwd=ROOT,check=True)
    for generator in ('build_seasoning_held.py','build_player_extensions.py'):
        subprocess.run([sys.executable,str(ROOT/'tools'/generator),'--check'],cwd=ROOT,check=True)
    subprocess.run(['node','--test','development/gameplay_core/test_seasoning_motion_runtime.mjs'],cwd=ROOT,check=True)
    print('G65 source invariants PASS; bounded native bottle/sprinkle evidence only, complete client/Java-all-view/family/saved-world admission remains pending')

if __name__=='__main__':main()
