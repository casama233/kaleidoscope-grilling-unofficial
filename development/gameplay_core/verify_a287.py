"""All held binding paths and pose dispatch. Does not simulate a Minecraft client."""
from pathlib import Path
import ast,json,re,subprocess
import a287_binding_repair as repair
import importlib.util
_spec=importlib.util.spec_from_file_location('tools_build_eating',Path(__file__).resolve().parents[2]/'tools/build_eating_motion.py')
_motion=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_motion)
from verify_a285 import survival_gate
from verify_a284 import eating_gate
from verify_a283 import main as previous_gate
RP=repair.RP;BP=repair.BP
def load(p):return json.loads(p.read_text())
def expression(expr,first,slot,bone,using=False,eat_profile=3,eat_hand=None,projection=None,posture=None):
 # Only the simple boolean Molang subset used by held pose dispatch is accepted.
 expr=expr.replace('q.item_slot_to_bone_name(context.item_slot)',repr(bone))
 for prefix in ('context','c'):
  expr=expr.replace(prefix+'.is_first_person',str(int(first))).replace(prefix+'.item_slot',repr(slot))
 if eat_hand is None:eat_hand=1 if slot=='main_hand' else 2
 expr=expr.replace("q.property('kaleidoscope_grilling:eat_hand')",str(eat_hand))
 expr=expr.replace('q.is_using_item',str(bool(using))).replace("q.property('kaleidoscope_grilling:eat_profile')",str(eat_profile))
 expr=expr.replace("q.property('kaleidoscope_grilling:eat_projection')",str(int(using and eat_profile in (2,4,5) if projection is None else projection)))
 for state in ('is_sneaking','is_swimming','is_gliding','is_riding'):expr=expr.replace('q.'+state,str(int(state==posture)))
 expr=expr.replace('&&',' and ').replace('||',' or ')
 tree=ast.parse(expr,mode='eval')
 assert all(isinstance(n,(ast.Expression,ast.BoolOp,ast.And,ast.Or,ast.Compare,ast.Eq,ast.NotEq,ast.Constant,ast.Load)) for n in ast.walk(tree)),expr
 return bool(eval(compile(tree,'<pose-condition>','eval'),{'__builtins__':{}},{}))
