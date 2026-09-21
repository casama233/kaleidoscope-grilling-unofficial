from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'common/src/main/resources/data/kaleidoscope_grilling/recipe/millstone/canola_powder.json':'83ef97ff4834dc130ac5be6b6793e7d4a6d0b86c',
 'common/src/main/resources/data/kaleidoscope_grilling/tags/item/ingredients/canola_seeds.json':'a69045793742c008107e10bf854406137ee83a41'
}
def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.16-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert git_blob(v)==FILES[path],(path,git_blob(v),FILES[path]);return v
def main():
 recipe=json.loads(fetch(next(p for p in FILES if '/recipe/millstone/' in p)))
 tag=json.loads(fetch(next(p for p in FILES if '/tags/item/ingredients/' in p)))
 assert recipe=={
  'type':'kaleidoscope_cookery:millstone',
  'ingredient':{'tag':'kaleidoscope_grilling:ingredients/canola_seeds'},
  'result':{'id':'kaleidoscope_grilling:canola_powder','count':1}
 }
 assert tag=={'replace':False,'values':['kaleidoscope_grilling:canola_seeds']}
 print('A2.7.16 pinned Java canola millstone contract: PASS')
if __name__=='__main__':main()
