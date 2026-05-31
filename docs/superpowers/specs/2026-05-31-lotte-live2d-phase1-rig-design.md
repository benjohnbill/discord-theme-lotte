# Lotte Live2D — Phase 1 (Rig the Real Lotte) Design

> Status: validated in the 2026-05-31 brainstorm; **revised 2026-05-31 after an independent Codex design review** (gstack-codex consult) — accepted findings folded in. Pending user review before the implementation plan (writing-plans).
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

3. **Base image is locked, not regenerated.** The source illustrations were produced by iterative revision, so a single prompt cannot reproduce the base. Phase 1 **locks** the base now (it does not re-decide it in W1): rig the **character from `Lotte discord original.png`** (1254×1254 — more facial pixels; it is the parent that `version` was outpainted from, so their faces are pixel-aligned), and take the **ambient background from `Lotte discord version.png`** (the live Discord look). W1 only *confirms and measures* this and records the checksum. Upscale the locked character source with waifu2x (×2, atlas 4096) before separation. See `live2d/BASE.md`.

4. **Cubism 5 FREE (`.moc3`).** Free tier is sufficient for a Tier-1 bust. Runtime change from Phase 0: swap the Cubism **2** core (`dylanNew` mirror) for the **official Cubism 4 core** (`live2dcubismcore.js`); PIXI v6 + `pixi-live2d-display` otherwise unchanged. **This swap is verified up front in Phase 1.0, not assumed** (see §6 and §12).

5. **Background is OUT of the model.** The Cubism model is **character-only with a transparent background**. Each surface supplies its own background (the Discord theme CSS background for now). This matches Phase 0 (`backgroundAlpha: 0`), keeps the rig portable across surfaces, and avoids rigging individual petals. Particle drift is an optional code-side enhancement, deferred.

6. **Flat-rig discipline (aesthetic guardrail).** The "3D / VTuber" feel of a Live2D model comes almost entirely from *pseudo-3D head-turn depth* (cheek compression, nose parallax on `ParamAngleX/Y`), which is a rigging choice — not a requirement of reactivity. To preserve the flat 2D illustration look:
   - Put reactivity on **flat channels**: eye gaze (`ParamEyeBallX/Y`), blink, breath, head **tilt** (`ParamAngleZ`), hair/ribbon physics, smile.
   - **Eye gaze does the recognition; head tilt does the charm.** These carry "she's looking at me."
   - Keep head **turn** (`ParamAngleX/Y`) tiny, and rig it as **planar offset + a small rotation + hair/body lag only**. Do **not** build cheek / nose / mouth parallax in Phase 1. (This is the easiest place for a first-time rigger to accidentally introduce the 3D feel — the guardrail is explicit for that reason.)
   - Keep all deformations gentle; visible warping is what reads as rubbery/3D.
   - Accepted trade-off: no large head rotations (Tier-1 restraint did not want them anyway).
   - Rigging deforms the existing pixels; it does not repaint. Lotte keeps her art style.

7. **Tier-1 restraint.** Most of the life comes for free from runtime auto-blink + auto-breath and from hair/ribbon physics. The only cursor-reactive motion is a **small, damped** gaze + slight head, plus an **occasional** eye-contact smile. Start under-animated; add only if it feels dead.

8. **Source-of-truth durability.** The locked base raster is the irreplaceable source asset (it cannot be regenerated). It **must** be committed to the repo, or stored in a declared location with a recorded checksum, before any downstream work. The pipeline is not resumable across sessions/machines if the base lives only on the user's disk. (Detail in §8.)

---

## 3. Reactive Behavior (Tier 1)

| Source | Behavior | Driver |
|---|---|---|
| Runtime auto | Blink | `pixi-live2d-display` auto-blink |
| Runtime auto | Breath (subtle shoulder/chest rise) | auto-breath sine |
| Physics | Back hair (L/R), side hair (L/R), bangs, ribbon sway | Cubism Physics, derived from head/body angle |
| Cursor-reactive | Iris gaze — the primary "notices me" signal | `model.focus(cursorX, cursorY)` → `ParamEyeBallX/Y` |
| Cursor-reactive | Gentle, **damped** head tilt + minimal flat turn + body lean | `ParamAngleZ` (tilt), small flat `ParamAngleX/Y`, `ParamBodyAngleX` |
| Occasional | Eye-contact + pretty smile, then relax | coded behavior (W5), see §3.1 |

