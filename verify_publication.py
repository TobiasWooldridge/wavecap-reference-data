#!/usr/bin/env python3
"""Offline package/hash/bundle/privacy guard, including reachable git history."""
import hashlib,json,pathlib,re,subprocess
ROOT=pathlib.Path(__file__).resolve().parent
FORBIDDEN_SUFFIXES={'.html','.htm','.jpg','.jpeg','.png','.gif','.wav','.mp3','.flac','.sqlite','.sqlite3','.db','.zip','.pbf','.pdf','.pem','.key'}
SECRET=re.compile(rb'-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}')
def validate():
 catalog=json.loads((ROOT/'catalog.json').read_text())
 assert catalog['schema_version']==1
 for entry in catalog['datasets']:
  path=ROOT/entry['path'];data=path.read_bytes()
  assert hashlib.sha256(data).hexdigest()==entry['sha256'],entry['path']
  assert (entry['source_urls'] or entry.get('provenance_kind')=='operator-confirmation') and entry['attribution'] and entry['license'] and entry['stable_key'] and entry['validity']
  if entry['record_count'] is not None:
   assert entry['record_count']==sum(bool(line.strip()) and not line.startswith('#') for line in data.decode().splitlines())
 bundle=json.loads((ROOT/'bundles/unit-labels.v1.json').read_text())
 fire=json.loads((ROOT/'data/reference.json').read_text())
 assert bundle['source_sha256']==hashlib.sha256((ROOT/'data/reference.json').read_bytes()).hexdigest()
 by_id={a['id']:a for a in fire['appliances']}
 assert len({row['match_key'] for row in bundle['rows']})==len(bundle['rows'])
 for row in bundle['rows']:
  assert row['reference_ids']
  original=by_id[row['reference_ids'][0]]
  assert row['reference_id']==original['listing_key']
  assert all((by_id[identity]['service'],by_id[identity]['station_id'],by_id[identity]['compact_label'])==(row['service'],row['station_id'],row['compact_label']) for identity in row['reference_ids'])
  assert all(row[key]==original[key] for key in ('service','full_label','compact_label','station_id','source_url','source_updated_text'))
  assert row['match_key']==''.join(row['full_label'].casefold().split()) and not row['match_key'].isdigit()
  assert row['match_key'] not in bundle['ambiguous_match_keys']
 radio=json.loads((ROOT/'datasets/radio/operator-confirmed-radio-units.v1.json').read_text())
 assert {row['radio_id'] for row in radio['records']}=={'5240303','5271291','5214914','5062003','5271282','5271299'}
 for row in radio['records']:
  assert row['source_id']=='sagrn' and row['provenance']['kind']=='operator-confirmation'
  assert row['provenance']['public_confirmation_url'] is None
  assert row['identity_scope']['wacn'] is None and row['identity_scope']['rf_system_id'] is None
 # Public snapshot contains public references, never working caches/incidents.
 for path in ROOT.rglob('*'):
  if '.git' in path.parts or '__pycache__' in path.parts or not path.is_file():continue
  assert path.suffix.lower() not in FORBIDDEN_SUFFIXES,path
  assert not SECRET.search(path.read_bytes()),path
 # Review every reachable historical blob, not just current working files.
 objects=subprocess.check_output(['git','rev-list','--objects','--all'],cwd=ROOT,text=True).splitlines()
 reviewed=0
 for entry in objects:
  if ' ' not in entry:continue
  oid,name=entry.split(' ',1)
  assert pathlib.PurePosixPath(name).suffix.lower() not in FORBIDDEN_SUFFIXES,name
  if subprocess.check_output(['git','cat-file','-t',oid],cwd=ROOT,text=True).strip()!='blob':continue
  data=subprocess.check_output(['git','cat-file','blob',oid],cwd=ROOT)
  assert not SECRET.search(data),name
  reviewed+=1
 print(f'PASS: {len(catalog["datasets"])} source/licence/hash entries; {len(bundle["rows"])} exact consumer rows; {reviewed} reachable historical blobs checked')
if __name__=='__main__':validate()
