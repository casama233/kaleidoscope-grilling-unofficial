"""Build a separate A1.15 animation rehearsal, preserving all previous project assets.
No external source code is executed. Original motion sources/audio are pinned by commit.
"""
from __future__ import annotations
import argparse,base64,copy,hashlib,io,json,math,re,shutil,struct,subprocess,sys,uuid,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling'
D=P/'integration/immersion_lab'
REPORT=P/'reports/immersion_a115'
PIN='9a1acdab27698457bec16c9362678e574895a28c'
NS='kaleidoscope_grilling'
COMMON='common/src/main/resources/assets/'+NS+'/'
JAVA='forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/'
SOURCE_FILES={
 'grill/GrillRenderer.java':'41e208c8fbd229f08becb3a2a2045e0a26cca6d6',
 'grill/GrillLoopSound.java':'0bb6a4d975afda3ff479ad88570f447c7223019a',
 'grill/GrillBlock.java':'b3f4784635d631a239a471642770b105977ee2d6',
 'oil/OilBrushAnimation.java':'63d637c4a015a32f1205fe12552ae37541e95fc9',
 'oil/OilBrushFirstPersonAnimation.java':'e896e64e6d3c24bd611ac26d3fd9126ec8feacdd',
 'seasoning/SeasoningAnimation.java':'845bd93d74049f36c247a52e7e3f5dcf5f611c69',
 'seasoning/SeasoningFirstPersonAnimation.java':'3beee2c8a8cb14c1108a98dfdcc421b158208586',
 'mixin/HumanoidAnvilPressMixin.java':'52fa7c496e6f41ccb2c19690ed3e869587c15891',
 'skewer/SkewerEatingAnimation.java':'ab2598cbd3fe18c7b11e61fedd3bbd9e0ce74ca3',
 'skewer/MultiBiteSkewerItem.java':'a24c67d0bb6c66446598d1338dcd1504e386bc0c',
 'skewer/EnderPearlEatingAnimation.java':None,
 'mixin/ItemInHandSkewerEatingMixin.java':None,
 'client/ClientSkewerEatingSound.java':None,
 'registry/ModSounds.java':None,
}
def h(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 if isinstance(data,(dict,list)):data=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
 if isinstance(data,bytes):path.write_bytes(data)
 else:path.write_text(data,encoding='utf-8')
def uid(name):return str(uuid.uuid5(uuid.NAMESPACE_URL,'https://github.com/casama233/kaleidoscope-grilling-unofficial/immersion-lab/'+name))
def arrays(text):
 return {name:[float(x.strip().rstrip('Ff')) for x in content.split(',') if x.strip()] for name,content in re.findall(r'float\[\]\s+(\w+)\s*=\s*\{([^}]+)\}',text,re.S)}
def sample(t,times,values):
 if t<=times[0]:return values[0]
 if t>=times[-1]:return values[-1]
 right=next(i for i,v in enumerate(times) if v>=t);left=right-1;u=(t-times[left])/(times[right]-times[left]);p0=values[max(0,left-1)];p1=values[left];p2=values[right];p3=values[min(len(values)-1,right+1)]
 return .5*((2*p1)+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u*u+(-p0+3*p1-3*p2+p3)*u*u*u)
def polynomial(t,times,values):
 if t<=times[0]:return values[0]
 for i in range(len(times)-1):
  if t<=times[i+1]:
   p=np.array([values[max(0,i-1)],values[i],values[i+1],values[min(len(values)-1,i+2)]])
   coefficients=np.array([[0,2,0,0],[-1,0,1,0],[2,-5,4,-1],[-1,3,-3,1]])@p/2
   u=(t-times[i])/(times[i+1]-times[i]);return sum(float(c)*u**k for k,c in enumerate(coefficients))
 return values[-1]
def vorbis_duration(data):
 ident=data.find(b'\x01vorbis')
 if ident<0:raise ValueError('Expected Vorbis')
 rate=struct.unpack_from('<I',data,ident+12)[0];last=0;offset=0
 while offset<len(data):
  if data[offset:offset+4]!=b'OggS':raise ValueError('Bad Ogg page')
  count=data[offset+26];size=sum(data[offset+27:offset+27+count]);g=struct.unpack_from('<Q',data,offset+6)[0]
  if g!=2**64-1:last=max(last,g)
  offset+=27+count+size
 return last/rate

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--upstream',type=Path,required=True);args=ap.parse_args();up=args.upstream
 guard=json.loads((ROOT/'.repo-target.json').read_text());assert guard['repository']=='casama233/kaleidoscope-grilling-unofficial' and guard['repository_id']==1377218440
 # Only this new, generated laboratory may be rebuilt. Never touch the main RP, guide or notebook.
 baseline={str(p.relative_to(P)):h(p.read_bytes()) for sub in ['resource_pack','editor/generated','source_snapshots','integration/cookery106'] for p in (P/sub).rglob('*') if p.is_file()}
 if D.exists():shutil.rmtree(D)
 D.mkdir(parents=True);REPORT.mkdir(parents=True,exist_ok=True)
 provenance=[]
 def source(path,expected=None):
  value=(up/path).read_bytes()
  if expected and blob(value)!=expected:raise ValueError('Source changed: '+path)
  write(D/'sources'/path,value)
  provenance.append({'path':path,'git_blob':blob(value),'sha256':h(value),'url':f'https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/{PIN}/{path}'})
  return value
 texts={name:source(JAVA+name,expected).decode('utf-8-sig') for name,expected in SOURCE_FILES.items()}
 meta={}
 for which in ['SkewerEatingAnimation','EnderPearlEatingAnimation']:
  a=arrays(texts['skewer/'+which+'.java']);meta[which]={'arrays':a,'source':JAVA+'skewer/'+which+'.java'}
 profiles={name:{'duration_ticks':int(duration),'bite_seconds':[float(x.strip().rstrip('Ff')) for x in bits.split(',')]} for name,duration,bits in re.findall(r'\b(ONE|TWO|THREE|THREE_ALT|THREE_RANDOM|FOUR)\((\d+),\s*([^)]*)\)',texts['skewer/MultiBiteSkewerItem.java'])}
 assert len(profiles)==6 and profiles['FOUR']['duration_ticks']==90
 write(D/'motion/source_curves.json',{'source_commit':PIN,'coordinate_space':'Unretargeted Java authored pose channels; not native player bindings','profiles':profiles,'curves':meta})
 # Bake only the authored scalar channels, with an explicit retargeting boundary.
 tracks={};checks=0;max_error=0
 for cls,entry in meta.items():
  a=entry['arrays'];cls_tracks={}
  for name,values in a.items():
   if name.endswith('TIMES'):continue
   prefix=name.rsplit('_',1)[0]
   choices=[name+'_TIMES',prefix+'_TIMES',prefix.replace('_ROT','')+'_TIMES']
   if name.startswith('SECOND_ITEM_'):choices+=['SECOND_ITEM_TRANSFORM_TIMES']
   if name.endswith('_SCALE'):choices=[name+'_TIMES']+choices
   times=next((a[k] for k in choices if k in a and len(a[k])==len(values)),None)
   if times is None:continue
   samples=sorted(set(times+[i/120 for i in range(601) if times[0]<=i/120<=times[-1]]))
   vals=[sample(t,times,values) for t in samples]
   for t in np.linspace(times[0],times[-1],701):
    error=abs(sample(t,times,values)-polynomial(t,times,values));max_error=max(max_error,error);checks+=1
   cls_tracks[name]={'keys':{f'{t:.8f}':v for t,v in zip(samples,vals)},'kind':'unretargeted scalar reference'}
  tracks[cls]=cls_tracks
 write(D/'motion/sampled_reference_tracks.json',tracks)
 # Retain original audio and per-sound definition options. Eating files are Forge-specific.
 defs=json.loads(source(COMMON+'sounds.json'));audio={};sound_defs={}
 forge_sounds=up/'forge-1.20.1/src/main/resources/assets/kaleidoscope_grilling'
 if (forge_sounds/'sounds.json').exists():defs.update(json.loads(source('forge-1.20.1/src/main/resources/assets/kaleidoscope_grilling/sounds.json')))
 wanted=['grill_flip','grill_loop','pickup_item','season','shake_seasoning','one_skewer_eat','two_skewer_eat','three_skewer_eat','four_skewer_eat']
 for event in wanted:
  if event not in defs:raise ValueError('Missing event '+event)
  converted=[]
  for entry in defs[event]['sounds']:
   d={'name':entry} if isinstance(entry,str) else dict(entry)
   name=d['name'].split(':')[-1];rel=COMMON+'sounds/'+name+'.ogg'
   if not (up/rel).exists():rel='forge-1.20.1/src/main/resources/assets/kaleidoscope_grilling/sounds/'+name+'.ogg'
   raw=source(rel);write(D/'resource_pack/sounds/kg_imm'/f'{name}.ogg',raw)
   audio[event]={'duration':vorbis_duration(raw),'source':rel}
   d['name']='sounds/kg_imm/'+name;converted.append(d)
  sound_defs['kg_imm.'+event]={'category':'block' if 'eat' not in event else 'player','sounds':converted}
 for i in range(8):sound_defs['kg_imm.four_skewer_eat_ch'+str(i)]=copy.deepcopy(sound_defs['kg_imm.four_skewer_eat'])
 write(D/'resource_pack/sounds/sound_definitions.json',{'format_version':'1.14.0','sound_definitions':sound_defs})
 write(D/'behavior_pack/scripts/audio.js','export const AUDIO='+json.dumps(audio)+';\n')
 for n in ['flow.js','main.js']:shutil.copyfile(Path(__file__).parent/n,D/'behavior_pack/scripts'/n)
 write(D/'behavior_pack/scripts/package.json',{'type':'module','private':True})
 # One deterministic atlas: copy existing texels exactly, never resample imported textures.
 existing=json.loads((P/'reports/build-report.json').read_text());records={r['name']:r for r in existing['candidates']}
 names=['grill_flat','grill_flat_lit','beef_raw','beef_stage_1','beef_stage_2','beef_stage_3','beef_cooked','beef_burnt']+['beef_cooked_bite_'+str(i) for i in range(1,5)]+['seasoning_v0_r8']
 textures={n:Image.open(P/records[n]['atlas']).convert('RGBA') for n in names}
 rawbrush=source(COMMON+'textures/item/canola_oil_brush.png');textures['brush']=Image.open(io.BytesIO(rawbrush)).convert('RGBA')
 width=256;positions={};x=y=0;rowheight=0
 for n,im in textures.items():
  if x+im.width>width:x=0;y+=rowheight;rowheight=0
  positions[n]=(x,y);x+=im.width;rowheight=max(rowheight,im.height)
 height=2**math.ceil(math.log2(y+rowheight));atlas=Image.new('RGBA',(width,height))
 for n,im in textures.items():atlas.paste(im,positions[n]);assert np.array_equal(np.asarray(atlas)[positions[n][1]:positions[n][1]+im.height,positions[n][0]:positions[n][0]+im.width],np.asarray(im))
 write(D/'resource_pack/textures/kg_imm/.keep','');atlas.save(D/'resource_pack/textures/kg_imm/scene.png')
 bones=[{'name':'root','pivot':[0,0,0]}];visibility=[]
 def rootbone(name,pivot=(0,0,0),parent='root'):bones.append({'name':name,'parent':parent,'pivot':list(pivot)})
 def append_model(n,prefix,parent,offset=(0,0,0)):
  g=json.loads((P/records[n]['geometry']).read_text())['minecraft:geometry'][0];dx,dy=positions[n]
  for b in g['bones']:
   if b['name']=='root':continue
   b=copy.deepcopy(b);b['name']=prefix+'_'+b['name'];b['parent']=parent if b.get('parent')=='root' else prefix+'_'+b['parent']
   b['pivot']=[v+d for v,d in zip(b.get('pivot',[0,0,0]),offset)]
   for c in b.get('cubes',[]):
    c['origin']=[v+d for v,d in zip(c['origin'],offset)]
    if 'pivot' in c:c['pivot']=[v+d for v,d in zip(c['pivot'],offset)]
    for f in c['uv'].values():f['uv']=[f['uv'][0]+dx,f['uv'][1]+dy]
   bones.append(b)
 for n,l in [('grill_flat',0),('grill_flat_lit',1)]:
  rootbone('body'+str(l));append_model(n,n,'body'+str(l))
 for slot in range(3):
  sx=5-slot*5;rootbone('slot'+str(slot),[sx,5,-1.75])
  for stage,n in enumerate(names[2:8]):
   rootbone(f'slot{slot}_stage{stage}',parent='slot'+str(slot));append_model(n,f's{slot}_{stage}',f'slot{slot}_stage{stage}',[sx,4,0])
 rootbone('held',[12,5,0]);
 for bite,n in enumerate(['beef_cooked']+['beef_cooked_bite_'+str(i) for i in range(1,5)]):
  rootbone('bite'+str(bite),parent='held');append_model(n,'held'+str(bite),'bite'+str(bite),[12,6,0])
 rootbone('season_tool',[0,0,0]);append_model('seasoning_v0_r8','season','season_tool')
 rootbone('brush_tool',[0,0,0]);dx,dy=positions['brush'];brush=textures['brush'];cubes=[]
 # Per-pixel extrusion is explicitly derived from a generated-item sprite, not an invented authored 3-D brush.
 for iy in range(brush.height):
  for ix in range(brush.width):
   if brush.getpixel((ix,iy))[3]<1:continue
   uv={k:{'uv':[dx+ix,dy+iy],'uv_size':[1,1]} for k in ['north','east','south','west','up','down']}
   cubes.append({'origin':[7-ix,15-iy,-.5],'size':[1,1,1],'uv':uv})
 bones.append({'name':'brush_pixels','parent':'brush_tool','pivot':[0,0,0],'cubes':cubes})
 geometry={'format_version':'1.21.0','minecraft:geometry':[{'description':{'identifier':'geometry.kg_imm.rehearsal','texture_width':width,'texture_height':height,'visible_bounds_width':5,'visible_bounds_height':5,'visible_bounds_offset':[0,1,0]},'bones':bones}]}
 write(D/'resource_pack/models/entity/rehearsal.geo.json',geometry)
 # The timed transforms operate on the same bones that the actual Bedrock client entity uses.
 animations={'body0':{'scale':'1-v.lit'},'body1':{'scale':'v.lit'},'held':{'scale':'v.held'},'brush_tool':{'scale':'0.42*v.brush','position':['4*math.sin(v.t*360)',10,0],'rotation':[-24,0,'32+34*math.sin(v.t*360)']},'season_tool':{'scale':'0.48*v.season','position':['1.28*math.sin(v.t*1440)','10+1.6*math.sin(v.t*360)',0],'rotation':['-28+42*math.sin(v.t*360)','18*math.sin(v.t*1440)','202+25*math.sin(v.t*1440)']}}
 for slot in range(3):
  animations['slot'+str(slot)]={'position':[0,f'16*v.flip*v.h{slot}*math.sin(180*math.clamp(v.t/0.7,0,1))',0],'rotation':[0,0,'180*v.flips-180*v.flip*(1-math.clamp(v.t/0.7,0,1))']}
  for stage in range(6):animations[f'slot{slot}_stage{stage}']={'scale':f'v.loaded*(v.stage=={stage})'}
 for i in range(5):animations['bite'+str(i)]={'scale':f'v.bites=={i}'}
 write(D/'resource_pack/animations/rehearsal.animation.json',{'format_version':'1.8.0','animations':{'animation.kg_imm.rehearsal':{'loop':True,'bones':animations}}})
 properties={k:{'type':'bool','default':False,'client_sync':True} for k in ['lit','loaded','held']}
 for k,hi in [('stage',5),('flips',4),('bites',4),('serial',1000000)]:properties[k]={'type':'int','range':[0,hi],'default':0,'client_sync':True}
 properties['action']={'type':'int','range':[0,4],'default':0,'client_sync':True}
 properties['seconds']={'type':'float','range':[0,5],'default':0,'client_sync':True}
 for i in range(3):properties['height'+str(i)]={'type':'float','range':[.28,.38],'default':[.28,.33,.38][i],'client_sync':True}
 write(D/'behavior_pack/entities/rehearsal.json',{'format_version':'1.21.0','minecraft:entity':{'description':{'identifier':'kg_imm:rehearsal','is_spawnable':True,'is_summonable':True,'properties':{'kg_imm:'+k:v for k,v in properties.items()}},'components':{'minecraft:type_family':{'family':['kg_imm_rehearsal']},'minecraft:health':{'value':10,'max':10},'minecraft:collision_box':{'width':1,'height':.65},'minecraft:physics':{'has_gravity':False,'has_collision':True},'minecraft:pushable':{'is_pushable':False,'is_pushable_by_piston':False},'minecraft:persistent':{},'minecraft:interact':{'interactions':[{'on_interact':{'event':'kg_imm:tap','target':'self'},'interact_text':'action.interact.kg_imm.step','swing':True}]}},'events':{'kg_imm:tap':{}}}})
 assignments=["v.raw=q.property('kg_imm:seconds');","v.a=q.property('kg_imm:action');","v.serial=q.property('kg_imm:serial');","v.limit=(v.a==1)?1:((v.a==2)?0.7:((v.a==3)?0.5:4.5));","v.t=math.min(v.limit,(v.raw!=v.last_raw || v.a!=v.last_a || v.serial!=v.last_serial) ? v.raw : math.min(v.raw+0.05,v.t+q.delta_time));","v.last_raw=v.raw;v.last_a=v.a;v.last_serial=v.serial;"]
 assignments+= [f"v.{k}=q.property('kg_imm:{k}');" for k in ['lit','loaded','held','stage','flips','bites']]
 assignments+= [f"v.h{i}=q.property('kg_imm:height{i}');" for i in range(3)]+[f"v.{k}=(v.a=={i});" for k,i in [('flip',2),('brush',1),('season',3)]]
 write(D/'resource_pack/entity/rehearsal.entity.json',{'format_version':'1.10.0','minecraft:client_entity':{'description':{'identifier':'kg_imm:rehearsal','materials':{'default':'entity_alphablend'},'textures':{'default':'textures/kg_imm/scene'},'geometry':{'default':'geometry.kg_imm.rehearsal'},'animations':{'scene':'animation.kg_imm.rehearsal'},'scripts':{'initialize':['v.t=0;v.last_raw=-1;v.last_a=0;v.last_serial=-1;'],'pre_animation':assignments,'animate':['scene']},'render_controllers':['controller.render.kg_imm.rehearsal'],'spawn_egg':{'base_color':'#4b3528','overlay_color':'#eaa94d'}}}})
 write(D/'resource_pack/render_controllers/rehearsal.render_controllers.json',{'format_version':'1.8.0','render_controllers':{'controller.render.kg_imm.rehearsal':{'geometry':'Geometry.default','materials':[{'*':'Material.default'}],'textures':['Texture.default']}}})
 write(D/'resource_pack/texts/languages.json',['en_US','zh_TW','zh_CN'])
 for lang,title in [('en_US','Grilling motion rehearsal (not survival gameplay)'),('zh_TW','煙火動效驗收台（非生存玩法）'),('zh_CN','烟火动效验收台（非生存玩法）')]:write(D/f'resource_pack/texts/{lang}.lang',f'entity.kg_imm:rehearsal.name={title}\nitem.spawn_egg.entity.kg_imm:rehearsal.name={title}\naction.interact.kg_imm.step=Next motion / 下一步\n')
 for pack in ['resource_pack','behavior_pack']:
  modules=[{'type':'resources' if pack=='resource_pack' else 'data','uuid':uid(pack+'-module'),'version':[0,1,15]}]
  manifest={'format_version':2,'header':{'name':'Grilling A1.15 • Immersion rehearsal '+('RP' if pack=='resource_pack' else 'BP'),'description':'動效驗收台；不耗材、不給食物、不取代Cookery或玩家外觀。','uuid':uid(pack),'version':[0,1,15],'min_engine_version':[1,26,50]},'modules':modules}
  if pack=='behavior_pack':
   modules.append({'type':'script','language':'javascript','entry':'scripts/main.js','uuid':uid('script'),'version':[0,1,15]});manifest['dependencies']=[{'uuid':uid('resource_pack'),'version':[0,1,15]},{'module_name':'@minecraft/server','version':'2.10.0'}]
  write(D/pack/'manifest.json',manifest)
  icon=textures['grill_flat_lit'].resize((192,192),Image.Resampling.NEAREST);icon.save(D/pack/'pack_icon.png')
  write(D/pack/'THIRD_PARTY_NOTICES.txt','Original Grilling source code: BSD-3-Clause; original textures/models/audio: CC BY-NC-SA 4.0.\nSources: breezeth-CN/KaleidoscopeGrilling '+PIN+'; grill models from the previously attributed Arbousier1 fork.\nChanges: timed Bedrock rehearsal, atlas packing, sprite extrusion, particles mapped to native Bedrock equivalents.\nNo endorsement. No Cookery original bundle or private scripts included.\nhttps://creativecommons.org/licenses/by-nc-sa/4.0/legalcode\n')
 write(D/'config.json',{'type':'minecraftBedrock','name':'Grilling A1.15 Immersion Lab','targetVersion':'1.26.50','namespace':'kg_imm','packs':{'behaviorPack':'./behavior_pack','resourcePack':'./resource_pack'},'compiler':{'plugins':[['simpleRewrite',{'packName':'KG_Immersion_Lab_A115'}]]}})
 for pack in ['resource_pack','behavior_pack']:
  for n in ['LICENSE-CODE','LICENSE-ASSETS','NOTICE']:
   if (up/n).exists():write(D/pack/(n+'.txt'),(up/n).read_bytes())
  write(D/pack/'ATTRIBUTION.txt',(P/'ATTRIBUTION.md').read_bytes())
 source_poses={'first_person_brush':'OilBrushFirstPersonAnimation.java — absolute camera transform preserved in source, fixture anchor differs','first_person_season':'SeasoningFirstPersonAnimation.java — preserves extra Z 180-degree inversion','third_person_arms':'HumanoidAnvilPressMixin.java — source radians retained; native player binding pending','eating':'6 duration/bite profiles; both SkewerEatingAnimation and EnderPearlEatingAnimation channels preserved; active/helper hand retarget pending'}
 write(D/'motion/retargeting_boundary.json',source_poses)
 write(D/'sources/manifest.json',provenance)
 write(REPORT/'source_checks.json',{'pinned_source_count':len(provenance),'scalar_curve_checks':checks,'max_catmull_formula_difference':max_error,'source_profiles':profiles,'reference_track_count':sum(len(v) for v in tracks.values()),'native_player_bound':False})
 # Full detailed visual checks and packaging are isolated from source generation.
 from preview import make_preview
 preview_results=make_preview(P,D,REPORT,records,animations)
 result={'version':'A1.15.0','scope':'separate interactive animation rehearsal, not full gameplay','base_candidate_count':existing['candidate_count'],'new_action_scene_count':1,'unchanged_baseline_files':len(baseline),'source_count':len(provenance),'audio_events':len(wanted),'isolated_eating_audio_channels':8,'unique_audio_files':len(list((D/'resource_pack/sounds/kg_imm').glob('*.ogg'))),'scalar_curve_checks':checks,'max_catmull_formula_difference':max_error,'new_eating_source_profiles':len(profiles),'reference_track_count':sum(len(v) for v in tracks.values()),'preview':preview_results,'minecraft_tested':False,'native_player_skin_hand_binding_tested':False,'bridge_ui_tested':False,'full_grilling_gameplay':False}
 for name,value in baseline.items():assert h((P/name).read_bytes())==value,'Baseline mutated: '+name
 test=subprocess.run(['node',str(Path(__file__).parent/'test.mjs')],capture_output=True,text=True,check=True);write(REPORT/'flow-tests.log',test.stdout);result['flow_tests']=json.loads(test.stdout.strip().splitlines()[-1])
 rt=subprocess.run(['node','--experimental-vm-modules',str(Path(__file__).parent/'test_runtime.mjs')],capture_output=True,text=True,check=True);write(REPORT/'runtime-tests.log',rt.stdout);result['runtime_tests']=json.loads(rt.stdout.strip().splitlines()[-1]);result['flip_height_rng']='Server-selected random heights in original 0.28–0.38 range; Java per-position RNG sequence not reproduced'
 write(REPORT/'verification.json',result)
 write(D/'README.zh-TW.md','''# 煙火 A1.15 動效驗收台\n\n這是獨立展示附加包，不是生存玩法。沒有材料消耗、食物取得、營養或配方變更，不需要Cookery，不新增指南書，不覆蓋player.json。\n\n在複製的創造測試世界啟用BP/RP後，使用刷怪蛋或 `/summon kg_imm:rehearsal`。空手互動依序點火、上三串、刷油、四次翻面、撒料、取串、四口進食展示、重置。忙碌時不接受重複動作。蹲下互動在忙碌時取消動作，閒置時重置驗收台。\n\n原作時序：刷油1秒、翻面0.7秒與180度及0.28–0.38格拋高、撒料0.5秒兩次抖動，牛肉四口進食90ticks。聲音使用原OGG，取空／離開／移除後停止烤肉聲。煙霧火焰映射基岩版原生粒子，不稱為像素相同。\n\n工具在展示台的固定位置、浮空分口樣本是驗收用配置，不是已還原的玩家手部位置。所有原作食用曲線与雙手資料保存在motion/；尚未完成原生第一／第三人稱玩家骨骼綁定。展示台不包含焦化失敗、油量、真實食用結算等正式玩法。\n\n原作GPL? 不適用；原碼BSD-3-Clause，素材依原授權CC BY-NC-SA 4.0。確切来源見sources/manifest.json與主工程ATTRIBUTION。\n'''.replace('原作GPL? 不適用；',''))
 artifacts=ROOT/'artifacts';artifacts.mkdir(exist_ok=True)
 with zipfile.ZipFile(artifacts/'Grilling_Immersion_Lab_A1.15.mcaddon','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for pack in ['behavior_pack','resource_pack']:
   for f in sorted((D/pack).rglob('*')):
    if f.is_file() and not f.name.startswith('.') and f.name!='package.json':z.write(f,f'{pack}/'+f.relative_to(D/pack).as_posix())
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
