from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'adv':('common/src/main/resources/data/kaleidoscope_grilling/advancement/mountain_fragrance.json','bf1cdf32fbba604779f7204ba6d63661c1696ac7'),
 'modadv':('neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModAdvancements.java','2791f158caf5885946d377da0b2a3686dcc89146'),
 'leaves':('neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/world/PepperLeavesBlock.java','886ddfc434d38f3df6c440b8ea16c5b7b9569af4'),
 'en':('common/src/main/resources/assets/kaleidoscope_grilling/lang/en_us.json','807c7f40618d409ca17ccb4c0a39e211a84a7b18'),
 'zh':('common/src/main/resources/assets/kaleidoscope_grilling/lang/zh_cn.json','bbc7465f6bf6ab0c698729e9800fbc3c03ae56db'),
}
def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(key):
 path,sha=FILES[key]
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.53-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert blob(v)==sha,(key,blob(v),sha)
 return v

def main():
 adv=json.loads(fetch('adv').decode('utf-8'))
 assert adv['parent']=='kaleidoscope_grilling:human_fireworks'
 d=adv['display']
 assert d['icon']=={'id':'kaleidoscope_grilling:sichuan_pepper'}
 assert d['title']=={'translate':'advancement.kaleidoscope_grilling.mountain_fragrance.title'}
 assert d['description']=={'translate':'advancement.kaleidoscope_grilling.mountain_fragrance.description'}
 assert d['frame']=='goal' and d['show_toast'] is True and d['announce_to_chat'] is True and d['hidden'] is False
 assert adv['criteria']=={'event':{'trigger':'minecraft:impossible'}}
 assert adv['rewards']=={'experience':25}

 mod=fetch('modadv').decode('utf-8')
 assert 'public static void pepperPicked(Player player)' in mod
 assert 'award(p, "mountain_fragrance")' in mod

 leaves=fetch('leaves').decode('utf-8')
 i=leaves.index('protected InteractionResult useWithoutItem')
 chunk=leaves[i:i+1800]
 for token in (
  'state.getValue(HAS_PEPPER)',
  'new ItemStack(ModItems.SICHUAN_PEPPER.get(), 1 + level.random.nextInt(2))',
  'ModAdvancements.pepperPicked(player)',
  'state.setValue(HAS_PEPPER, false)',
  'SoundEvents.SWEET_BERRY_BUSH_PICK_BERRIES',
 ):assert token in chunk,token
 assert chunk.index('popResource(')<chunk.index('ModAdvancements.pepperPicked(player)')<chunk.index('state.setValue(HAS_PEPPER, false)')

 en=json.loads(fetch('en').decode('utf-8'));zh=json.loads(fetch('zh').decode('utf-8'))
 assert en['advancement.kaleidoscope_grilling.mountain_fragrance.title']=='Mountain Fragrance'
 assert en['advancement.kaleidoscope_grilling.mountain_fragrance.description']=='Pick Sichuan pepper from a pepper tree.'
 assert zh['advancement.kaleidoscope_grilling.mountain_fragrance.title']=='山野麻香'
 assert zh['advancement.kaleidoscope_grilling.mountain_fragrance.description']=='从花椒树上摘得花椒。'
 print('A2.7.53 pinned Java Mountain Fragrance advancement contract: PASS')

if __name__=='__main__':main()
