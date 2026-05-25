# Discord DOM Probe And Archive Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify registry entries against the real Discord Desktop DOM through CDP and provide an append-only archive workflow for outdated selectors, so the repo can stay aligned with Discord changes without manual lore-drift surveillance.

**Architecture:** A pure `scripts/archive-lib.js` module produces archive entries and edits parsed registry/archive documents in memory. A thin `scripts/archive-entry.js` CLI loads YAML, calls the lib, writes both files. A pure `scripts/probe-lib.js` module gathers classes per screen and summarizes probe results; its `probeScreen()` orchestrator takes an injected `cdpClient` so tests stay disk-free and network-free. A thin `scripts/probe-discord-dom.js` CLI builds a real CDP client via native `fetch` + `WebSocket` (Node 22+) and connects to a Discord Desktop renderer exposed via `--remote-debugging-port`. `registry/archive.yaml` is a single append-only file. `validate-registry.js` schema-validates it. `docs/workflow.md` gets two short appended sections (CDP setup + probe/archive workflow). Phase 1 keeps Discord navigation manual; the agent only reads DOM through `document.querySelectorAll`.

**Tech Stack:** Node 22+ ESM, `node:test`, `node:assert/strict`, native `fetch`, native `WebSocket`, `yaml`, `ajv`, `fs`, `path`, `npm` scripts run through `rtk`. No new dependencies.

---

## File Structure

- Create: `registry/archive.yaml`
  - Single append-only YAML file. Shape: `{ schemaVersion: 1, entries: [...] }`.
  - Initial commit contains the empty `entries: []`.
- Create: `schema/archive.schema.json`
  - JSON Schema (Draft 2020-12) for `registry/archive.yaml`. Validates entry fields: `archivedAt`, `fromFile`, `key`, `snapshot`, `reason`, optional `evidence`, optional `replacedBy`.
- Create: `scripts/archive-lib.js`
  - Pure module. No I/O. Exports: `buildArchiveEntry`, `appendToArchive`, `removeFromRegistry`.
- Create: `scripts/archive-entry.js`
  - Thin CLI wrapper. Parses argv, reads YAML, calls `archive-lib`, writes YAML.
- Create: `scripts/probe-lib.js`
  - Pure-ish module. Exports: `gatherProbeClasses`, `summarizeProbeResults`, `probeScreen` (takes injected `cdpClient`).
- Create: `scripts/probe-discord-dom.js`
  - Thin CLI. Builds real `cdpClient` (native `fetch` + `WebSocket`), parses argv, calls `probeScreen`, prints JSON.
- Create: `test/archive-lib.test.js`
  - TDD tests for `archive-lib.js`.
- Create: `test/probe-lib.test.js`
  - TDD tests for `probe-lib.js` including `probeScreen` with a fake `cdpClient`.
- Modify: `scripts/validate-registry.js`
  - Add Ajv schema validation for `registry/archive.yaml` after the existing five registries.
  - Do NOT add cross-reference checks for archive entries in M4 v1 (live registries already enforce uniqueness; archive is forensic-only).
- Modify: `package.json`
  - Add `"archive": "node scripts/archive-entry.js"` and `"probe": "node scripts/probe-discord-dom.js"` scripts.
  - Add `"engines": { "node": ">=22" }` to declare native `WebSocket` requirement.
- Modify: `docs/workflow.md`
  - Append one "Discord CDP setup" section (Task 0).
  - Append one "Probe and archive workflow" section (Task 6).
- Preserve: every other file. No edits to `scripts/build-theme.js`, `scripts/sync-to-vencord.js`, `scripts/inspect-dom.js`, `scripts/registry-checks.js`, `registry/*.yaml` (other than the new archive.yaml), `schema/*.json` (other than the new archive schema), `src/**`, `snapshots/**`, `theme.manifest.yaml`, `AGENTS.md`, `CONTEXT.md`, `dist/**`.

## Non-Goals

- Do not automate Discord navigation. Phase 1 is read-only `document.querySelectorAll` against whichever screen the user has open.
- Do not auto-remove CSS blocks when archiving a registry entry. Archive only touches `registry/archive.yaml` and the source registry YAML. Orphan CSS is acceptable forensic residue; the user/agent prunes manually.
- Do not support archiving entries from `registry/screens.yaml`, `registry/palette.yaml`, or `registry/risks.yaml` in M4 v1. Only `registry/selectors.yaml` and `registry/do-not-touch.yaml` entries.
- Do not introduce browser automation libraries (Playwright, puppeteer, browser-use, chrome-remote-interface). Use the Node 22+ built-ins only.
- Do not add cross-reference checks that compare `archive.yaml` to live registries (no key-uniqueness, no replacedBy-resolution).
- Do not run `rtk npm run sync`.
- Do not edit the Vencord live theme directory.
- Do not commit `dist/NewKemonoFriends.theme.css` unless `rtk npm run build` actually changed it.
- Do not invoke `rtk npm run probe` against the real Discord during the plan execution. Probe is exercised only through unit tests with a fake `cdpClient`. The user will run the real probe in subsequent sessions after Task 0's manual setup.

## Tasks

### Task 0: Document Discord CDP Setup

**Files:**
- Modify: `docs/workflow.md`

- [ ] **Step 1: Append the CDP setup section**

Append the exact block below to the end of `docs/workflow.md` (after the existing `## Commit Shape` section):

