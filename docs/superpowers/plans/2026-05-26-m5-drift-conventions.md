# M5: Drift Detection Conventions + Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lock the M3/M4 drift detection layer's conventions into project memory (CONTEXT.md glossary, one ADR, plan convention augmentations), and fix the six high-priority concerns surfaced during M3/M4 review.

**Architecture:** Three new meta files (CONTEXT.md edits, `docs/adr/0001-*`, `.claude/rules/plan-conventions.md`) plus six in-place fixes. No new feature surface, no new scripts, no new dependencies. The drift detection layer itself was built in M3/M4; M5 names it, archives one architectural decision, and cleans up reviewer-flagged loose ends. The `Non-Goals → ### Deferred` section in this plan serves as the **self-demonstrating first use** of the new plan convention this plan itself introduces.

**Tech Stack:** Markdown (CONTEXT.md, ADR, `.claude/rules/plan-conventions.md`, `docs/workflow.md`). Node 22+ with `node:test` and `node:assert/strict` for the scripts/test fixes. The existing `yaml` dependency. No new dependencies.

---

## Non-Goals

- Do not change `registry/*.yaml` structure or content.
- Do not change `schema/*.json`.
- Do not change `theme.manifest.yaml` or any file under `src/**`.
- Do not change `scripts/build-theme.js`, `scripts/sync-to-vencord.js`, `scripts/inspect-dom.js`, `scripts/validate-registry.js`, `scripts/registry-checks.js`, `scripts/archive-lib.js`, `scripts/probe-lib.js`.
- Do not introduce browser automation libraries (Playwright, puppeteer, chrome-remote-interface, browser-use).
- Do not introduce CSS pruning automation (bound by ADR-0001 created in this plan).
- Do not introduce orphan-detection mechanisms in any form.
- Do not introduce per-feature scaffolding (`docs/features/`, `DOMAIN_MAP.md`).
- Do not wire up `~/.claude/scripts/retrospect-scan.sh` Step 2.5 hook.
- Do not run `rtk npm run sync` or touch the Vencord live theme directory.
- Do not run `rtk npm run probe` against real Discord during plan execution.
- Do not commit `dist/NewKemonoFriends.theme.css` unless `rtk npm run build` actually changes it.

### Deferred

Concerns and candidates intentionally not addressed by M5. Each entry follows the format introduced by this plan: a short reason and a concrete trigger to revisit.

- **Concern #1** — `package.json` scripts key ordering.
  - *Why deferred:* Purely cosmetic; not ship-blocking. Functionally identical to current state.
  - *Trigger to revisit:* When the `scripts` block in `package.json` is touched for any other reason.

- **Concern #8** — `test/snapshot-scaffold.test.js` does not assert `result.absolutePath`.
  - *Why deferred:* Test coverage strengthening is a separate concern from M5's cleanup theme; bundling it would mix shapes.
  - *Trigger to revisit:* When path-construction logic in `scaffoldSnapshot` changes, or when a test-improvement milestone is scheduled.

- **Concern #9** — `test/selector-usage-contract.test.js:30` uses `ownerCss.includes(className)`, a substring match that accepts CSS-comment-only references.
  - *Why deferred:* Same root cause as the future orphan warning milestone's CSS class extractor. Delegated.
  - *Trigger to revisit:* When the orphan warning milestone is scheduled; the shared `extract-css-classes` helper closes both at once.

- **Orphan warning feature** — informational signal for partials referencing classes absent from active registries.
  - *Why deferred:* Drift detection usage frequency is *predicted low* (M3/M4 only just introduced it). Orphan-CSS accumulation rate is bounded by archive frequency; current manual-prune burden is unknown. Best decided after real usage.
  - *Trigger to revisit:* When orphan CSS accumulation becomes a visible review burden, OR when the `intentionally_unowned.yaml` ledger pattern is wanted, OR when concern #9 needs closing.

