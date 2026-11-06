# D11 · From the spreadsheet to the portal, no server

**Audience.** Patient organisations and data stewards without an IT department.

**Story.** A steward fills the familiar ERDERA resource metadata spreadsheet,
drops it into [FDPlight](https://fdplight.fairdatapoint.org), sees the forms
already populated with a few red counts where the sheet was incomplete, fixes
them, publishes to a GitHub repository, and within one ping cycle the registry
appears in the demo Discovery Portal. No FDP to deploy, no credentials beyond a
repository token.

The import feature itself is built in the FDPlight repository. This folder
holds what the demonstrator needs around it.

## Layout

```
fixtures/synthetic-registry/   the official ERDERA template filled for a
                               fictional patient-organisation registry, as an
                               xlsx and as one TSV per sheet (the template
                               README recommends TSV export). Also fixture 1
                               of the FDPlight import tests.
recording-script.md            the walkthrough, step by step, with timings to fill in
```

Both forms follow the official workbook of the
[ERDERA template](https://github.com/ejp-rd-vp/resource-metadata-schema/blob/master/template/README.md),
which differs from its per-sheet documentation in places; the fixture README
lists how.

## Steps

Done (2026-11-06):

1. Demo index. The demo VP Index on the testbed
   (<https://fair-testbed.eemcs.utwente.nl/demo-index>, `infra/demo-index`)
   accepts unauthorised pings from GitHub Pages FDPs and accepts new entries
   automatically.
2. Repository and Pages. The synthetic organisation's FDP lives in
   `luizbonino/synthetic-rkpa-fdp` (personal account for now), with Pages on
   `main`, served at <https://luizbonino.github.io/synthetic-rkpa-fdp/>.
3. Dry run, headless (`dry-run/publish-fdp.ts`). With FDPlight's own code
   (the spreadsheet import, branch `spreadsheet-import` until merged): an
   ERDERA project whose root is filled as in the guided setup, the fixture
   workbook imported with zero red counts, one commit. The Pages build
   triggered FDPlight's ping workflow and the demo index harvested the FDP,
   the catalog and the patient registry (ACTIVE). The VP's Level 1 query,
   with the two rewrites FDPlight's SPEC §9.6 describes, lists all three.
   Publish to ACTIVE took about six minutes, nearly all of it the first Pages
   build.

   Pitfall for the recording: switching Pages on starts a build of the
   current commit. Publishing during that build cancels it, and the ping for
   the cancelled build is skipped; the next build pings. Switch Pages on
   first and let that build finish, or simply wait for the second ping.

Still to do:

4. The import in the live app: review and merge the FDPlight pull request.
5. A demo Discovery Portal on the testbed that reads the demo index. Until
   then the recording can end on the index entry and its harvested records.
6. Dry run on camera in the app, with a fine-grained token scoped to the
   repository (Contents, Workflows, Pull requests).
7. Co-owner review with the patient organisation. Adjust wording to their
   vocabulary. Their reaction to the red counts is the most informative moment.
8. Record five to seven minutes, closing with the contrast to the FDP
   Populator route (deployed FDP, credentials as GitHub secrets, a workflow).

## Acceptance

- A person who has never seen FDPlight, given the spreadsheet and the recording,
  reaches the portal result in under thirty minutes without help.
- Every value shown in the portal traces back to a cell in the spreadsheet.
- The synthetic registry never appears on vp.erdera.org.
