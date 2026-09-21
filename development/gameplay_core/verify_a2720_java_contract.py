from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModItems.java':'6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/food/EffectFoodItem.java':'273712fad21b79049c5db3b16fdeca8076a8ebad',
 'common/src/main/resources/data/kaleidoscope_grilling/tags/item/ingredients/sweet_potatoes.json':'e37d8276f40197bd99d85733b6cb3ec9d6a9b44e',
 'common/src/main/resources/data/kaleidoscope_grilling/recipe/roasted_sweet_potato.json':'955b5e820c82345ce9c1f2b4defde40161098ca5',
 'common/src/main/resources/data/kaleidoscope_grilling/recipe/roasted_sweet_potato_smoking.json':'9c275528d8bb4dadec89bc64ec97a4c24ada4ca7',
 'common/src/main/resources/data/kaleidoscope_grilling/recipe/roasted_sweet_potato_campfire.json':'e455f4bedef55ccc8d291100765cebd838b7d5cd'
}
def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.20-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert git_blob(v)==FILES[path],(path,git_blob(v),FILES[path]);return v
def main():
 items=fetch(next(p for p in FILES if p.endswith('ModItems.java'))).decode()
 start=items.index('public static final DeferredHolder<Item, Item> ROASTED_SWEET_POTATO =')
 chunk=items[start:start+900]
 for token in (
  '"roasted_sweet_potato"','new EffectFoodItem(','.nutrition(6)','.saturationModifier(0.2F)',
  'cookeryEffect("warmth")','600','"tooltip.kaleidoscope_grilling.roasted_sweet_potato.maxim"'
 ):assert token in chunk,token

 effect=fetch(next(p for p in FILES if p.endswith('EffectFoodItem.java'))).decode()
 assert 'CuisineQualitySupport.effectDuration(s, duration)' in effect
 assert 'new MobEffectInstance(h, effectDuration)' in effect

 tag=json.loads(fetch(next(p for p in FILES if p.endswith('ingredients/sweet_potatoes.json'))))
 assert tag=={'replace':False,'values':['kaleidoscope_grilling:sweet_potato']}

 expected={
  'roasted_sweet_potato.json':('minecraft:smelting',200,.35),
  'roasted_sweet_potato_smoking.json':('minecraft:smoking',100,.35),
  'roasted_sweet_potato_campfire.json':('minecraft:campfire_cooking',600,.35)
 }
 for path in [p for p in FILES if '/recipe/roasted_sweet_potato' in p]:
  data=json.loads(fetch(path));name=path.rsplit('/',1)[-1];typ,time,xp=expected[name]
  assert data['type']==typ and data['category']=='food'
  assert data['cookingtime']==time and abs(data['experience']-xp)<1e-9
  assert data['ingredient']=={'tag':'kaleidoscope_grilling:ingredients/sweet_potatoes'}
  assert data['result']=={'id':'kaleidoscope_grilling:roasted_sweet_potato'}
 print('A2.7.20 pinned Java roasted sweet potato contract: PASS')
if __name__=='__main__':main()
