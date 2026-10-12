#!/usr/bin/env python3
"""Exact agency-qualified public reference lookup, without network access."""
import argparse,json,pathlib
parser=argparse.ArgumentParser()
parser.add_argument('--station-id',required=True)
parser.add_argument('--appliance-name')
parser.add_argument('--vehicle-code',help='exact source-listed MFS code, not a radio ID')
args=parser.parse_args()
data=json.loads((pathlib.Path(__file__).parent/'data/reference.json').read_text())
station=next((s for s in data['stations'] if s['id']==args.station_id),None)
if station is None:parser.error('unknown agency-qualified station ID; no fuzzy fallback')
units=[a for a in data['appliances'] if a['station_id']==station['id'] and
       (args.appliance_name is None or a['name']==args.appliance_name) and
       (args.vehicle_code is None or a['vehicle_code']==args.vehicle_code)]
print(json.dumps({'schema_version':1,'station':station,'appliances':units,
                  'detail_page_imported':station['id'] in data['coverage']['detail_pages_visited'],
                  'attribution':'SACFS Promotions Unit','data_license':data['data_license']},indent=2))
