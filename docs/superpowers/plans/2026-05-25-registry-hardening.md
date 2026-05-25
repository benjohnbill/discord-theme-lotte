# Selector Registry And Snapshot Workflow Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tighten registry and snapshot cross-references so future selector knowledge updates fail loudly when they drift, without adding browser automation or visual regression.

**Architecture:** Extract pure cross-reference checks into `scripts/registry-checks.js` and wire them into `scripts/validate-registry.js`. Each check is a function that takes parsed registry/manifest structures and returns a list of error strings. `node:test` exercises each check on synthetic data; `npm run check` exercises them on the real repo. Schemas stay where they are.

**Tech Stack:** Node ESM, `node:test`, `node:assert/strict`, `yaml`, `ajv`, `fs`, `path`, `npm` scripts run through `rtk`.

---

## File Structure

- Create: `scripts/registry-checks.js`
  - Pure module. No top-level side effects. Exports cross-reference check functions that take parsed structures and return string arrays.
  - Functions: `checkSelectorsScreens`, `checkSelectorsCssOwners`, `checkSelectorsDoNotTouch`, `checkScreensOwns`, `checkScreensLatestSnapshot`, `checkSnapshotsScreens`, `checkSrcPartialsRegistered`.
- Modify: `scripts/validate-registry.js`
  - After existing schema validation and `paletteRole` check, call the new cross-reference functions and aggregate their errors.
  - Exits non-zero with a combined error message when any check fails.
- Create: `test/registry-cross-references.test.js`
  - One TDD-driven group of subtests per cross-reference function.
- Preserve: `test/build-contract.test.js`, `schema/*.json`, `registry/*.yaml`, `snapshots/**`.

## Non-Goals

- Do not change any `schema/*.json` file.
- Do not change `registry/*.yaml` or `snapshots/**` data.
- Do not add new `npm` scripts.
- Do not run `rtk npm run sync`.
- Do not edit the Vencord live theme directory.
- Do not introduce browser automation, visual regression, or Discord live DOM automation.
- Do not introduce PRD docs, issue tracking, or new milestone docs.
- Do not refactor unrelated parts of `scripts/validate-registry.js`.

## Tasks

### Task 1: Cross-Reference Module Tracer Bullet (selectors -> screens)

**Files:**
- Create: `test/registry-cross-references.test.js`
- Create: `scripts/registry-checks.js`

- [ ] **Step 1: Write the failing test**

Create `test/registry-cross-references.test.js`:

```js
import assert from "node:assert/strict";
import test from "node:test";

import { checkSelectorsScreens } from "../scripts/registry-checks.js";

const baseSelector = {
  screen: "x",
  classes: ["a"],
  cssOwner: "src/x.css",
  stability: "stable",
  action: "act",
  reason: "because"
};

const baseScreen = {
  owns: [],
  importantSelectors: [],
  goals: [],
  knownRisks: []
};

test("checkSelectorsScreens returns no errors when every selector screen exists", () => {
  const selectorsDoc = { schemaVersion: 1, selectors: { sel_a: baseSelector } };
  const screensDoc = { schemaVersion: 1, screens: { x: baseScreen } };
  assert.deepEqual(checkSelectorsScreens(selectorsDoc, screensDoc), []);
});

test("checkSelectorsScreens reports selectors that reference an unknown screen", () => {
  const selectorsDoc = {
    schemaVersion: 1,
    selectors: { sel_a: { ...baseSelector, screen: "missing" } }
  };
  const screensDoc = { schemaVersion: 1, screens: { x: baseScreen } };
  const errors = checkSelectorsScreens(selectorsDoc, screensDoc);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /sel_a: unknown screen "missing"/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
rtk npm test
```

Expected: FAIL with `Cannot find module '../scripts/registry-checks.js'` or equivalent missing-module error.

- [ ] **Step 3: Create the module with the first check**

Create `scripts/registry-checks.js`:

