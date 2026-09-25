"""One-shot explicit repair. Offline, no network fetch, no runtime callback simulation.
Invoked only to materialize reviewed assets; not part of the permanent CI build.
"""
from pathlib import Path
import hashlib,json,shutil
import a281_bottle_icons as icons
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'projects/grilling/gameplay_core';B=P/'behavior_pack';R=P/'resource_pack';D=Path(__file__).parent
BASE='45b5f8d001fb624fcf49f5503b5e16b81c93b950'
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def replace(path,old,new):
 text=path.read_text(encoding='utf-8-sig');assert text.count(old)==1,(path,old)
 path.write_text(text.replace(old,new),encoding='utf-8',newline='\n')
def main():
 assert load(B/'manifest.json')['header']['version']==[2,8,0],'unexpected baseline'
 vat=load(B/'blocks/big_vat.json');components=vat['minecraft:block']['components'];assert 'minecraft:item_visual' not in components
 components['minecraft:item_visual']={'geometry':'geometry.kg_a26.big_vat_0','material_instances':{'*':{'texture':'kg_a26_big_vat','render_method':'alpha_test','ambient_occlusion':True,'face_dimming':True}}}
 write(B/'blocks/big_vat.json',vat)
 archived=ROOT/'history/a281-retired/big_vat.attachable.json';archived.parent.mkdir(parents=True,exist_ok=True)
 shutil.move(R/'attachables/big_vat.attachable.json',archived)
 for name,image in icons.images().items():image.save(R/f'textures/items/{name}.png',compress_level=9)
 guide_path=ROOT/'projects/grilling/guide/catalog.a3.json';guide=load(guide_path)
 key='textures/ui/kg_grilling/catalog/special_seasoning';image=R/'textures/items/special_seasoning.png'
 guide['icon_sources'][key]['sha256']=hashlib.sha256(image.read_bytes()).hexdigest()
 write(guide_path,guide);shutil.copyfile(image,R/(key+'.png'))
 # Do not let an inventory-sprite correction change the historical material color palette.
 # These three items use the bottle material as their Java particle/model texture.
 replace(D/'a2770_placed_visual_assets.py',
  "  candidate=RP/(path if path.endswith('.png') else path+'.png')\n  if not candidate.is_file():continue",
  "  candidate=RP/(path if path.endswith('.png') else path+'.png')\n  if key in ('empty_seasoning_bottle','pending_seasoning','special_seasoning'):candidate=RP/'textures/blocks/seasoning_bottle.png'\n  if not candidate.is_file():continue")
 for side,label in ((B,'BP'),(R,'RP')):
  doc=load(side/'manifest.json');doc['header']['name']='Kaleidoscope Grilling A2.8.1 Vat and Icon Corrective '+label;doc['header']['version']=[2,8,1]
  for m in doc['modules']:m['version']=[2,8,1]
  for dep in doc.get('dependencies',[]):
   if dep.get('uuid')=='bbbd2d60-52e5-53a6-8b9a-c09b0f516389':dep['version']=[2,8,1]
  write(side/'manifest.json',doc)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.8.1 Vat and Icon Corrective'
 for plugin in cfg['compiler']['plugins']:
  if isinstance(plugin,list) and plugin[0]=='simpleRewrite':plugin[1]['packName']='Kaleidoscope_Grilling_A2_8_1_Vat_Icon_Corrective'
 write(P/'config.json',cfg)
 replace(D/'verify_current.py','    (2, 8, 0): "verify_a280.py",','    (2, 8, 0): "verify_a280.py",\n    (2, 8, 1): "verify_a281.py",')
 # Reuse the entire preceding suite with a new reviewed runtime fingerprint; no removed tests.
 replace(D/'verify_a280.py','def main():','def main(version=(2,8,0), proof_name="a280-integration-invariants.json"):\n global VERSION\n VERSION=list(version)')
 replace(D/'verify_a280.py',"proof=load(P/'reports/a280-integration-invariants.json')","proof=load(P/'reports'/proof_name)")
 replace(D/'verify_a280.py',"{'version':'A2.8.0','catalog':catalog","{'version':'A'+'.'.join(map(str,VERSION)),'catalog':catalog")
 import verify_a280
 proof=load(P/'reports/a280-integration-invariants.json')
 proof['runtime_sha256']=verify_a280.runtime_digest();proof['source_main']=BASE
 write(P/'reports/a281-invariants.json',proof)
 from a281_visual_contract import icon_contract,baseline_contract
 report={'version':'A2.8.1','baseline':BASE,'unchanged_runtime_files':baseline_contract(),
  'native_vat_display_contexts':7,'removed_active_attachables':['kaleidoscope_grilling:big_vat'],
  'icons':icon_contract(),'icon_source_sha256':icons.INPUTS,
  'pending_static_icon':'zero-ingredient Java default; live ingredient icon is not claimed',
  'special_static_icon':'full variant 0 representative; 64 held states unchanged',
  'gameplay_changed':False,'world_geometry_changed':False,'minecraft_tested':False,'bds_tested':False,'client_visuals_tested':False}
 write(P/'reports/a281-vat-icons.json',report)
 for name in ('a281-source-audit.yml','a281-materialize.yml'):
  path=ROOT/'.github/workflows'/name
  if path.exists():
   dest=ROOT/'history/a281-retired'/name;shutil.move(path,dest)
 for readme in (ROOT/'README.md',P/'README.zh-TW.md'):
  original=readme.read_text(encoding='utf-8-sig')
  readme.write_text('> 最新修正：A2.8.1 — 大缸使用原生方塊物品渲染；調料瓶 UI 圖示修正。見 docs/STATUS-A2.8.1.md。\n\n'+original,encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
