from __future__ import annotations
import copy, json, math, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LAB=ROOT/'projects/grilling/integration/immersion_lab'
REPORT=ROOT/'projects/grilling/reports/player_binding_a116'
VERSION=[0,1,16]
COOKERY_BP='10f37ae2-9ccf-435f-b34b-0eec8191cd94'
COOKERY_RP='c89dc8df-c3fc-4bc8-8bd0-527abba76681'
COOKERY_VER=[1,0,6]
PROFILE_ORDER=['ONE','TWO','THREE','THREE_ALT','THREE_RANDOM','FOUR']
RESOLVED=['ONE','TWO','THREE','THREE_ALT','FOUR']
MOJANG_PLAYER_REF='46ba6ea985fb5a92d79a9419198f10dda14c199d'

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(data,(dict,list)):
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:
        path.write_text(data,encoding='utf-8')

def sample(t,times,values):
    if t<=times[0]: return values[0]
    if t>=times[-1]: return values[-1]
    right=1
    while t>times[right]: right+=1
    left=right-1
    before=max(0,left-1)
    after=min(len(times)-1,right+1)
    p=(t-times[left])/(times[right]-times[left])
    p2=p*p
    p3=p2*p
    p0,p1,p2v,p3v=values[before],values[left],values[right],values[after]
    return .5*((2*p1)+(-p0+p2v)*p+(2*p0-5*p1+4*p2v-p3v)*p2+(-p0+3*p1-3*p2v+p3v)*p3)

def vec(curves,prefix,t):
    return [sample(t,curves[prefix+'_TIMES'],curves[prefix+'_'+axis]) for axis in ('X','Y','Z')]

def fmt(x):
    if abs(x)<5e-8: x=0
    return round(float(x),6)

def keytime(t):
    return f'{t:.5f}'.rstrip('0').rstrip('.') or '0'

def cond(fp,tp):
    if isinstance(fp,str): return fp
    if abs(fp-tp)<1e-6: return fmt(tp)
    return f'variable.is_first_person ? {fmt(fp)} : {fmt(tp)}'

def default_arm(side):
    return (-5.0,2.0,0.0) if side==1 else (5.0,2.0,0.0)

def fp_base(side):
    # Mojang current right-arm empty-hand baseline. Left is a mirrored calibration
    # and therefore remains engine-acceptance pending until left-handed client testing.
    return ([13.5,-10,12],[95,-45,115]) if side==1 else ([-13.5,-10,12],[95,45,-115])

def java_generic_pose(A,profile,t,side):
    if profile=='THREE_ALT':
        pos=vec(A,'SQUID_POSITION',t)
        rot=vec(A,'SQUID_ROTATION',t)
        item_y=sample(t,A['SQUID_ITEM_POSITION_TIMES'],A['SQUID_ITEM_POSITION_Y'])
        item_rx=sample(t,A['SQUID_ITEM_ROTATION_TIMES'],A['SQUID_ITEM_ROTATION_X'])
        item_rz=0
    elif profile=='TWO':
        pos=vec(A,'TWO_POSITION',t)
        rot=vec(A,'TWO_ROTATION',t)
        item_y=0
        item_rx=sample(t,[.45833,.95833,1.20833],[0,12.5,0])
        item_rz=sample(t,A['TWO_ITEM_ROTATION_Z_TIMES'],A['TWO_ITEM_ROTATION_Z'])
    else:
        pos=vec(A,'POSITION',t)
        rot=vec(A,'ROTATION',t)
        item_y=0
        item_rx=sample(t,A['ITEM_ROTATION_TIMES'],A['ITEM_ROTATION_X'])
        item_rz=0
    mirror=side
    xrot=-rot[0]
    ydir=-mirror if profile=='TWO' else mirror
    yrot=ydir*rot[1]
    zrot=mirror*rot[2]
    yr=math.radians(yrot)
    zr=math.radians(zrot)
    pd=-mirror
    cx=pd*math.cos(zr)*math.cos(yr)
    cy=pd*math.sin(zr)*math.cos(yr)
    cz=pd*-math.sin(yr)
    x=-mirror*(4+pos[0])+cx
    y=2-pos[1]+cy+(2 if profile=='TWO' else 0)
    z=pos[2]+cz
    base=default_arm(side)
    tp_pos=[x-base[0],-(y-base[1]),z-base[2]]
    tp_rot=[xrot,yrot,zrot]
    item_pos=[-mirror,9-item_y,-6]
    item_rot=[180+item_rx,0,mirror*item_rz]
    return tp_pos,tp_rot,item_pos,item_rot