```markdown

## Discord CDP Setup (one-time)

The probe workflow needs Discord Desktop to expose Chrome DevTools Protocol on port 9333. This is a one-time Windows-side setup.

### Windows side

1. Locate the Discord shortcut (Start Menu or Desktop). The user's launcher path is `C:\Users\benjohnbill\AppData\Local\Discord\Update.exe`. Right-click the shortcut, choose Properties, and set Target to:

   ```
   C:\Users\benjohnbill\AppData\Local\Discord\Update.exe --processStart Discord.exe --process-start-args "--remote-debugging-port=9333"
   ```

2. Fully quit Discord, including the system tray icon. Relaunch Discord via the modified shortcut.

3. Verify in Windows PowerShell:

   ```powershell
   curl http://localhost:9333/json/version
   ```

   The response is a JSON object that includes `Browser`, `Protocol-Version`, and `webSocketDebuggerUrl`. If the response is empty or the connection is refused, Discord was not relaunched through the modified shortcut.

4. Open an elevated Command Prompt and run:

   ```
   netsh interface portproxy add v4tov4 listenport=9333 listenaddress=0.0.0.0 connectport=9333 connectaddress=127.0.0.1
   ```

   This makes Windows listen on every interface at port 9333 and forward to local 9333 so WSL can reach the Discord CDP endpoint. The portproxy survives reboot.

5. If Windows Defender Firewall blocks inbound TCP 9333, add an allow rule scoped to the WSL subnet. The portproxy listens on `0.0.0.0`; on an untrusted network this is exposed to LAN. Only enable on trusted personal machines.

### WSL side

1. Find the Windows host IP visible from WSL:

   ```bash
   WINDOWS_HOST=$(ip route show default | awk '{print $3}')
   echo "$WINDOWS_HOST"
   ```

2. Verify the endpoint:

   ```bash
   curl "http://${WINDOWS_HOST}:9333/json/version"
   ```

3. Export the URL so the probe CLI sees it:

   ```bash
   export DISCORD_CDP_URL="http://${WINDOWS_HOST}:9333"
   ```

   Add this line to `~/.zshenv` (or your shell's env file) to make it persistent.

`DISCORD_CDP_URL` is intentionally separate from `BU_CDP_URL` so the browser-harness Chrome session and the Discord renderer session do not collide.
```

- [ ] **Step 2: Confirm the section is at the end of the file**

Run:

```bash
rtk tail -50 docs/workflow.md
```

Expected: the file ends with the `## Discord CDP Setup (one-time)` section, the existing earlier sections (`## Load Boundaries`, `## Standard Flow`, `## Test Boundaries`, `## Registry And Snapshot Rules`, `## Commit Shape`) are intact above it.

- [ ] **Step 3: Commit**

Run:

```bash
rtk git add docs/workflow.md
rtk git commit -m "docs: document Discord CDP setup for probe workflow"
```

Expected: commit succeeds and includes only `docs/workflow.md`.

### Task 1: Add archive.yaml Schema And Empty File

**Files:**
- Create: `schema/archive.schema.json`
- Create: `registry/archive.yaml`
- Modify: `scripts/validate-registry.js`

- [ ] **Step 1: Create the schema**

Create `schema/archive.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "archive.schema.json",
  "type": "object",
  "required": ["schemaVersion", "entries"],
  "properties": {
    "schemaVersion": { "const": 1 },
    "entries": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["archivedAt", "fromFile", "key", "snapshot", "reason"],
        "properties": {
          "archivedAt": { "type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$" },
          "fromFile": { "type": "string" },
          "key": { "type": "string" },
          "snapshot": { "type": "object" },
          "reason": { "type": "string" },
          "evidence": { "type": "string" },
          "replacedBy": { "type": "string" }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

- [ ] **Step 2: Create the empty archive file**

Create `registry/archive.yaml`:

```yaml
schemaVersion: 1
entries: []
```

- [ ] **Step 3: Wire schema validation into `scripts/validate-registry.js`**

Open `scripts/validate-registry.js`. Find the existing `validate("risks", ...)` call. Append one more `validate(...)` line immediately after it.

Change:

```js
validate("risks", "schema/risks.schema.json", "registry/risks.yaml", loadYaml);
```

to:

```js
validate("risks", "schema/risks.schema.json", "registry/risks.yaml", loadYaml);
validate("archive", "schema/archive.schema.json", "registry/archive.yaml", loadYaml);
```

- [ ] **Step 4: Run repo check to confirm archive validates**

Run:

```bash
rtk npm run check
```

Expected output includes a new line `ok registry/archive.yaml` between `ok registry/risks.yaml` and the snapshot lines:

```text
ok registry/palette.yaml
ok registry/screens.yaml
ok registry/selectors.yaml
ok registry/do-not-touch.yaml
ok registry/risks.yaml
ok registry/archive.yaml
ok snapshots/2026-05-25/call-screen-share-view.json
...
ok registry cross-references
Built dist/NewKemonoFriends.theme.css from 13 partials
```

- [ ] **Step 5: Run unit tests to confirm no regression**

Run:

```bash
rtk npm test
```

Expected: 17 tests pass (build-contract + 16 cross-reference subtests). No new tests added in this task.

- [ ] **Step 6: Commit**

Run:

```bash
rtk git add schema/archive.schema.json registry/archive.yaml scripts/validate-registry.js
rtk git commit -m "feat: add archive.yaml registry with schema validation"
```

Expected: commit succeeds and includes exactly three files.

### Task 2: Pure Archive Functions With TDD

**Files:**
- Create: `test/archive-lib.test.js`
- Create: `scripts/archive-lib.js`

- [ ] **Step 1: Write the failing test for `buildArchiveEntry`**

Create `test/archive-lib.test.js`:

```js
import assert from "node:assert/strict";
import test from "node:test";

import {
  appendToArchive,
  buildArchiveEntry,
  removeFromRegistry
} from "../scripts/archive-lib.js";

const originalEntry = {
  screen: "voice-panel",
  classes: ["button__67645"],
  cssOwner: "src/components/voice-panel.css",
  stability: "hashed",
  action: "style primary voice actions",
  reason: "aria labels were not sufficient"
};

