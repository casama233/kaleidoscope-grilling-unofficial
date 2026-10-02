"""Ingredient metadata and recipe-book parity; no simulated-player acceptance."""
from pathlib import Path
import subprocess
from verify_a2825 import main as baseline
ROOT=Path(__file__).resolve().parents[2]
def main():
    baseline()
    subprocess.run(['node','--test','development/gameplay_core/test_skewer_item_snapshot.mjs','development/gameplay_core/test_recipe_book_safety.mjs','development/gameplay_core/test_food_snapshot.mjs'],cwd=ROOT,check=True)
    subprocess.run(['python','tools/build_vanilla_food_nutrition.py','--check'],cwd=ROOT,check=True)
    print('A2.8.26 metadata/recipe-book regressions PASS; native/client gates remain separate')
if __name__=='__main__':main()
