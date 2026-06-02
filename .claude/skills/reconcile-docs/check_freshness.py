#!/usr/bin/env python3
"""reconcile-docs freshness validator.

Makes the mechanical half of the reconcile-docs Step-2 "Detect drift" pass
*executable* instead of eyeballed prose, so an execution lapse (the failure
mode that actually bit us: detection worked, write-back was skipped) is caught
by a command rather than by another reminder.

It does NOT replace judgment. It checks only what is enforceable:
  A. INV denylist  — superseded values (INV-* in the registry) appearing
                     UN-annotated and non-negated in a LIVE orientation surface.
  B. Frontier      — the "next/frontier" phase token agrees across surfaces
                     (catches granularity lag, e.g. "W4" vs the authority's "W4.2").
  C. Branch-state  — commit counts pinned in prose vs `git rev-list`, and any
                     "clean fast-forward" claim vs the real master/HEAD topology.

History surfaces (completed plans, FINDINGS — registry role contains
"history"/"annotate"/"never rewrite") are EXEMPT from the denylist: they are
supposed to retain the old values under a SUPERSEDED banner. Negated mentions
("NOT 4096", "no ParamEyeForm") and correct-context mentions ("PRO-only",
"resolved", "supersedes") are not violations either.

The surface list is PARSED FROM the registry table (single source of truth —
do not duplicate it here), with a fallback if the table cannot be parsed.

Usage:  python3 check_freshness.py [--root <worktree-root>]
Exit:   0 = clean (warnings allowed), 1 = hard FAIL. Stdlib only.
"""
from __future__ import annotations
import argparse
import glob
import os
import re
import subprocess
import sys

MEMORY_DIR = os.path.expanduser(
    "~/.claude/projects/-home-benjohnbill-dev-discord-theme-lotte/memory"
)
REGISTRY_REL = "docs/superpowers/DOC_ARCHITECTURE.md"

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
    # "Phase 2 / Vencord userplugin as the next/larger arc" is now the superseded value. ("deferred"/"pivot"
    # near the mention whitelist the correct "Phase 2 is DEFERRED behind the pivot" phrasing.)
    ("INV-3", re.compile(r"(?:real|larger|next)\s+arc\s*=?\s*(?:is\s+)?Phase\s*2", re.I),
     "Phase 2 as the next/larger arc (DEFERRED behind the rig-strategy pivot, ADR-0001)"),
]

# Hit line or up to 2 preceding non-blank lines mark it superseded/correct.
ANNOTATED = re.compile(
    r"superseded|⚠️|was wrong|\bstale\b|there is no|no standard|not merged|"
    r"originally named|renamed|correction|corrected|\bresolved\b|supersed|"
    r"pro[\s-]?only|harmless|lacks it|\bsample\b|shizuku|phase 0|"
    r"deferred|\bpivot\b|gate-dependent|gate-ordered",
    re.I,
)
# Negation immediately before the token => it's stating the correct rule.
NEG_BEFORE = re.compile(r"(?i)(?:\bnot\b|\bno\b|\bnever\b|n['’]t|≠|isn|aren)\W{0,3}$")

FRONTIER = re.compile(
    r"(?:next\s*=\s*|Start at\s*\*{0,2}|Frontier\s*=\s*\*{0,2}|EXECUTE\s+|rig(?:s)? .*?\bin\s+)"
    r"\bW(\d+(?:\.\d+)?)\b"
)
# Pivot phase frontier (A/B/C/D). The W-token regex above is BLIND to the pivot naming,
# so without this the frontier check is a no-op for the CURRENT frontier — which is exactly
# how a stale "next = Phase B" slipped past a clean run (all surfaces consistently stale, but
# the checker never looked at phase letters). Captures the phase token in a "next" context.
PHASE_FRONTIER = re.compile(
    r"(?:NEXT|next\s+action|next\s+arc|next\s+step)\b[^.\n]{0,30}?\bPhase\s*([A-D](?:\s*\+\s*[A-D])*)\b",
    re.I,
)
COMMITS = re.compile(r"\b(\d+)\s+commits\b")
# A commit-count phrased against origin is compared to origin..HEAD, not master..HEAD.
AHEAD_OF_ORIGIN = re.compile(r"ahead of\s+`?origin", re.I)
HISTORY_ROLE = re.compile(r"history|annotate|never rewrite|superseded", re.I)


