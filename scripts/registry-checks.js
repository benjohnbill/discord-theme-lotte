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
