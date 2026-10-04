"""G66 canonical source gate; bounded secret evidence never implies full admission."""
from pathlib import Path
import hashlib,json,subprocess,sys
from verify_a2862 import main as previous
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from baseline_gate import fingerprint
VERSION=(2,8,66)

def validate_local_pending_receipt(root=ROOT):
    receipt=json.loads((root/'.github/local-test-release-2.8.66.json').read_text())
    assert type(receipt['schema']) is int and receipt['schema']==1 and receipt['version']==list(VERSION)
    assert receipt['mode']=='local-pending-native-test' and receipt['publication_status']=='not_published'
    for key in ('complete_client_acceptance','java_all_view_parity','production_ready','saved_world_migration'):
        assert receipt[key] is False,key
    assert receipt['bounded_native_evidence']=='docs/NATIVE-SECRET-6504-20261004.json'
    raw=(root/receipt['bounded_native_evidence']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==receipt['bounded_native_evidence_sha256']
    witness=json.loads(raw)
    assert witness['public_base_commit']==receipt['public_base_commit']
    assert witness['release_version']==list(VERSION)
    assert witness['release_runtime_fingerprints']==receipt['source_trees']
    assert witness['client'] is False and witness['production_ready'] is False
    assert witness['verified']['main_apple_and_carrot_artwork_restored'] is True
    assert witness['verified']['off_apple_and_carrot_artwork_restored'] is True
    assert witness['verified']['cooked_effective_main_player_projection']==[174,180,184]
    assert witness['verified']['short_main_hand_cancel']['root_reported_use_ms']==500
    config=json.loads((root/'baseline.json').read_text())
    assert config['version']==list(VERSION)
    assert receipt['source_trees']=={side:fingerprint(root/relative)[0] for side,relative in config['runtime'].items()}
    return receipt

def main():
    validate_local_pending_receipt()
    previous(expected_version=VERSION)
    for script in ('test_g66_local_release_receipt.py','test_held_motion_expression.py','test_seasoning_animation.py','test_seasoning_sprinkle_anchor.py','test_secret_held_owner_context.py'):
        subprocess.run([sys.executable,str(ROOT/'development/gameplay_core'/script)],cwd=ROOT,check=True)
    for generator in ('build_seasoning_held.py','build_player_extensions.py','build_secret_held.py','build_eating_motion.py'):
        subprocess.run([sys.executable,str(ROOT/'tools'/generator),'--check'],cwd=ROOT,check=True)
    subprocess.run(['node','--test','development/gameplay_core/test_seasoning_motion_runtime.mjs'],cwd=ROOT,check=True)
    print('G66 source gate PASS; actual bounded6504 owner-context/recipe/cancel evidence only; lower-food crop, TP/ALT, continuous eating/full Java/family admission remain pending')
if __name__=='__main__':main()
