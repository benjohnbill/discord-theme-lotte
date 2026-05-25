# Theme Change Workflow Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make small future user-driven Discord theme edits smooth by adding one snapshot scaffolder, one selector-usage drift contract test, and a short workflow pointer, without expanding scope into visual regression or live Discord automation.

**Architecture:** Add `scripts/new-snapshot.js` as a thin CLI plus exported `scaffoldSnapshot()` function so a `node:test` suite can exercise it on synthetic inputs and the user can run `rtk npm run snapshot:new -- <screen>` to seed `snapshots/YYYY-MM-DD/<screen>.json` from a stub. Add `test/selector-usage-contract.test.js` as a workspace contract that asserts every class in `registry/selectors.yaml` appears at least once in its `cssOwner` partial, so silent drift between registry and CSS fails `npm test`. Update `docs/workflow.md` with one short reference block pointing at the new helper and contract test.

**Tech Stack:** Node ESM, `node:test`, `node:assert/strict`, `yaml`, `fs`, `path`, `npm` scripts run through `rtk`.

---

## File Structure

- Create: `scripts/new-snapshot.js`
  - Thin CLI module that exports `scaffoldSnapshot({ screen, today, root, fsImpl, screensDoc })` and runs the CLI when executed directly.
  - Writes `snapshots/<today>/<screen>.json` from a deterministic stub.
  - Refuses to overwrite an existing file.
  - Refuses to scaffold for a screen that is not in `registry/screens.yaml`.
  - Pure function under the hood so tests do not touch the real disk.
- Modify: `package.json`
  - Add `"snapshot:new": "node scripts/new-snapshot.js"` to `scripts`.
  - Do not change `build`, `validate`, `sync`, `check`, or `test`.
- Create: `test/snapshot-scaffold.test.js`
  - TDD-driven `node:test` subtests around `scaffoldSnapshot`:
    - creates a file at the expected path with the expected stub body,
    - refuses to overwrite an existing file,
    - refuses an unknown screen.
- Create: `test/selector-usage-contract.test.js`
  - Workspace contract test that loads `registry/selectors.yaml` and asserts every class for each selector entry appears in its `cssOwner` partial.
- Modify: `docs/workflow.md`
  - Append a short "Helpers" section pointing at `rtk npm run snapshot:new -- <screen>` and the selector-usage contract test.
  - Do not duplicate the standard flow or restructure existing sections.
- Preserve: `AGENTS.md`, `CONTEXT.md`, `scripts/build-theme.js`, `scripts/sync-to-vencord.js`, `scripts/inspect-dom.js`, `scripts/validate-registry.js`, `scripts/registry-checks.js`, `theme.manifest.yaml`, `registry/*.yaml`, `snapshots/**`, `dist/NewKemonoFriends.theme.css`.

## Non-Goals

- Do not change `schema/*.json`.
- Do not change `theme.manifest.yaml` or any `registry/*.yaml`.
- Do not change `src/**`.
- Do not change `scripts/inspect-dom.js`, `scripts/sync-to-vencord.js`, or `scripts/build-theme.js`.
- Do not write a new docs page; only append to `docs/workflow.md`.
- Do not introduce browser automation, visual regression, or Discord live DOM automation.
- Do not introduce PRD docs, issue tracking, or new milestone docs.
- Do not run `rtk npm run sync`.
- Do not edit the Vencord live theme directory.
- Do not run `rtk npm run snapshot:new` against the real repo; verification stays inside `node:test`.

## Tasks

### Task 1: Selector Usage Contract Test (drift detector)

**Files:**
- Create: `test/selector-usage-contract.test.js`

- [ ] **Step 1: Write the contract test**

Create `test/selector-usage-contract.test.js`:

