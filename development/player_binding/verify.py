"""A1.16 structural and real-Dash-output validation. Not a Minecraft client/BDS claim."""
from __future__ import annotations
from pathlib import Path
import argparse, json, math

ROOT=Path(__file__).resolve().parents[2]
LAB=ROOT/'projects/grilling/integration/immersion_lab'
REPORT=ROOT/'projects/grilling/reports/player_binding_a116'
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94'
COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681'
V=[1,0,6]

def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def finite(v):
    if isinstance(v,float) and not math.isfinite(v):raise ValueError('Non-finite JSON number')
    if isinstance(v,dict):
        for x in v.values():finite(x)
    if isinstance(v,list):
        for x in v:finite(x)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--compiled',action='store_true');args=ap.parse_args()
    rp=LAB/'resource_pack';bp=LAB/'behavior_pack'
    for p in LAB.rglob('*.json'):finite(load(p))
    bm=load(bp/'manifest.json');rm=load(rp/'manifest.json')
    assert bm['header']['version']==[0,1,16] and rm['header']['version']==[0,1,16]
    assert {'uuid':COOKERY_BP,'version':V} in bm['dependencies']
    assert {'uuid':COOKERY_RP,'version':V} in rm['dependencies']
    assert all(x['version']==[0,1,16] for x in bm['modules']+rm['modules'])
    animations=load(rp/'animations/player_binding.animation.json')['animations']
    expected={f'animation.kg_imm.player.eat_{p}.{h}' for p in ('one','two','three','three_alt','four') for h in ('main','off')}
    expected|={f'animation.kg_imm.player.{a}.{h}' for a in ('brush','season','reach') for h in ('main','off')}
    assert set(animations)==expected and len(animations)==16
    assert not any('three_random' in k for k in animations)
    for key,a in animations.items():
        assert a.get('override_previous_animation') is True
        if '.eat_three.' in key:assert abs(a['animation_length']-5.0)<1e-9
        if '.eat_' in key and '.eat_three.' not in key:assert abs(a['animation_length']-4.5)<1e-9
        arm=('leftarm' if key.endswith('.off') else 'rightarm')
        if '.eat_' in key or '.brush.' in key or '.season.' in key or '.reach.' in key:
            assert arm in a['bones']
    geos={g['description']['identifier']:g for g in load(rp/'models/entity/hand_props.geo.json')['minecraft:geometry']}
    assert set(geos)=={'geometry.kg_imm.hand_skewer','geometry.kg_imm.hand_brush','geometry.kg_imm.hand_seasoning','geometry.kg_imm.bite_piece'}
    for g in geos.values():
        roots=[b for b in g['bones'] if b['name']=='prop'];assert len(roots)==1
        assert roots[0]['binding']=='q.item_slot_to_bone_name(context.item_slot)'
    for ident in ['eat_one','eat_two','eat_three','eat_three_alt','eat_three_random','eat_four','oil_brush','seasoning_bottle','visual_0','visual_1','visual_2','visual_3','visual_4','bite_piece']:
        item=load(bp/'items'/f'{ident}.json')['minecraft:item'];assert item['description']['identifier']=='kg_imm:'+ident
        assert item['components']['minecraft:allow_off_hand'] is True
        attach=load(rp/'attachables'/f'{ident}.attachable.json')['minecraft:attachable']
        assert attach['description']['identifier']=='kg_imm:'+ident
    scene=load(rp/'animations/rehearsal.animation.json')['animations']['animation.kg_imm.rehearsal']['bones']
    assert scene['brush_tool']=={'scale':0} and scene['season_tool']=={'scale':0}
    definition=load(bp/'entities/rehearsal.json')['minecraft:entity']
    assert all(x.get('swing') is False for x in definition['components']['minecraft:interact']['interactions'])
    assert not (rp/'entity/player.entity.json').exists() and not (rp/'entity/player.json').exists()
    plan=load(REPORT/'binding-plan.json')
    assert plan['cookery_dependency']['behavior_pack_uuid']==COOKERY_BP
    assert plan['player_animation_count']==16
    rules=plan['profiles']
    assert rules['ONE']=={'durationTicks':90,'bites':[1.16667,3.08333]}
    assert rules['TWO']=={'durationTicks':90,'bites':[.95833,4.0]}
    assert rules['THREE']=={'durationTicks':100,'bites':[.95833,2.33333,3.54167]}
    assert rules['THREE_ALT']=={'durationTicks':90,'bites':[.95833,2.16667,3.5]}
    assert rules['FOUR']=={'durationTicks':90,'bites':[.95833,2.33333,3.45833,4.08333]}
    compiled=[]
    if args.compiled:
        for pack in ('resource_pack','behavior_pack'):
            source=LAB/pack;manifest=load(source/'manifest.json')
            matches=[x.parent for x in (LAB/'builds/dist').rglob('manifest.json') if load(x).get('header',{}).get('uuid')==manifest['header']['uuid']]
            assert len(matches)==1,(pack,matches)
            files=[p for p in source.rglob('*') if p.is_file() and not p.name.startswith('.')]
            for p in files:
                dst=matches[0]/p.relative_to(source);assert dst.is_file(),str(dst)
                if p.suffix=='.json':assert load(p)==load(dst),str(dst)
                else:assert p.read_bytes()==dst.read_bytes(),str(dst)
            compiled.append({'pack':pack,'uuid':manifest['header']['uuid'],'compared_files':len(files),'matches_source':True})
    result={'version':'A1.16.0','cookery_dependency_verified':True,'player_animations':len(animations),
            'attachable_geometries':len(geos),'profile_items':6,'main_off_hand_variants':True,
            'compiled':args.compiled,'compiled_packs':compiled,'minecraft_tested':False,'bridge_ui_tested':False,
            'scope':'structural and real Dash output verification; native client camera/skin/contact still needs Minecraft acceptance'}
    REPORT.mkdir(parents=True,exist_ok=True)
    out=REPORT/('dash-verification.json' if args.compiled else 'structure-verification.json')
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(out.read_text())
if __name__=='__main__':main()
