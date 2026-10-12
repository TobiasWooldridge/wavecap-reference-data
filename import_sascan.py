#!/usr/bin/env python3
"""Normalize factual SA Scan IDs/labels; retain archive/source provenance."""
import argparse,datetime,hashlib,html,json,pathlib,re,urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
ORIGINAL='https://www.sascan.net.au/?page=infPages/GRNTalkgroups'
ARCHIVE='https://web.archive.org/web/20251225115143/'+ORIGINAL
RAW='https://web.archive.org/web/20251225115143id_/'+ORIGINAL

def clean(value):return ' '.join(html.unescape(re.sub('<[^>]*>',' ',value)).split())
def parse(source):
 if 'SA GRN P25 Talkgroups' not in source:raise ValueError('unexpected source page')
 source=source.split('SA GRN P25 Talkgroups',1)[1]
 category=None;groups={};rejected=[]
 for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>',source,re.I|re.S):
  cells=re.findall(r'<td\b[^>]*>(.*?)</td>',row,re.I|re.S)
  if len(cells)==1 and re.search(r'colspan=["\']?2',row,re.I):category=clean(cells[0]);continue
  if len(cells)!=2:continue
  identifier,label=map(clean,cells)
  if identifier=='ID #':continue
  if not category:continue
  if not re.fullmatch(r'[0-9]+',identifier):
   if identifier or label:rejected.append({'id_text':identifier,'reason':'not an explicit decimal ID cell'})
   continue
  decimal=int(identifier)
  if not 0<decimal<=65535:raise ValueError('P25 talkgroup ID out of range')
  human=re.match(r'^(\d{1,3})\s*-\s*(.+)$',label)
  variant={'label':label,'name':human.group(2) if human else label,'human_channel_number':human.group(1) if human else None,'category':category}
  groups.setdefault(decimal,[])
  if variant not in groups[decimal]:groups[decimal].append(variant)
 records=[]
 for decimal,variants in sorted(groups.items()):
  records.append({'id':'sagrn:p25:talkgroup:'+str(decimal),'system_scope':'SA-GRN P25','source_id':'sagrn','talkgroup_id_decimal':decimal,'talkgroup_id_hex':format(decimal,'X'),'id_basis':'decimal numeric source ID column; independently crosschecked against existing ID keys','name':variants[0]['name'] if len(variants)==1 else None,'label_variants':variants,'has_source_conflict':len(variants)>1,'precedence':'reference-seed-only; never replaces verified/operator overrides','validity':'historical source snapshot; not verified current allocation'})
 return records,rejected

def main():
 p=argparse.ArgumentParser();p.add_argument('--input-html',type=pathlib.Path,required=True);p.add_argument('--fetch',action='store_true');p.add_argument('--existing-config',type=pathlib.Path);args=p.parse_args()
 if args.fetch:
  response=urllib.request.urlopen(urllib.request.Request(RAW,headers={'User-Agent':'WaveCapReference/1.0 (bounded source citation fetch)'}),timeout=40)
  assert '25 Dec 2025 11:51:43' in response.headers.get('memento-datetime',''),'unexpected capture datetime'
  args.input_html.parent.mkdir(parents=True,exist_ok=True);args.input_html.write_bytes(response.read())
 raw=args.input_html.read_bytes();source=raw.decode('utf-8');records,rejected=parse(source)
 comparison={'policy':'archive seeds only; existing application and verified/operator overrides remain unchanged','existing_config_sha256':None,'existing_ids':None,'matched_ids':None,'new_ids':None,'different_label_ids':[]}
 if args.existing_config:
  existing_raw=args.existing_config.read_bytes();existing={int(row['id']):row for row in json.loads(existing_raw)['talkgroups']}
  matched=[r for r in records if r['talkgroup_id_decimal'] in existing]
  comparison.update(existing_config_sha256=hashlib.sha256(existing_raw).hexdigest(),existing_ids=len(existing),matched_ids=len(matched),new_ids=len(records)-len(matched),different_label_ids=[r['talkgroup_id_decimal'] for r in matched if existing[r['talkgroup_id_decimal']]['name'] not in {v['label'] for v in r['label_variants']}|{v['name'] for v in r['label_variants']}])
  # Existing labels themselves are not republished from third-party RR-derived configs.
 provenance={'publisher':'SA Scan / sascan.net.au','original_url':ORIGINAL,'archive_url':ARCHIVE,'raw_archive_url':RAW,'requested_capture_timestamp':'20251225115143','actual_capture_timestamp':'20251225115143','capture_datetime':'2025-12-25T11:51:43Z','source_updated_date':'2025-07-27','retrieved_date':'2026-10-12','html_sha256':hashlib.sha256(raw).hexdigest(),'rights_status':'no explicit source reuse licence found; independently structured factual labels only','upstream_license':None,'contribution_license':'CC-BY-SA-4.0','raw_html_distributed':False}
 result={'schema_version':1,'dataset_id':'sascan:sagrn:p25:talkgroups:20251225115143','provenance':provenance,'records':records,'comparison':comparison,'rejected_rows':rejected}
 out=ROOT/'data/australia/south-australia/radio';out.mkdir(parents=True,exist_ok=True);(out/'sascan-sagrn-talkgroups.v1.json').write_text(json.dumps(result,indent=2)+'\n')
 print('SA Scan:',len(records),'distinct TGIDs;',sum(r['has_source_conflict'] for r in records),'source conflicts;',len(rejected),'rejected rows')
if __name__=='__main__':main()
