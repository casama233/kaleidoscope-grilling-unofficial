"""Import selected original 1.21.1 fatal-skewer sprites and author particle parameters.

Only selected sprites are exported. Native integrator/collision and client mixing
remain platform adaptations, not renderer equivalence.
"""
from pathlib import Path
import argparse,copy,hashlib,io,json,zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
RP=ROOT/'projects/grilling/gameplay_core/resource_pack'
def main():
 p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True);a=p.parse_args()
 meta=json.loads((a.reference/'minecraft-1.21.1-metadata.json').read_text());jar=a.reference/'minecraft-1.21.1-client.jar'
 assert meta['id']=='1.21.1'
 assert hashlib.sha1(jar.read_bytes()).hexdigest()==meta['downloads']['client']['sha1']
 files=[]
 with zipfile.ZipFile(jar) as z:
  def read(name):
   raw=z.read('assets/minecraft/textures/particle/'+name+'.png');files.append({'asset':name,'sha256':hashlib.sha256(raw).hexdigest()});return raw
  raw=read('damage');(RP/'textures/particle/kg_java_damage.png').write_bytes(raw)
  smoke=[Image.open(io.BytesIO(read('generic_'+str(i)))).convert('RGBA') for i in range(7,-1,-1)]
  w,h=smoke[0].size;assert all(im.size==(w,h) for im in smoke)
  atlas=Image.new('RGBA',(w*8,h))
  for i,im in enumerate(smoke):atlas.paste(im,(i*w,0))
  atlas.save(RP/'textures/particle/kg_java_smoke.png')
 for name,base,texture in [('damage_indicator','basic_crit','kg_java_damage'),('large_smoke','basic_smoke','kg_java_smoke')]:
  data=json.loads((RP/('particles/feedback_'+base+'.json')).read_text());e=data['particle_effect'];c=e['components'];e['description']['identifier']='kaleidoscope_grilling:feedback_'+name;e['description']['basic_render_parameters']['texture']='textures/particle/'+texture
  view=c['minecraft:particle_appearance_billboard'];view.pop('direction',None)
  if name=='damage_indicator':
   view['uv']={'texture_width':8,'texture_height':8,'uv':[0,0],'uv_size':[8,8]}
   view['size']=['(.075 + variable.particle_random_1*.075) * math.clamp(variable.particle_age * 32,0,1)']*2
   c['minecraft:particle_lifetime_expression']={'max_lifetime':1}
   c['minecraft:particle_appearance_tinting']={'color':['.6 + variable.particle_random_2*.3','(.6 + variable.particle_random_2*.3)*math.pow(.96,variable.particle_age*20+1)','(.6 + variable.particle_random_2*.3)*math.pow(.9,variable.particle_age*20+1)',1]}
   c['minecraft:particle_motion_dynamic']={'linear_acceleration':[0,-8,0],'linear_drag_coefficient':-20*__import__('math').log(.7)}
   # DamageIndicatorProvider adds one block/tick Y before Crit scales by .4.
   c['minecraft:emitter_shape_point']['direction']=['variable.kg_velocity.x*.4','variable.kg_velocity.y*.4+8','variable.kg_velocity.z*.4']
   vec=c['minecraft:emitter_shape_point']['direction'];c['minecraft:particle_initial_speed']='math.sqrt('+ ' + '.join('('+v+') * ('+v+')' for v in vec)+')'
  else:
   view['uv']={'texture_width':w*8,'texture_height':h,'uv':[0,0],'uv_size':[w,h],'flipbook':{'base_UV':[0,0],'size_UV':[w,h],'step_UV':[w,0],'max_frame':8,'stretch_to_lifetime':True}}
   view['size']=['(.1875 + variable.particle_random_1*.1875) * math.clamp(variable.particle_age/variable.particle_lifetime*32,0,1)']*2
   c['minecraft:particle_lifetime_expression']={'max_lifetime':'math.max(1,math.floor(20/(variable.particle_random_2*.8+.2)))/20'}
   c['minecraft:particle_appearance_tinting']={'color':['variable.particle_random_3*.3']*3+[1]}
   c['minecraft:particle_motion_dynamic']={'linear_acceleration':[0,1.6,0],'linear_drag_coefficient':-20*__import__('math').log(.96)}
  (RP/('particles/feedback_'+name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
 proof={'schema':1,'minecraft':'1.21.1','metadata_origin':'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json','client_sha1':meta['downloads']['client']['sha1'],'sprites':files,'source_classes':['CritParticle.DamageIndicatorProvider','CritParticle','LargeSmokeParticle','SmokeParticle','BaseAshSmokeParticle'],'adaptations':['Bedrock continuous particle integrator instead of Java tick integrator','Smoke collision and initial engine velocity jitter remain unverified'],'client':False}
 (ROOT/'development/gameplay_core/fixtures/java-ordinary-particles-1.21.1.json').write_text(json.dumps(proof,indent=2)+'\n')
if __name__=='__main__':main()
