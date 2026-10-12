import unittest
from import_sascan import parse
class ArchiveParserTests(unittest.TestCase):
 def test_decimal_id_is_not_human_channel_or_legacy_parenthesis(self):
  source='SA GRN P25 Talkgroups<table><tr><td colspan="2">Agency</td></tr><tr><td>3157</td><td>001 - OPERATIONS (48096)</td></tr><tr><td>???</td><td>002 - UNKNOWN</td></tr></table>'
  rows,rejected=parse(source)
  self.assertEqual(rows[0]['talkgroup_id_decimal'],3157)
  self.assertEqual(rows[0]['talkgroup_id_hex'],'C55')
  self.assertEqual(rows[0]['label_variants'][0]['human_channel_number'],'001')
  self.assertEqual(len(rejected),1)
 def test_same_id_contradictory_labels_abstain(self):
  rows,_=parse('SA GRN P25 Talkgroups<tr><td colspan="2">Agency</td></tr><tr><td>155</td><td>HF2</td></tr><tr><td>155</td><td>RADIO TECHNICIANS</td></tr>')
  self.assertTrue(rows[0]['has_source_conflict']);self.assertIsNone(rows[0]['name'])
 def test_wrong_source_page_is_rejected(self):
  with self.assertRaises(ValueError):parse('HTTP200 generic archive error')
if __name__=='__main__':unittest.main()
