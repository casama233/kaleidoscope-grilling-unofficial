"""Pure catalog-data checks, not Minecraft interaction or rendered UI tests."""
from copy import deepcopy
import itertools
import unittest
import a2771_shared_creative as c

class SharedCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=c.load(c.FIXTURE)
        cls.ids={c.NS+x for members in c.ASSIGNMENTS.values() for x in members}
        cls.catalog=c.build_catalog(cls.ids,cls.fixture)

    def test_pinned_reference_catalogs(self):
        self.assertEqual(len(c.validate_fixture(self.fixture)),14)
    def test_chinese_food_reuses_ten_actual_host_groups(self):
        host=c.validate_fixture(self.fixture)
        shared={(cat,g['group_identifier']['name']) for cat,g in c.catalog_groups(self.fixture['chinese_food']['catalog'])
                if g['group_identifier']['name'].startswith(c.HOST)}
        self.assertEqual(len(shared),10)
        self.assertTrue(shared<=host)
    def test_correct_equipment_category(self):
        self.assertEqual({cat for cat,_ in c.catalog_groups(self.catalog)},{'equipment'})
    def test_no_new_grilling_groups(self):
        host=c.validate_fixture(self.fixture)
        self.assertTrue({(cat,g['group_identifier']['name']) for cat,g in c.catalog_groups(self.catalog)}<=host)
    def test_preserve_host_icons(self):
        for _,g in c.catalog_groups(self.catalog):self.assertEqual(set(g['group_identifier']),{'name'})
    def test_exactly_ninety_unique_own_items(self):
        items=[i for _,g in c.catalog_groups(self.catalog) for i in g['items']]
        self.assertEqual(len(items),90)
        self.assertEqual(len(set(items)),90)
        self.assertTrue(all(i.startswith(c.NS) for i in items))
    def test_unknown_visible_item_fails(self):
        with self.assertRaises(ValueError):c.build_catalog(self.ids|{c.NS+'unexpected'},self.fixture)
    def test_missing_visible_item_fails(self):
        with self.assertRaises(ValueError):c.build_catalog(self.ids-{c.NS+'grill'},self.fixture)
    def test_same_label_wrong_category_not_accepted(self):
        changed=deepcopy(self.fixture)
        changed['cookery']['catalog']['minecraft:crafting_items_catalog']['categories'][0]['category_name']='items'
        with self.assertRaises(ValueError):c.validate_fixture(changed)
    def test_reference_content_cannot_be_silently_changed(self):
        changed=deepcopy(self.fixture)
        changed['cookery']['catalog']['minecraft:crafting_items_catalog']['categories'][0]['groups'].pop()
        with self.assertRaises(ValueError):c.validate_fixture(changed)
    def test_no_new_group_in_all_six_pack_orders(self):
        refs=[self.fixture[k]['catalog'] for k in ('cookery','chinese_food')]
        base=c.merged_members(refs)
        expected=set(i for members in base.values() for i in members)|self.ids
        for packs in itertools.permutations([*refs,self.catalog]):
            merged=c.merged_members(packs)
            self.assertEqual(set(merged),set(base))
            items=[i for members in merged.values() for i in members]
            self.assertEqual(set(items),expected)
            self.assertEqual(len(items),len(set(items)))
    def test_preserve_unrelated_locale_bytes(self):
        data=b'item.name=Item\r\nkaleidoscope_grilling:itemGroup.raw_skewers=Old\r\n\r\nitem.more=More\r\n'
        self.assertEqual(c.remove_own_labels(data),b'item.name=Item\r\n\r\nitem.more=More\r\n')
    def test_do_not_delete_host_translation(self):
        data=b'kaleidoscope_cookery:itemGroup.name.foods=Foods\n'
        self.assertEqual(c.remove_own_labels(data),data)
    def test_raw_cooked_order_still_matches(self):
        items=[i for _,g in c.catalog_groups(self.catalog) for i in g['items']]
        raw=[i.replace(':raw_',':',1) for i in items if i.startswith(c.NS+'raw_') and i.endswith('_skewer')]
        cooked=[i.replace(':grilled_',':',1) for i in items if i.startswith(c.NS+'grilled_') and i.endswith('_skewer')]
        self.assertEqual(len(raw),19)
        self.assertEqual(raw,cooked)
    def test_labels_resolve_in_host_without_copying(self):
        for _,group in c.catalog_groups(self.catalog):
            for locale in ('zh_TW','zh_CN','en_US'):
                self.assertTrue(self.fixture['cookery']['labels'][locale][group['group_identifier']['name']])

if __name__=='__main__':unittest.main(verbosity=2)