- **Architecture Candidate #1** — Collapse CLI script boilerplate into a `scriptHarness`.
  - *Why deferred:* 1-person project, low frequency of new CLI commands. Current boilerplate cost across three adapters (archive, probe, snapshot) is below the harness design + adoption cost. The pattern is already legible enough to copy.
  - *Trigger to revisit:* When new CLI commands are added frequently, OR when the same boilerplate change (logging, dry-run, env handling) needs to be made across all three scripts.

- **Architecture Candidate #2 + #3 pair** — Extract CDP transport into a standalone module; align lib modules around `pure-first` shape.
  - *Why deferred:* Daemon mode, batch probe, multi-target probing are future possibilities not currently on the roadmap. Probe-lib's asymmetry vs archive-lib does not block any current workflow. Concern #4 and #5 spot fixes from this plan absorb naturally when the pair is eventually undertaken.
  - *Trigger to revisit:* When daemon mode or batch probing is wanted, OR when adding a new lib module surfaces shape ambiguity, OR when concern #4 needs upstreaming into a reusable CDP client for any other caller.

- **Architecture Candidate #4** — Formalise registry-source adapter (`SOURCES` object in `archive-entry.js`).
  - *Why deferred:* No concrete plan to add a third archive-able registry source (screens / palette / risks / intentionally_unowned). The current 1-adapter-pair shape is sufficient until a real second adapter appears.
  - *Trigger to revisit:* When any of `screens.yaml`, `palette.yaml`, `risks.yaml`, `intentionally_unowned.yaml`, or any new registry source becomes archive-eligible.

- **Architecture Candidate #5** — Unified rule runner for `validate-registry.js` + `registry-checks.js`.
  - *Why deferred:* Current 7 cross-reference checks with manual wiring is not a friction point. Worth-exploring strength is the weakest among architecture candidates.
  - *Trigger to revisit:* When the cross-reference check count exceeds 7 and adding the next becomes visibly tedious, OR when CI needs to run a subset (e.g., fast-feedback vs full-validation modes).

- **Step 2.5 retrospect-scan hook** in `.claude/rules/plan-conventions.md`.
  - *Why deferred:* `retrospect-scan.sh` expects `docs/features/<slug>/RESEARCH.md` scaffolding and a separate `DOMAIN_MAP.md`. Neither exists; `CONTEXT.md` serves the glossary role under M5's decision.
  - *Trigger to revisit:* When the project adopts per-feature `RESEARCH.md` narratives, OR when `CONTEXT.md` outgrows its glossary scope and needs splitting.

- **Full global harness-pattern bootstrap** (`DOMAIN_MAP.md`, `docs/features/`, Read priority table, project override declaration).
  - *Why deferred:* `CONTEXT.md` already serves the glossary role under M5's decision. `AGENTS.md` already serves as the auto-loaded reference map. Project works in milestones, not per-feature directories. Adopting the full pattern would duplicate existing roles or scaffold empty infrastructure.
  - *Trigger to revisit:* When the project shifts from milestone-based to per-feature work, OR when `CONTEXT.md` needs splitting, OR when `SPEC.md`/`ARCHITECTURE.md` are added.

---

## Tasks

### Task 1: CONTEXT.md — drift detection vocabulary and glossary role

**Files:**
- Modify: `CONTEXT.md`

- [ ] **Step 1: Append four glossary entries**

In `CONTEXT.md`, locate the existing `## Glossary` section. After the last existing entry (**Dangerous selector**), append exactly:

```markdown
- **Drift detection:** The responsibility of noticing when registry knowledge has fallen out of sync with the live Discord DOM, and recording the resolution. Implemented in M3/M4 by the probe and archive commands; distinct from registry/snapshot management.
- **Probe:** Read-only check that uses Chrome DevTools Protocol against a running Discord renderer to verify whether the classes registered for a screen are currently present in the live DOM. Implemented by `scripts/probe-discord-dom.js`. Does not modify any registry.
- **Archive:** Forensic tombstone for a selector entry removed from an active registry. Implemented as `registry/archive.yaml` plus the `archive` command. Append-only, not garbage-collected. CSS pruning is the user's manual responsibility. See ADR-0001.
- **Screen:** A registered Discord surface (e.g. `voice-panel`, `friends-page`), declared as an entry in `registry/screens.yaml`. Unit at which probe runs and snapshots are taken.
```