```js
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import YAML from "yaml";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function readText(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

test("every selector class is referenced inside its cssOwner partial", () => {
  const selectorsDoc = YAML.parse(readText("registry/selectors.yaml"));
  const entries = Object.entries(selectorsDoc?.selectors ?? {});
  assert.ok(entries.length > 0, "registry/selectors.yaml must declare at least one selector entry");

  const ownerCache = new Map();
  const missing = [];

  for (const [name, entry] of entries) {
    if (!ownerCache.has(entry.cssOwner)) {
      ownerCache.set(entry.cssOwner, readText(entry.cssOwner));
    }
    const ownerCss = ownerCache.get(entry.cssOwner);

    for (const className of entry.classes ?? []) {
      if (!ownerCss.includes(className)) {
        missing.push(`${name}: class "${className}" not referenced in ${entry.cssOwner}`);
      }
    }
  }

  assert.deepEqual(missing, [], `selector classes missing from their cssOwner partial:\n${missing.join("\n")}`);
});
```

- [ ] **Step 2: Run tests to confirm the contract holds against current state**

Run:

```bash
rtk npm test
```

Expected: PASS with `build-contract.test.js`, `registry-cross-references.test.js` (from Milestone 2), and the new `selector-usage-contract.test.js` all green.

If `selector classes missing from their cssOwner partial:` appears, registry and CSS already drifted; stop and fix the registry or CSS before continuing.

- [ ] **Step 3: Commit**

Run:

```bash
rtk git add test/selector-usage-contract.test.js
rtk git commit -m "test: assert selector classes appear in their cssOwner partial"
```

Expected: commit succeeds and includes only the new test file.

### Task 2: Snapshot Scaffolder Tracer Bullet (creates file)

**Files:**
- Create: `test/snapshot-scaffold.test.js`
- Create: `scripts/new-snapshot.js`

- [ ] **Step 1: Write the failing test**

Create `test/snapshot-scaffold.test.js`:

```js
import assert from "node:assert/strict";
import test from "node:test";

import { scaffoldSnapshot } from "../scripts/new-snapshot.js";

function makeFsImpl(initial = {}) {
  const store = new Map(Object.entries(initial));
  return {
    existsSync: (filePath) => store.has(filePath),
    mkdirSync: (dirPath) => {
      store.set(`dir:${dirPath}`, "");
    },
    writeFileSync: (filePath, contents) => {
      store.set(filePath, contents);
    },
    readStore: () => store
  };
}

const screensDoc = {
  schemaVersion: 1,
  screens: {
    "friends-page": {
      owns: [],
      importantSelectors: [],
      goals: [],
      knownRisks: []
    }
  }
};

test("scaffoldSnapshot creates a snapshot file at snapshots/<today>/<screen>.json with stub metadata", () => {
  const fsImpl = makeFsImpl();
  const result = scaffoldSnapshot({
    screen: "friends-page",
    today: "2026-06-01",
    root: "/repo",
    fsImpl,
    screensDoc
  });

  assert.equal(result.relativePath, "snapshots/2026-06-01/friends-page.json");
  const written = fsImpl.readStore().get("/repo/snapshots/2026-06-01/friends-page.json");
  assert.ok(typeof written === "string" && written.length > 0, "scaffolded file must have non-empty content");

  const parsed = JSON.parse(written);
  assert.equal(parsed.schemaVersion, 1);
  assert.equal(parsed.screen, "friends-page");
  assert.equal(parsed.routeHint, "replace-with-current-route");
  assert.equal(parsed.sourceScreenshot, "replace-with-screenshot-path");
  assert.equal(parsed.discordBuild, "unknown");
  assert.deepEqual(parsed.elements, []);
  assert.match(parsed.capturedAt, /^2026-06-01/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
rtk npm test
```

Expected: FAIL with `Cannot find module '../scripts/new-snapshot.js'` or equivalent missing-module error.

- [ ] **Step 3: Implement the scaffolder**

Create `scripts/new-snapshot.js`:

