from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
OFFSET=[0,7,2]
ANIM_FILE=RP/'animations/a2725_skewer_hold.animation.json'
FIRST='animation.kaleidoscope_grilling.a2725.skewer_hold_first_person'
THIRD='animation.kaleidoscope_grilling.a2725.skewer_hold_third_person'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def geometry(doc,identifier=None):
 geos=doc['minecraft:geometry']
 if identifier is None:
  assert len(geos)==1
  return geos[0]
 rows=[g for g in geos if g.get('description',{}).get('identifier')==identifier]
 assert len(rows)==1,(identifier,[g.get('description',{}).get('identifier') for g in geos])
 return rows[0]

def find_bone(doc,suffix,identifier=None):
 geo=geometry(doc,identifier)
 rows=[b for b in geo['bones'] if b['name'].endswith(suffix)]
 assert len(rows)==1,(suffix,[b['name'] for b in geo['bones']])
 return rows[0]

def sub(a,b):return [round(a[i]-b[i],6) for i in range(3)]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,25] and rm['header']['version']==[2,7,25]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.25 Skewer Hand Anchor BP'

 anim=load(ANIM_FILE)
 assert anim['format_version']=='1.8.0'
 for key in (FIRST,THIRD):
  row=anim['animations'][key]
  assert row['loop'] is True
  assert row['bones']['root']=={'position':OFFSET}

 atts=sorted((RP/'attachables').glob('*_skewer.attachable.json'))
 assert len(atts)==39
 for path in atts:
  desc=load(path)['minecraft:attachable']['description']
  assert desc['animations']['hold_first_person']==FIRST,path.name
  assert desc['animations']['hold_third_person']==THIRD,path.name
  assert desc['scripts']['animate']==[
   {'hold_first_person':'context.is_first_person == 1.0'},
   {'hold_third_person':'context.is_first_person == 0.0'},
  ],path.name
  pre=desc['scripts'].get('pre_animation',[])
  assert pre and any('item_in_use_duration' in x for x in pre),path.name
  assert desc['render_controllers']==['controller.render.kg_a22.bite'],path.name

 # Spatial proof: A1.16's independently generated hand-prop geometry is the same
 # raw beef geometry translated by exactly [0,+7,+2]. Keep the source A2.2 geometry
 # unchanged and apply that missing offset at the bound root through animation.
 stage=load(RP/'models/entity/a22_bites/raw_beef_skewer_stage0.geo.json')
 proto=load(ROOT/'projects/grilling/integration/immersion_lab/resource_pack/models/entity/hand_props.geo.json')
 swood=find_bone(stage,'wood_0')
 pwood=find_bone(proto,'held0_instance_0_wood_0','geometry.kg_imm.hand_skewer')
 sfood=find_bone(stage,'food3_1')
 pfood=find_bone(proto,'held0_instance_0_food3_1','geometry.kg_imm.hand_skewer')
 assert sub(pwood['cubes'][0]['origin'],swood['cubes'][0]['origin'])==OFFSET
 assert sub(pfood['cubes'][0]['origin'],sfood['cubes'][0]['origin'])==OFFSET
 root=stage['minecraft:geometry'][0]['bones'][0]
 assert root['name']=='root' and root['binding']=='q.item_slot_to_bone_name(context.item_slot)'
 assert swood['cubes'][0]['origin']==[-0.25,0.75,-8]

 rc=load(RP/'render_controllers/a22_bites.render_controllers.json')
 body=rc['render_controllers']['controller.render.kg_a22.bite']
 assert body['geometry']=='Array.kg_bite_geo[v.kg_bite_stage]'

 report=load(P/'reports/a2725-skewer-hand-anchor.json')
 assert report['version']=='A2.7.25'
 assert report['bedrock_fix']['attachable_count']==39
 assert report['bedrock_fix']['first_person_offset']==OFFSET
 assert report['bedrock_fix']['third_person_offset']==OFFSET
 assert report['bedrock_fix']['geometry_rebaked'] is False
 assert report['bedrock_fix']['bite_stage_pre_animation_preserved'] is True
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json')
   matches=[x.parent for x in dist.rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})

 result={
  'version':'A2.7.25','skewer_attachables':39,'shared_hold_animation':True,
  'hand_offset':OFFSET,'bite_stage_logic_preserved':True,'geometry_rebaked':False,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a2725-dash-verification.json' if a.compiled else 'a2725-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(out.read_text(encoding='utf-8'))
if __name__=='__main__':main()
