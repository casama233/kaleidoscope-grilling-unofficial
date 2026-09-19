"""Decode the exported animated skeleton; compare flip frames to the independent Java-source path."""
from pathlib import Path
import base64,collections,copy,io,json,math,re,sys
import numpy as np
from PIL import Image,ImageDraw

def evaluate(x,v):
 if isinstance(x,(int,float)):return x
 if isinstance(x,list):return [evaluate(i,v) for i in x]
 if not re.fullmatch(r'[a-z0-9_.+*/()\-,<>= !]+',x):raise ValueError('Unknown generated expression')
 x=re.sub(r'\bv\.(\w+)',lambda m:str(float(v[m[1]])),x)
 x=x.replace('math.sin','dsin').replace('math.clamp','clamp')
 return float(eval(x,{'__builtins__':{}},{'dsin':lambda z:math.sin(math.radians(z)),'clamp':lambda z,a,b:min(b,max(a,z))}))

def make_preview(P,D,out,records,animations):
 sys.path.insert(0,str(P/'tools'));import audit_multiview as A
 specs={r['name']:r for r in json.loads((P/'config/asset_specs.json').read_text())['candidates']}
 doc=json.loads((D/'resource_pack/models/entity/rehearsal.geo.json').read_text())['minecraft:geometry'][0]
 tex=np.asarray(Image.open(D/'resource_pack/textures/kg_imm/scene.png').convert('RGBA'))
 bones={b['name']:b for b in doc['bones']};cache={}
 def vars(mode='idle',t=0,flips=0,stage=0,loaded=1,held=0,bites=0,lit=1):return {'t':t,'lit':lit,'flips':flips,'flip':mode=='flip','brush':mode=='brush','season':mode=='season','stage':stage,'loaded':loaded,'held':held,'bites':bites,'h0':.28,'h1':.33,'h2':.38}
 def native(v):
  matrices={};shown={};faces=[]
  for name,b in bones.items():
   parent=b.get('parent');prior=matrices[parent] if parent else np.eye(4)
   anim=animations.get(name,{});sc=evaluate(anim.get('scale',1),v);sc=np.array([sc]*3) if np.isscalar(sc) else np.array(sc)
   active=(shown.get(parent,True) and bool(np.any(sc)))
   shown[name]=active
   p=b.get('pivot',[0,0,0]);p=np.array([8-p[0],p[1],p[2]+8]);r=evaluate(anim.get('rotation',[0,0,0]),v);r=A.rotation([-r[0],-r[1],r[2]])
   pos=evaluate(anim.get('position',[0,0,0]),v);pos=np.array([-pos[0],pos[1],pos[2]])
   m=np.eye(4);m[:3,:3]=r@np.diag(sc);m[:3,3]=p+pos-m[:3,:3]@p;matrices[name]=prior@m
   if not active:continue
   for c in b.get('cubes',[]):
    o=np.array(c['origin']);s=np.array(c['size']);a=np.array([8-o[0]-s[0],o[1],o[2]+8]);z=a+s
    pivot=c.get('pivot',[0,0,0]);pivot=np.array([8-pivot[0],pivot[1],pivot[2]+8]);r=c.get('rotation',[0,0,0]);r=A.rotation([-r[0],-r[1],r[2]])
    for face,f in c['uv'].items():
     lo=np.array(f['uv']);hi=lo+np.array(f['uv_size']);
     if face in ('up','down'):lo,hi=hi,lo
     uv=np.roll(A.rectangle([*lo,*hi]),-int(f.get('uv_rotation',0)//90),axis=0)
     points=(A.vertices(a,z,face)-pivot)@r.T+pivot;hom=np.c_[points,np.ones(4)];points=(hom@matrices[name].T)[:,:3]
     faces.append({'points':points,'uv':uv,'atlas_uv':uv,'tex':tex,'source_face':face,'bone':name})
  return faces
 # Recover UV offset using a matched original pixel region rather than calling the atlas packer.
 names=['grill_flat','grill_flat_lit','beef_raw','beef_stage_1','beef_stage_2','beef_stage_3','beef_cooked','beef_burnt']+['beef_cooked_bite_'+str(i) for i in range(1,5)]+['seasoning_v0_r8']
 offsets={};x=y=rh=0
 for n in names:
  im=Image.open(P/records[n]['atlas']);
  if x+im.width>256:x=0;y+=rh;rh=0
  offsets[n]=np.array([x,y]);x+=im.width;rh=max(rh,im.height)
 def original_flip(t,n):
  outfaces=[]
  def add(name,transform=None):
   fs=A.source_faces(records[name],specs[name])
   for f in fs:
    if transform:f['points']=transform(f['points'])
    f['atlas_uv']=f['atlas_uv']+offsets[name];outfaces.append(f)
  add('grill_flat_lit');stage=min(4,1+n);food=['beef_raw','beef_stage_1','beef_stage_2','beef_stage_3','beef_cooked','beef_burnt'][stage]
  for i,h in enumerate([.28,.33,.38]):
   p=max(0,min(1,t/.7));m=A.rotation([0,0,(n-1+p)*180]);shift=np.array([3+i*5,5+16*h*math.sin(math.pi*p),6.25])
   add(food,lambda points,m=m,shift=shift:(points-np.array([8,1,6.25]))@m.T+shift)
  return outfaces
 frame=[[0,0,0],[16,16,16]];pairs=0;max_pixel=0;max_vertex=0
 for turn in range(1,5):
  for t in np.linspace(0,.7,15):
   v=vars('flip',float(t),turn,min(4,1+turn));b=native(v);a=original_flip(t,turn)
   same=collections.Counter(map(A.signature,a))==collections.Counter(map(A.signature,b))
   if not same:raise AssertionError(f'Animated directed surface mismatch {turn} {t}')
   for camera in ['front_oblique','back_oblique']:
    ia=A.render(a,camera,frame);ib=A.render(b,camera,frame);err=int(np.abs(np.asarray(ia).astype(int)-np.asarray(ib).astype(int)).max());max_pixel=max(max_pixel,err);pairs+=1
    if err:raise AssertionError(f'Animated pixels differ {turn} {t} {camera}: {err}')
 # Source-flip image sequences are rendered from the actual exported animation and scene geometry.
 image_sets={};labels={};durations={'flip':.7,'brush':1,'season':.5,'eat':4.5}
 for action,duration in durations.items():
  frames=[];N=round(duration*20)+1
  for i in range(N):
   t=min(duration,i/20)
   if action=='flip':v=vars(action,t,1,2)
   elif action=='brush':v=vars(action,t,0,1)
   elif action=='season':v=vars(action,t,4,4)
   else:v=vars(action,t,4,4,loaded=0,held=1,bites=sum(t>=b for b in [.95833,2.33333,3.45833,4.08333]))
   im=A.render(native(v),'front_oblique',frame if action!='eat' else [[-8,0,0],[16,16,16]],width=480,height=360);draw=ImageDraw.Draw(im);draw.text((12,12),f'{action}  {t:.2f}s / {duration:.2f}s',fill='white');frames.append(im)
  frames[0].save(out/(action+'.gif'),save_all=True,append_images=frames[1:],duration=[50]*(len(frames)-1)+[650],loop=0,disposal=2)
  image_sets[action]=frames
 contact=Image.new('RGB',(480*4,360*2),(23,27,34))
 for row,action in enumerate(['flip','season']):
  frames=image_sets[action]
  for col,idx in enumerate(np.linspace(0,len(frames)-1,4).astype(int)):contact.paste(frames[idx].convert('RGB'),(col*480,row*360))
 contact.save(out/'motion-contact.png')
 encoded={action:[base64.b64encode(_png(f)).decode() for f in frames] for action,frames in image_sets.items()}
 # Self contained scrubber. Does not claim to render native player hands or particle engine.
 html='''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>煙火・動作時序檢查 A1.15</title><style>body{margin:0;background:#141922;color:#e6e9ef;font:16px system-ui;line-height:1.65}main{max-width:1040px;margin:auto;padding:28px}h1{font-size:30px}small,.sub{color:#aebacd}button,select,input{font:inherit}button,select{background:#273343;color:white;border:1px solid #557080;padding:9px 16px;border-radius:7px}button[aria-pressed=true]{border-color:#efae53}nav{display:flex;gap:8px;flex-wrap:wrap}.viewer{display:grid;grid-template-columns:minmax(0,1fr) 270px;gap:20px;margin-top:22px}img{width:100%;image-rendering:pixelated;border-radius:12px;background:#1c2430}aside{background:#202a37;padding:20px;border-radius:12px}input[type=range]{width:100%}.hint{border-left:3px solid #daa356;padding:8px 15px;background:#252931}@media(max-width:740px){.viewer{grid-template-columns:1fr}main{padding:16px}}</style><main><p class="sub">GRILLING / A1.15 / MOTION REVIEW</p><h1>從刷油，到最後一口。</h1><p>使用真正匯出的骨骼與動畫檔計算畫面。可暫停、逐幀、慢放；這不是 Minecraft 截圖或原生玩家手部驗收。</p><nav id="actions"></nav><section class="viewer"><div><img id="view" alt="煙火匯出模型的動作影格"><input aria-label="動作時間" id="seek" type="range" min="0" value="0"><div><button id="play">播放</button> <button id="prev">上一幀</button> <button id="next">下一幀</button> <select aria-label="播放速度" id="speed"><option value="1">1×</option><option value="0.5">0.5×</option><option value="0.25">0.25×</option></select></div></div><aside><h2 id="name"></h2><p id="time"></p><p id="detail"></p><button id="audio">試聽對應原音效</button><p><small>聲音必須手動播放。停止或切換動作時會取消，不會自動循環。</small></p></aside></section><p class="hint">刷油與撒料保留原作節奏與相對運動；工具在驗收台的位置和浮空分口樣本是展示配置，不是已完成的玩家手部綁定。原作完整第一／第三人稱與雙手資料另附來源與曲線。</p><p>翻面：四次，每次0.7秒、180°、0.28–0.38格拋高。牛肉分口點：0.95833、2.33333、3.45833、4.08333秒。光照、透明排序、原生粒子與實際世界仍待引擎驗收。</p></main><script>const FRAMES=__FRAMES__;const DUR=__DUR__;const AUDIO=__AUDIO__;const META={flip:['翻面','半正弦拋起；每串高度不同。落下後保留累積翻面角度，不歸零。'],brush:['刷油','1秒一個完整往返；不是連續抖動。展示台位置並非第一人稱相機位置。'],season:['撒料','0.5秒兩個抖動週期，保留額外180°倒瓶姿態。'],eat:['進食分口','90ticks、四個不同咬合時間。顯示的是分口樣本，沒有假裝連接原生玩家雙手。']};let action='flip',index=0,playing=false,last=0,acc=0,sound=null;const $=id=>document.getElementById(id);function stop(){playing=false;$('play').textContent='播放';if(sound){sound.pause();sound.currentTime=0;sound=null}}function draw(){$('view').src='data:image/png;base64,'+FRAMES[action][index];$('seek').max=FRAMES[action].length-1;$('seek').value=index;$('name').textContent=META[action][0];$('detail').textContent=META[action][1];$('time').textContent=(index*.05).toFixed(2)+' / '+DUR[action].toFixed(2)+' 秒';document.querySelectorAll('[data-action]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.action===action)))}Object.keys(META).forEach(a=>{let b=document.createElement('button');b.textContent=META[a][0];b.dataset.action=a;b.onclick=()=>{stop();action=a;index=0;acc=0;draw()};$('actions').append(b)});$('play').onclick=()=>{if(playing)stop();else{playing=true;$('play').textContent='暫停';last=performance.now()}};$('seek').oninput=()=>{stop();index=+$('seek').value;draw()};$('prev').onclick=()=>{stop();index=Math.max(0,index-1);draw()};$('next').onclick=()=>{stop();index=Math.min(FRAMES[action].length-1,index+1);draw()};$('audio').onclick=()=>{if(sound)sound.pause();sound=new Audio('data:audio/ogg;base64,'+AUDIO[action]);sound.play().catch(()=>{$('time').textContent='瀏覽器未允許音訊播放'})};document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});function loop(t){if(playing){acc+=(t-last)*+$('speed').value;if(acc>=50){index=Math.min(FRAMES[action].length-1,index+Math.floor(acc/50));acc%=50;draw();if(index===FRAMES[action].length-1)stop()}}last=t;requestAnimationFrame(loop)}draw();requestAnimationFrame(loop);window.reviewState=()=>({action,index,playing});</script></html>'''
 audionames={'flip':'grill_flip_1','brush':'grill_flip_1','season':'season','eat':'four_skewer_eat'}
 audio={a:base64.b64encode((D/f'resource_pack/sounds/kg_imm/{n}.ogg').read_bytes()).decode() for a,n in audionames.items()}
 html=html.replace('__FRAMES__',json.dumps(encoded)).replace('__DUR__',json.dumps(durations)).replace('__AUDIO__',json.dumps(audio))
 (out/'index.html').write_text(html,encoding='utf-8')
 return {'source_vs_exported_flip_pose_samples':60,'source_vs_exported_flip_two_view_pairs':pairs,'max_pixel_difference':max_pixel,'source_curve_angles_validated_separately':True,'gif_actions':list(image_sets),'native_player_hand_rendering':False,'generated_png_frames':sum(len(x) for x in image_sets.values())}
def _png(image):
 b=io.BytesIO();image.save(b,'PNG');return b.getvalue()
