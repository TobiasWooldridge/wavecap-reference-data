#!/usr/bin/env python3
"""Offline contract/provenance and non-redistribution verification."""
import json,pathlib,urllib.parse
root=pathlib.Path(__file__).resolve().parent
d=json.loads((root/'data/reference.json').read_text())
assert d['schema_version']==1
assert d['data_license']=='CC-BY-SA-4.0'
def url(u):
 p=urllib.parse.urlparse(u);assert p.scheme=='https' and p.hostname=='www.fire-brigade.asn.au',u
station_ids={r['id'] for r in d['stations']}
assert len(station_ids)==len(d['stations'])
seen=set()
for s in d['stations']:
 assert s['id']=='sacfs:station:'+s['station_code'];url(s['source_url'])
 assert s['operational_status']=='unknown'
for a in d['appliances']:
 assert a['id'] not in seen,a['id'];seen.add(a['id'])
 assert a['id'].startswith(a['listing_key']+':')
 assert a['id_stability'] in ('registration-aware-listing','provisional')
 assert a['station_id'] in station_ids;url(a['source_url']);url(a['class_source_url'])
 assert a['name'] and (a['make_model'] is None or isinstance(a['make_model'],str))
 for field in ('water_litres','foam_litres'): assert a[field] is None or isinstance(a[field],int) and a[field]>=0
 assert a['photo']['image_url'] is None and a['photo']['redistribution_allowed'] is None
 assert a['photo']['rights_status']=='conflicting-notices';url(a['photo']['page_url'])
for source in d['sources']:
 url(source['url']);assert len(source['sha256'])==64 and source['retrieved_at']
c=d['coverage'];assert c['current_station_index_count']==sum(s['listed_in_current_station_index'] for s in d['stations'])
assert c['appliance_index_count']==sum(s['listed_in_appliance_index'] for s in d['stations'])
assert not c['complete_appliance_inventory'] or len(c['detail_pages_visited'])==c['appliance_index_count'] and not c['detail_page_failures']
seaf=[a for a in d['appliances'] if a['name']=='Seaford 34']
assert len(seaf)==1 and seaf[0]['water_litres']==3000 and seaf[0]['registration']=='S659AQX'
for p in root.rglob('*'):
 if '.git' in p.parts:continue
 assert p.suffix.lower() not in ('.jpg','.png','.gif','.wav','.mp3','.html'),p
print(f"PASS: {len(d['stations'])} station/group records, {len(d['appliances'])} appliances; {len(c['detail_pages_visited'])}/{c['appliance_index_count']} detail pages; {len(c['detail_page_failures'])} fetch failures")
