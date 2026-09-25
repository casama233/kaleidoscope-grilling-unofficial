"""One-shot explicit, source-pinned PR conflict resolution. Not a release/build entrypoint."""
from pathlib import Path
import subprocess,json,hashlib,zipfile,io,shutil,re
R=Path(__file__).resolve().parents[2];P=R/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
BASE='refs/audit/main';PR='refs/audit/pr69';CAT='refs/audit/pr74';PLACED='refs/audit/placed'
def git(*args):return subprocess.check_output(['git',*args],cwd=R)
def data(ref,path):return git('show',ref+':'+path)
def put(path,b):
 p=R/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b if isinstance(b,bytes) else b.encode())
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def paths(ref):return git('ls-tree','-r','--name-only',ref).decode().splitlines()
def changes(ref):
 base=git('merge-base',BASE,ref).decode().strip()
 return git('diff','--name-only',base,ref).decode().splitlines()
def take(ref,path):put(path,data(ref,path))
def edit(path,old,new,count=1):
 p=R/path;t=p.read_text(encoding='utf-8-sig');assert t.count(old)==count,(path,old,t.count(old));p.write_text(t.replace(old,new),encoding='utf-8')
resolutions={}
# The early branches' data is preserved and traceable, but no obsolete generator is reactivated.
for name in ('pr1','pr5','pr6'):
 ref='refs/audit/'+name;rows=[]
 for path in changes(ref):
  try:b=data(ref,path)
  except subprocess.CalledProcessError:continue
  put('history/integrated-pr/'+name+'/'+path,b)
  rows.append({'path':path,'git_blob':git('rev-parse',ref+':'+path).decode().strip()})
 resolutions[name]={'archive':name,'head':git('rev-parse',ref).decode().strip(),'resolution':'historical source preserved; current evolved implementation retained, no obsolete gameplay rollback','files':rows}
# Apply already reviewed catalog (later refreshed with current PR74 if it advances).
for path in changes(CAT):
 if path.startswith('.github/'):continue
 take(CAT,path)
# PR69 files unique to guide and tooling, plus revised current guide integration data.
prpaths=paths(PR)
for path in prpaths:
 if path.startswith(('history/standalone-guide-a3/','projects/grilling/guide/','development/guide/')) or path in ['tools/check_grilling_guide.py','tools/build_grilling_guide.py','tools/build_grilling_guide_release.py','tools/build_grilling_release.py','tools/check_grilling_release.py','tools/audit_grilling_render.py','tools/apply_skewer_display_parity.py']:
  take(PR,path)
for path in changes(PR):
 if path.startswith('projects/grilling/gameplay_core/behavior_pack/scripts/guide/') or path.startswith('projects/grilling/gameplay_core/resource_pack/textures/ui/'):
  take(PR,path)
 elif path.startswith('docs/STATUS-') or path.startswith('.github/workflows/') or path.startswith('projects/grilling/gameplay_core/reports/'):
  try:put('history/integrated-pr/pr69/'+path,data(PR,path))
  except subprocess.CalledProcessError:pass
# The old standalone guide is intentionally not part of the active product.
for folder in ('behavior_pack','resource_pack'):
 f=R/'projects/grilling/integration/cookery106'/folder
 if f.exists():
  archive=R/'history/integrated-pr/main-standalone-guide'/folder
  archive.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(f,archive,dirs_exist_ok=True);shutil.rmtree(f)
for f in (R/'.github/workflows').glob('*guide*.yml'):
 put('history/integrated-pr/main-standalone-guide/'+f.name,f.read_bytes());f.unlink()
# Merge translated keys, reject conflicts rather than overwriting gameplay text.
for loc in ('en_US','zh_CN','zh_TW'):
 p=RP/f'texts/{loc}.lang';text=p.read_text(encoding='utf-8-sig');keys={s.partition('=')[0]:s.partition('=')[2] for s in text.splitlines() if '=' in s}
 additions=[]
 for line in data(PR,p.relative_to(R).as_posix()).decode('utf-8-sig').splitlines():
  if '=' not in line:continue
  key,_,value=line.partition('=')
  if key not in keys:additions.append(line);keys[key]=value
  elif keys[key]!=value and key.startswith(('guide.','kg_a1.','kg_grilling.')):raise AssertionError(('guide translation conflict',key))
 p.write_text(text.rstrip()+'\n'+'\n'.join(additions)+'\n',encoding='utf-8')
