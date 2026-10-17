from pathlib import Path
import os,json,shutil,subprocess,time,hashlib
import argparse,sys
parser=argparse.ArgumentParser(description='Isolated native natural pepper world generation and normal-stop/restart probe; never production admission or simulated players.')
parser.add_argument('--bds-root',type=Path,required=True)
parser.add_argument('--family-candidate',type=Path,required=True)
parser.add_argument('--level-metadata',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--port',type=int,default=25740)
a=parser.parse_args()
if not 1024<=a.port<=65534:parser.error('port must be 1024..65534')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from baseline_gate import fingerprint
runtime_trees={side:fingerprint(ROOT/'projects/grilling/gameplay_core'/side)[0] for side in ['behavior_pack','resource_pack']}
BDS=a.bds_root.resolve()
GRILL=ROOT/'projects/grilling/gameplay_core'
BASE=a.family_candidate.resolve()
OUT=a.output.resolve()
if OUT.exists():raise SystemExit('Output exists; never replace a probe world')
OUT.mkdir()
for name in ['bedrock_server','definitions','behavior_packs','resource_packs']:(OUT/name).symlink_to(BDS/name,target_is_directory=(BDS/name).is_dir())
for name in ['config','minecraftpe','treatments']:shutil.copytree(BDS/name,OUT/name)
(OUT/'allowlist.json').write_text('[]\n')
(OUT/'server.properties').write_text(f'server-name=Isolated natural pepper world generation check\nlevel-name=Pepper Test\nserver-port={a.port}\nserver-portv6={a.port+1}\nonline-mode=false\nallow-list=false\nview-distance=4\ntick-distance=4\nmax-threads=2\nenable-lan-visibility=false\ncontent-log-file-enabled=true\ncontent-log-console-output-enabled=true\ntransport=nethernet\n')
world=OUT/'worlds/Pepper Test';shutil.copytree(BASE,world)
# Only own lab level metadata is copied; no old database or production world.
import nbtlib,io,struct
metadata=a.level_metadata.resolve()
f=nbtlib.File.parse(io.BytesIO(metadata.read_bytes()[8:]),byteorder='little');f['LevelName']=nbtlib.String('Pepper Test');f['experiments']=nbtlib.Compound({k:nbtlib.Byte(1) for k in ['upcoming_creator_features','experiments_ever_used','saved_with_toggled_experiments']});f['SpawnX']=nbtlib.Int(0);f['SpawnY']=nbtlib.Int(80);f['SpawnZ']=nbtlib.Int(0)
b=io.BytesIO();f.write(b,byteorder='little');body=b.getvalue();(world/'level.dat').write_bytes(struct.pack('<II',10,len(body))+body)
# Test-only source replacement; never represented as an admitted family receipt.
for side,label in [('behavior_pack','behavior'),('resource_pack','resource')]:
 m=json.loads((GRILL/side/'manifest.json').read_text());uid=m['header']['uuid'];dest=world/(label+'_packs')/uid
 shutil.move(dest,OUT/(side+'-previous-reference'));shutil.copytree(GRILL/side,dest)
 p=world/('world_'+label+'_packs.json');rows=json.loads(p.read_text())
 for row in rows:
  if row['pack_id']==uid:row['version']=m['header']['version']
 p.write_text(json.dumps(rows,indent=2)+'\n')
bp=world/'behavior_packs/c68005c5-23ff-54e8-a3ff-da6349ad43c2';main=bp/'scripts/main.js';canonical_sha=hashlib.sha256(main.read_bytes()).hexdigest()
shutil.copy2(Path(__file__).with_name('native_pepper_worldgen_probe.js'),bp/'scripts/pepper_native_probe.js')
with main.open('a') as out:out.write('\nimport {runPepperNativeProbe} from "./pepper_native_probe.js";\nrunPepperNativeProbe();\n')
reports=[]
for phase,marker in [('prepare','NATIVE_PEPPER_PREPARED '),('restart','NATIVE_PEPPER_RESTART_PASS ')]:
 log=OUT/(phase+'.log')
 with log.open('w') as out:
  proc=subprocess.Popen(['./bedrock_server'],cwd=OUT,env={**os.environ,'LD_LIBRARY_PATH':str(OUT)},stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT,text=True)
  try:
   for _ in range(300):
    time.sleep(1);s=log.read_text()
    if marker in s or 'NATIVE_PEPPER_FAIL' in s or proc.poll() is not None:break
   proc.communicate('stop\n',timeout=30)
  finally:
   if proc.poll() is None:proc.kill()
 text=log.read_text();matches=[x.split(marker,1)[1] for x in text.splitlines() if marker in x];errors=[x for x in text.splitlines() if ' ERROR]' in x or 'NATIVE_PEPPER_FAIL' in x]
 result={'phase':phase,'pass':bool(matches) and not errors,'errors':errors,'details':json.loads(matches[-1]) if matches else None};reports.append(result)
 (OUT/'report.json').write_text(json.dumps({'runtime_trees':runtime_trees,'family_receipt_sha256':hashlib.sha256((BASE/'family-receipt.json').read_bytes()).hexdigest(),'canonical_main_sha256':canonical_sha,'test_only_source_overlay':True,'simulated_players':False,'client':False,'production_ready':False,'runs':reports},indent=2)+'\n')
 print(json.dumps(result),flush=True)
 if not result['pass']:raise SystemExit(1)
