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

const desktopBody = `${chunks.join("\n")}\n`;
const outputPath = path.join(root, manifest.output);
fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, desktopBody, "utf8");

console.log(`Built ${manifest.output} from ${manifest.partials.length} partials`);

if (manifest.webOutput) {
  const web = manifest.webOutput;
  if (!web.path || !web.domain) {
    throw new Error("theme.manifest.yaml webOutput requires path and domain");
  }

  const meta = parseHeaderMeta(chunks[0]);
  const userStyleHeader = buildUserStyleHeader(meta, web);
  const escapedBody = escapeNonAscii(desktopBody);
  const wrappedBody = `@-moz-document domain(${JSON.stringify(web.domain)}) {\n${escapedBody}}\n`;
  const webPath = path.join(root, web.path);
  fs.mkdirSync(path.dirname(webPath), { recursive: true });
  fs.writeFileSync(webPath, `${userStyleHeader}\n${wrappedBody}`, "utf8");

  console.log(`Built ${web.path} (Stylus userstyle for ${web.domain})`);
}

function escapeNonAscii(str) {
  return str.replace(/[-￿]/g, (ch) => {
    const hex = ch.charCodeAt(0).toString(16).toUpperCase().padStart(6, "0");
    return `\\${hex} `;
  });
}

function parseHeaderMeta(headerChunk) {
  const meta = {};
  const fields = ["name", "author", "description", "version"];
  for (const field of fields) {
    const match = headerChunk.match(new RegExp(`@${field}\\s+(.+)`));
    if (match) meta[field] = match[1].trim();
  }
  return meta;
}

function buildUserStyleHeader(meta, web) {
  const namespace = web.namespace ?? "github.com/benjohnbill/discord-theme-lotte";
  const lines = [
    "/* ==UserStyle==",
    `@name           ${meta.name ?? "Discord Theme"}`,
    `@namespace      ${namespace}`,
    `@version        ${meta.version ?? "0.0.0"}`,
    `@description    ${meta.description ?? ""}`,
    `@author         ${meta.author ?? ""}`,
  ];
  if (web.updateURL) lines.push(`@updateURL      ${web.updateURL}`);
  lines.push("@preprocessor   default");
  lines.push("==/UserStyle== */");
  return lines.join("\n");
}
