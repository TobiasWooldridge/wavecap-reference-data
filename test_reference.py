"""Focused regressions for real source HTML and duplicate-listing findings."""
import json,pathlib,tempfile,unittest
from unittest.mock import patch
import import_reference
from import_reference import captioned_photos,links,normalize,photo_record
class ReferenceTests(unittest.TestCase):
 def test_offline_rebuild_uses_scoped_agency_snapshots(self):
  relative=pathlib.Path('data/australia/south-australia/fire')
  source=pathlib.Path(__file__).resolve().parent/relative
  expected=json.loads((source/'reference.json').read_text())
  with tempfile.TemporaryDirectory() as temporary:
   destination=pathlib.Path(temporary)/relative
   destination.mkdir(parents=True)
   for snapshot in source.glob('*.agency.json'):
    (destination/snapshot.name).write_bytes(snapshot.read_bytes())
   with patch.object(import_reference,'ROOT',pathlib.Path(temporary)):
    import_reference.bundle()
   actual=json.loads((destination/'reference.json').read_text())
   self.assertEqual(actual,expected)
 def test_captioned_photos_keep_each_credit_and_first_repeated_caption(self):
  cell='<img src="/photos/{0}.jpg" title="{1}" width=300>\n <BR>\n {1}<BR>\n Picture by {2}<BR>'
  source=''.join(cell.format(*row) for row in [('a','Seaford 34','Emergency Media SA'),('b','Seaford Air','CFS Promotions Unit'),('c','Seaford 34','Someone Else')])
  photos=captioned_photos(source)
  self.assertEqual(photos,{'Seaford 34':('/photos/a.jpg','Emergency Media SA'),'Seaford Air':('/photos/b.jpg','CFS Promotions Unit')})
  self.assertIsNone(captioned_photos(source+'<img src="/photos/d.jpg">'))
  record=photo_record('https://www.fire-brigade.asn.au/p',photos['Seaford 34'])
  self.assertEqual((record['rights_status'],record['credit'],record['license'],record['image_url']),
   ('cc-by-sa-4.0-sidebar','Emergency Media SA','CC-BY-SA-4.0','https://www.fire-brigade.asn.au/photos/a.jpg'))
  self.assertEqual(photo_record('https://www.fire-brigade.asn.au/p',None)['rights_status'],'no-photo')
 def test_unclosed_legacy_anchors_preserve_separate_agencies(self):
  source='<A href="Appliance_Display.asp?Service_Code=SAMFS&Station_Code=40">St Marys<br><A href="Appliance_Display.asp?Service_Code=SACFS&Station_Code=40">Other<br>'
  self.assertEqual(links(source,'Appliance','SAMFS')['40']['id'],'samfs:station:40')
  self.assertEqual(links(source,'Appliance','SACFS')['40']['id'],'sacfs:station:40')
 def test_conflicting_required_structure_is_retained_with_evidence(self):
  first={'id':'same','class_id':'first','photo':{'page_url':'first'},'water_litres':100,'make_model':None}
  second={'id':'same','class_id':'second','photo':{'page_url':'second'},'water_litres':200,'make_model':'Truck'}
  result=normalize([first,second])[0]
  self.assertEqual(result['class_id'],'first')
  self.assertEqual(result['photo'],{'page_url':'first'})
  self.assertIsNone(result['water_litres'])
  self.assertEqual(result['make_model'],'Truck')
  self.assertEqual(result['source_conflicts']['class_id'],['first','second'])
 def test_later_duplicate_cannot_erase_earlier_conflict(self):
  result=normalize([{'id':'same','water_litres':100},{'id':'same','water_litres':200},{'id':'same','water_litres':300}])[0]
  self.assertIsNone(result['water_litres'])
  self.assertEqual(result['source_conflicts']['water_litres'],[100,200,300])
if __name__=='__main__':unittest.main()
