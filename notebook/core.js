
// Own per-player notebook. No commands, world edits, inventory writes or global host replacement.
export const PROPERTY = 'kg_a1:notebook_v1';
export const BACKUP = 'kg_a1:notebook_backup_v1';
export const LIMITS = Object.freeze({recipes:64, favorites:128, name:40, note:240, bytes:24000});
export class NotebookError extends Error { constructor(code,message){super(message);this.code=code;} }
const fail=(c,m)=>{throw new NotebookError(c,m);};
const byteLength=s=>{let n=0;for(const c of s){const x=c.codePointAt(0);n+=x<128?1:x<2048?2:x<65536?3:4;}return n;};
const plain=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const idOK=s=>typeof s==='string'&&/^[a-z0-9_.-]+:[a-z0-9_./-]+$/.test(s)&&s.length<=160;
function cleanText(s,max,required=false){if(typeof s!=='string')fail('INVALID_TEXT','文字必須為字串');s=s.normalize('NFKC').trim();if(/[\u0000-\u001f\u007f\u202a-\u202e\u2066-\u2069§]/u.test(s))fail('INVALID_TEXT','文字含控制字元');if([...s].length>max||(required&&!s))fail('INVALID_TEXT','文字長度不合要求');return s;}
export function emptyNotebook(){return {schema:1,revision:0,nextId:1,favorites:[],recipes:[]};}
export function validateRecipe(input){
 if(!plain(input))fail('INVALID_RECIPE','配方必須為物件');
 const name=cleanText(input.name,LIMITS.name,true),note=cleanText(input.note??'',LIMITS.note);
 if(!Array.isArray(input.ingredients)||input.ingredients.length<1||input.ingredients.length>3)fail('INVALID_RECIPE','穿串需要一至三個有順序的材料位置');
 const ingredients=input.ingredients.map(i=>{if(!plain(i)||!idOK(i.item)||!Number.isInteger(i.count??1)||(i.count??1)<1||(i.count??1)>64)fail('INVALID_RECIPE','食材識別碼或數量錯誤');return {item:i.item,count:i.count??1};});
 const state=input.state??'raw';if(!['raw','cooked'].includes(state))fail('INVALID_RECIPE','狀態錯誤');
 return {name,note,ingredients,state};
}
export function decode(raw){
 if(raw===undefined||raw===null)return emptyNotebook();
 if(typeof raw!=='string'||byteLength(raw)>LIMITS.bytes)fail('CORRUPT','筆記儲存內容不合法；原資料未更改');
 let s;try{s=JSON.parse(raw);}catch{fail('CORRUPT','筆記 JSON 損壞；原資料未更改');}
 if(!plain(s)||s.schema!==1)fail('SCHEMA','不支援此筆記版本；未降版覆寫');
 if(!Number.isSafeInteger(s.revision)||s.revision<0||!Number.isSafeInteger(s.nextId)||s.nextId<1||!Array.isArray(s.favorites)||!Array.isArray(s.recipes)||s.favorites.length>LIMITS.favorites||s.recipes.length>LIMITS.recipes)fail('CORRUPT','筆記結構或數量不合法');
 if(s.favorites.some(i=>!idOK(i))||new Set(s.favorites).size!==s.favorites.length)fail('CORRUPT','收藏資料錯誤');
 const seen=new Set();for(const r of s.recipes){if(!plain(r)||!Number.isSafeInteger(r.id)||r.id<1||r.id>=s.nextId||seen.has(r.id))fail('CORRUPT','配方識別碼錯誤');seen.add(r.id);validateRecipe(r);}
 return {schema:1,revision:s.revision,nextId:s.nextId,favorites:[...s.favorites],recipes:s.recipes.map(r=>({id:r.id,...validateRecipe(r)}))};
}
export class NotebookStore {
 constructor(player){if(!player||typeof player.getDynamicProperty!=='function'||typeof player.setDynamicProperty!=='function')fail('ADAPTER','需要玩家儲存接口');this.player=player;}
 read(){return decode(this.player.getDynamicProperty(PROPERTY));}
 mutate(expectedRevision,change){
  const beforeRaw=this.player.getDynamicProperty(PROPERTY),s=decode(beforeRaw);
  if(expectedRevision!==undefined&&s.revision!==expectedRevision)fail('STALE','頁面已過期，請重新開啟；沒有覆寫較新資料');
  const result=change(s);s.revision++;
  const raw=JSON.stringify(s);if(byteLength(raw)>LIMITS.bytes)fail('LIMIT','筆記容量已滿');decode(raw);
  // No await between read and write: all updates remain synchronous in the server event loop.
  if(beforeRaw!==undefined)this.player.setDynamicProperty(BACKUP,beforeRaw);
  this.player.setDynamicProperty(PROPERTY,raw);
  if(this.player.getDynamicProperty(PROPERTY)!==raw)fail('WRITE','儲存後核對失敗');
  return {state:s,result};
 }
 save(recipe,id=null,revision){const value=validateRecipe(recipe);return this.mutate(revision,s=>{if(id===null){if(s.recipes.length>=LIMITS.recipes)fail('LIMIT','最多儲存64個配方');id=s.nextId++;s.recipes.push({id,...value});}else{const i=s.recipes.findIndex(x=>x.id===id);if(i<0)fail('MISSING','找不到配方');s.recipes[i]={id,...value};}return id;});}
 remove(id,revision){return this.mutate(revision,s=>{const i=s.recipes.findIndex(x=>x.id===id);if(i<0)fail('MISSING','找不到配方');s.recipes.splice(i,1);});}
 favorite(id,on,revision){if(!idOK(id)||typeof on!=='boolean')fail('INVALID_ID','收藏識別碼錯誤');return this.mutate(revision,s=>{const i=s.favorites.indexOf(id);if(on&&i<0){if(s.favorites.length>=LIMITS.favorites)fail('LIMIT','收藏數已滿');s.favorites.push(id);}if(!on&&i>=0)s.favorites.splice(i,1);});}
 export(){return JSON.stringify(this.read(),null,2);}
 restoreBackup(revision){const backup=decode(this.player.getDynamicProperty(BACKUP));if(this.player.getDynamicProperty(BACKUP)===undefined)fail('MISSING','沒有備份');return this.mutate(revision,s=>{s.recipes=backup.recipes;s.favorites=backup.favorites;s.nextId=Math.max(s.nextId,backup.nextId);});}
}
export function searchRecipes(catalog,query){const q=cleanText(query,120).toLocaleLowerCase();const tokens=q.split(/\s+/u).filter(Boolean);return catalog.filter(r=>{const words=[r.id,r.name,r.note,...(r.ingredients??[]).flatMap(x=>typeof x==='string'?[x]:[x.item,JSON.stringify(x)])].join(' ').normalize('NFKC').toLocaleLowerCase();return tokens.every(t=>words.includes(t));});}