- [ ] **Step 2: Append two working principles**

In `CONTEXT.md`, locate the existing `## Working Principles` section. After the last existing bullet (`- `CONTEXT.md` should change only when the domain language, visual direction, or safety boundaries change.`), append exactly:

```markdown
- Drift detection is a separate cycle from active registry curation. Probe never modifies registries. Archive shrinks an active registry but never modifies CSS partials.
- `CONTEXT.md` serves as the project's single domain glossary; no separate `DOMAIN_MAP.md` is maintained.
```

- [ ] **Step 3: Run tests and check**

```bash
rtk npm test
```
Expected: all existing tests pass (no test changes in this task).

```bash
rtk npm run check
```
Expected: passes.

- [ ] **Step 4: Commit**

```bash
git add CONTEXT.md
git commit -m "docs: add drift detection vocabulary and glossary role to CONTEXT.md"
```

---

### Task 2: ADR-0001 — Drift detection is forensic-only

**Files:**
- Create: `docs/adr/0001-drift-detection-is-forensic-only.md`

- [ ] **Step 1: Create the ADR directory and file**

Create `docs/adr/` if it does not exist, then write `docs/adr/0001-drift-detection-is-forensic-only.md` with exactly the following content:

```markdown
# ADR 0001: Drift detection is forensic-only

Date: 2026-05-26
Status: Accepted (retroactive — decision was implicit in the M4 plan; this ADR records the rationale via post-hoc review of alternatives)

## Context

M4 introduced the drift detection layer for the discord-theme-lotte workspace: a probe command (read-only Chrome DevTools Protocol query) and an archive command (forensic tombstone for selector entries removed from active registries). The archive command writes to `registry/archive.yaml`, an append-only YAML file.

Two design questions sit behind the archive command:

1. Should `registry/archive.yaml` be garbage-collected over time, or grow append-only?
2. When a selector is archived, should the matching CSS block in its former `cssOwner` partial be pruned automatically?

The M4 plan answered both with "forensic-only, manual prune." This ADR documents the rationale and the alternatives considered.

## Decision

`registry/archive.yaml` is forensic-only. No automatic garbage collection. The archive command modifies the source registry and the archive file; it never touches CSS partials. CSS pruning, when needed, is performed manually by the user.

## Alternatives considered

- **Automatic garbage collection** (e.g., remove archive entries older than N months, or move them to a cold-storage file). Rejected. The forensic value of an archive entry grows with time — "what did Discord look like 1 year ago" is precisely the kind of question forensic records answer. Garbage collection runs in the opposite direction from forensic preservation.

- **Integrated `archive`-and-`cssprune`** (the archive command both removes the registry entry and removes the matching CSS block from the partial). Rejected. CSS pruning is a *judgment* operation: an archived selector's class may still be intentionally referenced elsewhere in CSS (for parent-context cascading, for Vencord plugin classes, for kept-as-comment historical residue). Automatic pruning would mutate visual surface area without explicit user review, which conflicts with the project's Visual Direction principle in CONTEXT.md.

- **Orphan warning** (informational signal that flags CSS classes present in partials but absent from any active registry, without modifying anything). **Deferred, not rejected.** This mechanism is *compatible with* forensic-only. It operates on a different plane: forensic-only governs `archive.yaml` and the `archive` command; an orphan warning would govern the partial-vs-registry asymmetry as a memory aid. A future ADR can introduce orphan warning without superseding this one.

## Consequences

- `registry/archive.yaml` grows monotonically. Audit periodically when looking for replaced entries.
- Orphan CSS blocks accumulate after archiving until the user prunes them. This is intentional residue. The user's visual review remains the gate for CSS change.
- Adding an orphan warning mechanism does not require superseding this ADR — it operates on a separate concern. A new ADR would only be needed if `archive.yaml`'s forensic guarantee itself is reversed (e.g., auto-GC is later introduced).
- Reversing the forensic-only stance for `archive.yaml` would require a new ADR superseding 0001, including a migration policy for already-accumulated entries.
```