def binding_assets():
 idx={};animations={};rows=[];refs=set();cases=0
 for p in (RP/'models').rglob('*.geo.json'):
  for g in load(p)['minecraft:geometry']:
   ref=g['description']['identifier'];assert ref not in idx,ref;idx[ref]=g
 for p in (RP/'animations').glob('*.json'):
  for key,a in load(p).get('animations',{}).items():assert key not in animations,key;animations[key]=a
 for p in sorted((RP/'attachables').glob('*.json')):
  d=load(p)['minecraft:attachable']['description'];selected=[]
  for first in (0,1):
   for slot,hand in [('main_hand','right'),('off_hand','left')]:
    for bone in (hand+'item',hand+'Item','custom_'+hand+'_grip'):
     matches=[key for row in d['scripts']['animate'] for key,expr in row.items() if expression(expr,first,slot,bone)]
     expected=('fp_' if first else 'tp_')+hand
     assert matches==[expected],(p,first,slot,bone,matches)
     for profile in (2,3,4,5):
      using_matches=[key for row in d['scripts']['animate'] for key,expr in row.items() if expression(expr,first,slot,bone,True,profile)]
      eating='eat_alt_'+hand if profile==4 and 'eat_alt_'+hand in d['animations'] else 'eat_'+hand
      projected='fp_eat_'+hand
      projected_code={'two':2,'three_alt':4,'four':5}.get(d['animations'].get(projected,'').split('.')[-2] if projected in d['animations'] else '')
      expected_using=([projected] if first and profile==projected_code else [expected]+([eating] if eating in d['animations'] else [])) if tuple(load(BP/'manifest.json')['header']['version'])>=(2,8,58) else [expected]+([eating] if eating in d['animations'] else [])
      assert using_matches==expected_using,(p,profile,using_matches,expected_using)
      # Projection is independently synchronized, and every excluded posture
      # must fall back to the old pose plus local eating animation.
      for projection,posture in [(False,None)]+[(True,s) for s in ('is_sneaking','is_swimming','is_gliding','is_riding')]:
       fallback=[key for row in d['scripts']['animate'] for key,expr in row.items() if expression(expr,first,slot,bone,True,profile,projection=projection,posture=posture)]
       assert fallback==[expected]+([eating] if eating in d['animations'] else []),(p,profile,projection,posture,fallback)
      for inactive in (0,2 if slot=='main_hand' else 1):
       inactive_matches=[key for row in d['scripts']['animate'] for key,expr in row.items() if expression(expr,first,slot,bone,True,profile,inactive)]
       assert inactive_matches==[expected],(p,profile,inactive,inactive_matches)
     cases+=1
    selected.append(expected)
  for ref in d['geometry'].values():
   refs.add(ref);g=idx[ref]
   b=g['bones'][0];assert b['name']=='grip' and b['pivot']==[0,24,0]
   assert b['binding']=='q.item_slot_to_bone_name(context.item_slot)' and 'parent' not in b
   if ref.startswith('geometry.kg_a287.'):
    # A2.8.14 splits binding, display pose and handle-origin correction.
    assert len(g['bones'])==3 and not b.get('cubes'),ref
    pose,model=g['bones'][1:]
    assert pose=={'name':'skewer_pose','parent':'grip','pivot':[0,24,0]},ref
    assert model['name']=='skewer_model' and model['parent']=='skewer_pose' and model['pivot']==[0,24,0]
    for alias,anim in d['animations'].items():assert set(animations[anim]['bones'])==({'skewer_model'} if alias.startswith('eat_') else {'skewer_pose','skewer_model'}),anim
    oldref=ref.replace('kg_a287.','kg_a283.');old=idx[oldref]
    assert model['cubes']==[c for bone in old['bones'] for c in bone.get('cubes',[])],ref
   elif ref.startswith('geometry.kg_secret_held.'):
    assert len(g['bones'])==3 and not b.get('cubes'),ref
    pose,model=g['bones'][1:]
    assert pose=={'name':'skewer_pose','parent':'grip','pivot':[0,24,0]},ref
    assert model['name']=='skewer_model' and model['parent']=='skewer_pose',ref
   elif ref=='geometry.kg_a286.kg_a2763.advanced_rack_hand':
    assert len(g['bones'])==3 and not b.get('cubes'),ref
    pose,model=g['bones'][1:]
    assert pose=={'name':'rack_pose','parent':'grip','pivot':[0,24,0]}
    assert model['name']=='rack_model' and model['parent']=='rack_pose' and model['pivot']==[0,24,0]
    for anim in d['animations'].values():assert set(animations[anim]['bones'])=={'rack_pose','rack_model'},anim
   else:
    assert len(g['bones'])==1 and b.get('cubes'),ref
    for anim in d['animations'].values():assert set(animations[anim]['bones'])=={'grip'},anim
  if p.name.endswith('_skewer.attachable.json') and d['identifier']!='kaleidoscope_grilling:secret_skewer':
   old=repair.source(p);old=old['minecraft:attachable']['description']
   profiles=json.loads(re.search(r'PROFILE_BY_ITEM=Object.freeze\((\{.*?\})\)',(BP/'scripts/data.js').read_text()).group(1))
   from native_eating_clock import VARIABLE,ASSIGNMENT
   pre=d['scripts']['pre_animation']
   if tuple(load(BP/'manifest.json')['header']['version'])>=(2,8,58):
    assert pre[0]==ASSIGNMENT
    pre=[row.replace(VARIABLE,'q.item_in_use_duration') for row in pre[1:]]
   if profiles.get(d['identifier'])=='THREE_RANDOM':assert "q.property('kaleidoscope_grilling:eat_profile')" in pre[0]
   else:
    assert [row.replace(_motion.ACTIVE_HAND,'q.is_using_item') for row in pre]==old['scripts']['pre_animation']
   assert d['render_controllers']==old['render_controllers'] and d['textures']==old['textures']
   assert set(d['geometry'])==set(old['geometry'])
  rows.append({'item':d['identifier'],'geometries':list(d['geometry'].values()),'poses':selected,'bound_bone':'grip'})
 expected_count=107 if (RP/'attachables/secret_skewer.attachable.json').exists() else 106 if tuple(load(BP/'manifest.json')['header']['version']) >= (2,8,32) else 107
 assert len(rows)==expected_count and cases==expected_count*12,(len(rows),cases)
 # Regression reproduction: old dispatch can select zero poses for a normalized bone name.
 old=repair.source(RP/'attachables/empty_seasoning_bottle.attachable.json')['minecraft:attachable']['description']
 assert not any(expression(expr,0,'main_hand','rightitem') for row in old['scripts']['animate'] for expr in row.values())
 # World entities and native block items must never inherit a player hand binding.
 entities=0;native=0
 for p in (RP/'entity').glob('*.json'):
  d=load(p).get('minecraft:client_entity',{}).get('description',{})
  for ref in d.get('geometry',{}).values():
   if ref in idx:assert not any('binding' in b for b in idx[ref]['bones']),(p,ref)
  entities+=1
 for p in (BP/'blocks').glob('*.json'):
  c=load(p)['minecraft:block']['components'];v=c.get('minecraft:item_visual')
  if v:
   ref=v['geometry'];ref=ref.get('identifier') if isinstance(ref,dict) else ref
   assert not any('binding' in b for b in idx[ref]['bones']),ref;native+=1
 assert native==3
 return idx,refs,{'attachables':len(rows),'pose_cases':cases,'native_item_visuals':native,'client_entities':entities,'items':rows}