**Restraint controls:** the eye-contact-smile frequency and all damping start conservative. A constant smile reads as animatronic.

### 3.1 Eye-contact smile — behavior state machine (W5)

This behavior is core to the "presence" goal, so it is specified here rather than left as "some code." A small state machine, all timings randomized within bounds and starting conservative:

```
idle ──(trigger)──> glance/follow ──> soft eye-contact ──> smile-hold ──> relax ──> idle
```

- **idle** — auto-blink/breath + physics; gaze drifts subtly.
- **trigger** — any of: cursor enters a face-proximity radius; the Discord window regains focus; or a long randomized timer fires.
- **glance/follow** — damped gaze tracks the cursor (`ParamEyeBallX/Y`), tiny tilt toward it (`ParamAngleZ`).
- **soft eye-contact** — gaze settles on the cursor and holds briefly.
- **smile-hold** — `ParamMouthForm` + `ParamEyeForm` ramp up gently and hold (~1–2 s).
- **relax** — ramp back to idle.

**Tunables (start conservative, expose for tuning):** trigger interval range, cursor-distance threshold, ramp/damping time constants, smile-hold duration, and a **cooldown** so an eye-contact-smile stays rare. These move to the W5 plan with concrete starting values.

---

## 4. Layer Map (character-only, ~20–23 parts)

Depth-ordered, back to front. Counts are a starting target; the final split is settled during the Phase 1.0 pilot and W4 (rigging reveals real deformation needs).

| Depth | Part | Count | Rig purpose / source note |
|---|---|---|---|
| back | Back hair L / R | 2 | independent sway |
| | Body + sailor uniform (collar included) | 1 | breath, body lean |
| | Scarf knot (neckerchief) | 1 | sway with body |
| | Neck | 1 | — |
| | **Face base** (skin, cheeks, ears, forehead) | 1 | needs forehead (under bangs) and cheek/jaw (under side hair) reconstructed |
| | Eyebrows L / R | 2 | subtle expression |
| | Eye whites (sclera) L / R | 2 | container for irises; needs clipping mask |
| | Irises / pupils L / R | 2 | **gaze** (cursor tracking); clipped to sclera |
| | Upper eyelids + lashes L / R | 2 | **blink**; needs eyes-closed skin |
| | Lower eyelids L / R | 2 | promoted for the **eye-smile** (lid rises) |
| | Mouth — outer + inner (lip line, cavity/teeth) | 2 | open↔closed + smile form |
| front | Side hair L / R | 2 | sway, frames the face |
| | Bangs (front hair) | 1–2 | sway, occludes forehead |
| | Ribbon / bow | 1 | physics sway |

### Rigging principles (carry into W4 / `RIG_GUIDE.md`)

These are design constraints; exact mesh-density and texture-atlas numbers live in the writing-plans output, not here.

- **Art must extend beyond the visible area.** Face base under bangs/side hair, hair roots, and body edges must be painted larger than what shows, or deformation reveals holes at the edges.
- **Mouth interior is its own thing.** The open mouth already shows interior; the closed mouth needs a lip line. Keep outer mouth and inner cavity separable so open↔closed morphs cleanly.
- **Eyes need clipping masks** (sclera clips the iris; lids ride above).
- **Deformer hierarchy** (root → body → head → face → eyes/mouth → hair/ribbon) is defined in W4, not auto-flat.
- **MVP rig vs stretch rig.** Define a minimum-viable part set (what Phase 1.0 proves) and a stretch set (added only if the MVP feels under-alive). If separation quality is poor, **merging parts and shipping a simpler rig is an allowed outcome**, not a failure.

---

## 5. Rig Parameter Set

