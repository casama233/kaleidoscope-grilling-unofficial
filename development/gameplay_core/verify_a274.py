from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]
EXPECTED={
'dark_grilling':'abbfe3d7a5bb9575a24e028978ff42b3535bd17d',
'grilled_beef_skewer':'8abbdbc8e9c6e7cf1ad1b42d1173e62c7507081e',
'grilled_bun_slice_skewer':'1f6c1b495a79fbcdc788e10f4c315cda01d69bc9',
'grilled_caterpillar_skewer':'3ec9ba93b84efa08b0c5ae70108416aa3a789578',
'grilled_chicken_skin_skewer':'fb7313df0d0e47e45d8455cabc285bff756f1769',
'grilled_ender_pearl_skewer':'1f732e6a9576b53d5728532b9b5df4827b5f7269',
'grilled_fish_skewer':'688377302cd5f6fa68182f4d6e4359cbf1a7b31c',
'grilled_fried_egg_skewer':'4bf9b6529107d7ddeb36a8b645cdd19a4cd42362',
'grilled_gluten_skewer':'1d244babc36022fc877fa64859fdc97c465057c2',
'grilled_golden_skewer':'1d59443ed6e10f684b85fccba35f49a08f7a4335',
'grilled_lamb_skewer':'b983c58fa38ddc4381edb6c3f0dca31cd3575139',
'grilled_meat_and_bone_skewer':'953203719639179edf40eafe27f4b0fa81504bc2',
'grilled_meatball_skewer':'af6a48d5df60f53641e167944cc18f0104849420',
'grilled_mid_wing_skewer':'9b292bf832fe25edbd0cb45c77cd40513ef5956a',
'grilled_mushroom_skewer':'ae010d232bee1a8fdec52436964ec3daff7d9b8b',
'grilled_pork_belly_skewer':'f4952c85477e4f80d1ad6e0b3a5610615771fbe1',
'grilled_potato_slice_skewer':'574abe897515341875371f6228b2f32cefcc60c9',
'grilled_slime_skewer':'9ca49b428d49c498d50f23e2937ca357016ff66b',
'grilled_squid_tentacle_skewer':'e4eeb7092f2b0c2be66bb67e003dac8f1ec1a12a',
'grilled_sweet_potato_sheet_skewer':'03cf33b637ffdb8ffc645e1624414631c4749d06',
'mysterious_skewer':'bec4837ffa879d4e98ff30632beda7d96ebdada8',
'ordinary_skewer':'da504d39a68b44572cda466599302351a929f039',
'raw_beef_skewer':'2ba5b17264927b7ca9d3b767c29742f6921aaf50',
'raw_bun_slice_skewer':'cc6200ec355cc242c71ee1c70073325ffa3fed0f',
'raw_caterpillar_skewer':'abc8c1c9ea499e3362f4cb5335ce7a50c2db595c',
'raw_chicken_skin_skewer':'610862271dbfa68692d23256e7fac69004de5f3d',
'raw_ender_pearl_skewer':'c70ec384120d460ee9bccfbb9d80ab3db9c022be',
'raw_fish_skewer':'09f197a93995859ca4faff78d2d3a633b806fd18',
'raw_fried_egg_skewer':'dcd2f1a58c5fa06032786ceb8e22a75472d2e2eb',
'raw_gluten_skewer':'3a7688125ca3f345784812e32b813fccae8368a6',
'raw_golden_skewer':'62a80f23cbb7dc55e6412cc35557e8068fa4d3c9',
'raw_lamb_skewer':'b4ce6d2dd6798faa34be7965d2178125052299c0',
'raw_meat_and_bone_skewer':'7384836e1f837e49315fd60913ffedfb0e7ccbcd',
'raw_meatball_skewer':'fa47078cb6f8a4f806039cfb6e6c3b69a8ad29aa',
'raw_mid_wing_skewer':'b9d58cef80f9679d7cceabc14dfc6558fa587fe0',
'raw_mushroom_skewer':'8d6208dfe712acc92d72de279e70d9498f5dfe62',
'raw_pork_belly_skewer':'100dcd919c27fb2eec0dfad9d6c5fcb630bf1ea6',
'raw_potato_slice_skewer':'d7ec71b205b8963b13e0f850d1ba07bbc21949fb',
'raw_slime_skewer':'c9f1c608adf4ba2d8064955540459d04bd741c0e',
'raw_squid_tentacle_skewer':'18d5e127c542ee81cc47c6f6c73f9095309a87e7',
'raw_sweet_potato_sheet_skewer':'4aef022016a54b0e30de9610697325bc3848cb73'
}

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def blob(path):
 v=path.read_bytes();return hashlib.sha1(b'blob '+str(len(v)).encode()+bytes([0])+v).hexdigest()

