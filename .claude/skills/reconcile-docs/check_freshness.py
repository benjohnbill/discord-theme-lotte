#!/usr/bin/env python3
"""reconcile-docs freshness validator (post-restructure, ADR-0003).

Makes the mechanical half of the reconcile-docs Step-2 "Detect drift" pass
*executable* instead of eyeballed prose, so an execution lapse (the failure
mode that actually bit us: detection worked, write-back was skipped) is caught
by a command rather than by another reminder.

It does NOT replace judgment. It checks only what is enforceable:
  A. INV denylist  — superseded values appearing UN-annotated and non-negated in
                     a LIVE orientation surface.
  B. Frontier      — the "next/frontier" phase token agrees across surfaces
                     (W-stage granularity + pivot Phase A/B/C/D letters).
  C. Branch-state  — commit counts pinned in prose vs `git rev-list`.
  D. DOMAIN_MAP marker rule — `live2d/DOMAIN_MAP.md` must hold only settled
                     ✅/⛔ facts; an `❓` bullet there is a FAIL (open questions
                     belong in docs/features/<slug>/RESEARCH.md). [ADR-0003]
  E. Recency-warn  — the authority's "as-of" date vs the latest claude-mem
                     observation for this project; warns when memory is newer
                     (the 06-06 ↔ 06-07 gap that slipped past a clean run). [ADR-0003]
  F. Dissolved-ref — no LIVE orientation surface (incl. the CLAUDE.md entry doc)
                     may cite a DISSOLVED doc (a tombstone) as if it were live.
                     Tombstones are permanent redirects; a live nav surface must
                     point at the new home. Frozen lineage (specs/plans/ADRs/
                     archive) and the memory layer (separate track) are exempt. [ADR-0003]

Target list: PARSED FROM THE `CLAUDE.md` ENTRY-DOC MAP ("## Orientation docs"
section) — the registry doc (DOC_ARCHITECTURE.md) was dissolved into CLAUDE.md
(map) + DOMAIN_MAP.md (facts) + ADR-0003 (decision) + this checker (the
agreement rules). The new-structure homes are also added explicitly so the
check is robust even before the CLAUDE.md map edit is applied. A path-based
fallback covers a missing/renamed entry doc.

History surfaces (completed plans, FINDINGS, ADRs, docs/features/archive/, any
*-pre-restructure-* snapshot) are EXEMPT from the denylist: they retain old
values under a SUPERSEDED banner. Negated/correct-context mentions are not
violations either.

Usage:  python3 check_freshness.py [--root <worktree-root>]
Exit:   0 = clean (warnings allowed), 1 = hard FAIL. Stdlib only.
"""
from __future__ import annotations
import argparse
import glob
import os
import re
import sqlite3
import subprocess
import sys

MEMORY_DIR = os.path.expanduser(
    "~/.claude/projects/-home-benjohnbill-dev-discord-theme-lotte/memory"
)
ENTRY_REL = "CLAUDE.md"  # the entry-doc map (replaces the dissolved registry)
CLAUDE_MEM_DB = os.path.expanduser("~/.claude-mem/claude-mem.db")
DOMAIN_MAP_REL = "live2d/DOMAIN_MAP.md"

# Surfaces that always belong to the live set, even if the CLAUDE.md map has not
# yet been updated to name them (the new type-homes).
EXPLICIT_REL = [
    "live2d/PIPELINE.md",
    "live2d/DOMAIN_MAP.md",
    "live2d/CONTEXT.md",
    "docs/superpowers/next-session-prompt.md",
]
EXPLICIT_GLOBS = [
    "docs/features/*/*.md",   # active feature folders (archive/ is filtered out as history)
    "docs/adr/*.md",
    "docs/superpowers/specs/*.md",
    "docs/superpowers/plans/*.md",
]

