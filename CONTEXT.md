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
