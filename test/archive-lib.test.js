import assert from "node:assert/strict";
import test from "node:test";

import {
  appendToArchive,
  buildArchiveEntry,
  removeFromRegistry
} from "../scripts/archive-lib.js";

const originalEntry = {
  screen: "voice-panel",
  classes: ["button__67645"],
  cssOwner: "src/components/voice-panel.css",
  stability: "hashed",
  action: "style primary voice actions",
  reason: "aria labels were not sufficient"
};

test("buildArchiveEntry assembles a complete archive entry from required fields", () => {
  const entry = buildArchiveEntry({
    key: "voice_primary_actions",
    fromFile: "registry/selectors.yaml",
    originalEntry,
    reason: "button__67645 not observed in Discord probe on 2026-08-12",
    archivedAt: "2026-08-12"
  });

  assert.equal(entry.archivedAt, "2026-08-12");
  assert.equal(entry.fromFile, "registry/selectors.yaml");
  assert.equal(entry.key, "voice_primary_actions");
  assert.deepEqual(entry.snapshot, originalEntry);
  assert.equal(entry.reason, "button__67645 not observed in Discord probe on 2026-08-12");
  assert.equal(entry.evidence, undefined);
  assert.equal(entry.replacedBy, undefined);
});

test("buildArchiveEntry includes optional evidence and replacedBy when provided", () => {
  const entry = buildArchiveEntry({
    key: "voice_primary_actions",
    fromFile: "registry/selectors.yaml",
    originalEntry,
    reason: "replaced after Discord 2026-08 redesign",
    archivedAt: "2026-08-12",
    evidence: "snapshots/2026-08-12/voice-panel.json",
    replacedBy: "voice_primary_actions_v2"
  });

  assert.equal(entry.evidence, "snapshots/2026-08-12/voice-panel.json");
  assert.equal(entry.replacedBy, "voice_primary_actions_v2");
});

test("appendToArchive returns a new archive document with the entry appended", () => {
  const archiveDoc = { schemaVersion: 1, entries: [] };
  const entry = buildArchiveEntry({
    key: "k",
    fromFile: "registry/selectors.yaml",
    originalEntry,
    reason: "r",
    archivedAt: "2026-08-12"
  });

  const next = appendToArchive(archiveDoc, entry);
  assert.equal(next.schemaVersion, 1);
  assert.equal(next.entries.length, 1);
  assert.deepEqual(next.entries[0], entry);
});

test("appendToArchive does not mutate the input archive document", () => {
  const archiveDoc = { schemaVersion: 1, entries: [] };
  const entry = buildArchiveEntry({
    key: "k",
    fromFile: "registry/selectors.yaml",
    originalEntry,
    reason: "r",
    archivedAt: "2026-08-12"
  });

  appendToArchive(archiveDoc, entry);
  assert.equal(archiveDoc.entries.length, 0);
});

test("removeFromRegistry returns a new registry document with the named entry removed from the named root", () => {
  const registryDoc = {
    schemaVersion: 1,
    selectors: {
      voice_primary_actions: originalEntry,
      friends_page_body: { ...originalEntry, screen: "friends-page" }
    }
  };

  const next = removeFromRegistry(registryDoc, "selectors", "voice_primary_actions");
  assert.equal(next.schemaVersion, 1);
  assert.equal(Object.keys(next.selectors).length, 1);
  assert.ok(!("voice_primary_actions" in next.selectors));
  assert.ok("friends_page_body" in next.selectors);
});

test("removeFromRegistry does not mutate the input registry document", () => {
  const registryDoc = {
    schemaVersion: 1,
    selectors: { voice_primary_actions: originalEntry }
  };

  removeFromRegistry(registryDoc, "selectors", "voice_primary_actions");
  assert.ok("voice_primary_actions" in registryDoc.selectors);
});

test("removeFromRegistry throws when the key is missing", () => {
  const registryDoc = { schemaVersion: 1, selectors: { a: originalEntry } };

  assert.throws(
    () => removeFromRegistry(registryDoc, "selectors", "missing"),
    /key "missing" not found under "selectors"/
  );
});
