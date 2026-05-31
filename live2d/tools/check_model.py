"""W4.3: validate live2d/model/lotte.model3.json after the Cubism export — moc3 version <= 5
(the runtime Core max; it rejects v6), all referenced files exist, and populate/fix the EyeBlink
group + LipSync if Cubism exported them empty (pilot fix). Run after every (re)export.

Staged ahead of the W4.2 user export: it will FileNotFound until live2d/model/ exists — that is
expected; run it the moment the rig is exported."""
import json, pathlib, sys

MODEL = pathlib.Path("live2d/model/lotte.model3.json")
if not MODEL.exists():
    print(f"{MODEL} not found yet — export the rig in W4.2 first, then re-run.", file=sys.stderr)
    sys.exit(1)

d = json.loads(MODEL.read_text())
base = MODEL.parent
refs = d["FileReferences"]

moc = base / refs["Moc"]
ver = moc.read_bytes()[4]
print(f"moc3 magic ok, version_byte = {ver}", "(<=5 OK)" if ver <= 5 else "(>5 — WILL NOT LOAD; re-export at moc3 5.0)")
assert ver <= 5, "moc3 version > 5: the pinned Core rejects it. Re-export at .moc3 version 5.0."

for t in refs.get("Textures", []):
    assert (base / t).exists(), f"missing texture {t}"
if refs.get("Physics"):
    assert (base / refs["Physics"]).exists(), "missing physics3.json"
print("textures + physics present:", refs.get("Textures"), refs.get("Physics"))

# Cubism FREE export omits the Groups array entirely (and re-omits it on every re-export),
# so auto-blink/lip-sync have no params to drive. Ensure EyeBlink + LipSync exist and are
# populated — create-if-absent (not just fill-if-empty) so this is idempotent across re-exports.
# Only reference params the model actually declares (from the cdi3 DisplayInfo).
avail = set()
if refs.get("DisplayInfo") and (base / refs["DisplayInfo"]).exists():
    cdi = json.loads((base / refs["DisplayInfo"]).read_text())
    avail = {p["Id"] for p in cdi.get("Parameters", [])}

WANT = {"EyeBlink": ["ParamEyeLOpen", "ParamEyeROpen"], "LipSync": ["ParamMouthOpenY"]}
groups = d.setdefault("Groups", [])
changed = False
for name, ids in WANT.items():
    ids = [p for p in ids if not avail or p in avail]
    if not ids:
        print(f"skip {name}: none of its params present in model"); continue
    g = next((x for x in groups if x.get("Name") == name), None)
    if g is None:
        groups.append({"Target": "Parameter", "Name": name, "Ids": ids}); changed = True
    elif not g.get("Ids"):
        g["Target"] = "Parameter"; g["Ids"] = ids; changed = True
if changed:
    MODEL.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print("ensured EyeBlink + LipSync groups:", {g["Name"]: g["Ids"] for g in groups})
print("OK")