# INV-* denylist: a superseded value that must not appear live + un-annotated.
DENYLIST = [
    ("INV-7", re.compile(r"\b4096\b"), "atlas 4096 (Cubism FREE cap is a single 2048)"),
    ("INV-7", re.compile(r"\b(multi-?atlas|multiple atlases|2 atlases|two atlases)\b", re.I),
     "multi-atlas as a FREE option (multi-atlas is PRO-only)"),
    ("INV-8", re.compile(r"ParamEyeForm"), "ParamEyeForm rig param (use EyeL/R Smile)"),
    ("INV-1", re.compile(r"\b(cubism2|dylanNew)\b"), "cubism2/dylanNew for the rig (rig is Cubism 4)"),
    # INV-5 RESOLVED 2026-06-01: live2d-spike was merged into master and removed; master is the
    # single authority. The OLD split-brain language is now the superseded value.
    ("INV-5", re.compile(r"live2d-spike\s+(?:is|carries|copy is)\b(?![^.]*\bmerged\b)", re.I),
     "live2d-spike as live/authority (it was MERGED into master and removed)"),
    ("INV-5", re.compile(r"(?:worktree is the authority|authority until .* merge|split-brain (?:active|reopened|RE-ACTIVATED))", re.I),
     "worktree-authority / active split-brain (RESOLVED — master is the authority)"),
    ("INV-5", re.compile(r"`?master`?\s+is\s+NOT\s+merged", re.I),
     "'master is NOT merged' (spike WAS merged into master 2026-06-01)"),
    # INV-3 PIVOT 2026-06-01: Phase 1 quality superseded → rig-strategy pivot (ADR-0001) is the frontier.
    ("INV-3", re.compile(r"(?:real|larger|next)\s+arc\s*=?\s*(?:is\s+)?Phase\s*2", re.I),
     "Phase 2 as the next/larger arc (DEFERRED behind the rig-strategy pivot, ADR-0001)"),
]

# Hit line or up to 2 preceding non-blank lines mark it superseded/correct.
ANNOTATED = re.compile(
    r"superseded|⚠️|was wrong|\bstale\b|there is no|no standard|not merged|"
    r"originally named|renamed|correction|corrected|\bresolved\b|supersed|"
    r"pro[\s-]?only|harmless|lacks it|\bsample\b|shizuku|phase 0|dissolved|tombstone|history|"
    r"deferred|\bpivot\b|gate-dependent|gate-ordered",
    re.I,
)
# Negation immediately before the token => it's stating the correct rule.
NEG_BEFORE = re.compile(r"(?i)(?:\bnot\b|\bno\b|\bnever\b|n['’]t|≠|isn|aren)\W{0,3}$")

FRONTIER = re.compile(
    r"(?:next\s*=\s*|Start at\s*\*{0,2}|Frontier\s*=\s*\*{0,2}|EXECUTE\s+|rig(?:s)? .*?\bin\s+)"
    r"\bW(\d+(?:\.\d+)?)\b"
)
PHASE_FRONTIER = re.compile(
    r"(?:NEXT|next\s+action|next\s+arc|next\s+step)\b[^.\n]{0,30}?\bPhase\s*([A-D](?:\s*\+\s*[A-D])*)\b",
    re.I,
)
COMMITS = re.compile(r"\b(\d+)\s+commits\b")
AHEAD_OF_ORIGIN = re.compile(r"ahead of\s+`?origin", re.I)
# A DOMAIN_MAP bullet whose marker is ❓ (an open question parked in the fact dictionary).
DM_OPEN_MARKER = re.compile(r"^\s*[-*]\s*❓")
ISO_DATE = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")


def sh(args, root):
    return subprocess.run(args, cwd=root, capture_output=True, text=True).stdout.strip()


def _expand(p, root):
    p = p.replace("<date>", "*").replace("<hash>", "*").replace("<slug>", "*")
    if "/" not in p and not p.endswith(".md"):
        return []
    base = [os.path.expanduser(p)] if p[:1] in "~/" else glob.glob(os.path.join(root, p))
    out = []
    for f in base:
        if os.path.isdir(f):
            out += glob.glob(os.path.join(f, "**", "*.md"), recursive=True)
        elif f.endswith(".md"):
            out.append(f)
    return out


def is_history(path):
    pl = path.replace(os.sep, "/").lower()
    return ("/features/archive/" in pl or "/plans/" in pl or "findings" in pl
            or "/adr/" in pl or "-pre-restructure-" in pl)


def parse_surfaces(root):
    """Returns (surfaces, authority, history_set).

    Targets come from the CLAUDE.md '## Orientation docs' map + the explicit
    new-structure homes + the memory dir. History is detected by path.
    """
    surfaces, history, authority = [], set(), None

    def add(f):
        if f not in surfaces:
            surfaces.append(f)
        if is_history(f):
            history.add(f)

    # 1) the CLAUDE.md entry-doc map (orientation section only — not directory roles)
    entry = os.path.join(root, ENTRY_REL)
    try:
        lines = open(entry, encoding="utf-8").read().splitlines()
    except OSError:
        lines = []
    in_section = False
    for ln in lines:
        if ln.startswith("## "):
            in_section = "orientation" in ln.lower()
            continue
        if not in_section:
            continue
        is_auth = ("authority" in ln.lower() or "read first" in ln.lower())
        for raw in re.findall(r"`([^`]+)`", ln):
            for f in _expand(raw, root):
                add(f)
                if is_auth and authority is None and f.replace(os.sep, "/").endswith("PIPELINE.md"):
                    authority = f

    # 2) explicit new-structure homes (robust before the CLAUDE.md edit lands)
    for r in EXPLICIT_REL:
        p = os.path.join(root, r)
        if os.path.exists(p):
            add(p)
    for g in EXPLICIT_GLOBS:
        for f in glob.glob(os.path.join(root, g)):
            add(f)

    # 3) the out-of-repo memory layer
    for f in glob.glob(os.path.join(MEMORY_DIR, "*.md")):
        add(f)

    if authority is None:
        pipe = os.path.join(root, "live2d/PIPELINE.md")
        authority = pipe if os.path.exists(pipe) else None
    return surfaces, authority, history