def plant_gate():
 count=0;plant_refs=set()
 idx={g['description']['identifier']:g for p in (RP/'models').rglob('*.geo.json') for g in load(p)['minecraft:geometry']}
 for name in repair.PLANTS:
  b=load(BP/f'blocks/{name}.json')['minecraft:block'];before=repair.source(BP/f'blocks/{name}.json')['minecraft:block']
  for c in [b['components']]+[p['components'] for p in b.get('permutations',[])]:
   ref=c.get('minecraft:geometry');ref=ref.get('identifier') if isinstance(ref,dict) else ref
   if ref:plant_refs.add(ref)
   for m in c.get('minecraft:material_instances',{}).values():
    if isinstance(m,dict):assert m['render_method']=='alpha_test_single_sided';count+=1
  # Gameplay state, collision and component logic are not part of the material fix.
  def strip(value):
   if isinstance(value,dict):return {k:strip(v) for k,v in value.items() if k!='render_method'}
   if isinstance(value,list):return [strip(v) for v in value]
   return value
  assert strip(b)==strip(before),name
 for ref in plant_refs:
  for bone in idx[ref]['bones']:
   for cube in bone.get('cubes',[]):
    if isinstance(cube['uv'],list):continue  # Box UV emits all six directions.
    for axis,size in enumerate(cube['size']):
     if size==0:assert all(face in cube['uv'] for face in [('east','west'),('up','down'),('north','south')][axis]),ref
 # Third-person interaction gestures must not translate arms out of their joints.
 animations=load(RP/'animations/player_binding.animation.json')['animations']
 for key,a in animations.items():
  if not any(key.startswith('animation.kg_imm.player.'+kind+'.') for kind in ('reach','brush','season')):continue
  for b in a['bones'].values():
   p=b.get('position',[]);vectors=p.values() if isinstance(p,dict) else [p]
   for vector in vectors:
    assert all(v==0 or isinstance(v,str) and v.endswith(' : 0.0') for v in vector),key
 print('A287 single-sided plant material instances:',count)
def secret_compat_gate():
 main=(BP/'scripts/main.js').read_text()
 assert 'VANILLA_SMOKED' not in main
 assert 'resolveSecretSmokedId(row)' in main
 assert "emitSecretIngredientConsumed(player,row)" in main
 runtime=(BP/'scripts/secret_compat_runtime.js').read_text()
 for event in (
  'kaleidoscope_grilling:register_secret_smoking',
  'kaleidoscope_grilling:register_secret_food_behavior',
  'kaleidoscope_grilling:register_secret_compat',
  'kaleidoscope_grilling:secret_ingredient_consumed',
 ):
  assert event in runtime,event
 subprocess.run(['node',str(Path(__file__).with_name('test_secret_compat_core.mjs'))],check=True)
 print('A287 secret-skewer extensible smoking/finish-use compatibility: PASS')

def parity_batch2_gate():
 main=(BP/'scripts/main.js').read_text()
 assert 'compactMatchingHotFood' in main and 'isFoodStack(e.itemStack)' in main
 cuisine=(BP/'scripts/a2750_cookery_cuisine_runtime.js').read_text()
 assert 'kaleidoscope_grilling:cookery_output_ready' not in cuisine  # event constant stays in the contract module
 assert 'COOKERY_OUTPUT_READY_EVENT' in cuisine and 'applyAuthoritativeCookeryOutput' in cuisine
 subprocess.run(['node','--experimental-vm-modules',str(Path(__file__).with_name('test_hot_food_manual_merge.mjs'))],check=True)
 subprocess.run(['node',str(Path(__file__).with_name('test_cookery_output_contract_core.mjs'))],check=True)
 print('A287 generic hot-food manual merge and authoritative Cookery output contract: PASS')

def parity_batch3_gate():
 oil=(BP/'scripts/a23_oil_world.js').read_text()
 assert 'MAX_SOURCES' not in oil and 'slice(0,MAX_SOURCES)' not in oil
 assert 'getDynamicPropertyIds' in oil and 'FLOW_SOURCE_BUDGET' in oil and 'heightRange' in oil
 main=(BP/'scripts/main.js').read_text()
 assert 'skewerIngredientDecision' in main and 'customSkewerCookedId' in main and 'isCompatRawSkewer' in main
 plate=(BP/'scripts/a25_plate_recipe_runtime.js').read_text()
 assert 'RAW_SKEWER_TAG' in plate and 'GRILLED_SKEWER_TAG' in plate
 subprocess.run(['node',str(Path(__file__).with_name('test_oil_source_registry_core.mjs'))],check=True)
 subprocess.run(['node',str(Path(__file__).with_name('test_skewer_compat_core.mjs'))],check=True)
 print('A287 per-source oil registry and declarative SkewerCompat parity: PASS')

if __name__=='__main__':
 plant_gate();secret_compat_gate();parity_batch2_gate();parity_batch3_gate();eating_gate();survival_gate();previous_gate()
