from __future__ import annotations
import hashlib,json,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
VERSION=[2,7,4]
UP='https://raw.githubusercontent.com/breezeth-CN/KaleidoscopeGrilling/9a1acdab27698457bec16c9362678e574895a28c/common/src/main/resources/assets/kaleidoscope_grilling/textures/item/fixed_skewer_gui_16/'
ICONS={
'dark_grilling':('dark_grilling.png','abbfe3d7a5bb9575a24e028978ff42b3535bd17d'),
'grilled_beef_skewer':('grilled_beef_skewer_cooked.png','8abbdbc8e9c6e7cf1ad1b42d1173e62c7507081e'),
'grilled_bun_slice_skewer':('grilled_bun_slice_skewer_cooked.png','1f6c1b495a79fbcdc788e10f4c315cda01d69bc9'),
'grilled_caterpillar_skewer':('grilled_caterpillar_skewer_cooked.png','3ec9ba93b84efa08b0c5ae70108416aa3a789578'),
'grilled_chicken_skin_skewer':('grilled_chicken_skin_skewer_cooked.png','fb7313df0d0e47e45d8455cabc285bff756f1769'),
'grilled_ender_pearl_skewer':('grilled_ender_pearl_skewer_cooked.png','1f732e6a9576b53d5728532b9b5df4827b5f7269'),
'grilled_fish_skewer':('grilled_fish_skewer_cooked.png','688377302cd5f6fa68182f4d6e4359cbf1a7b31c'),
'grilled_fried_egg_skewer':('grilled_fried_egg_skewer_cooked.png','4bf9b6529107d7ddeb36a8b645cdd19a4cd42362'),
'grilled_gluten_skewer':('grilled_gluten_skewer_cooked.png','1d244babc36022fc877fa64859fdc97c465057c2'),
'grilled_golden_skewer':('grilled_golden_skewer_cooked.png','1d59443ed6e10f684b85fccba35f49a08f7a4335'),
'grilled_lamb_skewer':('grilled_lamb_skewer_cooked.png','b983c58fa38ddc4381edb6c3f0dca31cd3575139'),
'grilled_meat_and_bone_skewer':('grilled_meat_and_bone_skewer_cooked.png','953203719639179edf40eafe27f4b0fa81504bc2'),
'grilled_meatball_skewer':('grilled_meatball_skewer_cooked.png','af6a48d5df60f53641e167944cc18f0104849420'),
'grilled_mid_wing_skewer':('grilled_mid_wing_skewer_cooked.png','9b292bf832fe25edbd0cb45c77cd40513ef5956a'),
'grilled_mushroom_skewer':('grilled_mushroom_skewer_cooked.png','ae010d232bee1a8fdec52436964ec3daff7d9b8b'),
'grilled_pork_belly_skewer':('grilled_pork_belly_skewer_cooked.png','f4952c85477e4f80d1ad6e0b3a5610615771fbe1'),
'grilled_potato_slice_skewer':('grilled_potato_slice_skewer_cooked.png','574abe897515341875371f6228b2f32cefcc60c9'),
'grilled_slime_skewer':('grilled_slime_skewer_cooked_frame_0.png','9ca49b428d49c498d50f23e2937ca357016ff66b'),
'grilled_squid_tentacle_skewer':('grilled_squid_tentacle_skewer_cooked.png','e4eeb7092f2b0c2be66bb67e003dac8f1ec1a12a'),
'grilled_sweet_potato_sheet_skewer':('grilled_sweet_potato_sheet_skewer_cooked.png','03cf33b637ffdb8ffc645e1624414631c4749d06'),
'mysterious_skewer':('mysterious_skewer_frame_0.png','bec4837ffa879d4e98ff30632beda7d96ebdada8'),
'ordinary_skewer':('ordinary_skewer_cooked.png','da504d39a68b44572cda466599302351a929f039'),
'raw_beef_skewer':('raw_beef_skewer_raw.png','2ba5b17264927b7ca9d3b767c29742f6921aaf50'),
'raw_bun_slice_skewer':('raw_bun_slice_skewer_raw.png','cc6200ec355cc242c71ee1c70073325ffa3fed0f'),
'raw_caterpillar_skewer':('raw_caterpillar_skewer_raw.png','abc8c1c9ea499e3362f4cb5335ce7a50c2db595c'),
'raw_chicken_skin_skewer':('raw_chicken_skin_skewer_raw.png','610862271dbfa68692d23256e7fac69004de5f3d'),
'raw_ender_pearl_skewer':('raw_ender_pearl_skewer_raw.png','c70ec384120d460ee9bccfbb9d80ab3db9c022be'),
'raw_fish_skewer':('raw_fish_skewer_raw.png','09f197a93995859ca4faff78d2d3a633b806fd18'),
'raw_fried_egg_skewer':('raw_fried_egg_skewer_raw.png','dcd2f1a58c5fa06032786ceb8e22a75472d2e2eb'),
'raw_gluten_skewer':('raw_gluten_skewer_raw.png','3a7688125ca3f345784812e32b813fccae8368a6'),
'raw_golden_skewer':('raw_golden_skewer_raw.png','62a80f23cbb7dc55e6412cc35557e8068fa4d3c9'),
'raw_lamb_skewer':('raw_lamb_skewer_raw.png','b4ce6d2dd6798faa34be7965d2178125052299c0'),
'raw_meat_and_bone_skewer':('raw_meat_and_bone_skewer_raw.png','7384836e1f837e49315fd60913ffedfb0e7ccbcd'),
'raw_meatball_skewer':('raw_meatball_skewer_raw.png','fa47078cb6f8a4f806039cfb6e6c3b69a8ad29aa'),
'raw_mid_wing_skewer':('raw_mid_wing_skewer_raw.png','b9d58cef80f9679d7cceabc14dfc6558fa587fe0'),
'raw_mushroom_skewer':('raw_mushroom_skewer_raw.png','8d6208dfe712acc92d72de279e70d9498f5dfe62'),
'raw_pork_belly_skewer':('raw_pork_belly_skewer_raw.png','100dcd919c27fb2eec0dfad9d6c5fcb630bf1ea6'),
'raw_potato_slice_skewer':('raw_potato_slice_skewer_raw.png','d7ec71b205b8963b13e0f850d1ba07bbc21949fb'),
'raw_slime_skewer':('raw_slime_skewer_raw.png','c9f1c608adf4ba2d8064955540459d04bd741c0e'),
'raw_squid_tentacle_skewer':('raw_squid_tentacle_skewer_raw.png','18d5e127c542ee81cc47c6f6c73f9095309a87e7'),
'raw_sweet_potato_sheet_skewer':('raw_sweet_potato_sheet_skewer_raw.png','4aef022016a54b0e30de9610697325bc3848cb73')
}

