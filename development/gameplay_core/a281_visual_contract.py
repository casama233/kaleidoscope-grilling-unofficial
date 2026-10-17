"""Source/data contracts for the reported Big Vat hand and bottle icon defects."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,subprocess
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
BASE='45b5f8d001fb624fcf49f5503b5e16b81c93b950'
NATIVE_DEFAULTS={
 'gui':{'translation':[0,0,0],'rotation':[30,225,0],'scale':[.625]*3},
 'firstperson_righthand':{'translation':[0,0,0],'rotation':[0,45,0],'scale':[.4]*3},
 'firstperson_lefthand':{'translation':[0,0,0],'rotation':[0,-135,0],'scale':[.4]*3},
 'thirdperson_righthand':{'translation':[0,2.5,0],'rotation':[75,45,0],'scale':[.375]*3},
 'thirdperson_lefthand':{'translation':[0,2.5,0],'rotation':[75,45,0],'scale':[.375]*3},
 'ground':{'translation':[0,3,0],'rotation':[0,0,0],'scale':[.25]*3},
 'fixed':{'translation':[0,0,0],'rotation':[0,0,0],'scale':[.5]*3},
}
DEFAULTS_SOURCE='https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/itemdisplaytransforms'
ICON_NAMES=('empty_seasoning_bottle','pending_seasoning','special_seasoning')
REMOVED='resource_pack/attachables/big_vat.attachable.json'
ALLOWED_CHANGED={
 'behavior_pack/manifest.json','resource_pack/manifest.json','behavior_pack/blocks/big_vat.json',
 *('resource_pack/textures/items/'+x+'.png' for x in ICON_NAMES),
 'resource_pack/textures/ui/kg_grilling/catalog/special_seasoning.png',
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(data):return hashlib.sha256(data).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def normalized_display(row):
 return {'translation':row.get('translation',[0,0,0]),'rotation':[x%360 for x in row.get('rotation',[0,0,0])],'scale':row.get('scale',[1,1,1])}
def java_native_match():
 model=load(ROOT/'projects/grilling/source_snapshots/common/src/main/resources/assets/kaleidoscope_grilling/models/block/big_vat.json')
 display=model['display']
 assert set(NATIVE_DEFAULTS)<=set(display)
 for context,expected in NATIVE_DEFAULTS.items():
  assert normalized_display(display[context])==normalized_display(expected),(context,display[context])
 return len(NATIVE_DEFAULTS)

def vat_contract():
 block=load(BP/'blocks/big_vat.json')['minecraft:block']
 assert block['components']['minecraft:item_visual']=={
  'geometry':'geometry.kg_a26.big_vat_0',
  'material_instances':{'*':{'texture':'kg_a26_big_vat','render_method':'alpha_test','ambient_occlusion':True,'face_dimming':True}}}
 for path in (RP/'attachables').rglob('*.json'):
  assert load(path)['minecraft:attachable']['description']['identifier']!='kaleidoscope_grilling:big_vat',path
 for permutation in block.get('permutations',[]):assert 'minecraft:item_visual' not in permutation['components']
 geometry=load(RP/'models/blocks/big_vat_0.geo.json')['minecraft:geometry'][0]
 assert geometry['description']['identifier']=='geometry.kg_a26.big_vat_0'
 assert 'item_display_transforms' not in geometry
 assert not any('binding' in b for b in geometry['bones'])
 assert not any('fluid' in b.get('name','') for b in geometry['bones'])
 return java_native_match()

def icon_contract():
 material=Image.open(RP/'textures/blocks/seasoning_bottle.png').convert('RGBA')
 atlas=load(RP/'textures/item_texture.json')['texture_data']
 result={}
 for name in ICON_NAMES:
  path=RP/f'textures/items/{name}.png';image=Image.open(path).convert('RGBA')
  assert image.size==(64,64) and image.tobytes()!=material.tobytes(),name
  alpha=image.getchannel('A');bbox=alpha.getbbox();assert bbox and all(0<v<64 for v in bbox)
  assert 700<sum(x>0 for x in alpha.getdata())<2500,name
  assert all(image.getpixel((x,y))[3]==0 for x in range(64) for y in (0,63)),name
  assert all(image.getpixel((x,y))[3]==0 for y in range(64) for x in (0,63)),name
  assert atlas[name]['textures']==f'textures/items/{name}'
  result[name]={'bbox':bbox,'sha256':sha(path.read_bytes()),'rgba_sha256':sha(image.tobytes())}
 guide=load(ROOT/'projects/grilling/guide/catalog.a3.json')
 target='textures/ui/kg_grilling/catalog/special_seasoning'
 assert guide['icon_sources'][target]['sha256']==result['special_seasoning']['sha256']
 assert (RP/(target+'.png')).read_bytes()==(RP/'textures/items/special_seasoning.png').read_bytes()
 return result

def baseline_contract():
 if subprocess.run(['git','cat-file','-e',BASE+'^{commit}'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
  subprocess.run(['git','fetch','--depth=1','origin',BASE],cwd=ROOT,check=True)
 prefix='projects/grilling/gameplay_core/'
 raw=git('ls-tree','-r','-z',BASE,'--',prefix+'behavior_pack',prefix+'resource_pack');before={}
 for row in raw.split(b'\0'):
  if row:
   header,path=row.split(b'\t',1);before[path.decode()[len(prefix):]]=header.split()[2].decode()
 after={p.relative_to(P).as_posix():p for pack in (BP,RP) for p in pack.rglob('*') if p.is_file()}
 assert set(before)-set(after)=={REMOVED}
 assert not set(after)-set(before),('new runtime entries',set(after)-set(before))
 changed=set()
 for name,path in after.items():
  data=path.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if blob!=before[name]:changed.add(name)
 assert changed==ALLOWED_CHANGED,('unexpected runtime modification',changed^ALLOWED_CHANGED)
 original=json.loads(git('show',BASE+':'+prefix+'behavior_pack/blocks/big_vat.json'))
 new=load(BP/'blocks/big_vat.json');new['minecraft:block']['components'].pop('minecraft:item_visual')
 assert new==original,'world geometry, states, collision, category and recipes must not change'
 old=git('show',BASE+':'+prefix+REMOVED)
 assert (ROOT/'history/a281-retired/big_vat.attachable.json').read_bytes()==old
 old_catalog=json.loads(git('show',BASE+':projects/grilling/guide/catalog.a3.json'))
 new_catalog=load(ROOT/'projects/grilling/guide/catalog.a3.json');key='textures/ui/kg_grilling/catalog/special_seasoning'
 new_catalog['icon_sources'][key]['sha256']=old_catalog['icon_sources'][key]['sha256']
 assert new_catalog==old_catalog,'guide content must be unchanged beyond sprite provenance'
 return len(before)-len(changed)-1