test("buildArchiveEntry assembles a complete archive entry from required fields", () => {
  const entry = buildArchiveEntry({
    key: "voice_primary_actions",
    fromFile: "registry/selectors.yaml",
    originalEntry,
    reason: "button__67645 not observed in Discord probe on 2026-08-12",
    archivedAt: "2026-08-12"
  });

  assert.equal(entry.archivedAt, "2026-08-12");
  assert.equal(entry.fromFile, "registry/selectors.yaml");
  assert.equal(entry.key, "voice_primary_actions");
  assert.deepEqual(entry.snapshot, originalEntry);
  assert.equal(entry.reason, "button__67645 not observed in Discord probe on 2026-08-12");
  assert.equal(entry.evidence, undefined);
  assert.equal(entry.replacedBy, undefined);
});

test("buildArchiveEntry includes optional evidence and replacedBy when provided", () => {
  const entry = buildArchiveEntry({
    key: "voice_primary_actions",
    fromFile: "registry/selectors.yaml",
    originalEntry,
    reason: "replaced after Discord 2026-08 redesign",
    archivedAt: "2026-08-12",
    evidence: "snapshots/2026-08-12/voice-panel.json",
    replacedBy: "voice_primary_actions_v2"
  });

  assert.equal(entry.evidence, "snapshots/2026-08-12/voice-panel.json");
  assert.equal(entry.replacedBy, "voice_primary_actions_v2");
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
rtk npm test
```

Expected: FAIL with `Cannot find module '../scripts/archive-lib.js'` or equivalent missing-module error.

- [ ] **Step 3: Create the module with `buildArchiveEntry`**

Create `scripts/archive-lib.js`:

```js
export function buildArchiveEntry({
  key,
  fromFile,
  originalEntry,
  reason,
  archivedAt,
  evidence,
  replacedBy
}) {
  const entry = {
    archivedAt,
    fromFile,
    key,
    snapshot: originalEntry,
    reason
  };

  if (typeof evidence === "string") entry.evidence = evidence;
  if (typeof replacedBy === "string") entry.replacedBy = replacedBy;

  return entry;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS with 19 tests total (17 prior + 2 new).

- [ ] **Step 5: Add `appendToArchive` test**

Append to `test/archive-lib.test.js`:

```js
test("appendToArchive returns a new archive document with the entry appended", () => {
  const archiveDoc = { schemaVersion: 1, entries: [] };
  const entry = buildArchiveEntry({
    key: "k",
    fromFile: "registry/selectors.yaml",
    originalEntry,
    reason: "r",
    archivedAt: "2026-08-12"
  });

  const next = appendToArchive(archiveDoc, entry);
  assert.equal(next.schemaVersion, 1);
  assert.equal(next.entries.length, 1);
  assert.deepEqual(next.entries[0], entry);
});

test("appendToArchive does not mutate the input archive document", () => {
  const archiveDoc = { schemaVersion: 1, entries: [] };
  const entry = buildArchiveEntry({
    key: "k",
    fromFile: "registry/selectors.yaml",
    originalEntry,
    reason: "r",
    archivedAt: "2026-08-12"
  });

  appendToArchive(archiveDoc, entry);
  assert.equal(archiveDoc.entries.length, 0);
});
```

- [ ] **Step 6: Run test to verify it fails**

Run:

```bash
rtk npm test
```

Expected: FAIL with `appendToArchive is not a function` or `is not exported`.

- [ ] **Step 7: Implement `appendToArchive`**

Append to `scripts/archive-lib.js`:

```js
export function appendToArchive(archiveDoc, entry) {
  const existingEntries = archiveDoc?.entries ?? [];
  return {
    ...archiveDoc,
    schemaVersion: archiveDoc?.schemaVersion ?? 1,
    entries: [...existingEntries, entry]
  };
}
```

- [ ] **Step 8: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS with 21 tests total.

- [ ] **Step 9: Add `removeFromRegistry` test**

Append to `test/archive-lib.test.js`:

```js
test("removeFromRegistry returns a new registry document with the named entry removed from the named root", () => {
  const registryDoc = {
    schemaVersion: 1,
    selectors: {
      voice_primary_actions: originalEntry,
      friends_page_body: { ...originalEntry, screen: "friends-page" }
    }
  };

  const next = removeFromRegistry(registryDoc, "selectors", "voice_primary_actions");
  assert.equal(next.schemaVersion, 1);
  assert.equal(Object.keys(next.selectors).length, 1);
  assert.ok(!("voice_primary_actions" in next.selectors));
  assert.ok("friends_page_body" in next.selectors);
});

test("removeFromRegistry does not mutate the input registry document", () => {
  const registryDoc = {
    schemaVersion: 1,
    selectors: { voice_primary_actions: originalEntry }
  };

  removeFromRegistry(registryDoc, "selectors", "voice_primary_actions");
  assert.ok("voice_primary_actions" in registryDoc.selectors);
});

test("removeFromRegistry throws when the key is missing", () => {
  const registryDoc = { schemaVersion: 1, selectors: { a: originalEntry } };

  assert.throws(
    () => removeFromRegistry(registryDoc, "selectors", "missing"),
    /key "missing" not found under "selectors"/
  );
});
```

- [ ] **Step 10: Run test to verify it fails**

Run:

```bash
rtk npm test
```

Expected: FAIL with `removeFromRegistry is not a function` or `is not exported`.

- [ ] **Step 11: Implement `removeFromRegistry`**

Append to `scripts/archive-lib.js`:

```js
export function removeFromRegistry(registryDoc, rootKey, entryKey) {
  const root = registryDoc?.[rootKey];
  if (!root || !(entryKey in root)) {
    throw new Error(`key "${entryKey}" not found under "${rootKey}"`);
  }

  const nextRoot = { ...root };
  delete nextRoot[entryKey];

  return {
    ...registryDoc,
    [rootKey]: nextRoot
  };
}
```

- [ ] **Step 12: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS with 24 tests total.

- [ ] **Step 13: Commit**

Run:

```bash
rtk git add scripts/archive-lib.js test/archive-lib.test.js
rtk git commit -m "test: add pure archive lib functions"
```

Expected: commit succeeds and includes only the lib and its test.

### Task 3: Archive CLI Wrapper

**Files:**
- Create: `scripts/archive-entry.js`
- Modify: `package.json`

- [ ] **Step 1: Create the CLI**

Create `scripts/archive-entry.js`:

```js
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import YAML from "yaml";

import {
  appendToArchive,
  buildArchiveEntry,
  removeFromRegistry
} from "./archive-lib.js";

const SOURCES = {
  selectors: { file: "registry/selectors.yaml", rootKey: "selectors" },
  "do-not-touch": { file: "registry/do-not-touch.yaml", rootKey: "selectors" }
};

function parseArgs(argv) {
  const args = { key: undefined, from: undefined, reason: undefined, evidence: undefined, replacedBy: undefined };

  for (let i = 0; i < argv.length; i++) {
    const token = argv[i];
    if (token === "--from") args.from = argv[++i];
    else if (token === "--reason") args.reason = argv[++i];
    else if (token === "--evidence") args.evidence = argv[++i];
    else if (token === "--replaced-by") args.replacedBy = argv[++i];
    else if (!args.key) args.key = token;
    else throw new Error(`unexpected argument: ${token}`);
  }

  if (!args.key) throw new Error("missing required positional argument: <key>");
  if (!args.reason) throw new Error("missing required option: --reason <text>");
  return args;
}

function resolveSource(key, fromOption, root) {
  if (fromOption) {
    const candidate = SOURCES[fromOption];
    if (!candidate) {
      throw new Error(`unknown --from value "${fromOption}". Valid: ${Object.keys(SOURCES).join(", ")}`);
    }
    return candidate;
  }

  const matches = [];
  for (const [, source] of Object.entries(SOURCES)) {
    const doc = YAML.parse(fs.readFileSync(path.join(root, source.file), "utf8"));
    if (doc?.[source.rootKey] && key in doc[source.rootKey]) {
      matches.push(source);
    }
  }

  if (matches.length === 0) {
    throw new Error(`key "${key}" not found in any source registry`);
  }
  if (matches.length > 1) {
    const names = matches.map((s) => s.file).join(", ");
    throw new Error(`key "${key}" is ambiguous (in ${names}). Specify --from <selectors|do-not-touch>.`);
  }
  return matches[0];
}

function writeYaml(absolutePath, doc) {
  fs.writeFileSync(absolutePath, `${YAML.stringify(doc)}`);
}

function main() {
  const root = process.cwd();
  const args = parseArgs(process.argv.slice(2));
  const source = resolveSource(args.key, args.from, root);

  const sourceAbsolute = path.join(root, source.file);
  const archiveAbsolute = path.join(root, "registry/archive.yaml");

  const sourceDoc = YAML.parse(fs.readFileSync(sourceAbsolute, "utf8"));
  const archiveDoc = YAML.parse(fs.readFileSync(archiveAbsolute, "utf8"));

  const originalEntry = sourceDoc[source.rootKey][args.key];
  const archivedAt = new Date().toISOString().slice(0, 10);

  const entry = buildArchiveEntry({
    key: args.key,
    fromFile: source.file,
    originalEntry,
    reason: args.reason,
    archivedAt,
    evidence: args.evidence,
    replacedBy: args.replacedBy
  });

  const nextSource = removeFromRegistry(sourceDoc, source.rootKey, args.key);
  const nextArchive = appendToArchive(archiveDoc, entry);

  writeYaml(sourceAbsolute, nextSource);
  writeYaml(archiveAbsolute, nextArchive);

  console.log(`Archived ${args.key} from ${source.file} → registry/archive.yaml`);
}

main();
```

- [ ] **Step 2: Add the `archive` npm script and `engines` field**

Open `package.json`. Change:

```json
{
  "name": "discord-theme-lotte",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "description": "Maintainable Lotte-themed Vencord Discord CSS theme with DOM snapshots and selector registries.",
  "scripts": {
    "build": "node scripts/build-theme.js",
    "test": "node --test",
    "validate": "node scripts/validate-registry.js",
    "sync": "npm run check && node scripts/sync-to-vencord.js",
    "check": "npm run validate && npm run build"
  },
  "dependencies": {
    "ajv": "^8.17.1",
    "yaml": "^2.7.0"
  }
}
```

to:

```json
{
  "name": "discord-theme-lotte",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "description": "Maintainable Lotte-themed Vencord Discord CSS theme with DOM snapshots and selector registries.",
  "engines": {
    "node": ">=22"
  },
  "scripts": {
    "build": "node scripts/build-theme.js",
    "test": "node --test",
    "validate": "node scripts/validate-registry.js",
    "sync": "npm run check && node scripts/sync-to-vencord.js",
    "check": "npm run validate && npm run build",
    "archive": "node scripts/archive-entry.js",
    "probe": "node scripts/probe-discord-dom.js"
  },
  "dependencies": {
    "ajv": "^8.17.1",
    "yaml": "^2.7.0"
  }
}
```

- [ ] **Step 3: Confirm npm sees the new scripts**

Run:

```bash
rtk npm run
```

Expected: the listing includes `archive` mapped to `node scripts/archive-entry.js` and `probe` mapped to `node scripts/probe-discord-dom.js`. `probe` is registered now even though `scripts/probe-discord-dom.js` does not yet exist; that file lands in Task 5.

- [ ] **Step 4: Run unit tests to confirm no regression**

Run:

```bash
rtk npm test
```

Expected: 24 tests pass.

- [ ] **Step 5: Run repo check**

Run:

```bash
rtk npm run check
```

Expected: every `ok ...` line prints including `ok registry/archive.yaml` and `ok registry cross-references`, and the build completes with `Built dist/NewKemonoFriends.theme.css from 13 partials`.

- [ ] **Step 6: Commit**

Run:

```bash
rtk git add scripts/archive-entry.js package.json
rtk git commit -m "feat: add archive CLI and npm scripts"
```

Expected: commit succeeds and includes `scripts/archive-entry.js` and `package.json` only.

### Task 4: Pure Probe Functions With TDD

**Files:**
- Create: `test/probe-lib.test.js`
- Create: `scripts/probe-lib.js`

- [ ] **Step 1: Write the failing test for `gatherProbeClasses`**

Create `test/probe-lib.test.js`:

```js
import assert from "node:assert/strict";
import test from "node:test";

import {
  gatherProbeClasses,
  probeScreen,
  summarizeProbeResults
} from "../scripts/probe-lib.js";

const screensDoc = {
  schemaVersion: 1,
  screens: {
    "voice-panel": {
      owns: ["src/components/voice-panel.css"],
      latestSnapshot: "snapshots/2026-05-25/voice-panel.json",
      importantSelectors: ["panels__5e434", "wrapper_e131a9"],
      goals: [],
      knownRisks: []
    }
  }
};

const selectorsDoc = {
  schemaVersion: 1,
  selectors: {
    voice_primary_actions: {
      screen: "voice-panel",
      classes: ["button__67645", "enabled__67645"],
      cssOwner: "src/components/voice-panel.css",
      stability: "hashed",
      action: "",
      reason: ""
    },
    friends_page_body: {
      screen: "friends-page",
      classes: ["tabBody__133bf"],
      cssOwner: "src/components/friends-dm.css",
      stability: "hashed",
      action: "",
      reason: ""
    }
  }
};

test("gatherProbeClasses returns importantSelectors and matching selector classes for the screen", () => {
  const items = gatherProbeClasses("voice-panel", screensDoc, selectorsDoc);
  const sorted = [...items].sort((a, b) => a.class.localeCompare(b.class));

  assert.deepEqual(sorted, [
    { class: "button__67645", source: "selectors.voice_primary_actions.classes" },
    { class: "enabled__67645", source: "selectors.voice_primary_actions.classes" },
    { class: "panels__5e434", source: "screens.voice-panel.importantSelectors" },
    { class: "wrapper_e131a9", source: "screens.voice-panel.importantSelectors" }
  ]);
});

test("gatherProbeClasses throws when the screen is not in screens.yaml", () => {
  assert.throws(
    () => gatherProbeClasses("ghost", screensDoc, selectorsDoc),
    /unknown screen "ghost"/
  );
});

test("gatherProbeClasses ignores selectors that target other screens", () => {
  const items = gatherProbeClasses("voice-panel", screensDoc, selectorsDoc);
  const classes = items.map((i) => i.class);

  assert.ok(!classes.includes("tabBody__133bf"));
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
rtk npm test
```

Expected: FAIL with `Cannot find module '../scripts/probe-lib.js'`.

- [ ] **Step 3: Create the module with `gatherProbeClasses`**

Create `scripts/probe-lib.js`:

```js
export function gatherProbeClasses(screen, screensDoc, selectorsDoc) {
  const screens = screensDoc?.screens ?? {};
  if (!(screen in screens)) {
    throw new Error(`unknown screen "${screen}"`);
  }

  const items = [];

  for (const className of screens[screen].importantSelectors ?? []) {
    items.push({ class: className, source: `screens.${screen}.importantSelectors` });
  }

  const selectors = selectorsDoc?.selectors ?? {};
  for (const [name, entry] of Object.entries(selectors)) {
    if (entry.screen !== screen) continue;
    for (const className of entry.classes ?? []) {
      items.push({ class: className, source: `selectors.${name}.classes` });
    }
  }

  return items;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS with 27 tests total (24 prior + 3 new).

- [ ] **Step 5: Add `summarizeProbeResults` test**

Append to `test/probe-lib.test.js`:

```js
test("summarizeProbeResults separates present from missing classes", () => {
  const results = [
    { class: "panels__5e434", source: "x", count: 1 },
    { class: "wrapper_e131a9", source: "x", count: 2 },
    { class: "button__67645", source: "y", count: 0 }
  ];

  const summary = summarizeProbeResults(results);
  assert.deepEqual(summary.present, ["panels__5e434", "wrapper_e131a9"]);
  assert.deepEqual(summary.missing, ["button__67645"]);
  assert.equal(summary.counts.get("panels__5e434"), 1);
  assert.equal(summary.counts.get("button__67645"), 0);
});

test("summarizeProbeResults treats undefined count as missing", () => {
  const results = [{ class: "x", source: "y" }];
  const summary = summarizeProbeResults(results);
  assert.deepEqual(summary.missing, ["x"]);
  assert.deepEqual(summary.present, []);
});
```

- [ ] **Step 6: Run test to verify it fails**

Run:

```bash
rtk npm test
```

Expected: FAIL with `summarizeProbeResults is not a function` or `is not exported`.

- [ ] **Step 7: Implement `summarizeProbeResults`**

Append to `scripts/probe-lib.js`:

```js
export function summarizeProbeResults(results) {
  const present = [];
  const missing = [];
  const counts = new Map();

  for (const { class: className, count } of results) {
    counts.set(className, count ?? 0);
    if ((count ?? 0) > 0) present.push(className);
    else missing.push(className);
  }

  return { present, missing, counts };
}
```

- [ ] **Step 8: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS with 29 tests total.

- [ ] **Step 9: Add `probeScreen` test with a fake cdpClient**

Append to `test/probe-lib.test.js`:

```js
test("probeScreen delegates to the injected cdpClient and assembles per-class results", async () => {
  const seen = { expression: null };
  const cdpClient = {
    async evaluate(expression) {
      seen.expression = expression;
      return {
        panels__5e434: 1,
        wrapper_e131a9: 2,
        button__67645: 0,
        enabled__67645: 0
      };
    }
  };

  const output = await probeScreen({
    screen: "voice-panel",
    screensDoc,
    selectorsDoc,
    cdpClient
  });

  assert.equal(output.screen, "voice-panel");
  assert.ok(Array.isArray(output.results));
  assert.equal(output.results.length, 4);

  const byClass = Object.fromEntries(output.results.map((r) => [r.class, r]));
  assert.equal(byClass.panels__5e434.count, 1);
  assert.equal(byClass.button__67645.count, 0);
  assert.deepEqual(output.missing, ["button__67645", "enabled__67645"]);
  assert.match(seen.expression, /document\.querySelectorAll/);
});

test("probeScreen throws when the screen has no classes registered", async () => {
  const emptyScreens = {
    schemaVersion: 1,
    screens: {
      empty: { owns: [], importantSelectors: [], goals: [], knownRisks: [] }
    }
  };
  const emptySelectors = { schemaVersion: 1, selectors: {} };
  const cdpClient = { async evaluate() { return {}; } };

  await assert.rejects(
    () => probeScreen({ screen: "empty", screensDoc: emptyScreens, selectorsDoc: emptySelectors, cdpClient }),
    /no classes registered for screen "empty"/
  );
});
```

- [ ] **Step 10: Run test to verify it fails**

Run:

```bash
rtk npm test
```

Expected: FAIL with `probeScreen is not a function` or `is not exported`.

- [ ] **Step 11: Implement `probeScreen`**

Append to `scripts/probe-lib.js`:

```js
function buildProbeExpression(classNames) {
  return `(function(classes) {
  const out = {};
  for (const c of classes) {
    out[c] = document.querySelectorAll('.' + c).length;
  }
  return out;
})(${JSON.stringify(classNames)})`;
}

export async function probeScreen({ screen, screensDoc, selectorsDoc, cdpClient }) {
  const items = gatherProbeClasses(screen, screensDoc, selectorsDoc);
  if (items.length === 0) {
    throw new Error(`no classes registered for screen "${screen}"`);
  }

  const uniqueClasses = [...new Set(items.map((i) => i.class))];
  const expression = buildProbeExpression(uniqueClasses);
  const countsByClass = await cdpClient.evaluate(expression);

  const results = items.map((item) => ({
    class: item.class,
    source: item.source,
    count: countsByClass?.[item.class] ?? 0
  }));

  const summary = summarizeProbeResults(results);

  return {
    screen,
    probedAt: new Date().toISOString(),
    results,
    present: summary.present,
    missing: summary.missing
  };
}
```

- [ ] **Step 12: Run test to verify it passes**

Run:

```bash
rtk npm test
```

Expected: PASS with 31 tests total.

- [ ] **Step 13: Commit**

Run:

```bash
rtk git add scripts/probe-lib.js test/probe-lib.test.js
rtk git commit -m "test: add pure probe lib functions with DI cdpClient"
```

Expected: commit succeeds and includes only the lib and its test.

### Task 5: Probe CDP CLI With Real WebSocket Client

**Files:**
- Create: `scripts/probe-discord-dom.js`

- [ ] **Step 1: Create the CLI**

Create `scripts/probe-discord-dom.js`:

```js
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import YAML from "yaml";

import { probeScreen } from "./probe-lib.js";

const DISCORD_URL_PREFIXES = [
  "https://discord.com/",
  "https://canary.discord.com/",
  "https://ptb.discord.com/"
];

function parseArgs(argv) {
  const args = { screen: undefined };
  for (let i = 0; i < argv.length; i++) {
    const token = argv[i];
    if (!args.screen) args.screen = token;
    else throw new Error(`unexpected argument: ${token}`);
  }
  if (!args.screen) throw new Error("missing required positional argument: <screen>");
  return args;
}

async function findDiscordTarget(baseUrl) {
  const listResponse = await fetch(`${baseUrl}/json/list`);
  if (!listResponse.ok) {
    throw new Error(`CDP /json/list returned HTTP ${listResponse.status}. Is Discord running with --remote-debugging-port?`);
  }
  const targets = await listResponse.json();
  const candidates = targets.filter((target) => {
    if (target.type !== "page") return false;
    return DISCORD_URL_PREFIXES.some((prefix) => typeof target.url === "string" && target.url.startsWith(prefix));
  });

  if (candidates.length === 0) {
    throw new Error("no Discord renderer found among CDP targets. Open the Discord main window and try again.");
  }
  if (candidates.length > 1) {
    console.error(`Warning: ${candidates.length} Discord renderers found; using the first.`);
  }
  return candidates[0];
}

async function evaluateOnTarget(webSocketDebuggerUrl, expression) {
  const ws = new WebSocket(webSocketDebuggerUrl);

  const opened = new Promise((resolve, reject) => {
    ws.addEventListener("open", () => resolve(), { once: true });
    ws.addEventListener("error", (event) => reject(new Error(`CDP WebSocket error: ${event.message ?? "unknown"}`)), { once: true });
  });

  await opened;

  const message = {
    id: 1,
    method: "Runtime.evaluate",
    params: { expression, returnByValue: true, awaitPromise: false }
  };

  const replied = new Promise((resolve, reject) => {
    ws.addEventListener("message", (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.id === 1) resolve(data);
      } catch (error) {
        reject(error);
      }
    });
    ws.addEventListener("error", (event) => reject(new Error(`CDP WebSocket error: ${event.message ?? "unknown"}`)), { once: true });
  });

  ws.send(JSON.stringify(message));
  const response = await replied;
  ws.close();

  if (response.error) {
    throw new Error(`CDP Runtime.evaluate error: ${response.error.message}`);
  }
  const remoteValue = response.result?.result;
  if (remoteValue?.type === "object" && remoteValue.value !== undefined) {
    return remoteValue.value;
  }
  if (remoteValue?.subtype === "error" || response.result?.exceptionDetails) {
    const text = response.result?.exceptionDetails?.text ?? remoteValue?.description ?? "unknown CDP exception";
    throw new Error(`CDP renderer threw: ${text}`);
  }
  throw new Error("CDP Runtime.evaluate returned an unexpected shape");
}

function buildRealCdpClient(baseUrl) {
  return {
    async evaluate(expression) {
      const target = await findDiscordTarget(baseUrl);
      return evaluateOnTarget(target.webSocketDebuggerUrl, expression);
    }
  };
}

async function main() {
  const root = process.cwd();
  const baseUrl = process.env.DISCORD_CDP_URL;
  if (!baseUrl) {
    throw new Error("DISCORD_CDP_URL is not set. See docs/workflow.md§Discord CDP Setup.");
  }

  const args = parseArgs(process.argv.slice(2));
  const screensDoc = YAML.parse(fs.readFileSync(path.join(root, "registry/screens.yaml"), "utf8"));
  const selectorsDoc = YAML.parse(fs.readFileSync(path.join(root, "registry/selectors.yaml"), "utf8"));

  const cdpClient = buildRealCdpClient(baseUrl);
  const output = await probeScreen({
    screen: args.screen,
    screensDoc,
    selectorsDoc,
    cdpClient
  });

  process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);

  if (output.missing.length > 0) {
    process.exit(1);
  }
}