- [ ] **Step 2: Run tests and check**

```bash
rtk npm test
rtk npm run check
```
Expected: pass.

- [ ] **Step 3: Commit**

```bash
git add docs/adr/0001-drift-detection-is-forensic-only.md
git commit -m "docs: add ADR-0001 archive is forensic-only"
```

---

### Task 3: `.claude/rules/plan-conventions.md` — first project rule

**Files:**
- Create: `.claude/rules/plan-conventions.md`

- [ ] **Step 1: Create the directory and file**

Create `.claude/` and `.claude/rules/` if they do not exist, then write `.claude/rules/plan-conventions.md` with exactly the following content:

```markdown
# Plan Conventions

Scope: Applies when authoring or executing implementation plans under `docs/superpowers/plans/`.

## Plan Convention Augmentations

The `## Non-Goals` section in implementation plans serves two purposes:

1. **Scope constraints** — free-form one-liners describing what the plan never sets out to do (`Do not …`). This is the existing usage carried over from M1–M4 plans.

2. **Deferred fixes** — concerns surfaced during implementation review or grilling that are intentionally not addressed in this milestone. Each deferred item appears under a `### Deferred` subsection inside `## Non-Goals` and includes:
   - **Why deferred** — one sentence explaining the rationale.
   - **Trigger to revisit** — the concrete event or condition that should prompt reopening the item in a future plan.

This convention augments `superpowers:writing-plans` without overriding it. The plan author chooses scope; this rule formalizes how deferral is recorded once that choice is made, so the rationale is preserved alongside the plan rather than lost to session memory.
```

- [ ] **Step 2: Run tests and check**

```bash
rtk npm test
rtk npm run check
```
Expected: pass.

- [ ] **Step 3: Commit**

```bash
git add .claude/rules/plan-conventions.md
git commit -m "docs: add plan-conventions rule with deferred-fix format"
```

---

### Task 4: `docs/workflow.md` — fill four documentation gaps (concern #6)

**Files:**
- Modify: `docs/workflow.md`

- [ ] **Step 1: Define `cssOwner` inline at first use**

In `docs/workflow.md`, locate the `## Helpers` section. The current entry for `test/selector-usage-contract.test.js` reads:

```
  - `test/selector-usage-contract.test.js`: every class in `registry/selectors.yaml` is referenced inside its `cssOwner` partial.
```

Replace it with exactly:

```
  - `test/selector-usage-contract.test.js`: every class declared in `registry/selectors.yaml` is referenced inside the CSS partial named by that entry's `cssOwner` field (the partial path under `src/` that the selector entry says it lives in).
```

- [ ] **Step 2: Document the probe exit codes**

In `docs/workflow.md`, locate the `### Probe` subsection. The current step 3 reads:

```
3. The probe prints a JSON object with `results` (per-class `{class, source, count}`), `present`, and `missing` arrays. Exit code is `0` when every class is observed at least once and `1` when any class is missing.
```

Replace it with exactly:

```
3. The probe prints a JSON object with `results` (per-class `{class, source, count}`), `present`, and `missing` arrays. Exit codes:
   - `0` — every registered class for the screen was observed at least once in the live DOM.
   - `1` — at least one registered class was missing from the live DOM (the JSON payload still prints).
   - `2` — the probe itself failed (no `DISCORD_CDP_URL`, no Discord renderer found, CDP error, unknown screen, etc.). An error message is written to stderr.
```

- [ ] **Step 3: Document the `--replaced-by` option**

In `docs/workflow.md`, locate the `### Archive` subsection. The current command block reads:

```
rtk npm run archive -- <entry-key> --reason "<short why>" [--evidence "snapshots/YYYY-MM-DD/<screen>.json"] [--replaced-by <new-key>] [--from selectors|do-not-touch]
```

Immediately after the bullet list that follows (the three bullets explaining what the command does), add exactly the following two new bullets to the same list:

