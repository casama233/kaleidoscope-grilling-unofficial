"""Legal rack state domains; native registration retest remains required."""
from verify_a2875 import main as previous
def main():
 previous(expected_version=(2,8,76))
 print('G76 source checks PASS; native rack registration/interaction acceptance separate')
if __name__=='__main__':main()
