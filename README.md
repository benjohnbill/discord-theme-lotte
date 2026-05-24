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

## Data Model

- `registry/*.yaml` is the agent-readable index.
- `snapshots/**/*.json` is raw DOM evidence.
- `screenshots/**` stores visual reference states.
- `schema/*.json` validates registry and snapshot structure.
