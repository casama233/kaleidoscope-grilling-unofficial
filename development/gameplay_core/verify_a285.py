import json, subprocess
from pathlib import Path
from verify_a283 import BP, RP, ROOT, main as previous_gate
from verify_a284 import eating_gate

def survival_gate():
    script=(BP/'scripts/main.js').read_text()
    assert 'MAX_GRILLS' not in script and 'readRegistry' not in script
    assert "onTick(e){tickGrill(e.block)}" in script
    block=json.loads((BP/'blocks/grill.json').read_text())['minecraft:block']['components']
    assert block['minecraft:tick']=={'interval_range':[1,1],'looping':True}
    assert 'kaleidoscope_grilling:grill_tick' in block
    settle=script.split('function hungerSettle(',1)[1].split('function resolvedProfile(',1)[0]
    assert settle.index('eatingStillCurrent') < settle.index('commitEating')
    assert settle.index('secretRemainders') < settle.index('afterCommitted')
    full=script.split('world.afterEvents.itemCompleteUse.subscribe',1)[1].split('world.afterEvents.itemStopUse.subscribe',1)[0]
    assert full.rindex('secretRemainders') < full.rindex('afterCommitted')
    plate=script.split('function completePlateUse',1)[1].split('function completePending',1)[0]
    assert plate.index('secretRemainders') < plate.index('afterCommitted')
    assert 'captureEatingIdentity(e.itemStack,hand,e.source.selectedSlotIndex)' in script
    assert 'SEASON_PLACE_CACHE.set(key(e.block)' in script
    assert 'cached.playerId!==player.id' in script
    for name in ['empty_seasoning_bottle','pending_seasoning','special_seasoning']+[p.stem for p in (BP/'items').glob('special_seasoning_r*_v*.json')]:
        recipe=json.loads((BP/f'recipes/clear_{name}.json').read_text())['minecraft:recipe_shapeless']
        assert recipe['ingredients']==[{'item':'kaleidoscope_grilling:'+name}]
        assert recipe['result']=={'item':'kaleidoscope_grilling:empty_seasoning_bottle','count':1}
    subprocess.run(['node',str(Path(__file__).with_name('test_a285_core.mjs'))],cwd=ROOT,check=True)
    print('A285 native grill ticking, 67 clear-bottle recipes and placement snapshots: PASS')

if __name__=='__main__':
    eating_gate()
    survival_gate()
    previous_gate()
