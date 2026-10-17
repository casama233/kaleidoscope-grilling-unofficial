"""Isolated full/minimal native script profiling; never FPS/client/admission evidence."""
from pathlib import Path
import argparse,hashlib,io,json,os,shutil,struct,subprocess,time
import nbtlib
ROOT=Path(__file__).resolve().parents[2]
GRILL='c68005c5-23ff-54e8-a3ff-da6349ad43c2'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['candidate','bds-root','level-metadata','output']:p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--without-profiler',action='store_true');p.add_argument('--seconds',type=int,default=180);p.add_argument('--port',type=int,default=25720);a=p.parse_args()
 if a.seconds<5 or not 1024<=a.port<=65530:p.error('invalid duration or port')
 if a.output.exists():raise SystemExit('Output exists; preserve prior evidence')
 receipt=json.loads((a.candidate/'family-receipt.json').read_text());packs={row['uuid']:row for row in receipt['packs']}
 # Exact dependency closure, retaining the same host module bytes for comparison.
 minimal={GRILL};pending=[GRILL]
 while pending:
  uid=pending.pop()
  for dep in packs[uid].get('dependencies',[]):
   target=dep.get('uuid')
   if target and target not in minimal:minimal.add(target);pending.append(target)
 a.output.mkdir(parents=True);reports=[]
 for index,(name,selected) in enumerate([('minimal',minimal),('full',set(packs))]):
  out=a.output/name;out.mkdir()
  for item in ['bedrock_server','definitions','behavior_packs','resource_packs']:(out/item).symlink_to((a.bds_root/item).resolve(),target_is_directory=(a.bds_root/item).is_dir())
  for item in ['config','minecraftpe','treatments']:shutil.copytree(a.bds_root/item,out/item)
  (out/'allowlist.json').write_text('[]\n')
  (out/'server.properties').write_text(f'server-name=Isolated Grilling profile\ntransport=nethernet\nlevel-name=Performance Test\nserver-port={a.port+index*2}\nserver-portv6={a.port+index*2+1}\nonline-mode=false\nallow-list=false\nview-distance=4\ntick-distance=4\nmax-threads=2\nenable-lan-visibility=false\ncontent-log-file-enabled=true\ncontent-log-console-output-enabled=true\nallow-cheats=true\n')
  world=out/'worlds/Performance Test';world.mkdir(parents=True)
  for uid in selected:
   row=packs[uid];rel=Path(row['side']+'_packs')/uid;shutil.copytree(a.candidate/rel,world/rel)
  for side,order in receipt['order'].items():(world/('world_'+side+'_packs.json')).write_text(json.dumps([{'pack_id':uid,'version':packs[uid]['version']} for uid in order if uid in selected],indent=2)+'\n')
  f=nbtlib.File.parse(io.BytesIO(a.level_metadata.read_bytes()[8:]),byteorder='little');f['LevelName']=nbtlib.String('Performance Test');f['SpawnX']=nbtlib.Int(0);f['SpawnY']=nbtlib.Int(80);f['SpawnZ']=nbtlib.Int(0);f['commandsEnabled']=nbtlib.Byte(1)
  f['experiments']=nbtlib.Compound({k:nbtlib.Byte(1) for k in ['upcoming_creator_features','experiments_ever_used','saved_with_toggled_experiments']})
  data=io.BytesIO();f.write(data,byteorder='little');body=data.getvalue();(world/'level.dat').write_bytes(struct.pack('<II',10,len(body))+body)
  bp=world/'behavior_packs'/GRILL
  shutil.copy2(Path(__file__).with_name('native_performance_probe.js'),bp/'scripts/performance_probe.js')
  with (bp/'scripts/main.js').open('a') as stream:stream.write('\nimport {runPerformanceProbe} from "./performance_probe.js";\nrunPerformanceProbe({inv,writeState,initialState});\n')
  with (bp/'scripts/a23_oil_world.js').open('a') as stream:stream.write('\nexport {registerSource as performanceRegisterSource};\n')
  log=out/'bds.log';started=time.monotonic();ready=False;measured=False;samples=[];measurement_start=None
  with log.open('w') as stream:
   proc=subprocess.Popen(['./bedrock_server'],cwd=out,env={**os.environ,'LD_LIBRARY_PATH':str(out)},stdin=subprocess.PIPE,stdout=stream,stderr=subprocess.STDOUT,text=True)
   def command(text):proc.stdin.write(text+'\n');proc.stdin.flush()
   try:
    while time.monotonic()-started<180:
     time.sleep(1);text=log.read_text()
     if 'GRILLING_PERF_FAIL' in text or proc.poll() is not None:break
     if 'GRILLING_PERF_READY ' in text:ready=True;break
    if ready:
     command('scriptevent senluo:performance_sample start')
     if not a.without_profiler:command('script profiler start')
     measurement_start=time.monotonic();offset=len(log.read_text().splitlines())
     while time.monotonic()-measurement_start<a.seconds and proc.poll() is None:
      time.sleep(1)
      try:
       status=Path(f'/proc/{proc.pid}/status').read_text();rss=next(int(line.split()[1]) for line in status.splitlines() if line.startswith('VmRSS:'));samples.append({'elapsed_seconds':round(time.monotonic()-measurement_start,3),'rss_kib':rss})
      except (OSError,StopIteration):pass
     if proc.poll() is None:
      if not a.without_profiler:command('script profiler stop')
      command('scriptevent senluo:performance_sample end')
      measured=True;time.sleep(3)
    if proc.poll() is None:proc.communicate('stop\n',timeout=40)
   finally:
    if proc.poll() is None:proc.kill();proc.wait()
  text=log.read_text();errors=[line for line in text.splitlines() if ' ERROR]' in line or 'GRILLING_PERF_FAIL' in line]
  profile_files=[x for x in out.rglob('*.cpuprofile') if not x.is_symlink()]
  markers=[line.split('GRILLING_PERF_READY ',1)[1] for line in text.splitlines() if 'GRILLING_PERF_READY ' in line]
  tick_samples=[json.loads(line.split('GRILLING_PERF_SAMPLE ',1)[1]) for line in text.splitlines() if 'GRILLING_PERF_SAMPLE ' in line]
  tick_rate=None
  if len(tick_samples)==2 and tick_samples[1]['time']>tick_samples[0]['time']:tick_rate=1000*(tick_samples[1]['tick']-tick_samples[0]['tick'])/(tick_samples[1]['time']-tick_samples[0]['time'])
  warnings=[line for line in (text.splitlines()[offset:] if ready else text.splitlines()) if 'Watchdog' in line]
  report={'variant':name,'profiler_enabled':not a.without_profiler,'packs':len(selected),'pack_uuids':sorted(selected),'ready':ready,'setup':json.loads(markers[-1]) if markers else None,'measured_seconds':a.seconds if measured and not errors else None,'profiles':[{'path':str(x.relative_to(a.output)),'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in profile_files],'errors':errors,'watchdog_during_measurement':warnings,'rss_samples':samples,'tick_samples':tick_samples,'measured_ticks_per_second':tick_rate,'normal_exit':proc.returncode==0,'test_probe_sha256':hashlib.sha256(Path(__file__).with_name('native_performance_probe.js').read_bytes()).hexdigest(),'test_only_source_overlays':True,'same_host_extensions':True,'client':False,'production_ready':False}
  reports.append(report);(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['rss_samples','pack_uuids']}),flush=True)
  if not ready or not measured or errors or (not a.without_profiler and not profile_files):break
 (a.output/'report.json').write_text(json.dumps({'schema':1,'candidate_receipt_sha256':hashlib.sha256((a.candidate/'family-receipt.json').read_bytes()).hexdigest(),'runs':reports,'client':False,'production_ready':False},indent=2)+'\n')
 if len(reports)!=2 or any(not r['ready'] or r['measured_seconds'] is None or r['errors'] or (r['profiler_enabled'] and not r['profiles']) for r in reports):raise SystemExit(1)
if __name__=='__main__':main()
