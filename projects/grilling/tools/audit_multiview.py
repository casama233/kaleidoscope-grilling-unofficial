#!/usr/bin/env python3
"""Independent .geo decoder, directed-face audit and eight-view offline comparison.

Reads pinned Java source files and parent chains + original PNGs on one path, and exported
Bedrock geometry + atlas PNG on the other. It does not call the converter or use
.bbmodel as a proxy for Bedrock output. This is not a Minecraft renderer.
"""
from __future__ import annotations
import argparse,hashlib,json,math,time,copy,re
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'source_snapshots/common/src/main/resources/assets'
VIEWS={'front':(0,0,-1),'back':(0,0,1),'left':(-1,0,0),'right':(1,0,0),
       'top':(0,1,0),'bottom':(0,-1,0),'front_oblique':(-1,.8,-1),'back_oblique':(1,.8,1)}
W,H=320,260

def rotation(angles):
 a,b,c=np.radians(angles);ca,sa=np.cos(a),np.sin(a);cb,sb=np.cos(b),np.sin(b);cc,sc=np.cos(c),np.sin(c)
 return np.array([[cc,-sc,0],[sc,cc,0],[0,0,1]])@np.array([[cb,0,sb],[0,1,0],[-sb,0,cb]])@np.array([[1,0,0],[0,ca,-sa],[0,sa,ca]])

def vertices(a,b,face):
 x,y,z=a;X,Y,Z=b
 return np.array({'north':[[X,Y,z],[x,Y,z],[x,y,z],[X,y,z]],
  'south':[[x,Y,Z],[X,Y,Z],[X,y,Z],[x,y,Z]],
  'east':[[X,Y,Z],[X,Y,z],[X,y,z],[X,y,Z]],
  'west':[[x,Y,z],[x,Y,Z],[x,y,Z],[x,y,z]],
  'up':[[x,Y,z],[X,Y,z],[X,Y,Z],[x,Y,Z]],
  'down':[[x,y,Z],[X,y,Z],[X,y,z],[x,y,z]]}[face],dtype=float)

def rectangle(uv):
 a,b,c,d=uv;return np.array([[a,b],[c,b],[c,d],[a,d]],dtype=float)

def resolve_alias(ref,aliases):
 seen=set()
 while ref.startswith('#'):
  if ref in seen:raise ValueError('texture alias cycle')
  seen.add(ref);ref=aliases[ref[1:]]
 return ref

def read_source_model(identifier, ancestry=(), source_root=None):
 """Independent source resolver: never reads the converter's resolved-model cache."""
 root=Path(source_root) if source_root is not None else ASSETS
 if isinstance(identifier,str) and ":" not in identifier:identifier="minecraft:"+identifier
 if not isinstance(identifier,str) or not re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_./-]+",identifier):raise ValueError('Invalid source identifier')
 ns,name=identifier.split(':',1)
 if any(part in ('','.','..') for part in name.split('/')):raise ValueError('Unsafe source identifier')
 if identifier in ancestry or len(ancestry)>=48:raise ValueError('Source parent cycle/depth')
 path=root/ns/'models'/(name+'.json')
 own=json.loads(path.read_bytes().decode('utf-8-sig'))
 if not isinstance(own,dict):raise ValueError('Source model must be an object')
 inherited={};paths=[]
 if 'parent' in own:
  inherited,paths=read_source_model(own['parent'],(*ancestry,identifier),root)
 merged=copy.deepcopy(inherited)
 for key,value in own.items():
  if key=='parent':continue
  if key in ('textures','display'):
   if not isinstance(value,dict):raise ValueError('Invalid source mapping')
   target=dict(merged.get(key,{}));target.update(copy.deepcopy(value));merged[key]=target
  else:merged[key]=copy.deepcopy(value)
 return merged,[*paths,path]

