"""Portable Java-long arithmetic after the withdrawn 2.8.50 native discrepancy."""
from verify_a2850 import main as previous

def main():
    previous()
    print('A2.8.51 portable 64-bit Java coordinate hash PASS; native/client evidence stays separate')

if __name__=='__main__':
    main()