def ender_arm(E,profile,t,side,active):
    one=profile=='ONE'
    if one:
        p='ONE_RIGHT' if active else 'ONE_LEFT'
        times=E[p+'_TIMES']
        pos=[sample(t,times,E[p+'_'+a]) for a in ('X','Y','Z')]
        rot=[sample(t,times,E[p+'_ROT_'+a]) for a in ('X','Y','Z')]
    else:
        p='RIGHT' if active else 'LEFT'
        pos=vec(E,p+'_POSITION',t)
        rot=vec(E,p+'_ROTATION',t)
    authored=1 if active else -1
    actual=side if active else -side
    xrot=-rot[0]
    yrot=actual*rot[1]
    zrot=rot[2]
    yr=math.radians(yrot)
    zr=math.radians(zrot)
    pd=-actual
    cx=pd*math.cos(zr)*math.cos(yr)
    cy=pd*math.sin(zr)*math.cos(yr)
    cz=pd*-math.sin(yr)
    x=-actual*(4+authored*pos[0])+cx
    y=2-pos[1]+cy
    z=pos[2]+cz
    if one: y+=3.8
    if one and active:
        zrot-=actual*7.5
        zr=math.radians(zrot)
        xr=math.radians(xrot)
        x += math.cos(zr)*math.sin(yr)*math.sin(xr)-math.sin(zr)*math.cos(xr)
        y += math.sin(zr)*math.sin(yr)*math.sin(xr)+math.cos(zr)*math.cos(xr)
        z += math.cos(yr)*math.sin(xr)
    base=default_arm(actual)
    return [x-base[0],-(y-base[1]),z],[xrot,yrot,zrot]

def ender_pose(E,profile,t,side):
    active_pos,active_rot=ender_arm(E,profile,t,side,True)
    helper_pos,helper_rot=ender_arm(E,profile,t,side,False)
    if profile=='ONE':
        main_y=sample(t,[0,.45833,1.29167],[0,0,-3])
        main_rx=sample(t,[.20833,.45833,1.29167],[12.5,0,29.5])
        second=[-9,-2,5,75,0,-275,1 if t>=1.16667 else 0]
    else:
        main_y=sample(t,E['MAIN_ITEM_POSITION_TIMES'],E['MAIN_ITEM_POSITION_Y'])
        main_rx=sample(t,E['MAIN_ITEM_ROTATION_TIMES'],E['MAIN_ITEM_ROTATION_X'])
        second=[
            sample(t,E['SECOND_ITEM_TRANSFORM_TIMES'],E['SECOND_ITEM_POSITION_X']),
            sample(t,E['SECOND_ITEM_TRANSFORM_TIMES'],E['SECOND_ITEM_POSITION_Y']),
            sample(t,E['SECOND_ITEM_TRANSFORM_TIMES'],E['SECOND_ITEM_POSITION_Z']),
            sample(t,E['SECOND_ITEM_TRANSFORM_TIMES'],E['SECOND_ITEM_ROTATION_X']),
            sample(t,E['SECOND_ITEM_TRANSFORM_TIMES'],E['SECOND_ITEM_ROTATION_Y']),
            sample(t,E['SECOND_ITEM_TRANSFORM_TIMES'],E['SECOND_ITEM_ROTATION_Z']),
            max(0,min(1,sample(t,E['SECOND_ITEM_SCALE_TIMES'],E['SECOND_ITEM_SCALE'])))
        ]
    main_pos=[-side*(1.975)+side,8.925-main_y,-7.575]
    main_rot=[180+main_rx,0,0]
    helper_actual=-side
    authored=-1
    mirror=helper_actual*authored
    second_pos=[(-mirror*(10+second[0])+helper_actual),8.875-second[1],-5.75+second[2]]
    second_rot=[-second[3],helper_actual*second[4],second[5]+95]
    return active_pos,active_rot,main_pos,main_rot,helper_pos,helper_rot,second_pos,second_rot,second[6]

