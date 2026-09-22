from __future__ import annotations
import hashlib,urllib.request

COMMIT='73a171fc8393a1052b4ca0669dc82231f775d8b1'
BASE=f'https://raw.githubusercontent.com/microsoft/minecraft-scripting-samples/{COMMIT}/'
FILES={
 'containers':(
  'howto-gallery/scripts/Containers.ts',
  'b51c87f7d02c605b578df8cdf8fea9a643e6f066',
  (
   'xPlusTwoChestContainer.setItem(0, new ItemStack',
   'xPlusTwoChestContainer.getItem(0)?.typeId',
   'transferItem(0, chestCartContainer)',
   'swapItems(1, 0, xChestContainer)',
  )
 ),
 'dynamic_properties':(
  'howto-gallery/scripts/DynamicProperties.ts',
  '7eaf767f47f063c5cb6307018ee6736b8eb7b44d',
  (
   'world.getDynamicProperty("samplelibrary:longerjson")',
   'JSON.parse(paintStr)',
   'JSON.stringify(paint)',
   'world.setDynamicProperty("samplelibrary:longerjson", paintStr)',
  )
 ),
 'custom_components':(
  'custom-components/scripts/main.ts',
  '4f8057288e8792906a5228425230d780e15193a6',
  (
   'itemComponentRegistry.registerCustomComponent',
   'onCompleteUse: sprayWater',
   'onConsume(arg: ItemComponentConsumeEvent)',
  )
 ),
}

def git_blob(data:bytes)->str:
 return hashlib.sha1(b'blob '+str(len(data)).encode()+bytes([0])+data).hexdigest()

def main():
 for name,(path,expected,tokens) in FILES.items():
  req=urllib.request.Request(BASE+path,headers={'User-Agent':'Grilling-A2.7.57-official-samples/1'})
  with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
  actual=git_blob(data);assert actual==expected,(name,actual,expected)
  text=data.decode('utf-8')
  for token in tokens:assert token in text,(name,token)
 print('A2.7.57 pinned Microsoft minecraft-scripting-samples contract: PASS')
 print('commit:',COMMIT)
 print('patterns: exact-slot Container.setItem, JSON world dynamic properties, item complete-use custom component')

if __name__=='__main__':main()
