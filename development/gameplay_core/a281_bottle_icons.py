"""Bake static inventory sprites from existing Java models, never material sheets.
Only stdlib + Pillow; model/UV/GUI data are inputs, no Minecraft UI simulation.
The pending icon is its zero-ingredient Java default. Special uses full variant 0.
Runtime 3D fill/variant selection and model textures are not modified.
"""
from pathlib import Path
from copy import deepcopy
import argparse, hashlib, io, json, math
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/'projects/grilling/source_snapshots/common/src/main/resources/assets'
RP=ROOT/'projects/grilling/gameplay_core/resource_pack'
SIZE=64
SOURCES={
 'empty_seasoning_bottle':ASSETS/'kaleidoscope_grilling/models/block/seasoning_bottle.json',
 'pending_seasoning':ROOT/'development/gameplay_core/fixtures/a2770/grilling/kaleidoscope_grilling/models/item/pending_seasoning.json',
 'special_seasoning':ASSETS/'kaleidoscope_grilling/models/item/seasoning_special_states/remaining_8_variant_0.json',
}
INPUTS={}
def load(path):
 raw=path.read_bytes();INPUTS[path.relative_to(ROOT).as_posix()]=hashlib.sha256(raw).hexdigest()
 return json.loads(raw.decode('utf-8-sig'))
def model(path,seen=()):
 if path in seen:raise ValueError('model parent cycle')
 doc=load(path);result={}
 if 'parent' in doc:
  ns,name=doc['parent'].split(':',1)
  result=model(ASSETS/ns/'models'/(name+'.json'),(*seen,path))
 for key,val in doc.items():
  if key=='parent':continue
  result[key]={**result.get(key,{}),**val} if key in ('textures','display') else deepcopy(val)
 return result

def rotate(p,angles):
 x,y,z=p
 for axis,angle in enumerate(angles):
  c,s=math.cos(math.radians(angle)),math.sin(math.radians(angle))
  if axis==0:y,z=y*c-z*s,y*s+z*c
  elif axis==1:x,z=x*c+z*s,-x*s+z*c
  else:x,y=x*c-y*s,x*s+y*c
 return [x,y,z]
def vertices(a,b,face):
 x,y,z=a;X,Y,Z=b
 return {'north':[(X,Y,z),(x,Y,z),(x,y,z),(X,y,z)],
  'south':[(x,Y,Z),(X,Y,Z),(X,y,Z),(x,y,Z)],
  'east':[(X,Y,Z),(X,Y,z),(X,y,z),(X,y,Z)],
  'west':[(x,Y,z),(x,Y,Z),(x,y,Z),(x,y,z)],
  'up':[(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)],
  'down':[(x,y,Z),(X,y,Z),(X,y,z),(x,y,z)]}[face]

def make_faces(doc):
 gui=doc['display']['gui'];faces=[];cache={}
 for e in doc['elements']:
  if min(e['to'][i]-e['from'][i] for i in range(3))<=0:continue
  if e.get('rotation',{}).get('angle',0)!=0:raise ValueError('unexpected nonzero element rotation')
  for side,info in e['faces'].items():
   ref=info['texture'];visited=set()
   while ref.startswith('#'):
    if ref in visited:raise ValueError('texture cycle')
    visited.add(ref);ref=doc['textures'][ref[1:]]
   if ref not in cache:
    ns,name=ref.split(':',1);path=ASSETS/ns/'textures'/(name+'.png')
    data=path.read_bytes();INPUTS[path.relative_to(ROOT).as_posix()]=hashlib.sha256(data).hexdigest()
    cache[ref]=Image.open(io.BytesIO(data)).convert('RGBA')
   tex=cache[ref];u,v,U,V=info['uv'];uv=[(u,v),(U,v),(U,V),(u,V)]
   turns=info.get('rotation',0)//90;uv=uv[turns:]+uv[:turns]
   uv=[(u*tex.width/16,v*tex.height/16) for u,v in uv]
   pts=[]
   for p in vertices(e['from'],e['to'],side):
    p=[(p[i]-8)*gui.get('scale',[1]*3)[i] for i in range(3)]
    p=rotate(p,gui.get('rotation',[0]*3))
    pts.append([p[i]+gui.get('translation',[0]*3)[i] for i in range(3)])
   faces.append((pts,uv,tex))
 return faces

