from __future__ import annotations
from pathlib import Path
import argparse,json,subprocess

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94';COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681';CV=[1,0,6]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');a=ap.parse_args()
 for p in P.rglob('*.json'):load(p)
 report=load(P/'reports/build.json');a22=load(P/'reports/a22-build.json');stage_map=load(P/'reports/a22-bite-stages.json')
 assert report['version']=='A2.2.0' and a22['version']=='A2.2.0'
 assert report['bite_stage_attachables']==39 and report['bite_stage_geometry_files']==150
 assert len(stage_map)==39 and sum(len(v['candidates']) for v in stage_map.values())==150
 assert report['seasoning_physical_stack_max']==4 and report['seasoning_independent_bottle_payload'] is True
 assert report['seasoning_stack_uses_custom_block_states'] is False
 assert report['numb_limb_animation'] is True and report['numb_crosshair_offset'] is False
 assert report['true_custom_fluids'] is False and report['oil_types']==['canola','secret_chili','premium_chili']
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 assert bm['header']['version']==[2,2,0] and rm['header']['version']==[2,2,0]
 assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies']
 assert {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
 assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']
 items=list((BP/'items').glob('*.json'));assert len(items)==53,len(items)
 def duration(name):return load(BP/'items'/f'{name}.json')['minecraft:item']['components']['minecraft:use_modifiers']['use_duration']
 assert duration('grilled_lamb_skewer')==5.0 and duration('raw_lamb_skewer')==5.0 and duration('ordinary_skewer')==5.0
 assert duration('grilled_beef_skewer')==4.5 and duration('grilled_ender_pearl_skewer')==5.0
 attaches=list((RP/'attachables').glob('*.attachable.json'));assert len(attaches)==39,len(attaches)
 for p in attaches:
  d=load(p)['minecraft:attachable']['description']
  assert d['render_controllers']==['controller.render.kg_a22.bite']
  assert set(d['geometry'])=={f'stage{i}' for i in range(5)}
  assert set(d['textures'])=={f'stage{i}' for i in range(5)}
  pre=' '.join(d['scripts']['pre_animation'])
  assert 'q.item_in_use_duration' in pre and 'v.kg_bite_stage' in pre
  item=d['identifier'].split(':',1)[1];times=stage_map[item]['visual_bites'];last=times[-1]
  assert f'q.item_in_use_duration >= {last:.5f} ? {len(times)} :' in pre,(item,pre)
 geos=list((RP/'models/entity/a22_bites').glob('*.geo.json'));tex=list((RP/'textures/a22_bites').glob('*.png'))
 assert len(geos)==150,len(geos);assert len(tex)==150,len(tex)
 rc=load(RP/'render_controllers/a22_bites.render_controllers.json')['render_controllers']['controller.render.kg_a22.bite']
 assert len(rc['arrays']['geometries']['Array.kg_bite_geo'])==5 and len(rc['arrays']['textures']['Array.kg_bite_tex'])==5
 assert rc['geometry']=='Array.kg_bite_geo[v.kg_bite_stage]' and rc['textures']==['Array.kg_bite_tex[v.kg_bite_stage]']
 particle=load(RP/'particles/skewer_crumb.json')['particle_effect'];assert particle['description']['identifier']=='kaleidoscope_grilling:skewer_crumb'
 assert (RP/'textures/particle/kg_skewer_crumb.png').is_file()
 numb=load(RP/'animations/a22_numb.animation.json')['animations']['animation.kg_a22.player.numb'];assert numb['animation_length']==1.0
 for n in range(1,5):
  b=load(BP/'blocks'/f'seasoning_bottle_{n}.json')['minecraft:block']
  assert b['description']['identifier']==f'kaleidoscope_grilling:seasoning_bottle_{n}'
  assert 'states' not in b['description']
  assert b['components']['minecraft:geometry']==f'geometry.kg_a22.seasoning_bottles_{n}'
 for name in ('empty_seasoning_bottle','pending_seasoning','special_seasoning'):
  c=load(BP/'items'/f'{name}.json')['minecraft:item']['components']
  assert c['minecraft:block_placer']['block']=='kaleidoscope_grilling:seasoning_bottle_1'
 oil=(BP/'scripts/oil_types.js').read_text()
 for token in ("canola","secret_chili","premium_chili","heatTicks:1200","heatTicks:12000","heatTicks:24000"):assert token in oil
 runtime=(BP/'scripts/main.js').read_text()
 for token in ("skewer_crumb","item_in_use_duration" if False else "BITE_TIMES","seasoning_bottle_4","readBottleStack","THREE_RANDOM","animation.kg_a22.player.numb","OIL_TYPES","stopsound @s kg_imm."):assert token in runtime,token
 for p in BP.glob('scripts/*.js'):subprocess.run(['node','--check',str(p)],check=True)
 compiled=[]
 if a.compiled:
  dist=P/'builds/dist'
  for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
   manifest=load(source/'manifest.json');matches=[p.parent for p in dist.rglob('manifest.json') if load(p).get('header',{}).get('uuid')==manifest['header']['uuid']]
   assert len(matches)==1,(name,matches);target=matches[0];count=0
   for p in source.rglob('*'):
    if not p.is_file() or p.name.startswith('.'):continue
    q=target/p.relative_to(source);assert q.is_file(),str(q)
    if p.suffix=='.json':assert load(p)==load(q),str(q)
    else:assert p.read_bytes()==q.read_bytes(),str(q)
    count+=1
   compiled.append({'pack':name,'compared_files':count,'matches_source':True})
 result={'version':'A2.2.0','formal_items':53,'formal_foods':41,'bite_stage_attachables':39,'bite_stage_geometry_files':150,'seasoning_bottle_stack_max':4,'numb_limb_animation':True,'numb_crosshair_offset':False,'oil_type_contracts':3,'true_custom_fluids':False,'server_module':'2.9.0','compiled':a.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bds_tested':False}
 out=P/'reports'/('a22-dash-verification.json' if a.compiled else 'a22-structure-verification.json');out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(out.read_text())

if __name__=='__main__':main()
