from __future__ import annotations
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core'
BP=P/'behavior_pack'
RP=P/'resource_pack'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94'
COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681'
CV=[1,0,6]


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def formal_icon_stems():
    out=[]
    for p in sorted((BP/'items').glob('*.json')):
        stem=p.stem
        if (stem.startswith('raw_') or stem.startswith('grilled_')) and stem.endswith('_skewer'):
            out.append(stem)
        elif stem in ('ordinary_skewer','mysterious_skewer','dark_grilling'):
            out.append(stem)
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--compiled',action='store_true')
    args=ap.parse_args()

    for p in P.rglob('*.json'):
        load(p)

    bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
    assert bm['header']['version']==[2,7,3]
    assert rm['header']['version']==[2,7,3]
    assert bm['header']['name']=='Kaleidoscope Grilling A2.7.3 Stabilized BP'
    assert rm['header']['name']=='Kaleidoscope Grilling A2.7.3 Stabilized RP'
    assert {'uuid':COOKERY_BP,'version':CV} in bm['dependencies']
    assert {'uuid':COOKERY_RP,'version':CV} in rm['dependencies']
    assert {'module_name':'@minecraft/server','version':'2.9.0'} in bm['dependencies']

    # Inventory/UI is now a true rendered icon rather than the Java model material sheet.
    stems=formal_icon_stems()
    assert len(stems)==41,len(stems)
    tex=load(RP/'textures/item_texture.json')['texture_data']
    hashes={}
    alpha_stats={}
    for stem in stems:
        path=RP/f'textures/items/{stem}.png'
        assert path.is_file(),path
        im=Image.open(path).convert('RGBA')
        assert im.size==(64,64),(stem,im.size)
        a=np.asarray(im)[...,3]
        assert a[0,0]==0 and a[-1,-1]==0,stem
        visible=int((a>0).sum())
        assert 20<visible<3000,(stem,visible)
        ys,xs=np.nonzero(a>0)
        assert xs.max()-xs.min()+1>=8,(stem,'width')
        assert ys.max()-ys.min()+1>=8,(stem,'height')
        assert tex[stem]['textures']==f'textures/items/{stem}'
        hashes[stem]=hashlib.sha256(path.read_bytes()).hexdigest()
        alpha_stats[stem]=visible
    # A single leaked UV sheet copied under many names would fail this diversity floor.
    assert len(set(hashes.values()))>=38,len(set(hashes.values()))
    assert hashes['raw_golden_skewer']!=hashes['raw_beef_skewer']
    assert (P/'reports/a273-item-icon-contact.png').is_file()
    icon_report=load(P/'reports/a273-item-icons.json')
    assert icon_report['count']==41

    # The main grill top no longer relies on negative-Y leg geometry.
    grill=load(BP/'blocks/grill.json')['minecraft:block']
    visual=[x for x in grill['permutations'] if 'kaleidoscope_grilling:legged' in x.get('condition','')]
    assert len(visual)==4
    for row in visual:
        geo=row['components']['minecraft:geometry']
        assert geo in ('geometry.kg_a23.grill_flat','geometry.kg_a23.grill_flat_lit'),geo
        assert 'grill_legged' not in geo

    helper=load(BP/'blocks/grill_legs.json')['minecraft:block']
    assert helper['description']['identifier']=='kaleidoscope_grilling:grill_legs'
    assert helper['components']['minecraft:collision_box'] is False
    assert helper['components']['minecraft:selection_box'] is False
    assert 'minecraft:replaceable' in helper['components']
    assert helper['description']['states']['kaleidoscope_grilling:direction']==['north','south','west','east']

    geo=load(RP/'models/blocks/grill_legs.geo.json')['minecraft:geometry'][0]
    assert geo['description']['identifier']=='geometry.kg_a273.grill_legs'
    cubes=[c for b in geo['bones'] for c in b.get('cubes',[])]
    assert len(cubes)>=4
    for c in cubes:
        y=float(c['origin'][1]);h=float(c['size'][1])
        assert -1e-6<=y<=16+1e-6,(y,h)
        assert -1e-6<=y+h<=16+1e-6,(y,h)

    runtime=(BP/'scripts/main.js').read_text(encoding='utf-8')
    for token in (
        "GRILL_LEGS_ID='kaleidoscope_grilling:grill_legs'",
        'function ensureGrillLegs',
        'function removeGrillLegs',
        "below.typeId!==GRILL_LEGS_ID&&below.typeId!=='minecraft:air'",
        "helper?.typeId===GRILL_LEGS_ID",
        'removeGrillLegs(block);block.setType'
    ):
        assert token in runtime,token
    for p in (BP/'scripts').glob('*.js'):
        subprocess.run(['node','--check',str(p)],check=True)

    stab=load(P/'reports/a273-stabilization.json')
    assert stab['version']=='A2.7.3'
    assert stab['item_render_split']['formal_icon_count_expected']==41
    assert stab['grill_render_fix']['helper_geometry_y_range']==[0,16]
    assert stab['minecraft_tested_after_fix'] is False
    assert stab['bds_tested_after_fix'] is False

    compiled=[]
    if args.compiled:
        dist=P/'builds/dist'
        for name,source in [('behavior_pack',BP),('resource_pack',RP)]:
            manifest=load(source/'manifest.json')
            matches=[x.parent for x in dist.rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']]
            assert len(matches)==1,(name,matches)
            target=matches[0];count=0
            for p in source.rglob('*'):
                if not p.is_file() or p.name.startswith('.'):
                    continue
                q=target/p.relative_to(source)
                assert q.is_file(),str(q)
                if p.suffix=='.json':
                    assert load(p)==load(q),str(q)
                else:
                    assert p.read_bytes()==q.read_bytes(),str(q)
                count+=1
            compiled.append({'pack':name,'compared_files':count,'matches_source':True})

    result={
      'version':'A2.7.3',
      'formal_ui_icons':41,
      'distinct_icon_hashes':len(set(hashes.values())),
      'grill_main_negative_y_geometry':False,
      'grill_helper_block':True,
      'grill_helper_cubes':len(cubes),
      'dash_compiled_and_compared':args.compiled,
      'compiled_packs':compiled,
      'minecraft_tested_after_fix':False,
      'bds_tested_after_fix':False
    }
    out=P/'reports'/('a273-dash-verification.json' if args.compiled else 'a273-structure-verification.json')
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(out.read_text(encoding='utf-8'))


if __name__=='__main__':
    main()
