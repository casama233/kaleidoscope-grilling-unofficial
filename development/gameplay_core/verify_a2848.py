"""Feedback release on canonical third-person eating 2.8.47, preserving both gates."""
from pathlib import Path
import subprocess
import sys
from verify_a2847 import main as previous


def main():
    previous()
    root = Path(__file__).resolve().parents[2]
    subprocess.run(['node', '--test', 'development/gameplay_core/test_immersion_feedback.mjs'], cwd=root, check=True)
    subprocess.run([sys.executable, 'tools/build_feedback_particles.py', '--check'], cwd=root, check=True)
    print('A2.8.48 source event and owned single-particle regressions PASS; canonical third-person eating retained; client and saved-world evidence are separate')


if __name__ == '__main__':
    main()