main().catch((error) => {
  process.stderr.write(`probe failed: ${error.message}\n`);
  process.exit(2);
});
```

- [ ] **Step 2: Verify the file loads as ESM without syntax errors**

Run:

```bash
rtk node --check scripts/probe-discord-dom.js
```

Expected: command exits 0 with no output. If it fails, the file has a syntax error; fix and re-run.

- [ ] **Step 3: Verify the CLI gracefully refuses when `DISCORD_CDP_URL` is missing**

Run:

```bash
rtk env -u DISCORD_CDP_URL node scripts/probe-discord-dom.js voice-panel
```

Expected: exit code 2, and stderr contains `probe failed: DISCORD_CDP_URL is not set. See docs/workflow.md§Discord CDP Setup.`

- [ ] **Step 4: Run unit tests to confirm no regression**

Run:

```bash
rtk npm test
```

Expected: PASS with 31 tests total (no new tests; this task only adds the CLI shim, all logic was already tested in Task 4 through `probeScreen`).

- [ ] **Step 5: Run repo check**

Run:

```bash
rtk npm run check
```

Expected: every `ok ...` line prints including `ok registry/archive.yaml` and `ok registry cross-references`, build completes with `Built dist/NewKemonoFriends.theme.css from 13 partials`.

- [ ] **Step 6: Commit**

Run:

```bash
rtk git add scripts/probe-discord-dom.js
rtk git commit -m "feat: add Discord CDP probe CLI"
```

Expected: commit succeeds and includes only `scripts/probe-discord-dom.js`.

### Task 6: Document Probe And Archive Workflow

**Files:**
- Modify: `docs/workflow.md`

- [ ] **Step 1: Append the workflow section**

Append the exact block below to the end of `docs/workflow.md` (after the Task 0 `## Discord CDP Setup (one-time)` section):

