from __future__ import annotations
import hashlib,sys,zipfile,re,json
from pathlib import Path

EXPECTED='c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351'
TOKENS=(
 'mechanicsByLocale','guidebook_ready','guidebook_begin','guidebook_chunk','guidebook_end',
 'guidebookExtension','extensionRegistry','locale','language','names','text','mechanics'
)

def excerpt(text,needle,radius=6):
 lines=text.splitlines()
 out=[]
 for i,line in enumerate(lines):
  if needle.lower() in line.lower():
   a=max(0,i-radius);b=min(len(lines),i+radius+1)
   out.append({'needle':needle,'line':i+1,'excerpt':'\n'.join(f'{j+1}: {lines[j]}' for j in range(a,b))})
 return out

def main():
 if len(sys.argv)!=2:raise SystemExit('usage: inspect_cookery_locale.py <mcaddon>')
 p=Path(sys.argv[1]);got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==EXPECTED,(got,EXPECTED)
 hits=[]
 with zipfile.ZipFile(p) as z:
  for n in z.namelist():
   if not n.lower().endswith(('.js','.md','.json','.lang')):continue
   try:text=z.read(n).decode('utf-8-sig')
   except Exception:continue
   found=[]
   for token in TOKENS:
    if token.lower() in text.lower():found.extend(excerpt(text,token))
   if found:hits.append({'path':n,'matches':found})
 print(json.dumps({'sha256':got,'files':hits},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
