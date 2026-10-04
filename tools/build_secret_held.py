"""Three independently selected ingredient meshes on the existing bound hand rig.

Public icon references only. Arbitrary per-stack native GUI composition is not
provided by this generator. No host/vanilla client entity is replaced.
"""
from pathlib import Path
import argparse,copy,json
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'projects/grilling/gameplay_core';RP=P/'resource_pack';BP=P/'behavior_pack'
FIX=ROOT/'development/gameplay_core/fixtures/secret-visual-catalog.json'
def build():
 rows=json.loads(FIX.read_text())['items'];assert len(rows)<256
 textures={'stick':'textures/a22_bites/raw_beef_skewer_stage4'}
 geometries=[];refs={};controllers={};table={}
 base=json.loads((RP/'models/entity/a287_hand/kg_a22.raw_beef_skewer.stage4.geo.json').read_text())['minecraft:geometry'][0]
 stick=copy.deepcopy(base);stick['description']['identifier']='geometry.kg_secret_held.stick';geometries.append(stick);refs['stick']=stick['description']['identifier']
 for index,row in enumerate(rows,1):textures['food_'+str(index)]=row['texture'];table[row['id']]=index
 for slot in range(3):
  # Geometry is shared by every icon. Only empty / visible differs per slot.
  for index in [0,1]:
   name='part_'+str(slot)+'_'+str(index);geo=copy.deepcopy(base)
   geo['description'].update(identifier='geometry.kg_secret_held.'+name,texture_width=16,texture_height=16)
   geo['bones'][2].pop('cubes',None)
   # Stable cube faces: do not require experimental texture-mesh support.
   # Explicit opposing faces keep this icon cutout visible from both sides.
   if index:geo['bones'][2]['cubes']=[{'origin':[-1.92,24.75,1.08-slot*4],'size':[3.84,0,3.84],'uv':{'up':{'uv':[0,0],'uv_size':[16,16]},'down':{'uv':[16,0],'uv_size':[-16,16]}}}]
   geometries.append(geo);refs[name]=geo['description']['identifier']
  # Render-controller context is not the owning player. Resolve the hand and
  # player properties in attachable pre_animation, as the native-proven bottle
  # route does; controllers consume only the resulting numeric local variable.
  prop='v.kg_secret_ingredient_'+str(slot)
  controllers['controller.render.kg_secret_held.'+str(slot)]={'arrays':{'textures':{'Array.food':['Texture.stick']+['Texture.food_'+str(i) for i in range(1,len(rows)+1)]}},'geometry':prop+' == 0 ? Geometry.part_'+str(slot)+'_0 : Geometry.part_'+str(slot)+'_1','materials':[{'*':'Material.default'}],'textures':['Array.food['+prop+']'],'part_visibility':[{'skewer_model':'v.kg_bite_stage < '+str(slot+1)}]}
 controllers['controller.render.kg_secret_held.stick']={'geometry':'Geometry.stick','materials':[{'*':'Material.default'}],'textures':['Texture.stick']}
 attach={'format_version':'1.26.0','minecraft:attachable':{'description':{'identifier':'kaleidoscope_grilling:secret_skewer','materials':{'default':'entity_alphatest_one_sided'},'textures':textures,'geometry':refs,'scripts':{'pre_animation':[],'animate':[{key:"c.is_first_person == "+str(int(key.startswith('fp')))+" && c.item_slot == '"+('main_hand' if key.endswith('right') else 'off_hand')+"'"} for key in ['fp_right','fp_left','tp_right','tp_left']]},'animations':{key:'animation.kg_a287.skewer_'+key for key in ['fp_right','fp_left','tp_right','tp_left']},'render_controllers':['controller.render.kg_secret_held.stick']+['controller.render.kg_secret_held.'+str(slot) for slot in range(3)]}}}
 # Eating aliases/dispatch are added by the one shared motion generator.
 target=RP/'attachables/secret_skewer.attachable.json'
 if target.exists():
  existing=json.loads(target.read_text())['minecraft:attachable']['description']
  for key,value in existing.get('animations',{}).items():
   if key.startswith('eat_'):attach['minecraft:attachable']['description']['animations'][key]=value
  attach['minecraft:attachable']['description']['scripts']['animate'] += [row for row in existing.get('scripts',{}).get('animate',[]) if any(k.startswith('eat_') for k in row)]
  attach['minecraft:attachable']['description']['scripts']['pre_animation']=[s for s in existing.get('scripts',{}).get('pre_animation',[]) if not s.startswith('v.kg_secret_')]
 scripts=attach['minecraft:attachable']['description']['scripts']
 scripts['initialize']=['v.kg_secret_off_hand = 0;']
 scripts['pre_animation'].append("v.kg_secret_off_hand = c.item_slot == 'off_hand';")
 for slot in range(3):
  var='v.kg_secret_ingredient_'+str(slot)
  reads=[]
  for hand in ['off','main']:
   name='kaleidoscope_grilling:secret_'+hand+'_'+str(slot)
   reads.append("(c.owning_entity->q.has_property('"+name+"') ? c.owning_entity->q.property('"+name+"') : 0)")
  scripts['initialize'].append(var+' = 0;')
  scripts['pre_animation'].append(var+' = math.floor(math.clamp((v.kg_secret_off_hand ? '+reads[0]+' : '+reads[1]+'), 0, '+str(len(rows))+'));')
 return {RP/'models/entity/secret_held.geo.json':{'format_version':'1.21.0','minecraft:geometry':geometries},RP/'render_controllers/secret_held.render_controllers.json':{'format_version':'1.8.0','render_controllers':controllers},target:attach,BP/'scripts/secret_visual_catalog.js':'// Generated, reviewed public icon slots; 0 means no supported mesh.\nexport const SECRET_VISUAL_SLOTS=Object.freeze('+json.dumps(table,separators=(',',':'),sort_keys=True)+');\n'}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 for path,value in build().items():
  data=value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n'
  if args.check:assert path.read_text()==data,path
  else:path.write_text(data)
 print('Three held ingredient slots generated; native GUI and client rendering acceptance separate')
if __name__=='__main__':main()
