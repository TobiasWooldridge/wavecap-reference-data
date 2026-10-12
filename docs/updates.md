# Updating references

Refresh a specific source deliberately, preserve its source licence, review the
diff and update catalog hashes/counts/dates. A review date must never replace an
unknown original retrieval date. Retain original vintage and ambiguity.

Fire importer (stdlib; one uncached request per second, no images):

```sh
python3 import_reference.py --service SACFS --limit 794
python3 import_reference.py --service SAMFS --limit 60
python3 build_bundles.py
```

Cache defaults to a sibling `cache/` directory outside this repository. Override
with `WAVECAP_REFERENCE_CACHE` to reuse a retained cache. Without `--refresh`,
previously fetched pages are reused. Each agency snapshot remains separate;
combined JSON is built atomically. The default detail limit is zero (index-only),
so use the explicit bounded detail limit for a complete snapshot. Validation
rejects unexpected page identity/layout and records malformed detail rows.

The OSM and government TSVs were imported from already documented reference
snapshots, not regenerated for this publication. Their original header hashes,
source URLs, row structure and vintage remain. For a refresh, use the primary
source and recorded transform: OSM regional extract plus containing ABS locality
polygons; named streets use the dominant connected cluster (2km linkage,90% share)
and median representative point within the region bounding box; retirement venues
require exact registration/name/address/locality agreement between register and
spatial companion. Keep derived ODbL databases separate from CC fire references.

Official map-book files are extracted unchanged from the linked DEW ZIPs; only
the GDA2020 variant is included, with declared EPSG:7844 CRS and original licence.
Do not reinterpret the grid as commercial UBD, or assume book editions are current.

Confirmed radio records require explicit confirmation provenance, exact network
and source scope, confirmation date and declared validity. No range expansion,
last-digit decoding, inferred callsign evidence or missing public-source URL may
be turned into a verified allocation. Preserve full names and external reference
joins separately from compact presentation labels.

After changes run the focused offline validators and regressions, review source,
licensing and privacy, then commit and pin the new consumer commit. Application
updates consume a reviewed commit; they never silently follow an unpinned branch.

Keep source outputs in their declared geographic scope. Shared importers stay at
the root: fire writes agency snapshots and combined JSON beneath
`data/australia/south-australia/fire/`, and the SA Scan importer writes beneath
`data/australia/south-australia/radio/`. `build_bundles.py` still produces the
stable root `bundles/` consumer paths. Update `catalog.json` paths, hashes and
`geographic_scope` together when adding a dataset. Country/subdivision codes
are ISO codes; worldwide references use `{"coverage":"global"}`.

The first geography migration preserves all source and bundle bytes from
`cda3b32c67a915231175a7a6922856f192506114`. Its historical file inventory and
hashes are in `docs/path-migration.json`. At the migration revision,
`python3 verify_layout.py --check-migration` proves moved-file bytes against
that baseline; future intentional source refreshes need not match these
historical hashes. `python3 verify_layout.py` checks the current scope/layout.
Rebuilding with `python3 -c 'import import_reference; import_reference.bundle()'`
and `python3 build_bundles.py` is offline; neither command fetches source pages.
