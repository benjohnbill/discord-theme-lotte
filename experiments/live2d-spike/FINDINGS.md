# Live2D Spike — FINDINGS

Living record of Phase 0 feasibility results. Three gates: (1) Vencord custom-plugin
capability, (runtime) standalone Live2D render + cursor tracking, (3) in-Discord
injection + CSP. Ends with a go/no-go in the Decision section.

Working environment: Discord desktop runs on Windows; this repo and the spike run in WSL2.
The Vencord user-data dir is at `/mnt/c/Users/benjohnbill/AppData/Roaming/Vencord/`.

---

## Gate 1 — Vencord plugin capability (Task 1)

**Verdict: STOCK installer build. Custom JS userplugins are NOT loadable as-is.**

Evidence (read-only investigation, no Discord changes):

- **User-data dir confirmed.** `AppData/Roaming/Vencord/` contains `themes/`, `settings/`, `dist/`.
  `themes/NewKemonoFriends.theme.css` is present — this is the theme sync target, confirming
  Vencord is installed and active.
- **No source clone found.** Searched for a `userplugins/` directory across the likely Windows
  dev locations (`~`, `~/dev`, `~/Documents`, `~/source`, maxdepth 4) and the WSL home (maxdepth 5).
  **Zero results.** The only directory named `Vencord` anywhere is the AppData user-data dir
  (the stock installer's data dir), not a Git source checkout.
- **settings.json** lists only the canonical Vencord built-in plugins (CommandsAPI,
  MessageAccessoriesAPI, UserSettingsAPI, CrashHandler enabled; the rest of the standard catalog
  disabled). No custom userplugin entries.

**Conclusion:** A stock Vencord install loads themes (CSS) but cannot load custom JS plugins.
Running the throwaway `LotteLive2dSpike` userplugin (Task 3) requires standing up a **Vencord
source/dev build** and re-injecting it into the Windows Discord install. This is the real cost
that gates Task 3.

### Bonus finding — custom CSP is already in use (relevant to Gate 3 / CSP)

`settings/native-settings.json` contains:

```json
"customCspRules": {
  "images5.alphacoders.com": ["connect-src", "img-src", "style-src", "font-src"]
}
```

The user already whitelists a remote domain via Vencord's `customCspRules` mechanism (almost
certainly to let the current theme load its background image). **Implication for Task 3:** Discord's
CSP can be relaxed per-domain through `native-settings.json` rather than only by bundling the runtime
into the plugin. Loading remote `<script>` tags additionally needs a `script-src` entry for the CDN
domains (`cdn.jsdelivr.net`, `cubism.live2d.com`). This is a lighter mitigation path than full
bundling — to be confirmed in Task 3 if/when we proceed.

### Dev-build path (recorded for Task 3 — NOT executed in this session)

Run on the side that owns the Discord install — Windows here:

```text
git clone https://github.com/Vendicated/Vencord
cd Vencord && pnpm install --frozen-lockfile
mkdir -p src/userplugins
(place the plugin under src/userplugins/lotteLive2dSpike/)
pnpm build
pnpm inject     # patches the local Discord desktop install; pick the right branch
```

Maintenance cost: re-run `pnpm build` (and sometimes re-inject) after Discord/Vencord updates.

Cross-env caveat: building can be done in WSL, but `pnpm inject` must target the **Windows**
Discord install. If WSL-side inject cannot see the Windows Discord, run the build/inject on the
Windows side (Node + pnpm on Windows). Confirm which works during Task 3.

---

## Gate runtime — standalone Live2D (Task 2)

_(pending)_

---

## Gate 1 proof — in Discord (Task 3)

_(pending — requires explicit user approval; patches the real Discord client)_

---

## Decision (Task 4)

_(pending)_
