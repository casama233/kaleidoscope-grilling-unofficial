from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'bottle_hud':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/seasoning/SeasoningBottleHud.java',
  '01856ffcce5dcbeaf304f0f8adffc8a4f1daf667',
  (
   'Component.translatable("hud.kaleidoscope_grilling.seasoning.title")',
   'SeasoningBottleBlockEntity.CAPACITY - values.size()',
   'REQUIRED.forEach(id -> counts.put(id, 0));',
   'List<Component> effects = SeasoningEffects.describe(values);',
   'Component.translatable("hud.kaleidoscope_grilling.seasoning.missing")',
   'Component.translatable("hud.kaleidoscope_grilling.seasoning.no_effect")',
  )
 ),
 'jade_provider':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/compat/jade/SeasoningBottleProvider.java',
  '57a0f4d20c6f4c961a9d4f88cb25b0d335687c9b',
  (
   'bottle.count() != 1',
   'SeasoningData.MAX_USES - SeasoningData.getUses(bottle.top())',
   '"jade.kaleidoscope_grilling.seasoning.uses"',
   '"jade.kaleidoscope_grilling.seasoning.capacity"',
  )
 ),
 'block_entity':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/seasoning/SeasoningBottleBlockEntity.java',
  'c43cc4e4b8871f345dbe18d8d16bbcae2830bd8d',
  (
   'public static final int CAPACITY = 8;',
   'public static final int MAX_BOTTLES = 4;',
   'public List<String> ingredients()',
   'public boolean isFinished()',
   'public int variant()',
  )
 ),
 'seasoning_data':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/seasoning/SeasoningData.java',
  '435d3689b7bb1143d4cca0b0978c053c5ef61413',
  (
   'public static final int MAX_USES = 16;',
   'clamp(data.copyTag().getInt(VARIANT_KEY), 0, 7)',
   'clamp(data.copyTag().getInt(USES_KEY), 0, MAX_USES)',
  )
 ),
 'effects':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/seasoning/SeasoningEffects.java',
  'f379ab061b4d9e4421d50cdc0546fbadceced387',
  (
   'List.of("speed", "strength", "duration", "totem", "vitality")',
   'seasoningCount(values, "numbness")',
   'pepper >= 4 ? "numbness" : "numbness_pending"',
  )
 ),
}

def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 for name,(path,expected,tokens) in FILES.items():
  req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.43-contract/1'})
  with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
  actual=git_blob(data);assert actual==expected,(name,actual,expected)
  s=data.decode('utf-8')
  for token in tokens:assert token in s,(name,token)
 print('A2.7.43 pinned Java seasoning HUD contract: PASS')

if __name__=='__main__':main()
