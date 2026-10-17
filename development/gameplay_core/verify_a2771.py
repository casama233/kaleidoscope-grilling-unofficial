"""Shared Cookery creative groups plus existing gameplay/resource regression gates."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import a2771_shared_creative as catalog
import verify_a2769 as prior

ROOT=Path(__file__).resolve().parents[2]
DEV=Path(__file__).resolve().parent
BP=ROOT/'projects/grilling/gameplay_core/behavior_pack'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--compiled',action='store_true');args=parser.parse_args()
    result=catalog.check()
    from verify_a2766 import check_assets
    assets=check_assets()
    maps=prior.source_guards((2,7,71))
    prior.java_contract()
    for script,extra in (
        ('test_a2771_catalog.py',[]),
        ('test_vibrant_gate.py',[]),
        ('a2764_rebake_skewer_hand_geometry.py',['--check']),
        ('verify_a2761_java_interaction_contract.py',[]),
    ):
        subprocess.run([sys.executable,str(DEV/script),*extra],check=True)
    for test in ('test_a275_core.mjs','test_a276_core.mjs','test_a277_core.mjs','test_a2762_core.mjs','test_a2769_core.mjs'):
        subprocess.run(['node',str(DEV/test)],check=True)
    for path in BP.joinpath('scripts').rglob('*.js'):
        subprocess.run(['node','--check',str(path)],check=True)
    result.update(material_maps_checked=maps,assets=assets,compiled_requested=args.compiled)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
