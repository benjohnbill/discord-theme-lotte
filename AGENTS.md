# Agent Instructions

This repo manages a private Vencord Discord theme.

Rules:
- Treat `src/` as the CSS source of truth.
- Treat `dist/NewKemonoFriends.theme.css` as generated output.
- Do not edit files in the Vencord themes directory directly from this repo.
- Add raw DOM observations to `snapshots/YYYY-MM-DD/*.json`.
- Update `registry/selectors.yaml` when a selector is added, removed, or reclassified.
- Add dangerous media/rendering selectors to `registry/do-not-touch.yaml`.
- Keep `theme.manifest.yaml` as the only build-order authority.
- Run `npm run check` before syncing.
