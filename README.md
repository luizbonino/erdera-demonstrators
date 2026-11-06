# ERDERA Virtual Platform demonstrators

Demonstrators that show end users (data stewards, biomedical and rare disease
researchers, clinicians, patients and patient representatives) what the ERDERA
Virtual Platform (VP) makes possible. They follow the demonstrator plan agreed
in the DSH group after the autumn 2026 General Assembly.

Each demonstrator lives in its own folder under `demonstrators/`, with a README
that states the user story, what the demonstrator shows, what it needs, and how
to run or record it. Code that belongs to an existing tool stays in that tool's
repository (FDPlight, FDPneo, the FAIR Data Train components) and is only
referenced from here.

| Id  | Demonstrator                                        | Audience                          | Status   |
| --- | --------------------------------------------------- | --------------------------------- | -------- |
| D4  | One search, three kinds of answers (neuromuscular)  | researchers, clinicians           | planned  |
| D5  | From a VP metadata record to a notebook             | researchers, data scientists      | started  |
| D6  | Programmatic cohort counts across the network       | data scientists, developers       | planned  |
| D7  | Trial feasibility across registries, two phases     | ERN clinicians                    | planned  |
| D8  | The VP inside an ERN site                           | clinical researchers              | planned  |
| D9  | Where is the research on my condition               | patients, representatives         | planned  |
| D10 | What happens to data about my disease               | patients, representatives         | planned  |
| D11 | From the spreadsheet to the portal, no server       | patient organisations, stewards   | started  |
| D13 | Level 3 by data visiting                            | DSH, Distributed Analysis group   | planned  |

## Layout

```
demonstrators/
  D05-metadata-to-notebook/     D5: notebook, library, fixtures, tests
  D11-spreadsheet-to-portal/    D11: fixtures and the recording script; the
                                import feature itself lives in FDPlight
```

## Conventions

- Python 3.11 or later. Each demonstrator has its own `requirements.txt`.
- Nothing in this repository talks to the production VP (`vp.erdera.org`) in a
  way that writes. Synthetic resources are labelled as such and registered only
  in the demo index on the testbed.
- Recordings are not committed. Put them in the shared drive and link them
  from the demonstrator README.