```markdown

## Probe And Archive Workflow

### When to run

- Discord behavior on a specific screen looks different than last seen.
- A registered selector seems to have no effect after Vencord reload.
- After Vencord or Discord update notifications.

### Probe

1. Open Discord Desktop and navigate to the screen you want to verify (e.g. voice-panel by connecting to a voice channel).
2. From WSL, with `DISCORD_CDP_URL` exported per the setup section:

   ```bash
   rtk npm run probe -- voice-panel
   ```

3. The probe prints a JSON object with `results` (per-class `{class, source, count}`), `present`, and `missing` arrays. Exit code is `0` when every class is observed at least once and `1` when any class is missing.

### Archive

When a class is in `missing` and you confirm Discord no longer renders it on the relevant screen:

```bash
rtk npm run archive -- <entry-key> --reason "<short why>" [--evidence "snapshots/YYYY-MM-DD/<screen>.json"] [--replaced-by <new-key>] [--from selectors|do-not-touch]
```

The command:

- Reads the entry from `registry/selectors.yaml` or `registry/do-not-touch.yaml` (auto-detects if the key is unambiguous; otherwise requires `--from`).
- Appends a record to `registry/archive.yaml` with `archivedAt: <today>`, the original entry as `snapshot`, and the provided `reason` / `evidence` / `replacedBy`.
- Removes the entry from the source registry.

The command does NOT touch CSS partials. After archiving, manually prune the orphan CSS block in the entry's former `cssOwner` partial if it now does nothing. `rtk npm run check` and `rtk npm test` should still pass.

### Caveats

- The probe is read-only. It runs only `document.querySelectorAll('.<class>').length` expressions through CDP.
- The probe is screen-aware. A class that exists only when a voice call is active will be reported as missing if the user is not currently in a call. Open the correct Discord screen before probing.
- Archive is forensic-only. Once an entry is archived, it is not garbage-collected; the file grows append-only. Audit `registry/archive.yaml` periodically when looking for replaced entries.
- YAML serialization through `YAML.stringify` does not preserve source comments. Registry files in this repo currently carry no meaningful comments, so this is acceptable for M4 v1.
```

