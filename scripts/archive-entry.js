import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import YAML from "yaml";

import {
  appendToArchive,
  buildArchiveEntry,
  removeFromRegistry
} from "./archive-lib.js";

const SOURCES = {
  selectors: { file: "registry/selectors.yaml", rootKey: "selectors" },
  "do-not-touch": { file: "registry/do-not-touch.yaml", rootKey: "selectors" }
};

function parseArgs(argv) {
  const args = { key: undefined, from: undefined, reason: undefined, evidence: undefined, replacedBy: undefined };

  function consumeValue(flag) {
    if (i + 1 >= argv.length) {
      throw new Error(`${flag} requires a value`);
    }
    return argv[++i];
  }

  let i = 0;
  for (; i < argv.length; i++) {
    const token = argv[i];
    if (token === "--from") args.from = consumeValue("--from");
    else if (token === "--reason") args.reason = consumeValue("--reason");
    else if (token === "--evidence") args.evidence = consumeValue("--evidence");
    else if (token === "--replaced-by") args.replacedBy = consumeValue("--replaced-by");
    else if (!args.key) args.key = token;
    else throw new Error(`unexpected argument: ${token}`);
  }

  if (!args.key) throw new Error("missing required positional argument: <key>");
  if (!args.reason) throw new Error("missing required option: --reason <text>");
  return args;
}

function resolveSource(key, fromOption, root) {
  if (fromOption) {
    const candidate = SOURCES[fromOption];
    if (!candidate) {
      throw new Error(`unknown --from value "${fromOption}". Valid: ${Object.keys(SOURCES).join(", ")}`);
    }
    return candidate;
  }

  const matches = [];
  for (const [, source] of Object.entries(SOURCES)) {
    const doc = YAML.parse(fs.readFileSync(path.join(root, source.file), "utf8"));
    if (doc?.[source.rootKey] && key in doc[source.rootKey]) {
      matches.push(source);
    }
  }

  if (matches.length === 0) {
    throw new Error(`key "${key}" not found in any source registry`);
  }
  if (matches.length > 1) {
    const names = matches.map((s) => s.file).join(", ");
    throw new Error(`key "${key}" is ambiguous (in ${names}). Specify --from <selectors|do-not-touch>.`);
  }
  return matches[0];
}

function writeYaml(absolutePath, doc) {
  fs.writeFileSync(absolutePath, `${YAML.stringify(doc)}`);
}

function main() {
  const root = process.cwd();
  const args = parseArgs(process.argv.slice(2));
  const source = resolveSource(args.key, args.from, root);

  const sourceAbsolute = path.join(root, source.file);
  const archiveAbsolute = path.join(root, "registry/archive.yaml");

  const sourceDoc = YAML.parse(fs.readFileSync(sourceAbsolute, "utf8"));
  const archiveDoc = YAML.parse(fs.readFileSync(archiveAbsolute, "utf8"));

  const originalEntry = sourceDoc[source.rootKey][args.key];
  const archivedAt = new Date().toISOString().slice(0, 10);

  const entry = buildArchiveEntry({
    key: args.key,
    fromFile: source.file,
    originalEntry,
    reason: args.reason,
    archivedAt,
    evidence: args.evidence,
    replacedBy: args.replacedBy
  });

  const nextSource = removeFromRegistry(sourceDoc, source.rootKey, args.key);
  const nextArchive = appendToArchive(archiveDoc, entry);

  writeYaml(sourceAbsolute, nextSource);
  writeYaml(archiveAbsolute, nextArchive);

  console.log(`Archived ${args.key} from ${source.file} → registry/archive.yaml`);
}

const isCli = process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname);
if (isCli) {
  main();
}