def formal_stems():
 out=[]
 for p in (BP/'items').glob('*.json'):
  s=p.stem
  if ((s.startswith('raw_') or s.startswith('grilled_')) and s.endswith('_skewer')) or s in ('ordinary_skewer','mysterious_skewer','dark_grilling'):out.append(s)
 return sorted(out)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,7,4] and rm['header']['version']==[2,7,4]
 assert bm['header']['name']=='Kaleidoscope Grilling A2.7.4 Java GUI Parity BP'
 assert rm['header']['name']=='Kaleidoscope Grilling A2.7.4 Java GUI Parity RP'
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies'] and {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

 stems=formal_stems();assert stems==sorted(EXPECTED),(len(stems),set(stems)^set(EXPECTED))
 tex=load(RP/'textures/item_texture.json')['texture_data']
 hashes={}
 for stem,sha in EXPECTED.items():
  p=RP/f'textures/items/{stem}.png';assert p.is_file(),p
  with Image.open(p) as im:assert im.size==(16,16),(stem,im.size)
  got=blob(p);assert got==sha,(stem,got,sha)
  assert tex[stem]['textures']==f'textures/items/{stem}'
  hashes[stem]=hashlib.sha256(p.read_bytes()).hexdigest()
 assert len(set(hashes.values()))>=39
 assert (P/'reports/a274-java-gui-icons-contact.png').is_file()

 report=load(P/'reports/a274-java-gui-icons.json')
 assert report['version']=='A2.7.4'
 assert report['java_commit']=='9a1acdab27698457bec16c9362678e574895a28c'
 assert report['java_default_config']['useFixedSkewer64xCache'] is False
 assert report['exact_static_java_icons']==39
 assert set(report['frame0_java_icons'])=={'grilled_slime_skewer','mysterious_skewer'}
 assert len(report['items'])==41
 assert report['minecraft_tested'] is False and report['bds_tested'] is False

 # A2.7.4 is icon-only. Preserve A2.7.3's suspended-grill stabilization.
 grill=load(BP/'blocks/grill.json')['minecraft:block']
 visual=[x for x in grill['permutations'] if 'kaleidoscope_grilling:legged' in x.get('condition','')]
 assert len(visual)==4
 assert all('grill_legged' not in x['components']['minecraft:geometry'] for x in visual)
 assert (BP/'blocks/grill_legs.json').is_file()
 for p in (BP/'scripts').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True)

 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json')
   matches=[x.parent for x in dist.rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})

 result={
  'version':'A2.7.4','exact_java_default_icons':39,'exact_java_frame0_icons':2,'total_formal_icons':41,
  'all_icon_git_blobs_match_upstream':True,'icon_size':[16,16],
  'slime_gui_animation_exact':False,'mysterious_gui_animation_exact':False,
  'a273_grill_stabilization_preserved':True,
  'compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False
 }
 out=P/'reports'/('a274-dash-verification.json' if a.compiled else 'a274-structure-verification.json')
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.read_text(encoding='utf-8'))

if __name__=='__main__':main()