def render(faces,size=SIZE):
 points=[p for pts,_,_ in faces for p in pts]
 low=[min(p[i] for p in points) for i in (0,1)];high=[max(p[i] for p in points) for i in (0,1)]
 center=[(a+b)/2 for a,b in zip(low,high)]
 scale=min((size-10)/(b-a) for a,b in zip(low,high))
 # Per-pixel sorted fragments, not a depth write that loses translucent glass.
 fragments=[[] for _ in range(size*size)]
 light=(-.25,.65,-.72);lightlen=math.sqrt(sum(x*x for x in light))
 for face_index,(pts,uv,tex) in enumerate(faces):
  a=[pts[1][i]-pts[0][i] for i in range(3)];b=[pts[2][i]-pts[0][i] for i in range(3)]
  n=[a[2]*b[1]-a[1]*b[2],a[0]*b[2]-a[2]*b[0],a[1]*b[0]-a[0]*b[1]]
  nl=math.sqrt(sum(x*x for x in n));shade=.72+.28*max(0,sum(n[i]*light[i] for i in range(3))/(nl*lightlen))
  screen=[((p[0]-center[0])*scale+size/2,-(p[1]-center[1])*scale+size/2,-p[2]) for p in pts]
  for ti,ids in enumerate(((0,1,2),(0,2,3))):
   q=[screen[i] for i in ids];t=[uv[i] for i in ids]
   den=(q[1][1]-q[2][1])*(q[0][0]-q[2][0])+(q[2][0]-q[1][0])*(q[0][1]-q[2][1])
   if abs(den)<1e-10:continue
   for y in range(max(0,math.floor(min(p[1] for p in q))),min(size,math.ceil(max(p[1] for p in q)))):
    for x in range(max(0,math.floor(min(p[0] for p in q))),min(size,math.ceil(max(p[0] for p in q)))):
     px,py=x+.5,y+.5
     a=((q[1][1]-q[2][1])*(px-q[2][0])+(q[2][0]-q[1][0])*(py-q[2][1]))/den
     b=((q[2][1]-q[0][1])*(px-q[2][0])+(q[0][0]-q[2][0])*(py-q[2][1]))/den;c=1-a-b
     if min(a,b,c)<-1e-8 or (ti==1 and c<=1e-8):continue
     weights=(a,b,c)
     u=math.floor(round(sum(weights[i]*t[i][0] for i in range(3)),8))
     v=math.floor(round(sum(weights[i]*t[i][1] for i in range(3)),8))
     rgba=tex.getpixel((max(0,min(tex.width-1,u)),max(0,min(tex.height-1,v))))
     if not rgba[3]:continue
     depth=round(sum(weights[i]*q[i][2] for i in range(3)),8)
     fragments[y*size+x].append((depth,face_index,rgba,shade))
 pixels=[]
 for fs in fragments:
  rgb=[0.,0.,0.];alpha=0.
  for _,_,color,shade in sorted(fs):
   a=color[3]/255
   rgb=[rgb[i]*(1-a)+color[i]*shade*a for i in range(3)];alpha=alpha*(1-a)+a
  pixels.append(tuple(max(0,min(255,round(c/alpha))) for c in rgb)+(round(alpha*255),) if alpha else (0,0,0,0))
 image=Image.new('RGBA',(size,size));image.putdata(pixels);return image

def images():
 INPUTS.clear()
 return {name:render(make_faces(model(path))) for name,path in SOURCES.items()}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 result=images()
 for name,image in result.items():
  path=RP/'textures/items'/(name+'.png')
  if args.check:
   actual=Image.open(path).convert('RGBA')
   assert actual.size==image.size and actual.tobytes()==image.tobytes(),('sprite drift',name)
  else:image.save(path,compress_level=9)
 print(json.dumps({'icons':len(result),'size':SIZE,'source_sha256':INPUTS,'minecraft_tested':False},indent=2))
if __name__=='__main__':main()
