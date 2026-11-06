# ERDERA demonstrators · hand-off for Claude Code

Read this first. It is the state of the work as of 6 November 2026. It was
written by the planning session that scaffolded this repository and updated
the same day after D5 tasks 1 to 4. Everything below the "Verified" heading
has been checked against live sources. Everything under "Not yet verified"
has not.

## What this repository is

Demonstrators that show end users of the ERDERA Virtual Platform (VP) what it
makes possible. The DSH group agreed after the autumn 2026 General Assembly to
invest in demonstrators because the technology stack exists but end users do
not know what it does. Nine demonstrators were selected. Two are started here,
D5 (from a VP metadata record to a notebook) and D11 (from the ERDERA
spreadsheet to the portal with FDPlight, no server). Each demonstrator lives in
its own folder under `demonstrators/` with a README that holds the user story,
the remaining steps and the acceptance criteria. Read those READMEs before
touching code.

Code that belongs to an existing tool stays in that tool's repository. The
FDPlight spreadsheet import (D11 part A) is built in `~/GitHub/FDPlight`, not
here. This repository holds the fixtures, scripts, notebooks and recordings
around the tools.

## Owner and environment

- Owner Luiz Olavo Bonino, University of Twente, lead of the VP technology
  work in ERDERA (Task 13.2, with AIT). Repositories live in `~/GitHub/`.
- This repository is hosted in Luiz's personal GitHub account for now,
  `https://github.com/luizbonino/erdera-demonstrators`, branch `main`. It may
  move to the ERDERA organisation later. The D5 PROV agent IRI
  (`AGENT_IRI` in `src/vpfollow.py`) points there; GitHub redirects a
  transferred repository, but update the constant if it moves.
- Testbed server for the demo VP Index and Discovery Portal is
  `fair-testbed.eemcs.utwente.nl` (Ubuntu 24.04, reached over eduVPN, ssh as
  `luiz`; Docker and anything under `/opt` need sudo with a password, so root
  steps are run by Luiz). Its only public host name is that one. The Caddy
  front proxy of the pid-relay stack (`/opt/pid-relay/deploy`, from
  `luizbonino/pid-relay`) holds ports 80 and 443 and routes by path; new
  services join the `pid-relay_default` network and get a `handle` block in
  pid-relay's `deploy/Caddyfile`. Nothing in this repository writes to the
  production VP at `vp.erdera.org`.
- The demo VP Index is `infra/demo-index`, served at
  `https://fair-testbed.eemcs.utwente.nl/demo-index`. Its README has the
  deploy steps.
- The planning documents (demonstrator plan, D5 and D11 implementation plan)
  are Claude artifacts that this session cannot read. Their substance is in
  the demonstrator READMEs and in this file. Ask Luiz if something is missing.

## Verified (checked against live pages on 5 and 6 November 2026)

- `vp.erdera.org/discovery/sources` lists 71 resources. Only 14 answer
  content queries (Level 2), all of them BBMRI-ERIC biobanks. ERKReg is the
  only entry typed PatientRegistry.
- The rows for the EJPRD WP13 CAKUT proteome, peptidome and mirnome and for
  the Huntington disease datasets carry no link at all on that page, neither
  to their FDP record nor to ProteomeXchange or Zenodo. D5 therefore starts
  from the FDP record, found through the VP Index, and the recording calls
  that gap out.
- FDPlight (`https://fdplight.fairdatapoint.org`) with the ERDERA profile
  selected offers the types Catalog, Dataset, Distribution, Patient Registry,
  Biobank, Guideline, Access Service and Data Service, a VPDiscoverable /
  VPInvisible choice, nested Publisher (organisation name, description, logo,
  landing page) and Contact Information fields, required ORDO-based
  ontological description and keywords, red counts for problems, Turtle
  preview, publish to GitHub with a fine-grained token, and an optional
  workflow that pings an FDP Index after each Pages deployment. The visibility
  field's hint text reads "indexd by default" (typo, will be on screen).
- The ERDERA spreadsheet template has one sheet per resource type
  (Organisation, Biobank, Patient registry, Guideline, Dataset, Distribution,
  Data Service, Catalog, ContactPoint). Rows reference other rows by Title,
  titles must be unique in the spreadsheet, and the template README recommends
  exporting as TSV. Per-sheet field documentation is at
  `https://github.com/ejp-rd-vp/resource-metadata-schema/blob/master/template/README.md`.
  The pages disagree in places (two field sets on the Guideline page, the
  Dataset VPConnection heading missing, Biobank text copied from Patient
  registry). Follow the schema classes page and the SHACL shapes in that
  repository where the template pages conflict.
- D5 records. The VP Index (`https://index.vp.ejprarediseases.org`,
  `/index/entries/all`) lists the EJP RD WP13 FDP
  `https://w3id.org/ejp-rd/fairdatapoints/wp13` as ACTIVE. It holds the CAKUT
  proteome, peptidome and mirnome and the two Huntington datasets. IRIs,
  distribution URLs, what is at each data end, and the metadata errors found
  (licence differing from the repository, publisher IRI that is a CI file
  path, wrong media types) are in
  `demonstrators/D05-metadata-to-notebook/records.md`.
- D5 data ends. The CAKUT proteome record has only an access URL, and
  PXD022926 is about 100 GB of raw MS files with no processed table. The
  CAKUT mirnome (Zenodo, CC BY 4.0, 817 KB) and Huntington transcriptomics
  (GEO GSE64810, 12.7 MB) both have working `dcat:downloadURL`s.
