import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import YAML from "yaml";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function readText(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

test("every selector class is referenced inside its cssOwner partial", () => {
  const selectorsDoc = YAML.parse(readText("registry/selectors.yaml"));
  const entries = Object.entries(selectorsDoc?.selectors ?? {});
  assert.ok(entries.length > 0, "registry/selectors.yaml must declare at least one selector entry");

  const ownerCache = new Map();
  const missing = [];

  for (const [name, entry] of entries) {
    if (!ownerCache.has(entry.cssOwner)) {
      ownerCache.set(entry.cssOwner, readText(entry.cssOwner));
    }
    const ownerCss = ownerCache.get(entry.cssOwner);

    for (const className of entry.classes ?? []) {
      if (!ownerCss.includes(className)) {
        missing.push(`${name}: class "${className}" not referenced in ${entry.cssOwner}`);
      }
    }
  }

  assert.deepEqual(missing, [], `selector classes missing from their cssOwner partial:\n${missing.join("\n")}`);
});
