#!/usr/bin/env python3
"""Small CC BY-SA 4.0 thumbnails for fire appliance photos whose licence is recorded.

Only `photo.rights_status == 'cc-by-sa-4.0-sidebar'` rows are fetched (see
RIGHTS.md). Originals are held in memory only and never written to disk; the
committed thumbnails are adaptations (centre-cropped, resized) shared under the
same licence. A rerun reuses every thumbnail its manifest already records."""
import hashlib, io, json, os, pathlib, time, urllib.request
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent
# Originals an earlier version of this script cached: consumed once, then deleted.
LEGACY_CACHE = pathlib.Path(os.environ.get('WAVECAP_REFERENCE_CACHE', ROOT.parent / 'cache')) / 'photos'
REFERENCE = ROOT / 'data/australia/south-australia/fire/reference.json'
OUTPUT = ROOT / 'media/australia/south-australia/fire/thumbnails'
# Source photos are ~300 px wide; 224x160 stays sharp at 2x density in the card.
SIZE = (224, 160)
# Averages ~8 KB per thumbnail on a sample of the source photos.
QUALITY = 78
LICENSE_URL = 'https://creativecommons.org/licenses/by-sa/4.0/'
ADAPTATION = f'Centre-cropped and resized to {SIZE[0]}x{SIZE[1]} WebP from the source photo'
# Storage bound for every committed thumbnail together.
MAX_TOTAL_BYTES = 25 * 1024 * 1024


def original(url):
    legacy = LEGACY_CACHE / (hashlib.sha256(url.encode()).hexdigest() + pathlib.PurePosixPath(url).suffix)
    if legacy.exists():
        raw = legacy.read_bytes()
        legacy.unlink()
        return raw
    time.sleep(1)
    request = urllib.request.Request(url, headers={'User-Agent': 'CFSReference/1.0 (CC BY-SA thumbnails with attribution)'})
    return urllib.request.urlopen(request, timeout=45).read()


def thumbnail(raw):
    image = Image.open(io.BytesIO(raw)).convert('RGB')
    scale = max(SIZE[0] / image.width, SIZE[1] / image.height)
    image = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left, top = (image.width - SIZE[0]) // 2, (image.height - SIZE[1]) // 2
    out = io.BytesIO()
    image.crop((left, top, left + SIZE[0], top + SIZE[1])).save(out, 'WEBP', quality=QUALITY, method=6)
    return out.getvalue()


def main():
    reference = json.loads(REFERENCE.read_text())
    photos = {}
    for appliance in reference['appliances']:
        photo = appliance['photo']
        if photo['rights_status'] != 'cc-by-sa-4.0-sidebar':
            continue
        entry = photos.setdefault(photo['image_url'], {'credit': photo['credit'], 'page_url': photo['page_url'], 'listing_keys': set()})
        assert entry['credit'] == photo['credit'] and entry['page_url'] == photo['page_url'], photo['image_url']
        entry['listing_keys'].add(appliance['listing_key'])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUTPUT.parent / 'thumbnails.json'
    previous = ({row['image_url']: row for row in json.loads(manifest_path.read_text())['thumbnails']}
                if manifest_path.exists() else {})
    rows = []
    for url, entry in sorted(photos.items()):
        name = pathlib.PurePosixPath(url).stem + '.webp'
        known = previous.get(url)
        if known and (OUTPUT / name).exists() and hashlib.sha256((OUTPUT / name).read_bytes()).hexdigest() == known['sha256']:
            data, source_sha256 = (OUTPUT / name).read_bytes(), known['source_sha256']
        else:
            raw = original(url)
            data, source_sha256 = thumbnail(raw), hashlib.sha256(raw).hexdigest()
            del raw
            (OUTPUT / name).write_bytes(data)
        rows.append({'file': name, 'sha256': hashlib.sha256(data).hexdigest(),
                     'listing_keys': sorted(entry['listing_keys']), 'image_url': url,
                     'source_sha256': source_sha256, 'page_url': entry['page_url'],
                     'credit': entry['credit'], 'publisher': 'fire-brigade.asn.au',
                     'license': 'CC-BY-SA-4.0', 'license_url': LICENSE_URL, 'adaptation': ADAPTATION})
        print(name, len(data), flush=True)
    total = sum((OUTPUT / row['file']).stat().st_size for row in rows)
    assert total <= MAX_TOTAL_BYTES, f'thumbnails total {total} bytes exceeds {MAX_TOTAL_BYTES}'
    stale = {path.name for path in OUTPUT.glob('*.webp')} - {row['file'] for row in rows}
    for name in stale:
        (OUTPUT / name).unlink()
    manifest = {'schema_version': 1, 'source_reference_sha256': hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
                'width': SIZE[0], 'height': SIZE[1], 'license': 'CC-BY-SA-4.0', 'license_url': LICENSE_URL,
                'rights': 'RIGHTS.md#photo-decision-2026-10-17', 'total_bytes': total, 'thumbnails': rows}
    manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + '\n')
    print(f'{len(rows)} thumbnails, {total} bytes; removed {len(stale)} stale')


if __name__ == '__main__':
    main()