def annotated_near(lines, i):
    if ANNOTATED.search(lines[i]):
        return True
    seen = 0
    for j in range(i - 1, -1, -1):
        if not lines[j].strip():
            continue
        if ANNOTATED.search(lines[j]):
            return True
        seen += 1
        if seen >= 2:
            break
    return False


def latest_memory_date(root):
    """Latest claude-mem observation date (YYYY-MM-DD) for this project, or None.

    The IDEAL signal (the plan's intent) is the newest claude-mem observation; a
    stdlib script cannot reach the MCP, but the local SQLite store is readable
    read-only. Best-effort: any error (db absent on another machine, locked,
    schema drift) → None, never fails the run."""
    proj = os.path.basename(root.rstrip("/"))
    try:
        con = sqlite3.connect(f"file:{CLAUDE_MEM_DB}?mode=ro", uri=True, timeout=1.0)
        try:
            row = con.execute(
                "SELECT MAX(created_at) FROM observations WHERE project=?", (proj,)
            ).fetchone()
        finally:
            con.close()
        if row and row[0]:
            return row[0][:10]
    except Exception:
        return None
    return None


def latest_date_in(path):
    try:
        txt = open(path, encoding="utf-8").read()
    except OSError:
        return None
    ds = ISO_DATE.findall(txt)
    return max(ds) if ds else None


