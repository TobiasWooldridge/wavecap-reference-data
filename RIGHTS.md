# Rights and attribution evidence

Observed 2026-10-12 on https://www.fire-brigade.asn.au/legal.asp and the appliance
and station pages. The site footer links to CC BY-SA 4.0:
https://creativecommons.org/licenses/by-sa/4.0/ .

The same legal page's Copyright section restricts downloading/display to private
noncommercial purposes, describes written permission for other reproduction,
and attributes photos/descriptive content to CFS Promotions Unit unless otherwise
specified. This contradicts the broad footer. No page-specific newer licence
was found on the inspected appliance pages that resolves that conflict. Photo
credits on the Seaford page include Emergency Media SA and Emergency Services
Adelaide, as well as CFS Promotions Unit. Credit alone is not a licence.

This repository independently structures factual identifiers, names, models,
registrations and numerical capacities, with source links and hashes. It excludes
source prose, database schema, artwork and photo binaries. The project's own
arrangement and contributions in data/australia/south-australia/fire/reference.json are licensed CC BY-SA 4.0;
third-party rights are not relicensed or represented as conclusively cleared.
Importer/validator code is MIT (LICENSE-CODE). Photo records follow the decision
below; do not turn any other photo record into an affirmative media permission.

# Photo decision 2026-10-17

Decision by the repository owner (relayed in SDR task 1560), after reviewing the
site: every appliance photo on fire-brigade.asn.au is used under the site's
CC BY-SA 4.0 notice. Attribution keeps the photo's own credit exactly as the site
captions it, plus fire-brigade.asn.au, the source page and the licence, e.g.
"Photo: Braeden Gatt via fire-brigade.asn.au · CC BY-SA 4.0".

Evidence, re-fetched 2026-10-17:

- Every page's sidebar (not the footer, as the 2026-10-12 note above says):
  "This work is licensed under a Creative Commons Attribution-ShareAlike 4.0
  International License", linking https://creativecommons.org/licenses/by-sa/4.0/ .
- https://www.fire-brigade.asn.au/legal.asp, Copyright section, which was
  considered and set aside by this decision: "the Site Owner grants visitors to
  the site a licence to download and display its copyright material for private
  and non-commercial purposes only. Written permission for reproduction or use of
  the copyrighted material beyond this limited licence will be granted to persons
  who apply for such ... All Photographs are © Copyright CFS Promotions Unit
  unless otherwise specified."
- Appliance pages caption each photo "Picture by <credit>". At this snapshot
  1,111 of 1,274 listings have a captioned photo (1,101 distinct images); 317 are
  credited "CFS Promotions Unit" and 794 to 168 other credits (photographers,
  media units, brigades and regions). None is uncredited. One caption ("Region 6
  Air Support Trailer") appears twice; the listing keeps the first photo and
  that photo's credit.

Per-row `photo.rights_status` is `cc-by-sa-4.0-sidebar` (with `image_url`,
`credit` as captioned and `license=CC-BY-SA-4.0`) or `no-photo` (163 rows).

`media/australia/south-australia/fire/thumbnails/` holds 224x160 WebP
thumbnails of those photos. They are adaptations (centre-cropped and resized)
shared under CC BY-SA 4.0; `thumbnails.json` lists each with its credit, source
page, source image and hash. Originals are not committed.
`verify_publication.py` allows no other image files.

# Additional source scopes

See catalog.json for dataset-specific licences. ABS/SAgovernment/DEW references
retain CC BY4.0 attribution; separate OSM-derived databases retain ODbL1.0 and
ABS locality attribution; maritime MID data retains Apache2.0. SA Scan archived
page has no explicit upstream reuse licence in the retained page: only original
arrangement of factual IDs/short labels is contributed, without asserting an
upstream grant. Operator confirmations are independently curated contributions
with no invented public source URL. No mixed blanket relicensing occurs.
