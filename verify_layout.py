#!/usr/bin/env python3
"""Check geographic scopes; optionally prove the original path-only migration."""
import argparse
import hashlib
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
SCOPES = (
    ('data/australia/south-australia/', {'country': 'AU', 'subdivision': 'SA'}),
    ('data/australia/', {'country': 'AU'}),
    ('data/united-states/washington/king-county/',
     {'country': 'US', 'subdivision': 'WA', 'county': 'King County'}),
    ('data/global/', {'coverage': 'global'}),
)


def validate(*, migration=False):
    catalog = json.loads((ROOT / 'catalog.json').read_text())
    ids = [entry['id'] for entry in catalog['datasets']]
    assert len(ids) == len(set(ids)), 'duplicate catalog IDs'
    for entry in catalog['datasets']:
        path = entry['path']
        if path.startswith('bundles/'):
            # Existing v1 bundles are South Australian consumer contracts.
            assert entry['id'] in ('wavecap:fire-unit-labels:v1',
                                   'wavecap:sagrn-talkgroups:v1')
            scope = {'country': 'AU', 'subdivision': 'SA'}
        else:
            scope = next((scope for prefix, scope in SCOPES
                          if path.startswith(prefix)), None)
        assert scope is not None, path
        assert entry['geographic_scope'] == scope, path
        assert (ROOT / path).is_file(), path
        if 'license_notice' in entry:
            assert (ROOT / entry['license_notice']).is_file(), entry['license_notice']
    manifest = json.loads((ROOT / 'docs/path-migration.json').read_text())
    for entry in manifest['files']:
        assert (ROOT / entry['path']).is_file(), entry['path']
        if entry['path'] != entry['old_path']:
            assert not (ROOT / entry['old_path']).exists(), entry['old_path']
    # A split layout must not quietly accumulate new category-first sources.
    assert not any(path.is_file() for path in (ROOT / 'datasets').rglob('*'))
    assert not list((ROOT / 'data').glob('*.json'))
    if migration:
        baseline = manifest['baseline_commit']
        for entry in manifest['files']:
            original = subprocess.check_output(
                ['git', 'show', baseline + ':' + entry['old_path']], cwd=ROOT)
            assert hashlib.sha256(original).hexdigest() == entry['sha256'], entry
            assert (ROOT / entry['path']).read_bytes() == original, entry['path']
        old_catalog = json.loads(subprocess.check_output(
            ['git', 'show', baseline + ':catalog.json'], cwd=ROOT))
        old_paths = {entry['path']: entry['old_path'] for entry in manifest['files']}
        for before, after in zip(old_catalog['datasets'], catalog['datasets'], strict=True):
            restored = dict(after)
            restored['path'] = old_paths[restored['path']]
            restored.pop('geographic_scope')
            restored.pop('license_notice', None)
            assert restored == before, after['id']
        current_data = {str(path.relative_to(ROOT))
                        for path in (ROOT / 'data').rglob('*') if path.is_file()}
        moved_data = {entry['path'] for entry in manifest['files']
                      if entry['path'].startswith('data/')}
        assert current_data == moved_data, current_data ^ moved_data
        print(f"PASS: {len(manifest['files'])} source/bundle/notice files unchanged "
              f"from {baseline}; all catalog facts preserved")
    print(f"PASS: {len(ids)} catalog entries have geographic scopes and valid paths")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-migration', action='store_true',
                        help='compare this migration revision with its original public baseline')
    validate(migration=parser.parse_args().check_migration)