- [ ] **Step 2: Confirm the file structure**

Run:

```bash
rtk grep -n "^## " docs/workflow.md
```

Expected:

```text
## Load Boundaries
## Standard Flow
## Test Boundaries
## Registry And Snapshot Rules
## Commit Shape
## Discord CDP Setup (one-time)
## Probe And Archive Workflow
```

- [ ] **Step 3: Commit**

Run:

```bash
rtk git add docs/workflow.md
rtk git commit -m "docs: document probe and archive workflow"
```

Expected: commit succeeds and includes only `docs/workflow.md`.

### Task 7: Final Verification

**Files:**
- Inspect: `scripts/archive-lib.js`
- Inspect: `scripts/archive-entry.js`
- Inspect: `scripts/probe-lib.js`
- Inspect: `scripts/probe-discord-dom.js`
- Inspect: `registry/archive.yaml`
- Inspect: `schema/archive.schema.json`
- Inspect: `docs/workflow.md`
- Inspect: `package.json`

- [ ] **Step 1: Run tests**

Run:

```bash
rtk npm test
```

Expected: 31 tests pass — 1 build-contract, 16 cross-reference, 7 archive-lib, 7 probe-lib.

- [ ] **Step 2: Run repo check**

Run:

```bash
rtk npm run check
```

