from __future__ import annotations
import hashlib,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'items':('neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModItems.java','6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a',(
  '"wedding_candy"','new WeddingCandyItem','nutrition(20)','saturationModifier(0.5F)','.alwaysEdible()','grillingEffect("invincible")')),
 'item':('neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/food/WeddingCandyItem.java','5c1037e0c9e97583eaa8ef852327b0c4e3d2f914',(
  'private static final int EFFECT_DURATION = 15 * 20;','finishUsingItem','new MobEffectInstance(holder, EFFECT_DURATION)','wedding_candy." + line')),
 'handler':('neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/event/WeddingCandyHandler.java','310f5bd4d49bd2bbd6fbada87a51677ef7d4636a',(
  'ZoneId.of("Asia/Shanghai")','date.getYear() == 2026','date.getMonth() == Month.SEPTEMBER','date.getDayOfMonth() >= 1','date.getDayOfMonth() <= 12','seconds < amount * 60','new ItemStack(ModItems.WEDDING_CANDY.get(), amount)','ModAdvancements.weddingCandy(player)')),
 'advancement':('common/src/main/resources/data/kaleidoscope_grilling/advancement/wedding_candy.json','22f03c57420d1038767d53830eeca974fea70cec',(
  '"id": "kaleidoscope_grilling:wedding_candy"','"hidden": true','"experience": 50')),
}
TEXTURE=('common/src/main/resources/assets/kaleidoscope_grilling/textures/item/wedding_candy.png','d7ca9f5dfa61d6658372d8e181283fb5bf756d78')

def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def get(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.47-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:return r.read()

def main():
 for name,(path,expected,tokens) in FILES.items():
  data=get(path);actual=blob(data);assert actual==expected,(name,actual,expected)
  text=data.decode('utf-8')
  for token in tokens:assert token in text,(name,token)
 path,expected=TEXTURE;data=get(path);assert blob(data)==expected,(blob(data),expected)
 print('A2.7.47 pinned Java Wedding Candy contract: PASS')

if __name__=='__main__':main()
