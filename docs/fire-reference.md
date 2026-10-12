# CFS and MFS factual reference

Independent normalized public-source facts from the SACFS Promotions Unit,
https://www.fire-brigade.asn.au/ . The fire dataset contains no radio observations,
RF identifiers, recordings, transcripts, credentials, photo binaries, or copied
narrative descriptions. It is a reference snapshot, not an operational dispatch
or live availability service.

`data/reference.json` is the versioned consumer contract. Attribution must remain
visible: **Source: SACFS Promotions Unit**, linking each record's `source_url`.
See RIGHTS.md before displaying media. Code is MIT; this independently arranged
factual dataset is offered under CC BY-SA 4.0. Neither licence replaces third-party
rights or resolves the source site's inconsistent notices.

Run `python3 import_reference.py --service SACFS --limit 794` for CFS and
`python3 import_reference.py --service SAMFS --limit 60` for MFS. These update
agency snapshots `data/sacfs.agency.json` and `data/samfs.agency.json`, and atomically
rebuild the combined `data/reference.json`. Other agencies are preserved. Default is indexes only, deliberately replacing that agency’s detail coverage with an
explicit incomplete snapshot; review the diff before committing. Requests are
serial, at most one new request per second, cached in a sibling `cache/` directory (override WAVECAP_REFERENCE_CACHE), with a
45-second timeout and no automatic retry storm. `--refresh` refetches selected
pages. No photo requests occur. Raw HTML remains outside the git repository.
A JSON checkpoint is written every 25 successful detail pages, so interrupted
updates retain useful data and the HTML cache. Run `python3 verify.py` after updates. Review coverage/failures and licensing
changes before publishing a new snapshot. Fetch failures are recorded; completeness
is never claimed unless every index entry was visited.

## Consumer contract

- `schema_version`: 1. IDs are namespaced strings, never radio IDs.
- Station IDs: `sacfs:station:<source Station_Code>` or `samfs:station:<code>`. Service is independently
  retained; codes are source identifiers, not assumed callsign abbreviations.
- Appliance IDs are registration-aware source-listing identities. The registration
  suffix is always present when known, so importing another same-named vehicle
  does not change an existing ID. `listing_key` preserves the station/name grouping
  and may match multiple vehicles. These IDs do not claim a permanent chassis
  identity: source name, station or registration changes require re-verification.
  Missing-registration IDs are explicitly `provisional`, derived from name/class.
  Compatible repeated rows merge missing fields. Contradictory nullable numerical/model
  facts become null with alternatives retained in `source_conflicts`; required
  structure/links retain their first source variant and record alternatives.
  Consumers must suppress any disputed field rather than treating the retained
  structural variant as resolved. Do not merge by
  class number alone or treat a named listing_key as unique without checking.
- Full labels retain source names. Compact labels are `SEAF 34` for CFS and
  `MFS 401` for MFS. MFS vehicle codes come from exact public source appliance
  names. Facility numbers come from explicit source “Station” labels. Neither
  a radio ID nor a universal last-digit type splitter is used. Per-class source
  type-code variants are retained separately; individual roles come from their
  own source type links.
- Coverage visit entries are agency-qualified station IDs; `coverage.by_service`
  retains each agency’s completeness/failures separately.
- Station/group/region distinction is not inferred from names. Current station
  index membership and appliance index membership are separate booleans.
  Source indexes disagree in scope; absence does not establish decommissioning.
- Appliance `operational_status=listed_at_source` means source listing only.
  Retrieval time appears in sources; source information may be older.
- `class_id` is a type, e.g. `sacfs:class:34`; class specifications are typical,
  while appliance water/foam/model facts are per listing. Missing values are null.
- `photo.page_url` links to the original source page. `image_url=null` deliberately:
  no hotlink/download permission is inferred. `redistribution_allowed=null` means
  unresolved, not permission. A UI can show a source link immediately; photo
  previews require separately verified per-image rights and credits.
- Equipment is not asserted from typical class lists. Source appliance pages
  remain available for additional factual verification.

## Parent integration

The SDR parent uses git submodules. Proposed path is `cfs-reference/`; pin a reviewed
commit from this independent repository after its public remote is created and
reviewed. Do not copy this dataset into the application-code licence. Read the
JSON during a build/server import, expose only the fields needed for cards, and
retain source/attribution/rights fields. Use explicit application mappings from
private local observations to these public IDs outside this repository. No fuzzy
identity merge: Salisbury CFS, MFS and SES are different services/records.

No parent checkout or publication is changed by the importer. Repository creation,
remote URL and pinned parent gitlink are coordinated by the parent publisher.
