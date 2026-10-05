"""One-shot 6711 frozen copy of canonical idle calibration; no install/publish.

Source BP is exact 6709. Source RP changes exactly three owned attachables plus
one independently generated idle-animation file. Previous copies are verified.
"""
from pathlib import Path
import argparse,copy,hashlib,json,shutil,subprocess,zipfile
from secret_idle_calibration import OWNED,TARGET,ROOT,RP
RUNTIME=ROOT/'projects/grilling/gameplay_core';BASE='f64bcbd0a1f9e350c17aa7db1b05aa5d5430c236';VERSION=[2,8,6711]
def sha(data):return hashlib.sha256(data).hexdigest()
def inventory(root):return {p.relative_to(root).as_posix():sha(p.read_bytes())for p in sorted(root.rglob('*'))if p.is_file()and not p.name.startswith('.')}
def tree_hash(rows):return sha(''.join(k+'\0'+v+'\n'for k,v in sorted(rows.items())).encode())
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def verified_copy(path):
 receipt=path/'candidate-receipt.json';data=json.loads(receipt.read_text());archive=Path(data['mcaddon']['path']);assert sha(archive.read_bytes())==data['mcaddon']['sha256']
 for pack,rows in data['candidate_files'].items():assert inventory(path/pack)==rows
 return data,{'path':str(path),'receipt_sha256':sha(receipt.read_bytes()),'mcaddon_sha256':sha(archive.read_bytes())}
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--base6709',type=Path,required=True);p.add_argument('--diag6710',type=Path,required=True);p.add_argument('--prior6708',type=Path,required=True);a=p.parse_args();out=a.output.resolve();evidence=a.evidence.resolve()
 assert not out.exists(),'6711 identity exists; never overwrite';assert not git('status','--porcelain').strip(),'Commit clean source before packaging'
 head=git('rev-parse','HEAD').decode().strip();assert git('merge-base',BASE,head).decode().strip()==BASE
 log=(evidence/'focused-tests.log').read_bytes();assert b'FAILED'not in log and b'Traceback'not in log
 old,prior6709=verified_copy(a.base6709);assert old['candidate_commit']==BASE and old['version']==[2,8,6709]
 diag,prior6710=verified_copy(a.diag6710);assert diag['candidate_commit']=='fc83dee2b6918a78beccb13bd342244e3db42fe0'
 _,prior6708=verified_copy(a.prior6708)
 source_files={pack:inventory(RUNTIME/pack)for pack in ('behavior_pack','resource_pack')};assert source_files['behavior_pack']==old['source_files']['behavior_pack']
 added=set(source_files['resource_pack'])-set(old['source_files']['resource_pack']);assert added=={TARGET.relative_to(RP).as_posix()}
 assert not(set(old['source_files']['resource_pack'])-set(source_files['resource_pack']))
 changed=sorted(k for k in old['source_files']['resource_pack']if source_files['resource_pack'][k]!=old['source_files']['resource_pack'][k]);expected=sorted('attachables/'+id.split(':')[1]+'.attachable.json'for id in OWNED);assert changed==expected
 guards={p:sha((ROOT/p).read_bytes())for p in ('baseline.json','release-history.json','projects/grilling/gameplay_core/behavior_pack/manifest.json','projects/grilling/gameplay_core/resource_pack/manifest.json')}
 rp_uuid=json.loads((RP/'manifest.json').read_text())['header']['uuid'];candidate_files={};identity={};out.mkdir(parents=True)
 for pack in ('behavior_pack','resource_pack'):
  dst=out/pack;shutil.copytree(RUNTIME/pack,dst);path=dst/'manifest.json';doc=json.loads(path.read_text());original=copy.deepcopy(doc)
  doc['header']['version']=VERSION;doc['header']['name']+=' [PRIVATE THREADED IDLE QA 6711]';doc['header']['description']+=' | Empirical 1.26.52.3 threaded idle calibration; mouth/transition acceptance pending'
  for module in doc['modules']:module['version']=VERSION
  for dep in doc.get('dependencies',[]):
   if dep.get('uuid')==rp_uuid:dep['version']=VERSION
  path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n');check=copy.deepcopy(doc);check['header']=original['header']
  for module,old_module in zip(check['modules'],original['modules']):module['version']=old_module['version']
  check['dependencies']=original.get('dependencies',[]);assert check==original
  candidate_files[pack]=inventory(dst);assert set(candidate_files[pack])==set(source_files[pack]);assert [k for k in source_files[pack]if source_files[pack][k]!=candidate_files[pack][k]]==['manifest.json']
  identity[pack]={'source_sha256':source_files[pack]['manifest.json'],'candidate_sha256':candidate_files[pack]['manifest.json']}
 archive=out/'Kaleidoscope_Grilling_Private_Threaded_Idle_6711.mcaddon'
 with zipfile.ZipFile(archive,'w')as z:
  for pack,rows in candidate_files.items():
   for relative in sorted(rows,key=lambda x:Path(x).parts):
    info=zipfile.ZipInfo(pack+'/'+relative,(2020,1,1,0,0,0));info.create_system=3;info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,(out/pack/relative).read_bytes(),compresslevel=6)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for pack,rows in candidate_files.items():
   for relative,digest in rows.items():assert sha(z.read(pack+'/'+relative))==digest
 fixture=ROOT/'development/gameplay_core/fixtures/secret-idle-fp-calibration-1.26.52.3.json';proof=json.loads(fixture.read_text())
 receipt={'kind':'PRIVATE_UNACCEPTED_TARGETED_IDLE_CALIBRATION_NOT_FOR_RELEASE','private_parent':BASE,'candidate_commit':head,'candidate_source_tree':git('show','-s','--format=%T',head).decode().strip(),'candidate_branch':git('branch','--show-current').decode().strip(),'source_version':[2,8,67],'version':VERSION,'frozen':True,'native_acceptance':False,'client':False,'production_ready':False,'published':False,'live_changed':False,
  'scope':'Empirical 1.26.52.3 idle-only FP calibration for secret/ALT/unfinished; +3.41 world Y inverse-socket positions exactly reproduce 6710; three attachables and one owned animation file',
  'proof_boundary':'Native 6710 A/B showed all 3 pieces on old cooked secret in both idle hands at FOV 60; universal engine-eye value and6711 active mouth transition remain unproven',
  'calibration_fixture_sha256':sha(fixture.read_bytes()),'calibration_proof':proof,'source_runtime_changed_paths':git('diff','--name-only',BASE,head,'--','projects/grilling/gameplay_core').decode().splitlines(),
  'preserved':'All source BP files; existing shared FP/TP and active eating/helper animation bytes; geometry, textures, palette arrays, property counts, metadata, complete/partial source-state selections and owner masks',
  'remaining_gaps':['6711 native 0/1/2/3 views and idle-to-active mouth/transition acceptance','Other FOV/aspect/client versions/rigs/postures','Plate/dropped/native inventory projection','Cookery Java particle fidelity and 3 unresolved Grilling particles','Existing completion flash and full-family memory acceptance'],
  'client_property_count':32,'new_player_properties':[],'copy_identity_changed_paths':{pack:['manifest.json']for pack in candidate_files},'identity_mutations':identity,'source_files':source_files,'candidate_files':candidate_files,'file_counts':{pack:len(rows)for pack,rows in candidate_files.items()},'source_tree_sha256':{pack:tree_hash(rows)for pack,rows in source_files.items()},'tree_sha256':{pack:tree_hash(rows)for pack,rows in candidate_files.items()},'tree_sha256_algorithm':'sha256 of sorted UTF-8 relative path + NUL + file SHA256 + LF','mcaddon':{'path':str(archive),'sha256':sha(archive.read_bytes()),'runtime_files':sum(map(len,candidate_files.values()))},
  'tests':{'new_idle_alias_cases':4,'exact_generator_checks':['build_secret_held.py','build_eating_motion.py','build_native_eating_variants.py'],'log_sha256':sha(log),'full_suite':'not rerun','native':'root-owned pending'},'texture_budget':old['texture_budget'],'prior_immutable_copies':[prior6708,prior6709,prior6710],
  'packaging_policy':'One-shot copied manifest identity only; no runtime transform, public lock, install, world, UI, publish or live changes; files read-only after readback','excluded_inputs':'No source JAR, original Cookery pack, worlds, screenshots, private logs or credentials copied to runtime'}
 path=out/'candidate-receipt.json';path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');receipt_sha=sha(path.read_bytes());(out/'SHA256SUMS.txt').write_text(sha(archive.read_bytes())+'  '+archive.name+'\n'+receipt_sha+'  '+path.name+'\n')
 for pack,rows in candidate_files.items():assert inventory(out/pack)==rows
 for path,digest in guards.items():assert sha((ROOT/path).read_bytes())==digest
 for prior in (prior6708,prior6709,prior6710):assert sha((Path(prior['path'])/'candidate-receipt.json').read_bytes())==prior['receipt_sha256']
 assert not git('status','--porcelain').strip()
 summary={k:receipt[k]for k in ('kind','candidate_commit','version','file_counts','mcaddon')};summary['receipt']={'path':str(out/'candidate-receipt.json'),'sha256':receipt_sha};(evidence/'candidate-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 for path in out.rglob('*'):path.chmod(0o555 if path.is_dir()else 0o444)
 out.chmod(0o555);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
