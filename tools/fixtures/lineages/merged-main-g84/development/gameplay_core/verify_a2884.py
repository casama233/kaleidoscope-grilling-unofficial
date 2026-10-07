"""Native projectile-responsible source repair, preserving G83 ownership guards."""
from verify_a2883 import main as previous
def main():
    previous(expected_version=(2,8,84))
if __name__=='__main__':
    main()