Expected: every `ok ...` line prints including `ok registry/archive.yaml` and `ok registry cross-references`, and the build completes with `Built dist/NewKemonoFriends.theme.css from 13 partials`.

- [ ] **Step 3: Confirm probe CLI handles missing env var**

Run:

```bash
rtk env -u DISCORD_CDP_URL node scripts/probe-discord-dom.js voice-panel
```

Expected: exit code 2, stderr contains `DISCORD_CDP_URL is not set`.

- [ ] **Step 4: Confirm archive CLI rejects missing args**

Run:

```bash
rtk node scripts/archive-entry.js 2>&1 | head -3
```

Expected: a non-zero exit and an error message containing `missing required positional argument: <key>`.

- [ ] **Step 5: Confirm no live sync happened**

Run:

```bash
rtk git diff --stat HEAD
```

Expected: no uncommitted changes. No command in this plan runs `rtk npm run sync` or `rtk npm run probe` against the real Discord.

- [ ] **Step 6: Review scope boundaries**

Run:

```bash
rtk git status
rtk git log --oneline -12
```

Expected: only new files are `scripts/archive-lib.js`, `scripts/archive-entry.js`, `scripts/probe-lib.js`, `scripts/probe-discord-dom.js`, `registry/archive.yaml`, `schema/archive.schema.json`, `test/archive-lib.test.js`, `test/probe-lib.test.js`; only modified files are `scripts/validate-registry.js`, `docs/workflow.md`, `package.json`. No `docs/agents/`, no PRD docs, no browser automation libraries, no visual regression files. Commits map one-to-one with Tasks 0 through 6.

