from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'moditems':('forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModItems.java','a359de5425e3008e728e4790b7bd1b0fe92fbabf'),
 'sugared':('common/src/main/resources/data/kaleidoscope_grilling/recipe/sugared_tomato.json','bd5dbd8d3ed3788e3637e3766d04243c32808cec'),
 'pepper':('common/src/main/resources/data/kaleidoscope_grilling/recipe/pepper_honey.json','2eeb3b30c9fd3090605c6c39c681e4d0d0b18a2e'),
}
def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(key):
 path,sha=FILES[key]
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.41-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert blob(v)==sha,(key,blob(v),sha)
 return v

def main():
 src=fetch('moditems').decode('utf-8')
 i=src.index('SUGARED_TOMATO');s=src[i:i+900]
 assert 'nutrition(6)' in s and 'saturationMod(0.65F)' in s
 i=src.index('PEPPER_HONEY');p=src[i:i+1000]
 assert 'nutrition(4)' in p and 'saturationMod(0.25F)' in p
 assert 'grillingEffect("numb")' in p and '1200' in p

 sug=json.loads(fetch('sugared').decode('utf-8'))
 assert sug['type']=='minecraft:crafting_shapeless'
 assert sug['ingredients']==[{'tag':'c:crops/tomato'},{'item':'minecraft:sugar'}]
 assert sug['result']=={'id':'kaleidoscope_grilling:sugared_tomato','count':1}
 pep=json.loads(fetch('pepper').decode('utf-8'))
 assert pep['type']=='minecraft:crafting_shapeless'
 assert pep['ingredients']==[
  {'item':'kaleidoscope_grilling:sichuan_pepper'},
  {'item':'kaleidoscope_grilling:sichuan_pepper'},
  {'item':'kaleidoscope_grilling:sichuan_pepper'},
  {'item':'minecraft:honey_bottle'}
 ]
 assert pep['result']=={'id':'kaleidoscope_grilling:pepper_honey','count':1}
 print('A2.7.41 pinned Java food/recipe contract: PASS')
if __name__=='__main__':main()
