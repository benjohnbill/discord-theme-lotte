import fs from "node:fs";
import path from "node:path";
import Ajv2020 from "ajv/dist/2020.js";
import YAML from "yaml";

import {
  checkScreensLatestSnapshot,
  checkScreensOwns,
  checkSelectorsCssOwners,
  checkSelectorsDoNotTouch,
  checkSelectorsScreens,
  checkSnapshotsScreens,
  checkSrcPartialsRegistered
} from "./registry-checks.js";

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
const screensDoc = validate("screens", "schema/screens.schema.json", "registry/screens.yaml", loadYaml);
const selectorsDoc = validate("selectors", "schema/selectors.schema.json", "registry/selectors.yaml", loadYaml);
const doNotTouchDoc = validate("do-not-touch", "schema/do-not-touch.schema.json", "registry/do-not-touch.yaml", loadYaml);
validate("risks", "schema/risks.schema.json", "registry/risks.yaml", loadYaml);
validate("archive", "schema/archive.schema.json", "registry/archive.yaml", loadYaml);

const paletteRoles = new Set(Object.keys(palette.palette ?? {}));
const unknownRoles = Object.entries(selectorsDoc.selectors ?? {})
  .filter(([, selector]) => selector.paletteRole && !paletteRoles.has(selector.paletteRole))
  .map(([name, selector]) => `${name}: ${selector.paletteRole}`);

if (unknownRoles.length > 0) {
  throw new Error(`selectors reference unknown paletteRole values:\n${unknownRoles.join("\n")}`);
}

const manifest = YAML.parse(fs.readFileSync(path.join(root, "theme.manifest.yaml"), "utf8"));

const snapshots = [];
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
      snapshots.push({ path: relativePath, data });
      console.log(`ok ${relativePath}`);
    }
  }
}

function listSrcCssFiles() {
  const srcRoot = path.join(root, "src");
  const collected = [];

  function walk(absoluteDir) {
    const entries = fs
      .readdirSync(absoluteDir, { withFileTypes: true })
      .sort((a, b) => a.name.localeCompare(b.name));

    for (const entry of entries) {
      const absolutePath = path.join(absoluteDir, entry.name);
      if (entry.isDirectory()) {
        walk(absolutePath);
        continue;
      }
      if (!entry.name.endsWith(".css")) continue;
      collected.push(path.relative(root, absolutePath));
    }
  }

  if (fs.existsSync(srcRoot)) {
    walk(srcRoot);
  }
  return collected;
}

const existsOnDisk = (relativePath) => fs.existsSync(path.join(root, relativePath));
const srcCssFiles = listSrcCssFiles();

const crossErrors = [
  ...checkSelectorsScreens(selectorsDoc, screensDoc),
  ...checkSelectorsCssOwners(selectorsDoc, manifest),
  ...checkSelectorsDoNotTouch(selectorsDoc, doNotTouchDoc),
  ...checkScreensOwns(screensDoc, manifest),
  ...checkScreensLatestSnapshot(screensDoc, existsOnDisk),
  ...checkSnapshotsScreens(snapshots, screensDoc),
  ...checkSrcPartialsRegistered(srcCssFiles, manifest)
];

if (crossErrors.length > 0) {
  throw new Error(`cross-reference checks failed:\n${crossErrors.join("\n")}`);
}

console.log("ok registry cross-references");