```
- The optional `--replaced-by <new-key>` records that the archived entry was succeeded by `<new-key>` in the same source registry. This is a forensic annotation only; the command does not verify that `<new-key>` exists. Use it when Discord renamed or restructured a class set and the active registry now has the replacement under a different entry key.
- The optional `--from <selectors|do-not-touch>` disambiguates the source registry when an entry key happens to exist in both. Without it, the command auto-detects and refuses to proceed if the key is ambiguous.
```

- [ ] **Step 4: Run tests and check**

```bash
rtk npm test
rtk npm run check
```
Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add docs/workflow.md
git commit -m "docs: clarify cssOwner, probe exit codes, and archive options in workflow.md"
```

---

### Task 5: Snapshot `themeVersion` derived from `package.json` (concern #7)

**Files:**
- Modify: `scripts/new-snapshot.js`
- Modify: `test/snapshot-scaffold.test.js`
- Modify: `docs/workflow.md`

- [ ] **Step 1: Write the failing test**

In `test/snapshot-scaffold.test.js`, the existing first test asserts various stub fields but does **not** assert `themeVersion`. Append the assertion to the existing first test and add one new test for an explicit `themeVersion` override path.

Locate this block (lines around 32–54):

```js
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

Replace it with exactly:

```js
test("scaffoldSnapshot creates a snapshot file at snapshots/<today>/<screen>.json with stub metadata", () => {
  const fsImpl = makeFsImpl();
  const result = scaffoldSnapshot({
    screen: "friends-page",
    today: "2026-06-01",
    root: "/repo",
    fsImpl,
    screensDoc,
    themeVersion: "9.9.9"
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
  assert.equal(parsed.themeVersion, "9.9.9");
  assert.deepEqual(parsed.elements, []);
  assert.match(parsed.capturedAt, /^2026-06-01/);
});

test("scaffoldSnapshot requires themeVersion to be provided by the caller", () => {
  const fsImpl = makeFsImpl();

  assert.throws(
    () =>
      scaffoldSnapshot({
        screen: "friends-page",
        today: "2026-06-01",
        root: "/repo",
        fsImpl,
        screensDoc
      }),
    /themeVersion is required/
  );
});
```

- [ ] **Step 2: Run tests to verify the new tests fail**

```bash
rtk npm test
```
Expected: the first test fails (because `themeVersion: "9.9.9"` is not accepted and the field is still hardcoded `"0.1.0"`), and the second test fails (because the function does not currently throw).

- [ ] **Step 3: Update `scaffoldSnapshot` to accept and require `themeVersion`**

In `scripts/new-snapshot.js`, locate this function (lines 6–39):

```js
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
```

Replace it with exactly:

```js
export function scaffoldSnapshot({ screen, today, root, fsImpl, screensDoc, themeVersion }) {
  const knownScreens = new Set(Object.keys(screensDoc?.screens ?? {}));
  if (!knownScreens.has(screen)) {
    throw new Error(`unknown screen "${screen}". Add it to registry/screens.yaml first.`);
  }

  if (typeof themeVersion !== "string" || themeVersion.length === 0) {
    throw new Error("themeVersion is required; pass the value from package.json");
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
    themeVersion,
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
```

- [ ] **Step 4: Update the CLI `main()` to read `themeVersion` from `package.json`**

In `scripts/new-snapshot.js`, locate the `main()` function (lines 41–61):

```js
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
```

Replace it with exactly:

```js
function main() {
  const screen = process.argv[2];
  if (!screen) {
    console.error("usage: node scripts/new-snapshot.js <screen-id>");
    process.exit(1);
  }

  const root = process.cwd();
  const screensDoc = YAML.parse(nodeFs.readFileSync(path.join(root, "registry/screens.yaml"), "utf8"));
  const pkg = JSON.parse(nodeFs.readFileSync(path.join(root, "package.json"), "utf8"));
  const today = new Date().toISOString().slice(0, 10);

  const { relativePath } = scaffoldSnapshot({
    screen,
    today,
    root,
    fsImpl: nodeFs,
    screensDoc,
    themeVersion: pkg.version
  });

  console.log(`Scaffolded ${relativePath}`);
}
```