# Non-overlapping runtime ownership and dirty-state work from PR69.
runtime=BP/'scripts';base69=git('merge-base',BASE,PR).decode().strip()
for name in ('a23_oil_world.js','a25_plate_recipe_runtime.js','a26_oil_machine_runtime.js','a271_sweet_potato_runtime.js','a2722_cold_houttuynia_runtime.js','a2737_offhand_oil_fill_runtime.js','a2746_advanced_rack_runtime.js'):
 path=(runtime/name).relative_to(R).as_posix();assert data(BASE,path)==data(base69,path),name
 take(PR,path)
 text=(runtime/name).read_text()
 # Reuse current common intent adapter instead of introducing a second implementation.
 for line in text.splitlines():
  if "from './interaction_intent.js'" in line:
   names=line.partition('{')[2].partition('}')[0].split(',')
   replace=[]
   if 'interactionStackSignature' in names:
    names.remove('interactionStackSignature')
    replace.append("import {stackIntentSignature as interactionStackSignature} from './a2762_interaction_intent_core.js';")
   if names:replace.append("import {"+','.join(names)+"} from './a2762_interaction_intent_adapter.js';")
   text=text.replace(line,'\n'.join(replace))
 (runtime/name).write_text(text,encoding='utf-8')
# Retain A2769 rollback/state variants, but capture cuisine from the actual event hand.
f=runtime/'a2750_cookery_cuisine_runtime.js';s=f.read_text()
s=s.replace('setMainHand,isCreative}', 'setMainHand,getHand,isCreative}')
old="  const kind=stationKind(event.block?.typeId);if(!kind||!isFirst(event))return;\n  const player=event.player,main=getMainHand(player);\n  if(isSpecialSeasoningId(main?.typeId)){\n   event.cancel=true;const dimension=event.block.dimension,location={...event.block.location},intent=captureInteractionIntent(player,main);"
new="  const kind=stationKind(event.block?.typeId);if(!kind)return;\n  const player=event.player,intent=captureInteractionIntent(player,event.itemStack),hand=intent.hand,used=getHand(player,hand);\n  if(hand==='main'&&isSpecialSeasoningId(used?.typeId)){\n   event.cancel=true;if(!isFirst(event))return;const dimension=event.block.dimension,location={...event.block.location};"
assert old in s;s=s.replace(old,new)
s=s.replace("  const dimension=event.block.dimension,location={...event.block.location};\n  const stateBefore", "  if(!isFirst(event))return;\n  const dimension=event.block.dimension,location={...event.block.location};\n  const stateBefore")
s=s.replace("typedHeldOil(main):''","typedHeldOil(used):''")
f.write_text(s,encoding='utf-8')
# Main: keep canonical dispatch, add only reviewed dirty-state comparison.
f=runtime/'main.js';s=f.read_text();other=data(PR,f.relative_to(R).as_posix()).decode()
start=other.index('function writeTickState(');end=other.index('\nfunction ',start+1)
function=other[start:end]+'\n'
assert 'writeTickState(' not in s
anchor='function oilInfo('
if anchor not in s:
 anchor=next(line for line in s.splitlines() if line.startswith('function ') and 'writeState' not in line)
