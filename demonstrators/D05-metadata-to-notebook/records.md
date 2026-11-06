# D5 dataset records

Where the D5 datasets are described, what their distributions point to, and
what is at the other end. Checked on 2026-11-06.

## Where the records are

The VP Index (`https://index.vp.ejprarediseases.org`, `/index/entries/all`)
lists `https://w3id.org/ejp-rd/fairdatapoints/wp13` as ACTIVE. It resolves to
`https://wp13.fdps.ejprd.semlab-leiden.nl/`. The CAKUT datasets are in its
catalog "Catalog for CAKUT"
(`…/wp13/catalog/4cad6f79-a7e1-46ef-8706-37f942f4aaea`). The Huntington
datasets are in the catalog "BYOD" (`…/wp13/catalog/bf209b8a-eb67-4f35-864f-6d02228e1d91`).
The Index also lists `https://wp13.fdps.ejprd.semlab-leiden.nl/` itself as
INACTIVE, so the same FDP has two entries.

Six of the FDP's 21 catalogs do not resolve (five 404, one 403).

## Records

All IRIs below start with `https://w3id.org/ejp-rd/fairdatapoints/wp13/`.

### EJPRD WP13 CAKUT mirnome (alternative for D5)

| | |
| --- | --- |
| Dataset | `dataset/0d2930d7-933d-4a5f-86e4-05e9537a18a0` |
| Distribution | `distribution/db0ba7b6-933e-472a-bf32-5e17cd14b89f` |
| `dcat:downloadURL` | <https://zenodo.org/record/7866785/files/CAKUT_miRNA.xlsx?download=1> |
| `dcat:accessURL` | <https://zenodo.org/record/7866785> |
| Data end | Zenodo 10.5281/zenodo.7866785, open, CC BY 4.0, one file `CAKUT_miRNA.xlsx`, 816,974 bytes |
| Contents | sheets Background, Metadata (one row per sample), Experimental information, Data matrix (503 miRNAs × 137 samples, RMA-normalised) |
| Groups | `characteristics: group` on the Metadata sheet: Non-severe CAKUT 58, Severe CAKUT 29, CAKUT 29, Control (non-CAKUT) 21 |

### EJPRD WP13 CAKUT proteome

| | |
| --- | --- |
| Dataset | `dataset/ff86604c-e9a2-4671-85d4-05708a07a0e5` |
| Distribution | `distribution/d84236e1-085f-454b-901e-5c8ca278c032` |
| `dcat:downloadURL` | none |
| `dcat:accessURL` | <http://proteomecentral.proteomexchange.org/cgi/GetDataset?ID=PXD022926> (resolves, via two redirects) |
| Data end | PRIDE PXD022926, CC0, 30 files, about 102.7 GB: 29 Thermo `.raw` files of 1.5–1.9 GB and `MaxQuant_workflow.7z` (1 MB). No processed table. |

Not usable for a five-minute notebook: no download URL in the record, and no
processed data at the other end.

### EJPRD WP13 CAKUT peptidome

| | |
| --- | --- |
| Dataset | `dataset/d55ad1fa-1a87-4f3e-b841-c0655aaa2785` |
| Distribution | `distribution/77d674bd-20e3-4fc5-a42a-9b3ed347403a` |
| `dcat:downloadURL` | none |
| `dcat:accessURL` | <https://doi.org/10.5281/zenodo.10497903> |
| Data end | Zenodo, open, CC BY 4.0, `CAKUT_peptide.xlsx`, 6,253,314 bytes |

Usable data, but the record only has an access URL to the landing page, so
the notebook cannot reach the file from the metadata.

### Huntingtons disease transcriptomics (chosen for D5)