def blob(v):
 return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def fetch(name,sha):
 req=urllib.request.Request(UP+name,headers={'User-Agent':'Grilling-A2.7.4/1'})
 with urllib.request.urlopen(req,timeout=90) as r:v=r.read()
 got=blob(v)
 if got!=sha:raise RuntimeError(f'pinned Java GUI icon mismatch {name}: {got} != {sha}')
 return v

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text((json.dumps(d,ensure_ascii=False,indent=2)+'\n') if isinstance(d,(dict,list)) else d,encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.4 Java GUI Parity BP'),(rm,'Kaleidoscope Grilling A2.7.4 Java GUI Parity RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write(BP/'manifest.json',bm);write(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.4 Java GUI Icon Parity';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_4_Java_GUI';write(P/'config.json',cfg)

def import_java_icons():
 outdir=RP/'textures/items';outdir.mkdir(parents=True,exist_ok=True)
 rows=[]
 for item,(name,sha) in ICONS.items():
  raw=fetch(name,sha);path=outdir/f'{item}.png';path.write_bytes(raw)
  with Image.open(path) as im:
   if im.size!=(16,16):raise RuntimeError(f'Java GUI icon {name} is not 16x16: {im.size}')
  rows.append({'item':item,'java_file':name,'git_blob_sha1':sha})
 return rows

def contact(rows):
 scale=4;cell=92;cols=8
 sheet=Image.new('RGBA',(cols*cell,((len(rows)+cols-1)//cols)*cell),(24,27,34,255));draw=ImageDraw.Draw(sheet)
 for i,row in enumerate(rows):
  x=(i%cols)*cell;y=(i//cols)*cell
  icon=Image.open(RP/f"textures/items/{row['item']}.png").convert('RGBA').resize((64,64),Image.Resampling.NEAREST)
  sheet.alpha_composite(icon,(x+14,y+1));draw.text((x+3,y+68),row['item'].replace('raw_','r_').replace('grilled_','g_')[:14],fill=(235,235,235,255))
 out=P/'reports/a274-java-gui-icons-contact.png';out.parent.mkdir(parents=True,exist_ok=True);sheet.save(out)

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,3]:raise RuntimeError('A2.7.4 must augment A2.7.3 stabilization')
 patch_versions();rows=import_java_icons();contact(rows)
 write(P/'reports/a274-java-gui-icons.json',{
  'version':'A2.7.4',
  'source':'Java 1.1.1 fixed_skewer_gui_16 hand-authored/default GUI icons',
  'java_commit':'9a1acdab27698457bec16c9362678e574895a28c',
  'java_default_config':{'useFixedSkewer64xCache':False,'meaning':'hand-drawn 16x16 icons are the Java default for fixed skewers'},
  'exact_static_java_icons':39,
  'frame0_java_icons':{
   'grilled_slime_skewer':'Java cycles 5 cooked frames every 4 game ticks; Bedrock A2.7.4 uses exact Java frame 0.',
   'mysterious_skewer':'Java cycles 5 failure frames every 4 game ticks; Bedrock A2.7.4 uses exact Java frame 0.'
  },
  'items':rows,
  'note':'No Python 3D rasterizer is used for final inventory icons. Held/eating attachables remain separate.',
  'minecraft_tested':False,'bds_tested':False
 })
 print('A2.7.4 exact Java GUI icon import complete:',len(rows))

if __name__=='__main__':main()
