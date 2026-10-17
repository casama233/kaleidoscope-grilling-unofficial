"""Plate transfer failures, strict saved data and source-correct orientation."""
from pathlib import Path
import json,subprocess
from verify_a2832 import main as baseline
ROOT=Path(__file__).resolve().parents[2]
def main():
 baseline()
 subprocess.run(['node','--test','development/gameplay_core/test_plate_transactions.mjs'],cwd=ROOT,check=True)
 block=json.loads((ROOT/'projects/grilling/gameplay_core/behavior_pack/blocks/skewer_plate_block.json').read_text())['minecraft:block']
 assert block['description']['traits']['minecraft:placement_direction']['enabled_states']==['minecraft:cardinal_direction']
 assert len(block['permutations'])==4
 print('A2.8.34 plate transfer, saved-data validation and direction gate PASS; no real-client claim')
if __name__=='__main__':main()
