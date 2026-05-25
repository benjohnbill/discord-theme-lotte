# Discord Theme Lotte

Private source repository for the Lotte-themed Vencord Discord CSS theme.

## Source Of Truth

- Edit CSS in `src/`.
- Build generated CSS into `dist/NewKemonoFriends.theme.css`.
- Sync generated CSS to Vencord with `npm run sync`.
- Do not edit the Vencord theme file directly except for emergency recovery.

## Commands

```bash
npm install
npm run validate
npm run build
npm run sync
```

Run `npm run check` before syncing or handing off changes. It validates the
registries and snapshots, then rebuilds `dist/NewKemonoFriends.theme.css`.

## Data Model

- `registry/*.yaml` is the agent-readable index.
- `snapshots/**/*.json` is raw or sanitized DOM evidence.
- `screenshots/**` stores visual reference states.
- `schema/*.json` validates registry and snapshot structure.

## Snapshot Workflow

Use `scripts/inspect-dom.js` from Discord DevTools when capturing live DOM
observations, then save the output under `snapshots/YYYY-MM-DD/*.json` and
validate it with `npm run check`.

Snapshots may be either live captures or seed/sanitized baselines. For sanitized
baselines, preserve the structural facts that matter to the theme: selector
hashes, element roles, approximate rectangles, backgrounds, borders, and the
screen goal being exercised. Do not include friend names, server names, channel
names, message text, avatars, call content, or any other private account
content. Replace those details with neutral labels such as `Sample Friend`,
`Sample Server`, or `Sample Voice Channel`.

Every snapshot must include `schemaVersion`, `capturedAt`, `screen`,
`routeHint`, `viewport`, `sourceScreenshot`, and `elements`. Avoid placeholder
metadata such as `unknown` or `replace-with-*`; the validator rejects those
top-level values.

`sourceScreenshot` should match the corresponding `latestScreenshot` entry in
`registry/screens.yaml`. Screenshot paths can point at private local evidence
used during manual review; those image files do not have to be committed when
they contain private Discord UI state.
