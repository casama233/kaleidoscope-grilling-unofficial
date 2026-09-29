"""A2.8.8 Batch 1 parity gate: extensible secret-food contracts and generic manual hot-food merge."""
from pathlib import Path
import subprocess, sys
from verify_a287 import binding_assets, plant_gate
from verify_a285 import survival_gate
from verify_a284 import eating_gate
from verify_a283 import BP, ROOT, main as previous_gate

DEV=Path(__file__).parent

def parity_gate():
    main=(BP/'scripts/main.js').read_text(encoding='utf-8')
    ingredient=(BP/'scripts/a285_ingredient_effects.js').read_text(encoding='utf-8')
    hot=(BP/'scripts/a23_hot_runtime.js').read_text(encoding='utf-8')
    contract=(BP/'scripts/a288_parity_contract.js').read_text(encoding='utf-8')
    runtime=(BP/'scripts/a288_parity_runtime.js').read_text(encoding='utf-8')
    assert 'VANILLA_SMOKED' not in main
    assert 'resolveSmokingResult(row.id)' in main
    assert "import './a288_parity_runtime.js'" in main
    assert 'compactHotFoodContainer(c,undefined,id)' in main
    assert 'ingredientFinishBehavior(row.id)' in ingredient
    assert 'registerSmokingResult' in contract and 'registerIngredientFinishBehavior' in contract
    assert 'kaleidoscope_grilling:register_smoking' in runtime
    assert 'kaleidoscope_grilling:register_food_finish' in runtime
    assert 'export function compactHotFoodContainer' in hot
    subprocess.run(
        ['node','--experimental-vm-modules',str(DEV/'test_a288_parity.mjs')],
        cwd=ROOT,check=True
    )
    print('A288 parity contracts and generic manual hot-food merge: PASS')

if __name__=='__main__':
    parity_gate()
    binding_assets()
    plant_gate()
    eating_gate()
    survival_gate()
    previous_gate()