def fp_from_delta(tp_pos,tp_rot,base_tp_pos,base_tp_rot,side):
    bp,br=fp_base(side)
    return [bp[i]+tp_pos[i]-base_tp_pos[i] for i in range(3)],[br[i]+tp_rot[i]-base_tp_rot[i] for i in range(3)]

def bone_keys(pos_frames,rot_frames,fp_pos_frames=None,fp_rot_frames=None,scale_frames=None):
    out={}
    if fp_pos_frames:
        out['position']={keytime(t):[cond(fp[i],tp[i]) for i in range(3)] for (t,tp),(_,fp) in zip(pos_frames,fp_pos_frames)}
        out['rotation']={keytime(t):[cond(fp[i],tp[i]) for i in range(3)] for (t,tp),(_,fp) in zip(rot_frames,fp_rot_frames)}
    else:
        out['position']={keytime(t):[fmt(x) for x in v] for t,v in pos_frames}
        out['rotation']={keytime(t):[fmt(x) for x in v] for t,v in rot_frames}
    if scale_frames:
        out['scale']={keytime(t):[fmt(v),fmt(v),fmt(v)] for t,v in scale_frames}
    return out

def make_eat_animation(curves,profile,side,fps=60):
    dur=curves['profiles'][profile]['duration_ticks']/20
    A=curves['curves']['SkewerEatingAnimation']['arrays']
    E=curves['curves']['EnderPearlEatingAnimation']['arrays']
    times=[i/fps for i in range(round(dur*fps)+1)]
    if times[-1]<dur: times.append(dur)
    active=[];arot=[];item=[];irot=[]
    helper=[];hrot=[];hitem=[];hirot=[];hscale=[]
    for t in times:
        if profile in ('ONE','THREE'):
            p,r,ip,ir,hp,hr,hip,hir,hs=ender_pose(E,profile,t,side)
            helper.append((t,hp));hrot.append((t,hr));hitem.append((t,hip));hirot.append((t,hir));hscale.append((t,hs))
        else:
            p,r,ip,ir=java_generic_pose(A,profile,t,side)
        active.append((t,p));arot.append((t,r));item.append((t,ip));irot.append((t,ir))
    basep=active[0][1];baser=arot[0][1]
    fp_pos=[];fp_rot=[]
    for (t,p),(_,r) in zip(active,arot):
        a,b=fp_from_delta(p,r,basep,baser,side);fp_pos.append((t,a));fp_rot.append((t,b))
    active_name='rightarm' if side==1 else 'leftarm'
    item_name='rightitem' if side==1 else 'leftitem'
    bones={active_name:bone_keys(active,arot,fp_pos,fp_rot),item_name:bone_keys(item,irot)}
    if helper:
        hs=-side
        name='rightarm' if hs==1 else 'leftarm'
        iname='rightitem' if hs==1 else 'leftitem'
        hbasep=helper[0][1];hbaser=hrot[0][1];hfp=[];hfr=[]
        for (t,p),(_,r) in zip(helper,hrot):
            a,b=fp_from_delta(p,r,hbasep,hbaser,hs);hfp.append((t,a));hfr.append((t,b))
        bones[name]=bone_keys(helper,hrot,hfp,hfr)
        bones[iname]=bone_keys(hitem,hirot,scale_frames=hscale)
    return {'animation_length':dur,'override_previous_animation':True,'bones':bones}

def smooth01(x):
    x=max(0,min(1,x)); return x*x*(3-2*x)

