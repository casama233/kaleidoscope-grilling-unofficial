from __future__ import annotations
import hashlib,json,sys,zipfile
from pathlib import Path

EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'
EMPTY='kaleidoscope_cookery:oil_pot'
FILLED='kaleidoscope_cookery:oil_pot_filled'
COUNT_KEY='kc_oil_count'

def main():
 if len(sys.argv)!=2:
  raise SystemExit('usage: verify_a2730_cookery_contract.py <Cookery 1.0.6 mcaddon>')
 p=Path(sys.argv[1]);got=hashlib.sha256(p.read_bytes()).hexdigest()
 assert got==EXPECTED_SHA,(got,EXPECTED_SHA)

 with zipfile.ZipFile(p) as z:
  item_docs={}
  scripts={}
  for name in z.namelist():
   if '[BP]/items/' in name and name.endswith('.json'):
    try:
     doc=json.loads(z.read(name).decode('utf-8-sig'))
     ident=doc.get('minecraft:item',{}).get('description',{}).get('identifier')
     if ident in (EMPTY,FILLED):item_docs[ident]=(name,doc)
    except Exception:pass
   if '[BP]/scripts/' in name and name.endswith('.js'):
    try:scripts[name]=z.read(name).decode('utf-8')
    except UnicodeDecodeError:pass

 assert set(item_docs)=={EMPTY,FILLED},item_docs.keys()
 joined='\n'.join(scripts.values())
 assert COUNT_KEY in joined,'Cookery host no longer exposes kc_oil_count; re-audit adapter'
 owners=[name for name,s in scripts.items() if COUNT_KEY in s]
 assert owners,'missing count-key owner'
 assert '256' in joined,'Cookery host no longer contains native 256-point oil capacity; re-audit adapter'
 assert 'kaleidoscope_grilling:oil_type' not in joined

 print('A2.7.30 Cookery 1.0.6 oil-pot host contract: PASS')
 print('empty item:',item_docs[EMPTY][0])
 print('filled item:',item_docs[FILLED][0])
 print('count key owners:',','.join(owners[:12]))

if __name__=='__main__':
 main()
