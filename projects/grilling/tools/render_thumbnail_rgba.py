"""Derived RGBA icon rasterizer. Preserves fractional coverage; offline, not game material validation.
Uses the project camera and directed-face conventions; separate from validation results.
"""
import numpy as np
from PIL import Image
import audit_multiview as audit

def render_rgba(faces,view,frame,width=audit.W,height=audit.H):
 basis=audit.view_basis(view);cam=faces and np.concatenate([f['points'] for f in faces])@basis.T
 bounds=np.array(frame)@basis.T;lo=bounds[:,:2].min(0);hi=bounds[:,:2].max(0)
 center=(lo+hi)/2
 # A single scale for ALL eight angles of this object: end-on skewers must not
 # become larger than their side views through per-camera auto-zoom.
 spans=[np.ptp(np.array(frame)@audit.view_basis(v).T,axis=0)[:2] for v in audit.VIEWS]
 span=np.max(spans,axis=0)
 scale=min((width-40)/max(span[0],.5),(height-40)/max(span[1],.5))
 yy,xx=np.mgrid[:height,:width];checker=((xx//16+yy//16)%2)[...,None]
 image=np.zeros((height,width,3),dtype=float)
 coverage=np.zeros((height,width),dtype=float)
 opaque_depth=np.full((height,width),-np.inf);fragments=[]
 light=np.array([-.3,.85,-.43]);light/=np.linalg.norm(light)
 # Stable directed-face order makes coincident surfaces deterministic on both paths.
 for original in sorted(faces,key=audit.signature):
  f = dict(original)
  # Normalize cyclic start only (never reverse winding). It removes triangulation
  # arithmetic differences after lossless four-corner/180-degree UV remapping.
  keys = np.concatenate([f['points'],f['atlas_uv']],axis=1).round(7).tolist()
  shift = min(range(4), key=lambda i: keys[i])
  for key in ['points','uv','atlas_uv']:
   f[key] = np.roll(f[key], -shift, axis=0)
  n=audit.normal(f)
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
   image[region][visible]=rgb[visible];coverage[region][visible]=1;opaque_depth[region][visible]=depth[visible]
   transparent=mask&(alpha>0)&(alpha<1)
   if transparent.any():fragments.append((float(p[:,2].mean()),region,depth,alpha,rgb,transparent))
 for _,region,depth,alpha,rgb,mask in sorted(fragments,key=lambda f:f[0]):
  mask&=depth>=opaque_depth[region]-1e-8
  aa=(alpha*mask)[...,None];image[region]=image[region]*(1-aa)+rgb*aa
  coverage[region]=coverage[region]*(1-aa[...,0])+aa[...,0]
 straight=np.divide(image,coverage[...,None],out=np.zeros_like(image),where=coverage[...,None]>0)
 return Image.fromarray(np.dstack([np.clip(straight,0,255),coverage*255]).round().astype('uint8'),'RGBA')
