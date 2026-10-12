# Reviewable integration recipe

Prepared checkout: `/home/thw/cfs-reference/checkout/datarepo` on Dana4.
No remote exists and no publisher checkout has been modified. SDR's established
convention is a top-level git submodule named for its repository, so the proposed
path is `cfs-reference/`.

For an isolated local integration review, the parent integrator can run:

```sh
git -c protocol.file.allow=always submodule add /home/thw/cfs-reference/checkout/datarepo cfs-reference
git -C cfs-reference checkout <reviewed-commit>
python3 cfs-reference/verify.py
```

The absolute file URL is **local review only**. Before publishing a parent commit,
replace `.gitmodules` URL with the separately approved repository URL, and confirm
that the reviewed data commit exists there. This worker has not created a public
remote. Stage `.gitmodules` and `cfs-reference` gitlink together. No application
code licence change is necessary: retain LICENSE-DATA/RIGHTS alongside data.

## Selective hovercard adapter

Offline example (no browser/network/image side effects):

```sh
python3 cfs-reference/lookup.py --station-id sacfs:station:SEAF --appliance-name 'Seaford 34'
python3 cfs-reference/lookup.py --station-id sacfs:station:SLSB
python3 cfs-reference/lookup.py --station-id samfs:station:40 --vehicle-code 401
python3 cfs-reference/lookup.py --station-id samfs:station:32 --vehicle-code 321
```

Application-local, explicitly verified identity mappings can point at `station.id`
and `appliance.id` (Seaford 34: `sacfs:appliance:SEAF:SEAFORD-34:S659AQX`).
`listing_key` is a station/name grouping, not a guaranteed unique vehicle. IDs
always include the public registration when known; unregistered IDs are provisional. Keep those mappings outside this public repository. The
adapter result contains station, exact matching appliance records, attribution,
licence and whether that station detail page has been imported. An empty
appliance list with `detail_page_imported=false` is incomplete coverage, not proof
that the station has no vehicles.

Display name, per-vehicle make/model and water/foam capacities when present.
Do not substitute typical class figures for missing per-vehicle fields. Photo
presentation is a source-page link labelled “Vehicle photos and source”, with
credit if available. `image_url` is null, and no binary is licensed here. Use
accessible link text and avoid a blank image placeholder. Station icon remains
fixed; vehicle type metadata is independent of station identity. Class 34 is a
shared category, not the identifier of a unique vehicle.

SAMFS40 is St Marys, vehicle401 is its source-listed pumper. Vehicle409 is
a separate pumper-rescue, not a synonym. SAMFS32 Salisbury and SACFS SLSB Salisbury
are distinct facilities. `compact_label` is ready for display (`MFS 401`, `MFS 321`,
`SEAF 34`); keep full_label/source/rights available in detail views. No private RF
identifier joins are provided. Suppress disputed fields listed in source_conflicts.
