from __future__ import annotations
import hashlib,json,sys,zipfile
from pathlib import Path
EXPECTED='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'
NEEDED={
 'kaleidoscope_cookery:oil_pot',
 'kaleidoscope_cookery:oil_pot_filled',
 'kaleidoscope_cookery:iron_kitchen_knife',
 'kaleidoscope_cookery:gold_kitchen_knife',
 'kaleidoscope_cookery:diamond_kitchen_knife',
 'kaleidoscope_cookery:netherite_kitchen_knife',
 'kaleidoscope_cookery:kitchen_shovel',
 'kaleidoscope_cookery:kitchenware_racks',
}
def main():
 p=Path(sys.argv[1]);assert hashlib.sha256(p.read_bytes()).hexdigest()==EXPECTED
 found=set()
 with zipfile.ZipFile(p) as z:
  for name in z.namelist():
   if not name.endswith('.json'):continue
   try:obj=json.loads(z.read(name).decode('utf-8-sig'))
   except:continue
   for root in ('minecraft:item','minecraft:block'):
    ident=obj.get(root,{}).get('description',{}).get('identifier')
    if ident:found.add(ident)
 missing=NEEDED-found
 assert not missing,sorted(missing)
 print('A2.7.45 Cookery 1.0.6 Rack host IDs: PASS')
if __name__=='__main__':main()
