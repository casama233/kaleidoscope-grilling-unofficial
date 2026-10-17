from __future__ import annotations
import hashlib,re,sys,zipfile
from pathlib import Path

EXPECTED_SHA='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'

def main():
 if len(sys.argv)!=2:raise SystemExit('usage: verify_a279_cookery_contract.py <Cookery 1.0.6 mcaddon>')
 p=Path(sys.argv[1]);got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==EXPECTED_SHA,(got,EXPECTED_SHA)
 with zipfile.ZipFile(p) as z:
  direct=next(n for n in z.namelist() if n.endswith('[BP]/scripts/custom_components/blocks/directStation.js'))
  data=next(n for n in z.namelist() if n.endswith('[BP]/scripts/data/stationRecipes.js'))
  s=z.read(direct).decode('utf-8');d=z.read(data).decode('utf-8')
 required=[
  '"minecraft:beef":0',
  'function k(b){return `kc_station:${b.dimension.id}:${b.x},${b.y},${b.z}`;}',
  'const r=BOARD_RECIPES[id]||getExtensionBoardRecipe(id);',
  'save(b,{input:id,cuts:0,max:r.cuts,result:{id:r.result,count:r.count},extension:!!r.extension})',
  'if((d.cuts||0)>=d.max){pop(b,d.result.id,d.result.count);save(b,{})',
 ]
 for token in required:assert token in s,token
 assert re.search(r'"minecraft:beef":\{"result":"kaleidoscope_cookery:raw_cow_offal","count":2,"cuts":4\}',d)
 print('A2.7.9 Cookery 1.0.6 beef-board contract: PASS')
if __name__=='__main__':main()