idx=s.index(anchor);s=s[:idx]+function+s[idx:]
s=s.replace('world.beforeEvents.playerInteractWithBlock.subscribe(e=>{','world.beforeEvents.playerInteractWithBlock.subscribe(e=>{\n if(e.cancel)return;')
# Both branches leave this loop unchanged except PR69's reviewed state-write coalescing.
oldline=next(x for x in s.splitlines() if 'let state=readState(block),before=state.phase;' in x)
newline=next(x for x in other.splitlines() if 'writeTickState(block,beforeState,state)' in x)
s=s.replace(oldline,newline)
s="import './guide/main.js';\n"+s
f.write_text(s,encoding='utf-8')
# World geometry and host-owned hand props from PR69, never its older block material maps.
for path in changes(PR):
 if not path.startswith('projects/grilling/gameplay_core/resource_pack/'):continue
 rel=path.split('resource_pack/',1)[1]
 if rel.startswith(('models/blocks/big_vat_','models/entity/a22_bites/')) or rel in ('models/entity/a2762_big_vat_hand.geo.json','models/entity/a2763_advanced_rack_hand.geo.json'):
  take(PR,path)
 if rel.startswith(('animations/a2762_big_vat','animations/a2763_advanced_rack','animations/a2763_seasoning_bottle_display','animations/a2764_skewer_java_display','render_controllers/a2762_big_vat','render_controllers/a2763_advanced_rack')):
  take(PR,path)
 if rel in ('attachables/big_vat.attachable.json','attachables/advanced_rack.attachable.json') or (rel.startswith('attachables/') and rel.endswith('_skewer.attachable.json')):
  take(PR,path)
# Extend PR69 hand-space DISPLAY child to all current seasoning variants; no double root transform.
prbottle=loadjson=None
example=json.loads(data(PR,'projects/grilling/gameplay_core/resource_pack/attachables/special_seasoning.attachable.json'))['minecraft:attachable']['description']
for p in [RP/'models/entity/a2733_seasoning_bottle_hand.geo.json',*sorted((RP/'models/entity/a2766_special_seasoning').glob('*.geo.json'))]:
 d=load(p)
 for g in d['minecraft:geometry']:
  bones=g['bones'];assert not any(b['name']=='display' for b in bones)
  for b in bones[1:]:
   if b.get('parent')=='root':b['parent']='display'
  g['bones']=[bones[0],{'name':'display','parent':'root','pivot':[0,0,0]},*bones[1:]]
 save(p,d)
for p in (RP/'attachables').glob('*.json'):
 if p.stem.startswith(('empty_seasoning_bottle.','pending_seasoning.','special_seasoning')):
  d=load(p);v=d['minecraft:attachable']['description'];v['animations']=example['animations'];v.setdefault('scripts',{})['animate']=example['scripts']['animate'];save(p,d)
# Original placement source now includes display bones, but the filled cube coordinates remain unchanged.
for path in changes(PLACED):
 if path.startswith('.github/') or path.endswith('verify_a2770.py') or path.startswith('docs/STATUS-'):continue
 take(PLACED,path)
# Fix the exact missing bracket that blocked the last attempt.
f=runtime/'a2770_placed_visual_core.js';s=f.read_text();assert s.count('[-4.25,-3.25]];')==1;f.write_text(s.replace('[-4.25,-3.25]];','[-4.25,-3.25]]];'))
# Dirty notifications do not write or duplicate authoritative container contents.
f=runtime/'a2743_seasoning_block_adapter.js';s=f.read_text();old=';return true}catch{return false}';assert s.count(old)==1
f.write_text("import {markPlacedVisualDirty} from './a2770_placed_visual_queue.js';\n"+s.replace(old,';markPlacedVisualDirty(block);return true}catch{return false}'))
f=runtime/'a2739_cookery_oil_pot_block_adapter.js';s=f.read_text();assert s.count('  return true;')==1
f.write_text("import {markPlacedVisualDirty} from './a2770_placed_visual_queue.js';\n"+s.replace('  return true;','  markPlacedVisualDirty(block);return true;').replace(' return ok;',' markPlacedVisualDirty(block);return ok;'))
f=runtime/'main.js';f.write_text("import './a2770_placed_visual_runtime.js';\n"+f.read_text())
# Guide validation maps private materialized seasoning IDs onto the canonical entry.
f=R/'tools/check_grilling_guide.py';s=f.read_text();needle="        require(iid in owner,'Item absent '+iid);covered+=1"
repl="        if re.fullmatch(NS+r'special_seasoning_r[1-8]_v[0-7]',iid):\n            require(item['description']['menu_category']['category']=='none' and NS+'special_seasoning' in owner,'Private seasoning entry leaked');continue\n"+needle
assert needle in s;s=s.replace(needle,repl);f.write_text(s)
# Consolidated version, preserving all UUIDs/dependencies/PBR.
for pack in (BP,RP):
 d=load(pack/'manifest.json');d['header']['name']='Kaleidoscope Grilling A2.8.0 Integrated Test '+('BP' if pack==BP else 'RP');d['header']['version']=[2,8,0]
 for m in d['modules']:m['version']=[2,8,0]
 for dep in d.get('dependencies',[]):
  if dep.get('uuid')=='bbbd2d60-52e5-53a6-8b9a-c09b0f516389':dep['version']=[2,8,0]
 save(pack/'manifest.json',d)
