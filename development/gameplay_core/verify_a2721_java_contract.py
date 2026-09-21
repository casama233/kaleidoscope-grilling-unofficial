from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModItems.java':'6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/food/FlavorFoodItem.java':'ace726a35ccbafbbb65202876eb9279332a5e9fe',
 'common/src/main/resources/data/kaleidoscope_grilling/tags/item/ingredients/chicken_wings.json':'308ad7c5d7cc2d5137aa07a0381e785ab6a5caad',
 'common/src/main/resources/data/kaleidoscope_grilling/recipe/roasted_chicken_wing.json':'7227f7b48f3f5edf02b5c26e773ab17e75a262f4',
 'common/src/main/resources/data/kaleidoscope_grilling/recipe/roasted_chicken_wing_smoking.json':'a1eb36ba0ee1cf419a2b5b80035f499061f2f233',
 'common/src/main/resources/data/kaleidoscope_grilling/recipe/roasted_chicken_wing_campfire.json':'38e901f9f4d4232722e87b557ff1133e81daa1cf'
}
def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.21-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert git_blob(v)==FILES[path],(path,git_blob(v),FILES[path]);return v

def main():
 items=fetch(next(p for p in FILES if p.endswith('ModItems.java'))).decode()
 start=items.index('public static final DeferredHolder<Item, Item> ROASTED_CHICKEN_WING =')
 chunk=items[start:start+700]
 for token in ('new FlavorFoodItem(','.nutrition(5)','.saturationModifier(0.12F)','tooltip.kaleidoscope_grilling.roasted_chicken_wing.maxim'):assert token in chunk,token

 flavor=fetch(next(p for p in FILES if p.endswith('FlavorFoodItem.java'))).decode()
 assert 'CuisineQualitySupport.foodProperties' in flavor
 assert 'CuisineQualitySupport.appendTooltip' in flavor

 tag=json.loads(fetch(next(p for p in FILES if p.endswith('ingredients/chicken_wings.json'))))
 assert tag=={'replace':False,'values':['kaleidoscope_grilling:chicken_wing']}

 expected={
  'roasted_chicken_wing.json':('minecraft:smelting',200,0.35),
  'roasted_chicken_wing_smoking.json':('minecraft:smoking',100,0.35),
  'roasted_chicken_wing_campfire.json':('minecraft:campfire_cooking',600,0.35)
 }
 for name,(typ,ticks,xp) in expected.items():
  path=next(p for p in FILES if p.endswith('/'+name));doc=json.loads(fetch(path))
  assert doc['type']==typ and doc['category']=='food'
  assert doc['cookingtime']==ticks and doc['experience']==xp
  assert doc['ingredient']=={'tag':'kaleidoscope_grilling:ingredients/chicken_wings'}
  assert doc['result']=={'id':'kaleidoscope_grilling:roasted_chicken_wing'}
 print('A2.7.21 pinned Java roasted chicken wing contract: PASS')
if __name__=='__main__':main()