```js
export function checkSelectorsScreens(selectorsDoc, screensDoc) {
  const selectors = selectorsDoc?.selectors ?? {};
  const knownScreens = new Set(Object.keys(screensDoc?.screens ?? {}));
  const errors = [];

  for (const [name, entry] of Object.entries(selectors)) {
    if (!knownScreens.has(entry.screen)) {
      errors.push(`${name}: unknown screen "${entry.screen}"`);
    }
  }

  return errors;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS, with two new passing subtests inside `registry-cross-references.test.js` and the existing `build-contract.test.js` still passing.

- [ ] **Step 5: Commit**

Run:

```bash
rtk git add scripts/registry-checks.js test/registry-cross-references.test.js
rtk git commit -m "test: add selectors-to-screens cross-reference check"
```

Expected: commit succeeds and includes only the new module and test file.

### Task 2: selectors.cssOwner Must Be A Manifest Partial

**Files:**
- Modify: `test/registry-cross-references.test.js`
- Modify: `scripts/registry-checks.js`

- [ ] **Step 1: Add failing tests**

Append to `test/registry-cross-references.test.js`:

```js
import { checkSelectorsCssOwners } from "../scripts/registry-checks.js";

test("checkSelectorsCssOwners returns no errors when every cssOwner is in manifest.partials", () => {
  const selectorsDoc = {
    schemaVersion: 1,
    selectors: { sel_a: { ...baseSelector, cssOwner: "src/components/a.css" } }
  };
  const manifest = { partials: ["src/components/a.css", "src/components/b.css"] };
  assert.deepEqual(checkSelectorsCssOwners(selectorsDoc, manifest), []);
});