```js
import nodeFs from "node:fs";
import path from "node:path";
import process from "node:process";
import YAML from "yaml";

export function scaffoldSnapshot({ screen, today, root, fsImpl, screensDoc }) {
  const knownScreens = new Set(Object.keys(screensDoc?.screens ?? {}));
  if (!knownScreens.has(screen)) {
    throw new Error(`unknown screen "${screen}". Add it to registry/screens.yaml first.`);
  }

  const relativePath = `snapshots/${today}/${screen}.json`;
  const absolutePath = path.join(root, relativePath);

  if (fsImpl.existsSync(absolutePath)) {
    throw new Error(`refusing to overwrite existing file ${relativePath}`);
  }

  const stub = {
    schemaVersion: 1,
    capturedAt: `${today}T00:00:00+09:00`,
    discordBuild: "unknown",
    vencordVersion: "unknown",
    themeVersion: "0.1.0",
    os: "unknown",
    zoom: "unknown",
    screen,
    routeHint: "replace-with-current-route",
    viewport: "replace-with-viewport",
    sourceScreenshot: "replace-with-screenshot-path",
    notes: "Stub created by scripts/new-snapshot.js. Replace placeholders before commit.",
    elements: []
  };

  fsImpl.mkdirSync(path.dirname(absolutePath), { recursive: true });
  fsImpl.writeFileSync(absolutePath, `${JSON.stringify(stub, null, 2)}\n`);

  return { relativePath, absolutePath };
}

function main() {
  const screen = process.argv[2];
  if (!screen) {
    console.error("usage: node scripts/new-snapshot.js <screen-id>");
    process.exit(1);
  }

  const root = process.cwd();
  const screensDoc = YAML.parse(nodeFs.readFileSync(path.join(root, "registry/screens.yaml"), "utf8"));
  const today = new Date().toISOString().slice(0, 10);

  const { relativePath } = scaffoldSnapshot({
    screen,
    today,
    root,
    fsImpl: nodeFs,
    screensDoc
  });

  console.log(`Scaffolded ${relativePath}`);
}

const isCli = process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname);
if (isCli) {
  main();
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS with `build-contract.test.js`, `registry-cross-references.test.js`, `selector-usage-contract.test.js`, and the new subtest in `snapshot-scaffold.test.js` all green.

- [ ] **Step 5: Commit**

Run:

```bash
rtk git add scripts/new-snapshot.js test/snapshot-scaffold.test.js
rtk git commit -m "feat: add snapshot scaffolder with disk-free unit test"
```

Expected: commit succeeds and includes only the scaffolder and its test.

### Task 3: Scaffolder Refuses Overwrites

**Files:**
- Modify: `test/snapshot-scaffold.test.js`

- [ ] **Step 1: Add failing test**

Append to `test/snapshot-scaffold.test.js`:

```js
test("scaffoldSnapshot refuses to overwrite an existing snapshot file", () => {
  const fsImpl = makeFsImpl({
    "/repo/snapshots/2026-06-01/friends-page.json": "{}"
  });

  assert.throws(
    () =>
      scaffoldSnapshot({
        screen: "friends-page",
        today: "2026-06-01",
        root: "/repo",
        fsImpl,
        screensDoc
      }),
    /refusing to overwrite existing file snapshots\/2026-06-01\/friends-page\.json/
  );
});
```

- [ ] **Step 2: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS, because Task 2's implementation already throws on overwrite. If this test fails, fix `scripts/new-snapshot.js` to throw `refusing to overwrite existing file ${relativePath}` before adding the test as a separate commit.

- [ ] **Step 3: Commit**

Run:

```bash
rtk git add test/snapshot-scaffold.test.js
rtk git commit -m "test: assert snapshot scaffolder refuses overwrites"
```

Expected: commit succeeds and includes only the test file.

### Task 4: Scaffolder Rejects Unknown Screens

**Files:**
- Modify: `test/snapshot-scaffold.test.js`

- [ ] **Step 1: Add failing test**

Append to `test/snapshot-scaffold.test.js`:

```js
test("scaffoldSnapshot rejects screens that are not in registry/screens.yaml", () => {
  const fsImpl = makeFsImpl();

  assert.throws(
    () =>
      scaffoldSnapshot({
        screen: "ghost-screen",
        today: "2026-06-01",
        root: "/repo",
        fsImpl,
        screensDoc
      }),
    /unknown screen "ghost-screen"\. Add it to registry\/screens\.yaml first\./
  );
});
```

- [ ] **Step 2: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS, because Task 2's implementation already throws on unknown screens. If this test fails, fix `scripts/new-snapshot.js` to throw `unknown screen "${screen}". Add it to registry/screens.yaml first.` before adding the test as a separate commit.

- [ ] **Step 3: Commit**

Run:

```bash
rtk git add test/snapshot-scaffold.test.js
rtk git commit -m "test: assert snapshot scaffolder rejects unknown screens"
```

Expected: commit succeeds and includes only the test file.

### Task 5: Wire snapshot:new Into npm Scripts

**Files:**
- Modify: `package.json`

- [ ] **Step 1: Replace the `scripts` block in `package.json`**

Change:

```json
  "scripts": {
    "build": "node scripts/build-theme.js",
    "validate": "node scripts/validate-registry.js",
    "sync": "npm run check && node scripts/sync-to-vencord.js",
    "check": "npm run validate && npm run build",
    "test": "node --test"
  },
