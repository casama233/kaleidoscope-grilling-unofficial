"""Cross-pack contracts, actual target CAS and fresh-host safety; client/vanilla generation are separate."""
from pathlib import Path
import subprocess
from verify_a2848 import main as previous

def main():
    previous()
    root=Path(__file__).resolve().parents[2]
    subprocess.run(['node','--test','development/gameplay_core/test_integration_interfaces.mjs'],cwd=root,check=True)
    print('A2.8.49 integration contracts and failure recovery PASS; no vanilla generation/client acceptance claim')

if __name__=='__main__':
    main()
