from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModItems.java':'6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/food/EffectFoodItem.java':'273712fad21b79049c5db3b16fdeca8076a8ebad',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/food/ColdHouttuyniaCraftingRecipe.java':'e309072bf8b8398317f4b312df59726159848fbe',
 'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/oil/OilPotCompat.java':'4264ab947a4222784151fbd50ae84a1a8037d491',
 'common/src/main/resources/data/kaleidoscope_grilling/tags/item/ingredients/houttuynia.json':'05ca6efd89873ba77e4257404337212c0a416ff1',
 'common/src/main/resources/data/kaleidoscope_grilling/recipe/cold_houttuynia.json':'58087181db700f9d5ee8405db63f6333f9d5764c'
}
def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.22-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert git_blob(v)==FILES[path],(path,git_blob(v),FILES[path]);return v

def main():
 items=fetch(next(p for p in FILES if p.endswith('ModItems.java'))).decode()
 start=items.index('public static final DeferredHolder<Item, Item> COLD_HOUTTUYNIA =')
 chunk=items[start:start+850]
 for token in ('new EffectFoodItem(','.nutrition(6)','.saturationModifier(1.0F)','ResourceLocation.withDefaultNamespace("fire_resistance")','1200','tooltip.kaleidoscope_grilling.cold_houttuynia.maxim'):assert token in chunk,token

 effect=fetch(next(p for p in FILES if p.endswith('EffectFoodItem.java'))).decode()
 assert 'CuisineQualitySupport.foodProperties' in effect
 assert 'CuisineQualitySupport.effectDuration' in effect
 assert 'CuisineQualitySupport.appendTooltip' in effect

 recipe=fetch(next(p for p in FILES if p.endswith('ColdHouttuyniaCraftingRecipe.java'))).decode()
 for token in ('countHouttuynia(input) == 3','occupiedSlots(input) == 4','"premium_chili".equals(OilPotCompat.getType(stack))','OilPotCompat.getCount(stack) < 2','OilPotCompat.consume(oilPot, 2)'):assert token in recipe,token

 oil=fetch(next(p for p in FILES if p.endswith('OilPotCompat.java'))).decode()
 assert 'public static final int FLUID_CAPACITY = 64;' in oil
 assert 'if (remaining == 0) setType(stack, "");' in oil

 tag=json.loads(fetch(next(p for p in FILES if p.endswith('ingredients/houttuynia.json'))))
 assert tag=={'replace':False,'values':['kaleidoscope_grilling:houttuynia']}

 stub=json.loads(fetch(next(p for p in FILES if p.endswith('/recipe/cold_houttuynia.json'))))
 assert stub=={'type':'kaleidoscope_grilling:cold_houttuynia','category':'food'}
 print('A2.7.22 pinned Java cold houttuynia contract: PASS')
if __name__=='__main__':main()
