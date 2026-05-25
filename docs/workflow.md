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
