from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
B=P/'behavior_pack'
R=P/'resource_pack'
D=Path(__file__).resolve().parent
PALETTES={
 5:'4ed27986868159012ad3927e2ca17d81d21c8fb35d19ba7a682583e86f3683e3',
 6:'d9e4347dcc8f0c4ced04620e096da71f88d20365b2168e0e9d728a21e93ba0ed',
 7:'29763206a3c76d4e470377e84c03253438f9949e6251571f2f499e32496354ee',
}
UV=[(0,8),(0,16),(8,16),(24,16),(0,24),(8,24),(16,24),(24,24)]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def check_assets(java_display=False):
 models={g['description']['identifier']:g for p in R.rglob('*.geo.json') for g in load(p).get('minecraft:geometry',[])}
 for v,h in PALETTES.items():assert sha(R/f'textures/a2766_special_seasoning/palette_v{v}.png')==h
 assert sha(R/'textures/blocks/seasoning_bottle.png')=='9a889a96a4bb34b999ddfc5bcb42b1f1a691fc1e65c91253726b7eee6a3dc94b'
 expected={f'special_seasoning_r{r}_v{v}' for r in range(1,9) for v in range(8)}
 assert {p.stem for p in (B/'items').glob('special_seasoning_r*.json')}==expected
 for r in range(1,9):
  for v in range(8):
   name=f'special_seasoning_r{r}_v{v}'
   item=load(B/f'items/{name}.json')['minecraft:item']
   assert item['description']['identifier']=='kaleidoscope_grilling:'+name
   assert item['description']['menu_category']['category']=='none'
   assert item['components']['minecraft:max_stack_size']==1
   assert item['components']['minecraft:block_placer']['block']=='kaleidoscope_grilling:seasoning_bottle_1'
   assert item['components']['minecraft:icon']['textures']['default']=='special_seasoning'
   desc=load(R/f'attachables/{name}.attachable.json')['minecraft:attachable']['description']
   assert desc['identifier']==item['description']['identifier']
   assert desc['render_controllers']==['controller.render.kg_a2733.seasoning_bottle_hand']
   if java_display:
    assert len(desc.get('animations',{}))==4 and len(desc.get('scripts',{}).get('animate',[]))==4
   else:assert not desc.get('animations') and not desc.get('scripts',{}).get('animate')
   geometry=models[desc['geometry']['default']]
   root=geometry['bones'][0]
   assert root['binding']=='q.item_slot_to_bone_name(context.item_slot)'
   fill=[c for b in geometry['bones'] if 'spice_fill' in b['name'] for c in b.get('cubes',[])]
   assert len(fill)==1 and abs(fill[0]['size'][1]-5*r/8)<1e-8
   texture=desc['textures']['default']
   assert (R/(texture+'.png')).is_file()
   if texture=='textures/blocks/seasoning_bottle':u,w=UV[v]
   else:
    assert v in PALETTES and texture==f'textures/a2766_special_seasoning/palette_v{v}'
    assert desc['geometry']['default']==f'geometry.kg_a2766.special_seasoning.r{r}.v0'
    u,w=UV[0]
   for direction,face in fill[0]['uv'].items():
    a,b=face['uv'];c,d=face['uv_size']
    low=w if direction in ('up','down') else w+8-r
    assert sorted([a,a+c])==[u,u+8] and sorted([b,b+d])==[low,w+8],(name,direction,face)
 # Preserve the already-delivered skewer conversion, not its unverified visual claim.
 skewers=list((R/'attachables').glob('*_skewer.attachable.json'))
 assert len(skewers)==39
 for p in skewers:
  desc=load(p)['minecraft:attachable']['description']
  if java_display:
   assert len(desc.get('animations',{}))==4 and len(desc.get('scripts',{}).get('animate',[]))==4
  else:assert not desc.get('animations') and not desc.get('scripts',{}).get('animate')
  assert desc['scripts']['pre_animation'] and desc['render_controllers']==['controller.render.kg_a22.bite']
  prefix='geometry.kg_a22.' if java_display else 'geometry.kg_a2764.'
  assert all(g.startswith(prefix) and g in models for g in desc['geometry'].values())
 assert len(list((R/'models/entity/a2764_skewer_hand').glob('*.geo.json')))==150
 return {'special_seasoning_states':64,'active_uses_variant_combinations':128,'skewer_attachables_retained':39,'minecraft_tested':False,'client_visuals_tested':False}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--compiled',action='store_true');parser.add_argument('--assets-only',action='store_true');args=parser.parse_args()
 result=check_assets()
 if not args.assets_only:
  for pack in (B,R):assert load(pack/'manifest.json')['header']['version']==[2,7,66]
  subprocess.run([sys.executable,str(D/'a2764_rebake_skewer_hand_geometry.py'),'--check'],check=True)
  for name in ('test_a275_core.mjs','test_a276_core.mjs','test_a277_core.mjs','test_a2762_core.mjs'):
   subprocess.run(['node',str(D/name)],check=True)
  subprocess.run(['node','--experimental-vm-modules',str(D/'test_a2766_runtime.mjs')],check=True)
  subprocess.run([sys.executable,str(D/'verify_a2761_java_interaction_contract.py')],check=True)
  for p in (B/'scripts').rglob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
  report=load(P/'reports/a2766-seasoning-state-completion.json')
  assert report['version']=='A2.7.66' and report['state_count']==64
  assert not any(report[k] for k in ('minecraft_tested','bds_tested','client_visuals_tested'))
 print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
