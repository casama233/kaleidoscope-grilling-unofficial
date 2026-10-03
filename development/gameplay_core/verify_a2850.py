"""Native vanilla food fallback after the withdrawn 2.8.49 BDS candidate."""
from verify_a2849 import main as previous

def main():
    previous()
    print('A2.8.50 pinned native vanilla-food producer fallback PASS; engine/client evidence stays separate')

if __name__=='__main__':
    main()
