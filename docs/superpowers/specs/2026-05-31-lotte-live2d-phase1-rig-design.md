# Lotte Live2D — Phase 1 (Rig the Real Lotte) Design

> Status: validated in the 2026-05-31 brainstorm; pending user review before the implementation plan (writing-plans).
> Builds on Phase 0 (feasibility spike), which reached **GO**: Discord's Electron client renders `pixi-live2d-display` full-window behind the translucent UI, allows the CDN runtime with zero CSP violations, reports WebGL 2, and tracks the cursor via `model.focus(x, y)`. See `experiments/live2d-spike/FINDINGS.md`.

This document is the spec for Phase 1. It captures the decided design, the locked aesthetic/technical constraints, the work decomposition, and the cross-tool/cross-session orchestration model. The phase-by-phase implementation steps are produced separately by writing-plans.

---

## 1. Goal & Scope

**Goal.** Turn the existing flat Lotte illustration into a single Cubism rig and swap it into the proven Phase 0 plumbing, so that the Discord background character is *reactively alive* at Tier 1: she blinks, breathes, her hair and ribbon sway, her gaze follows the cursor, and she occasionally meets the cursor and smiles — while still reading as the flat 2D anime illustration the user already loves.

**In scope (Phase 1).**
- The **Discord surface only**, framed as a **bust** (head + shoulders + upper chest, matching the current Discord background `Lotte discord version.png`).
- One portable, character-only Cubism model with Tier-1 reactivity.
- Integration into the Phase 0 standalone page and console-probe plumbing, plus verification.

**Out of scope / deferred.**
- **Mobile** live wallpaper — stays a **static image** for now (revisit later).
- Desktop wallpaper (Lively) port — later phase (the rig is portable, so this is unconstrained once Phase 1 exists).
- **Phase 2 production delivery** — turning the console probe into a persistent Vencord userplugin (requires a self-built dev Vencord; tracked in FINDINGS as a Phase 2 cost).
- Background particle drift (petals/bokeh) — optional code-side (PIXI) enhancement, deferred to W5/later.
- Tier 2/3 attention, animated avatar/banner, informational presence, workspace pet.

---

## 2. Locked Decisions

These are settled; they seed `live2d/DECISIONS.md` and are not to be re-litigated without new information.

1. **Technique = Live2D mesh deformation (path A), not frame/sprite animation.** Reactive cursor-aware presence requires runtime deformation, not a sequence of pre-rendered frames. Frame/sprite was rejected: it cannot do continuous gaze tracking, and GPT-image-2 per-generation drift would make a frame sequence jitter. Phase 0 already proved the Live2D path in the real Discord client.

2. **Scope = Discord bust only; mobile stays static.** Smallest complete end-to-end slice. Lets the user learn the full pipeline once before any extension.

3. **Base image is locked, not regenerated.** The source illustrations were produced by iterative revision, so a single prompt cannot reproduce the base. Phase 1 therefore **locks one existing raster** as the base and commits to it. Recommended base: `Lotte discord version.png` (1586×992, 16:10) for the on-Discord look and its particle background. The *character pixels* may instead be taken from `Lotte discord original.png` (1254×1254) if it yields more facial resolution — decided by live comparison in W1. Upscale the chosen base with waifu2x before separation.

4. **Cubism 5 FREE (`.moc3`).** Free tier is sufficient for a Tier-1 bust. Runtime change from Phase 0: swap the Cubism **2** core (`dylanNew` mirror) for the **official Cubism 4 core** (`live2dcubismcore.js`); PIXI v6 + `pixi-live2d-display` otherwise unchanged.

5. **Background is OUT of the model.** The Cubism model is **character-only with a transparent background**. Each surface supplies its own background (the Discord theme CSS background for now). This matches Phase 0 (`backgroundAlpha: 0`), keeps the rig portable across surfaces, and avoids rigging individual petals. Particle drift is an optional code-side enhancement, deferred.

