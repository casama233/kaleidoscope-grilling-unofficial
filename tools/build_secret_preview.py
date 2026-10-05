"""Review-only Blockbench assembly, separate from runtime/engine acceptance."""
from pathlib import Path
from copy import deepcopy
import argparse,hashlib,importlib.util,json
from PIL import Image
from secret_skewer_assets import ROOT,model,STATES,palette_texture

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--foods',nargs=3,default=['minecraft:apple','minecraft:carrot','minecraft:beef']);p.add_argument('--shapes',nargs=3,type=int,default=[1,2,3]);p.add_argument('--style',type=int,default=0);p.add_argument('--count',type=int,default=3);p.add_argument('--runtime-export',action='store_true');a=p.parse_args()
 assert all(1<=v<=3 for v in a.shapes)and 0<=a.style<=6 and 0<=a.count<=3
 state=sum(a.shapes[i]*(16,4,1)[i]for i in range(a.count))
 rp=ROOT/'projects/grilling/gameplay_core/resource_pack';catalog=json.loads((ROOT/'development/gameplay_core/fixtures/secret-food-palettes.json').read_text());slots={r['id']:r['index']for r in catalog['items']}
 atlas=Image.new('RGBA',(784,96));placements={'preview:shaft':{'x':0,'y':0,'width':16,'height':16}};atlas.paste(Image.open(rp/'textures/secret_skewer_stick.png').convert('RGBA'),(0,0))
 doc={'textures':{'stick':'preview:shaft'},'elements':[]}
 runtime_path=rp/'models/entity/secret_held.geo.json'
 runtime_geometries={g['description']['identifier']:g for g in json.loads(runtime_path.read_text())['minecraft:geometry']}
 def reverse(c,texture,name,width,height):
  o,z=c['origin'],c['size'];fr=[8-o[0]-z[0],o[1]-24,o[2]+8];to=[fr[i]+z[i]for i in range(3)]
  element={'name':name,'from':fr,'to':to,'faces':{}}
  for face,data in c['uv'].items():
   u0,v0=data['uv'];du,dv=data['uv_size'];u1,v1=u0+du,v0+dv
   if face in ('up','down'):u0,v0,u1,v1=u1,v1,u0,v0
   f={'texture':texture,'uv':[u0*16/width,v0*16/height,u1*16/width,v1*16/height]}
   if data.get('uv_rotation'):f['rotation']=data['uv_rotation']
   element['faces'][face]=f
  if 'rotation'in c:
   angles=c['rotation'];axis=next(i for i,v in enumerate(angles)if v);pivot=c['pivot']
   element['rotation']={'angle':angles[axis]*(-1 if axis<2 else 1),'axis':'xyz'[axis],'origin':[8-pivot[0],pivot[1]-24,pivot[2]+8]}
  return element
 if a.runtime_export:
  shaft=runtime_geometries['geometry.kg_secret_held.stick'];doc['elements']=[reverse(c,'#stick','runtime_shaft_'+str(i),16,16)for i,c in enumerate(shaft['bones'][2]['cubes'])]
 else:doc['elements']=[deepcopy(model(21)['elements'][0])]
 for slot,(identifier,shape)in enumerate(zip(a.foods[:a.count],a.shapes[:a.count])):
  texture='preview:food_'+str(slot);x=16+slot*256
  placements[texture]={'x':x,'y':0,'width':256,'height':96};doc['textures']['food_'+str(slot)]=texture
  atlas.paste(Image.open(rp/(palette_texture(slots[identifier],a.style)+'.png')).convert('RGBA'),(x,0))
  if a.runtime_export:
   geo=runtime_geometries[f'geometry.kg_secret_held.'+('state_'if a.count==3 else 'partial_state_')+f'{state}_{slot}'];width=geo['description']['texture_width'];height=geo['description']['texture_height']
   doc['elements'] += [reverse(c,'#food_'+str(slot),f'runtime_slot_{slot}_cell_{i}',width,height)for i,c in enumerate(geo['bones'][2]['cubes'])]
  else:
   for e in model(state)['elements']:
    if not any('tintindex'in f for f in e['faces'].values()):continue
    if next(iter(e['faces'].values()))['tintindex']//128!=slot:continue
    e=deepcopy(e)
    for f in e['faces'].values():
     local=f.pop('tintindex')%128;cell=local%16;face=local//16;u0,v0,u1,v1=f['uv']
     f['uv']=[(u0+cell*16)*16/256,(v0+face*16)*16/96,(u1+cell*16)*16/256,(v1+face*16)*16/96];f['texture']='#food_'+str(slot)
    doc['elements'].append(e)
 a.output.parent.mkdir(parents=True,exist_ok=True);png=a.output.with_suffix('.png');atlas.save(png)
 spec=importlib.util.spec_from_file_location('java_asset_export',ROOT/'projects/grilling/tools/build_assets.py');exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
 exporter.inspect_model(doc,allow_native_uv_rotation=True)
 out=exporter.editable_model(doc,'Secret_Apple_Carrot_Beef_'+('runtime_export_preview' if a.runtime_export else 'source_preview'),placements,png,[[0,0]])
 a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 receipt={'preview_only':True,'runtime_acceptance':False,'foods':a.foods,'shapes':a.shapes,'style':a.style,'cubes':len(doc['elements']),'ingredient_count':a.count,'joint_source_state':state,'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),'source_pin':'9a1acdab27698457bec16c9362678e574895a28c','input_kind':'actual_exported_bedrock_geometry_inverse_mapped'if a.runtime_export else 'pinned_java_source_assembly','held_offset_removed':24,'runtime_geometry_sha256':hashlib.sha256(runtime_path.read_bytes()).hexdigest()}
 a.output.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
