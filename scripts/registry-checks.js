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