def source_faces(record,spec):
 data,_=read_source_model(spec['source_model'])
 textures={};faces=[]
 for dx,dz in spec['offsets']:
  offset=np.array([dx,0,dz])
  for e in data['elements']:
   r=e.get('rotation',{});angles=[0,0,0];pivot=np.array(r.get('origin',[0,0,0]),dtype=float)
   if r:angles['xyz'.index(r['axis'])]=r['angle']
   mat=rotation(angles)
   for face,f in e['faces'].items():
    ref=resolve_alias(f['texture'],data['textures']);ns,path=ref.split(':',1)
    if ref not in textures:textures[ref]=np.asarray(Image.open(ASSETS/ns/'textures'/(path+'.png')).convert('RGBA'))
    tex=textures[ref]
    if 'uv' not in f:
     if e['from'] != [0,0,0] or e['to'] != [16,16,16]:raise ValueError('Implicit source UV outside full cube')
     uv=rectangle([0,0,16,16])
    else:uv=rectangle(f['uv'])
    # Java source corners are rotated independently of exporter endpoint baking.
    face_rotation=f.get('rotation',0)
    if isinstance(face_rotation,bool) or face_rotation not in (0,90,180,270):raise ValueError('Unsupported Java face rotation')
    uv=np.roll(uv,-int(face_rotation//90),axis=0)*np.array([tex.shape[1]/16,tex.shape[0]/16])
    rect=record['atlas_regions'][ref]
    puv=uv+np.array([rect['x'],rect['y']])
    relative=vertices(e['from'],e['to'],face)-pivot
    if r.get('rescale'):
     factors=np.full(3,1/np.cos(np.radians(r['angle'])));factors['xyz'.index(r['axis'])]=1
     relative=relative*factors
    points=relative@mat.T+pivot+offset
    faces.append({'points':points,'uv':uv,'atlas_uv':puv,'tex':tex,'source_face':face})
 return faces

def bedrock_faces(record):
 document=json.loads((ROOT/record['geometry']).read_text());g=document['minecraft:geometry'][0]
 tex=np.asarray(Image.open(ROOT/record['atlas']).convert('RGBA'))
 if g['description']['texture_width']!=tex.shape[1] or g['description']['texture_height']!=tex.shape[0]:raise ValueError('atlas size mismatch')
 out=[]
 for bone in g['bones']:
  if any(bone.get('rotation',[0,0,0])) or bone.get('scale') or bone.get('binding'):raise ValueError('Bone transform outside this audit decoder scope')
  for cube in bone.get('cubes',[]):
   o=np.array(cube['origin'],dtype=float);s=np.array(cube['size'],dtype=float)
   if np.any(s<0):raise ValueError('Negative exported cube size')
   # This decoder follows the pinned Blockbench bedrock parseCube contract.
   a=np.array([8-o[0]-s[0],o[1],o[2]+8]);b=a+s
   p=cube.get('pivot',[0,0,0]);pivot=np.array([8-p[0],p[1],p[2]+8],dtype=float)
   r=cube.get('rotation',[0,0,0]);mat=rotation([-r[0],-r[1],r[2]])
   for face,f in cube['uv'].items():
    uv_rotation=f.get('uv_rotation',0)
    if isinstance(uv_rotation,bool) or uv_rotation not in (0,90,180,270):raise ValueError('Invalid native UV rotation')
    if uv_rotation and document['format_version']!='1.21.0':raise ValueError('Native UV rotation requires geometry 1.21.0 in this audit')
    lo=np.array(f['uv']);hi=lo+np.array(f['uv_size'])
    if face in ('up','down'):lo,hi=hi,lo
    # Read native face rotation after restoring up/down endpoint conventions.
    uv=np.roll(rectangle([*lo,*hi]),-int(uv_rotation//90),axis=0)
    points=(vertices(a,b,face)-pivot)@mat.T+pivot
    out.append({'points':points,'uv':uv,'atlas_uv':uv,'tex':tex,'source_face':face})
 return out

def normal(f):
 p=f['points'];v=-np.cross(p[1]-p[0],p[2]-p[0]);size=np.linalg.norm(v)
 return v/size if size>1e-10 else v

def signature(f):
 """Cyclic ordering is ignored; winding and vertex-to-UV association are not."""
 rows=np.concatenate([f['points'],f['atlas_uv']],axis=1).round(7)
 v=[tuple(float(x) for x in row) for row in rows]
 return min(tuple(v[i:]+v[:i]) for i in range(4))

def view_basis(name):
 d=np.array(VIEWS[name],dtype=float);d/=np.linalg.norm(d)
 up=np.array([0,1,0],dtype=float)
 if name=='top':up=np.array([0,0,-1],dtype=float)
 if name=='bottom':up=np.array([0,0,1],dtype=float)
 right=np.cross(up,d);right/=np.linalg.norm(right);up=np.cross(d,right)
 return np.stack([right,up,d])

def render(faces,view,frame,width=W,height=H):
 basis=view_basis(view);cam=faces and np.concatenate([f['points'] for f in faces])@basis.T
 bounds=np.array(frame)@basis.T;lo=bounds[:,:2].min(0);hi=bounds[:,:2].max(0)
 center=(lo+hi)/2
 # A single scale for ALL eight angles of this object: end-on skewers must not
 # become larger than their side views through per-camera auto-zoom.
 spans=[np.ptp(np.array(frame)@view_basis(v).T,axis=0)[:2] for v in VIEWS]
 span=np.max(spans,axis=0)
 scale=min((width-40)/max(span[0],.5),(height-40)/max(span[1],.5))
 yy,xx=np.mgrid[:height,:width];checker=((xx//16+yy//16)%2)[...,None]
 image=np.broadcast_to(np.array([23.,27.,34.]),(height,width,3)).copy()+checker*4
 opaque_depth=np.full((height,width),-np.inf);fragments=[]
 light=np.array([-.3,.85,-.43]);light/=np.linalg.norm(light)
 # Stable directed-face order makes coincident surfaces deterministic on both paths.
 for original in sorted(faces,key=signature):
  f = dict(original)
  # Normalize cyclic start only (never reverse winding). It removes triangulation
  # arithmetic differences after lossless four-corner/180-degree UV remapping.
  keys = np.concatenate([f['points'],f['atlas_uv']],axis=1).round(7).tolist()
  shift = min(range(4), key=lambda i: keys[i])
  for key in ['points','uv','atlas_uv']:
   f[key] = np.roll(f[key], -shift, axis=0)
  n=normal(f)
  if np.linalg.norm(n)<1e-9 or np.dot(n,basis[2])<=1e-9:continue
  p=f['points']@basis.T;xy=(p[:,:2]-center)*scale;xy[:,1]*=-1;xy+=np.array([width/2,height/2])
  brightness=.62+.38*max(0,float(np.dot(n,light)))
  for idx,ids in enumerate(([0,1,2],[0,2,3])):
   v=xy[ids];t=f['uv'][ids];z=p[ids,2]
   xl=max(int(np.floor(v[:,0].min())),0);xh=min(int(np.ceil(v[:,0].max())),width-1)
   yl=max(int(np.floor(v[:,1].min())),0);yh=min(int(np.ceil(v[:,1].max())),height-1)
   if xl>xh or yl>yh:continue
   den=(v[1,1]-v[2,1])*(v[0,0]-v[2,0])+(v[2,0]-v[1,0])*(v[0,1]-v[2,1])
   if abs(den)<1e-10:continue
   ys,xs=np.mgrid[yl:yh+1,xl:xh+1];xs=xs+.5;ys=ys+.5
   a=((v[1,1]-v[2,1])*(xs-v[2,0])+(v[2,0]-v[1,0])*(ys-v[2,1]))/den
   b=((v[2,1]-v[0,1])*(xs-v[2,0])+(v[0,0]-v[2,0])*(ys-v[2,1]))/den;c=1-a-b
   mask=(a>=-1e-8)&(b>=-1e-8)&(c>=-1e-8)
   if idx==1:mask&=c>1e-8 # avoid double blending along the shared triangle diagonal
   u=np.floor(np.round(a*t[0,0]+b*t[1,0]+c*t[2,0],9)).astype(int);vv=np.floor(np.round(a*t[0,1]+b*t[1,1]+c*t[2,1],9)).astype(int)
   tex=f['tex'];u=np.clip(u,0,tex.shape[1]-1);vv=np.clip(vv,0,tex.shape[0]-1)
   rgba=tex[vv,u].astype(float);depth=a*z[0]+b*z[1]+c*z[2]
   rgb=rgba[...,:3]*brightness;alpha=rgba[...,3]/255
   region=(slice(yl,yh+1),slice(xl,xh+1));visible=mask&(alpha==1)&(depth>opaque_depth[region]+1e-8)
   image[region][visible]=rgb[visible];opaque_depth[region][visible]=depth[visible]
   transparent=mask&(alpha>0)&(alpha<1)
   if transparent.any():fragments.append((round(float(p[:,2].mean()),9),region,depth,alpha,rgb,transparent))
 for _,region,depth,alpha,rgb,mask in sorted(fragments,key=lambda f:f[0]):
  mask&=depth>=opaque_depth[region]-1e-8
  aa=(alpha*mask)[...,None];image[region]=image[region]*(1-aa)+rgb*aa
 return Image.fromarray(np.clip(image,0,255).round().astype('uint8'))

def input_hashes(record,spec):
 _,chain=read_source_model(spec['source_model'])
 paths=[record['geometry'],record['atlas']]+[p.relative_to(ROOT).as_posix() for p in chain]
 for ref in record['atlas_regions']:
  ns,p=ref.split(':',1);paths.append('source_snapshots/common/src/main/resources/assets/'+ns+'/textures/'+p+'.png')
 out={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
 out['$spec']=hashlib.sha256(json.dumps(spec,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
 out['$audit_code']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 return out

def run(start=0,end=None):
 build=json.loads((ROOT/'reports/build-report.json').read_text());specs={s['name']:s for s in json.loads((ROOT/'config/asset_specs.json').read_text())['candidates']}
 folder=ROOT/'reports/multiview';folder.mkdir(parents=True,exist_ok=True)
 result=[];began=time.monotonic()
 for rec in build['candidates'][start:end]:
  a=source_faces(rec,specs[rec['name']]);b=bedrock_faces(rec)
  ca,cb=Counter(map(signature,a)),Counter(map(signature,b));exact=ca==cb
  frame=np.concatenate([f['points'] for f in a]).tolist()
  row={'name':rec['name'],'label_zh':rec['label_zh'],'group':rec['group'],
       'source_faces':len(a),'exported_faces':len(b),'directed_faces_and_uv_equal':exact,
       'degenerate_faces':int(sum(np.linalg.norm(normal(f))<1e-9 for f in a)),
       'source_aabb':[np.min(frame,axis=0).tolist(),np.max(frame,axis=0).tolist()],
       'export_aabb':[np.min(np.concatenate([f['points'] for f in b]),axis=0).tolist(),np.max(np.concatenate([f['points'] for f in b]),axis=0).tolist()],
       'views':[],'minecraft_tested':False,'human_visual_review':False,
       'input_sha256':input_hashes(rec,specs[rec['name']])}
  if not exact:
   row['face_mismatch']={'missing':len(list((ca-cb).elements())),'extra':len(list((cb-ca).elements()))}
  for view in VIEWS:
   src=render(a,view,frame);dst=render(b,view,frame)
   x=np.asarray(src).astype(int);y=np.asarray(dst).astype(int);diff=np.abs(x-y)
   srcpath=folder/f"{rec['name']}__{view}__source.png";dstpath=folder/f"{rec['name']}__{view}__bedrock.png"
   src.save(srcpath);dst.save(dstpath)
   row['views'].append({'view':view,'source':str(srcpath.relative_to(ROOT)), 'bedrock':str(dstpath.relative_to(ROOT)),
                        'mean_channel_error_255':float(diff.mean()),'max_channel_error_255':int(diff.max()),
                        'changed_pixels':int((diff.max(2)>0).sum()),'changed_pixels_gt2':int((diff.max(2)>2).sum()),'total_pixels':W*H})
  (folder/f"{rec['name']}.audit.json").write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');result.append(row)
  print(rec['name'],'faces',len(a),'equal',exact,'max_pixel_diff',max(v['max_channel_error_255'] for v in row['views']),flush=True)
 print('elapsed_s',round(time.monotonic()-began,2),flush=True)
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--start',type=int,default=0);p.add_argument('--end',type=int);args=p.parse_args();run(args.start,args.end)
