export function gatherProbeClasses(screen, screensDoc, selectorsDoc) {
  const screens = screensDoc?.screens ?? {};
  if (!(screen in screens)) {
    throw new Error(`unknown screen "${screen}"`);
  }

  const items = [];

  for (const className of screens[screen].importantSelectors ?? []) {
    items.push({ class: className, source: `screens.${screen}.importantSelectors` });
  }

  const selectors = selectorsDoc?.selectors ?? {};
  for (const [name, entry] of Object.entries(selectors)) {
    if (entry.screen !== screen) continue;
    for (const className of entry.classes ?? []) {
      items.push({ class: className, source: `selectors.${name}.classes` });
    }
  }

  return items;
}

export function summarizeProbeResults(results) {
  const present = [];
  const missing = [];
  const counts = new Map();

  for (const { class: className, count } of results) {
    counts.set(className, count ?? 0);
    if ((count ?? 0) > 0) present.push(className);
    else missing.push(className);
  }

  return { present, missing, counts };
}

function buildProbeExpression(classNames) {
  return `(function(classes) {
  const out = {};
  for (const c of classes) {
    out[c] = document.querySelectorAll('.' + c).length;
  }
  return out;
})(${JSON.stringify(classNames)})`;
}

export async function probeScreen({ screen, screensDoc, selectorsDoc, cdpClient }) {
  const items = gatherProbeClasses(screen, screensDoc, selectorsDoc);
  if (items.length === 0) {
    throw new Error(`no classes registered for screen "${screen}"`);
  }

  const uniqueClasses = [...new Set(items.map((i) => i.class))];
  const expression = buildProbeExpression(uniqueClasses);
  const countsByClass = await cdpClient.evaluate(expression);

  const results = items.map((item) => ({
    class: item.class,
    source: item.source,
    count: countsByClass?.[item.class] ?? 0
  }));

  const summary = summarizeProbeResults(results);

  return {
    screen,
    probedAt: new Date().toISOString(),
    results,
    present: summary.present,
    missing: summary.missing
  };
}
