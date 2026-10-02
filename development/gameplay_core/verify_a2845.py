from pathlib import Path
import subprocess,json
from verify_a2843 import main as previous
def main():
 previous()
 root=Path(__file__).resolve().parents[2]
 for command in [['node','development/gameplay_core/test_food_finish.mjs'],['python3','tools/build_player_extensions.py','--check'],['python3','tools/build_eating_motion.py','--check'],['python3','tools/build_secret_held.py','--check']]:subprocess.run(command,cwd=root,check=True)
 assert len(json.loads((root/'projects/grilling/gameplay_core/resource_pack/models/entity/secret_held.geo.json').read_text())['minecraft:geometry'])==7
 print('A2845 shared eating, heat, native health and preserved player-frame contracts PASS; client separate')
if __name__=='__main__':main()
