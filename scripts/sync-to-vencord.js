import fs from "node:fs";
import path from "node:path";
import YAML from "yaml";

const root = process.cwd();
const manifest = YAML.parse(fs.readFileSync(path.join(root, "theme.manifest.yaml"), "utf8"));
const outputPath = path.join(root, manifest.output);
const targetPath = process.env.VENCORD_THEME_TARGET ?? manifest.vencordTarget;

if (!fs.existsSync(outputPath)) {
  throw new Error(`Build output missing: ${manifest.output}. Run npm run build first.`);
}

const css = fs.readFileSync(outputPath);
fs.copyFileSync(outputPath, targetPath);

console.log(`Synced ${css.byteLength} bytes to ${targetPath}`);
