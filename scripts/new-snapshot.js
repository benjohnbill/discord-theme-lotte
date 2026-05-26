import nodeFs from "node:fs";
import path from "node:path";
import process from "node:process";
import YAML from "yaml";

export function scaffoldSnapshot({ screen, today, root, fsImpl, screensDoc, themeVersion }) {
  const knownScreens = new Set(Object.keys(screensDoc?.screens ?? {}));
  if (!knownScreens.has(screen)) {
    throw new Error(`unknown screen "${screen}". Add it to registry/screens.yaml first.`);
  }

  if (typeof themeVersion !== "string" || themeVersion.length === 0) {
    throw new Error("themeVersion is required; pass the value from package.json");
  }

  const relativePath = `snapshots/${today}/${screen}.json`;
  const absolutePath = path.join(root, relativePath);

  if (fsImpl.existsSync(absolutePath)) {
    throw new Error(`refusing to overwrite existing file ${relativePath}`);
  }

  const stub = {
    schemaVersion: 1,
    capturedAt: `${today}T00:00:00+09:00`,
    discordBuild: "unknown",
    vencordVersion: "unknown",
    themeVersion,
    os: "unknown",
    zoom: "unknown",
    screen,
    routeHint: "replace-with-current-route",
    viewport: "replace-with-viewport",
    sourceScreenshot: "replace-with-screenshot-path",
    notes: "Stub created by scripts/new-snapshot.js. Replace placeholders before commit.",
    elements: []
  };

  fsImpl.mkdirSync(path.dirname(absolutePath), { recursive: true });
  fsImpl.writeFileSync(absolutePath, `${JSON.stringify(stub, null, 2)}\n`);

  return { relativePath, absolutePath };
}

function main() {
  const screen = process.argv[2];
  if (!screen) {
    console.error("usage: node scripts/new-snapshot.js <screen-id>");
    process.exit(1);
  }

  const root = process.cwd();
  const screensDoc = YAML.parse(nodeFs.readFileSync(path.join(root, "registry/screens.yaml"), "utf8"));
  const pkg = JSON.parse(nodeFs.readFileSync(path.join(root, "package.json"), "utf8"));
  const today = new Date().toISOString().slice(0, 10);

  const { relativePath } = scaffoldSnapshot({
    screen,
    today,
    root,
    fsImpl: nodeFs,
    screensDoc,
    themeVersion: pkg.version
  });

  console.log(`Scaffolded ${relativePath}`);
}

const isCli = process.argv[1] && path.resolve(process.argv[1]) === path.resolve(new URL(import.meta.url).pathname);
if (isCli) {
  main();
}
