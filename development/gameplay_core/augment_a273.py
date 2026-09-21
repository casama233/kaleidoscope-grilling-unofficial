from __future__ import annotations
import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
BP=P/'behavior_pack'
RP=P/'resource_pack'
DEV=Path(__file__).parent
VERSION=[2,7,3]
GRILL='kaleidoscope_grilling:grill'
LEGS='kaleidoscope_grilling:grill_legs'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n' if isinstance(data,(dict,list)) else data,encoding='utf-8')


def replace_once(text,old,new,label):
    if old not in text:
        raise RuntimeError('A2.7.3 patch anchor missing: '+label)
    return text.replace(old,new,1)


def patch_versions():
    bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
    for doc,name in ((bm,'Kaleidoscope Grilling A2.7.3 Stabilized BP'),(rm,'Kaleidoscope Grilling A2.7.3 Stabilized RP')):
        doc['header']['version']=VERSION
        doc['header']['name']=name
        for module in doc.get('modules',[]):
            module['version']=VERSION
    for dep in bm.get('dependencies',[]):
        if dep.get('uuid')==rm['header']['uuid']:
            dep['version']=VERSION
    write(BP/'manifest.json',bm)
    write(RP/'manifest.json',rm)
    cfg=load(P/'config.json')
    cfg['name']='Kaleidoscope Grilling A2.7.3 Render/Runtime Stabilization'
    cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_3_Stabilized'
    write(P/'config.json',cfg)


def build_leg_helper_geometry():
    src=load(RP/'models/blocks/grill_legged.geo.json')['minecraft:geometry'][0]
    cubes=[]
    for bone in src.get('bones',[]):
        for cube in bone.get('cubes',[]):
            origin=list(cube.get('origin',[0,0,0]))
            size=list(cube.get('size',[0,0,0]))
            # The main block now always renders the flat grill top. The helper owns
            # only geometry that lives completely below the Java block origin.
            if float(origin[1])+float(size[1])>1e-6:
                continue
            c=copy.deepcopy(cube)
            c['origin'][1]=float(c['origin'][1])+16
            if 'pivot' in c:
                c['pivot'][1]=float(c['pivot'][1])+16
            lo=float(c['origin'][1]);hi=lo+float(c['size'][1])
            if lo<-1e-6 or hi>16+1e-6:
                raise RuntimeError(f'grill helper cube escapes one-cell renderer: {lo}..{hi}')
            cubes.append(c)
    if len(cubes)<4:
        raise RuntimeError('unexpectedly few grill leg cubes')
    geometry={
      'format_version':'1.21.0',
      'minecraft:geometry':[{
        'description':{
          'identifier':'geometry.kg_a273.grill_legs',
          'texture_width':int(src['description']['texture_width']),
          'texture_height':int(src['description']['texture_height']),
          'visible_bounds_width':2.5,
          'visible_bounds_height':2.5,
          'visible_bounds_offset':[0,.5,0]
        },
        'bones':[{'name':'root','pivot':[0,0,0],'cubes':cubes}]
      }]
    }
    write(RP/'models/blocks/grill_legs.geo.json',geometry)
    return len(cubes)


def helper_block():
    perms=[]
    for face,rot in [('north',0),('south',180),('west',90),('east',270)]:
        perms.append({
          'condition':f"q.block_state('kaleidoscope_grilling:direction') == '{face}'",
          'components':{'minecraft:transformation':{'rotation':[0,rot,0]}}
        })
    return {
      'format_version':'1.26.50',
      'minecraft:block':{
        'description':{
          'identifier':LEGS,
          'states':{'kaleidoscope_grilling:direction':['north','south','west','east']}
        },
        'components':{
          'minecraft:geometry':'geometry.kg_a273.grill_legs',
          'minecraft:material_instances':{
            '*':{
              'texture':'kg_a23_grill_unlit',
              'render_method':'alpha_test',
              'ambient_occlusion':1.0,
              'face_dimming':True
            }
          },
          'minecraft:collision_box':False,
          'minecraft:selection_box':False,
          'minecraft:replaceable':{},
          'minecraft:destructible_by_mining':{'seconds_to_destroy':0.05},
          'minecraft:destructible_by_explosion':{'explosion_resistance':0}
        },
        'permutations':perms
      }
    }


def patch_grill_block():
    path=BP/'blocks/grill.json'
    doc=load(path)
    block=doc['minecraft:block']
    # Keep legged as gameplay/support state, but never use the oversized negative-Y
    # geometry in the main block. The grill top must always have an in-cell model.
    for perm in block.get('permutations',[]):
        cond=perm.get('condition','')
        if 'kaleidoscope_grilling:legged' not in cond:
            continue
        lit="kaleidoscope_grilling:lit') == true" in cond
        comp=perm['components']
        comp['minecraft:geometry']='geometry.kg_a23.grill_flat_lit' if lit else 'geometry.kg_a23.grill_flat'
        comp['minecraft:material_instances']={
          '*':{
            'texture':'kg_a23_grill_lit' if lit else 'kg_a23_grill_unlit',
            'render_method':'alpha_test',
            'ambient_occlusion':0.0 if lit else 1.0,
            'face_dimming':False if lit else True
          }
        }
        comp['minecraft:light_emission']=13 if lit else 0
    write(path,doc)
    write(BP/'blocks/grill_legs.json',helper_block())


