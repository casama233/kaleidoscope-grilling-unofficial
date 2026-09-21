from __future__ import annotations
import hashlib,json,sys,zipfile
from pathlib import Path

EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def main():
 if len(sys.argv)!=2:raise SystemExit('usage: verify_a2712_cookery_contract.py <Cookery 1.0.6 mcaddon>')
 p=Path(sys.argv[1]);got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==EXPECTED_SHA,(got,EXPECTED_SHA)
 with zipfile.ZipFile(p) as z:
  candidates=[n for n in z.namelist() if n.endswith('/items/raw_cow_offal.json') or n.endswith('[BP]/items/raw_cow_offal.json')]
  assert len(candidates)==1,candidates
  doc=json.loads(z.read(candidates[0]).decode('utf-8-sig'))
 item=doc['minecraft:item']
 assert item['description']['identifier']=='kaleidoscope_cookery:raw_cow_offal'
 print('A2.7.12 Cookery 1.0.6 raw_cow_offal item contract: PASS')

if __name__=='__main__':main()
