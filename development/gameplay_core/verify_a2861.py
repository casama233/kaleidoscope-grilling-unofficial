"""Client held-content and observer animation regression gate; native evidence separate."""
from pathlib import Path
import subprocess
from verify_a2860 import main as previous

def main():
    previous()
    root=Path(__file__).resolve().parents[2]
    subprocess.run(['python3','development/gameplay_core/test_eating_observer_projection.py'],cwd=root,check=True)
    subprocess.run(['node','--test','development/gameplay_core/test_eating_native_completion.mjs'],cwd=root,check=True)
    subprocess.run(['node','--test','development/gameplay_core/test_bottle_held_visual.mjs','development/gameplay_core/test_seasoning_native_storage.mjs'],cwd=root,check=True)
    subprocess.run(['python3','-B','-m','unittest','test_bottle_visual_assets','test_native_bottle_fp'],cwd=root/'development/gameplay_core',check=True)
    for generator in ['a2770_placed_visual_assets.py','a2861_bottle_held_visual_assets.py']:
        subprocess.run(['python3','development/gameplay_core/'+generator,'--check'],cwd=root,check=True)
    print('A2.8.61 observer projection and bottle contents regressions PASS; native acceptance separate')

if __name__=='__main__':main()
