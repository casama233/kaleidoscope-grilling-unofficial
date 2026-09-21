from __future__ import annotations
import hashlib,json,sys,zipfile
from pathlib import Path

EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'
REQUIRED={'kaleidoscope_cookery:straw_hat','kaleidoscope_cookery:straw_hat_flower'}
def main():
 if len(sys.argv)!=2:raise SystemExit('usage: verify_a2715_cookery_contract.py <Cookery 1.0.6 mcaddon>')
 p=Path(sys.argv[1]);got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==EXPECTED_SHA,(got,EXPECTED_SHA)
 found=set()
 with zipfile.ZipFile(p) as z:
  for name in z.namelist():
   if '[BP]/items/' not in name or not name.endswith('.json'):continue
   try:doc=json.loads(z.read(name).decode('utf-8-sig'))
   except Exception:continue
   ident=doc.get('minecraft:item',{}).get('description',{}).get('identifier')
   if ident in REQUIRED:found.add(ident)
 assert found==REQUIRED,(found,REQUIRED)
 print('A2.7.15 Cookery 1.0.6 straw-hat contract: PASS')
if __name__=='__main__':main()