## Self-Review

- Spec coverage:
  - "Verify registry entries against real Discord Desktop DOM via CDP" — Tasks 4-5 deliver `probeScreen` and the `scripts/probe-discord-dom.js` CLI, which connects to `DISCORD_CDP_URL` and executes `document.querySelectorAll` per registered class on the named screen.
  - "Append-only archive workflow" — Tasks 1-3 add `registry/archive.yaml`, its schema, the pure `archive-lib`, and the `scripts/archive-entry.js` CLI. The CLI writes to `registry/archive.yaml` via `appendToArchive` (never overwrites) and removes from source via `removeFromRegistry`.
  - "Phase 1 keeps Discord navigation manual" — the probe does only read-only `querySelectorAll` evaluations; no navigation, no click, no input.
  - "No new dependencies" — every script uses Node 22+ built-ins (`fetch`, `WebSocket`, `fs`, `path`, `process`) plus the already-present `yaml` and `ajv`.
  - "Document the one-time Windows + WSL setup" — Task 0 appends a complete setup section to `docs/workflow.md` with exact Discord shortcut target, portproxy command, and env var.
  - "Tight, no doc bloat" — only `docs/workflow.md` is modified, only two sections appended.
- Placeholder scan: No `TODO`, no "later", no "fill in", no "similar to Task N", no untyped pseudo-code; every step shows complete code or an explicit command with expected output.
- Type and API consistency:
  - `buildArchiveEntry({key, fromFile, originalEntry, reason, archivedAt, evidence, replacedBy})` is defined in Task 2 and consumed unchanged by `scripts/archive-entry.js` in Task 3.
  - `appendToArchive(archiveDoc, entry)` and `removeFromRegistry(registryDoc, rootKey, entryKey)` from Task 2 are imported by `scripts/archive-entry.js` in Task 3 with matching call shapes.
  - `gatherProbeClasses`, `summarizeProbeResults`, and `probeScreen({screen, screensDoc, selectorsDoc, cdpClient})` are defined in Task 4 and consumed unchanged by `scripts/probe-discord-dom.js` in Task 5.
  - `cdpClient.evaluate(expression) → Promise<{[className]: number}>` is the contract between `probeScreen` and any client. The fake client in Task 4 returns this shape; the real client in Task 5 wraps `fetch` + `WebSocket` to do the same.
  - `DISCORD_CDP_URL` env var (Task 0 docs, Task 5 CLI, Task 6 docs) is consistently named — never `BU_CDP_URL`, never `CDP_URL`.
  - `registry/archive.yaml` schema shape (`schemaVersion`, `entries[*]: {archivedAt, fromFile, key, snapshot, reason, evidence?, replacedBy?}`) matches what `buildArchiveEntry` produces and what `scripts/validate-registry.js` validates.
- Scope check: No `docs/agents/`, no PRD workflow, no Playwright, no visual regression, no Discord navigation automation, no sync invocation, no Vencord live theme edits, no `src/**` edits, no other registry data changes, no new dependencies in `package.json`.
