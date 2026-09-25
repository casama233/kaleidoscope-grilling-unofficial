"""Publish only the exact successfully built main commit; never mark a test stable."""
from pathlib import Path
import hashlib,json,os,re,subprocess
ROOT=Path(__file__).resolve().parents[2]
REPO='casama233/kaleidoscope-grilling-unofficial'
def call(*args):return subprocess.check_output(args,cwd=ROOT,text=True).strip()
def main():
 assert os.environ.get('GITHUB_REPOSITORY')==REPO
 assert os.environ.get('GITHUB_REPOSITORY_ID')=='1377218440'
 assert os.environ.get('GITHUB_REF')=='refs/heads/main'
 sha=call('git','rev-parse','HEAD');assert sha==os.environ['GITHUB_SHA']
 out=ROOT/'artifacts/review';report=json.loads((out/'build-report.json').read_text(encoding='utf-8-sig'))
 assert report['git_sha']==sha,'Release tag and tested source must identify the same commit'
 version=report['version'];assert re.fullmatch(r'A\d+\.\d+\.\d+',version)
 tag=f"{version}-test.{os.environ['GITHUB_RUN_NUMBER']}.{os.environ['GITHUB_RUN_ATTEMPT']}"
 assets=[]
 for key,ext in [('mcaddon','.mcaddon'),('brproject','.brproject')]:
  matches=list(out.glob('*'+ext));assert len(matches)==1
  p=matches[0];assert hashlib.sha256(p.read_bytes()).hexdigest()==report[key]['sha256'];assets.append(p)
 assets += [out/'SHA256SUMS.txt',out/'build-report.json']
 assert all(p.is_file() for p in assets)
 notes=out/'release-notes.md'
 status=ROOT/'docs'/f'STATUS-{version}.md'
 notes.write_text(f'# {version} 整合測試版\n\n此包直接由合併後 main 的 `{sha}` 建置並校驗。\n\n'
  'Minecraft / BDS / client visuals：**尚未實機驗收**。請先備份測試世界。\n\n'
  '安裝 `.mcaddon`；原有 Cookery 1.0.6 依賴不變，煙火指南已在本體內，不需另外安裝指南包。\n\n'
  +(status.read_text(encoding='utf-8') if status.exists() else '')+'\n',encoding='utf-8')
 # Unique tag for each attempt; no deletion of older test builds or release assets.
 subprocess.run(['gh','release','create',tag,*map(str,assets),'--repo',REPO,'--target',sha,
  '--title',f'Kaleidoscope Grilling {version} Integrated Test','--notes-file',str(notes),'--prerelease'],cwd=ROOT,check=True)
 print('Published',tag,'from tested main',sha)
if __name__=='__main__':main()