def make_tool(kind,side,fps=60):
    core=1.0 if kind=='brush' else .5
    lead=tail=.15
    dur=core+lead+tail
    times=[i/fps for i in range(round(dur*fps)+1)]
    if times[-1]<dur: times.append(dur)
    arm='rightarm' if side==1 else 'leftarm'
    item='rightitem' if side==1 else 'leftitem'
    arm_pos={};arm_rot={};item_pos={};item_rot={}
    bp,br=fp_base(side)
    for t in times:
        if t<lead:
            e=smooth01(t/lead); ct=0
        elif t>lead+core:
            e=smooth01((dur-t)/tail); ct=core
        else:
            e=1; ct=t-lead
        if kind=='brush':
            w=math.sin(2*math.pi*max(0,min(1,ct)))
            tp_r=[-math.degrees(1.32)*e,side*math.degrees(.18+.70*w)*e,side*math.degrees(.10+.42*w)*e]
            fp_p=[side*(.52+w*.25)*16*e,-.48*16*e,-.78*16*e]
            fp_r=[-24*e,180*e,side*(32+w*34)*e]
            tp_item_r=[0,0,side*w*16*e]
        else:
            p=max(0,min(1,ct/.5));w=math.sin(4*math.pi*p);a=math.sin(math.pi*p)
            tp_r=[math.degrees(-1.75-.35*a+.18*w)*e,side*math.degrees(.35+.95*w)*e,side*math.degrees(.55+.55*a+.25*w)*e]
            fp_p=[side*(.50+w*.08)*16*e,(-.41+a*.10)*16*e,-.82*16*e]
            fp_r=[(-28+a*42)*e,(180+side*w*18)*e,side*(22+w*25)*e+180*e]
            tp_item_r=[0,0,0]
        # First-person arm follows current Mojang base pose into/out of the authored camera-space item motion.
        fpa=[bp[i]*e for i in range(3)]
        fpr=[br[i]*e for i in range(3)]
        arm_pos[keytime(t)]=[cond(fpa[i],[0,0,0][i]) for i in range(3)]
        arm_rot[keytime(t)]=[cond(fpr[i],tp_r[i]) for i in range(3)]
        item_pos[keytime(t)]=[cond(fp_p[i],0) for i in range(3)]
        item_rot[keytime(t)]=[cond(fp_r[i],tp_item_r[i]) for i in range(3)]
    return {'animation_length':dur,'override_previous_animation':True,'bones':{
        arm:{'position':arm_pos,'rotation':arm_rot},item:{'position':item_pos,'rotation':item_rot}
    }},{'core_seconds':core,'lead_seconds':lead,'tail_seconds':tail,'total_seconds':dur}

def make_reach(curves,side,fps=60):
    A=curves['curves']['SkewerEatingAnimation']['arrays']
    half=.45833;dur=half*2
    times=[i/fps for i in range(round(dur*fps)+1)]
    if times[-1]<dur: times.append(dur)
    poses=[]
    for t in times:
        src=t if t<=half else max(0,dur-t)
        p,r,_,_=java_generic_pose(A,'FOUR',src,side);poses.append((t,p,r))
    basep=poses[0][1];baser=poses[0][2];fp_p=[];fp_r=[]
    for t,p,r in poses:
        a,b=fp_from_delta(p,r,basep,baser,side);fp_p.append((t,a));fp_r.append((t,b))
    arm='rightarm' if side==1 else 'leftarm'
    return {'animation_length':dur,'override_previous_animation':True,'bones':{
        arm:bone_keys([(t,p) for t,p,_ in poses],[(t,r) for t,_,r in poses],fp_p,fp_r)
    }}

def descendants(bones,root):
    children={}
    for b in bones: children.setdefault(b.get('parent'),[]).append(b['name'])
    out=[];stack=[root]
    while stack:
        n=stack.pop();out.append(n);stack+=children.get(n,[])
    return out

