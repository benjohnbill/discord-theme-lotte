import fs from "node:fs";
import path from "node:path";
import YAML from "yaml";

const root = process.cwd();
const manifestPath = path.join(root, "theme.manifest.yaml");
const manifest = YAML.parse(fs.readFileSync(manifestPath, "utf8"));

if (manifest.schemaVersion !== 1) {
  throw new Error(`Unsupported manifest schemaVersion: ${manifest.schemaVersion}`);
}

if (!Array.isArray(manifest.partials) || manifest.partials.length === 0) {
  throw new Error("theme.manifest.yaml must define non-empty partials");
}

const chunks = [];
for (const partial of manifest.partials) {
  const partialPath = path.join(root, partial);
  if (!fs.existsSync(partialPath)) {
    throw new Error(`Manifest partial does not exist: ${partial}`);
  }

  const css = fs.readFileSync(partialPath, "utf8").trimEnd();
  chunks.push(`/* source: ${partial} */\n${css}\n`);
}

const outputPath = path.join(root, manifest.output);
fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, `${chunks.join("\n")}\n`, "utf8");

console.log(`Built ${manifest.output} from ${manifest.partials.length} partials`);