test("checkSelectorsCssOwners reports selectors whose cssOwner is not registered as a manifest partial", () => {
  const selectorsDoc = {
    schemaVersion: 1,
    selectors: { sel_a: { ...baseSelector, cssOwner: "src/components/orphan.css" } }
  };
  const manifest = { partials: ["src/components/a.css"] };
  const errors = checkSelectorsCssOwners(selectorsDoc, manifest);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /sel_a: cssOwner "src\/components\/orphan\.css" not listed in theme\.manifest\.yaml partials/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
rtk npm test
```

Expected: FAIL with `checkSelectorsCssOwners is not a function` or `is not exported`.

- [ ] **Step 3: Implement the check**

Append to `scripts/registry-checks.js`:

```js
export function checkSelectorsCssOwners(selectorsDoc, manifest) {
  const selectors = selectorsDoc?.selectors ?? {};
  const partials = new Set(manifest?.partials ?? []);
  const errors = [];

  for (const [name, entry] of Object.entries(selectors)) {
    if (!partials.has(entry.cssOwner)) {
      errors.push(`${name}: cssOwner "${entry.cssOwner}" not listed in theme.manifest.yaml partials`);
    }
  }

  return errors;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS with all subtests green.

- [ ] **Step 5: Commit**

Run:

```bash
rtk git add scripts/registry-checks.js test/registry-cross-references.test.js
rtk git commit -m "test: enforce selector cssOwner against manifest partials"
```

Expected: commit succeeds and includes only the module and test file.

### Task 3: selectors.doNotTouch Must Reference Real do-not-touch Entries

**Files:**
- Modify: `test/registry-cross-references.test.js`
- Modify: `scripts/registry-checks.js`

- [ ] **Step 1: Add failing tests**

Append to `test/registry-cross-references.test.js`:

```js
import { checkSelectorsDoNotTouch } from "../scripts/registry-checks.js";

const baseDoNotTouch = {
  screen: "x",
  reason: "fragile",
  allowedActions: ["inspect"]
};

test("checkSelectorsDoNotTouch returns no errors when doNotTouch references are all known", () => {
  const selectorsDoc = {
    schemaVersion: 1,
    selectors: { sel_a: { ...baseSelector, doNotTouch: ["wrapper_known"] } }
  };
  const doNotTouchDoc = { schemaVersion: 1, selectors: { wrapper_known: baseDoNotTouch } };
  assert.deepEqual(checkSelectorsDoNotTouch(selectorsDoc, doNotTouchDoc), []);
});

test("checkSelectorsDoNotTouch reports selectors with unknown doNotTouch references", () => {
  const selectorsDoc = {
    schemaVersion: 1,
    selectors: { sel_a: { ...baseSelector, doNotTouch: ["wrapper_missing"] } }
  };
  const doNotTouchDoc = { schemaVersion: 1, selectors: { wrapper_known: baseDoNotTouch } };
  const errors = checkSelectorsDoNotTouch(selectorsDoc, doNotTouchDoc);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /sel_a: doNotTouch entry "wrapper_missing" not declared in do-not-touch\.yaml/);
});

test("checkSelectorsDoNotTouch ignores selectors that have no doNotTouch list", () => {
  const selectorsDoc = { schemaVersion: 1, selectors: { sel_a: baseSelector } };
  const doNotTouchDoc = { schemaVersion: 1, selectors: {} };
  assert.deepEqual(checkSelectorsDoNotTouch(selectorsDoc, doNotTouchDoc), []);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
rtk npm test
```

Expected: FAIL with `checkSelectorsDoNotTouch is not a function` or `is not exported`.

- [ ] **Step 3: Implement the check**

Append to `scripts/registry-checks.js`:

```js
export function checkSelectorsDoNotTouch(selectorsDoc, doNotTouchDoc) {
  const selectors = selectorsDoc?.selectors ?? {};
  const known = new Set(Object.keys(doNotTouchDoc?.selectors ?? {}));
  const errors = [];

  for (const [name, entry] of Object.entries(selectors)) {
    for (const reference of entry.doNotTouch ?? []) {
      if (!known.has(reference)) {
        errors.push(`${name}: doNotTouch entry "${reference}" not declared in do-not-touch.yaml`);
      }
    }
  }

  return errors;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS with all subtests green.

- [ ] **Step 5: Commit**

Run:

```bash
rtk git add scripts/registry-checks.js test/registry-cross-references.test.js
rtk git commit -m "test: enforce selector doNotTouch references against do-not-touch registry"
```

Expected: commit succeeds and includes only the module and test file.

### Task 4: screens.owns Entries Must Be Manifest Partials

**Files:**
- Modify: `test/registry-cross-references.test.js`
- Modify: `scripts/registry-checks.js`

- [ ] **Step 1: Add failing tests**

Append to `test/registry-cross-references.test.js`:

```js
import { checkScreensOwns } from "../scripts/registry-checks.js";

test("checkScreensOwns returns no errors when every owned path is in manifest.partials", () => {
  const screensDoc = {
    schemaVersion: 1,
    screens: { x: { ...baseScreen, owns: ["src/components/a.css"] } }
  };
  const manifest = { partials: ["src/components/a.css", "src/base/palette.css"] };
  assert.deepEqual(checkScreensOwns(screensDoc, manifest), []);
});

test("checkScreensOwns reports screens that own paths missing from manifest.partials", () => {
  const screensDoc = {
    schemaVersion: 1,
    screens: { x: { ...baseScreen, owns: ["src/components/orphan.css"] } }
  };
  const manifest = { partials: ["src/components/a.css"] };
  const errors = checkScreensOwns(screensDoc, manifest);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /x: owns "src\/components\/orphan\.css" not listed in theme\.manifest\.yaml partials/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
rtk npm test
```

Expected: FAIL with `checkScreensOwns is not a function` or `is not exported`.

- [ ] **Step 3: Implement the check**

Append to `scripts/registry-checks.js`:

```js
export function checkScreensOwns(screensDoc, manifest) {
  const screens = screensDoc?.screens ?? {};
  const partials = new Set(manifest?.partials ?? []);
  const errors = [];

  for (const [name, entry] of Object.entries(screens)) {
    for (const owned of entry.owns ?? []) {
      if (!partials.has(owned)) {
        errors.push(`${name}: owns "${owned}" not listed in theme.manifest.yaml partials`);
      }
    }
  }

  return errors;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS with all subtests green.

- [ ] **Step 5: Commit**

Run:

```bash
rtk git add scripts/registry-checks.js test/registry-cross-references.test.js
rtk git commit -m "test: enforce screen-owned paths against manifest partials"
```

Expected: commit succeeds and includes only the module and test file.

### Task 5: screens.latestSnapshot Must Resolve To An Existing File

**Files:**
- Modify: `test/registry-cross-references.test.js`
- Modify: `scripts/registry-checks.js`

- [ ] **Step 1: Add failing tests**

Append to `test/registry-cross-references.test.js`:

```js
import { checkScreensLatestSnapshot } from "../scripts/registry-checks.js";

test("checkScreensLatestSnapshot returns no errors when each latestSnapshot exists according to the predicate", () => {
  const screensDoc = {
    schemaVersion: 1,
    screens: {
      x: { ...baseScreen, latestSnapshot: "snapshots/2026-05-25/x.json" }
    }
  };
  const exists = (relativePath) => relativePath === "snapshots/2026-05-25/x.json";
  assert.deepEqual(checkScreensLatestSnapshot(screensDoc, exists), []);
});

test("checkScreensLatestSnapshot reports screens whose latestSnapshot file is missing", () => {
  const screensDoc = {
    schemaVersion: 1,
    screens: {
      x: { ...baseScreen, latestSnapshot: "snapshots/2026-05-25/missing.json" }
    }
  };
  const exists = () => false;
  const errors = checkScreensLatestSnapshot(screensDoc, exists);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /x: latestSnapshot "snapshots\/2026-05-25\/missing\.json" does not exist on disk/);
});

test("checkScreensLatestSnapshot ignores screens without latestSnapshot", () => {
  const screensDoc = { schemaVersion: 1, screens: { x: baseScreen } };
  const exists = () => false;
  assert.deepEqual(checkScreensLatestSnapshot(screensDoc, exists), []);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
rtk npm test
```

Expected: FAIL with `checkScreensLatestSnapshot is not a function` or `is not exported`.

- [ ] **Step 3: Implement the check**

Append to `scripts/registry-checks.js`:

```js
export function checkScreensLatestSnapshot(screensDoc, exists) {
  const screens = screensDoc?.screens ?? {};
  const errors = [];

  for (const [name, entry] of Object.entries(screens)) {
    if (typeof entry.latestSnapshot !== "string") continue;
    if (!exists(entry.latestSnapshot)) {
      errors.push(`${name}: latestSnapshot "${entry.latestSnapshot}" does not exist on disk`);
    }
  }

  return errors;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS with all subtests green.

- [ ] **Step 5: Commit**

Run:

```bash
rtk git add scripts/registry-checks.js test/registry-cross-references.test.js
rtk git commit -m "test: enforce screen latestSnapshot paths against disk"
```

Expected: commit succeeds and includes only the module and test file.

### Task 6: snapshot.screen Must Reference A Real Screen

**Files:**
- Modify: `test/registry-cross-references.test.js`
- Modify: `scripts/registry-checks.js`

- [ ] **Step 1: Add failing tests**

Append to `test/registry-cross-references.test.js`:

```js
import { checkSnapshotsScreens } from "../scripts/registry-checks.js";

test("checkSnapshotsScreens returns no errors when every snapshot screen is known", () => {
  const screensDoc = { schemaVersion: 1, screens: { x: baseScreen } };
  const snapshots = [
    { path: "snapshots/2026-05-25/a.json", data: { screen: "x" } }
  ];
  assert.deepEqual(checkSnapshotsScreens(snapshots, screensDoc), []);
});

test("checkSnapshotsScreens reports snapshots whose screen is not in screens.yaml", () => {
  const screensDoc = { schemaVersion: 1, screens: { x: baseScreen } };
  const snapshots = [
    { path: "snapshots/2026-05-25/a.json", data: { screen: "ghost" } }
  ];
  const errors = checkSnapshotsScreens(snapshots, screensDoc);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /snapshots\/2026-05-25\/a\.json: unknown screen "ghost"/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
rtk npm test
```

Expected: FAIL with `checkSnapshotsScreens is not a function` or `is not exported`.

- [ ] **Step 3: Implement the check**

Append to `scripts/registry-checks.js`:

```js
export function checkSnapshotsScreens(snapshots, screensDoc) {
  const known = new Set(Object.keys(screensDoc?.screens ?? {}));
  const errors = [];

  for (const { path: snapshotPath, data } of snapshots) {
    if (!known.has(data?.screen)) {
      errors.push(`${snapshotPath}: unknown screen "${data?.screen}"`);
    }
  }

  return errors;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS with all subtests green.

- [ ] **Step 5: Commit**

Run:

```bash
rtk git add scripts/registry-checks.js test/registry-cross-references.test.js
rtk git commit -m "test: enforce snapshot screen against screens registry"
```

Expected: commit succeeds and includes only the module and test file.

### Task 7: Every src CSS Partial Must Be Registered In The Manifest

**Files:**
- Modify: `test/registry-cross-references.test.js`
- Modify: `scripts/registry-checks.js`

- [ ] **Step 1: Add failing tests**

Append to `test/registry-cross-references.test.js`:

```js
import { checkSrcPartialsRegistered } from "../scripts/registry-checks.js";

test("checkSrcPartialsRegistered returns no errors when every src css file is a manifest partial", () => {
  const manifest = { partials: ["src/a.css", "src/b.css"] };
  const srcCssFiles = ["src/a.css", "src/b.css"];
  assert.deepEqual(checkSrcPartialsRegistered(srcCssFiles, manifest), []);
});

test("checkSrcPartialsRegistered reports src css files that are missing from manifest.partials", () => {
  const manifest = { partials: ["src/a.css"] };
  const srcCssFiles = ["src/a.css", "src/orphan.css"];
  const errors = checkSrcPartialsRegistered(srcCssFiles, manifest);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /src\/orphan\.css: not listed in theme\.manifest\.yaml partials/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
rtk npm test
```

Expected: FAIL with `checkSrcPartialsRegistered is not a function` or `is not exported`.

- [ ] **Step 3: Implement the check**

Append to `scripts/registry-checks.js`:

```js
export function checkSrcPartialsRegistered(srcCssFiles, manifest) {
  const partials = new Set(manifest?.partials ?? []);
  const errors = [];

  for (const file of srcCssFiles) {
    if (!partials.has(file)) {
      errors.push(`${file}: not listed in theme.manifest.yaml partials`);
    }
  }

  return errors;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS with all subtests green.

- [ ] **Step 5: Commit**

Run:

```bash
rtk git add scripts/registry-checks.js test/registry-cross-references.test.js
rtk git commit -m "test: enforce src css files are registered as manifest partials"
```

Expected: commit succeeds and includes only the module and test file.

### Task 8: Wire All Cross-Reference Checks Into validate-registry

**Files:**
- Modify: `scripts/validate-registry.js`

- [ ] **Step 1: Replace `scripts/validate-registry.js` with the wired version**

Replace the entire file with:

```js
import fs from "node:fs";
import path from "node:path";
import Ajv2020 from "ajv/dist/2020.js";
import YAML from "yaml";

import {
  checkScreensLatestSnapshot,
  checkScreensOwns,
  checkSelectorsCssOwners,
  checkSelectorsDoNotTouch,
  checkSelectorsScreens,
  checkSnapshotsScreens,
  checkSrcPartialsRegistered
} from "./registry-checks.js";

const root = process.cwd();
const ajv = new Ajv2020({ allErrors: true });

function loadJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
}

function loadYaml(relativePath) {
  return YAML.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
}

function validate(name, schemaPath, dataPath, loader) {
  const schema = loadJson(schemaPath);
  const data = loader(dataPath);
  const validateFn = ajv.compile(schema);

  if (!validateFn(data)) {
    const details = ajv.errorsText(validateFn.errors, { separator: "\n" });
    throw new Error(`${name} failed validation:\n${details}`);
  }

  console.log(`ok ${dataPath}`);
  return data;
}

function assertNoSnapshotPlaceholders(relativePath, snapshot) {
  const placeholders = Object.entries(snapshot)
    .filter(([, value]) => typeof value === "string")
    .filter(([, value]) => value === "unknown" || value.startsWith("replace-with-"))
    .map(([key, value]) => `${key}: ${value}`);

  if (placeholders.length > 0) {
    throw new Error(`${relativePath} contains placeholder metadata:\n${placeholders.join("\n")}`);
  }
}

const palette = validate("palette", "schema/palette.schema.json", "registry/palette.yaml", loadYaml);
const screensDoc = validate("screens", "schema/screens.schema.json", "registry/screens.yaml", loadYaml);
const selectorsDoc = validate("selectors", "schema/selectors.schema.json", "registry/selectors.yaml", loadYaml);
const doNotTouchDoc = validate("do-not-touch", "schema/do-not-touch.schema.json", "registry/do-not-touch.yaml", loadYaml);
validate("risks", "schema/risks.schema.json", "registry/risks.yaml", loadYaml);

const paletteRoles = new Set(Object.keys(palette.palette ?? {}));
const unknownRoles = Object.entries(selectorsDoc.selectors ?? {})
  .filter(([, selector]) => selector.paletteRole && !paletteRoles.has(selector.paletteRole))
  .map(([name, selector]) => `${name}: ${selector.paletteRole}`);

if (unknownRoles.length > 0) {
  throw new Error(`selectors reference unknown paletteRole values:\n${unknownRoles.join("\n")}`);
}

const manifest = YAML.parse(fs.readFileSync(path.join(root, "theme.manifest.yaml"), "utf8"));

const snapshots = [];
const snapshotSchema = loadJson("schema/snapshot.schema.json");
const validateSnapshot = ajv.compile(snapshotSchema);
const snapshotsRoot = path.join(root, "snapshots");

if (fs.existsSync(snapshotsRoot)) {
  for (const dateDir of fs.readdirSync(snapshotsRoot).sort()) {
    const fullDateDir = path.join(snapshotsRoot, dateDir);
    if (!fs.statSync(fullDateDir).isDirectory()) continue;

    for (const file of fs.readdirSync(fullDateDir).sort()) {
      if (!file.endsWith(".json")) continue;

      const relativePath = path.join("snapshots", dateDir, file);
      const data = loadJson(relativePath);
      if (!validateSnapshot(data)) {
        const details = ajv.errorsText(validateSnapshot.errors, { separator: "\n" });
        throw new Error(`${relativePath} failed validation:\n${details}`);
      }

      assertNoSnapshotPlaceholders(relativePath, data);
      snapshots.push({ path: relativePath, data });
      console.log(`ok ${relativePath}`);
    }
  }
}

function listSrcCssFiles() {
  const srcRoot = path.join(root, "src");
  const collected = [];

  function walk(absoluteDir) {
    const entries = fs
      .readdirSync(absoluteDir, { withFileTypes: true })
      .sort((a, b) => a.name.localeCompare(b.name));

    for (const entry of entries) {
      const absolutePath = path.join(absoluteDir, entry.name);
      if (entry.isDirectory()) {
        walk(absolutePath);
        continue;
      }
      if (!entry.name.endsWith(".css")) continue;
      collected.push(path.relative(root, absolutePath));
    }
  }

  if (fs.existsSync(srcRoot)) {
    walk(srcRoot);
  }
  return collected;
}

const existsOnDisk = (relativePath) => fs.existsSync(path.join(root, relativePath));
const srcCssFiles = listSrcCssFiles();

const crossErrors = [
  ...checkSelectorsScreens(selectorsDoc, screensDoc),
  ...checkSelectorsCssOwners(selectorsDoc, manifest),
  ...checkSelectorsDoNotTouch(selectorsDoc, doNotTouchDoc),
  ...checkScreensOwns(screensDoc, manifest),
  ...checkScreensLatestSnapshot(screensDoc, existsOnDisk),
  ...checkSnapshotsScreens(snapshots, screensDoc),
  ...checkSrcPartialsRegistered(srcCssFiles, manifest)
];

if (crossErrors.length > 0) {
  throw new Error(`cross-reference checks failed:\n${crossErrors.join("\n")}`);
}

console.log("ok registry cross-references");
```

- [ ] **Step 2: Run unit tests to confirm the module is untouched**

Run:

```bash
rtk npm test
```

Expected: PASS with `build-contract.test.js` and all subtests in `registry-cross-references.test.js` green.

- [ ] **Step 3: Run the full check against real repo state**

Run:

```bash
rtk npm run check
```

Expected output (the new `ok registry cross-references` line appears after all schema/snapshot lines and before the build line):

```text
ok registry/palette.yaml
ok registry/screens.yaml
ok registry/selectors.yaml
ok registry/do-not-touch.yaml
ok registry/risks.yaml
ok snapshots/2026-05-25/call-screen-share-view.json
ok snapshots/2026-05-25/friends-page.json
ok snapshots/2026-05-25/server-sidebar-dm-selected.json
ok snapshots/2026-05-25/voice-panel.json
ok registry cross-references
Built dist/NewKemonoFriends.theme.css from 13 partials
```

If `cross-reference checks failed:` appears, the registries already drifted; stop and fix the registries before continuing.

- [ ] **Step 4: Commit**

Run:

```bash
rtk git add scripts/validate-registry.js dist/NewKemonoFriends.theme.css
rtk git commit -m "feat: validate registry cross-references in npm run check"
```

Expected: commit succeeds. If `dist/NewKemonoFriends.theme.css` is unchanged after build, Git will only include `scripts/validate-registry.js`; that is acceptable.

### Task 9: Final Verification

**Files:**
- Inspect: `scripts/registry-checks.js`
- Inspect: `scripts/validate-registry.js`
- Inspect: `test/registry-cross-references.test.js`

- [ ] **Step 1: Run tests**

Run:

```bash
rtk npm test
```

Expected: PASS with `build-contract.test.js` and `registry-cross-references.test.js` green.

- [ ] **Step 2: Run repo check**

Run:

```bash
rtk npm run check
```

Expected: every `ok ...` line prints, including `ok registry cross-references`, and the build completes with `Built dist/NewKemonoFriends.theme.css from 13 partials`.

- [ ] **Step 3: Confirm no sync happened**

Run:

```bash
rtk git diff --stat HEAD
```

Expected: no uncommitted changes. No command in this plan runs `rtk npm run sync`.

- [ ] **Step 4: Review scope boundaries**

Run:

```bash
rtk git status
rtk git log --oneline -12
```

Expected: only new files are `scripts/registry-checks.js` and `test/registry-cross-references.test.js`; only modified script is `scripts/validate-registry.js`; no `docs/agents/`, no PRD docs, no browser automation files, no visual regression files; commits map one-to-one with tasks 1 through 8.

## Self-Review

- Spec coverage:
  - "Improve registry/snapshot contract tests using `node:test`" — Tasks 1 through 7 add seven cross-reference checks, each driven by `node:test` with red, green, commit.
  - "Make selector knowledge updates safer and easier for future agents" — Task 8 wires every new check into `npm run check`, which is the existing pre-sync gate.
  - "Keep registries as structured memory, not prose docs" — Plan adds no new prose docs; all behavior lives in code, tests, and existing YAML registries.
  - "Avoid visual/browser automation in this milestone" — Plan does not import Playwright, does not launch any browser, does not read live Discord DOM.
- Placeholder scan: No `TODO`, no "later", no "fill in", no "similar to Task N", no untyped pseudo-code; every step has either complete code or an explicit command and expected output.
- Type and API consistency:
  - All seven check functions are named in the same camelCase shape, exported from `scripts/registry-checks.js`, imported in both `test/registry-cross-references.test.js` and `scripts/validate-registry.js`.
  - `checkScreensLatestSnapshot` takes an injected `exists` predicate; the CLI passes `(relativePath) => fs.existsSync(path.join(root, relativePath))`; tests pass simple functions.
  - `checkSnapshotsScreens` takes a `snapshots` array of `{ path, data }`; `validate-registry.js` builds that array in the same shape while walking `snapshots/**/*.json`.
- Scope check: No `docs/agents/`, no PRD workflow, no Playwright, no visual regression, no Discord live DOM automation, no sync invocation, no Vencord live theme edits.