def build_geometry():
    src=json.loads((LAB/'resource_pack/models/entity/rehearsal.geo.json').read_text())['minecraft:geometry'][0]
    bones=src['bones'];byname={b['name']:b for b in bones};desc=src['description'];geos=[]
    sk=[{'name':'prop','pivot':[0,0,0],'binding':'q.item_slot_to_bone_name(context.item_slot)'}]
    for stage in range(5):
        root=f'bite{stage}'
        sk.append({'name':root,'parent':'prop','pivot':[0,0,0]})
        for n in descendants(bones,root):
            if n==root: continue
            b=copy.deepcopy(byname[n])
            b['parent']=root if b.get('parent')==root else b['parent']
            d=(-12,1,2)
            if 'pivot' in b: b['pivot']=[b['pivot'][i]+d[i] for i in range(3)]
            for c in b.get('cubes',[]):
                c['origin']=[c['origin'][i]+d[i] for i in range(3)]
                if 'pivot' in c: c['pivot']=[c['pivot'][i]+d[i] for i in range(3)]
            sk.append(b)
    geos.append({'description':{**desc,'identifier':'geometry.kg_imm.hand_skewer','visible_bounds_width':4,'visible_bounds_height':4},'bones':sk})
    def copied(root,newroot,delta):
        out=[{'name':newroot,'pivot':[0,0,0],'binding':'q.item_slot_to_bone_name(context.item_slot)'}]
        for n in descendants(bones,root):
            if n==root:continue
            b=copy.deepcopy(byname[n]);b['parent']=newroot if b.get('parent')==root else b['parent']
            if 'pivot' in b:b['pivot']=[b['pivot'][i]+delta[i] for i in range(3)]
            for c in b.get('cubes',[]):
                c['origin']=[c['origin'][i]+delta[i] for i in range(3)]
                if 'pivot' in c:c['pivot']=[c['pivot'][i]+delta[i] for i in range(3)]
            out.append(b)
        return out
    geos.append({'description':{**desc,'identifier':'geometry.kg_imm.hand_brush','visible_bounds_width':3,'visible_bounds_height':3},'bones':copied('brush_tool','prop',(0,-8,0))})
    geos.append({'description':{**desc,'identifier':'geometry.kg_imm.hand_seasoning','visible_bounds_width':3,'visible_bounds_height':3},'bones':copied('season_tool','prop',(0,-6,0))})
    piece_src=copy.deepcopy(byname['held0_instance_0_food3_1']);cube=piece_src['cubes'][0];center=[cube['origin'][i]+cube['size'][i]/2 for i in range(3)]
    piece_src['name']='piece';piece_src['parent']='prop';piece_src['pivot']=[0,0,0];cube['origin']=[cube['origin'][i]-center[i] for i in range(3)]
    if 'pivot' in cube:cube['pivot']=[cube['pivot'][i]-center[i] for i in range(3)]
    geos.append({'description':{**desc,'identifier':'geometry.kg_imm.bite_piece','visible_bounds_width':2,'visible_bounds_height':2},'bones':[
        {'name':'prop','pivot':[0,0,0],'binding':'q.item_slot_to_bone_name(context.item_slot)'},piece_src]})
    return {'format_version':'1.21.0','minecraft:geometry':geos}

def item(identifier,label,icon,menu=True):
    d={'identifier':identifier}
    if menu:d['menu_category']={'category':'items'}
    return {'format_version':'1.26.30','minecraft:item':{'description':d,'components':{
        'minecraft:display_name':{'value':label},
        'minecraft:icon':{'textures':{'default':icon}},
        'minecraft:allow_off_hand':True,'minecraft:max_stack_size':1,'minecraft:hand_equipped':True
    }}}

def attach(identifier,geometry,stage=None):
    anims={};scripts={}
    if stage is not None:
        anims['stage']=f'animation.kg_imm.attach.stage{stage}';scripts={'animate':['stage']}
    return {'format_version':'1.10.0','minecraft:attachable':{'description':{
        'identifier':identifier,'materials':{'default':'entity_alphablend'},
        'textures':{'default':'textures/kg_imm/scene'},'geometry':{'default':geometry},
        'animations':anims,'scripts':scripts,'render_controllers':['controller.render.kg_imm.hand_prop']
    }}}

def patch_manifests():
    bp=LAB/'behavior_pack/manifest.json';rp=LAB/'resource_pack/manifest.json'
    b=json.loads(bp.read_text());r=json.loads(rp.read_text())
    for m,name in ((b,'BP'),(r,'RP')):
        m['header']['version']=VERSION
        m['header']['name']=f'Grilling A1.16 • Cookery-linked immersion {name}'
        m['header']['description']='沉浸動效驗收；需要 Kaleidoscope Cookery 1.0.6。非完整生存玩法。'
        for mod in m.get('modules',[]):mod['version']=VERSION
    ownrp=r['header']['uuid']
    server=[d for d in b.get('dependencies',[]) if 'module_name' in d]
    b['dependencies']=[{'uuid':ownrp,'version':VERSION},{'uuid':COOKERY_BP,'version':COOKERY_VER}]+server
    r['dependencies']=[{'uuid':COOKERY_RP,'version':COOKERY_VER}]
    write(bp,b);write(rp,r)
    cfg=json.loads((LAB/'config.json').read_text());cfg['name']='Grilling A1.16 Cookery-linked Immersion Lab';cfg['compiler']['plugins'][0][1]['packName']='KG_Immersion_Lab_A116';write(LAB/'config.json',cfg)

