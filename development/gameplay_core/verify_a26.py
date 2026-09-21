from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
A1RP=ROOT/'projects/grilling/resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def git_blob(p):
 v=p.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,6,0] and rm['header']['version']==[2,6,0]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.6 Gameplay BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.6 Gameplay RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 press=load(BP/'blocks/oil_press.json')['minecraft:block'];vat=load(BP/'blocks/big_vat.json')['minecraft:block']
 assert press['description']['states']['kaleidoscope_grilling:cake_count']==[0,1,2,3,4]
 assert press['description']['states']['kaleidoscope_grilling:press_stage']==[0,1,2,3,4]
 assert press['description']['traits']['minecraft:placement_direction']['y_rotation_offset']==180.0
 assert vat['description']['states']['kaleidoscope_grilling:vat_level']==[0,1,2,3,4]
 assert vat['description']['states']['kaleidoscope_grilling:vat_fluid']==['empty','water','lava','canola','secret_chili','premium_chili']

 for name in ('canola_powder','oil_cake','oil_residue'):
  item=load(BP/f'items/{name}.json')['minecraft:item'];assert item['description']['identifier']=='kaleidoscope_grilling:'+name
 assert git_blob(RP/'textures/items/canola_powder.png')=='1772fc66d797448e29396b41eb45ae408e959786'
 assert git_blob(RP/'textures/items/oil_cake.png')=='7fe58aa3aec5c9ba01d47efed453f65f54dceaca'
 assert git_blob(RP/'textures/items/oil_residue.png')=='6160880abe309657cd7e9e6ffe7ebaa109179052'
 assert (RP/'textures/blocks/oil_press.png').read_bytes()==(A1RP/'textures/kg_a1/oil_press.png').read_bytes()
 assert (RP/'textures/blocks/big_vat.png').read_bytes()==(A1RP/'textures/kg_a1/big_vat.png').read_bytes()

 for c in range(5):
  g=load(RP/f'models/blocks/oil_press_c{c}_s0.geo.json')['minecraft:geometry'][0]
  assert g['description']['identifier']==f'geometry.kg_a26.oil_press_c{c}_s0'
 for st in range(1,5):
  g=load(RP/f'models/blocks/oil_press_c4_s{st}.geo.json')['minecraft:geometry'][0]
  assert g['description']['identifier']==f'geometry.kg_a26.oil_press_c4_s{st}'
 for lv in range(5):
  g=load(RP/f'models/blocks/big_vat_{lv}.geo.json')['minecraft:geometry'][0]
  assert g['description']['identifier']==f'geometry.kg_a26.big_vat_{lv}'
  fluid=[b for b in g['bones'] if b.get('name')=='fluid_surface']
  assert (len(fluid)==1)==(lv>0)
  if fluid:
   faces=fluid[0]['cubes'][0]['uv'];assert all(x.get('material_instance')=='fluid' for x in faces.values())

 for name in ('oil_cake','big_vat','oil_press'):
  recipe=load(BP/f'recipes/{name}.json')['minecraft:recipe_shaped'];assert recipe['description']['identifier']=='kaleidoscope_grilling:'+name

 core=(BP/'scripts/a26_oil_machine_core.js').read_text(encoding='utf-8')
 for token in ('PRESS_MAX_CAKES=4','PRESS_REQUIRED_PROGRESS=16','PRESS_IMPACT_TICK=6','VAT_CAPACITY_BUCKETS=8','potFillPlan','nearbyOffsets'):assert token in core,token
 rt=(BP/'scripts/a26_oil_machine_runtime.js').read_text(encoding='utf-8')
 for token in ('PRESS_REG','scanVat','finishPress','startPress','fillVatFromBucket','takeVatBucket','fillPotFromVat','breakVat','doubleCropGrowth'):assert token in rt,token
 main=(BP/'scripts/main.js').read_text(encoding='utf-8');assert "import './a26_oil_machine_runtime.js';" in main
 oil=(BP/'scripts/a23_oil_world.js').read_text(encoding='utf-8');assert "if(e.block.typeId==='kaleidoscope_grilling:big_vat')return;" in oil

 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a24_core.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a25_core.mjs')],check=True)
 subprocess.run(['node',str(ROOT/'development/gameplay_core/test_a26_core.mjs')],check=True)

 parity=load(P/'reports/a26-parity.json')
 assert parity['version']=='A2.6.0'
 assert parity['oil_press']['max_cakes']==4 and parity['oil_press']['required_progress']==16
 assert parity['oil_press']['impact_tick']==6 and parity['oil_press']['completion_delay_ticks']==10
 assert parity['oil_press']['nearby_scan']==[4,2,4] and parity['oil_press']['canola_output_buckets']==4
 assert parity['big_vat']['capacity_buckets']==8 and parity['big_vat']['oil_pot_points_per_bucket']==8

 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json')
   matches=[p.parent for p in dist.rglob('manifest.json') if load(p).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})

 result={'version':'A2.6.0','press_max_cakes':4,'press_progress':16,'impact_tick':6,'completion_delay':10,'scan':[4,2,4],
  'vat_capacity':8,'vat_supported':['water','lava','canola','secret_chili','premium_chili'],'oil_pot_points_per_bucket':8,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False}
 out=P/'reports'/('a26-dash-verification.json' if a.compiled else 'a26-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