```

to:

```json
  "scripts": {
    "build": "node scripts/build-theme.js",
    "validate": "node scripts/validate-registry.js",
    "sync": "npm run check && node scripts/sync-to-vencord.js",
    "check": "npm run validate && npm run build",
    "test": "node --test",
    "snapshot:new": "node scripts/new-snapshot.js"
  },
```

- [ ] **Step 2: Confirm npm exposes the new script**

Run:

```bash
rtk npm run
```

Expected: the listing includes `snapshot:new` mapped to `node scripts/new-snapshot.js`.

- [ ] **Step 3: Run tests to confirm wiring did not regress anything**

Run:

```bash
rtk npm test
```

Expected: PASS for `build-contract.test.js`, `registry-cross-references.test.js`, `selector-usage-contract.test.js`, and all three subtests in `snapshot-scaffold.test.js`.

- [ ] **Step 4: Run repo check**

Run:

```bash
rtk npm run check
```

Expected: every `ok ...` line prints (including `ok registry cross-references` from Milestone 2) and the build completes with `Built dist/NewKemonoFriends.theme.css from 13 partials`.

- [ ] **Step 5: Commit**

Run:

```bash
rtk git add package.json
rtk git commit -m "chore: expose snapshot:new npm script"
```

Expected: commit succeeds and includes only `package.json`.

### Task 6: Append Helpers Section To docs/workflow.md

**Files:**
- Modify: `docs/workflow.md`

- [ ] **Step 1: Append a short Helpers section**

Append the exact block below to the end of `docs/workflow.md` (after `## Commit Shape`):

```markdown

## Helpers

- `rtk npm run snapshot:new -- <screen-id>` creates `snapshots/YYYY-MM-DD/<screen-id>.json` with placeholder metadata for the requested screen. The script refuses to overwrite an existing file and refuses screens that are not in `registry/screens.yaml`. Replace placeholder fields (`viewport`, `routeHint`, `sourceScreenshot`, and the `elements` array) before committing.
- `rtk npm test` runs the workspace contract suite, including:
  - `test/build-contract.test.js`: the generated theme follows the manifest output and partial order.
  - `test/registry-cross-references.test.js`: registry and snapshot cross-references hold.
  - `test/selector-usage-contract.test.js`: every class in `registry/selectors.yaml` is referenced inside its `cssOwner` partial.
  - `test/snapshot-scaffold.test.js`: the snapshot scaffolder enforces its contract.
- These tests do not launch a browser, do not open Discord, and do not touch the Vencord live theme directory.
```

- [ ] **Step 2: Confirm the file still scopes execution clearly**

Read `docs/workflow.md` and verify that `## Load Boundaries`, `## Standard Flow`, `## Test Boundaries`, `## Registry And Snapshot Rules`, and `## Commit Shape` are preserved in that order, with the new `## Helpers` section appended at the end.

- [ ] **Step 3: Commit**

Run:

```bash
rtk git add docs/workflow.md
rtk git commit -m "docs: document snapshot scaffolder and contract tests"
```

Expected: commit succeeds and includes only `docs/workflow.md`.

### Task 7: Final Verification

**Files:**
- Inspect: `scripts/new-snapshot.js`
- Inspect: `test/snapshot-scaffold.test.js`
- Inspect: `test/selector-usage-contract.test.js`
- Inspect: `package.json`
- Inspect: `docs/workflow.md`