- [ ] **Step 5: Run tests to verify all pass**

```bash
rtk npm test
```
Expected: all tests pass, including the two updated/added cases.

- [ ] **Step 6: Update the workflow placeholder list**

In `docs/workflow.md`, locate the `## Helpers` section. The current `snapshot:new` entry reads:

```
- `rtk npm run snapshot:new -- <screen-id>` creates `snapshots/YYYY-MM-DD/<screen-id>.json` with placeholder metadata for the requested screen. The script refuses to overwrite an existing file and refuses screens that are not in `registry/screens.yaml`. Replace placeholder fields (`viewport`, `routeHint`, `sourceScreenshot`, and the `elements` array) before committing.
```

Replace it with exactly:

```
- `rtk npm run snapshot:new -- <screen-id>` creates `snapshots/YYYY-MM-DD/<screen-id>.json` with placeholder metadata for the requested screen. The script refuses to overwrite an existing file and refuses screens that are not in `registry/screens.yaml`. The `themeVersion` field is auto-filled from `package.json` and stays correct as the theme version advances. Replace placeholder fields (`viewport`, `routeHint`, `sourceScreenshot`, the `elements` array, and the `discordBuild` / `vencordVersion` / `os` / `zoom` `"unknown"` markers as relevant) before committing.
```

- [ ] **Step 7: Run check**

```bash
rtk npm run check
```
Expected: pass.

- [ ] **Step 8: Commit**

```bash
git add scripts/new-snapshot.js test/snapshot-scaffold.test.js docs/workflow.md
git commit -m "fix: derive snapshot themeVersion from package.json"
```

---

### Task 6: `archive-entry.js` — isCli guard and parseArgs bounds (concern #2 + #3)

**Files:**
- Modify: `scripts/archive-entry.js`

- [ ] **Step 1: Add the isCli guard at module bottom**

In `scripts/archive-entry.js`, the file currently ends with (line 99):

```js
main();
```

Replace that single line with exactly:

```js
const isCli = process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname);
if (isCli) {
  main();
}
```

- [ ] **Step 2: Tighten `parseArgs` bounds checks**

In `scripts/archive-entry.js`, locate the `parseArgs` function (lines 17–33):

```js
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
```

Replace it with exactly:

```js
function parseArgs(argv) {
  const args = { key: undefined, from: undefined, reason: undefined, evidence: undefined, replacedBy: undefined };

  function consumeValue(flag) {
    if (i + 1 >= argv.length) {
      throw new Error(`${flag} requires a value`);
    }
    return argv[++i];
  }

  let i = 0;
  for (; i < argv.length; i++) {
    const token = argv[i];
    if (token === "--from") args.from = consumeValue("--from");
    else if (token === "--reason") args.reason = consumeValue("--reason");
    else if (token === "--evidence") args.evidence = consumeValue("--evidence");
    else if (token === "--replaced-by") args.replacedBy = consumeValue("--replaced-by");
    else if (!args.key) args.key = token;
    else throw new Error(`unexpected argument: ${token}`);
  }

  if (!args.key) throw new Error("missing required positional argument: <key>");
  if (!args.reason) throw new Error("missing required option: --reason <text>");
  return args;
}
```

- [ ] **Step 3: Run tests and check**

```bash
rtk npm test
rtk npm run check
```
Expected: pass. `archive-lib.test.js` does not exercise `parseArgs`; the change is observable only via the CLI behavior change (trailing flag now errors instead of silently passing `undefined`). The isCli guard removes the prior top-level execution side effect on import.

- [ ] **Step 4: Commit**

```bash
git add scripts/archive-entry.js
git commit -m "fix: guard archive-entry main() and bound parseArgs flag values"
```

---

### Task 7: `probe-discord-dom.js` — CDP evaluate timeout (concern #4) and listener intent comment (concern #5)

