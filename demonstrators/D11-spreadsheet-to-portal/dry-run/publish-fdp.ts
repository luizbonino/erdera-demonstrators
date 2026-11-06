// D11 dry run, headless. Does what the recording shows in the FDPlight app,
// with FDPlight's own code: an ERDERA project whose root is filled as in the
// guided setup, the fixture workbook imported (Import spreadsheet…), the
// checks the app runs before publishing, and one commit to the synthetic
// organisation's repository. Its ping workflow announces the FDP to the demo
// VP Index on the testbed, never the production index.
//
// Needs an FDPlight checkout that has the spreadsheet import (SPEC §4.4,
// branch spreadsheet-import until it is merged), with `npm install` done:
//
//   cd ~/GitHub/FDPlight
//   R=~/GitHub/ERDERA/erdera-demonstrators/demonstrators/D11-spreadsheet-to-portal/dry-run
//   FDPLIGHT=$PWD GH_TOKEN=$(gh auth token) npx vite-node --config $R/vite.config.mjs $R/publish-fdp.ts            # dry run
//   FDPLIGHT=$PWD GH_TOKEN=$(gh auth token) npx vite-node --config $R/vite.config.mjs $R/publish-fdp.ts --show     # print files
//   FDPLIGHT=$PWD GH_TOKEN=$(gh auth token) npx vite-node --config $R/vite.config.mjs $R/publish-fdp.ts --commit   # publish

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const F = process.env.FDPLIGHT;
if (!F) throw new Error('set FDPLIGHT to an FDPlight checkout, e.g. FDPLIGHT=$PWD from ~/GitHub/FDPlight');
const { expandTerm, fieldKey, shapeFields } = await import(`${F}/node_modules/@fairdatateam/record-core/src/record.ts`);
const { checkProject } = await import(`${F}/src/core/checks.ts`);
const { userGraphFromForm } = await import(`${F}/src/core/forms.ts`);
const { pathOf, stamp } = await import(`${F}/src/core/project.ts`);
const { planPublish } = await import(`${F}/src/core/publish.ts`);
const { readSpreadsheet } = await import(`${F}/src/core/spreadsheet.ts`);
const { importSpreadsheet } = await import(`${F}/src/core/spreadsheetImport.ts`);
const { checkEntity, findingText, shapesGraph } = await import(`${F}/src/core/validation.ts`);
const { serializeEntity } = await import(`${F}/src/core/wiring.ts`);
const { createClient } = await import(`${F}/src/github/client.ts`);
const { useProject } = await import(`${F}/src/composables/useProject.ts`);
const { PROFILES } = await import(`${F}/src/profiles/index.ts`);

const REPO = { owner: 'luizbonino', repo: 'synthetic-rkpa-fdp', branch: 'main' };
const BASE = 'https://luizbonino.github.io/synthetic-rkpa-fdp/';
const DEMO_INDEX = 'https://fair-testbed.eemcs.utwente.nl/demo-index';
const WORKBOOK = join(dirname(fileURLToPath(import.meta.url)), '..', 'fixtures', 'synthetic-registry', 'synthetic-registry.xlsx');

// What the steward types in the guided setup for the FDP itself; the
// spreadsheet has no row for it.
const ROOT: Record<string, string | string[] | Record<string, string>> = {
  title: 'SYNTHETIC Rare Kidney Patient Alliance FAIR Data Point',
  description: 'The resources of the fictional SYNTHETIC Rare Kidney Patient Alliance, published with FDPlight for the ERDERA D11 demonstrator. Not a real organisation; contains no real data.',
  theme: 'http://www.orpha.net/ORDO/Orphanet_93545',
  keyword: ['synthetic', 'CAKUT', 'patient organisation'],
  language: 'http://id.loc.gov/vocabulary/iso639-1/en',
  license: 'https://w3id.org/ejp-rd/resources/licenses/v1.0/',
  publisher: {
    name: 'SYNTHETIC Rare Kidney Patient Alliance',
    description: 'A fictional patient organisation used for the ERDERA D11 demonstrator. Not a real organisation.',
    landingPage: 'https://example.org/synthetic-rkpa',
  },
  contactPoint: 'mailto:registry@example.org',
};