| Parameter | Effect | Driven by | Tier 1 |
|---|---|---|---|
| `ParamEyeLOpen` / `ParamEyeROpen` | blink | runtime auto-blink | core |
| `ParamBreath` | breathing | runtime auto-breath | core |
| Physics (hair, ribbon) | secondary sway | derived from angle/body params | core |
| `ParamEyeBallX` / `ParamEyeBallY` | iris gaze | `model.focus(cursor)` | core |
| `ParamEyeForm` | eye-smile crease | occasional smile behavior | adopted |
| `ParamAngleZ` | head tilt | idle + gaze liveliness | core (flat) |
| `ParamAngleX` / `ParamAngleY` | head turn — **flat: planar offset + tiny rotation + lag only** | small, damped | restrained |
| `ParamBodyAngleX` | body lean | idle + slight follow | subtle |
| `ParamMouthOpenY` / `ParamMouthForm` | mouth open + smile form | occasional smile; otherwise near-static open smile | adopted |
| brow / other expression params | — | — | deferred |

Concrete restrained **value ranges** (not just names) and the deformer hierarchy are authored in W4 and recorded in `RIG_GUIDE.md`.

---

## 6. Phase 1.0 — Vertical-Slice Pilot (gate before the full pipeline)

Phase 0 proved the Discord *runtime*. It did **not** prove the *art → rig → runtime* chain, which is the real risk of Phase 1. Before generating the full source pack or writing the full rig guide, run a one-session "ugly vertical slice" that exercises the entire hardest chain end to end. This is the feasibility gate for Phase 1.

**Steps:**

0. **Runtime pre-flight.** Load a stock/dummy **Cubism 4** `.model3.json` (a free Cubism sample) in the Phase 0 standalone page using `pixi-live2d-display` + the **official Cubism 4 core**, and confirm it renders and `focus()` tracks. This verifies the core swap (decision §2.4) before any Lotte rigging.
1. **Temp base** — a cropped face region of the locked raster (not the full bust).
2. **One generated reference** — a single GPT-image-2 edit (e.g. eyes-closed or forehead-revealed) to test hidden-pixel harvesting.
3. **Minimal layers (agent-scripted)** — face base + one eye (sclera + iris) + one upper eyelid + mouth (open + closed) + one hair piece (~6 parts).
4. **Cubism** — import, auto-mesh + minimal cleanup, rig blink + gaze + a tiny smile (mouth form + eye form) + one hair physics chain. Export a Cubism 4 model.
5. **Runtime** — load that crude model in the Phase 0 standalone runtime (SwiftShader) and confirm blink / gaze / smile / sway.

**Gate.** If the chain works and looks acceptable → proceed to the full W1–W5. If layer or deformation quality is poor → decide between a simpler rig, fewer parts, or an art-pipeline rethink **before** investing days in the full source pack. This is where the "does AI-assisted layering actually produce a riggable asset" question gets answered cheaply.

---

## 7. Work Decomposition (workstreams)

Phase 1.0 (above) runs first. The full build then proceeds through five workstreams. **Honest dependency model (corrected after review):** the claimed parallelism is limited. W1 (base lock) and the W5 plumbing prep can run in parallel up front, but **W2 → W3 → W4 form an iterative core, not cleanly parallel stages**, because:

- W2's reference set cannot be fully specified until W3's cutting exposes which pixels are missing.
- W3's part boundaries cannot be finalized until W4 rigging reveals deformation needs.
- W4 parameter choices feed back into W3 (more/larger parts) and W5 behavior feeds back into W4.

So treat W2/W3/W4 as a loop that converges, seeded by the Phase 1.0 pilot. **W3 is the load-bearing workstream** — if layer separation is bad, rigging becomes cleanup hell; everything downstream depends on it.