6. **Flat-rig discipline (aesthetic guardrail).** The "3D / VTuber" feel of a Live2D model comes almost entirely from *pseudo-3D head-turn depth* (cheek compression, nose parallax on `ParamAngleX/Y`), which is a rigging choice — not a requirement of reactivity. To preserve the flat 2D illustration look:
   - Put reactivity on **flat channels**: eye gaze (`ParamEyeBallX/Y`), blink, breath, head **tilt** (`ParamAngleZ`), hair/ribbon physics, smile.
   - Keep head **turn** (`ParamAngleX/Y`) **small and flat-rigged** — no pseudo-3D depth. A slight planar shift/tilt is enough to read as "turned toward you."
   - Make the **eye gaze + cute head tilt** the primary "she's looking at me" signal.
   - Keep all deformations gentle; visible warping is what reads as rubbery/3D.
   - Accepted trade-off: no large head rotations (Tier-1 restraint did not want them anyway).
   - Rigging deforms the existing pixels; it does not repaint. Lotte keeps her art style.

7. **Tier-1 restraint.** Most of the life comes for free from runtime auto-blink + auto-breath and from hair/ribbon physics. The only cursor-reactive motion is a **small, damped** gaze + slight head, plus an **occasional** eye-contact smile. Start under-animated; add only if it feels dead.

---

## 3. Reactive Behavior (Tier 1)

| Source | Behavior | Driver |
|---|---|---|
| Runtime auto | Blink | `pixi-live2d-display` auto-blink |
| Runtime auto | Breath (subtle shoulder/chest rise) | auto-breath sine |
| Physics | Back hair (L/R), side hair (L/R), bangs, ribbon sway | Cubism Physics, derived from head/body angle |
| Cursor-reactive | Iris gaze — the primary "notices me" signal | `model.focus(cursorX, cursorY)` → `ParamEyeBallX/Y` |
| Cursor-reactive | Gentle, **damped** head tilt/turn + body lean | `ParamAngleX/Y/Z`, `ParamBodyAngleX` (small range, flat) |
| Occasional | Eye-contact + pretty smile, then relax | coded behavior in W5: gaze snaps softly to cursor + smile expression (smile eyes via `ParamEyeForm`, smile mouth via `ParamMouthForm`), infrequent and gentle; candidate trigger = window refocus and/or a long random interval |

**Restraint controls:** the eye-contact-smile frequency and all damping start conservative. A constant smile reads as animatronic.

---

## 4. Layer Map (character-only, ~20–23 parts)

Depth-ordered, back to front. Counts are a starting target; W3 may merge/split slightly.

| Depth | Part | Count | Rig purpose / source note |
|---|---|---|---|
| back | Back hair L / R | 2 | independent sway |
| | Body + sailor uniform (collar included) | 1 | breath, body lean |
| | Scarf knot (neckerchief) | 1 | sway with body |
| | Neck | 1 | — |
| | **Face base** (skin, cheeks, ears, forehead) | 1 | needs forehead (under bangs) and cheek/jaw (under side hair) reconstructed |
| | Eyebrows L / R | 2 | subtle expression |
| | Eye whites (sclera) L / R | 2 | container for irises |
| | Irises / pupils L / R | 2 | **gaze** (cursor tracking) |
| | Upper eyelids + lashes L / R | 2 | **blink**; needs eyes-closed skin |
| | Lower eyelids L / R | 2 | promoted for the **eye-smile** (lid rises) |
| | Mouth — outer + inner (teeth/interior) | 2 | open↔closed + smile form |
| front | Side hair L / R | 2 | sway, frames the face |
| | Bangs (front hair) | 1–2 | sway, occludes forehead |
| | Ribbon / bow | 1 | physics sway |

### Hidden-state assets to generate in W2 (GPT-image-2 bridge edits on the locked base)

Separating overlapping parts exposes pixels that do not exist in a flat image. Six high-value reconstruction points:

