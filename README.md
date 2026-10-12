# WaveCap reference data

Versioned, source-attributed reference data for radio monitoring applications.
This repository separates public factual references from application code and
from live operational evidence. Each dataset keeps its own licence; this is not
one blanket-licensed database.

| Dataset | Location | Licence / source |
| --- | --- | --- |
| CFS/MFS stations, vehicles and types | `data/reference.json`, agency snapshots | Original factual arrangement CC BY-SA4.0; [SACFS Promotions Unit](https://www.fire-brigade.asn.au/); [mixed source notices](RIGHTS.md) |
| Small exact appliance-label bundle | `bundles/unit-labels.v1.json` | CC BY-SA4.0; same per-row source citations |
| SA locality centres and boundary | `datasets/geography/abs/` | [ABS, CC BY4.0](https://www.abs.gov.au/website-privacy-copyright-and-disclaimer) |
| SA places/facilities and regional streets | `datasets/geography/osm/` | [OpenStreetMap contributors, ODbL1.0](https://www.openstreetmap.org/copyright); ABS locality labels separately CC BY4.0 |
| SA retirement-village facility references | `datasets/geography/sa-government/` | [Government of South Australia, CC BY4.0](https://data.sa.gov.au/data/dataset/retirement-villages-register) |
| Official CFS map-book pages/extents | `datasets/geography/dew-mapbook/` | [DEW WaterConnect](https://www.waterconnect.sa.gov.au/Content/Downloads/DEW/MAPS_CfsMapBookPages_geojson.zip), archive CC BY4.0 notice retained |
| Archived SA Scan factual talkgroups | `datasets/radio/`, `bundles/sagrn-talkgroups.v1.json` | [SA Scan archive](https://web.archive.org/web/20251225115143/https://www.sascan.net.au/?page=infPages/GRNTalkgroups); upstream licence unstated, factual contribution scope only |
| Explicit operator RF/unit confirmations | `datasets/radio/operator-confirmed-radio-units.v1.json` | Original factual contributions CC BY-SA4.0; truthful per-record confirmation provenance, no public confirmation URL |
| Maritime identification digits | `datasets/maritime/` | [MIDs](https://github.com/michaeljfazio/MIDs), Apache2.0 licence retained; [ITU factual source](https://www.itu.int/en/ITU-R/terrestrial/fmd/Pages/mid.aspx) |

[Catalog](catalog.json) records namespaces, stable-key limits, hashes, attribution,
source URLs, known dates and validity for every included dataset. Unknown original
retrieval dates remain null; a review date is not silently substituted for them.
[Inventory](docs/inventory.md) records excluded and deferred sources.

The consumer bundle contains exact full names, compact labels, agency, reference
ID and source citations. `MFS 401`, `MFS 321` and `SEAF 34` are display labels;
full names and source identities remain available. Ambiguous names abstain.
A numeric radio ID alone never identifies a vehicle through this bundle.

Read [fire reference contract](docs/fire-reference.md), [typed interface](reference.d.ts),
[update instructions](docs/updates.md) [radio provenance](docs/radio-reference.md), and [parent integration](INTEGRATION.md).
Run `python3 verify.py`, `python3 verify_publication.py`, and
`python3 -m unittest test_reference.py` offline. `python3 build_bundles.py` rebuilds
the small consumer file deterministically from the committed fire snapshot.

This is a snapshot reference, not a dispatch or live availability service.
Public mapped locations are venue/feature references, not incident positions.
CFS map-book data is distinct from commercial UBD/Gregory grids; original GDA2020
coordinates are declared, not relabelled as WGS84.

Photos remain source-page links because the source site's footer CC notice and
copyright page conflict. No photo binaries or copied narrative descriptions are
included. No raw audio, incident transcripts, live inference/evidence databases,
credentials or private conversation contents belong here. Confirmed radio/unit
records, when included, are explicitly curated confirmations with scoped identity
and validity; they are not inferred from traffic or presented as public allocations.