d=load(P/'config.json');d['name']='Kaleidoscope Grilling A2.8.0 Integrated Test';d['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_8_0_Integrated_Test';save(P/'config.json',d)
put('docs/integration/early-pr-resolutions.json',json.dumps(resolutions,ensure_ascii=False,indent=2)+'\n')
print('prepared base resolution')
D=R/'development/gameplay_core'
def patch(p,old,new):
 s=p.read_text();assert s.count(old)==1,(p,old,s.count(old));p.write_text(s.replace(old,new),encoding='utf-8')
# Preserve provenance-only A2764 rebakes while active A22 models use a display child.
patch(D/'a2764_rebake_skewer_hand_geometry.py','    for bone in geo["bones"]:', '''    # A2.8 uses Java display on a child bone; remove only that identity node
    # when rebuilding the retired A2764 hand-space provenance assets.
    display = [b for b in geo["bones"] if b.get("name") == "display"]
    if display:
        assert display == [{"name": "display", "parent": "root", "pivot": [0, 0, 0]}]
        geo["bones"] = [b for b in geo["bones"] if b.get("name") != "display"]
        for bone in geo["bones"]:
            if bone.get("parent") == "display": bone["parent"] = "root"
    for bone in geo["bones"]:''')
p=D/'verify_a2766.py';s=p.read_text().replace('def check_assets():','def check_assets(java_display=False):')
s=s.replace("   assert not desc.get('animations') and not desc.get('scripts',{}).get('animate')", "   if java_display:\n    assert len(desc.get('animations',{}))==4 and len(desc.get('scripts',{}).get('animate',[]))==4\n   else:assert not desc.get('animations') and not desc.get('scripts',{}).get('animate')")
s=s.replace("  assert not desc.get('animations') and not desc.get('scripts',{}).get('animate')", "  if java_display:\n   assert len(desc.get('animations',{}))==4 and len(desc.get('scripts',{}).get('animate',[]))==4\n  else:assert not desc.get('animations') and not desc.get('scripts',{}).get('animate')")
s=s.replace("  assert all(g.startswith('geometry.kg_a2764.') and g in models for g in desc['geometry'].values())", "  prefix='geometry.kg_a22.' if java_display else 'geometry.kg_a2764.'\n  assert all(g.startswith(prefix) and g in models for g in desc['geometry'].values())")
p.write_text(s)
p=D/'verify_visual_refs.py';s=p.read_text()
s=s.replace('        assert "animations" not in desc, f"{path}: A2733 hand-space geometry must not receive the retired A2726 -6Y animation again"\n        assert "scripts" not in desc, f"{path}: A2733 hand-space geometry must not double-apply a hold transform"', '''        if tuple(load(BP / "manifest.json")["header"]["version"]) >= (2,8,0):
            expected = load(RP / "animations/a2763_seasoning_bottle_display.animation.json")["animations"]
            assert set(desc["animations"].values()) == set(expected)
            assert all(set(anim["bones"]) == {"display"} for anim in expected.values())
        else:
            assert "animations" not in desc
            assert "scripts" not in desc''')
s=s.replace('        bone.get("name") == "root" or (','        bone.get("name") in {"root", "display"} or (')
p.write_text(s)
p=D/'verify_current.py';s=p.read_text();s=s.replace('    (2, 7, 70): "verify_a2770.py",','    (2, 7, 70): "verify_a2770.py",\n    (2, 8, 0): "verify_a280.py",')
s=s.replace('(BP / "scripts").glob("*.js")','(BP / "scripts").rglob("*.js")');p.write_text(s)
p=D/'a2770_placed_visual_assets.py';s=p.read_text();s=s.replace('def install():','def install():\n raise RuntimeError("Retired one-shot installer; A2.8 integration owns manifests and runtime wiring")\n');p.write_text(s)
p=P/'behavior_pack/scripts/a2770_placed_visual_runtime.js';s=p.read_text()
s=s.replace(" try{if(entry.entity.isValid)entry.entity.remove()}catch(error){warn(error)}\n owned.delete(entry.id);row.helpers.delete(slot);", " try{if(entry.entity.isValid)entry.entity.remove()}catch(error){warn(error);return false}\n owned.delete(entry.id);row.helpers.delete(slot);return true;")
s=s.replace("if(entry&&(!entry.entity.isValid||entry.type!==type)){dispose(row,slot);entry=undefined}", "if(entry&&(!entry.entity.isValid||entry.type!==type)){if(!dispose(row,slot))return;entry=undefined}")
s=s.replace("clear(row);tracked.delete(visualLocationKey(row.dimensionId,l));", "clear(row);if(!row.helpers.size)tracked.delete(visualLocationKey(row.dimensionId,l));");p.write_text(s)
# Apply latest PR74 shared Cookery grouping; do not restore the superseded own-group scheme.
ref='refs/audit/latest-pr74';base=git('merge-base','refs/audit/pr74',ref).decode().strip()
for path in git('diff','--name-only',base,ref).decode().splitlines():
 if path.startswith('projects/grilling/gameplay_core/behavior_pack/items/') or path.startswith('projects/grilling/gameplay_core/behavior_pack/blocks/') or path.startswith('projects/grilling/gameplay_core/behavior_pack/item_catalog/') or path.startswith('development/gameplay_core/a2771_') or path.startswith('development/gameplay_core/test_a2771_') or path.startswith('development/gameplay_core/fixtures/a2771') or path.endswith('verify_a2771.py') or path.startswith('projects/grilling/gameplay_core/reports/a2771') or path=='docs/STATUS-A2.7.71.md':
  put(path,git('show',ref+':'+path))
for p in RP.joinpath('texts').glob('*.lang'):
 b=p.read_bytes();p.write_bytes(b''.join(line for line in b.splitlines(keepends=True) if not line.split(b'=',1)[0].startswith(b'kaleidoscope_grilling:itemGroup.')))
p=D/'verify_current.py';s=p.read_text().replace('    (2, 7, 70): "verify_a2770.py",','    (2, 7, 70): "verify_a2770.py",\n    (2, 7, 71): "verify_a2771.py",');p.write_text(s)
# Restore the guide generator's ownership markers; do not duplicate unmarked guide keys.
for p in RP.joinpath('texts').glob('*.lang'):
 text=p.read_text(encoding='utf-8-sig')
 text='\n'.join(line for line in text.splitlines() if not line.partition('=')[0].startswith('guide.kg.'))+'\n'
 p.write_text(text,encoding='utf-8')
subprocess.run([__import__('sys').executable,str(R/'tools/build_grilling_guide.py')],cwd=R,check=True)
for name,target in [('build_grilling_release.py','package_current.py'),('build_grilling_guide_release.py','package_current.py'),('check_grilling_release.py','verify_current.py')]:
 p=R/'tools'/name
 put('history/integrated-pr/pr69/tools/'+name,data(PR,'tools/'+name))
 p.write_text('"""Compatibility entry: the guide is part of the canonical Grilling pack."""\nfrom pathlib import Path\nimport runpy\nif __name__ == "__main__":\n    runpy.run_path(str(Path(__file__).resolve().parents[1]/"development/gameplay_core/'+target+'"),run_name="__main__")\n')
# More detailed reviewed corrections are kept as ordinary text patches, not opaque payloads.
from integration_finish_a280 import finish
finish(R,P,D,RP,BASE,PR,git,data,put,paths,save)
