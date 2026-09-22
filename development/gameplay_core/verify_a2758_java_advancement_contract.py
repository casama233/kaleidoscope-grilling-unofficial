from __future__ import annotations
import hashlib,urllib.request,json

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
ADV={
 'mental_preparation_failed':('a86a14fe9c8fa758b54829eb58070cbfdce28f47','looking_the_part','challenge',50,False),
 'metallic_taste':('97947340d24335e3d5cf6b7bce95f6f4ac4f05ef','world_in_a_bottle','goal',25,False),
 'taste_of_dragon':('fef4b80df6ab3ef077812f883db5ad1e4d459d78','world_in_a_bottle','goal',25,False),
 'metal_tolerance_failed':('a1c668a45e29c3ebf35e6a1d79fe3aa4a4b7c8c3','metallic_taste','challenge',50,False),
 'strongest_shield':('4725a78168ec357d685691e5e8ad8d563eaf3107','fireworks_feast','challenge',50,False),
 'strongest_spear':('9ea3f2bb265709e8ca56d7dd15ad1adf34e6a17d','fireworks_feast','challenge',50,False),
 'wedding_candy':('22f03c57420d1038767d53830eeca974fea70cec','human_fireworks','challenge',50,True),
}
FILES={
 'mod_adv':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModAdvancements.java',
  '2791f158caf5885946d377da0b2a3686dcc89146',
  (
   'path.equals("raw_caterpillar_skewer")','award(player, "mental_preparation_failed")',
   'seasoningFinished(LivingEntity entity, List<String> ingredients)',
   'award(player, "metallic_taste")','award(player, "taste_of_dragon")',
   'heavyMetalBlocked(LivingEntity entity)','award(player, "metal_tolerance_failed")',
   'strongestShield(LivingEntity entity)','award(player, "strongest_shield")',
   'strongestSpear(LivingEntity entity)','award(player, "strongest_spear")',
   'weddingCandy(ServerPlayer player)','award(player, "wedding_candy")',
  )
 ),
 'pending':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/seasoning/PendingSeasoningItem.java',
  '8d4c10c2cda18330a4b77d475a8b7be405fa8116',
  ('ModAdvancements.seasoningFinished(entity, ingredients)','SeasoningData.setRandomVariant(result)')
 ),
 'advanced':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/seasoning/AdvancedSeasoningHandler.java',
  'c934a21565d450bbb35841272671d4f0ba18eddd',
  ('entity.hasEffect(ModEffects.HEAVY_METAL_POISONING)','ModAdvancements.heavyMetalBlocked(entity)')
 ),
 'cursed':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/CursedSkewerItem.java',
  '90fc712c19e6f292825faffafffb8b9270ef7675',
  ('boolean blocked = challenged && entity.getRandom().nextBoolean()','ModAdvancements.strongestShield(entity)',
   'if (challenged) ModAdvancements.strongestSpear(entity)')
 ),
 'wedding':(
  'neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/event/WeddingCandyHandler.java',
  '310f5bd4d49bd2bbd6fbada87a51677ef7d4636a',
  ('ModAdvancements.weddingCandy(player)','data.putString(CLAIMED_DATE, today)')
 ),
}

def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.58-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:return r.read()

def main():
 for name,(path,sha,tokens) in FILES.items():
  data=fetch(path);actual=git_blob(data);assert actual==sha,(name,actual,sha)
  s=data.decode('utf-8')
  for token in tokens:assert token in s,(name,token)
 for id,(sha,parent,frame,xp,hidden) in ADV.items():
  data=fetch('common/src/main/resources/data/kaleidoscope_grilling/advancement/'+id+'.json')
  actual=git_blob(data);assert actual==sha,(id,actual,sha)
  d=json.loads(data)
  assert d['parent']=='kaleidoscope_grilling:'+parent,(id,d['parent'])
  assert d['display']['frame']==frame
  assert d['display']['hidden'] is hidden
  assert d['display']['show_toast'] is True and d['display']['announce_to_chat'] is True
  assert d['rewards']['experience']==xp
 print('A2.7.58 pinned Java challenge advancement contract: PASS')

if __name__=='__main__':main()