| # | Workstream | Tool | Owner | Interface artifact (output) |
|---|---|---|---|---|
| **W1** | Base lock + upscale | GPT / waifu2x | User | `assets/lotte_base.png` (locked, hi-res, **committed/checksummed**) + lock rationale in `BASE.md` |
| **W2** | Generative source pack | ChatGPT (GPT-image-2) | User | accepted hidden-state **patches + masks** (not raw gens) + `gen/PROMPTS.md` audit log |
| **W3** | Part separation (layering) | Claude Code scripts (segmentation/compositing) + user review | Agent scripts; user reviews | `layers/*.png` (per-part, alpha, inpainted) + layered PSD for Cubism |
| **W4** | Cubism rig | Cubism 5 FREE | User (agent guides) | `model/lotte.model3.json` (+ `.moc3`, textures, `physics3.json`) |
| **W5** | Integrate + verify | Claude Code | Agent; user verifies | swapped plumbing + checkpoint screenshots |

### W2 — defending against GPT-image-2 edit drift

Bridge edits drift even on the locked base (lighting, line weight, color temperature, scale, registration, hair-edge alpha, face geometry). Composited naively, that produces visible seams, foreign-looking patches, halos, and misaligned eye/mouth extremes. Defenses (required, not optional):

- **Harvest only hidden / interior pixels** from a generated reference — never swap in a full visible region.
- **Landmark-align** each reference back to the locked base before harvesting.
- **Color/histogram-match** harvested pixels to the surrounding base pixels.
- Keep masks **conservative**, feather only where appropriate.
- **Reject gate:** a patch is usable only if it composites invisibly at 100% opacity *and* survives the blink / mouth-open deformation test.
- Store **accepted patches + their masks**, not raw generated images. `gen/PROMPTS.md` is an **audit log**, not a reproducibility guarantee (the base cannot be regenerated; edits are stochastic).

### W3 — segmentation, and the fallback that respects the no-hand-paint constraint

Auto-segmentation (rembg / SAM / GrabCut) will isolate a character but will **not** reliably produce clean production Live2D parts for anime hair, lashes, translucent edges, ribbon overlap, mouth interiors, or eyelids. The fallback must stay within the user's constraint (no manual painting/cutting):

1. Agent generates rough masks (SAM / GrabCut / rembg) and **mask candidates + compositing previews**.
2. User only **chooses among previews** or marks **coarse keep/remove** regions — no pixel painting.
3. Agent **refines** via scripted CV: grow/shrink, feather, edge matting, symmetry cloning, patch inpainting.
4. **Allowed escape:** merge parts to reduce cut complexity, or drop to a simpler rig, if separation quality is insufficient. The success path must not silently depend on auto-seg delivering clean per-part alpha.

---

## 8. Repository Layout & Artifact Storage

