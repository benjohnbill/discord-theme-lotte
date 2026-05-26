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
  - `test/selector-usage-contract.test.js`: every class declared in `registry/selectors.yaml` is referenced inside the CSS partial named by that entry's `cssOwner` field (the partial path under `src/` that the selector entry says it lives in).
  - `test/snapshot-scaffold.test.js`: the snapshot scaffolder enforces its contract.
- These tests do not launch a browser, do not open Discord, and do not touch the Vencord live theme directory.

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

3. The probe prints a JSON object with `results` (per-class `{class, source, count}`), `present`, and `missing` arrays. Exit codes:
   - `0` — every registered class for the screen was observed at least once in the live DOM.
   - `1` — at least one registered class was missing from the live DOM (the JSON payload still prints).
   - `2` — the probe itself failed (no `DISCORD_CDP_URL`, no Discord renderer found, CDP error, unknown screen, etc.). An error message is written to stderr.

### Archive

When a class is in `missing` and you confirm Discord no longer renders it on the relevant screen:

```bash
rtk npm run archive -- <entry-key> --reason "<short why>" [--evidence "snapshots/YYYY-MM-DD/<screen>.json"] [--replaced-by <new-key>] [--from selectors|do-not-touch]
```

The command:

- Reads the entry from `registry/selectors.yaml` or `registry/do-not-touch.yaml` (auto-detects if the key is unambiguous; otherwise requires `--from`).
- Appends a record to `registry/archive.yaml` with `archivedAt: <today>`, the original entry as `snapshot`, and the provided `reason` / `evidence` / `replacedBy`.
- Removes the entry from the source registry.
- The optional `--replaced-by <new-key>` records that the archived entry was succeeded by `<new-key>` in the same source registry. This is a forensic annotation only; the command does not verify that `<new-key>` exists. Use it when Discord renamed or restructured a class set and the active registry now has the replacement under a different entry key.
- The optional `--from <selectors|do-not-touch>` disambiguates the source registry when an entry key happens to exist in both. Without it, the command auto-detects and refuses to proceed if the key is ambiguous.

The command does NOT touch CSS partials. After archiving, manually prune the orphan CSS block in the entry's former `cssOwner` partial if it now does nothing. `rtk npm run check` and `rtk npm test` should still pass.

### Caveats

- The probe is read-only. It runs only `document.querySelectorAll('.<class>').length` expressions through CDP.
- The probe is screen-aware. A class that exists only when a voice call is active will be reported as missing if the user is not currently in a call. Open the correct Discord screen before probing.
- Archive is forensic-only. Once an entry is archived, it is not garbage-collected; the file grows append-only. Audit `registry/archive.yaml` periodically when looking for replaced entries.
- YAML serialization through `YAML.stringify` does not preserve source comments. Registry files in this repo currently carry no meaningful comments, so this is acceptable for M4 v1.
