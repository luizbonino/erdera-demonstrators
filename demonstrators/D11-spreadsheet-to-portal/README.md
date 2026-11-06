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
fixtures/synthetic-registry/   the ERDERA template filled for a fictional
                               patient-organisation registry, one TSV per sheet
                               (the template README recommends TSV export).
                               Also fixture 1 of the FDPlight import tests.
recording-script.md            the walkthrough, step by step, with timings to fill in
```

The TSV column headers follow the per-sheet documentation of the
[ERDERA template](https://github.com/ejp-rd-vp/resource-metadata-schema/blob/master/template/README.md).
Before use, copy the values into the official `.xlsx` template as well, so the
import is tested against both the xlsx and the TSV form.

## Steps

1. Demo index accepts a GitHub Pages FDP. Configure the demo VP Index on the
   testbed to accept pings from the demo organisation's Pages domain and
   confirm with a hand-made FDPlight project that the FDP is listed as active
   and its resources appear in the demo portal.
2. Repository and Pages. Create a repository under the demo organisation with
   Pages enabled on the branch FDPlight publishes to, and a fine-grained token
   scoped to it (Contents, Workflows, Pull requests).
3. Dry run with the fixture, on camera. Note the time between publish and
   appearance in the portal.
4. Co-owner review with the patient organisation. Adjust wording to their
   vocabulary. Their reaction to the red counts is the most informative moment.
5. Record five to seven minutes, closing with the contrast to the FDP
   Populator route (deployed FDP, credentials as GitHub secrets, a workflow).

## Acceptance

- A person who has never seen FDPlight, given the spreadsheet and the recording,
  reaches the portal result in under thirty minutes without help.
- Every value shown in the portal traces back to a cell in the spreadsheet.
- The synthetic registry never appears on vp.erdera.org.
