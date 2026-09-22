from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'items':('neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModItems.java','6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a'),
 'potato_exact':('common/src/main/resources/data/kaleidoscope_grilling/recipe/stockpot/potato_beef_stew.json','7596270b1a876561e70fec6afa8966d3be08c9be'),
 'potato_flex':('common/src/main/resources/data/kaleidoscope_grilling/recipe/flex_stockpot/potato_beef_stew.json','30bf95328b2648c9e4c2d3e9f22352c6966f5c1d'),
 'porridge_exact':('common/src/main/resources/data/kaleidoscope_grilling/recipe/stockpot/red_sweet_potato_porridge.json','b8fed24b8ea41e93fdcb4611dbb61a0b12301c4c'),
 'porridge_flex':('common/src/main/resources/data/kaleidoscope_grilling/recipe/flex_stockpot/red_sweet_potato_porridge.json','7329e081c912aaa32cd3d84e50994eff471cdb2b'),
 'noodles_exact':('common/src/main/resources/data/kaleidoscope_grilling/recipe/stockpot/sour_spicy_noodles.json','0726d66b1e7a004826eb108dc078ef0f3a490361'),
 'noodles_flex':('common/src/main/resources/data/kaleidoscope_grilling/recipe/flex_stockpot/sour_spicy_noodles.json','4a6693123f50e07b078d858c23b3a7dba84956f9'),
 'beef_tag':('common/src/main/resources/data/kaleidoscope_grilling/tags/item/ingredients/beef_chunks.json','e10de3d77c34004be696c698486629cb83cc67cf'),
 'carrot_tag':('common/src/main/resources/data/kaleidoscope_grilling/tags/item/ingredients/carrot_dice.json','14ff7804097460749069e81694d5d4aec23278f9'),
 'onion_tag':('common/src/main/resources/data/kaleidoscope_grilling/tags/item/ingredients/onions.json','38c13e1a55a253306b87c3e5c3795f832b9e2675'),
 'sweet_tag':('common/src/main/resources/data/kaleidoscope_grilling/tags/item/ingredients/sweet_potatoes.json','e37d8276f40197bd99d85733b6cb3ec9d6a9b44e'),
 'leaf_tag':('common/src/main/resources/data/kaleidoscope_grilling/tags/item/ingredients/leafy_greens.json','0a48318514e8fa269cf8c6a1aa9a86b520f07e70'),
}
def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(key):
 path,sha=FILES[key]
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.52-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert blob(v)==sha,(key,blob(v),sha)
 return v
def j(key):return json.loads(fetch(key).decode('utf-8'))

def main():
 src=fetch('items').decode('utf-8')
 for token in (
  'dish("potato_beef_stew", 12, 0.9F)',
  '.nutrition(14)','.saturationModifier(0.071429F)',
  'cookeryEffect("flatulence")','cookeryEffect("warmth")','900',
  '"sour_spicy_noodles"','.nutrition(10)','.saturationModifier(0.6F)',
 ):assert token in src,token

 assert j('beef_tag')['values']==['kaleidoscope_grilling:beef_chunks']
 assert j('carrot_tag')['values']==['kaleidoscope_grilling:carrot_dice']
 assert j('onion_tag')['values']==['#c:crops/onion']
 assert j('sweet_tag')['values']==['kaleidoscope_grilling:sweet_potato']
 assert j('leaf_tag')['values']==['kaleidoscope_cookery:lettuce']

 p=j('potato_exact');assert p['type']=='kaleidoscope_cookery:stockpot'
 assert p['result']=={'id':'kaleidoscope_grilling:potato_beef_stew','count':1}
 assert len(p['ingredients'])==5
 p=j('potato_flex');assert p['type']=='kaleidoscope_cookery:flex_stockpot' and p['soup_base']=='minecraft:water' and p['time']==300
 assert p['carrier']=={'item':'minecraft:bowl'}

 p=j('porridge_exact');assert p['type']=='kaleidoscope_cookery:stockpot' and len(p['ingredients'])==6
 p=j('porridge_flex');assert p['type']=='kaleidoscope_cookery:flex_stockpot' and len(p['ingredients'])==2

 for key in ('noodles_exact','noodles_flex'):
  p=j(key)
  assert p['neoforge:conditions']==[{'type':'neoforge:mod_loaded','modid':'kaleidoscope_tavern'}]
  assert p['ingredients'][0]=={'item':'kaleidoscope_tavern:vinegar'}
 assert j('noodles_exact')['type']=='kaleidoscope_cookery:stockpot'
 assert j('noodles_flex')['type']=='kaleidoscope_cookery:flex_stockpot'

 print('A2.7.52 pinned Java Stockpot food/recipe/tag contract: PASS')
if __name__=='__main__':main()
