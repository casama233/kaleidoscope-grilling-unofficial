from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
PATH='neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/VillagePepperLootHandler.java'
SHA='2ec1ae96d8bb7236463eff07127403da45bc8246'

def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 req=urllib.request.Request(BASE+PATH,headers={'User-Agent':'Grilling-A2.7.54-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert blob(v)==SHA,(blob(v),SHA)
 text=v.decode('utf-8')
 for token in (
  'VILLAGE_CHEST_PREFIX = "chests/village/"',
  '"minecraft".equals(name.getNamespace())',
  'name.getPath().startsWith(VILLAGE_CHEST_PREFIX)',
  'LootItemRandomChanceCondition.randomChance(0.4F)',
  'LootItem.lootTableItem(ModItems.SICHUAN_PEPPER.get())',
  'UniformGenerator.between(3.0F, 10.0F)',
  'LootItemRandomChanceCondition.randomChance(0.2F)',
  'LootItem.lootTableItem(ModBlocks.PEPPER_SAPLING_ITEM.get())',
 ):assert token in text,token
 assert text.count('.setRolls(ConstantValue.exactly(1.0F))')==2
 print('A2.7.54 pinned Java Village Pepper Loot contract: PASS')

if __name__=='__main__':main()