1. **Forehead** — hair pushed back (for face base under bangs).
2. **Cheek / jaw line** — side hair tucked (for face base under side hair).
3. **Eyes-closed skin** — for the upper-eyelid blink art.
4. **Smiling (softly creased) eyes** — for the pretty eye-smile (`ParamEyeForm`).
5. **Closed mouth** — high value: unlocks both the tight-closed mouth and the closed smile via `ParamMouthForm`. (The base already has the open mouth with visible interior.)
6. *(optional)* **Gentle closed smile mouth** — only if deriving it from closed + form looks unnatural.

Other occlusions (hair beneath the ribbon, shoulders behind back hair) are filled by agent scripting from symmetry/surroundings, not by GPT.

> Note on mouth/eye states: Live2D defines two **extremes** as art and morphs between them with parameters. We do not draw every state. Mouth = open (have) + closed (generate), all intermediate forms via `ParamMouthOpenY` / `ParamMouthForm`. Eye-smile needs its own reference because a flat blink (`ParamEyeOpen`) cannot produce the upturned ^^ crease.

---

## 5. Rig Parameter Set

| Parameter | Effect | Driven by | Tier 1 |
|---|---|---|---|
| `ParamEyeLOpen` / `ParamEyeROpen` | blink | runtime auto-blink | core |
| `ParamBreath` | breathing | runtime auto-breath | core |
| Physics (hair, ribbon) | secondary sway | derived from angle/body params | core |
| `ParamEyeBallX` / `ParamEyeBallY` | iris gaze | `model.focus(cursor)` | core |
| `ParamEyeForm` | eye-smile crease | occasional smile behavior | adopted |
| `ParamAngleX` / `ParamAngleY` | head turn (yaw/pitch) | small, damped, **flat-rigged** | restrained |
| `ParamAngleZ` | head tilt | idle + gaze liveliness | subtle |
| `ParamBodyAngleX` | body lean | idle + slight follow | subtle |
| `ParamMouthOpenY` / `ParamMouthForm` | mouth open + smile form | occasional smile; otherwise near-static open smile | adopted |
| brow / other expression params | — | — | deferred |

---

## 6. Work Decomposition (5 workstreams)

Each workstream is separable across sessions because it hands the next a defined **interface artifact**. W1 and W2 (user, in GPT/waifu2x) can run in parallel with the agent preparing W3 scripts. W2↔W3 is a small loop: cutting can reveal a need for more references.

| # | Workstream | Tool | Owner | Interface artifact (output) |
|---|---|---|---|---|
| **W1** | Base lock + upscale | GPT / waifu2x | User | `assets/lotte_base.png` (locked, hi-res) + lock rationale in `BASE.md` |
| **W2** | Generative source pack | ChatGPT (GPT-image-2) | User | `gen/*` (forehead, cheek/jaw, eyes-closed, smiling-eyes, closed-mouth) + `gen/PROMPTS.md` |
| **W3** | Part separation (layering) | Claude Code scripts (segmentation/compositing) + user review | Agent scripts; user reviews | `layers/*.png` (per-part, alpha, inpainted) + layered PSD for Cubism |
| **W4** | Cubism rig | Cubism 5 FREE | User (agent guides) | `model/lotte.model3.json` (+ `.moc3`, textures, `physics3.json`) |
| **W5** | Integrate + verify | Claude Code | Agent; user verifies | swapped plumbing + verification screenshots |

---

## 7. Repository Layout & Artifact Storage

