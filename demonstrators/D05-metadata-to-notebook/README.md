# D5 · From a VP metadata record to a notebook

**Audience.** Biomedical researchers and data scientists.

**Story.** A researcher finds a dataset in the ERDERA Virtual Platform, follows
its metadata to the data, loads it in a notebook and runs a first analysis.
Every URL comes out of the metadata. The point is that FAIR metadata leads to
reusable data, not to a listing.

**What it shows today.** The VP portal's resource list shows the EJPRD WP13
CAKUT datasets and the Huntington disease datasets with no link to their record
or to the data (ProteomeXchange, Zenodo). So the notebook starts one level
below the portal, at the FAIR Data Point record, and the recording calls that
gap out. Closing it is a portal change the DSH group may want to request.

## Layout

```
notebook/d5_metadata_to_notebook.ipynb   the demonstrator, parameterised by DATASET_IRI
src/vpfollow.py                          fetch record, follow distributions, download, PROV
src/firstlook.py                         case-versus-control means on a feature x sample matrix
records.md                               the dataset records, their data ends, metadata issues
fixtures/                                an FDP-shaped dataset + distribution + CSV for tests
tests/test_vpfollow.py                   end-to-end test against a local fixture server
tests/test_firstlook.py                  the group comparison
requirements.txt
```

## Run

```bash
cd demonstrators/D05-metadata-to-notebook
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest                      # runs the chain against local fixtures
jupyter lab notebook/       # Huntington GSE64810 is the default; run all
```

The notebook writes `notebook/downloads/` and `notebook/output/` (figure and
PROV record), both ignored by git. The committed run is in [output/](output/).

## Steps

Done (2026-11-06):

1. Located the dataset records in the EJP RD WP13 FDP
   (`https://w3id.org/ejp-rd/fairdatapoints/wp13`, ACTIVE in the VP Index).
   IRIs and distribution URLs are in [records.md](records.md).
2. Checked the data ends. The CAKUT proteome has no download URL in its
   record, and PXD022926 holds only about 100 GB of raw MS files, so it is out.
   **Huntington disease transcriptomics** (GSE64810, a 12.7 MB open GEO
   download) is the default. The CAKUT mirnome (an 817 KB open Zenodo
   workbook) is the alternative. The IBM fallback was not needed. The licence
   and publisher issues found on the way are listed in `records.md`.
3. Ran the notebook top to bottom from the IRI alone for both datasets
   (Huntington: 28,087 genes, 20 HD vs 49 controls; CAKUT: 503 miRNAs, 116
   CAKUT vs 21 controls). The record and the repository agree that a derived
   figure may be redistributed, so the executed notebook, figure and PROV
   record are committed under `output/`.

Still to do:

4. Register the notebook as a resource in the demo index with FDPlight (ERDERA
   profile), so the recording ends with the analysis itself being findable.
   This needs a public URL for the notebook (this repository on GitHub) and
   the testbed demo index.
5. Record five minutes, portal row to figure, opening with what the portal
   shows and what it does not. Worth showing on the way: the Huntington
   record's publisher IRI, a file path left by the populator script.

## Acceptance

- The notebook runs top to bottom on a clean environment from the dataset IRI
  alone.
- Every URL it follows comes from the metadata, none is typed in.
- `pytest` passes.
- The recording shows the full chain with the missing portal link called out.

## Notes on the code

`vpfollow.follow()` fetches the dataset record with content negotiation and,
for each `dcat:distribution`, fetches the distribution as its own resource when
the dataset graph does not already describe it, which is how an FDP serves
them. `choose()` prefers a distribution with a download URL over one with an
access URL. `download()` streams the file, names it from Content-Disposition
or the URL after redirects (Zenodo and GEO both redirect), and unpacks `.gz`.
`sheets()` lists a workbook's sheets and `load_table()` loads one, or sniffs
the delimiter of a text file. `prov_graph()` writes a PROV-O record naming the
dataset, the distribution, the data URL and the local file.

`firstlook` takes the matrix (first column as feature id), gets each sample's
group from a sample sheet or from a regex on the sample name, collapses the
groups to control and case, and ranks features by the difference of means.
