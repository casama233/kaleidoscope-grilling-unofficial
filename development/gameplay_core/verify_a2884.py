"""Native projectile-responsible source repair, preserving G83 ownership guards."""
from verify_a2883 import main as previous
def main(expected_version=(2,8,84)):
    previous(expected_version=expected_version)
if __name__=='__main__':
    main()
