# D11 recording script

Target length five to seven minutes. Fill in the timings after the dry run.

| Step | On screen                                                                 | Voice-over                                                                                              | Time |
| ---- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ---- |
| 1    | The filled spreadsheet, sheet tabs visible                                | This is the spreadsheet ERDERA already asks resource providers to fill. One sheet per kind of resource. |      |
| 2    | fdplight.fairdatapoint.org, guided setup, ERDERA profile                  | FDPlight runs in the browser. No server, nothing to install.                                            |      |
| 3    | Import spreadsheet, import report                                         | The sheets are read, rows become resources, references between sheets are resolved.                    |      |
| 4    | The tree with the catalog and the registry, red counts                    | What the sheet left incomplete shows up as red counts, exactly where the VP validator would complain.   |      |
| 5    | Fixing a red count in the form                                            | Fix it in place.                                                                                        |      |
| 6    | The Turtle preview                                                        | This is the record the VP will read. You never have to touch it.                                        |      |
| 7    | Publish to GitHub, Pages deploy, the ping workflow                        | Publishing writes the files to a repository and pings the VP Index.                                     |      |
| 8    | The demo Discovery Portal, search for the disease, the registry appears   | And here it is, findable next to the biobanks and registries that are already there.                    |      |
| 9    | Closing slide, contrast with the FDP Populator route                      | Before, this needed a running FDP, credentials stored as secrets and a workflow to run.                 |      |

Measured during the headless dry run (2026-11-06): time from publish to the
entry being ACTIVE in the demo index, about 6 minutes, nearly all of it the
first Pages build. Time to appearance in a portal: to be measured once a demo
portal reads the demo index.
