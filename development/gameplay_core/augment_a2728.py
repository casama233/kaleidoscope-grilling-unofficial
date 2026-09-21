from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'projects/grilling/gameplay_core';BP=P/'behavior_pack';RP=P/'resource_pack'
VERSION=[2,7,28]

CN_OVERRIDES={
 'item.kaleidoscope_grilling:green_chili_powder.name':'绿辣椒粉',
 'item.kaleidoscope_grilling:houttuynia_powder.name':'折耳根粉',
 'item.kaleidoscope_grilling:totem_powder.name':'不死图腾粉',
 'tile.kaleidoscope_grilling:houttuynia_crop.name':'折耳根',
}

TW_OVERRIDES={
 'item.kaleidoscope_grilling:green_chili_powder.name':'青辣椒粉',
 'item.kaleidoscope_grilling:houttuynia_powder.name':'折耳根粉',
 'item.kaleidoscope_grilling:totem_powder.name':'不死圖騰粉',
 'item.kaleidoscope_grilling:raw_potato_slice_skewer.name':'生馬鈴薯片串',
 'item.kaleidoscope_grilling:grilled_potato_slice_skewer.name':'烤馬鈴薯片串',
 'item.kaleidoscope_grilling:potato_slice.name':'馬鈴薯片',
 'item.kaleidoscope_grilling:sweet_potato.name':'番薯',
 'item.kaleidoscope_grilling:sweet_potato_powder.name':'番薯粉',
 'item.kaleidoscope_grilling:roasted_sweet_potato.name':'烤番薯',
 'tile.kaleidoscope_grilling:sweet_potato_crop.name':'番薯',
 'tile.kaleidoscope_grilling:houttuynia_crop.name':'折耳根',
}

TR=str.maketrans({
 '烧':'燒','馒':'饅','猪':'豬','儿':'兒','鸡':'雞','鱼':'魚','鱿':'魷','须':'鬚',
 '黄':'黃','连':'連','调':'調','制':'製','摇':'搖','盘':'盤','谱':'譜','饼':'餅',
 '红':'紅','萝':'蘿','块':'塊','葱':'蔥','凉':'涼','图':'圖','龙':'龍','绿':'綠',
 '鱼':'魚','边':'邊','层':'層','发':'發','后':'後','里':'裡','这':'這','个':'個',
 '种':'種','与':'與','为':'為','开':'開','关':'關','处':'處','过':'過','复':'複',
 '气':'氣','区':'區','对':'對','应':'應','显':'顯','条':'條','数':'數','类':'類',
 '别':'別','样':'樣','时':'時','间':'間','满':'滿','还':'還','从':'從','实':'實',
 '体':'體','储':'儲','备':'備','传':'傳','统':'統','页':'頁','简':'簡','选':'選',
 '择':'擇','进':'進','词':'詞','义':'義','块':'塊','卜':'蔔','虫':'蟲','面':'麵'
})

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write_json(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read_lang(p):
 out={};order=[]
 for line in p.read_text(encoding='utf-8-sig').splitlines():
  if '=' not in line:continue
  k,v=line.split('=',1);out[k]=v;order.append(k)
 return out,order
def write_lang(p,data,order):
 p.write_text('\n'.join(f'{k}={data[k]}' for k in order)+'\n',encoding='utf-8')

def patch_versions():
 bm,rm=load(BP/'manifest.json'),load(RP/'manifest.json')
 for doc,name in ((bm,'Kaleidoscope Grilling A2.7.28 Localization BP'),(rm,'Kaleidoscope Grilling A2.7.28 Localization RP')):
  doc['header']['version']=VERSION;doc['header']['name']=name
  for m in doc.get('modules',[]):m['version']=VERSION
 for dep in bm.get('dependencies',[]):
  if dep.get('uuid')==rm['header']['uuid']:dep['version']=VERSION
 write_json(BP/'manifest.json',bm);write_json(RP/'manifest.json',rm)
 cfg=load(P/'config.json');cfg['name']='Kaleidoscope Grilling A2.7.28 Localization';cfg['compiler']['plugins'][0][1]['packName']='Kaleidoscope_Grilling_A2_7_28_Localization';write_json(P/'config.json',cfg)

def patch_languages():
 texts=RP/'texts';cn,order=read_lang(texts/'zh_CN.lang');tw,tw_order=read_lang(texts/'zh_TW.lang');en,en_order=read_lang(texts/'en_US.lang')
 if order!=tw_order or order!=en_order or set(cn)!=set(tw) or set(cn)!=set(en):
  raise RuntimeError('language key sets/order drift before A2.7.28')
 cn.update(CN_OVERRIDES)
 # Build Traditional Chinese from the corrected Simplified source so every key has a deliberate counterpart.
 tw={k:cn[k].translate(TR) for k in order};tw.update(TW_OVERRIDES)
 write_lang(texts/'zh_CN.lang',cn,order);write_lang(texts/'zh_TW.lang',tw,order)
 write_json(texts/'languages.json',['zh_CN','zh_TW','en_US'])
 return len(order)

def report(count):
 write_json(P/'reports/a2728-localization.json',{
  'version':'A2.7.28','scope':'language file normalization only','language_keys':count,
  'languages':['zh_CN','zh_TW','en_US'],'equal_key_sets':True,
  'zh_cn_java_terminology_fixes':['绿辣椒粉','折耳根粉','不死图腾粉','折耳根'],
  'zh_tw_generated_from_corrected_zh_cn_then_overridden':True,
  'zh_tw_semantic_overrides':['馬鈴薯片','番薯','不死圖騰粉','青辣椒粉'],
  'gameplay_logic_changed':False,'minecraft_tested':False,'bds_tested':False,
 })

def main():
 if load(BP/'manifest.json')['header']['version']!=[2,7,27]:
  raise RuntimeError('A2.7.28 must augment verified A2.7.27')
 patch_versions();count=patch_languages();report(count);print('A2.7.28 localization complete')
if __name__=='__main__':main()