Phase 1 artifacts live under a new `live2d/` directory, **outside the theme build pipeline** (not in `src/`, not listed in `theme.manifest.yaml`), so they are never concatenated into the generated theme. Work continues on the `live2d-spike` branch/worktree (the Live2D initiative's worktree), alongside the Phase 0 `experiments/live2d-spike/` artifacts.

```
live2d/
  PIPELINE.md          # master tracker (authority): workstreams, status, interfaces, "current state / next action"
  DECISIONS.md         # locked decisions (§2)
  BASE.md              # which raster, upscale factor, checksum, why
  assets/lotte_base.png   # locked source-of-truth raster — COMMITTED (or checksummed if stored elsewhere)
  gen/
    PROMPTS.md         # audit log of bridge prompts + which output came from which
    patches/           # accepted hidden-state patches + masks (not raw gens)
  layers/              # per-part PNGs (agent-produced) + layer manifest
  lotte.psd            # layered file for Cubism import
  model/               # Cubism export: moc3, textures, model3.json, physics3.json
  RIG_GUIDE.md         # Tier-1 Cubism walkthrough, grows as we learn
  checkpoints/
    YYYY-MM-DD-<gate>/ # one screenshot + short RESULT.md per gate (keeps evidence out of the tree root)
```

**Artifact / binary policy (explicit — required for resumability):**
- The **locked base raster** is source-of-truth: **commit it**, or store it in a declared location and record its **checksum** in `BASE.md`. Not optional.
- The **layer manifest** and accepted **patches + masks** are committed (they are reconstruction inputs).
- Large derived binaries (`.psd`, `.moc3`, model textures) may be git-ignored, but their **checksums are recorded** so a session knows whether its local copy matches. The PSD-vs-generated boundary is recorded in `PIPELINE.md`.

---

## 9. Context / Documentation Spine

Multi-session, three-tool (ChatGPT, Cubism Editor, Claude Code) work needs durable in-repo state, per the project's "MD files are the basis of work; handoffs are low-trust" model.

- **`PIPELINE.md`** — single source of truth for progress and the **authority** for pipeline state. Every new session reads this **first**.
- **`DECISIONS.md`** — the locked decisions, to prevent re-litigation.
- **`gen/PROMPTS.md`** — audit log of the bridge prompts and their outputs (not a reproducibility claim).
- **`RIG_GUIDE.md`** — the Cubism Tier-1 walkthrough, written as the user learns.
- **`checkpoints/<gate>/`** — one screenshot + short `RESULT.md` per gate (evidence; verification-before-completion).
- **claude-mem / MEMORY.md** — cross-session **observations** only. It is a secondary memory layer, never the pipeline's state of record (that is `PIPELINE.md`).

---

## 10. Session Model

One bounded workstream (or sub-step) per focused session. A session ends by producing its checkpoint artifact and updating `PIPELINE.md`; the next session resumes from `PIPELINE.md`. Avoid a single mega-session (context exhaustion). This matches the user's "small change + user-verification loop" method for external-platform interaction. The W2/W3/W4 iterative core means some sessions revisit a prior workstream — that is expected, and `PIPELINE.md` records the loop state.

---

## 11. Skill-Learning Plan

- **GPT-image-2 editing (W1/W2)** — a prompt cookbook in `gen/PROMPTS.md`: exact edit prompts for each hidden-state asset, refined against results, with the harvest/align/reject discipline from §7.
- **Layering (W3)** — mostly agent-scripted; the user only reviews candidate part PNGs / previews. Minimal new skill for the user.
- **Cubism rigging (W4)** — the one substantive new skill. `RIG_GUIDE.md` gives a Tier-1-only walkthrough (install Cubism 5 FREE → import PSD → auto-mesh + cleanup → set the Tier-1 parameter set with restrained ranges → deformer hierarchy → physics → export), anchored to official tutorials with Lotte-specific steps and the *why* of each deformer. The Phase 1.0 pilot is the first, smallest pass through this.

---

## 12. Execution-Time Checks (verify-and-decide, not placeholders)

1. **Runtime core swap (Phase 1.0 step 0).** Load a dummy Cubism 4 `.model3.json` in the Phase 0 runtime with the official Cubism 4 core before rigging Lotte; confirm it loads and tracks. (Per the user's "verify tool availability before relying on it" rule.)
2. **W1 — confirm the locked base.** The base is locked (character = `original`, background = `version`; §2.3). W1 measures `original`'s facial resolution to confirm it beats `version`, then records source + checksum in `BASE.md`. (Not a re-decision.)
3. **W3 — segmentation tool availability.** Run the chosen tool (rembg / SAM / GrabCut) live on the locked base; confirm it works in this WSL environment; record the fallback ladder (§7) if it underperforms.
4. **Smile derivation.** Attempt to derive the smile mouth from the closed-mouth art + `ParamMouthForm` before generating a dedicated smile-mouth reference.

---

## 13. Success Criteria

- **Phase 1.0 gate passes:** the dummy Cubism 4 model loads in the Phase 0 runtime, and the ~6-part face slice blinks / gazes / smiles / sways end to end.
- A `model/lotte.model3.json` loads in the Phase 0 plumbing (standalone SwiftShader page first, then the real Discord console probe).
- The character blinks and breathes, hair and ribbon sway, the gaze follows the cursor, and an occasional eye-contact smile fires — all Tier-1 gentle.
- The result preserves the flat 2D illustration look (flat-rig discipline; no pseudo-3D head turn).
- `master` is untouched; work lives on the `live2d-spike` branch; `live2d/` is outside the theme build pipeline; the locked base raster is committed or checksummed.
- `PIPELINE.md` reflects final state; per-gate checkpoints are committed as evidence.