**Files:**
- Modify: `scripts/probe-discord-dom.js`

- [ ] **Step 1: Add a timeout to the real CDP client's `evaluate`**

In `scripts/probe-discord-dom.js`, locate the `buildRealCdpClient` function (lines 91–98):

```js
function buildRealCdpClient(baseUrl) {
  return {
    async evaluate(expression) {
      const target = await findDiscordTarget(baseUrl);
      return evaluateOnTarget(target.webSocketDebuggerUrl, expression);
    }
  };
}
```

Replace it with exactly:

```js
const DEFAULT_CDP_EVALUATE_TIMEOUT_MS = 10000;

function buildRealCdpClient(baseUrl, { timeoutMs = DEFAULT_CDP_EVALUATE_TIMEOUT_MS } = {}) {
  return {
    async evaluate(expression) {
      const target = await findDiscordTarget(baseUrl);
      let timeoutHandle;
      const timeoutPromise = new Promise((_, reject) => {
        timeoutHandle = setTimeout(
          () => reject(new Error(`CDP Runtime.evaluate timed out after ${timeoutMs}ms; Discord may be unresponsive`)),
          timeoutMs
        );
      });
      try {
        return await Promise.race([
          evaluateOnTarget(target.webSocketDebuggerUrl, expression),
          timeoutPromise
        ]);
      } finally {
        clearTimeout(timeoutHandle);
      }
    }
  };
}
```