Phase 1 artifacts live under a new `live2d/` directory, **outside the theme build pipeline** (not in `src/`, not listed in `theme.manifest.yaml`), so they are never concatenated into the generated theme. Work continues on the `live2d-spike` branch/worktree (the Live2D initiative's worktree), alongside the Phase 0 `experiments/live2d-spike/` artifacts.

```
live2d/
  PIPELINE.md          # master tracker: 5 workstreams, status, interfaces, "current state / next action"
  DECISIONS.md         # locked decisions (section 2 of this spec)
  BASE.md              # which raster, upscale factor, why
  assets/lotte_base.png
  gen/                 # GPT-image-2 outputs
    PROMPTS.md         # bridge prompts + which output came from which (reproducibility)
  layers/              # per-part PNGs (agent-produced)
  lotte.psd            # layered file for Cubism import (or a layer manifest)
  model/               # Cubism export: moc3, textures, model3.json, physics3.json
  RIG_GUIDE.md         # Tier-1 Cubism walkthrough, grows as we learn
  *.png                # verification screenshots committed per gate
```

Large binaries (`.psd`, `.moc3`, model textures, raw model dirs) are git-ignored by default like the Phase 0 spike; committed evidence is the per-gate screenshots and the text docs. (Final decision on committing the model binaries is taken at W4/W5.)

---

## 8. Context / Documentation Spine

Multi-session, three-tool (ChatGPT, Cubism Editor, Claude Code) work needs durable in-repo state, per the project's "MD files are the basis of work; handoffs are low-trust" model.

- **`PIPELINE.md`** — single source of truth for progress. Every new session reads this **first** to know exactly where the work stands and what the next action is.
- **`DECISIONS.md`** — the locked decisions, to prevent re-litigation.
- **`gen/PROMPTS.md`** — the bridge prompts and their outputs, for reproducible regeneration.
- **`RIG_GUIDE.md`** — the Cubism Tier-1 walkthrough, written as the user learns ("building while learning").
- **claude-mem / MEMORY.md** — cross-session observations and feedback.
- **Per-gate screenshots** committed as evidence (verification-before-completion).

---

## 9. Session Model

One bounded workstream (or sub-step) per focused session. A session ends by producing its verification artifact and updating `PIPELINE.md`; the next session resumes from `PIPELINE.md`. Avoid a single mega-session (context exhaustion). This matches the user's "small change + user-verification loop" method for external-platform interaction.

---

## 10. Skill-Learning Plan

- **GPT-image-2 editing (W1/W2)** — a prompt cookbook in `gen/PROMPTS.md`: exact edit prompts for each hidden-state asset, refined against results.
- **Layering (W3)** — mostly agent-scripted; the user only reviews candidate part PNGs. Minimal new skill for the user.
- **Cubism rigging (W4)** — the one substantive new skill. `RIG_GUIDE.md` gives a Tier-1-only walkthrough (install Cubism 5 FREE → import PSD → auto-mesh + cleanup → set the Tier-1 parameter set → physics → export), anchored to official tutorials with Lotte-specific steps and the *why* of each deformer.

---

## 11. Execution-Time Checks (verify-and-decide, not placeholders)

1. **W1 — base pixel source.** Compare `version` vs `original` for facial resolution; lock one. Record in `BASE.md`.
2. **W3 — segmentation tool availability.** Before relying on scripted segmentation, run the chosen tool (e.g. rembg / SAM / OpenCV GrabCut) live on the locked base and confirm it works in this WSL environment; record the fallback (manual mask assist) if it does not. (Per the user's "verify tool availability before prescribing it" rule.)
3. **Smile derivation.** Attempt to derive the smile mouth from the closed-mouth art + `ParamMouthForm` before generating a dedicated smile-mouth reference.

---

## 12. Success Criteria

- A `model/lotte.model3.json` loads in the Phase 0 plumbing (standalone SwiftShader page first, then the real Discord console probe).
- The character blinks and breathes, hair and ribbon sway, the gaze follows the cursor, and an occasional eye-contact smile fires — all Tier-1 gentle.
- The result preserves the flat 2D illustration look (flat-rig discipline; no pseudo-3D head turn).
- `master` is untouched; work lives on the `live2d-spike` branch; `live2d/` is outside the theme build pipeline.
- `PIPELINE.md` reflects final state; per-gate screenshots are committed as evidence.
