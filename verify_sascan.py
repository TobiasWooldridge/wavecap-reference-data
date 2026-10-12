#!/usr/bin/env python3
import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
def validate():
 d=json.loads((ROOT/'data/australia/south-australia/radio/sascan-sagrn-talkgroups.v1.json').read_text())
 p=d['provenance'];assert p['requested_capture_timestamp']==p['actual_capture_timestamp']=='20251225115143'
 assert p['source_updated_date']=='2025-07-27' and p['upstream_license'] is None and p['raw_html_distributed'] is False
 records=d['records'];assert len(records)==678 and len({r['id'] for r in records})==678
 assert sum(r['has_source_conflict'] for r in records)==4 and len(d['rejected_rows'])==8
 for row in records:
  n=row['talkgroup_id_decimal'];assert 0<n<=65535 and int(row['talkgroup_id_hex'],16)==n
  assert row['id']=='sagrn:p25:talkgroup:'+str(n)
  assert row['source_id']=='sagrn' and row['label_variants']
  assert not row['has_source_conflict'] or row['name'] is None
 sample=next(r for r in records if r['talkgroup_id_decimal']==3157)
 assert sample['talkgroup_id_hex']=='C55' and sample['label_variants'][0]['human_channel_number']=='001'
 assert d['comparison']['matched_ids']==444 and d['comparison']['new_ids']==234
 print('PASS:678 decimal TGIDs,4 retained source conflicts,8 missing-ID rows rejected; TG3157/C55 distinct from channel001')
if __name__=='__main__':validate()
