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
