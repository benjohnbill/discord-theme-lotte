import assert from "node:assert/strict";
import test from "node:test";

import {
  gatherProbeClasses,
  probeScreen,
  summarizeProbeResults
} from "../scripts/probe-lib.js";

const screensDoc = {
  schemaVersion: 1,
  screens: {
    "voice-panel": {
      owns: ["src/components/voice-panel.css"],
      latestSnapshot: "snapshots/2026-05-25/voice-panel.json",
      importantSelectors: ["panels__5e434", "wrapper_e131a9"],
      goals: [],
      knownRisks: []
    }
  }
};

const selectorsDoc = {
  schemaVersion: 1,
  selectors: {
    voice_primary_actions: {
      screen: "voice-panel",
      classes: ["button__67645", "enabled__67645"],
      cssOwner: "src/components/voice-panel.css",
      stability: "hashed",
      action: "",
      reason: ""
    },
    friends_page_body: {
      screen: "friends-page",
      classes: ["tabBody__133bf"],
      cssOwner: "src/components/friends-dm.css",
      stability: "hashed",
      action: "",
      reason: ""
    }
  }
};

test("gatherProbeClasses returns importantSelectors and matching selector classes for the screen", () => {
  const items = gatherProbeClasses("voice-panel", screensDoc, selectorsDoc);
  const sorted = [...items].sort((a, b) => a.class.localeCompare(b.class));

  assert.deepEqual(sorted, [
    { class: "button__67645", source: "selectors.voice_primary_actions.classes" },
    { class: "enabled__67645", source: "selectors.voice_primary_actions.classes" },
    { class: "panels__5e434", source: "screens.voice-panel.importantSelectors" },
    { class: "wrapper_e131a9", source: "screens.voice-panel.importantSelectors" }
  ]);
});

test("gatherProbeClasses throws when the screen is not in screens.yaml", () => {
  assert.throws(
    () => gatherProbeClasses("ghost", screensDoc, selectorsDoc),
    /unknown screen "ghost"/
  );
});

test("gatherProbeClasses ignores selectors that target other screens", () => {
  const items = gatherProbeClasses("voice-panel", screensDoc, selectorsDoc);
  const classes = items.map((i) => i.class);

  assert.ok(!classes.includes("tabBody__133bf"));
});

test("summarizeProbeResults separates present from missing classes", () => {
  const results = [
    { class: "panels__5e434", source: "x", count: 1 },
    { class: "wrapper_e131a9", source: "x", count: 2 },
    { class: "button__67645", source: "y", count: 0 }
  ];

  const summary = summarizeProbeResults(results);
  assert.deepEqual(summary.present, ["panels__5e434", "wrapper_e131a9"]);
  assert.deepEqual(summary.missing, ["button__67645"]);
  assert.equal(summary.counts.get("panels__5e434"), 1);
  assert.equal(summary.counts.get("button__67645"), 0);
});

test("summarizeProbeResults treats undefined count as missing", () => {
  const results = [{ class: "x", source: "y" }];
  const summary = summarizeProbeResults(results);
  assert.deepEqual(summary.missing, ["x"]);
  assert.deepEqual(summary.present, []);
});

test("probeScreen delegates to the injected cdpClient and assembles per-class results", async () => {
  const seen = { expression: null };
  const cdpClient = {
    async evaluate(expression) {
      seen.expression = expression;
      return {
        panels__5e434: 1,
        wrapper_e131a9: 2,
        button__67645: 0,
        enabled__67645: 0
      };
    }
  };

  const output = await probeScreen({
    screen: "voice-panel",
    screensDoc,
    selectorsDoc,
    cdpClient
  });

  assert.equal(output.screen, "voice-panel");
  assert.ok(Array.isArray(output.results));
  assert.equal(output.results.length, 4);

  const byClass = Object.fromEntries(output.results.map((r) => [r.class, r]));
  assert.equal(byClass.panels__5e434.count, 1);
  assert.equal(byClass.button__67645.count, 0);
  assert.deepEqual(output.missing, ["button__67645", "enabled__67645"]);
  assert.match(seen.expression, /document\.querySelectorAll/);
});

test("probeScreen throws when the screen has no classes registered", async () => {
  const emptyScreens = {
    schemaVersion: 1,
    screens: {
      empty: { owns: [], importantSelectors: [], goals: [], knownRisks: [] }
    }
  };
  const emptySelectors = { schemaVersion: 1, selectors: {} };
  const cdpClient = { async evaluate() { return {}; } };

  await assert.rejects(
    () => probeScreen({ screen: "empty", screensDoc: emptyScreens, selectorsDoc: emptySelectors, cdpClient }),
    /no classes registered for screen "empty"/
  );
});
