from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
PATH='neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/FortressHouttuyniaHandler.java'
SHA='27af759e8f807e0f21dc887ca53594a596de72c1'
def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 req=urllib.request.Request(BASE+PATH,headers={'User-Agent':'Grilling-A2.7.55-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert blob(v)==SHA,(blob(v),SHA)
 text=v.decode('utf-8')
 for token in (
  'ResourceLocation.withDefaultNamespace("chests/nether_bridge")',
  'setRolls(UniformGenerator.between(1, 2))',
  'LootItemRandomChanceCondition.randomChance(0.65f)',
  'LootItem.lootTableItem(ModItems.HOUTTUYNIA.get())',
  'SetItemCountFunction.setCount(UniformGenerator.between(1, 3))',
 ):assert token in text,token
 print('A2.7.55 pinned Java Fortress Houttuynia Loot contract: PASS')
if __name__=='__main__':main()
