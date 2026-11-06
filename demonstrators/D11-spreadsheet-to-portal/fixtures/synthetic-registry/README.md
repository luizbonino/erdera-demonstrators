# Fixture 1 · a fictional patient-organisation registry

The official ERDERA resource metadata template, filled for a fictional
organisation, in two forms that hold the same values:

- `synthetic-registry.xlsx`, the official workbook with our rows;
- one TSV per sheet, as the template README recommends for export.

Everything carries the word SYNTHETIC in its title so it can never be mistaken
for a real resource, and it is only ever registered in the demo index on the
testbed.

| File                 | Template sheet  | Rows |
| -------------------- | --------------- | ---- |
| Organisation.tsv     | Organisation    | 1    |
| ContactPoint.tsv     | ContactPoint    | 1    |
| PatientRegistry.tsv  | PatientRegistry | 1    |
| Catalog.tsv          | Catalog         | 1    |

The other resource sheets of the workbook (Biobank, Guideline, Dataset,
Distribution, DataService) are empty. Mediatypes and Languages are the
template's lookup lists, not resource types.

## The template, as it really is

Checked against the workbook at ejp-rd-vp/resource-metadata-schema commit
`74df189` (2023-11-10, CC0) on 2026-11-06. It differs from the per-sheet
documentation in ways an importer has to handle.

- Sheet names have no spaces (`PatientRegistry`, `DataService`), nor do most
  headers (`LandingPage`, `ContactPoint`, `PersonalData`,
  `PopulationCoverage`, `AccessRights`). The ODRL column is `ODRL Policy` on
  some sheets and `ODRLPolicy` on others.
- The ContactPoint sheet has one column, `URL`. A resource's `ContactPoint`
  cell holds that URL; there is no title to point to.
- `Publisher` points to an Organisation `Title`. Catalog `Dataset` points to
  the `Title` of a dataset, patient registry or biobank. `Distribution`,
  `IsPartOf`, `AccessService` and `ServesDataset` point to titles too.
- Row 2 of every resource sheet comes pre-filled with only `VPConnection`
  set to `http://purl.org/ejp-rd/vocabulary/VPDiscoverable`. That row is not
  a resource, and that IRI is not the one the ERDERA shapes use
  (`https://w3id.org/ejp-rd/vocabulary#VPDiscoverable`).
- The example row separates keywords with `|`.
- `Issued` and `Modified` are dates; the ERDERA shapes want `xsd:dateTime`.
- `PersonalData` has no field in the ERDERA patient registry or catalog
  shapes. `Keyword` is optional in the template but required by the shapes.
- `build_xlsx.py` also has to clear Excel hyperlinks: the template's URLs
  are hyperlinks that openpyxl writes back as values otherwise.

## Deliberate choices, so the import is exercised

- `Publisher` and catalog `Dataset` reference other rows by `Title`, and
  `ContactPoint` by URL. The import must resolve them.
- `VPConnection` is empty on the registry and set on the catalog to the
  template's own `purl.org` value. Empty must become `ejp:VPDiscoverable`, and
  the `purl.org` form must be read as the same thing.
- `Keyword` uses `|` on the registry and `,` on the catalog.
- `PersonalData` is `true` on the registry and `false` on the catalog, with
  no field to go to. The import must report it, not drop it silently.
- `Language` is the two-letter code, as the template's list offers it.

Expected import result: zero red counts on the imported catalog and registry.

The theme is `http://www.orpha.net/ORDO/Orphanet_93545`, "Renal or urinary
tract malformation". ORDO has no single class named CAKUT. 93545 is the group
that covers it, syndromic forms included. Its child `Orphanet_93546`
("Non-syndromic renal or urinary tract malformation") was the earlier
placeholder. Checked against ORDO in EBI OLS on 2026-11-06.

## Regenerating the xlsx

The TSVs are the source. After changing one, run `python build_xlsx.py`
(needs openpyxl and network access) and commit both.
