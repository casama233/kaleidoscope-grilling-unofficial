from __future__ import annotations
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/"projects/grilling/gameplay_core"
BP=PROJECT/"behavior_pack"
RP=PROJECT/"resource_pack"

def load(path:Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def check(cond,msg):
    if not cond:
        raise AssertionError(msg)

required=[
 "unfinished_skewer","secret_skewer","beef_chunks","chicken_skin","chicken_wing",
 "squid_tentacle","raw_sweet_potato_sheet","minced_houttuynia","potato_slice",
 "carrot_dice","raw_mantou_slice","houttuynia"
]
for item in required:
    path=BP/"items"/f"{item}.json"
    check(path.exists(),f"missing item {item}")
    data=load(path)
    check(data["minecraft:item"]["description"]["identifier"]==f"kaleidoscope_grilling:{item}",f"bad id {item}")

atlas=load(RP/"textures/item_texture.json")["texture_data"]
for item in required:
    check(item in atlas,f"missing texture atlas entry {item}")

for lang in ("zh_CN.lang","zh_TW.lang","en_US.lang"):
    text=(RP/"texts"/lang).read_text(encoding="utf-8-sig")
    for item in required:
        check(f"item.kaleidoscope_grilling:{item}.name=" in text,f"missing {lang} name {item}")

bp=load(BP/"manifest.json")
rp=load(RP/"manifest.json")
check(bp["header"]["version"]==[2,4,0],"BP version is not A2.4")
check(rp["header"]["version"]==[2,4,0],"RP version is not A2.4")
check(any(x.get("module_name")=="@minecraft/server" and x.get("version")=="2.9.0" for x in bp["dependencies"]),"server 2.9.0 missing")
check(any(x.get("version")==[1,0,6] for x in bp["dependencies"] if "uuid" in x and x["uuid"]!="bbbd2d60-52e5-53a6-8b9a-c09b0f516389"),"Cookery 1.0.6 BP dependency missing")
check(any(x.get("version")==[1,0,6] for x in rp["dependencies"]),"Cookery 1.0.6 RP dependency missing")

rules=(BP/"scripts/a24_skewer_rules.js").read_text(encoding="utf-8")
runtime=(BP/"scripts/a24_skewering.js").read_text(encoding="utf-8")
main=(BP/"scripts/main.js").read_text(encoding="utf-8")
check(rules.count("{result:")==20,"expected 20 Java threading recipes")
check("secretFoodStats" in runtime and "coefficient=.6" in runtime and "?.8:1" in runtime,"secret nutrition formula missing")
check("world.beforeEvents.itemUse.subscribe" in main,"itemUse threading hook missing")
check("copyOne(held)" in main,"grill does not preserve per-stack metadata")
check("id===SECRET_ID&&!isSecretCooked(held)" in main,"raw secret skewer grill path missing")
check("settleSecretNative" in main,"dynamic secret food settlement missing")

all_json=list(BP.rglob("*.json"))+list(RP.rglob("*.json"))
for path in all_json:
    load(path)

print(json.dumps({
 "ok":True,
 "a24_items":len(required),
 "threading_recipes":20,
 "server_module":"2.9.0",
 "cookery_dependency":"1.0.6",
 "json_files":len(all_json)
},ensure_ascii=False))