def find_tombstones(root):
    """Relpaths of dissolved docs — files whose H1 is marked DISSOLVED (the
    permanent redirect tombstones, ADR-0003). Detected by content so a new
    dissolution is caught without maintaining a hardcoded list."""
    out = []
    for p in glob.glob(os.path.join(root, "**", "*.md"), recursive=True):
        try:
            head = open(p, encoding="utf-8").read(300)
        except OSError:
            continue
        first = head.splitlines()[0] if head.strip() else ""
        if first.startswith("#") and re.search(r"\bDISSOLVED\b", first, re.I):
            out.append(os.path.relpath(p, root).replace(os.sep, "/"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    surfaces, authority, history = parse_surfaces(root)
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    fails, warns = [], []

    def rel(p):
        return os.path.relpath(p, root) if p.startswith(root) else p

    # ---- A. INV denylist (live surfaces only) ----
    for path in surfaces:
        ap_ = os.path.abspath(path)
        if ap_.startswith(skill_dir) or path in history:
            continue
        try:
            lines = open(path, encoding="utf-8").read().splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines):
            for inv, rx, note in DENYLIST:
                for m in rx.finditer(line):
                    if NEG_BEFORE.search(line[:m.start()]):
                        continue
                    if annotated_near(lines, i):
                        continue
                    fails.append(f"[{inv}] {rel(path)}:{i+1}  un-annotated: {note}\n        > {line.strip()[:108]}")
                    break

    # ---- B. frontier agreement (W-stage granularity) ----
    def tokens(path):
        try:
            return set(FRONTIER.findall(open(path, encoding="utf-8").read()))
        except OSError:
            return set()

    auth_tokens = tokens(authority) if authority else set()
    auth_max = max(auth_tokens, key=len) if auth_tokens else None
    for path in surfaces:
        for t in tokens(path):
            if auth_max and t != auth_max and auth_max.startswith(t + "."):
                warns.append(f"[frontier] {rel(path)}: says 'W{t}' but authority frontier = 'W{auth_max}' (granularity lag)")
            elif auth_tokens and t not in auth_tokens and "." not in t:
                warns.append(f"[frontier] {rel(path)}: 'W{t}' not among authority tokens {sorted(auth_tokens)}")

    # ---- B2. pivot phase-frontier agreement (Phase A/B/C/D) ----
    def phase_letters(path):
        out = set()
        try:
            txt = open(path, encoding="utf-8").read()
        except OSError:
            return out
        for tok in PHASE_FRONTIER.findall(txt):
            out |= set(re.findall(r"[A-D]", tok.upper()))
        return out

    auth_letters = phase_letters(authority) if authority else set()
    if auth_letters:
        for path in surfaces:
            ap_ = os.path.abspath(path)
            if ap_.startswith(skill_dir) or path in history:
                continue
            sl = phase_letters(path)
            if sl and sl.isdisjoint(auth_letters):
                fails.append(
                    f"[phase-frontier] {rel(path)}: next-action names Phase {sorted(sl)} "
                    f"but authority frontier = Phase {sorted(auth_letters)} (stale phase frontier — reconcile to the authority)")

    # ---- C. branch-state vs git ----
    if sh(["git", "rev-parse", "--git-dir"], root):
        mb = sh(["git", "merge-base", "master", "HEAD"], root)
        ahead = sh(["git", "rev-list", "--count", f"{mb}..HEAD"], root) if mb else ""
        behind = sh(["git", "rev-list", "--count", "HEAD..master"], root) if mb else ""
        ahead_origin = sh(["git", "rev-list", "--count", "origin/master..HEAD"], root) or ""
        for path in surfaces:
            if path in history:
                continue
            try:
                lines = open(path, encoding="utf-8").read().splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines):
                m = COMMITS.search(line)
                if not m:
                    continue
                baseline, blabel = (ahead_origin, "origin") if AHEAD_OF_ORIGIN.search(line) else (ahead, "master-base")
                if baseline and m.group(1) != baseline:
                    warns.append(f"[branch] {rel(path)}:{i+1}: prose pins '{m.group(1)} commits' but git ahead ({blabel}) = {baseline} (counts drift — prefer qualitative)")
        if behind and behind != "0":
            print(f"note: branch is 3-way (master has {behind} commit(s) HEAD lacks) — any 'clean FF' claim is a FAIL above.")

    # ---- D. DOMAIN_MAP marker rule (no ❓ in the fact dictionary) ----
    dm = os.path.join(root, DOMAIN_MAP_REL)
    if os.path.exists(dm):
        for i, line in enumerate(open(dm, encoding="utf-8").read().splitlines()):
            if DM_OPEN_MARKER.search(line):
                fails.append(
                    f"[domain-map] {DOMAIN_MAP_REL}:{i+1}: an ❓ bullet in the fact dictionary — "
                    f"open questions belong in docs/features/<slug>/RESEARCH.md (ADR-0003 marker rule)\n        > {line.strip()[:108]}")

    # ---- E. recency-warn (authority as-of date vs latest claude-mem observation) ----
    mem_date = latest_memory_date(root)
    fr_date = latest_date_in(authority) if authority else None
    if mem_date and fr_date and mem_date > fr_date:
        warns.append(
            f"[recency] authority {rel(authority)} as-of date {fr_date} < latest claude-mem observation "
            f"{mem_date} (project '{os.path.basename(root.rstrip('/'))}') — work may have landed since the "
            f"doc's stated date; a reconcile may be due. (Bump the authority's as-of date when you reconcile.)")

    # ---- F. dissolved-ref (a live nav surface must not cite a dissolved doc as live) ----
    tombstones = find_tombstones(root)
    tomb_set = set(tombstones)
    mem_abs = os.path.abspath(MEMORY_DIR)

    def dref_skip(path):
        rp = rel(path).replace(os.sep, "/")
        ap2 = os.path.abspath(path)
        # frozen lineage (history/specs/ADRs/archive), the tombstones themselves, this skill,
        # and the memory layer (reconciled on a SEPARATE track — ADR-0003 Open) are exempt.
        return (path in history or ap2.startswith(skill_dir) or rp in tomb_set
                or "/specs/" in rp or ap2.startswith(mem_abs))

    # the CLAUDE.md entry doc is the prime target even though it is not a scanned surface
    dref_targets = [os.path.join(root, ENTRY_REL)] + [s for s in surfaces if not dref_skip(s)]
    seen = set()
    for path in dref_targets:
        ap2 = os.path.abspath(path)
        if ap2 in seen:
            continue
        seen.add(ap2)
        try:
            txt = open(path, encoding="utf-8").read()
        except OSError:
            continue
        for diss in tombstones:
            if diss in txt:
                fails.append(
                    f"[dissolved-ref] {rel(path)} cites dissolved '{diss}' as live — repoint to its new home "
                    f"(the tombstone is a permanent redirect; do not cite a dissolved doc as an authority)")

    # ---- report ----
    print(f"reconcile-docs freshness: {len(surfaces)} surfaces "
          f"({len(history)} history-exempt), authority = {rel(authority) if authority else '?'}")
    for w in warns:
        print("WARN " + w)
    for f in fails:
        print("FAIL " + f)
    if fails:
        print(f"\n{len(fails)} hard failure(s), {len(warns)} warning(s). Reconcile, then re-run.")
        return 1
    print(f"\nclean ({len(warns)} warning(s) — judgment calls, review).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
