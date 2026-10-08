"""Current completion, finish feedback and retained seasoning lore."""
from pathlib import Path
import subprocess
from verify_a28109 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main(expected_version=(2,8,110)):
    previous(expected_version=expected_version)
    subprocess.run(['node','--test','development/gameplay_core/test_seasoning_ingredient_lore.mjs'],cwd=ROOT,check=True)
if __name__=='__main__':main()
