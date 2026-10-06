"""G73 original feedback and provisional native health repair; no full parity claim."""
from pathlib import Path
import subprocess
from verify_a2872 import main as previous
ROOT=Path(__file__).resolve().parents[2]
def main():
 previous(expected_version=(2,8,73))
 subprocess.run(['node','--test','development/gameplay_core/test_ordinary_java_feedback.mjs'],cwd=ROOT,check=True)
if __name__=='__main__':main()
