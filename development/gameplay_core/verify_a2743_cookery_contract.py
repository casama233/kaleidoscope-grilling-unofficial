from __future__ import annotations
import hashlib,json,sys,zipfile
from pathlib import Path
EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def main():
 if len(sys.argv)!=2:raise SystemExit('usage: verify_a2743_cookery_contract.py <Cookery 1.0.6 mcaddon>')
 p=Path(sys.argv[1]);got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==EXPECTED_SHA,(got,EXPECTED_SHA)
 matches=[]
 with zipfile.ZipFile(p) as z:
  for name in z.namelist():
   if not name.lower().endswith('.json') or '/items/' not in name.replace('\\','/').lower():continue
   try:doc=json.loads(z.read(name).decode('utf-8-sig'))
   except Exception:continue
   item=doc.get('minecraft:item',{}) if isinstance(doc,dict) else {}
   ident=item.get('description',{}).get('identifier') if isinstance(item,dict) else None
   if ident=='kaleidoscope_cookery:tomato':matches.append(name)
 assert matches,'Cookery 1.0.6 tomato item not found'
 print('A2.7.43 Cookery 1.0.6 tomato host contract: PASS')
 print('tomato item:',matches[0])
if __name__=='__main__':main()
