// D5 step 4. Registers the notebook's output as a resource in a file-only FAIR
// Data Point, published with FDPlight's own code and ERDERA profile, so the
// files are exactly what the FDPlight app would write. The FDP lives in fdp/
// of this repository, served by GitHub Pages, and its ping workflow announces
// it to the demo VP Index on the testbed (never the production index).
//
// Run from an FDPlight checkout (~/GitHub/FDPlight, `npm install` done):
//
//   cd ~/GitHub/FDPlight
//   R=~/GitHub/ERDERA/erdera-demonstrators/demonstrators/D05-metadata-to-notebook/register
//   FDPLIGHT=$PWD GH_TOKEN=$(gh auth token) npx vite-node --config $R/vite.config.mjs $R/publish-fdp.ts            # dry run
//   FDPLIGHT=$PWD GH_TOKEN=$(gh auth token) npx vite-node --config $R/vite.config.mjs $R/publish-fdp.ts --show     # dry run, print files
//   FDPLIGHT=$PWD GH_TOKEN=$(gh auth token) npx vite-node --config $R/vite.config.mjs $R/publish-fdp.ts --commit   # one commit to main
//
// Later edits can be made in the app: open this repository, folder fdp/.

import { readFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { DataFactory } from 'n3';

const F = process.env.FDPLIGHT;
if (!F) throw new Error('set FDPLIGHT to an FDPlight checkout, e.g. FDPLIGHT=$PWD from ~/GitHub/FDPlight');
const { expandTerm, fieldKey, shapeFields } = await import(`${F}/node_modules/@fairdatateam/record-core/src/record.ts`);
const { checkProject } = await import(`${F}/src/core/checks.ts`);
const { userGraphFromForm } = await import(`${F}/src/core/forms.ts`);
const { pathOf, stamp } = await import(`${F}/src/core/project.ts`);
const { planPublish } = await import(`${F}/src/core/publish.ts`);
const { checkEntity, findingText, shapesGraph } = await import(`${F}/src/core/validation.ts`);
const { serializeEntity } = await import(`${F}/src/core/wiring.ts`);
const { createClient } = await import(`${F}/src/github/client.ts`);
const { useProject } = await import(`${F}/src/composables/useProject.ts`);
const { PROFILES } = await import(`${F}/src/profiles/index.ts`);

const REPO = { owner: 'luizbonino', repo: 'erdera-demonstrators', branch: 'main' };
const FOLDER = 'fdp/';
const BASE = 'https://luizbonino.github.io/erdera-demonstrators/fdp/';
const DEMO_INDEX = 'https://fair-testbed.eemcs.utwente.nl/demo-index';

// The files the distributions point to, served by the same Pages site.
const D5 = 'demonstrators/D05-metadata-to-notebook';
const PAGES = 'https://luizbonino.github.io/erdera-demonstrators/';
const OUTPUT = join(dirname(fileURLToPath(import.meta.url)), '..', 'output');
const served = (file: string) => `${PAGES}${D5}/output/${file}`;
const size = (file: string) => String(statSync(join(OUTPUT, file)).size);
readFileSync(join(OUTPUT, 'prov.ttl')); // fail early if the outputs are missing

const SOURCE_DATASET = 'https://w3id.org/ejp-rd/fairdatapoints/wp13/dataset/22238845-1213-43f6-a60f-e84cdc9fa2ed';
const REPO_URL = 'https://github.com/luizbonino/erdera-demonstrators';
const ISSUES = `${REPO_URL}/issues`;
const PUBLISHER = {
  name: 'ERDERA demonstrators, University of Twente',
  description: 'Demonstrators of the ERDERA Virtual Platform, maintained at the University of Twente (Task 13.2).',
  landingPage: REPO_URL,
};
const EN = 'http://id.loc.gov/vocabulary/iso639-1/en';
const CC0 = 'https://creativecommons.org/publicdomain/zero/1.0/';
const CC_BY = 'https://creativecommons.org/licenses/by/4.0/';
const MIT = 'https://spdx.org/licenses/MIT';
const FILE_TYPE = 'http://publications.europa.eu/resource/authority/file-type/';
const RARE_DISEASE = 'http://www.wikidata.org/entity/Q929833';
const HUNTINGTON = 'http://www.orpha.net/ORDO/Orphanet_399';
const TRANSCRIPTOMICS = 'http://edamontology.org/topic_3308';

// Values ERDERA's dataset shape fixes with sh:hasValue. A dataset is not valid
// without them, whatever it is, so they are written as required. See
// records.md for why some of them are wrong for this dataset.
const ERDERA_FIXED = {
  hdab: 'http://example.org/hdab/national-health-authority-de',
  healthCategory: 'http://data.europa.eu/healthdcat-ap/vocabulary#RareDiseaseData',
  provenance: 'http://example.org/provenance/rare-disease-registry-how-we-collect',
  spatial: 'http://data.europa.eu/nuts/code/EU',
  hasPurpose: 'https://w3id.org/dpv#ResearchAndDevelopment',
  type: 'http://data.europa.eu/930/dataset-type/PERSONAL_DATA',
  hasPersonalData: 'https://w3id.org/dpv#HealthData',
  healthTheme: 'http://www.wikidata.org/entity/Q55789681',
};

const common = (theme: string[], keyword: string[], license: string) => ({
  theme, keyword, language: EN, license, publisher: PUBLISHER, contactPoint: ISSUES,
});

const distribution = (title: string, description: string, file: string, format: string, license: string) => ({
  title, description,
  ...common([HUNTINGTON, TRANSCRIPTOMICS], ['Huntington disease', 'transcriptomics', 'ERDERA demonstrator'], license),
  accessURL: served(file),
  format: FILE_TYPE + format,
  rights: license,
  byteSize: size(file),
});

type Value = string | string[] | Record<string, string>;

/** Form values per entity, by the local name of each field's path. A nested node takes an object. */
const RECORDS: Record<string, Record<string, Value>> = {
  'fdp.ttl': {
    title: 'ERDERA demonstrator outputs',
    description:
      'Analyses produced by the ERDERA Virtual Platform demonstrators, each registered with the data it came from. Published with FDPlight as a file-only FAIR Data Point.',
    landingPage: REPO_URL,
    ...common([RARE_DISEASE], ['ERDERA', 'Virtual Platform', 'demonstrator'], CC0),
  },
  'catalog/analyses.ttl': {
    title: 'Demonstrator analyses',
    description: 'Results of the notebooks of the ERDERA demonstrators, with the notebook, its figures and the provenance of each run.',
    landingPage: REPO_URL,
    ...common([RARE_DISEASE], ['ERDERA', 'demonstrator', 'notebook'], CC0),
  },
  'dataset/d5-huntington-first-look.ttl': {
    title: 'D5 first look: Huntington disease transcriptomics (GSE64810)',
    description:
      'A first two-group look at GEO GSE64810 (Labadorf et al. 2015, 20 Huntington disease and 49 control prefrontal cortex samples): genes ranked by the difference of mean log2(count + 1). Produced by the ERDERA D5 notebook, which reached the data from the EJP RD WP13 FAIR Data Point record alone. A first look, not a differential expression analysis.',
    landingPage: `${REPO_URL}/tree/main/${D5}`,
    ...common([HUNTINGTON, TRANSCRIPTOMICS], ['Huntington disease', 'transcriptomics', 'RNA-Seq', 'ERDERA demonstrator'], CC_BY),
    ...ERDERA_FIXED,
    // The PROV record of the run is the real provenance; ERDERA's fixed value stays as required.
    provenance: [ERDERA_FIXED.provenance, served('prov.ttl')],
    sample: served('top_differences.png'),
  },
  'distribution/d5-notebook.ttl': distribution(
    'D5 notebook, executed',
    'The Jupyter notebook with its outputs, from the dataset record to the figure and the PROV record.',
    'd5_metadata_to_notebook.executed.ipynb', 'JSON', MIT,
  ),
  'distribution/d5-figure.ttl': distribution(
    'Figure: top 20 genes by difference of means',
    'Bar chart of the 20 genes with the largest difference of mean log2(count + 1) between Huntington disease and control samples.',
    'top_differences.png', 'PNG', CC_BY,
  ),
  'distribution/d5-prov.ttl': distribution(
    'PROV-O record of the run',
    'What the notebook used (dataset record, distribution record, data URL) and what it produced.',
    'prov.ttl', 'RDF_TURTLE', CC_BY,
  ),
};

/** Triples with no form field, kept with the entity as FDPlight keeps unmapped triples (SPEC §5.7). */
const EXTRAS = {
  'dataset/d5-huntington-first-look.ttl': [
    DataFactory.quad(
      DataFactory.namedNode(BASE + 'dataset/d5-huntington-first-look.ttl'),
      DataFactory.namedNode('http://www.w3.org/ns/prov#wasDerivedFrom'),
      DataFactory.namedNode(SOURCE_DATASET),
    ),
  ],
};

const LANGUAGE_TAGGED = new Set(['title', 'description']);

const localName = (term: string, prefixes: any) => (expandTerm(term, prefixes) ?? term).replace(/^.*[#/]/, '');

// As in FDPlight's scripts/publish-own-fdp.ts, plus nested nodes filled field by field.
function fill(form: any, node: any, record: Record<string, Value>): void {
  for (const f of shapeFields(form)) {
    const local = localName(f.path, form.prefixes);
    const v = record[local];
    if (v === undefined) continue;
    const list = Array.isArray(v) ? v : [v];
    const key = fieldKey(f);
    node[key] = list.map((value: string | Record<string, string>, i: number) => {
      const entry = { ...(node[key]?.[i] ?? node[key][0]) };
      if (entry.node) {
        // Nested (publisher, contact point): an object fills its fields by
        // local name, a string fills its first field.
        const inner = { ...entry.node };
        const fields = typeof value === 'string' ? { [localName(Object.keys(inner)[0], form.prefixes)]: value } : value;
        for (const k of Object.keys(inner)) {
          const nested = fields[localName(k, form.prefixes)];
          if (nested !== undefined) inner[k] = [{ ...inner[k][0], value: nested }];
        }
        return { ...entry, node: inner };
      }
      return { ...entry, value, lang: LANGUAGE_TAGGED.has(local) ? 'en' : '' };
    });
  }
}

async function main(): Promise<void> {
  const commit = process.argv.includes('--commit');
  const token = process.env.GH_TOKEN;
  if (!token) throw new Error('set GH_TOKEN, e.g. GH_TOKEN=$(gh auth token)');

  const state = useProject(undefined, 'erdera');
  const p = state.project;
  p.name = 'ERDERA demonstrator outputs';
  p.base = BASE;
  p.folder = FOLDER;
  p.use = ['catalog', 'dataset', 'distribution'];
  p.index = { url: DEMO_INDEX, pagesWorkflow: 'pages-build-deployment' };
  p.defaults.license = null;
  state.add('fdp.ttl', 'catalog');
  state.rename(state.selected.value, 'analyses');
  state.add('catalog/analyses.ttl', 'dataset');
  state.rename(state.selected.value, 'd5-huntington-first-look');
  for (const id of ['d5-notebook', 'd5-figure', 'd5-prov']) {
    state.add('dataset/d5-huntington-first-look.ttl', 'distribution');
    state.rename(state.selected.value, id);
  }
  if (state.lastError.value) throw new Error(state.lastError.value);

  for (const e of p.entities) {
    const path = pathOf(p, e);
    if (!RECORDS[path]) throw new Error(`no values for ${path}`);
    fill(state.forms[e.type], state.values[path], RECORDS[path]);
  }

  // The same checks the app runs before publishing (SPEC §6).
  const now = new Date();
  const graphs = new Map(
    p.entities.map((e: any) => {
      const path = pathOf(p, e);
      return [path, serializeEntity(p, stamp(e, now), userGraphFromForm(state.forms[e.type], BASE + path, state.values[path], (EXTRAS as any)[path]))];
    }),
  );
  const structural = checkProject(p, graphs).filter((i: any) => i.severity === 'error');
  const shacl: string[] = [];
  for (const e of p.entities) {
    const path = pathOf(p, e);
    const findings = await checkEntity(state.forms[e.type], BASE + path, state.values[path], graphs.get(path), shapesGraph(PROFILES.erdera.shapes[e.type]));
    shacl.push(...findings.map((f: any) => `${path} ${f.loc ?? ''}: ${findingText(f)}`));
  }
  if (structural.length || shacl.length) {
    console.error([...structural.map((i: any) => `${i.entity}: ${i.message}`), ...shacl].join('\n'));
    throw new Error('the metadata does not pass the checks');
  }

  const client = createClient(token);
  const head = await client.branchHead(REPO);
  const files = await client.listFiles(REPO, head);
  const remote = new Map<string, string | null>();
  for (const f of files.filter((x: string) => x.startsWith(FOLDER) || x === '.github/workflows/fdp-ping.yml'))
    remote.set(f, await client.readFile(REPO, f, head));

  const plan = await planPublish({ project: p, forms: state.forms, values: state.values, shapes: state.shapes, extras: EXTRAS, remote, remoteFiles: files, now });
  console.log(plan.message);
  console.log(plan.changes.map((c: any) => `${c.content === null ? 'delete' : 'write '} ${c.path}`).join('\n'));
  if (process.argv.includes('--show'))
    for (const c of plan.changes) if (c.content && c.path.startsWith(FOLDER) && !c.path.includes('/shapes/') && !c.path.includes('/profile/')) console.log(`\n# ${c.path}\n${c.content}`);
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
