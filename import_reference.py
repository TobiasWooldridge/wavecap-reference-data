#!/usr/bin/env python3
"""Bounded, cached, agency-separated factual import. No image fetching."""
import argparse, datetime, hashlib, html, json, os, pathlib, re, time, urllib.parse, urllib.request
BASE = 'https://www.fire-brigade.asn.au/'
ROOT = pathlib.Path(__file__).resolve().parent
CACHE = pathlib.Path(os.environ.get('WAVECAP_REFERENCE_CACHE', ROOT.parent / 'cache'))
SERVICES = {'SACFS': 'sacfs', 'SAMFS': 'samfs'}
NULLABLE_FACTS = {'make_model', 'registration', 'water_litres', 'foam_litres', 'source_updated_text'}

def text(value):
    return ' '.join(html.unescape(re.sub('<[^>]*>', ' ', value)).split())

def fetch(path, refresh=False):
    url = urllib.parse.urljoin(BASE, path)
    file = CACHE / (hashlib.sha256(url.encode()).hexdigest() + '.html')
    CACHE.mkdir(parents=True, exist_ok=True)
    if refresh or not file.exists():
        time.sleep(1)
        request = urllib.request.Request(url, headers={'User-Agent': 'CFSReference/1.0 (cached factual reference; no image download)'})
        file.write_bytes(urllib.request.urlopen(request, timeout=45).read())
    raw = file.read_bytes()
    return raw.decode('utf-8', errors='replace'), {
        'url': url, 'sha256': hashlib.sha256(raw).hexdigest(),
        'retrieved_at': datetime.datetime.fromtimestamp(file.stat().st_mtime, datetime.timezone.utc).isoformat(),
        'rights_status': 'conflicting-notices',
        'attribution': 'SACFS Promotions Unit; individual photo credits remain on source page',
    }

def links(source, kind, service):
    result = {}
    for href, label in re.findall(r'<a\s+href=["\']([^"\']+)["\'][^>]*>([^<]*)', source, re.I | re.S):
        if kind + '_Display.asp?' not in href:
            continue
        query = urllib.parse.parse_qs(urllib.parse.urlparse(html.unescape(href)).query)
        if query.get('Service_Code') != [service]:
            continue
        code = query['Station_Code'][0]
        name = text(label)
        number = re.search(r'\(Station (\d+)\)', name)
        result[code] = {
            'id': SERVICES[service] + ':station:' + code,
            'service': service, 'station_code': code, 'name': name,
            'facility_name': re.sub(r'\s*\(Station \d+\)', '', name),
            'station_number': number.group(1) if number else None,
            'source_url': BASE + 'Station_Display.asp?' + urllib.parse.urlencode({'Service_Code': service, 'Station_Code': code}),
        }
    return result

def normalize(appliances):
    """Merge repeated listings; conflicts cannot erase required structure/links."""
    result = []
    identities = {}
    for item in appliances:
        appliance = dict(item)
        if appliance['id'] not in identities:
            identities[appliance['id']] = appliance
            result.append(appliance)
            continue
        previous = identities[appliance['id']]
        for key, value in appliance.items():
            conflicts = previous.get('source_conflicts', {})
            if key in conflicts:
                if value is not None and value not in conflicts[key]:
                    conflicts[key].append(value)
                continue
            if previous.get(key) is None:
                previous[key] = value
            elif value is not None and value != previous[key]:
                previous.setdefault('source_conflicts', {})[key] = [previous[key], value]
                # Required structural fields retain the first source variant;
                # consumers can see both alternatives in source_conflicts.
                if key in NULLABLE_FACTS:
                    previous[key] = None
    return result

