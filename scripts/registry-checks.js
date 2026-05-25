export function checkSelectorsScreens(selectorsDoc, screensDoc) {
  const selectors = selectorsDoc?.selectors ?? {};
  const knownScreens = new Set(Object.keys(screensDoc?.screens ?? {}));
  const errors = [];

  for (const [name, entry] of Object.entries(selectors)) {
    if (!knownScreens.has(entry.screen)) {
      errors.push(`${name}: unknown screen "${entry.screen}"`);
    }
  }

  return errors;
}

export function checkSelectorsCssOwners(selectorsDoc, manifest) {
  const selectors = selectorsDoc?.selectors ?? {};
  const partials = new Set(manifest?.partials ?? []);
  const errors = [];

  for (const [name, entry] of Object.entries(selectors)) {
    if (!partials.has(entry.cssOwner)) {
      errors.push(`${name}: cssOwner "${entry.cssOwner}" not listed in theme.manifest.yaml partials`);
    }
  }

  return errors;
}

export function checkSelectorsDoNotTouch(selectorsDoc, doNotTouchDoc) {
  const selectors = selectorsDoc?.selectors ?? {};
  const known = new Set(Object.keys(doNotTouchDoc?.selectors ?? {}));
  const errors = [];

  for (const [name, entry] of Object.entries(selectors)) {
    for (const reference of entry.doNotTouch ?? []) {
      if (!known.has(reference)) {
        errors.push(`${name}: doNotTouch entry "${reference}" not declared in do-not-touch.yaml`);
      }
    }
  }

  return errors;
}

export function checkScreensOwns(screensDoc, manifest) {
  const screens = screensDoc?.screens ?? {};
  const partials = new Set(manifest?.partials ?? []);
  const errors = [];

  for (const [name, entry] of Object.entries(screens)) {
    for (const owned of entry.owns ?? []) {
      if (!partials.has(owned)) {
        errors.push(`${name}: owns "${owned}" not listed in theme.manifest.yaml partials`);
      }
    }
  }

  return errors;
}

export function checkScreensLatestSnapshot(screensDoc, exists) {
  const screens = screensDoc?.screens ?? {};
  const errors = [];

  for (const [name, entry] of Object.entries(screens)) {
    if (typeof entry.latestSnapshot !== "string") continue;
    if (!exists(entry.latestSnapshot)) {
      errors.push(`${name}: latestSnapshot "${entry.latestSnapshot}" does not exist on disk`);
    }
  }

  return errors;
}

export function checkSnapshotsScreens(snapshots, screensDoc) {
  const known = new Set(Object.keys(screensDoc?.screens ?? {}));
  const errors = [];

  for (const { path: snapshotPath, data } of snapshots) {
    if (!known.has(data?.screen)) {
      errors.push(`${snapshotPath}: unknown screen "${data?.screen}"`);
    }
  }

  return errors;
}
