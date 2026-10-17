"""One-shot immutable private QA copy; runtime source and public locks unchanged.

No install, export transform, publication or live/world mutation is performed.
Only copied manifest identity fields are changed after canonical source checks.
"""
from pathlib import Path
import argparse,copy,hashlib,json,shutil,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1];RUNTIME=ROOT/'projects/grilling/gameplay_core';BASE='fa2446c4bbf2a4375dc657c2d1e41082e050a4bb';VERSION=[2,8,6709]
def sha(data):return hashlib.sha256(data).hexdigest()
def inventory(root):return {p.relative_to(root).as_posix():sha(p.read_bytes())for p in sorted(root.rglob('*'))if p.is_file()and not p.name.startswith('.')}
def tree_hash(rows):return sha(''.join(k+'\0'+v+'\n'for k,v in sorted(rows.items())).encode())
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--prior6705',type=Path,required=True);p.add_argument('--prior6708',type=Path,required=True);a=p.parse_args();out=a.output.resolve();evidence=a.evidence.resolve()
 assert not out.exists(),'6709 identity already exists; never overwrite'
 assert not git('status','--porcelain').strip(),'Source must be committed and clean'
 head=git('rev-parse','HEAD').decode().strip();assert git('merge-base',BASE,head).decode().strip()==BASE
 for log in ('focused-tests.log','generator-checks.log'):assert (evidence/log).is_file()
 assert 'FAILED'not in (evidence/'focused-tests.log').read_text() and 'Traceback'not in (evidence/'generator-checks.log').read_text()
 props=json.loads((RUNTIME/'behavior_pack/entities/player.json').read_text())['minecraft:entity']['description']['properties'];assert len(props)==32
 old_receipt=a.prior6705/'candidate-receipt.json';old=json.loads(old_receipt.read_text());old_archive=Path(old['mcaddon']['path']);assert sha(old_archive.read_bytes())==old['mcaddon']['sha256']
 for pack,rows in old['candidate_files'].items():assert inventory(a.prior6705/pack)==rows
 prior={'path':str(a.prior6705),'receipt_sha256':sha(old_receipt.read_bytes()),'mcaddon_sha256':sha(old_archive.read_bytes())}
 receipt6708=a.prior6708/'candidate-receipt.json';prior_data=json.loads(receipt6708.read_text());archive6708=Path(prior_data['mcaddon']['path']);assert sha(archive6708.read_bytes())==prior_data['mcaddon']['sha256']
 for pack,rows in prior_data['candidate_files'].items():assert inventory(a.prior6708/pack)==rows
 prior6708={'path':str(a.prior6708),'receipt_sha256':sha(receipt6708.read_bytes()),'mcaddon_sha256':sha(archive6708.read_bytes())}
 # Packaging must not change the public source identity/lock.
 guards={p:sha((ROOT/p).read_bytes())for p in ('baseline.json','release-history.json','projects/grilling/gameplay_core/behavior_pack/manifest.json','projects/grilling/gameplay_core/resource_pack/manifest.json')}
 rp_uuid=json.loads((RUNTIME/'resource_pack/manifest.json').read_text())['header']['uuid'];source_files={};candidate_files={};identity={}
 out.mkdir(parents=True)
 for pack in ('behavior_pack','resource_pack'):
  src=RUNTIME/pack;dst=out/pack;source_files[pack]=inventory(src);shutil.copytree(src,dst)
  path=dst/'manifest.json';doc=json.loads(path.read_text());original=copy.deepcopy(doc)
  doc['header']['version']=VERSION;doc['header']['name']+=' [PRIVATE THREADED QA 6709]';doc['header']['description']+=' | Source-backed threaded secret volumes/palettes; unaccepted private QA'
  for module in doc['modules']:module['version']=VERSION
  for dependency in doc.get('dependencies',[]):
   if dependency.get('uuid')==rp_uuid:dependency['version']=VERSION
  path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
  check=copy.deepcopy(doc);check['header']=original['header']
  for module,prior_module in zip(check['modules'],original['modules']):module['version']=prior_module['version']
  check['dependencies']=original.get('dependencies',[]);assert check==original
  candidate_files[pack]=inventory(dst);assert set(candidate_files[pack])==set(source_files[pack]);assert [f for f in source_files[pack]if source_files[pack][f]!=candidate_files[pack][f]]==['manifest.json']
  identity[pack]={'source_sha256':source_files[pack]['manifest.json'],'candidate_sha256':candidate_files[pack]['manifest.json']}
 archive=out/'Kaleidoscope_Grilling_Private_Threaded_6709.mcaddon'
 with zipfile.ZipFile(archive,'w')as z:
  for pack,rows in candidate_files.items():
   for relative in sorted(rows,key=lambda x:Path(x).parts):
    info=zipfile.ZipInfo(pack+'/'+relative,(2020,1,1,0,0,0));info.create_system=3;info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
    z.writestr(info,(out/pack/relative).read_bytes(),compresslevel=6)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None;assert len(z.namelist())==sum(map(len,candidate_files.values()))
  for pack,rows in candidate_files.items():
   for relative,digest in rows.items():assert sha(z.read(pack+'/'+relative))==digest
 textures=list((out/'resource_pack/textures/secret_food_palette').glob('*.png'));assert len(textures)==1491
 changed=git('diff','--name-only',BASE,head).decode().splitlines()
 receipt={'kind':'PRIVATE_UNACCEPTED_CANDIDATE_NOT_FOR_RELEASE','private_parent':BASE,'candidate_commit':head,'candidate_source_tree':git('show','-s','--format=%T',head).decode().strip(),'candidate_branch':git('branch','--show-current').decode().strip(),'source_version':[2,8,67],'version':VERSION,
  'frozen':True,'native_acceptance':False,'client':False,'production_ready':False,'published':False,'live_changed':False,
  'source_pin':'9a1acdab27698457bec16c9362678e574895a28c','scope':'All27 exact mixed complete Java states split into81 slot meshes for held/grill; all12 partial states split into21 held slot meshes; actual0/1/2 unfinished metadata displays; existing full-fidelity palette and hand/helper motion preserved',
  'preserved':'32 player properties, owner occupancy/masks, authored held/eating/socket/helper motion, raw-last-item helper, item snapshots/creator/cooked cache and transaction settlement',
  'remaining_gaps':['Plate composition and dropped/inventory native projection','113 Cookery palettes sample reviewed Bedrock sprites; Java particle parity unverified','3 pinned Grilling particle references unresolved; provisional provider fallback palettes','Dynamic ingredient model/tint and resource overrides','Native rig/lighting/rendering and full-family memory acceptance','Existing completion flash is not claimed repaired'],
  'client_property_count':32,'new_player_properties':[],'source_changed_paths':changed,'source_runtime_changed_paths':[p for p in changed if p.startswith('projects/grilling/gameplay_core/')],
  'copy_identity_changed_paths':{p:['manifest.json']for p in candidate_files},'identity_mutations':identity,'source_files':source_files,'candidate_files':candidate_files,'file_counts':{p:len(v)for p,v in candidate_files.items()},
  'source_tree_sha256':{p:tree_hash(v)for p,v in source_files.items()},'tree_sha256':{p:tree_hash(v)for p,v in candidate_files.items()},
  'tree_sha256_algorithm':'sha256 of sorted UTF-8 relative-path + NUL + file-sha256 + LF','mcaddon':{'path':str(archive),'sha256':sha(archive.read_bytes()),'runtime_files':sum(map(len,candidate_files.values()))},
  'texture_budget':{'food_texture_count':1491,'width':256,'height':96,'rgba_decoded_bytes':146571264,'food_png_bytes':sum(p.stat().st_size for p in textures),'lossy_downsampling':False,'before_mipmaps':True},
  'tests':{'focused_cases':77,'palette_java_differential_cases':31304,'focused_log_sha256':sha((evidence/'focused-tests.log').read_bytes()),'generator_log_sha256':sha((evidence/'generator-checks.log').read_bytes()),'full_suite':'not run','full_family_BDS_saved_world':'not run','native':'root-owned pending'},
  'prior_6705_reverified_immutable':prior,'prior_6708_reverified_immutable':prior6708,'packaging_policy':'One-shot copied identity only; no runtime transforms, no public lock changes; files read-only after hash readback','excluded_inputs':'No source JAR, original Cookery pack, worlds, screenshots, private logs, credentials or third-party private scripts in runtime copy'}
 receipt_path=out/'candidate-receipt.json';receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');receipt_sha=sha(receipt_path.read_bytes());(out/'SHA256SUMS.txt').write_text(sha(archive.read_bytes())+'  '+archive.name+'\n'+receipt_sha+'  '+receipt_path.name+'\n')
 for pack,rows in candidate_files.items():assert inventory(out/pack)==rows
 for path,digest in guards.items():assert sha((ROOT/path).read_bytes())==digest
 assert sha(old_receipt.read_bytes())==prior['receipt_sha256'];assert sha(receipt6708.read_bytes())==prior6708['receipt_sha256'];assert not git('status','--porcelain').strip()
 summary={k:receipt[k]for k in ('kind','candidate_commit','version','file_counts','mcaddon','texture_budget')};summary['receipt']={'path':str(receipt_path),'sha256':receipt_sha};(evidence/'candidate-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 for path in out.rglob('*'):path.chmod(0o555 if path.is_dir()else 0o444)
 out.chmod(0o555);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
