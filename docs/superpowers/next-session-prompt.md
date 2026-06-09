# Next Session — Lotte Live2D — launcher (thin pointer)

> This launcher is intentionally **thin**: it points, it does not restate the frontier. The live state has a
> single home (`live2d/PIPELINE.md`) — duplicating it here is exactly the drift the doc restructure (ADR-0003)
> removed. Paste the block below to start a session.

---

## Task

Continue the Lotte Live2D rig. **Read `live2d/PIPELINE.md` first** — it is the authority for *where we are /
what's the single next action*. The active investigation is `docs/features/cd4-blink/` (blink under the
통짜 pivot, ADR-0001; it is the sole remaining blocker — gaze + breath already drive live in Discord).

Do **not** infer state from this launcher or from memory — `PIPELINE.md` owns it.

## Read first (in order)

1. `MEMORY.md` auto-loads → orientation pointers (it holds no load-bearing state; PIPELINE does).
2. **`live2d/PIPELINE.md`** — live state authority (dynamic cursor: active feature + single next + done-log).
3. **`docs/features/cd4-blink/INDEX.md`** — the active blink investigation hub → `RESEARCH.md` (the saga,
   open ❓) · `DECISIONS.md`. The 통짜 rig walkthrough is strategy-level:
   **`docs/features/tongjja-rig/RIG_PROCEDURE.md`** (CD-1..9).
4. **`live2d/DOMAIN_MAP.md`** — platform/tool facts (✅/⛔). **`docs/adr/`** — decisions (0001 pivot ·
   0003 doc-arch · 0004 locked rig constraints). **`live2d/CONTEXT.md`** — glossary.
5. As needed (history): `docs/superpowers/specs/`, `docs/superpowers/plans/` (completed — don't re-execute),
   `docs/features/archive/`, `live2d/pilot/RESULT.md`.

## Working directory

`/home/benjohnbill/dev/discord-theme-lotte` on branch **`master`** (the single authority; live2d-spike was
merged in and removed). `master` is **local-only, well ahead of `origin/master`, NOT pushed** — pushing is
Tier-3 (sign-off only; never push/force yourself). There is also one unrelated uncommitted change (a
`src/base/background.css` swap + dist rebuild) that predates this work — leave it to the user.

## Stopping conditions

Stop and report at any user-action task (a Cubism GUI edit, a Discord verify) or any decision that needs the
user (an art/tune call, or pushing `master`).
