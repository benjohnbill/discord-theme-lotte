import assert from "node:assert/strict";
import test from "node:test";

import { checkSelectorsScreens } from "../scripts/registry-checks.js";

const baseSelector = {
  screen: "x",
  classes: ["a"],
  cssOwner: "src/x.css",
  stability: "stable",
  action: "act",
  reason: "because"
};

const baseScreen = {
  owns: [],
  importantSelectors: [],
  goals: [],
  knownRisks: []
};

test("checkSelectorsScreens returns no errors when every selector screen exists", () => {
  const selectorsDoc = { schemaVersion: 1, selectors: { sel_a: baseSelector } };
  const screensDoc = { schemaVersion: 1, screens: { x: baseScreen } };
  assert.deepEqual(checkSelectorsScreens(selectorsDoc, screensDoc), []);
});

test("checkSelectorsScreens reports selectors that reference an unknown screen", () => {
  const selectorsDoc = {
    schemaVersion: 1,
    selectors: { sel_a: { ...baseSelector, screen: "missing" } }
  };
  const screensDoc = { schemaVersion: 1, screens: { x: baseScreen } };
  const errors = checkSelectorsScreens(selectorsDoc, screensDoc);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /sel_a: unknown screen "missing"/);
});

import { checkSelectorsCssOwners } from "../scripts/registry-checks.js";

test("checkSelectorsCssOwners returns no errors when every cssOwner is in manifest.partials", () => {
  const selectorsDoc = {
    schemaVersion: 1,
    selectors: { sel_a: { ...baseSelector, cssOwner: "src/components/a.css" } }
  };
  const manifest = { partials: ["src/components/a.css", "src/components/b.css"] };
  assert.deepEqual(checkSelectorsCssOwners(selectorsDoc, manifest), []);
});

test("checkSelectorsCssOwners reports selectors whose cssOwner is not registered as a manifest partial", () => {
  const selectorsDoc = {
    schemaVersion: 1,
    selectors: { sel_a: { ...baseSelector, cssOwner: "src/components/orphan.css" } }
  };
  const manifest = { partials: ["src/components/a.css"] };
  const errors = checkSelectorsCssOwners(selectorsDoc, manifest);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /sel_a: cssOwner "src\/components\/orphan\.css" not listed in theme\.manifest\.yaml partials/);
});

import { checkSelectorsDoNotTouch } from "../scripts/registry-checks.js";

const baseDoNotTouch = {
  screen: "x",
  reason: "fragile",
  allowedActions: ["inspect"]
};

test("checkSelectorsDoNotTouch returns no errors when doNotTouch references are all known", () => {
  const selectorsDoc = {
    schemaVersion: 1,
    selectors: { sel_a: { ...baseSelector, doNotTouch: ["wrapper_known"] } }
  };
  const doNotTouchDoc = { schemaVersion: 1, selectors: { wrapper_known: baseDoNotTouch } };
  assert.deepEqual(checkSelectorsDoNotTouch(selectorsDoc, doNotTouchDoc), []);
});

test("checkSelectorsDoNotTouch reports selectors with unknown doNotTouch references", () => {
  const selectorsDoc = {
    schemaVersion: 1,
    selectors: { sel_a: { ...baseSelector, doNotTouch: ["wrapper_missing"] } }
  };
  const doNotTouchDoc = { schemaVersion: 1, selectors: { wrapper_known: baseDoNotTouch } };
  const errors = checkSelectorsDoNotTouch(selectorsDoc, doNotTouchDoc);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /sel_a: doNotTouch entry "wrapper_missing" not declared in do-not-touch\.yaml/);
});

test("checkSelectorsDoNotTouch ignores selectors that have no doNotTouch list", () => {
  const selectorsDoc = { schemaVersion: 1, selectors: { sel_a: baseSelector } };
  const doNotTouchDoc = { schemaVersion: 1, selectors: {} };
  assert.deepEqual(checkSelectorsDoNotTouch(selectorsDoc, doNotTouchDoc), []);
});

import { checkScreensOwns } from "../scripts/registry-checks.js";

test("checkScreensOwns returns no errors when every owned path is in manifest.partials", () => {
  const screensDoc = {
    schemaVersion: 1,
    screens: { x: { ...baseScreen, owns: ["src/components/a.css"] } }
  };
  const manifest = { partials: ["src/components/a.css", "src/base/palette.css"] };
  assert.deepEqual(checkScreensOwns(screensDoc, manifest), []);
});

test("checkScreensOwns reports screens that own paths missing from manifest.partials", () => {
  const screensDoc = {
    schemaVersion: 1,
    screens: { x: { ...baseScreen, owns: ["src/components/orphan.css"] } }
  };
  const manifest = { partials: ["src/components/a.css"] };
  const errors = checkScreensOwns(screensDoc, manifest);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /x: owns "src\/components\/orphan\.css" not listed in theme\.manifest\.yaml partials/);
});

import { checkScreensLatestSnapshot } from "../scripts/registry-checks.js";

test("checkScreensLatestSnapshot returns no errors when each latestSnapshot exists according to the predicate", () => {
  const screensDoc = {
    schemaVersion: 1,
    screens: {
      x: { ...baseScreen, latestSnapshot: "snapshots/2026-05-25/x.json" }
    }
  };
  const exists = (relativePath) => relativePath === "snapshots/2026-05-25/x.json";
  assert.deepEqual(checkScreensLatestSnapshot(screensDoc, exists), []);
});

test("checkScreensLatestSnapshot reports screens whose latestSnapshot file is missing", () => {
  const screensDoc = {
    schemaVersion: 1,
    screens: {
      x: { ...baseScreen, latestSnapshot: "snapshots/2026-05-25/missing.json" }
    }
  };
  const exists = () => false;
  const errors = checkScreensLatestSnapshot(screensDoc, exists);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /x: latestSnapshot "snapshots\/2026-05-25\/missing\.json" does not exist on disk/);
});

test("checkScreensLatestSnapshot ignores screens without latestSnapshot", () => {
  const screensDoc = { schemaVersion: 1, screens: { x: baseScreen } };
  const exists = () => false;
  assert.deepEqual(checkScreensLatestSnapshot(screensDoc, exists), []);
});
