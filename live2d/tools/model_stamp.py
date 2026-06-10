#!/usr/bin/env python3
"""model_stamp.py - freshness fingerprint for a Live2D runtime model.

Print this BEFORE any agent-side render, or any "is this the current model?" claim, so we
always know exactly which export is loaded: SHA + mtime + size + moc3 version + band-type guess.
It exists because the verification loop kept silently loading stale/wrong models -- see
live2d/PIPELINE.md (2026-06-08 loop redesign). Two different bad states share the ~34K size
(06-01 pre-pivot mesh-deform AND the full-silhouette band), so size alone is ambiguous: the SHA
is the only definitive identity. Stdlib only; runs under any python3.

Usage:
  python3 live2d/tools/model_stamp.py [path/to/xxx.model3.json]   # default: live2d/model/lotte.model3.json
"""
import json, hashlib, sys, datetime
from pathlib import Path

DEFAULT = Path("live2d/model/lotte.model3.json")


def sha12(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()[:12]


def mtime(p: Path) -> str:
    return datetime.datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds")


def band_guess(nbytes: int) -> str:
    kb = nbytes / 1024
    if kb < 28:
        return f"~{kb:.0f}K SMALL-band (rt1-3 class -> runtime-clean blink)"
    return (f"~{kb:.0f}K WIDE/full mesh (34K class: 06-01 pre-pivot mesh-deform OR "
            f"full-silhouette band -- both may warp at runtime; SHA disambiguates)")


def main():
    mp = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not mp.exists() and (Path("..") / mp).exists():   # tolerate running from live2d/
        mp = Path("..") / mp
    if not mp.exists():
        print(f"NO MODEL at {mp} -- nothing loaded (export to model/ first).", file=sys.stderr)
        sys.exit(1)

    d = json.loads(mp.read_text())
    base = mp.parent
    refs = d.get("FileReferences", {})
    moc = base / refs["Moc"]
    raw = moc.read_bytes()
    ver = raw[4]

    print(f"=== model_stamp: {mp} ===")
    print(f"  moc3      : {moc.name}")
    print(f"  sha256/12 : {sha12(raw)}")
    print(f"  size      : {len(raw)} bytes  ({band_guess(len(raw))})")
    print(f"  mtime     : {mtime(moc)}")
    print(f"  moc3 ver  : {ver}  ({'OK <=5' if ver <= 5 else '>5 WILL NOT LOAD'})")
    for t in refs.get("Textures", []):
        tp = base / t
        print(f"  texture   : {t}  ({tp.stat().st_size if tp.exists() else 'MISSING'} bytes)")
    print(f"  physics   : {refs.get('Physics', '(none)')}")
    di = refs.get("DisplayInfo")
    if di and (base / di).exists():
        cdi = json.loads((base / di).read_text())
        print(f"  cdi3      : {len(cdi.get('Parameters', []))} params, {len(cdi.get('Parts', []))} parts")
    print(f"  groups    : {[g.get('Name') for g in d.get('Groups', [])]}")


if __name__ == "__main__":
    main()
