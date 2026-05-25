# Workspace Memory Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a lightweight workspace memory layer and one tracer-bullet contract test so future Discord theme edits preserve Lotte's visual intent without adding process bloat.

**Architecture:** `AGENTS.md` stays the automatically loaded guardrail and reference map. `CONTEXT.md` becomes concise domain memory, `docs/workflow.md` becomes the manually loaded playbook, registries and snapshots remain structured task-specific evidence, and `test/` holds Node built-in contract tests for repo safety.

**Tech Stack:** Markdown, YAML registries, Vencord theme CSS, existing Node ESM scripts, `node:test`, `node:assert/strict`, `yaml`, `npm` scripts run through `rtk`.

---

## File Structure

- Create: `CONTEXT.md`
  - Concise private workspace memory: purpose, visual direction, working principles, glossary, and safety boundaries.
  - Must not contain a changelog, PRD, selector dump, broad task list, or implementation plan.
- Create: `docs/workflow.md`
  - Detailed playbook for translating user visual intent into selector, CSS, registry, snapshot, build, check, commit, and optional sync work.
  - Explicitly separates automatic load from manual load.
- Modify: `AGENTS.md`
  - Keep existing rules intact.
  - Add short references to `CONTEXT.md` and `docs/workflow.md`.
  - Do not copy the workflow into this automatically loaded file.
- Modify: `package.json`
  - Add `"test": "node --test"` only.
  - Do not wire `npm test` into `npm run check` in Milestone 1.
- Create: `test/build-contract.test.js`
  - One tracer-bullet contract test around `theme.manifest.yaml` as build-order authority and `dist/NewKemonoFriends.theme.css` as generated output.
  - Verify public generated behavior: configured output exists, each manifest partial appears in order through existing `/* source: ... */` markers, and the generated file contains exactly the manifest partial set.
- Generated output: `dist/NewKemonoFriends.theme.css`
  - May change only by running `rtk npm run build`.
  - Never hand-edit this file.

## Non-Goals

- Do not introduce `docs/agents/`.
- Do not introduce local issue tracking, PRD workflow, broad project management docs, or new milestone docs.
- Do not introduce Jest, Vitest, Playwright, browser automation, visual regression testing, or Discord live DOM automation.
- Do not run `rtk npm run sync`.
- Do not edit the Vencord live theme directory.
- Do not add broad horizontal test coverage in this milestone.

## Tasks

### Task 1: Add Concise Domain Memory

**Files:**
- Create: `CONTEXT.md`

- [ ] **Step 1: Create `CONTEXT.md`**

Create this exact file:

