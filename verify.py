#!/usr/bin/env python3
"""Offline agency, coverage, provenance and non-redistribution verification."""
import json,pathlib,urllib.parse
root=pathlib.Path(__file__).resolve().parent
d=json.loads((root/'data/australia/south-australia/fire/reference.json').read_text())
assert d['schema_version']==1 and d['data_license']=='CC-BY-SA-4.0'
services={'SACFS':'sacfs','SAMFS':'samfs'}
def url(value):
 p=urllib.parse.urlparse(value);assert p.scheme=='https' and p.hostname=='www.fire-brigade.asn.au',value
station_ids={station['id'] for station in d['stations']}
assert len(station_ids)==len(d['stations'])
for station in d['stations']:
 assert station['id']==services[station['service']]+':station:'+station['station_code']
 assert station['operational_status']=='unknown';url(station['source_url'])
seen=set()
for a in d['appliances']:
 assert a['id'] not in seen,a['id'];seen.add(a['id'])
 assert a['id'].startswith(a['listing_key']+':')
 assert a['id_stability'] in ('registration-aware-listing','provisional')
 assert a['station_id'] in station_ids and a['station_id'].startswith(services[a['service']]+':station:')
 assert a['class_id'].startswith(services[a['service']]+':class:')
 url(a['source_url']);url(a['class_source_url'])
 assert a['name'] and a['full_label'] and a['compact_label']
 assert a['make_model'] is None or isinstance(a['make_model'],str)
 for field in ('water_litres','foam_litres'):
  assert a[field] is None or isinstance(a[field],int) and a[field]>=0
 assert isinstance(a['photo'],dict)
 photo=a['photo'];url(photo['page_url'])
 # RIGHTS.md decision 2026-10-17: every captioned photo is CC BY-SA 4.0, credited as captioned.
 if photo['rights_status']=='cc-by-sa-4.0-sidebar':
  assert photo['redistribution_allowed'] is True and photo['license']=='CC-BY-SA-4.0'
  assert isinstance(photo['credit'],str) and photo['credit'],photo
  url(photo['image_url']);assert urllib.parse.urlparse(photo['image_url']).path.startswith('/photos/')
 else:
  assert photo['rights_status']=='no-photo' and photo['image_url'] is None and photo['credit'] is None,photo
  assert photo['license'] is None and photo['redistribution_allowed'] is None
 if a['service']=='SAMFS' and a['vehicle_code']:
  assert a['compact_label']=='MFS '+a['vehicle_code']
for source in d['sources']:
 url(source['url']);assert len(source['sha256'])==64 and source['retrieved_at']
c=d['coverage']
assert c['current_station_index_count']==sum(s['listed_in_current_station_index'] for s in d['stations'])
assert c['appliance_index_count']==sum(s['listed_in_appliance_index'] for s in d['stations'])
assert set(c['detail_pages_visited'])<=station_ids
assert len(set(c['detail_pages_visited']))==len(c['detail_pages_visited'])
assert not c['complete_appliance_inventory'] or len(c['detail_pages_visited'])==c['appliance_index_count'] and not c['detail_page_failures']
for service,coverage in c['by_service'].items():
 assert all(s.startswith(services[service]+':station:') for s in coverage['detail_pages_visited'])
 assert not coverage['complete_appliance_inventory'] or len(coverage['detail_pages_visited'])==coverage['appliance_index_count'] and not coverage['detail_page_failures']
seaf=[a for a in d['appliances'] if a['station_id']=='sacfs:station:SEAF' and a['name']=='Seaford 34']
assert len(seaf)==1 and seaf[0]['water_litres']==3000 and seaf[0]['registration']=='S659AQX' and seaf[0]['compact_label']=='SEAF 34'
if 'SAMFS' in c['by_service']:
 unit=[a for a in d['appliances'] if a['station_id']=='samfs:station:40' and a['vehicle_code']=='401']
 assert len(unit)==1 and unit[0]['make_model']=='Scania P360' and unit[0]['water_litres']==2500 and unit[0]['foam_litres']==120 and unit[0]['registration']=='XS58JM'
roles={a['full_label']:a['compact_label'] for a in d['appliances'] if a['service']=='SAMFS'}
for role in ('Car 40','Hooklift 01','Surge 01'):
 assert roles[role]=='MFS '+role
for p in root.rglob('*'):
 if '.git' in p.parts or '__pycache__' in p.parts:continue
 assert p.suffix.lower() not in ('.jpg','.png','.gif','.wav','.mp3','.html'),p
print(f"PASS: {len(d['stations'])} agency-qualified station/group records, {len(d['appliances'])} appliances; {len(c['detail_pages_visited'])}/{c['appliance_index_count']} validated detail pages; {len(c['detail_page_failures'])} failures")
