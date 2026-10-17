from __future__ import annotations
import hashlib,json,sys,zipfile
from pathlib import Path

EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'
RED_CHILI='kaleidoscope_cookery:red_chili'

def main():
 if len(sys.argv)!=2:raise SystemExit('usage: verify_a2724_cookery_contract.py <Cookery 1.0.6 mcaddon>')
 p=Path(sys.argv[1]);got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==EXPECTED_SHA,(got,EXPECTED_SHA)
 with zipfile.ZipFile(p) as z:
  texts={};item_ids=set()
  for name in z.namelist():
   if name.endswith('.js') and '[BP]/scripts/' in name:
    try:texts[name]=z.read(name).decode('utf-8')
    except UnicodeDecodeError:pass
   if name.endswith('.json') and '[BP]/items/' in name:
    try:
     doc=json.loads(z.read(name).decode('utf-8-sig'))
     ident=doc.get('minecraft:item',{}).get('description',{}).get('identifier')
     if ident:item_ids.add(str(ident))
    except Exception:pass
 joined='\n'.join(texts.values())
 assert RED_CHILI in item_ids,(RED_CHILI,sorted(x for x in item_ids if 'chili' in x))
 assert 'kaleidoscope_cookery:api_ready' in joined
 assert 'kaleidoscope_cookery:register_recipe' in joined
 candidates=[(name,s) for name,s in texts.items() if 'millstone' in s.lower() and ('register_recipe' in s or 'extension' in s.lower())]
 assert candidates,'Cookery millstone extension path no longer discoverable'
 print('A2.7.24 Cookery 1.0.6 red chili + millstone extension contract: PASS')
 print('millstone extension candidates:',','.join(n for n,_ in candidates[:8]))
if __name__=='__main__':main()
