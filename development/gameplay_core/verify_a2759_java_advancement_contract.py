from __future__ import annotations
import hashlib,urllib.request,json

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
ADV={
 'human_fireworks':('763d52bb4ef005ba84ffc51bcf02106eae8475dc','', 'task',10),
 'better_write_it_down':('2c2337b23e55e496127b13a50a36b6b044bba56c','looking_the_part','task',10),
 'a_handful_of_canola':('24f77a53e3a84928595b4e83a29722c5d13d8f98','human_fireworks','task',10),
 'strength_makes_oil':('0561e1065958163269c3c3c1cdadfd4b5998b68f','a_handful_of_canola','goal',25),
 'sweet_potato':('6cd94c428ddddb0ee52926343a75319cdd48fd59','human_fireworks','task',10),
 'nether_taste':('517481f0a4d7e5c6f4a2f8658178bb91b7002a07','human_fireworks','goal',25),
}
MOD=('neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModAdvancements.java','2791f158caf5885946d377da0b2a3686dcc89146')

def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.59-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:return r.read()

def main():
 path,sha=MOD;data=fetch(path);actual=git_blob(data);assert actual==sha,(actual,sha)
 s=data.decode('utf-8')
 for token in (
  'player.tickCount % 20 != 0',
  'has(player, ModBlocks.GRILL_ITEM.get())','award(serverPlayer, "human_fireworks")',
  'ModItems.RAW_SKEWERS.stream().anyMatch','award(serverPlayer, "looking_the_part")',
  'has(player, ModItems.SKEWER_RECIPE_BOOK.get())','award(serverPlayer, "better_write_it_down")',
  'has(player, ModItems.CANOLA_SEEDS.get())','award(serverPlayer, "a_handful_of_canola")',
  'has(player, ModItems.OIL_RESIDUE.get())','award(serverPlayer, "strength_makes_oil")',
  'has(player, ModItems.SWEET_POTATO.get())','award(serverPlayer, "sweet_potato")',
  'player.level().dimension() == Level.NETHER','has(player, ModItems.HOUTTUYNIA.get())',
  'award(serverPlayer, "nether_taste")'
 ):assert token in s,token
 for id,(sha,parent,frame,xp) in ADV.items():
  data=fetch('common/src/main/resources/data/kaleidoscope_grilling/advancement/'+id+'.json')
  actual=git_blob(data);assert actual==sha,(id,actual,sha)
  d=json.loads(data)
  if parent:assert d['parent']=='kaleidoscope_grilling:'+parent,(id,d['parent'])
  else:assert 'parent' not in d,id
  assert d['display']['frame']==frame
  assert d['display']['show_toast'] is True and d['display']['announce_to_chat'] is True
  assert d['rewards']['experience']==xp
 print('A2.7.59 pinned Java inventory advancement contract: PASS')

if __name__=='__main__':main()
