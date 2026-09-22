from __future__ import annotations
import hashlib,urllib.request,json

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
ADV={
 'looking_the_part':('15b01e508c0dcde6e3a55fbfedb7b0f7656dacc6','human_fireworks','task',10),
 'gleaming_with_oil':('5c9227d082047e381a1c7b53db7d9592dd46cb19','looking_the_part','task',10),
 'three_flavors_base':('dd6b6b0984fa4db3bf7b7ee6ed7f35bc86f5ff13','gleaming_with_oil','task',10),
 'world_in_a_bottle':('86bb4f0641c115e0cd8c599a99c54c4aa9743785','three_flavors_base','goal',25),
 'eat_it_hot':('92aac6d8b4c448c3ed95f35436bacbfebe696c50','gleaming_with_oil','goal',25),
 'neat_and_orderly':('f8fc42707a62b4469f4327af45588fa90b3a24d7','better_write_it_down','goal',25),
}
MOD_ADV=('neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModAdvancements.java',
 '2791f158caf5885946d377da0b2a3686dcc89146')

def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.56-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:return r.read()

def main():
 p,sha=MOD_ADV;data=fetch(p);assert git_blob(data)==sha
 s=data.decode('utf-8')
 for token in (
  'skewerCompleted(Player player)','award(p, "looking_the_part")',
  'oiled(Player player)','award(p, "gleaming_with_oil")',
  'seasoningAdded(Player player, List<String> ingredients)',
  'award(p, "three_flavors_base")','ingredients.size() >= 8','award(p, "world_in_a_bottle")',
  'FoodState.isHot(stack, player.level())','path.startsWith("grilled_") || path.equals("secret_skewer")',
  'award(player, "eat_it_hot")','event.getPlacedBlock().is(ModBlocks.ADVANCED_RACK.get())',
  'award(player, "neat_and_orderly")'
 ):assert token in s,token
 for id,(sha,parent,frame,xp) in ADV.items():
  data=fetch('common/src/main/resources/data/kaleidoscope_grilling/advancement/'+id+'.json')
  assert git_blob(data)==sha,(id,git_blob(data),sha)
  d=json.loads(data)
  assert d['parent']=='kaleidoscope_grilling:'+parent,(id,d['parent'])
  assert d['display']['frame']==frame,(id,d['display']['frame'])
  assert d['display']['show_toast'] is True and d['display']['announce_to_chat'] is True
  assert d['rewards']['experience']==xp,(id,d['rewards']['experience'])
 print('A2.7.56 pinned Java event advancement contract: PASS')

if __name__=='__main__':main()