| | |
| --- | --- |
| Dataset | `dataset/22238845-1213-43f6-a60f-e84cdc9fa2ed` |
| Distributions | `distribution/9f91a17c-905a-4487-9ee2-57502fa7a452` (download), `distribution/4b8215da-e58a-4465-ada1-ab09c90618a2` (access) |
| `dcat:downloadURL` | <https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE64810&format=file&file=GSE64810%255Fmlhd%255FDESeq2%255Fnorm%255Fcounts%255Fadjust%252Etxt%252Egz> |
| `dcat:accessURL` | <https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE64810> |
| Data end | GEO GSE64810. The download URL redirects to `GSE64810_mlhd_DESeq2_norm_counts_adjust.txt.gz`, 12,679,694 bytes (30 MB unpacked) |
| Contents | tab-separated DESeq2-normalised counts, 28,087 genes × 69 samples; names start `C_` (49 controls) or `H_` (20 Huntington) |

### Huntington disease mRNA

| | |
| --- | --- |
| Dataset | `dataset/049e99aa-0794-4331-8a50-d4cee8641c0f` |
| `dcat:downloadURL` | <https://ftp.ncbi.nlm.nih.gov/geo/series/GSE3nnn/GSE3790/matrix/GSE3790-GPL96_series_matrix.txt.gz>, 25,747,831 bytes |

A GEO series matrix (microarray, `!`-prefixed header block). Larger and
harder to load than GSE64810, so not used.

### IBM expression datasets (README fallback, not needed)

`dataset/25e903e5-…` (gene expression normalised) and `dataset/aaed392c-…`
(miRNA normalised) in the "Inclusion Body Myositis datasets" catalog. Both
have download URLs to GEO (GSE151757, GSE151756) and remain a fallback.

## Choice

Huntington disease transcriptomics (GSE64810) is the notebook default,
decided by Luiz on 2026-11-06. Its record has a `dcat:downloadURL`, the file
is a single 12.7 MB open download, and the sample names carry the HD versus
control split. The data are from Labadorf et al., PLoS One 2015 (PMID
26636579): 20 HD and 49 control prefrontal cortex (BA9) samples.

The CAKUT mirnome is the alternative, set by the commented block in the
parameters cell. It is the only CAKUT record with a `dcat:downloadURL`, and
the workbook carries its own sample sheet.

### Licence of what is committed

The rule is to go by the licence of the repository that holds the data, not
by the FDP record, and to report the record when the two differ. For GSE64810
the record says CC BY-NC 4.0 and NCBI places no restrictions on GEO data.
Either way, a derived figure may be redistributed with attribution, so the
executed notebook, the figure and the PROV record are committed under
`output/`. The same would hold for the CAKUT mirnome (Zenodo, CC BY 4.0).

## Metadata issues to raise

These are worth showing in the recording, and worth reporting to the WP13
FDP maintainers.

1. **Licence.** Every WP13 CAKUT record says `dct:license
   <http://rdflicense.appspot.com/rdflicense/cc-by-nc-nd3.0>`. Zenodo says CC
   BY 4.0 for the mirnome and peptidome, and PRIDE says CC0 for the proteome.
   The record is more restrictive than the data. The same CC BY-NC-ND 3.0
   value is on 15 of the 24 dataset records in this FDP, which suggests a
   populator default.
2. **Publisher.** On the CAKUT records the publisher's `foaf:name` is the
   ORCID URL `https://orcid.org/0000-0002-0637-9950`, not a name. On the
   Huntington records the publisher IRI is
   `file:///home/runner/work/ejprd-wp13-metadata/ejprd-wp13-metadata/fdp-populator/scripts/`,
   a path leaked from the populator's CI run, with `foaf:name "NCBI"`.
3. **Media types.** The mirnome distribution says `application/vnd.ms-excel`
   (that is `.xls`) for an `.xlsx`. The Huntington distributions say
   `text/csv` for a gzipped tab-separated file.
4. **Missing download URLs.** The proteome and peptidome records have only an
   access URL to a landing page, although the peptidome file is a plain open
   download.
5. **Typos in keywords.** "amniotic fluit" (CAKUT), "Hungtington disease",
   "trancriptomics".