def write_json(path, value):
    path.parent.mkdir(exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(path)

def bundle():
    snapshots = [json.loads(path.read_text()) for path in sorted((ROOT / 'data').glob('*.agency.json'))]
    coverage = {key: sum(s['coverage'][key] for s in snapshots) for key in ('current_station_index_count', 'appliance_index_count')}
    coverage.update({
        'detail_pages_visited': [entry for s in snapshots for entry in s['coverage']['detail_pages_visited']],
        'detail_page_failures': [entry for s in snapshots for entry in s['coverage']['detail_page_failures']],
        'complete_appliance_inventory': all(s['coverage']['complete_appliance_inventory'] for s in snapshots),
        'by_service': {s['service']: s['coverage'] for s in snapshots},
    })
    result = {'schema_version': 1, 'data_license': 'CC-BY-SA-4.0',
              'third_party_rights': 'See RIGHTS.md; no photo or prose redistribution licence inferred',
              'coverage': coverage}
    for key in ('stations', 'appliances', 'classes'):
        result[key] = [entry for snapshot in snapshots for entry in snapshot[key]]
    result['sources'] = list({source['url']: source for snapshot in snapshots for source in snapshot['sources']}.values())
    write_json(ROOT / 'data/reference.json', result)

def import_service(service, limit, refresh):
    namespace = SERVICES[service]
    sources = []
    source, provenance = fetch('Station_Find.asp?' + urllib.parse.urlencode({'Station_Name': '', 'Service_Code': service, 'btnLogin': 'Find Stations'}), refresh)
    sources.append(provenance)
    current = links(source, 'Station', service)
    source, provenance = fetch('vehicles/Appliance_Find.asp?' + urllib.parse.urlencode({'Station_Name': '', 'Service_Code': service, 'btnLogin': 'Find Appliances'}), refresh)
    sources.append(provenance)
    fleet = links(source, 'Station', service) | links(source, 'Appliance', service)
    if not current or not fleet:
        raise ValueError('source index has no expected agency entries; refusing destructive empty import')
    stations = []
    for code in sorted(set(current) | set(fleet)):
        station = dict(current[code] if code in current else fleet[code])
        station.update(listed_in_current_station_index=code in current, listed_in_appliance_index=code in fleet,
                       record_kind='station_or_group_or_region', operational_status='unknown')
        stations.append(station)
    classes = ([{'id': 'sacfs:class:34', 'name': '34', 'water_litres_typical': 3000, 'drive': '4WD',
                 'variants': ['34R', '34P', '34URP'], 'source_url': BASE + 'vehicles/vehicles/sacfs-34.asp',
                 'equipment_varies_by_appliance': True}]
               if service == 'SACFS' else
               [{'id': 'samfs:class:PUMPER', 'name': 'Pumper', 'water_litres_typical': 1200,
                 'source_type_codes': ['1', '2', '11', '12'], 'source_url': BASE + 'about-anyone/vehicles/samfs/samfs-pumper.asp',
                 'equipment_varies_by_appliance': True}])
    appliances, failures, visited = [], [], []
    def checkpoint():
        coverage = {'current_station_index_count': len(current), 'appliance_index_count': len(fleet),
                    'detail_pages_visited': visited, 'detail_page_failures': failures,
                    'complete_appliance_inventory': len(visited) == len(fleet) and not failures}
        write_json(ROOT / ('data/' + namespace + '.agency.json'), {
            'schema_version': 1, 'service': service, 'data_license': 'CC-BY-SA-4.0',
            'stations': stations, 'appliances': normalize(appliances), 'classes': classes,
            'sources': sources, 'coverage': coverage,
        })
        bundle()
    preferred = ('SEAF', 'SLSB') if service == 'SACFS' else ('40', '32')
    codes = sorted(fleet, key=lambda code: (code not in preferred, code not in current, code))[:limit]
    for code in codes:
        station_id = namespace + ':station:' + code
        url = 'vehicles/Appliance_Display.asp?' + urllib.parse.urlencode({'Service_Code': service, 'Station_Code': code})
        try:
            source, provenance = fetch(url, refresh)
        except Exception as error:
            failures.append({'station_id': station_id, 'error': str(error)})
            continue
        sources.append(provenance)
        valid = ('Vehicles &amp; Appliances' in source and 'Appliances - ' in source
                 and re.search(r'name="Station_Code"\s+value="' + re.escape(code) + r'"', source, re.I)
                 and re.search(r'name="Service_Code"\s+value="' + service + r'"', source, re.I))
        if not valid:
            failures.append({'station_id': station_id, 'error': 'unexpected detail layout or station/service identity'})
            continue
        visited.append(station_id)
        updated = re.search(r'last updated on\s*([^<]+)', source, re.I)
        credits = {text(name): text(credit) for name, credit in re.findall(r'<BR>\s*([^<]+)<BR>\s*Picture by ([^<]+)', source, re.I)}
        blocks = re.split(r'<TD WIDTH="25%"[^>]*>', source.split('Vehicles &amp; Appliances', 1)[1], flags=re.I)[1:]
        for block in blocks:
            name = text(block.split('</TD>', 1)[0])
            match = re.search(r'<a\s+Href="([^"]+)">([^<]+)</a>\s*<br>Make and Model:\s*(.*?)\s*<FONT', block, re.I | re.S)
            if not match:
                failures.append({'station_id': station_id, 'error': 'unparsed appliance row'})
                continue
            flat = text(block)
            registration_match = re.search(r'Registration Number:\s*([A-Za-z0-9 -]+?)(?:\s+Equipment:|$)', flat)
            registration = registration_match.group(1).strip() if registration_match else None
            listing_key = namespace + ':appliance:' + code + ':' + re.sub('[^A-Z0-9]+', '-', name.upper()).strip('-')
            suffix = (re.sub('[^A-Z0-9]+', '-', registration.upper()).strip('-') if registration else
                      'UNREGISTERED-' + hashlib.sha256((name + '|' + match.group(1)).encode()).hexdigest()[:12].upper())
            facility = (current[code] if code in current else fleet[code])['facility_name']
            cfs_suffix = name[len(facility):].strip() if name.startswith(facility + ' ') else None
            vehicle_code = cfs_suffix if service == 'SAMFS' and cfs_suffix and cfs_suffix.isdecimal() else None
            compact = ('MFS ' + vehicle_code if vehicle_code else 'MFS ' + name) if service == 'SAMFS' else (code + ' ' + cfs_suffix if cfs_suffix else name)
            class_name = pathlib.PurePosixPath(match.group(1)).stem.removeprefix(namespace + '-').upper()
            record = {
                'id': listing_key + ':' + suffix, 'listing_key': listing_key,
                'id_stability': 'registration-aware-listing' if registration else 'provisional',
                'service': service, 'station_id': station_id, 'name': name, 'full_label': name,
                'compact_label': compact, 'vehicle_code': vehicle_code,
                'vehicle_role': text(match.group(2)).split(' (', 1)[0],
                'registration': registration, 'source_updated_text': text(updated.group(1)) if updated else None,
                'make_model': text(match.group(3)) or None, 'class_id': namespace + ':class:' + class_name,
                'class_source_url': urllib.parse.urljoin(BASE, match.group(1)), 'source_url': provenance['url'],
                'operational_status': 'listed_at_source',
                'photo': {'page_url': provenance['url'], 'credit': credits.get(name), 'rights_status': 'conflicting-notices',
                          'redistribution_allowed': None, 'image_url': None},
            }
            for field, label in [('water_litres', 'Water Capacity'), ('foam_litres', 'Foam Quantity')]:
                capacity = re.search(label + r':\s*(\d+)\s*Litres', flat)
                record[field] = int(capacity.group(1)) if capacity else None
            appliances.append(record)
        print(service, code, len(appliances), flush=True)
        if len(visited) % 25 == 0:
            checkpoint()
    for path in ['legal.asp', classes[0]['source_url']]:
        _, provenance = fetch(path, refresh)
        sources.append(provenance)
    if service == 'SAMFS':
        # Navigation evidence only: this template page must not become a facility.
        _, provenance = fetch('Station_Display.asp?Service_Code=SAMFS&Station_Code=80', refresh)
        sources.append(provenance)
    checkpoint()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--service', choices=SERVICES, default='SACFS')
    parser.add_argument('--limit', type=int, default=0, help='maximum detail pages; 0 indexes only')
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    import_service(args.service, args.limit, args.refresh)

if __name__ == '__main__':
    main()
