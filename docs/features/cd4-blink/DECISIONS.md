# cd4-blink — Decisions

Feature-scoped decision log (too small for an ADR). Decisions that generalize past this feature graduate to
an ADR or `DOMAIN_MAP` on retrospect (propose to USER).

---

## 결정 로그

### 2026-06-09: Re-test the blink state cleanly AFTER the doc restructure

**컨텍스트:** stale/contradictory orientation docs contaminated the USER's own verification loop across the
~10 blink rounds — self-test results could no longer be trusted (`RESEARCH.md` §3.1).
**옵션:** (a) carry forward the pre-restructure verdict (Cubism-clean / runtime-patchwork); (b) re-run the
localization test cleanly after the restructure.
**결정:** (b). No pre-restructure claim about where blink stands is treated as settled; the root cause
stays `❓` until the clean re-test.
**근거:** a contaminated verify loop cannot resolve the pixi-vs-model fork; un-contaminating it is the
primary purpose of the restructure (ADR-0003).
**영향 범위:** this feature (gates the next blink action), but the lesson is general (→ ADR-0003).

### 2026-06-06: Run the localization test FIRST (before any more blink dev)

**컨텍스트:** after ~10 rounds both band variants warp; root cause UNCONFIRMED (pixi vs model).
**옵션:** 1 = run one definitive localization test (full-silhouette band at opacity 100 / Angle 0 in
Cubism); 2 = defer blink, ship gaze+breath as sufficient; 3 = a Cubism PRO free-trial mesh-copy cleanup.
**결정:** option 1 first. It routes the fix deterministically — clean in Cubism ⇒ pixi (library bump);
warps in Cubism ⇒ model (re-bind / PRO mesh-copy). Option 2 = the fallback if the test is discouraging;
option 3 = only if localized to the model.
**근거:** cheapest move that disambiguates the fork; measurement gates commitment.
**영향 범위:** this feature.

### 2026-06-02: Bands are full-silhouette base-filled frame-swaps (not feathered rectangles)

**컨텍스트:** a feathered rectangle band's bottom edge rendered as a premultiplied-alpha dark line.
**옵션:** feathered rectangle band vs full-silhouette band (alpha = whole silhouette, content = base + one
feature in a tight mask).
**결정:** full-silhouette bands.
**근거:** the silhouette edge is the base's own outline — no face-interior edge → no dark line.
**영향 범위:** generalized → `DOMAIN_MAP` (the premultiplied-alpha edge fact applies to any opacity-swap band).

### 2026-06-02: 2-state blink first; both eyes together

**컨텍스트:** one `eyeband_closed` band covers both eyes.
**결정:** 2-state (open↔closed) first, both eyes blink together.
**근거:** an independent wink would need the band split L/R = a PSD re-cut, out of scope now. 3-state stays
an open question decided on-screen.
**영향 범위:** this feature.
