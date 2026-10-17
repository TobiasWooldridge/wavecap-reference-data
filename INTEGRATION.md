# Pinned parent integration and consumer contract

Intended public origin: `https://github.com/TobiasWooldridge/wavecap-reference-data.git`.
The SDR parent convention is a top-level git submodule. Proposed path is
`wavecap-reference-data/`; source publication and parent integration are separate
commits, both reviewable. The sole parent publisher applies the reviewed gitlink.

```sh
git submodule add https://github.com/TobiasWooldridge/wavecap-reference-data.git wavecap-reference-data
git -C wavecap-reference-data checkout <reviewed-public-commit>
python3 wavecap-reference-data/verify.py
python3 wavecap-reference-data/verify_publication.py
```

Stage `.gitmodules` and the gitlink together. Never follow an unpinned branch in a
build or copy datasets into a blanket application-code licence.

Use `bundles/unit-labels.v1.json` for the small fire-label import. Rows contain
`service`, `full_label`, `compact_label`, `station_id`, `source_url`,
`source_updated_text`, stable named `reference_id`, and physical-source
`reference_ids`. Multiple registrations may share a named unit if agency/station/
compact label agree. Truly ambiguous names abstain. Match only exact full source
names after case/whitespace normalization, within the application's verified
source scope; numeric IDs alone never match.

`St Marys 401` → `MFS 401` (samfs:station:40); `Salisbury 321` → `MFS 321`
(samfs:station:32); `Seaford 34` → `SEAF 34` (sacfs:station:SEAF).
Role names remain: `Car 40` → `MFS Car 40`, `Hooklift 01` → `MFS Hooklift 01`,
`Surge 01` → `MFS Surge 01`; fireboat names keep their role/name. CFS names do
not acquire an extra CFS prefix. Full source labels remain canonical detail text.

`bundles/sagrn-talkgroups.v1.json` is a historical reference seed only. Join on
exact configured source `sagrn` and decimal TGID; do not confuse channel numbers
or legacy numbers inside a label. Existing configured/curated and verified
operator overrides retain precedence. Four conflicting archived IDs are omitted
from this seed and retained in the full source dataset. Preserve publisher,
original/archive citation and capture/update dates in consumers.

`data/australia/south-australia/radio/operator-confirmed-radio-units.v1.json` contains six explicitly
curated confirmations, exact source/radio scope and per-record validity. It is
not a live database export or a permanent assignment claim. Three older records
have unknown bounds. Do not infer station role/appliance type for Adelaide Fire
or the older confirmations. Do not expand neighbouring IDs or transfer mappings
across systems. Public confirmation URLs are unavailable, explicitly null.

For richer metadata, use exact `lookup.py --station-id samfs:station:40
--vehicle-code 401` or the typed fire contract. Missing per-vehicle specs remain
null; typical class figures are never a substitute. Photos are source-page links
with credit and a CC BY-SA 4.0 thumbnail when the listing has a photo
(RIGHTS.md, photo decision 2026-10-17).
Geography stays in its separately licensed database, with source CRS/vintage.

Source organization is geography-first. The fire snapshot is
`data/australia/south-australia/fire/reference.json`; archived and confirmed
SA-GRN sources are in `data/australia/south-australia/radio/`. Existing root
`bundles/` filenames and their contents remain compatible. Read catalog
`geographic_scope` when discovering datasets: root bundle paths do not imply
worldwide coverage. Source paths changed from the original public snapshot;
[the migration manifest](docs/path-migration.json) records every moved file and
its original SHA-256 at the baseline commit.
