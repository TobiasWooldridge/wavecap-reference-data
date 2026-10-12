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
