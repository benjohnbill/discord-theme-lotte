---
name: live2d-authoring
description: Use when tuning, animating, or verifying the Lotte Live2D rig — routes config / JSON / motion / expression authoring and the no-WebGL verification recipe, and marks the boundary where work crosses back to the Cubism GUI (geometry / keyforms / new params / export). NOT for cutting mesh or building deformers; those are USER-only in the Editor.
---

# Live2D Authoring (Lotte rig)

The agent's repeatable authority over the **drivable / authorable** layer of the Lotte rig —
config tuning, motion/expression authoring, and verification — with the geometry boundary made
explicit. This skill is **procedure, not state**: read `live2d/PIPELINE.md` FIRST for where we are.

> **Why this shape (decided 2026-06-02, grill session):** the Cubism *Editor* has no rig-authoring
> API — mesh/deformer/keyform authoring is GUI-only (USER). But the post-export artifacts
> (`model3 / cdi3 / physics3 / motion3 / exp3`), the probe, and the runtime harness are plain
> JSON/JS the agent owns fully. The pivot (ADR-0001) moves the heavy work OUT of the GUI layer, so
> most remaining iteration is authorable. This skill formalizes that division of labor. Full
> rationale: [[live2d-claude-cubism-authority]].

## Three-tier authority map

| Tier | What | Who | Official API? |
|---|---|---|---|
| **1 — post-export artifacts** | `model3 / cdi3 / physics3 / motion3 / exp3.json`, `build_discord_probe.py`, `runtime-check-full.html` | **agent** (this skill) | n/a — plain JSON/JS |
| **2 — live Editor drive** | read params, `SetParameterValues` (pose), export-event notifications | **agent via MCP** (Tier-2, deferred to Phase C/D) | yes — External API, WebSocket `:22033` |
| **3 — geometry rigging** | ArtMesh/vertices, deformers, keyforms, *creating* params, *triggering* export | **USER, Cubism GUI only** | **no** |

## Routing — task → tier → touch → verify

| Ask | Tier | Touch | Verify |
|---|---|---|---|
| gaze / tilt / turn / lean amplitude, head-lean vs iris | 1 config | `build_discord_probe.py` (`GAZE`, `im.updateFocus`) | harness `?p=` montage |
| breath rate / depth | 1 config | probe / `ParamBreath` driver | `?p=` + `breathoff` A/B |
| hair / ribbon physics feel (lag, scale, delay) | 1 config | `live2d/model/lotte.physics3.json` | `?autosine` + `phase_measure.py` |
| timed idle animation (glance loop, settle, periodic tilt) | 1 motion | **new** `*.motion3.json` + wire in `model3.json` | `?cinema` |
| expression preset (happy ^^, surprised, soft) | 1 expr | **new** `*.exp3.json` | `?p=` pins / expression load |
| param wiring, EyeBlink/LipSync groups | 1 wiring | `model3.json`, `tools/check_model.py` | runtime load |
| blink band (feathered opacity-swap, Phase C) | 2↔3 boundary | `full_segment.py` band + Cubism re-rig | harness blink at real scale |
| **new keyform / asymmetric pose / wink** | **3 GEOMETRY** | **USER in Cubism GUI** | export-hook → `check_model.py` |
| **cut/merge a face part, deformer, mesh edit** | **3 GEOMETRY** | **USER (W3↔W4 loop)** | re-export → runtime montage |

## The human-in-loop boundary (STOP conditions)

Hand back to the USER's Cubism GUI — do not try to fake it in JSON — when the ask needs any of:
**a new keyform**, **a new parameter**, **mesh / ArtMesh / vertex edits**, **deformer creation**,
or **an export**. Give the USER the *exact* Cubism instruction (which param/keyform, which deformer),
then catch the export (Tier-2 MCP at Phase C/D, or a manual "exported" signal until then) and verify.

## Verification recipe (no WebGL in headless — the consolidated how-to)

- **bh-chrome has NO WebGL** → use a **SwiftShader throwaway Chrome** or the **real Discord client**
  for any render/Live2D check (memory [[bh-chrome-no-webgl]]). Never conclude "broken" from bh-chrome.
- **Harness:** `live2d/runtime-check-full.html`. URL params: `p=Id:val,…` (pin params), `blinkoff` /
  `breathoff`, `scale` / `ax` / `ay` / `ox` / `oy` (framing), `freeze`, `?autosine` / `?cinema`
  (motion), `?imgbg=` (backdrop).
- **Capture gotcha:** PIXI's continuous rAF stops `--virtual-time-budget` from expiring, so the
  headless proc never exits. Keep the ticker running for a clean paint (SwiftShader needs real
  frames); kill the chrome **MAIN proc by PID** afterward (`pgrep -f` self-matches — kill by PID).
- **Physics / phase:** persistent headless Chrome (NO `--virtual-time-budget`; `--remote-allow-origins=*`)
  + `?autosine` + CDP frame capture + `/tmp/phase_measure.py`. Frame-diff measures *amount*; phase lag
  measures what reads as *natural*.
- **Backdrop alignment:** verify composites on the REAL `version` lavender background, not dark navy
  (the W5 halo "issue" was a dark-bg artifact — env-alignment lesson).

## Tier-2 MCP (export-hook) — deferred

The Cubism Editor External API (WebSocket `:22033`) gives a **passive export-event listener**: on
USER export, auto-run `check_model.py` + `sync` and report. Structured so live `SetParameterValues`
posing (blind-drive; USER watches) flips on for a rigging sprint. **Build just-in-time at Phase C/D**
(first real Editor re-export) — dead weight until the Editor re-opens; gate it on a live connect
(portproxy `:22033`, handshake, prove `GetParameters`). WSL→Windows reach uses the same `netsh
portproxy` pattern as chrome-devtools. ToS: official API + plain JSON only — never a reverse-engineered
moc3 writer.

## References (state + schemas live here — do not duplicate)

- `live2d/PIPELINE.md` — pipeline-state authority (read FIRST)
- `live2d/DOMAIN_MAP.md` — platform/tool facts (✅/⛔: moc3 ≤5, single-2048 atlas, machine-ops, verify recipe)
- `docs/features/tongjja-rig/` — the 통짜 strategy (ADR-0001): `RIG_PROCEDURE` (the CD-1..9 walkthrough, reused
  across investigations) + `INDEX`
- `docs/features/cd4-blink/` — active blink investigation: `INDEX` (hub) · `RESEARCH` (saga, open ❓) · `DECISIONS`
- `live2d/CONTEXT.md` — glossary. **As-built rig tree = the model files** (`pilot/lotte-good.cmo3`, `model/`)
- `docs/adr/` — 0001 pivot · 0004 locked rig constraints (flat discipline) · 0002 this skill's mandate
- memory [[bh-chrome-no-webgl]], [[live2d-claude-cubism-authority]]
