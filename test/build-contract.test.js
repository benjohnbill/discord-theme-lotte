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

test("generated theme follows manifest output and partial order", () => {
  const manifest = YAML.parse(readText("theme.manifest.yaml"));
  const generated = readText(manifest.output);

  assert.equal(manifest.output, "dist/NewKemonoFriends.theme.css");
  assert.ok(Array.isArray(manifest.partials));
  assert.ok(manifest.partials.length > 0);

  const expected = `${manifest.partials
    .map((partial) => `/* source: ${partial} */\n${readText(partial).trimEnd()}\n`)
    .join("\n")}\n`;

  assert.equal(generated, expected);
});