def build():
    guard=json.loads((ROOT/'.repo-target.json').read_text())
    if guard['repository']!='casama233/kaleidoscope-grilling-unofficial' or guard['repository_id']!=1377218440:raise RuntimeError('Wrong repository')
    curves=json.loads((LAB/'motion/source_curves.json').read_text())
    if curves['source_commit']!='9a1acdab27698457bec16c9362678e574895a28c' or list(curves['profiles'])!=PROFILE_ORDER:raise RuntimeError('Unexpected motion source')
    patch_manifests()
    write(LAB/'resource_pack/models/entity/hand_props.geo.json',build_geometry())
    write(LAB/'resource_pack/render_controllers/hand_props.render_controllers.json',{'format_version':'1.8.0','render_controllers':{'controller.render.kg_imm.hand_prop':{'geometry':'Geometry.default','materials':[{'*':'Material.default'}],'textures':['Texture.default']}}})
    attach_anims={}
    for s in range(5):
        attach_anims[f'animation.kg_imm.attach.stage{s}']={'loop':True,'bones':{f'bite{i}':{'scale':1 if i==s else 0} for i in range(5)}}
    write(LAB/'resource_pack/animations/hand_props.animation.json',{'format_version':'1.8.0','animations':attach_anims})
    items=LAB/'behavior_pack/items';atts=LAB/'resource_pack/attachables';items.mkdir(exist_ok=True);atts.mkdir(exist_ok=True)
    profile_ids={}
    for p in PROFILE_ORDER:
        ident=f'kg_imm:eat_{p.lower()}';profile_ids[ident]=p
        write(items/(ident.split(':')[1]+'.json'),item(ident,f'item.{ident}.name','kg_imm_profile',True))
        write(atts/(ident.split(':')[1]+'.attachable.json'),attach(ident,'geometry.kg_imm.hand_skewer',0))
    for s in range(5):
        ident=f'kg_imm:visual_{s}'
        write(items/f'visual_{s}.json',item(ident,f'item.{ident}.name','kg_imm_profile',False))
        write(atts/f'visual_{s}.attachable.json',attach(ident,'geometry.kg_imm.hand_skewer',s))
    for ident,geo,icon in [('kg_imm:oil_brush','geometry.kg_imm.hand_brush','kg_imm_brush'),('kg_imm:seasoning_bottle','geometry.kg_imm.hand_seasoning','kg_imm_season')]:
        write(items/(ident.split(':')[1]+'.json'),item(ident,f'item.{ident}.name',icon,True))
        write(atts/(ident.split(':')[1]+'.attachable.json'),attach(ident,geo,None))
    ident='kg_imm:bite_piece'
    write(items/'bite_piece.json',item(ident,'item.kg_imm:bite_piece.name','kg_imm_profile',False))
    write(atts/'bite_piece.attachable.json',attach(ident,'geometry.kg_imm.bite_piece',None))
    shutil.copyfile(LAB/'resource_pack/pack_icon.png',LAB/'resource_pack/textures/kg_imm/lab_item.png')
    write(LAB/'resource_pack/textures/item_texture.json',{'resource_pack_name':'kg_imm','texture_name':'atlas.items','texture_data':{
        'kg_imm_profile':{'textures':'textures/kg_imm/lab_item'},
        'kg_imm_brush':{'textures':'textures/kg_imm/lab_item'},
        'kg_imm_season':{'textures':'textures/kg_imm/lab_item'}}})
    anims={};tool_meta={}
    for p in RESOLVED:
        for side,label in ((1,'main'),(-1,'off')):
            anims[f'animation.kg_imm.player.eat_{p.lower()}.{label}']=make_eat_animation(curves,p,side)
    for kind in ('brush','season'):
        for side,label in ((1,'main'),(-1,'off')):
            a,meta=make_tool(kind,side);anims[f'animation.kg_imm.player.{kind}.{label}']=a;tool_meta[kind]=meta
    for side,label in ((1,'main'),(-1,'off')):
        anims[f'animation.kg_imm.player.reach.{label}']=make_reach(curves,side)
    if len(anims)!=16:raise RuntimeError(f'Expected 16 player animations, got {len(anims)}')
    write(LAB/'resource_pack/animations/player_binding.animation.json',{'format_version':'1.8.0','animations':anims})
    rules={p:{'durationTicks':curves['profiles'][p]['duration_ticks'],'bites':curves['profiles'][p]['bite_seconds']} for p in PROFILE_ORDER}
    js='export const PROFILE_RULES=Object.freeze('+json.dumps(rules,separators=(',',':'))+');\n'
    js+='export const SELECTORS=Object.freeze('+json.dumps(profile_ids,separators=(',',':'))+');\n'
    js+="export function resolveProfile(profile,r=Math.random()){return profile==='THREE_RANDOM'?(r<.5?'THREE':'THREE_ALT'):profile;}\n"
    js+="export function soundFor(profile){return ({ONE:'one_skewer_eat',TWO:'two_skewer_eat',THREE:'three_skewer_eat',THREE_ALT:'three_skewer_eat',FOUR:'four_skewer_eat'})[profile];}\n"
    js+="export function stageAt(profile,seconds){let n=0;for(const t of PROFILE_RULES[profile].bites)if(seconds>=t)n++;return Math.min(4,n);}\n"
    write(LAB/'behavior_pack/scripts/profile_rules.js',js)
    source_dir=Path(__file__).parent
    for name in ('flow.js','player_binding.js','main.js'):
        shutil.copyfile(source_dir/name,LAB/'behavior_pack/scripts'/name)
    # The old fixture-local tools are hidden: A1.16 renders brush and bottle through the player's item bones.
    scene_anim=LAB/'resource_pack/animations/rehearsal.animation.json'
    scene=json.loads(scene_anim.read_text())
    sb=scene['animations']['animation.kg_imm.rehearsal']['bones']
    sb['brush_tool']={'scale':0}
    sb['season_tool']={'scale':0}
    write(scene_anim,scene)
    entity_path=LAB/'behavior_pack/entities/rehearsal.json'
    entity=json.loads(entity_path.read_text())
    interactions=entity['minecraft:entity']['components']['minecraft:interact']['interactions']
    for interaction in interactions: interaction['swing']=False
    write(entity_path,entity)
    report={
        'version':'A1.16.0',
        'cookery_dependency':{'behavior_pack_uuid':COOKERY_BP,'resource_pack_uuid':COOKERY_RP,'version':COOKERY_VER},
        'profiles':rules,'player_animation_count':len(anims),'resolved_player_profiles':RESOLVED,
        'three_random_resolution':'server chooses THREE or THREE_ALT once per interaction; the chosen branch drives both pose and bite stages',
        'hand_variants':['main/rightItem','off/leftItem'],
        'first_person_baseline':{'source':'Mojang/bedrock-samples','commit':MOJANG_PLAYER_REF,'rightarm_position':[13.5,-10,12],'rightarm_rotation':[95,-45,115],'leftarm':'mirrored calibration; real left-handed client test pending'},
        'attachable_binding':'q.item_slot_to_bone_name(context.item_slot)',
        'tool_transitions':tool_meta,
        'eating_pickup_stow':'uses the original source curve endpoints; no extra seconds inserted into the six eating rules',
        'helper_piece':'ONE and THREE drive the authored helper arm/item; the visual bite piece is installed only if the opposite hand is empty',
        'contact_calibration':{'horizontal_distance':[0.72,1.32],'view_dot_min':0.90,'vertical_difference_max':0.75,'note':'narrows player pose so the authored camera-space brush/bottle trajectories pass through the grill working area; engine pixel/contact acceptance pending'},
        'minecraft_tested':False,'bridge_ui_tested':False,'native_player_skin_verified':False,'left_handed_player_setting_verified':False,
        'scope':'Cookery-linked player bone/camera-space animation lab; not survival inventory/nutrition or final processing logic'
    }
    write(REPORT/'binding-plan.json',report)
    return report

if __name__=='__main__':
    print(json.dumps(build(),ensure_ascii=False,indent=2))
