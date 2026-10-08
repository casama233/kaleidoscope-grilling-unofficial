"""Existing stale full bottles refresh derived lore only on normal pickup."""
from verify_a28111 import main as previous
def main():
    previous(expected_version=(2,8,112))
    print('G112 pickup compatibility source gates PASS; full native candidate acceptance remains pending')
if __name__=='__main__':main()
