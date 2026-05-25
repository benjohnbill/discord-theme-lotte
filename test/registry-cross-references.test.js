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