- [ ] **Step 2: Add an intent comment to the message listener (concern #5)**

In `scripts/probe-discord-dom.js`, locate the message listener inside `evaluateOnTarget` (around lines 61–71):

```js
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
```

Replace it with exactly:

```js
  const replied = new Promise((resolve, reject) => {
    // Listener stays attached across messages because CDP may emit unsolicited
    // events before our id=1 reply arrives; ws.close() below detaches once we
    // match on data.id === 1.
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
```

The error listener already uses `{ once: true }` correctly — a single error terminates the call.

- [ ] **Step 3: Run tests and check**

```bash
rtk npm test
rtk npm run check
```
Expected: pass. The timeout wrapper around the real CDP client is not unit-tested in this plan because the WebSocket lifecycle would require dependency injection beyond M5's scope; the change is covered by code review and by the existing `probe-lib.test.js` suite, which already injects mock `cdpClient`s and remains untouched. The intent comment is documentation-only.

- [ ] **Step 4: Commit**

```bash
git add scripts/probe-discord-dom.js
git commit -m "fix: add CDP evaluate timeout and clarify message listener intent in probe"
```

---

### Task 8: Sync `CLAUDE.md` with `AGENTS.md` and start tracking it

**Files:**
- Modify: `AGENTS.md`
- Create (start tracking): `CLAUDE.md`

**Context:** `CLAUDE.md` exists locally on master but is untracked (`.gitignore` does not list it; it was a manual file the user created so Claude Code's auto-load picks something up, while `AGENTS.md` was the git-tracked canonical). M3 updated only `AGENTS.md`, so the two files drifted. M5 reconciles by starting to track `CLAUDE.md` and keeping the two files byte-identical from here onward.

- [ ] **Step 1: Write the new canonical body to `AGENTS.md`**

Replace the entire contents of `AGENTS.md` with exactly:

```markdown
# Agent Instructions

This repo manages a private Vencord Discord theme.

Reference map:
- `CONTEXT.md` — concise theme memory, visual direction, domain glossary, and safety boundaries.
- `docs/workflow.md` — detailed playbook for turning user visual intent into selector, CSS, registry, snapshot, build, check, commit, and optional sync work. Includes Discord CDP setup, probe, and archive sections.
- `docs/adr/` — architectural decision records. Read the relevant ADR before re-litigating a decision recorded there.
- `.claude/rules/plan-conventions.md` — auto-loaded rule documenting the `## Non-Goals → ### Deferred` format for implementation plans under `docs/superpowers/plans/`.

Rules:
- Treat `src/` as the CSS source of truth.
- Treat `dist/NewKemonoFriends.theme.css` as generated output.
- Do not edit files in the Vencord themes directory directly from this repo.
- Add raw DOM observations to `snapshots/YYYY-MM-DD/*.json`.
- Update `registry/selectors.yaml` when a selector is added, removed, or reclassified.
- Add dangerous media/rendering selectors to `registry/do-not-touch.yaml`.
- Keep `theme.manifest.yaml` as the only build-order authority.
- Do not modify `registry/archive.yaml` directly; use the `archive` command. See ADR-0001.
- Do not run `npm run probe` against real Discord during plan execution; probe usage is interactive and user-initiated.
- Run `npm run check` before syncing.
```

- [ ] **Step 2: Copy `AGENTS.md` to `CLAUDE.md` so the two are byte-identical**

```bash
cp AGENTS.md CLAUDE.md
```

Verify:

```bash
rtk diff AGENTS.md CLAUDE.md
```
Expected: no output (files identical).

- [ ] **Step 3: Run tests and check**

```bash
rtk npm test
rtk npm run check
```
Expected: pass. Both files are doc-only.

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md CLAUDE.md
git commit -m "docs: sync AGENTS.md and CLAUDE.md with M5 reference map and start tracking CLAUDE.md"
```

**Maintenance note for future plans:** When this reference map needs updating (a new doc residence added, a rule changed), update both files together in the same commit. The two are intentionally byte-identical because Claude Code auto-loads `CLAUDE.md` while other agent CLIs (codex, etc.) auto-load `AGENTS.md`; keeping them in sync prevents drift between agent toolchains.

---

## Self-Review

- **Spec coverage:**
  - "Lock M3/M4 drift detection conventions into project memory" — Tasks 1, 2, 3 cover CONTEXT.md vocabulary, ADR-0001 forensic-only, and `.claude/rules/plan-conventions.md`. Task 8 makes the new reference map visible to both Claude Code (`CLAUDE.md`) and other agent CLIs (`AGENTS.md`).
  - "Fix six high-priority concerns from M3/M4 review" — Tasks 4 (concern #6), 5 (concern #7), 6 (concerns #2 + #3), 7 (concerns #4 + #5). All six addressed.
  - "Self-demonstrating Non-Goals" — the `### Deferred` section contains both the four remaining M3/M4 concerns (1, 8, 9, orphan) and the architecture candidates, each with Why / Trigger, exercising the convention this plan introduces in Task 3.
  - "No new feature surface, no new scripts, no new dependencies" — verified per task above; only new files are documentation (CONTEXT.md edits, ADR, plan-conventions, workflow.md edits, AGENTS.md / CLAUDE.md sync).
  - "Resolve CLAUDE.md / AGENTS.md drift" — Task 8 starts tracking `CLAUDE.md` and pins both files to identical content, with a maintenance note documenting why they must stay in sync going forward.

- **Placeholder scan:** No TBD, TODO, "implement later", "fill in details", "Add appropriate error handling", "write tests later", or "similar to Task N" appears in any task. All code blocks are complete and copy-pasteable.

- **Type and API consistency:**
  - `scaffoldSnapshot` adds one required parameter `themeVersion: string`; the CLI `main()` and both test cases supply it. The new "themeVersion is required" error string matches the test's regex `/themeVersion is required/`.
  - `parseArgs`'s `consumeValue` is an inner function closing over `i`; `i` is hoisted with `let` declared before the loop. The flag-value error strings (`"--from requires a value"` etc.) are not asserted by any test and are user-facing only.
  - `buildRealCdpClient` accepts an optional `{ timeoutMs }` second argument; no caller in this plan passes a second argument, so the default 10000ms applies in production.
  - The intent comment in Task 7 Step 2 has no code-level effect.

- **Convention compliance:** The `### Deferred` subsection in this plan's `## Non-Goals` follows the format introduced by Task 3's `.claude/rules/plan-conventions.md` — each item carries *Why deferred* and *Trigger to revisit* lines. Future plans inherit this convention automatically since `plan-conventions.md` is auto-loaded as a project rule.
