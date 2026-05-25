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
- Keep Milestone 1 tests limited to Node workspace contract tests.

## Registry And Snapshot Rules

- Registries are structured memory and should be updated when selector knowledge changes.
- Snapshots are raw evidence and should stay dated under `snapshots/YYYY-MM-DD/`.
- Prose docs may explain how evidence is used, but they should not duplicate selector inventories.

## Commit Shape

- Prefer small commits that map to one durable workspace improvement.
- Keep generated `dist/NewKemonoFriends.theme.css` changes in the same commit as the source or manifest change that produced them.
- Do not include unrelated local edits.

## Helpers

- `rtk npm run snapshot:new -- <screen-id>` creates `snapshots/YYYY-MM-DD/<screen-id>.json` with placeholder metadata for the requested screen. The script refuses to overwrite an existing file and refuses screens that are not in `registry/screens.yaml`. Replace placeholder fields (`viewport`, `routeHint`, `sourceScreenshot`, and the `elements` array) before committing.
- `rtk npm test` runs the workspace contract suite, including:
  - `test/build-contract.test.js`: the generated theme follows the manifest output and partial order.
  - `test/registry-cross-references.test.js`: registry and snapshot cross-references hold.
  - `test/selector-usage-contract.test.js`: every class in `registry/selectors.yaml` is referenced inside its `cssOwner` partial.
  - `test/snapshot-scaffold.test.js`: the snapshot scaffolder enforces its contract.
- These tests do not launch a browser, do not open Discord, and do not touch the Vencord live theme directory.