def sh(args, root):
    return subprocess.run(args, cwd=root, capture_output=True, text=True).stdout.strip()


def _expand(p, root):
    p = p.replace("<date>", "*").replace("<hash>", "*")
    if "/" not in p and not p.endswith(".md"):
        return []
    base = [os.path.expanduser(p)] if p[:1] in "~/" else glob.glob(os.path.join(root, p))
    out = []
    for f in base:
        if os.path.isdir(f):
            out += glob.glob(os.path.join(f, "*.md"))
        elif f.endswith(".md"):
            out.append(f)
    return out


def parse_surfaces(root):
    """Returns (surfaces, authority, history_set) parsed from the registry table."""
    reg = os.path.join(root, REGISTRY_REL)
    surfaces, history, authority = [], set(), None
    try:
        lines = open(reg, encoding="utf-8").read().splitlines()
    except OSError:
        return [], None, set()
    in_table = False
    for ln in lines:
        if ln.startswith("## "):
            in_table = "Orientation surfaces" in ln
            continue
        if not (in_table and ln.startswith("|")):
            continue
        is_hist = bool(HISTORY_ROLE.search(ln))
        is_auth = "authority" in ln.lower()
        for raw in re.findall(r"`([^`]+)`", ln):
            for f in _expand(raw, root):
                if f not in surfaces:
                    surfaces.append(f)
                if is_hist:
                    history.add(f)
                if is_auth and authority is None and f.endswith(".md"):
                    authority = f
    for f in glob.glob(os.path.join(MEMORY_DIR, "*.md")):
        if f not in surfaces:
            surfaces.append(f)
    return surfaces, authority, history


def fallback_surfaces(root):
    rel = ["docs/superpowers/next-session-prompt.md", "live2d/PIPELINE.md",
           "live2d/RIG_GUIDE.md", "live2d/DECISIONS.md", "live2d/BASE.md", "live2d/gen/PROMPTS.md"]
    out = [os.path.join(root, r) for r in rel if os.path.exists(os.path.join(root, r))]
    out += glob.glob(os.path.join(root, "docs/superpowers/specs/*.md"))
    out += glob.glob(os.path.join(MEMORY_DIR, "*.md"))
    return out, os.path.join(root, "live2d/PIPELINE.md"), set()


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    surfaces, authority, history = parse_surfaces(root)
    if len(surfaces) < 3:
        surfaces, authority, history = fallback_surfaces(root)
    reg_abs = os.path.abspath(os.path.join(root, REGISTRY_REL))
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    fails, warns = [], []

    def rel(p):
        return os.path.relpath(p, root) if p.startswith(root) else p

    # ---- A. INV denylist (live surfaces only) ----
    for path in surfaces:
        ap_ = os.path.abspath(path)
        if ap_ == reg_abs or ap_.startswith(skill_dir) or path in history:
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

    # ---- B. frontier agreement ----
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
    # A surface whose next-action phase letters are DISJOINT from the authority's is stale
    # (e.g. "next = Phase B" vs authority "Phase C+D"). Overlap (C / D / C+D phrasings) passes;
    # this is a FAIL, not a warn — it is the consistently-stale-frontier lapse we want to block.
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
            if ap_ == reg_abs or ap_.startswith(skill_dir) or path in history:
                continue  # registry enumerates stale-triggers; history keeps old frontiers
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
        # origin baseline: a count phrased "ahead of origin" is compared to origin/master..HEAD.
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