```markdown
# Lotte Theme Context

## Purpose

This repo is a private Vencord theme workspace for preserving Lotte's visual intent and the Discord DOM modification context needed to maintain it over time.

The user usually describes desired Discord theme behavior in visual language instead of editing code directly. Agents should turn that intent into focused questions, selector evidence, registry updates, CSS changes in `src/`, generated `dist/`, and commits.

## Visual Direction

- Keep Discord usable first: readable text, visible controls, and predictable interaction states.
- Preserve the Lotte/Kemono Friends feeling through soft color, warmth, and characterful accents without obscuring current Discord UI structure.
- Prefer small, targeted refinements over broad restyles when Discord or Vencord changes the DOM.
- Avoid risky media, rendering, stream, call, and video selectors unless they are explicitly understood and registered as safe.

## Working Principles

- `src/` is the CSS source of truth.
- `dist/NewKemonoFriends.theme.css` is generated output.
- `theme.manifest.yaml` is the only build-order authority.
- Registries hold structured selector, screen, palette, and risk knowledge.
- Snapshots hold raw DOM evidence gathered for a specific date and surface.
- `CONTEXT.md` should change only when the domain language, visual direction, or safety boundaries change.

## Glossary

- **Workspace memory:** The compact set of docs, registries, snapshots, tests, and generated output that lets future agents continue theme work after Discord DOM changes.
- **Visual intent:** The user's desired look or behavior, expressed in plain language before selectors or CSS are chosen.
- **Selector evidence:** Snapshot or registry-backed reason to trust a Discord or Vencord selector.
- **Source partial:** A CSS file listed in `theme.manifest.yaml` and concatenated into the generated theme.
- **Dangerous selector:** A selector that can affect media playback, calls, streams, rendering surfaces, or other fragile Discord behavior.

## Safety Boundaries

- Do not edit the Vencord live theme directory from this repo.
- Do not run sync unless the user explicitly asks.
- Do not treat generated `dist/` changes as source changes.
- Do not add raw selector knowledge only to prose; update `registry/*.yaml` when selector status changes.
- Do not let this file become a PRD, changelog, selector dump, or implementation plan.
```

- [ ] **Step 2: Review for bloat**

Run:

```bash
rtk wc -l CONTEXT.md
```

Expected: the file is under 60 lines.

- [ ] **Step 3: Commit**

Run:

```bash
rtk git add CONTEXT.md
rtk git commit -m "docs: add workspace context memory"
```

Expected: commit succeeds and includes only `CONTEXT.md`.

### Task 2: Add Manual Workflow Playbook

**Files:**
- Create: `docs/workflow.md`

- [ ] **Step 1: Create `docs/workflow.md`**

Create this exact file:

```markdown
# Theme Editing Workflow

## Load Boundaries

- `AGENTS.md` is the automatically loaded guardrail and reference map.
- `CONTEXT.md` is concise domain memory for visual direction, glossary, and safety boundaries.
- `docs/workflow.md` is the detailed playbook for doing theme work.
- `registry/*.yaml` and `snapshots/YYYY-MM-DD/*.json` are task-specific evidence, not general prose docs.

## Standard Flow

1. Start from the user's visual intent.
2. Ask one focused clarification question at a time when the intent is ambiguous.
3. Inspect `CONTEXT.md` for domain language, visual direction, and safety boundaries.
4. Inspect relevant registry files and dated snapshots before trusting selectors.
5. Update `CONTEXT.md` only if domain language, visual direction, or safety boundaries changed.
6. Update `registry/selectors.yaml` when a selector is added, removed, or reclassified.
7. Update `registry/do-not-touch.yaml` when dangerous media, rendering, stream, call, or video selectors are identified.
8. Add raw DOM observations to `snapshots/YYYY-MM-DD/*.json` when new evidence is gathered.
9. Create a small implementation plan for the requested change.
10. Use TDD for script, registry, build, or workspace contract behavior where applicable.
11. Edit CSS only in `src/`.
12. Run `rtk npm run build` when generated output needs to be refreshed.
13. Run `rtk npm run check` before considering the repo ready to sync.
14. Commit focused changes with generated `dist/` included only when it was produced by the build.
15. Run `rtk npm run sync` only when the user explicitly asks.

## Test Boundaries

- Use Node built-in `node:test` for workspace contract tests.
- Test build, registry, manifest, and safety behavior.
- Do not test visual beauty with unit tests.
- Do not add browser automation or visual regression to Milestone 1.

## Registry And Snapshot Rules

- Registries are structured memory and should be updated when selector knowledge changes.
- Snapshots are raw evidence and should stay dated under `snapshots/YYYY-MM-DD/`.
- Prose docs may explain how evidence is used, but they should not duplicate selector inventories.

## Commit Shape

- Prefer small commits that map to one durable workspace improvement.
- Keep generated `dist/NewKemonoFriends.theme.css` changes in the same commit as the source or manifest change that produced them.
- Do not include unrelated local edits.
```

- [ ] **Step 2: Confirm the playbook keeps execution manual**

Run:

```bash
rtk sed -n '1,220p' docs/workflow.md
```

Expected: the file explicitly says `docs/workflow.md` is the detailed playbook and `AGENTS.md` is the automatically loaded guardrail and reference map.

- [ ] **Step 3: Commit**

Run:

```bash
rtk git add docs/workflow.md
rtk git commit -m "docs: add theme editing workflow"
```

Expected: commit succeeds and includes only `docs/workflow.md`.

### Task 3: Keep Automatic Agent Instructions Short

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Replace `AGENTS.md` with the short reference-map version**

Replace the file with this exact content:

```markdown
# Agent Instructions

This repo manages a private Vencord Discord theme.

Reference map:
- `CONTEXT.md` captures concise theme memory, visual direction, domain language, and safety boundaries.
- `docs/workflow.md` contains the detailed playbook for turning user visual intent into selector, CSS, registry, snapshot, build, check, commit, and optional sync work.

Rules:
- Treat `src/` as the CSS source of truth.
- Treat `dist/NewKemonoFriends.theme.css` as generated output.
- Do not edit files in the Vencord themes directory directly from this repo.
- Add raw DOM observations to `snapshots/YYYY-MM-DD/*.json`.
- Update `registry/selectors.yaml` when a selector is added, removed, or reclassified.
- Add dangerous media/rendering selectors to `registry/do-not-touch.yaml`.
- Keep `theme.manifest.yaml` as the only build-order authority.
- Run `npm run check` before syncing.
```

- [ ] **Step 2: Verify the full workflow was not copied into `AGENTS.md`**

Run:

```bash
rtk wc -l AGENTS.md
rtk sed -n '1,120p' AGENTS.md
```

Expected: `AGENTS.md` remains short, references `CONTEXT.md` and `docs/workflow.md`, and preserves the existing project rules.

- [ ] **Step 3: Commit**

Run:

```bash
rtk git add AGENTS.md
rtk git commit -m "docs: map agent instructions to workspace memory"
```

Expected: commit succeeds and includes only `AGENTS.md`.

### Task 4: Add One Build Contract Test With TDD

**Files:**
- Modify: `package.json`
- Create: `test/build-contract.test.js`

- [ ] **Step 1: Write the tracer-bullet test before wiring the harness**

Create `test/build-contract.test.js`:

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

test("generated theme follows manifest output and partial order", () => {
  const manifest = YAML.parse(readText("theme.manifest.yaml"));
  const generated = readText(manifest.output);

  assert.equal(manifest.output, "dist/NewKemonoFriends.theme.css");
  assert.ok(Array.isArray(manifest.partials));
  assert.ok(manifest.partials.length > 0);

  let cursor = 0;
  for (const partial of manifest.partials) {
    const marker = `/* source: ${partial} */`;
    const index = generated.indexOf(marker, cursor);

    assert.notEqual(index, -1, `${marker} is present after the previous partial`);
    cursor = index + marker.length;
  }

  const generatedMarkers = [...generated.matchAll(/^\/\* source: (.+) \*\/$/gm)].map((match) => match[1]);
  assert.deepEqual(generatedMarkers, manifest.partials);
});
```

