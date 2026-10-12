#!/usr/bin/env python3
"""Emit exact public reference matches for hovercard adapters (no network)."""
import argparse,json,pathlib
p=argparse.ArgumentParser();p.add_argument('--station-id',required=True);p.add_argument('--appliance-name');a=p.parse_args()
d=json.loads((pathlib.Path(__file__).parent/'data/reference.json').read_text())
s=next((s for s in d['stations'] if s['id']==a.station_id),None)
if s is None:p.error('unknown station ID; no fuzzy fallback')
units=[u for u in d['appliances'] if u['station_id']==s['id'] and (a.appliance_name is None or u['name']==a.appliance_name)]
print(json.dumps({'schema_version':1,'station':s,'appliances':units,'detail_page_imported':s['station_code'] in d['coverage']['detail_pages_visited'],'attribution':'SACFS Promotions Unit','data_license':d['data_license']},indent=2))
