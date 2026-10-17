"""Pure catalog/data tests; these do not simulate a Minecraft client."""
import unittest
import a2770_creative_catalog as c

class CatalogTests(unittest.TestCase):
    def test_no_ambiguous_item_assignment(self):
        ids=[x for row in c.GROUPS for x in row[4]]
        self.assertEqual(len(ids),len(set(ids)))
    def test_unknown_visible_item_fails_closed(self):
        with self.assertRaises(ValueError): c.make_groups({c.NS+'future_item'})
    def test_foreign_namespace_rejected(self):
        with self.assertRaises(ValueError): c.make_groups({'kaleidoscope_tavern:shaker'})
    def test_empty_groups_not_emitted(self):
        groups=c.make_groups({c.NS+'grill'})
        self.assertEqual(len(groups),1)
        self.assertTrue(groups[0]['group_identifier']['name'].endswith('.stations'))
    def test_raw_cooked_pair_order(self):
        ids={c.NS+p+x+'_skewer' for x in reversed(c.SKEWERS) for p in ('raw_','grilled_')}
        groups=c.make_groups(ids)
        self.assertEqual(len(groups),2)
        self.assertEqual([x.replace(':raw_',':') for x in groups[0]['items']],
                         [x.replace(':grilled_',':') for x in groups[1]['items']])
    def test_icon_is_member(self):
        ids={c.NS+x for row in c.GROUPS for x in row[4]}
        for group in c.make_groups(ids):
            self.assertIn(group['group_identifier']['icon'],group['items'])
    def test_all_locales(self):
        groups=c.make_groups({c.NS+'grill',c.NS+'raw_beef_skewer'})
        active={g['group_identifier']['name'] for g in groups}
        for locale in c.LOCALES:
            result=c.localized('other:item=unchanged\r\n',locale,active)
            for key in active:self.assertEqual(result.count(key+'='),1)
            self.assertIn('other:item=unchanged',result.splitlines())
    def test_localization_idempotent(self):
        active={c.GROUP_PREFIX+'stations'}
        first=c.localized('old:key=text\n', 'zh_TW', active)
        self.assertEqual(first,c.localized(first,'zh_TW',active))
    def test_locale_normalization_preserves_non_group_text(self):
        old='item.name=Name\r\n\r\n'
        result=c.localized(old,'en_US',{c.GROUP_PREFIX+'stations'})
        self.assertEqual(c.strip_group_lines(old),c.strip_group_lines(result))
    def test_hidden_definitions_not_eligible(self):
        self.assertFalse(c.visible({'menu_category':{'category':'none'}}))
        self.assertFalse(c.visible({}))
        self.assertTrue(c.visible({'menu_category':{'category':'items'}}))
    def test_no_duplicate_emitted_items(self):
        ids={c.NS+x for row in c.GROUPS for x in row[4]}
        items=[i for group in c.make_groups(ids) for i in group['items']]
        self.assertEqual(set(items),ids)
        self.assertEqual(len(items),len(ids))
    def test_flat_official_catalog_schema(self):
        doc=c.expected_catalog(c.make_groups({c.NS+'grill'}))
        cats=doc['minecraft:crafting_items_catalog']['categories']
        self.assertEqual(len(cats),1)
        self.assertEqual(cats[0]['category_name'],'items')
        self.assertEqual(doc['format_version'],'1.21.60')

if __name__=='__main__':unittest.main(verbosity=2)