def patch_runtime():
    path=BP/'scripts/main.js'
    s=path.read_text(encoding='utf-8')
    anchor="const REGISTRY='kaleidoscope_grilling:a2_grills';"
    s=replace_once(
      s,anchor,
      anchor+"\nconst GRILL_LEGS_ID='kaleidoscope_grilling:grill_legs';",
      'helper id'
    )
    old="""function syncGrillPermutation(block,state){
 try{
  let perm=block.permutation,below=block.below(),legged=!(below?.isSolid??false),lit=!!state.lit;
  if(perm.getState('kaleidoscope_grilling:legged')!==legged)perm=perm.withState('kaleidoscope_grilling:legged',legged);
  if(perm.getState('kaleidoscope_grilling:lit')!==lit)perm=perm.withState('kaleidoscope_grilling:lit',lit);
  block.setPermutation(perm);
 }catch{}
}"""
    new="""function grillDirection(block){
 try{const d=String(block.permutation.getState('minecraft:cardinal_direction')??'north');return ['north','south','west','east'].includes(d)?d:'north'}catch{return 'north'}
}
function removeGrillLegs(block){
 try{const below=block.below();if(below?.typeId===GRILL_LEGS_ID)below.setType('minecraft:air')}catch{}
}
function ensureGrillLegs(block){
 try{
  const below=block.below();if(!below)return false;
  if(below.typeId!==GRILL_LEGS_ID&&below.typeId!=='minecraft:air')return false;
  if(below.typeId==='minecraft:air')below.setType(GRILL_LEGS_ID);
  let p=below.permutation,dir=grillDirection(block);
  if(p.getState('kaleidoscope_grilling:direction')!==dir)p=p.withState('kaleidoscope_grilling:direction',dir);
  below.setPermutation(p);return true;
 }catch{return false}
}
function syncGrillPermutation(block,state){
 try{
  let below=block.below(),helper=below?.typeId===GRILL_LEGS_ID,supported=!helper&&(below?.isSolid??false),legged=!supported,lit=!!state.lit;
  if(legged)ensureGrillLegs(block);else removeGrillLegs(block);
  let perm=block.permutation;
  if(perm.getState('kaleidoscope_grilling:legged')!==legged)perm=perm.withState('kaleidoscope_grilling:legged',legged);
  if(perm.getState('kaleidoscope_grilling:lit')!==lit)perm=perm.withState('kaleidoscope_grilling:lit',lit);
  block.setPermutation(perm);
 }catch{}
}"""
    s=replace_once(s,old,new,'grill helper lifecycle')
    old_break=""" clearContainer(block);clearState(block);block.setType('minecraft:air');
 if(!creative(player))player.dimension.spawnItem(new ItemStack(GRILL_ID,1),{x:block.x+.5,y:block.y+.3,z:block.z+.5});"""
    new_break=""" clearContainer(block);clearState(block);removeGrillLegs(block);block.setType('minecraft:air');
 if(!creative(player))player.dimension.spawnItem(new ItemStack(GRILL_ID,1),{x:block.x+.5,y:block.y+.3,z:block.z+.5});"""
    s=replace_once(s,old_break,new_break,'break helper cleanup')
    old_loop=""" for(const row of rows){try{const block=world.getDimension(row.d).getBlock({x:row.x,y:row.y,z:row.z});if(!block||block.typeId!==GRILL_ID)continue;keep.push(row);let state=readState(block),before=state.phase;"""
    new_loop=""" for(const row of rows){try{const dim=world.getDimension(row.d),block=dim.getBlock({x:row.x,y:row.y,z:row.z});if(!block||block.typeId!==GRILL_ID){const helper=dim.getBlock({x:row.x,y:row.y-1,z:row.z});if(helper?.typeId===GRILL_LEGS_ID)helper.setType('minecraft:air');continue}keep.push(row);let state=readState(block),before=state.phase;"""
    s=replace_once(s,old_loop,new_loop,'orphan helper cleanup')
    path.write_text(s,encoding='utf-8')


def generate_icons():
    subprocess.run([sys.executable,str(DEV/'render_a273_icons.py')],cwd=ROOT,check=True)


def report(cube_count):
    write(P/'reports/a273-stabilization.json',{
      'version':'A2.7.3',
      'scope':'engine-first display/runtime stabilization; no new recipe/content batch',
      'user_reproduced_failures':[
        'creative inventory showed raw Java UV/material sheets instead of recognisable 3D skewer icons',
        'unsupported/legged grill had selection box and gameplay state but no visible model'
      ],
      'item_render_split':{
        'inventory_ui':'64x64 transparent icon rasterized from pinned Java 3D item model and GUI transform',
        'held_eating':'existing Bedrock attachable/staged geometry remains separate',
        'formal_icon_count_expected':41
      },
      'grill_render_fix':{
        'main_block':'always renders in-cell flat or flat-lit top geometry',
        'unsupported_visual':'replaceable non-colliding grill_legs helper in block below',
        'helper_geometry_cubes':cube_count,
        'helper_geometry_y_range':[0,16],
        'legged_state_preserved':True
      },
      'compatibility_note':'Cookery v1.0.6 public CurseForge listing currently tags 26.40/26.30 and its description says Minecraft 26.3+; Grilling 26.51 runtime remains provisional until direct engine acceptance.',
      'minecraft_tested_after_fix':False,
      'bds_tested_after_fix':False
    })


def main():
    if load(BP/'manifest.json')['header']['version']!=[2,7,2]:
        raise RuntimeError('A2.7.3 stabilization must augment verified A2.7.2')
    patch_versions()
    cube_count=build_leg_helper_geometry()
    patch_grill_block()
    patch_runtime()
    generate_icons()
    report(cube_count)
    print('A2.7.3 render/runtime stabilization augmentation complete')


if __name__=='__main__':
    main()