- The demo VP Index (stock FDP 1.22.2 in index mode, auto-permit on)
  accepts an unauthorised JSON ping from a GitHub Pages FDP and harvests it:
  tested in local Docker on 6 November 2026 with the WP13.3 ProQolid FDP,
  through the same Caddy route as on the testbed, and again on the live
  testbed after the deploy the same day (entry ACCEPTED and ACTIVE). Ping both `/demo-index`
  and `/demo-index/`; neither redirects.
- ORDO has no single CAKUT class. The fixtures use `Orphanet_93545` "Renal or
  urinary tract malformation", the group that covers it (checked in EBI OLS).
  `Orphanet_399` is Huntington disease.
- The FDP Populator route (`https://github.com/ejp-rd-vp/fdp-populator`)
  needs a deployed FDP, stores FDP username and password as GitHub secrets,
  and its README says distributions are "almost ready" with limitations from
  schema discrepancies. D11 replaces that route.

## Not yet verified (the planning session had no PyPI and no access to the FDP hosts)

- The official `.xlsx` template could not be downloaded. The D11 fixture is
  TSV only, with column headers taken from the per-sheet documentation. Copy
  the values into the official workbook and keep both forms.

## Tasks, in order

### D5

Tasks 1 to 4 are done (6 November 2026). See the D5 README for the detail.

1. Done. Requirements installed (Python 3.14 locally), `pytest` passes. The
   one failure was a non-existent `dct:theme` term.
2. Done. Luiz did not supply the IRIs; they were found in the VP Index and
   recorded in `records.md`. Luiz chose Huntington transcriptomics (GSE64810)
   as the notebook default, with the CAKUT mirnome as the commented
   alternative.
3. Done. `vpfollow.follow()` handles both real records. Fixes: blank-node
   publishers, download file names from Content-Disposition or the redirect
   target (GEO and Zenodo redirect), workbook sheets. `hd_*.ttl.in` and
   `GSE0_counts.txt.gz` reproduce the WP13 Huntington shape. The group
   comparison is in `src/firstlook.py`.
4. Done. The executed notebook, figure and PROV record are committed under
   `output/`, with attribution in `output/README.md`.
5. Registration done (6 November 2026): `register/publish-fdp.ts` builds a
   file-only FDP in `fdp/` with FDPlight's code and ERDERA profile, served by
   GitHub Pages; its ping workflow points at the demo index, which harvested
   it. Still to do: the recording (README step 5).
   ERDERA's dataset shape fixes eight values with `sh:hasValue`, including a
   wrong Wikidata health theme (Q55789681, "benign neoplasm of ciliary body",
   labelled "rare disease"). Listed in `records.md`; to be reported to the
   shape maintainers.

### D11

1. ORDO code verified (`Orphanet_93545`). Still to do: the xlsx form of the
   fixture, from the official template.
2. In `~/GitHub/FDPlight` (separate repository, shares code with Contour),
   read how the ERDERA profile is defined, how form state is held in memory
   and how IRIs are minted from the base URI. Then add the import as three
   client-side components in front of the existing form state, with nothing
   changed downstream.
   - Sheet reader. xlsx (SheetJS) or one TSV per sheet. Sheet names are the
     resource types, each data row is one resource of that type. Skip empty
     and tooltip rows, match headers case- and space-insensitively, report
     unknown sheets and columns instead of dropping them silently.
   - Column mapper. Template column to profile property, one table per type.
     Theme and Keyword split on commas, Language ISO 639-1 to the id.loc.gov
     IRI, License defaults to the EJP RD licence IRI when empty, Personal Data
     must be true or false, Population Coverage one of National,
     International, Regional, European, VPConnection empty means
     VPDiscoverable.
   - Pointer resolver. Mint an IRI for every row first, then replace Publisher,
     Contact Point, Dataset, Distribution, Is Part Of, Access Service and
     Serves Dataset title references with the target row's IRI. An unresolved
     title becomes a red count on that field. Organisation and ContactPoint
     rows are copied into the nested publisher and contact fields of each
     resource, since the ERDERA profile nests them. A resource that no
     catalog lists goes under a catalog named after its organisation, and the
     import report says so.
   - Menu entry "Import spreadsheet…" next to "Import from a FAIR Data
     Point…" and "Open from files…", followed by an import report (rows per
     sheet, unresolved pointers, defaults applied) before the forms show.
   - Three test fixtures. This repository's synthetic registry (zero red
     counts expected), a copy with a dangling publisher title and a bad
     population coverage value (exactly two red counts on the right fields),
     and the TSV form importing identically to the xlsx. Plus a check that
     the generated Turtle validates against the ERDERA SHACL shapes.
3. Demo index accepting Pages pings, repository and Pages for the demo
   organisation, dry run, co-owner review, recording. Steps and acceptance in
   `demonstrators/D11-spreadsheet-to-portal/README.md` and
   `recording-script.md`.

## Rules that apply to all work here

- Synthetic resources carry the word SYNTHETIC in their titles and are
  registered only in the demo index on the testbed, never in the production
  index. Never write to `vp.erdera.org`.
- Reuse existing standards and the existing ERDERA schema and profile. Do not
  invent properties or vocabularies.
- Every URL a demonstrator follows comes from metadata, none is typed in
  beyond the starting IRI.
- When an FDP record's licence and the licence at the repository holding the
  data differ, go by the repository and report the record as a metadata
  error (Luiz, 6 November 2026).
- Recordings are not committed. Put them in the shared drive and link them
  from the demonstrator README.
- Keep each demonstrator self-contained under its folder with its own
  `requirements.txt`. Python 3.11 or later.
- Plain prose in READMEs and docs. Short sentences, no marketing tone.

## When something is unclear

Ask Luiz rather than guessing, especially about which registries and datasets
to use, which GitHub organisation hosts the demo repositories, and anything
about the FDPlight code base.
