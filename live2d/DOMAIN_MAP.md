# Lotte Live2D — Domain Map (platform & tool facts)

Durable facts about how the **platform and toolchain always behave** — phase-independent,
stable across the gate. The dictionary a fresh agent reads to avoid re-deriving a settled
truth. Read with `CONTEXT.md` (what the words *mean*) and `docs/adr/` (why a *decision* was made).

**Marker rule — this file holds only `✅` (settled true) and `⛔` (settled false / forbidden).
No `❓`.** Open questions live in `docs/features/<slug>/RESEARCH.md` (the single home of `❓`);
when one resolves it graduates here as a one-line `✅`/`⛔` (back-link to the RESEARCH section).
A frequently-read dictionary advertises no unsettled content, so its stale surface ≈ 0.

**Source of truth = the model files.** As-built rig facts (the deformer tree, which params
drive what, atlas contents) are owned by `live2d/pilot/lotte-good.cmo3` and the exported
`*.model3.json` / `*.moc3`. This map states *platform rules*, not the as-built model — it
never duplicates what the artifact already encodes.

---

## Runtime (load + render)

- ✅ The Lotte rig runs on **Cubism 4**: official `live2dcubismcore.min.js` + `pixi.js@6.5.10`
  + `pixi-live2d-display@0.4.0/dist/cubism4.min.js`. *(was INV-1)*
- ⛔ `cubism2.min.js` / the `dylanNew` core **for the rig** — those were Phase 0's *Shizuku
  sample* only, never the Lotte rig. *(was INV-1)*
- ✅ Export **moc3 version ≤ 5** (`.moc3 file version` 5.0, or 4.2). The pinned web Core
  reports `csmGetLatestMocVersion()=5`. *(was INV-6)*
- ⛔ **moc3 v6** (Cubism Editor 5.3's default) — it **fails to load**
  (`csmReviveMocInPlace … unsupport later than moc3 ver`). Fix: export 5.0/4.2, **or** bump the
  Core / use the `pixi-live2d-display-lipsyncpatch` fork. *(was INV-6)*
- ⛔ A runtime hack that hides/toggles a single band's drawable opacity — **pixi-live2d-display
  caches drawable opacity**, so `setPartOpacityById`, a `getDrawableOpacities` getter patch, and
  a `coreModel.update` wrap all fail. Open the eyes by **driving the keyed param** (wire blink),
  not by hiding a band. *(memory `live2d-cubism-rig-gotchas`)*

## Render verification (no headless WebGL)

- ⛔ WebGL on the persistent **bh-chrome** service — it has none; any 3D/Live2D render check
  must use a **SwiftShader throwaway Chrome** or the real Discord client. *(memory `bh-chrome-no-webgl`)*
- ✅ SwiftShader CDP recipe: **no `--virtual-time-budget`** (it freezes `performance.now`, so a
  PIXI rAF loop never paints), `--remote-allow-origins=*`, and `preserveDrawingBuffer: true` +
  an explicit render (SwiftShader needs real frames). Afterward kill the chrome **main proc by
  PID** — `pgrep -f` self-matches its own pipeline. *(memory gotchas; hookify `warn-pgrep-kill-selfmatch`)*

## Cubism FREE constraints

- ✅ Texture atlas = a **single 2048×2048**, ≤100 pieces. Pack parts via **Edit Texture Atlas →
  Auto Layout → "Set magnification automatically"** (scales parts down on layout). *(was INV-7)*
- ⛔ **4096 atlas** or **multiple atlases** — PRO-only. *(was INV-7)*
- ✅ **Max 2 params per deformer object** → rig **one param per deformer** (Angle X / Y / Z each
  on its own warp). This *also* removes the **2D-keyform diagonal corner-blend distortion**: two
  params on one deformer blend the diagonal corners, and the head-lean gaze drives X+Y+Z
  diagonally every frame. *(memory gotchas; PIPELINE W4 / Phase C+D)*
- ⛔ Cubism **PRO mesh-copy** — FREE lacks it (bears on the blink-warp fix fork). *(memory gotchas §3)*
- ✅ Eye-smile uses the template's standard **`EyeL Smile` / `EyeR Smile`**. *(was INV-8)*
- ⛔ **`ParamEyeForm`** — there is no such standard param (only `ParamEyeBallForm`, which is
  eyeball *scaling*, not an eye-smile). *(was INV-8)*

## Cubism machine-ops (strategy-invariant editor procedure)

- ✅ A PSD update is **"Replace [lotte.psd]"** — it keeps meshes / deformers / keyforms. *(memory gotchas §3)*
- ⛔ **"Add all layers as new ArtMesh"** on reimport — it **triplicates every part and destroys
  the warp rig** (parts fall to `[Root]`). Recover from a `.cmo3` that still holds the warps. *(memory gotchas §3)*
- ✅ After a texture **shape** change, re-mesh: Automatic Mesh generator (**Ctrl+Shift+A**) → click
  a Setting number field → **Enter**. There is **no OK button** — the mesh applies on Enter. *(memory gotchas §3)*
- ✅ Verify the **exported runtime model**, never a PIL layer composite — straight-alpha composites
  cannot reproduce **premultiplied-alpha edge darkening**. *(memory gotchas §3)*
- ✅ An opacity-swap band's edge over a face interior renders as a **premultiplied-alpha dark line
  that scales with opacity**; a **full-silhouette band** (the base's own outline, no face-interior
  edge) avoids it. *(graduated from `cd4-blink` — applies to any opacity-swap band)*

## Base raster & source lineage

- ✅ Rig the character from **`lotte-discord-original.png`** (1254², the parent — more facial px
  than `version`'s 992). *(was INV-2)*
- ✅ Ambient background from **`lotte-discord-version.png`** (a pixel-aligned side-extension /
  outpaint of `original`). *(was INV-2)*
- ✅ Upscaled rig master = **`live2d/assets/lotte_base.png` (2508²)**, via **PIL Lanczos x2**
  (no neural upscaler in the env — softer; re-upscale if edge crispness ever proves insufficient).
  Checksums in `live2d/source/SHA256SUMS`. *(BASE.md / W1)*
- ✅ The base **cannot be regenerated** (iterative revision, no reproducible prompt) → the four
  source rasters are committed source-of-truth (`live2d/source/`, lineage in `source/README.md`).
- ⛔ Source rasters under **`src/`** — they live in **`live2d/source/`**, never `src/`. *(was INV-2)*

## Displays & fit

- ✅ Target displays: **1920×1200 / 2560×1440 / 2560×1600** — author for the densest (2560×1600).
  One rig serves all three via Phase-0 `fit()`; it is **aspect-agnostic** (character-only,
  transparent background), and the background layer adapts via `background-size: cover`. *(BASE.md)*