const localName = (term: string, prefixes: any) => (expandTerm(term, prefixes) ?? term).replace(/^.*[#/]/, '');

/** As D5's register/publish-fdp.ts: fill a form by local field names, nested nodes from an object. */
function fill(form: any, node: any, record: typeof ROOT): void {
  for (const f of shapeFields(form)) {
    const local = localName(f.path, form.prefixes);
    const v = record[local];
    if (v === undefined) continue;
    const list = Array.isArray(v) ? v : [v];
    const key = fieldKey(f);
    node[key] = list.map((value: string | Record<string, string>, i: number) => {
      const entry = { ...(node[key]?.[i] ?? node[key][0]) };
      if (entry.node) {
        const inner = { ...entry.node };
        const fields = typeof value === 'string' ? { [localName(Object.keys(inner)[0], form.prefixes)]: value } : value;
        for (const k of Object.keys(inner)) {
          const nested = fields[localName(k, form.prefixes)];
          if (nested !== undefined) inner[k] = [{ ...inner[k][0], value: nested }];
        }
        return { ...entry, node: inner };
      }
      return { ...entry, value, lang: local === 'title' || local === 'description' ? 'en' : '' };
    });
  }
}

async function main(): Promise<void> {
  const commit = process.argv.includes('--commit');
  const token = process.env.GH_TOKEN;
  if (!token) throw new Error('set GH_TOKEN, e.g. GH_TOKEN=$(gh auth token)');

  // Guided setup: ERDERA profile, base URI, Index, the root's form.
  const state = useProject(undefined, 'erdera');
  const p = state.project;
  p.name = 'SYNTHETIC Rare Kidney Patient Alliance';
  p.base = BASE;
  p.folder = '';
  p.use = ['catalog'];
  p.index = { url: DEMO_INDEX, pagesWorkflow: 'pages-build-deployment' };
  fill(state.forms.fdp, state.values['fdp.ttl'], ROOT);

  // Import spreadsheet…
  const read = readSpreadsheet([{ name: 'synthetic-registry.xlsx', data: new Uint8Array(readFileSync(WORKBOOK)) }]);
  if (!read.ok) throw new Error(read.error);
  const imported = importSpreadsheet({ sheets: read.sheets, project: p, forms: state.forms });
  if (!imported.ok) throw new Error(imported.error);
  state.addImported(imported);
  console.log('Import report');
  for (const [k, v] of Object.entries(imported.report)) if ((v as string[]).length) console.log(`  ${k}: ${(v as string[]).join('; ')}`);

  // The checks the app runs before publishing (SPEC §6): every red count counts.
  const now = new Date();
  const graphs = new Map(
    p.entities.map((e: any) => {
      const path = pathOf(p, e);
      return [path, serializeEntity(p, stamp(e, now), userGraphFromForm(state.forms[e.type], BASE + path, state.values[path]))];
    }),
  );
  const structural = checkProject(p, graphs).filter((i: any) => i.severity === 'error');
  const shacl: string[] = [];
  for (const e of p.entities) {
    const path = pathOf(p, e);
    const findings = await checkEntity(state.forms[e.type], BASE + path, state.values[path], graphs.get(path), shapesGraph(PROFILES.erdera.shapes[e.type]));
    shacl.push(...findings.map((f: any) => `${path} ${f.loc ?? ''}: ${findingText(f)}`));
  }
  console.log(`\nRecords: ${p.entities.map((e: any) => pathOf(p, e)).join(', ')}`);
  console.log(`Red counts: ${structural.length + shacl.length}`);
  if (structural.length || shacl.length) {
    console.error([...structural.map((i: any) => `${i.entity}: ${i.message}`), ...shacl].join('\n'));
    throw new Error('the metadata does not pass the checks');
  }

  const client = createClient(token);
  const head = await client.branchHead(REPO);
  const files = await client.listFiles(REPO, head);
  const remote = new Map<string, string | null>();
  for (const f of files.filter((x: string) => x.endsWith('.ttl') || x === 'fdplight.json' || x === '.github/workflows/fdp-ping.yml'))
    remote.set(f, await client.readFile(REPO, f, head));

  const plan = await planPublish({ project: p, forms: state.forms, values: state.values, shapes: state.shapes, remote, remoteFiles: files, now });
  console.log(`\n${plan.message}`);
  if (process.argv.includes('--show'))
    for (const c of plan.changes) if (c.content && c.path.endsWith('.ttl') && !/^(shapes|profile)\//.test(c.path)) console.log(`\n# ${c.path}\n${c.content}`);
  if (!commit) {
    console.log('\nDry run. Add --commit to publish.');
    return;
  }
  if (!plan.changes.length) return;
  const sha = await client.commitFiles(REPO, head, plan.changes, plan.message);
  console.log(`\nPublished https://github.com/${REPO.owner}/${REPO.repo}/commit/${sha}`);
}

main().catch((e) => {
  console.error(e instanceof Error ? e.message : e);
  process.exit(1);
});
