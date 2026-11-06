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
fixtures/                                an FDP-shaped dataset + distribution + CSV for tests
tests/test_vpfollow.py                   end-to-end test against a local fixture server
requirements.txt
```

## Run

```bash
cd demonstrators/D05-metadata-to-notebook
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest                      # runs the chain against local fixtures
jupyter lab notebook/       # set DATASET_IRI in the first code cell, run all
```

## Steps still to do

1. Locate the dataset records. From the VP Index member list, or from the FDP
   the WP13 datasets were published to, take the `dcat:Dataset` IRIs of the
   CAKUT proteome and the Huntington transcriptomics datasets. Record them in
   `records.md` in this folder with the distribution URLs they point to.
2. Check the data end. Confirm the ProteomeXchange and Zenodo landing pages
   resolve, note file list, sizes and licence. Pick the smallest open download.
   If neither distribution carries `dcat:downloadURL` or `dcat:accessURL`
   (both are optional in the ERDERA schema), fall back to the IBM expression
   datasets on the same portal page.
3. Run the notebook with the chosen IRI and `GROUP_COLUMN` set to the column
   that separates CAKUT from non-CAKUT (or the brain region, for Huntington).
4. Register the notebook as a resource in the demo index with FDPlight (ERDERA
   profile), so the recording ends with the analysis itself being findable.
5. Record five minutes, portal row to figure, opening with what the portal
   shows and what it does not.

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
access URL. `download()` streams the file and unpacks `.gz`. `load_table()`
sniffs the delimiter. `prov_graph()` writes a PROV-O record naming the dataset,
the distribution, the data URL and the local file.
