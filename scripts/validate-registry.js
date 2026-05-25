import fs from "node:fs";
import path from "node:path";
import Ajv2020 from "ajv/dist/2020.js";
import YAML from "yaml";

const root = process.cwd();
const ajv = new Ajv2020({ allErrors: true });

function loadJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
}

function loadYaml(relativePath) {
  return YAML.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
}

function validate(name, schemaPath, dataPath, loader) {
  const schema = loadJson(schemaPath);
  const data = loader(dataPath);
  const validateFn = ajv.compile(schema);

  if (!validateFn(data)) {
    const details = ajv.errorsText(validateFn.errors, { separator: "\n" });
    throw new Error(`${name} failed validation:\n${details}`);
  }

  console.log(`ok ${dataPath}`);
  return data;
}

function assertNoSnapshotPlaceholders(relativePath, snapshot) {
  const placeholders = Object.entries(snapshot)
    .filter(([, value]) => typeof value === "string")
    .filter(([, value]) => value === "unknown" || value.startsWith("replace-with-"))
    .map(([key, value]) => `${key}: ${value}`);

  if (placeholders.length > 0) {
    throw new Error(`${relativePath} contains placeholder metadata:\n${placeholders.join("\n")}`);
  }
}

const palette = validate("palette", "schema/palette.schema.json", "registry/palette.yaml", loadYaml);
validate("screens", "schema/screens.schema.json", "registry/screens.yaml", loadYaml);
const selectors = validate("selectors", "schema/selectors.schema.json", "registry/selectors.yaml", loadYaml);
validate("do-not-touch", "schema/do-not-touch.schema.json", "registry/do-not-touch.yaml", loadYaml);
validate("risks", "schema/risks.schema.json", "registry/risks.yaml", loadYaml);

const paletteRoles = new Set(Object.keys(palette.palette ?? {}));
const unknownRoles = Object.entries(selectors.selectors ?? {})
  .filter(([, selector]) => selector.paletteRole && !paletteRoles.has(selector.paletteRole))
  .map(([name, selector]) => `${name}: ${selector.paletteRole}`);

if (unknownRoles.length > 0) {
  throw new Error(`selectors reference unknown paletteRole values:\n${unknownRoles.join("\n")}`);
}

const snapshotSchema = loadJson("schema/snapshot.schema.json");
const validateSnapshot = ajv.compile(snapshotSchema);
const snapshotsRoot = path.join(root, "snapshots");

if (fs.existsSync(snapshotsRoot)) {
  for (const dateDir of fs.readdirSync(snapshotsRoot).sort()) {
    const fullDateDir = path.join(snapshotsRoot, dateDir);
    if (!fs.statSync(fullDateDir).isDirectory()) continue;

    for (const file of fs.readdirSync(fullDateDir).sort()) {
      if (!file.endsWith(".json")) continue;

      const relativePath = path.join("snapshots", dateDir, file);
      const data = loadJson(relativePath);
      if (!validateSnapshot(data)) {
        const details = ajv.errorsText(validateSnapshot.errors, { separator: "\n" });
        throw new Error(`${relativePath} failed validation:\n${details}`);
      }

      assertNoSnapshotPlaceholders(relativePath, data);
      console.log(`ok ${relativePath}`);
    }
  }
}
