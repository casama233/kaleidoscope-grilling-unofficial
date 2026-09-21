from __future__ import annotations
import hashlib,json,urllib.request

BASE='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/'
FILES={
 'common/src/main/resources/data/kaleidoscope_grilling/recipe/millstone/onion_powder.json':'763aaf30a9e7a6540f36406f5e7155a9eec9be4d',
 'common/src/main/resources/data/kaleidoscope_grilling/tags/item/ingredients/onions.json':'38c13e1a55a253306b87c3e5c3795f832b9e2675',
 'common/src/main/resources/data/c/tags/item/crops/onion.json':'7ba3089ca4c404f7954bcd8d1533cd4ed62c8875'
}
def git_blob(v):return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()
def fetch(path):
 req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.18-contract/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 assert git_blob(v)==FILES[path],(path,git_blob(v),FILES[path]);return v
def main():
 recipe=json.loads(fetch(next(p for p in FILES if '/recipe/millstone/' in p)))
 tag=json.loads(fetch(next(p for p in FILES if '/ingredients/onions.json' in p)))
 common=json.loads(fetch(next(p for p in FILES if '/data/c/tags/item/crops/onion.json' in p)))
 assert recipe=={
  'type':'kaleidoscope_cookery:millstone',
  'ingredient':{'tag':'kaleidoscope_grilling:ingredients/onions'},
  'result':{'id':'kaleidoscope_grilling:onion_powder','count':1}
 }
 assert tag=={'replace':False,'values':['#c:crops/onion']}
 assert common=={'replace':False,'values':['kaleidoscope_grilling:onion']}
 print('A2.7.18 pinned Java onion millstone/tag-chain contract: PASS')
if __name__=='__main__':main()
