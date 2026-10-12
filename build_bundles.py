#!/usr/bin/env python3
"""Build a small exact-name consumer index; ambiguous names abstain."""
import collections,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
source_path=ROOT/'data/australia/south-australia/fire/reference.json'
source=json.loads(source_path.read_text())
groups=collections.defaultdict(list)
for unit in source['appliances']:
    if unit.get('source_conflicts'):continue
    groups[''.join(unit['full_label'].casefold().split())].append(unit)
rows=[];ambiguous=[]
for key,units in sorted(groups.items()):
    if len({(unit['service'],unit['station_id'],unit['compact_label']) for unit in units})!=1:
        ambiguous.append(key);continue
    unit=units[0]
    rows.append({field:unit[field] for field in ('service','full_label','compact_label','source_url','source_updated_text')} | {'reference_id':unit['listing_key'],'reference_ids':sorted({entry['id'] for entry in units}),'station_id':unit['station_id'],'match_key':key})
result={'schema_version':1,'bundle_id':'wavecap:fire-unit-labels:v1','source_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),'license':'CC-BY-SA-4.0','attribution':'SACFS Promotions Unit; WaveCap reference contributors','attribution_url':'https://www.fire-brigade.asn.au/','rights_url':'https://www.fire-brigade.asn.au/legal.asp','match_policy':'exact full source name with case/whitespace normalization; never a numeric-only join; ambiguous names omitted','rows':rows,'ambiguous_match_keys':ambiguous}
(ROOT/'bundles').mkdir(exist_ok=True)
(ROOT/'bundles/unit-labels.v1.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
print(f'Generated {len(rows)} exact label rows; omitted {len(ambiguous)} ambiguous names')
talkgroup_path=ROOT/'data/australia/south-australia/radio/sascan-sagrn-talkgroups.v1.json'
if talkgroup_path.exists():
    archive=json.loads(talkgroup_path.read_text());provenance=archive['provenance']
    talkgroups={'schema_version':1,'bundle_id':'wavecap:sagrn-talkgroups:v1','source_id':'sagrn','source_sha256':hashlib.sha256(talkgroup_path.read_bytes()).hexdigest(),'publisher':provenance['publisher'],'original_url':provenance['original_url'],'archive_url':provenance['archive_url'],'source_updated_date':provenance['source_updated_date'],'capture_datetime':provenance['capture_datetime'],'upstream_license':None,'contribution_license':'CC-BY-SA-4.0','precedence':'reference seeds only; never overrides configured/operator names','rows':[{'talkgroup_id':r['talkgroup_id_decimal'],'talkgroup_id_hex':r['talkgroup_id_hex'],'name':r['name'],'category':r['label_variants'][0]['category'],'human_channel_number':r['label_variants'][0]['human_channel_number']} for r in archive['records'] if not r['has_source_conflict']],'conflicting_talkgroup_ids':[r['talkgroup_id_decimal'] for r in archive['records'] if r['has_source_conflict']]}
    (ROOT/'bundles/sagrn-talkgroups.v1.json').write_text(json.dumps(talkgroups,separators=(',',':'))+'\n')
    print(f'Generated {len(talkgroups["rows"])} historical talkgroup seeds; omitted {len(talkgroups["conflicting_talkgroup_ids"])} source conflicts')
