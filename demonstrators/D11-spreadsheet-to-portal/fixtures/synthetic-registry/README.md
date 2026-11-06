# Fixture 1 · a fictional patient-organisation registry

One TSV per sheet of the ERDERA resource metadata template, filled for a
fictional organisation. Everything carries the word SYNTHETIC in its title so
it can never be mistaken for a real resource, and it is only ever registered in
the demo index on the testbed.

| File                 | Template sheet   | Rows |
| -------------------- | ---------------- | ---- |
| Organisation.tsv     | Organisation     | 1    |
| ContactPoint.tsv     | ContactPoint     | 1    |
| PatientRegistry.tsv  | Patient registry | 1    |
| Catalog.tsv          | Catalog          | 1    |

Deliberate choices, so the FDPlight import is exercised:

- `Publisher`, `Contact Point` and `Dataset` reference other rows by their
  `Title`, as the template does. The import must resolve them to minted IRIs.
- `VPConnection` is empty on the registry and set on the catalog. The import
  must default the empty one to `ejp:VPDiscoverable`.
- `Theme` and `Keyword` hold comma-separated values.
- `Personal Data` is `true` on the registry and `false` on the catalog.

Expected import result: zero red counts.

The theme is `http://www.orpha.net/ORDO/Orphanet_93545`, "Renal or urinary
tract malformation". ORDO has no single class named CAKUT. 93545 is the group
that covers it, syndromic forms included. Its child `Orphanet_93546`
("Non-syndromic renal or urinary tract malformation") was the earlier
placeholder. Checked against ORDO in EBI OLS on 2026-11-06.

Column headers follow the per-sheet template documentation. The official
`.xlsx` template could not be downloaded when this fixture was written, so the
values should also be copied into that workbook and both forms kept here.
