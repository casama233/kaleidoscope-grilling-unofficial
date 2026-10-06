"""Execute bottle item authoring expressions; never rebuild over repaired packs."""
import ast
from copy import deepcopy
from pathlib import Path
import json
import runpy
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
DEV = Path(__file__).resolve().parent
BP = ROOT / 'projects/grilling/gameplay_core/behavior_pack'
SOURCE_BASE = '9bb6d63f10d9004b874e81794803737704a4b671'
STATE_BOTTLES = {f'special_seasoning_r{r}_v{v}' for r in range(1, 9) for v in range(8)}
BOTTLES = {'empty_seasoning_bottle', 'pending_seasoning', 'special_seasoning'} | STATE_BOTTLES


def source(name, old=False):
    if old:
        return subprocess.check_output(['git', 'show', SOURCE_BASE + ':development/gameplay_core/' + name], cwd=ROOT).decode()
    return (DEV / name).read_text(encoding='utf-8-sig')


def authored_items(old=False):
    # Execute the actual support-item loop with an in-memory writer, not a copy
    # of its JSON. The three oil-brush definitions are kept in the same loop.
    tree = ast.parse(source('build.py', old))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    loop = next(n for n in main.body if isinstance(n, ast.For) and isinstance(n.target, ast.Name)
                and n.target.id == 'item_id' and ast.unparse(n.iter) == 'sorted(support)')
    definitions = {}
    env = {'NS': 'kaleidoscope_grilling', 'support': {'empty_seasoning_bottle', 'special_seasoning',
           'canola_oil_brush', 'secret_chili_oil_brush', 'premium_chili_oil_brush'},
           'item_dir': Path('items'), 'write': lambda p, doc: definitions.__setitem__(p.stem, doc)}
    exec(compile(ast.Module(body=[loop], type_ignores=[]), 'build.py:support', 'exec'), env)
    tree = ast.parse(source('augment_a21.py', old))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    pending = next(n for n in main.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'pending' for t in n.targets))
    definitions['pending_seasoning'] = eval(compile(ast.Expression(pending.value), 'augment_a21.py:pending', 'eval'), {})
    if old:
        tree = ast.parse(source('a2766_build_special_seasoning_visuals.py', True))
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'item_doc')
        env = {'PREFIX': 'kaleidoscope_grilling:special_seasoning_r', 'DISPLAY': 'item.kaleidoscope_grilling:special_seasoning.name'}
        exec(compile(ast.Module(body=[fn], type_ignores=[]), 'a2766:item_doc', 'exec'), env)
        item_doc = env['item_doc']
    else:
        item_doc = runpy.run_path(str(DEV / 'a2766_build_special_seasoning_visuals.py'))['item_doc']
    for r in range(1, 9):
        for v in range(8):
            definitions[f'special_seasoning_r{r}_v{v}'] = item_doc(v, r)
    return definitions


def authoring_expectation(baseline, name):
    expected = deepcopy(baseline)
    if name in BOTTLES:
        expected['minecraft:item']['components']['minecraft:allow_off_hand'] = True
    if name in STATE_BOTTLES:
        # G71 corrects the inventory icon for each exact finished state. Keep
        # every other field in this historical authoring comparison intact.
        expected['minecraft:item']['components']['minecraft:icon'] = {'textures': {'default': name}}
    return expected


def check_authoring():
    current, old = authored_items(), authored_items(old=True)
    assert set(current) == BOTTLES | {'canola_oil_brush', 'secret_chili_oil_brush', 'premium_chili_oil_brush'}
    for name, definition in current.items():
        expected = authoring_expectation(old[name], name)
        if name in BOTTLES:
            actual = json.loads((BP / f'items/{name}.json').read_bytes())
            assert actual['minecraft:item']['description']['identifier'] == 'kaleidoscope_grilling:' + name
            assert actual['minecraft:item']['components']['minecraft:allow_off_hand'] is True, name
        assert definition == expected, 'Authoring changed more than exact bottle eligibility and state icon bindings: ' + name
    return len(BOTTLES)


class BottleItemOffhandSources(unittest.TestCase):
    def test_all_67_authored_items_retain_flag_and_other_authoring_fields(self):
        self.assertEqual(check_authoring(), 67)

    def test_state_icon_expectation_is_exact_and_preserves_every_other_field(self):
        baseline = {'minecraft:item': {'components': {
            'minecraft:max_stack_size': 1,
            'minecraft:icon': {'textures': {'default': 'special_seasoning'}},
        }}}
        for name in STATE_BOTTLES:
            expected = authoring_expectation(baseline, name)
            self.assertEqual(expected['minecraft:item']['components']['minecraft:icon'], {'textures': {'default': name}})
            for wrong in ('special_seasoning', 'special_seasoning_r0_v0', name + '_wrong'):
                altered = deepcopy(expected)
                altered['minecraft:item']['components']['minecraft:icon']['textures']['default'] = wrong
                self.assertNotEqual(altered, expected)
            altered = deepcopy(expected)
            altered['minecraft:item']['components']['minecraft:max_stack_size'] = 64
            self.assertNotEqual(altered, expected)
        for name in ('empty_seasoning_bottle', 'pending_seasoning', 'special_seasoning', 'special_seasoning_r9_v0', 'other'):
            expected = authoring_expectation(baseline, name)
            self.assertEqual(expected['minecraft:item']['components']['minecraft:icon'], baseline['minecraft:item']['components']['minecraft:icon'])

    def test_label_gate_rejects_missing_false_and_unrelated_non_display_changes(self):
        # The same full-dict expectation used by the label gate permits exactly
        # one prescribed value, rather than stripping a component from either side.
        from test_item_labels import current_behavior_expectation
        baseline = {'minecraft:item': {'components': {'minecraft:max_stack_size': 1}}}
        expected = current_behavior_expectation(baseline, 'item', 'pending_seasoning', (2, 8, 61))
        self.assertEqual(baseline, {'minecraft:item': {'components': {'minecraft:max_stack_size': 1}}})
        self.assertIs(expected['minecraft:item']['components']['minecraft:allow_off_hand'], True)
        for value in [False, None, 1]:
            altered = deepcopy(expected)
            altered['minecraft:item']['components']['minecraft:allow_off_hand'] = value
            self.assertFalse(type(value) is bool and altered == expected)
        altered = deepcopy(expected)
        altered['minecraft:item']['components']['minecraft:max_stack_size'] = 64
        self.assertNotEqual(altered, expected)
        self.assertEqual(current_behavior_expectation(baseline, 'item', 'other', (2, 8, 61)), baseline)
        self.assertEqual(current_behavior_expectation(baseline, 'item', 'pending_seasoning', (2, 8, 60)), baseline)


if __name__ == '__main__':
    unittest.main()
