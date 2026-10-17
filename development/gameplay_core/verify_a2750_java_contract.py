from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'items':('neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/registry/ModItems.java','6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a'),
 'houttuynia':('common/src/main/resources/data/kaleidoscope_grilling/recipe/pot/houttuynia_stir_fried_pork.json','31676dd8c13331aec31560df1028f21aeb77feef'),
 'squid':('common/src/main/resources/data/kaleidoscope_grilling/recipe/pot/green_pepper_squid_tentacles.json','4b7a16790f96ba00e112d3ce94c1492263d703a0'),
 'wings':('common/src/main/resources/data/kaleidoscope_grilling/recipe/pot/braised_chicken_wings.json','3a07fd7c9c9252db9134043b2438e10c46089d0c'),
}
def blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(key):
 path,sha=FILES[key]
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.50-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert blob(v)==sha,(key,blob(v),sha)
 return v

def main():
 src=fetch('items').decode('utf-8')
 for token in (
  'dish("houttuynia_stir_fried_pork", 9, 0.7F)',
  'dish("green_pepper_squid_tentacles", 8, 0.6F)',
  'dish("braised_chicken_wings", 10, 0.8F)',
  '.stacksTo(16)'
 ):assert token in src,token
 expected={
  'houttuynia':[
   {'tag':'kaleidoscope_grilling:ingredients/houttuynia'}]*3+
   [{'item':'minecraft:porkchop'}]*3,
  'squid':[
   {'item':'kaleidoscope_cookery:green_chili'},{'item':'kaleidoscope_cookery:green_chili'},
   {'tag':'kaleidoscope_grilling:ingredients/squid_tentacles'},{'tag':'kaleidoscope_grilling:ingredients/squid_tentacles'},
   {'tag':'kaleidoscope_grilling:ingredients/onions'}],
  'wings':[
   {'tag':'kaleidoscope_grilling:ingredients/chicken_wings'}]*3+
   [{'item':'minecraft:sugar'}]*3,
 }
 results={
  'houttuynia':'kaleidoscope_grilling:houttuynia_stir_fried_pork',
  'squid':'kaleidoscope_grilling:green_pepper_squid_tentacles',
  'wings':'kaleidoscope_grilling:braised_chicken_wings',
 }
 for key in ('houttuynia','squid','wings'):
  doc=json.loads(fetch(key).decode('utf-8'))
  assert doc['type']=='kaleidoscope_cookery:pot',(key,doc['type'])
  assert doc['carrier']=={'item':'minecraft:bowl'},key
  assert doc['ingredients']==expected[key],key
  assert doc['result']=={'id':results[key],'count':1},key
 print('A2.7.50 pinned Java Wok food/recipe contract: PASS')
if __name__=='__main__':main()
