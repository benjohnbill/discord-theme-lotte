# cd4-blink — Research Notes

The blink (CD-4) investigation under the rig-strategy pivot (ADR-0001). Learning-narrative home; pairs
with `live2d/DOMAIN_MAP.md` (one-line settled facts). Markers: `❓` guess/unverified · `✅` verified
(verification line attached) · `⛔` ruled out.

> **Premise (2026-06-09): the current blink state must be RE-TESTED cleanly after the doc restructure.**
> The strongest finding here is that *stale docs contaminated the human verification loop* (§3) — so no
> claim below about "where blink stands" is asserted as settled. The root cause is still `❓`.

---

## §1. The patchwork failure mode and the opacity-swap mechanism

### ✅ 1.1 The flat source has no under-drawing → blink must be a frame-swap, not a deform

The base is a flat (un-layered) AI illustration: no skin under an eyelid, no socket behind an eye. So
runtime mesh-deform of cut face parts slides/doubles ("누더기" — `CONTEXT.md`). Blink is therefore a
**frame-swap** (opacity-swap) of a baked closed-eye state, not a geometry deform.

[검증: 2026-06-01 / 방법: first live Discord render of the W4 mesh-deform rig / 출처: ADR-0001]

### ✅ 1.2 Swap bands must be FULL-SILHOUETTE, not feathered rectangles

A feathered **rectangle** band's bottom edge (over the mouth/face interior) renders as a horizontal
**premultiplied-alpha dark line** that scales with opacity. A **full-silhouette** band (alpha = the whole
character silhouette; content = base + the one feature in a tight mask) has no face-interior edge, so no
line. Dead-ends that chased band *skin* (all irrelevant): extend-rect → gray patch → tight-island-mask →
base-fill-rect.

[검증: 2026-06-02 / 방법: exported-model render + delta-diff / 출처: PIPELINE 06-02 PM record]
→ **graduated to `DOMAIN_MAP` (premultiplied-alpha edge fact — applies to any opacity-swap band).**

### ✅ 1.3 Verify the EXPORTED runtime model, and reimport via "Replace"

PIL straight-alpha layer composites **cannot** reproduce premultiplied-alpha edge darkening — verify the
exported model. PSD reimport = **"Replace [lotte.psd]"** (keeps the rig); **"Add all layers as new
ArtMesh"** triplicated every part and destroyed the warp rig (a model-corruption saga, recovered from a
`.cmo3` that still held the warps; compounded by a second 'lotte' tab being watched). After Replace,
re-mesh each band to full silhouette.

[검증: 2026-06-02 / 방법: model-corruption recovery / 출처: PIPELINE 06-02 PM record; memory `live2d-cubism-rig-gotchas` §3]
→ **graduated to `DOMAIN_MAP` (machine-ops: Replace-not-Add, re-mesh on Enter, verify-exported).**

---

## §2. The CD-4 blink warp/distortion wall — the live blocker

### ❓ 2.1 Both band variants fail; root cause pixi-vs-model UNCONFIRMED

The 06-02 PM plan ("~90%, just re-rig + export") was executed 06-03 (~10 more rounds) and **failed**. Both
swap-band variants fail when the blink opacity drives:
- the earlier **island-to-string** band → visible artifacts;
- the **full-silhouette** band (the landing mechanism) → **warp / distortion on the eyelids**.

**Root cause UNCONFIRMED — the fork that decides the fix:**
- **pixi-live2d-display@0.4.0 runtime bug** ⇒ it renders **clean inside Cubism** ⇒ fixable in FREE tier by
  a library version bump / replacement; **or**
- **inherent model/mesh problem** ⇒ it **warps in Cubism itself** ⇒ needs a model re-bind, or Cubism PRO's
  **mesh-copy** (which FREE lacks — the toolchain bottleneck found 06-03).

Everything else already drives live in real Discord: head-lean gaze (Phase A) + breath. **Blink is the SOLE
remaining blocker**, not a foundational render issue.

검증 계획 (the localization test — USER decision 2026-06-06): in Cubism, set the full-silhouette band to
**opacity 100 at Angle 0** and look. Clean there ⇒ warp is pixi-specific → pursue a library update (verify
a bump in the SwiftShader harness). Warps there ⇒ it's the model/mesh → re-bind or PRO mesh-copy. The
verify recipe is `live2d/cd_render.html` + `tools/cd_capture.py` / `tools/blink_render.py`
(`?eyes=` ramp + `?still`) over `gen/scene-plate.png`.

### ❓ 2.2 Cubism-clean / runtime-patchwork (06-07) — not yet trustworthy

A later read (06-07) suggested the warp was **gone on the Cubism screen** (`pilot/lotte-good.cmo3`) while
the runtime render (SwiftShader + the USER's localhost) was **still patchwork** — which would point at
pixi/runtime. **But** (a) whether the runtime was rendering the *latest* export is uncertain (obs 2840:
rt vs rt4 render identically), and (b) the 06-06 localization test was itself run under stale docs that
contaminated the verify loop (§3). ⇒ Treat this as **unconfirmed**; the clean re-test resolves it.

### ❓ 2.3 The lipsyncpatch fork as a runtime swap

The `pixi-live2d-display-lipsyncpatch` fork (v0.5.0-ls-8) was tried 06-07 as a one-off diagnostic
(rt6 model rendered under it; obs 2788). The runtime is nominally `@0.4.0`. Whether a fork/bump is the fix
is exactly what 2.1's localization test routes to — re-test decides.

---

## §3. The verification-loop lesson (why the restructure comes first)

### ✅ 3.1 Stale docs contaminated the human verification loop

Across the ~10 blink rounds, stale/contradictory orientation docs (the PIPELINE fossil stack + the
quadruple-copied frontier) misled not just the agent but the **USER's own read of self-test results** —
the loop reached the point where a test outcome could not be trusted. This is the **load-bearing
justification** for the doc restructure (ADR-0003): a contaminated verify loop cannot resolve 2.1.

[검증: 2026-06-07 / 방법: USER observation across the blink saga / 출처: design plan E-1; obs 2882]

**Consequence:** the standing decision (see `DECISIONS.md`) is to run the localization re-test **cleanly,
after** the restructure — not to carry forward any pre-restructure verdict.

---

## DOMAIN_MAP promotion log (graduated from this feature)

- ✅ premultiplied-alpha edge → full-silhouette bands *(§1.2)*
- ✅ Replace-not-Add reimport · re-mesh on Enter · verify-exported-not-PIL *(§1.3)*
- ⛔ Cubism PRO mesh-copy unavailable in FREE *(§2.1 — relevant to the fix fork)*