- [ ] **Step 1: Run tests**

Run:

```bash
rtk npm test
```

Expected: PASS for `build-contract.test.js`, `registry-cross-references.test.js`, `selector-usage-contract.test.js`, and all three subtests in `snapshot-scaffold.test.js`.

- [ ] **Step 2: Run repo check**

Run:

```bash
rtk npm run check
```

Expected: every `ok ...` line prints (including `ok registry cross-references`) and the build completes with `Built dist/NewKemonoFriends.theme.css from 13 partials`.

- [ ] **Step 3: Confirm no scaffold side-effect leaked into the repo**

Run:

```bash
rtk git status
```

Expected: no untracked files under `snapshots/`. No command in this plan runs `rtk npm run snapshot:new` against the real repo; the scaffolder is exercised only inside `node:test` with an in-memory `fsImpl`.

- [ ] **Step 4: Confirm no sync happened**

Run:

```bash
rtk git diff --stat HEAD
```

Expected: no uncommitted changes. No command in this plan runs `rtk npm run sync`.

- [ ] **Step 5: Review scope boundaries**

Run:

```bash
rtk git log --oneline -10
```

Expected: commits map one-to-one with Tasks 1 through 6; only new files are `scripts/new-snapshot.js`, `test/snapshot-scaffold.test.js`, and `test/selector-usage-contract.test.js`; only modified files are `package.json` and `docs/workflow.md`. No `docs/agents/`, no PRD docs, no Playwright, no visual regression, no Discord live DOM automation, no Vencord live theme edits.

## Self-Review

- Spec coverage:
  - "Prepare the repo for small future user-driven Discord theme edits" — Task 2 adds the `snapshot:new` scaffolder, Task 5 wires it into `npm run snapshot:new`, Task 6 documents both helpers in `docs/workflow.md`.
  - "Add only minimal helpers/tests/docs needed to support intent → evidence → CSS → build/check → optional sync" — Plan adds one helper script, one drift contract test, one scaffolder contract test, and a short docs append; no new docs file, no new dependencies, no new build steps.
  - "Keep `src/` as source of truth and `dist/` generated" — Plan does not modify `src/**` or hand-edit `dist/**`; `dist/NewKemonoFriends.theme.css` only changes when `rtk npm run check` runs the build.
  - "Avoid broad redesign, visual regression, live DOM automation, and PRD/process bloat" — Plan does not import Playwright, does not launch any browser, does not edit live Discord DOM; no PRD, no issue tracker, no `docs/agents/` directory.
  - TDD coverage where required: Task 2 is red, then green, then commit; Tasks 3 and 4 add contract tests against the implementation from Task 2; Tasks 1, 5, 6 do not touch executable behavior and so do not require red, green, refactor cycles, but each still verifies behavior via `rtk npm test` and `rtk npm run check`.
- Placeholder scan: No `TODO`, no "later", no "fill in", no "similar to Task N", no untyped pseudo-code; every step shows complete code or an explicit command with expected output.
- Type and API consistency:
  - `scaffoldSnapshot({ screen, today, root, fsImpl, screensDoc })` is defined in Task 2 and consumed unchanged by Tasks 3 and 4 plus the CLI shim in Task 2.
  - The `fsImpl` shape (`existsSync`, `mkdirSync`, `writeFileSync`) used by the test helper `makeFsImpl` matches the calls made inside `scaffoldSnapshot`.
  - The `screensDoc` shape (`{ schemaVersion, screens: { <key>: { owns, importantSelectors, goals, knownRisks } } }`) matches `registry/screens.yaml` as written today and as validated by `schema/screens.schema.json`.
  - The selector-usage contract test reads `registry/selectors.yaml` in the same shape consumed by Milestone 2's cross-reference checks (`selectorsDoc.selectors[name].classes` and `selectorsDoc.selectors[name].cssOwner`).
- Scope check: No `docs/agents/`, no PRD workflow, no Playwright, no visual regression, no Discord live DOM automation, no sync invocation, no Vencord live theme edits, no `src/**` edits, no schema changes, no registry data changes.
