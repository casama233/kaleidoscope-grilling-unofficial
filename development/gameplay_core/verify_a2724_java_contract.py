from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModItems.java':'6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModCreativeTabs.java':'86d28da185347b45319d79596e27a9a3c5713eed',
 'common/src/main/resources/data/kaleidoscope_grilling/recipe/millstone/red_chili_powder.json':'986d4c5930293b380f984f1cecfb0d0d661d5540',
 'common/src/main/resources/data/kaleidoscope_grilling/recipe/secret_chili_oil.json':'a8bf9c6b177a9b943829e68179ff2b06c9123b0e',
 'common/src/main/resources/assets/kaleidoscope_grilling/textures/item/red_chili_powder.png':'57936897efae12b743a539f0bf1dac54d45dda39'
}
def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.24-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert git_blob(v)==FILES[path],(path,git_blob(v),FILES[path]);return v

def main():
 items=fetch(next(p for p in FILES if p.endswith('ModItems.java'))).decode()
 a=items.index('CANOLA_POWDER = ingredient("canola_powder")')
 b=items.index('RED_CHILI_POWDER = ingredient("red_chili_powder")')
 c=items.index('public static final DeferredHolder<Item, Item> ONION =')
 assert a<b<c,(a,b,c)

 creative=fetch(next(p for p in FILES if p.endswith('ModCreativeTabs.java'))).decode()
 assert 'ModItems.ITEMS' in creative and '.getEntries()' in creative
 assert 'added.add(item)' in creative

 mill=json.loads(fetch(next(p for p in FILES if p.endswith('/millstone/red_chili_powder.json'))))
 assert mill=={
  'type':'kaleidoscope_cookery:millstone',
  'ingredient':{'item':'kaleidoscope_cookery:red_chili'},
  'result':{'id':'kaleidoscope_grilling:red_chili_powder','count':1}
 }

 oil=json.loads(fetch(next(p for p in FILES if p.endswith('/secret_chili_oil.json'))))
 assert oil['type']=='minecraft:crafting_shapeless' and oil['category']=='misc'
 assert oil['ingredients']==[
  {'item':'kaleidoscope_grilling:canola_oil_bucket'},
  {'item':'kaleidoscope_grilling:red_chili_powder'},
  {'item':'kaleidoscope_grilling:red_chili_powder'},
  {'item':'kaleidoscope_grilling:red_chili_powder'}
 ]
 assert oil['result']=={'id':'kaleidoscope_grilling:secret_chili_oil_bucket','count':1}
 print('A2.7.24 pinned Java red chili + creative-order contract: PASS')
if __name__=='__main__':main()
