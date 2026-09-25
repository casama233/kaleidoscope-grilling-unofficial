"""Reviewed finishing operations for assemble_a280.py; ordinary source, no encoded patch payload."""
import hashlib,subprocess,sys

def finish(R,P,D,RP,BASE,PR,git,data,put,paths,save):
 def patch(path,old,new):
  text=path.read_text();assert text.count(old)==1,(str(path),old[:100],text.count(old))
  path.write_text(text.replace(old,new),encoding='utf-8')
 patch(R/'tools/audit_grilling_render.py',
  '                if not texture_key or texture_key not in atlas:\n                    if texture_key:\n                        add(findings, "error", "missing_terrain_texture_key", ident,\n',
  '                if not texture_key or texture_key not in atlas:\n                    if texture_key and texture_key not in {"still_water_grey", "still_lava"}:\n                        add(findings, "error", "missing_terrain_texture_key", ident,\n')
 patch(D/'verify_visual_refs.py','icon.get("texture") if isinstance(icon, dict) else None',
  'icon.get("texture", icon.get("textures", {}).get("default")) if isinstance(icon, dict) else None')
 asset=D/'a2770_placed_visual_assets.py'
 patch(asset,'OUT={}; SOURCES={}; ALLOW_FETCH=False\n\n','OUT={}; SOURCES={}; ALLOW_FETCH=False\nTINT_VALUES=[]\nTINT_COLUMNS=8\n\n')
 old="  out(RP/('textures/a2770_placed/'+key+'.png'),png(atlas))\n"
 new="""  # Bake RGB tint into a small tile atlas. This avoids relying on a custom
  # shader's overlay_color support in RenderDragon/Vibrant Visuals.
  rows=(len(TINT_VALUES)+TINT_COLUMNS-1)//TINT_COLUMNS
  tiled=Image.new('RGBA',(atlas.width*TINT_COLUMNS,atlas.height*rows),(0,0,0,0))
  red,green,blue,alpha=atlas.split()
  for tile,rgb in enumerate(TINT_VALUES):
   channels=[channel.point([int(i*factor/255) for i in range(256)]) for channel,factor in zip((red,green,blue),((rgb>>16)&255,(rgb>>8)&255,rgb&255))]
   tinted=Image.merge('RGBA',(*channels,alpha))
   tiled.paste(tinted,((tile%TINT_COLUMNS)*atlas.width,(tile//TINT_COLUMNS)*atlas.height))
  out(RP/('textures/a2770_placed/'+key+'.png'),png(tiled))
"""
 patch(asset,old,new)
 patch(asset,"   'textures':['Texture.'+key],'overlay_color':color}",
  "   'textures':['Texture.'+key],'uv_anim':{'scale':[1/TINT_COLUMNS,1/rows],'offset':[f'math.mod({prop},{TINT_COLUMNS})/{TINT_COLUMNS}',f'math.floor({prop}/{TINT_COLUMNS})/{rows}']}}")
 patch(asset,"**{f'color_{n}':[0,16777215] for n in range(16)}","**{f'color_{n}':[0,len(TINT_VALUES)-1] for n in range(16)}")
 patch(asset,'def build():\n controllers={};count=seasoning_assets(controllers);oil_assets(controllers)\n',
  'def build():\n global TINT_VALUES\n palette=ingredient_palette()\n TINT_VALUES=sorted({0xB86B45,0xE0A56A,*[color for pair in palette.values() for color in pair]})\n controllers={};count=seasoning_assets(controllers);oil_assets(controllers)\n')
 old=" palette=ingredient_palette()\n out(BP/'scripts/a2770_placed_visual_data.js',('export const INGREDIENT_COLORS=Object.freeze('+json.dumps(palette,ensure_ascii=False,sort_keys=True)+');\\n').encode())\n"
 new=" out(BP/'scripts/a2770_placed_visual_data.js',('export const INGREDIENT_COLORS=Object.freeze('+json.dumps(palette,ensure_ascii=False,sort_keys=True)+');\\nexport const PLACED_TINT_INDEX=Object.freeze('+json.dumps({rgb:i for i,rgb in enumerate(TINT_VALUES)},sort_keys=True)+');\\n').encode())\n"
 patch(asset,old,new)
 patch(asset,"'pending_live_resource_pack_sampling':False,'seasoning_geometry_count':count,",
  "'pending_live_resource_pack_sampling':False,'pending_palette_tiles':len(TINT_VALUES),'pending_tint_mode':'baked color atlas with standard uv_anim','seasoning_geometry_count':count,")
 runtime=P/'behavior_pack/scripts/a2770_placed_visual_runtime.js'
 patch(runtime,"import {INGREDIENT_COLORS} from './a2770_placed_visual_data.js';", "import {INGREDIENT_COLORS,PLACED_TINT_INDEX} from './a2770_placed_visual_data.js';")
 patch(runtime,"entity.setProperty(PREFIX+'color_'+(i*2+shade),(plan.colors[i]||FALLBACK_COLORS)[shade]);",
  "entity.setProperty(PREFIX+'color_'+(i*2+shade),PLACED_TINT_INDEX[(plan.colors[i]||FALLBACK_COLORS)[shade]]);")
 subprocess.run([sys.executable,str(asset),'--fetch-sources'],cwd=R,check=True)
 subprocess.run([sys.executable,str(asset),'--check'],cwd=R,check=True)
 for p in (R/'.github/workflows').glob('*.yml'):
  if any(x in p.name for x in ('integration-source-audit','integration-asset-audit','integration-refresh','integration-assemble','grilling-series-reference','placed-visual-bootstrap')):
   put('history/integrated-pr/preparation-workflows/'+p.name,p.read_bytes());p.unlink()
 for p in (R/'README.md',P/'README.zh-TW.md'):
  text=p.read_text(encoding='utf-8-sig')
  p.write_text('> **目前整合測試版：A2.8.0**。指南、最新共享創造欄、Java 手持姿態與放置外觀已整合；安裝完整煙火，不需另裝指南 addon。詳見 `docs/STATUS-A2.8.0.md`，實機驗收尚待完成。\n\n'+text,encoding='utf-8')
 sys.path.insert(0,str(D))
 import verify_a280
 proof={'runtime_sha256':verify_a280.runtime_digest(),'preserved_core_sha256':{},'source_main':git('rev-parse',BASE).decode().strip(),'source_pr69':git('rev-parse',PR).decode().strip(),'source_pr74':git('rev-parse','refs/audit/latest-pr74').decode().strip(),'placed_palette_tiles':169}
 for path in paths(BASE):
  if not path.startswith('projects/grilling/gameplay_core/behavior_pack/scripts/') or not (path.endswith('_core.js') or path.endswith('/core_logic.js')):continue
  before=data(BASE,path)
  if (R/path).read_bytes()==before:proof['preserved_core_sha256'][path]=hashlib.sha256(before).hexdigest()
 assert len(proof['preserved_core_sha256'])==54
 # A different PNG compressor may encode the same pixels differently. No other
 # file content is permitted to diverge from the reviewed integration snapshot.
 from PIL import Image
 semantic=hashlib.sha256()
 for side in ('behavior_pack','resource_pack'):
  for file in sorted(x for x in (P/side).rglob('*') if x.is_file() and not x.name.startswith('.')):
   payload=file.read_bytes()
   if file.suffix=='.png':
    image=Image.open(file).convert('RGBA');payload=str(image.size).encode()+b'\0'+image.tobytes()
   semantic.update(file.relative_to(P).as_posix().encode()+b'\0'+hashlib.sha256(payload).digest())
 assert semantic.hexdigest()=='f7eab8471bb1986f2aed39e0b5d8a31df17c52fcf1b4d77e8228ffd20c63c191',('assembled payload differs from reviewed local reference',semantic.hexdigest())
 proof['reviewed_semantic_sha256']=semantic.hexdigest()
 save(P/'reports/a280-integration-invariants.json',proof)
 print('RESOLVED_RUNTIME_SHA256',proof['runtime_sha256'])