- [ ] **Step 2: Run test to verify red**

Run:

```bash
rtk npm test
```

Expected: FAIL because `package.json` does not define a `test` script yet.

- [ ] **Step 3: Add the `npm test` script**

Change `package.json` scripts from:

```json
  "scripts": {
    "build": "node scripts/build-theme.js",
    "validate": "node scripts/validate-registry.js",
    "sync": "npm run check && node scripts/sync-to-vencord.js",
    "check": "npm run validate && npm run build"
  },
```

to:

```json
  "scripts": {
    "build": "node scripts/build-theme.js",
    "validate": "node scripts/validate-registry.js",
    "sync": "npm run check && node scripts/sync-to-vencord.js",
    "check": "npm run validate && npm run build",
    "test": "node --test"
  },
```

- [ ] **Step 4: Run test to verify green**

Run:

```bash
rtk npm test
```

Expected: PASS, with one passing test file and no failed tests.

- [ ] **Step 5: Build generated output from the manifest**

Run:

```bash
rtk npm run build
```

Expected:

```text
Built dist/NewKemonoFriends.theme.css from 13 partials
```

- [ ] **Step 6: Run test again after build**

Run:

```bash
rtk npm test
```

Expected: PASS, with one passing test file and no failed tests.

- [ ] **Step 7: Confirm `npm run check` remains unchanged**

Run:

```bash
rtk npm run check
```

Expected:

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
Built dist/NewKemonoFriends.theme.css from 13 partials
```

Also verify `npm test` is not part of the `check` script in `package.json`.

- [ ] **Step 8: Commit**

Run:

```bash
rtk git add package.json test/build-contract.test.js dist/NewKemonoFriends.theme.css
rtk git commit -m "test: add theme build contract tracer bullet"
```

Expected: commit succeeds. If `dist/NewKemonoFriends.theme.css` is unchanged after `rtk npm run build`, Git will ignore it; that is acceptable.

### Task 5: Final Verification

**Files:**
- Inspect: `AGENTS.md`
- Inspect: `CONTEXT.md`
- Inspect: `docs/workflow.md`
- Inspect: `package.json`
- Inspect: `test/build-contract.test.js`
- Inspect: `dist/NewKemonoFriends.theme.css`

- [ ] **Step 1: Run tests**

Run:

```bash
rtk npm test
```

Expected: PASS.

- [ ] **Step 2: Run existing repo check**

Run:

```bash
rtk npm run check
```

Expected: registry validation, snapshot validation, and build all pass.

- [ ] **Step 3: Verify no live sync happened**

Run:

```bash
rtk git diff --stat HEAD
```

Expected: no uncommitted changes after the task commits. No command in this plan runs `rtk npm run sync`.

- [ ] **Step 4: Review scope boundaries**

Run:

```bash
rtk find . -maxdepth 3 -type f
```

Expected: no new `docs/agents/`, no issue tracker docs, no PRD, no visual regression files, no browser automation files, and no Discord live DOM automation files.

## Self-Review

- Spec coverage: The plan covers `CONTEXT.md`, `docs/workflow.md`, short `AGENTS.md` references, a minimal `node:test` harness, generated dist handling, no live Vencord edits, and no sync.
- Placeholder scan: The plan contains no unresolved placeholders, deferred steps, or broad "write tests later" instructions.
- Type and API consistency: The test uses Node ESM, `node:test`, `node:assert/strict`, `fs`, `path`, and the existing `yaml` dependency already used by repo scripts.
- Scope check: Milestone 1 deliberately excludes `docs/agents/`, local issues, PRD workflow, visual regression, browser automation, and Discord live DOM automation.
