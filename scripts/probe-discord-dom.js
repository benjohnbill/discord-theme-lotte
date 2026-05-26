import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import YAML from "yaml";

import { probeScreen } from "./probe-lib.js";

const DISCORD_URL_PREFIXES = [
  "https://discord.com/",
  "https://canary.discord.com/",
  "https://ptb.discord.com/"
];

function parseArgs(argv) {
  const args = { screen: undefined };
  for (let i = 0; i < argv.length; i++) {
    const token = argv[i];
    if (!args.screen) args.screen = token;
    else throw new Error(`unexpected argument: ${token}`);
  }
  if (!args.screen) throw new Error("missing required positional argument: <screen>");
  return args;
}

async function findDiscordTarget(baseUrl) {
  const listResponse = await fetch(`${baseUrl}/json/list`);
  if (!listResponse.ok) {
    throw new Error(`CDP /json/list returned HTTP ${listResponse.status}. Is Discord running with --remote-debugging-port?`);
  }
  const targets = await listResponse.json();
  const candidates = targets.filter((target) => {
    if (target.type !== "page") return false;
    return DISCORD_URL_PREFIXES.some((prefix) => typeof target.url === "string" && target.url.startsWith(prefix));
  });

  if (candidates.length === 0) {
    throw new Error("no Discord renderer found among CDP targets. Open the Discord main window and try again.");
  }
  if (candidates.length > 1) {
    console.error(`Warning: ${candidates.length} Discord renderers found; using the first.`);
  }
  return candidates[0];
}

async function evaluateOnTarget(webSocketDebuggerUrl, expression) {
  const ws = new WebSocket(webSocketDebuggerUrl);

  const opened = new Promise((resolve, reject) => {
    ws.addEventListener("open", () => resolve(), { once: true });
    ws.addEventListener("error", (event) => reject(new Error(`CDP WebSocket error: ${event.message ?? "unknown"}`)), { once: true });
  });

  await opened;

  const message = {
    id: 1,
    method: "Runtime.evaluate",
    params: { expression, returnByValue: true, awaitPromise: false }
  };

  const replied = new Promise((resolve, reject) => {
    ws.addEventListener("message", (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.id === 1) resolve(data);
      } catch (error) {
        reject(error);
      }
    });
    ws.addEventListener("error", (event) => reject(new Error(`CDP WebSocket error: ${event.message ?? "unknown"}`)), { once: true });
  });

  ws.send(JSON.stringify(message));
  const response = await replied;
  ws.close();

  if (response.error) {
    throw new Error(`CDP Runtime.evaluate error: ${response.error.message}`);
  }
  const remoteValue = response.result?.result;
  if (remoteValue?.type === "object" && remoteValue.value !== undefined) {
    return remoteValue.value;
  }
  if (remoteValue?.subtype === "error" || response.result?.exceptionDetails) {
    const text = response.result?.exceptionDetails?.text ?? remoteValue?.description ?? "unknown CDP exception";
    throw new Error(`CDP renderer threw: ${text}`);
  }
  throw new Error("CDP Runtime.evaluate returned an unexpected shape");
}

function buildRealCdpClient(baseUrl) {
  return {
    async evaluate(expression) {
      const target = await findDiscordTarget(baseUrl);
      return evaluateOnTarget(target.webSocketDebuggerUrl, expression);
    }
  };
}

async function main() {
  const root = process.cwd();
  const baseUrl = process.env.DISCORD_CDP_URL;
  if (!baseUrl) {
    throw new Error("DISCORD_CDP_URL is not set. See docs/workflow.md§Discord CDP Setup.");
  }

  const args = parseArgs(process.argv.slice(2));
  const screensDoc = YAML.parse(fs.readFileSync(path.join(root, "registry/screens.yaml"), "utf8"));
  const selectorsDoc = YAML.parse(fs.readFileSync(path.join(root, "registry/selectors.yaml"), "utf8"));

  const cdpClient = buildRealCdpClient(baseUrl);
  const output = await probeScreen({
    screen: args.screen,
    screensDoc,
    selectorsDoc,
    cdpClient
  });

  process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);

  if (output.missing.length > 0) {
    process.exit(1);
  }
}

main().catch((error) => {
  process.stderr.write(`probe failed: ${error.message}\n`);
  process.exit(2);
});
