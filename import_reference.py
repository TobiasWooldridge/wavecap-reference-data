#!/usr/bin/env python3
"""Bounded, cached source importer; standard library only. No image fetching."""
import argparse, datetime, hashlib, html, json, pathlib, re, time, urllib.parse, urllib.request
BASE='https://www.fire-brigade.asn.au/'
ROOT=pathlib.Path(__file__).resolve().parent
CACHE=ROOT.parent.parent/'cache'
def text(s): return ' '.join(html.unescape(re.sub('<[^>]*>',' ',s)).split())
def fetch(path, refresh=False):
 url=urllib.parse.urljoin(BASE,path); key=hashlib.sha256(url.encode()).hexdigest(); file=CACHE/(key+'.html'); CACHE.mkdir(parents=True,exist_ok=True)
 if refresh or not file.exists():
  time.sleep(1)
  req=urllib.request.Request(url,headers={'User-Agent':'CFSReference/1.0 (cached factual reference; no image download)'})
  file.write_bytes(urllib.request.urlopen(req,timeout=45).read())
 raw=file.read_bytes(); return raw.decode('utf-8',errors='replace'),{'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'retrieved_at':datetime.datetime.fromtimestamp(file.stat().st_mtime,datetime.timezone.utc).isoformat(),'rights_status':'conflicting-notices','attribution':'SACFS Promotions Unit; individual photo credits remain on source page'}
def links(s, kind):
 out={}
 for href,label in re.findall(r'<a\s+href=["\']([^"\']+)["\'][^>]*>([^<]*)',s,re.I|re.S):
  if kind+'_Display.asp?' not in href: continue
  q=urllib.parse.parse_qs(urllib.parse.urlparse(html.unescape(href)).query)
  if q.get('Service_Code')!=['SACFS']:continue
  code=q['Station_Code'][0];out[code]={'id':'sacfs:station:'+code,'service':'SACFS','station_code':code,'name':text(label),'source_url':urllib.parse.urljoin(BASE if kind=='Station' else BASE+'vehicles/',html.unescape(href))}
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=0,help='maximum detail pages to fetch; 0 indexes only');ap.add_argument('--refresh',action='store_true');args=ap.parse_args()
 sources=[];s,p=fetch('Station_Find.asp?Station_Name=&Service_Code=SACFS&btnLogin=Find+Stations',args.refresh);sources.append(p);current=links(s,'Station')
 s,p=fetch('vehicles/Appliance_Find.asp?Station_Name=&Service_Code=SACFS&btnLogin=Find+Appliances',args.refresh);sources.append(p);fleet=links(s,'Station') | links(s,'Appliance')
 stations=[]
 for code in sorted(set(current)|set(fleet)):
  r=dict(current[code] if code in current else fleet[code]);r['listed_in_current_station_index']=code in current;r['listed_in_appliance_index']=code in fleet;r['record_kind']='station_or_group_or_region';r['operational_status']='unknown';stations.append(r)
 apps=[];failed=[];visited=[]
 codes=sorted(fleet,key=lambda c:(c not in ('SEAF','SLSB'),c not in current,c))[:args.limit]
 for code in codes:
  url='vehicles/Appliance_Display.asp?Service_Code=SACFS&Station_Code='+urllib.parse.quote(code)
  try:s,p=fetch(url,args.refresh)
  except Exception as e:failed.append({'station_code':code,'error':str(e)});continue
  sources.append(p);visited.append(code)
  if 'Vehicles &amp; Appliances' not in s:continue
  updated=re.search(r'last updated on\s*([^<]+)',s,re.I)
  photo_credits={text(name):text(credit) for name,credit in re.findall(r'<BR>\s*([^<]+)<BR>\s*Picture by ([^<]+)',s,re.I)}
  body=s.split('Vehicles &amp; Appliances',1)[1]
  blocks=re.split(r'<TD WIDTH="25%"[^>]*>',body,flags=re.I)[1:]
  for block in blocks:
   name=text(block.split('</TD>',1)[0]);m=re.search(r'<a\s+Href="([^"]+)">([^<]+)</a>\s*<br>Make and Model:\s*(.*?)\s*<FONT',block,re.I|re.S)
   if not m:continue
   flat=text(block);reg=re.search(r'Registration Number:\s*([A-Za-z0-9 -]+?)(?:\s+Equipment:|$)',flat)
   registration=reg.group(1).strip() if reg else None
   unit_key=re.sub('[^A-Z0-9]+','-',name.upper()).strip('-')
   record={'id':'sacfs:appliance:'+code+':'+unit_key,'station_id':'sacfs:station:'+code,'name':name,'registration':registration,'source_updated_text':text(updated.group(1)) if updated else None,'make_model':text(m.group(3)),'class_id':'sacfs:class:'+pathlib.PurePosixPath(m.group(1)).stem.removeprefix('sacfs-').upper(),'class_source_url':urllib.parse.urljoin(BASE,m.group(1)),'source_url':p['url'],'operational_status':'listed_at_source','photo':{'page_url':p['url'],'credit':photo_credits.get(name),'rights_status':'conflicting-notices','redistribution_allowed':None,'image_url':None}}
   for field,label in [('water_litres','Water Capacity'),('foam_litres','Foam Quantity')]:
    match=re.search(label+r':\s*(\d+)\s*Litres',flat);record[field]=int(match.group(1)) if match else None
   apps.append(record)
  print(code,len(apps),flush=True)
 for path in ['legal.asp','vehicles/vehicles/sacfs-34.asp']:
  _,p=fetch(path,args.refresh);sources.append(p)
 classes=[{'id':'sacfs:class:34','name':'34','water_litres_typical':3000,'drive':'4WD','variants':['34R','34P','34URP'],'source_url':BASE+'vehicles/vehicles/sacfs-34.asp','equipment_varies_by_appliance':True}]
 result={'schema_version':1,'data_license':'CC-BY-SA-4.0','third_party_rights':'See RIGHTS.md; no photo or prose redistribution licence inferred','stations':stations,'appliances':apps,'classes':classes,'sources':sources,'coverage':{'current_station_index_count':len(current),'appliance_index_count':len(fleet),'detail_pages_visited':visited,'detail_page_failures':failed,'complete_appliance_inventory':len(visited)==len(fleet)}}
 (ROOT/'data').mkdir(exist_ok=True);(ROOT/'data/reference.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
