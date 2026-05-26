export function buildArchiveEntry({
  key,
  fromFile,
  originalEntry,
  reason,
  archivedAt,
  evidence,
  replacedBy
}) {
  const entry = {
    archivedAt,
    fromFile,
    key,
    snapshot: originalEntry,
    reason
  };

  if (typeof evidence === "string") entry.evidence = evidence;
  if (typeof replacedBy === "string") entry.replacedBy = replacedBy;

  return entry;
}

export function appendToArchive(archiveDoc, entry) {
  const existingEntries = archiveDoc?.entries ?? [];
  return {
    ...archiveDoc,
    schemaVersion: archiveDoc?.schemaVersion ?? 1,
    entries: [...existingEntries, entry]
  };
}

export function removeFromRegistry(registryDoc, rootKey, entryKey) {
  const root = registryDoc?.[rootKey];
  if (!root || !(entryKey in root)) {
    throw new Error(`key "${entryKey}" not found under "${rootKey}"`);
  }

  const nextRoot = { ...root };
  delete nextRoot[entryKey];

  return {
    ...registryDoc,
    [rootKey]: nextRoot
  };
}
