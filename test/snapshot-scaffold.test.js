import assert from "node:assert/strict";
import test from "node:test";

import { scaffoldSnapshot } from "../scripts/new-snapshot.js";

function makeFsImpl(initial = {}) {
  const store = new Map(Object.entries(initial));
  return {
    existsSync: (filePath) => store.has(filePath),
    mkdirSync: (dirPath) => {
      store.set(`dir:${dirPath}`, "");
    },
    writeFileSync: (filePath, contents) => {
      store.set(filePath, contents);
    },
    readStore: () => store
  };
}

const screensDoc = {
  schemaVersion: 1,
  screens: {
    "friends-page": {
      owns: [],
      importantSelectors: [],
      goals: [],
      knownRisks: []
    }
  }
};

test("scaffoldSnapshot creates a snapshot file at snapshots/<today>/<screen>.json with stub metadata", () => {
  const fsImpl = makeFsImpl();
  const result = scaffoldSnapshot({
    screen: "friends-page",
    today: "2026-06-01",
    root: "/repo",
    fsImpl,
    screensDoc
  });

  assert.equal(result.relativePath, "snapshots/2026-06-01/friends-page.json");
  const written = fsImpl.readStore().get("/repo/snapshots/2026-06-01/friends-page.json");
  assert.ok(typeof written === "string" && written.length > 0, "scaffolded file must have non-empty content");

  const parsed = JSON.parse(written);
  assert.equal(parsed.schemaVersion, 1);
  assert.equal(parsed.screen, "friends-page");
  assert.equal(parsed.routeHint, "replace-with-current-route");
  assert.equal(parsed.sourceScreenshot, "replace-with-screenshot-path");
  assert.equal(parsed.discordBuild, "unknown");
  assert.deepEqual(parsed.elements, []);
  assert.match(parsed.capturedAt, /^2026-06-01/);
});

test("scaffoldSnapshot refuses to overwrite an existing snapshot file", () => {
  const fsImpl = makeFsImpl({
    "/repo/snapshots/2026-06-01/friends-page.json": "{}"
  });

  assert.throws(
    () =>
      scaffoldSnapshot({
        screen: "friends-page",
        today: "2026-06-01",
        root: "/repo",
        fsImpl,
        screensDoc
      }),
    /refusing to overwrite existing file snapshots\/2026-06-01\/friends-page\.json/
  );
});
