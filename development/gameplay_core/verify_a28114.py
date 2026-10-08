"""RawMessage lore contract, native storage conservation and exact tested pose."""
from pathlib import Path
import os
import subprocess
import sys
from verify_a28113 import main as previous
from verification_session import SESSION_ENV, current_source_validation_session
ROOT=Path(__file__).resolve().parents[2]
def main():
    previous(expected_version=(2,8,114))
    subprocess.run(['node','--test','development/gameplay_core/test_bottle_raw_lore.mjs'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'development/gameplay_core/test_bottle_pose_review.py'],cwd=ROOT,check=True)
    print('G114 RawMessage and exact pose source gates PASS; native getter and candidate acceptance remain separate')
if __name__=='__main__':
    # Consume the selector before launching tests; they cannot inherit it.
    if os.environ.pop(SESSION_ENV, None) == Path(__file__).name:
        with current_source_validation_session():
            main()
    else:
        main()
