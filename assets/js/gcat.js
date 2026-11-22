/* Utilitaires partagés : lecture des TSV GCAT, dates, filtres, pagination.
   Aucune dépendance externe — les fichiers sont lus tels quels depuis data/gcat/. */

const IDENT = /^#?[A-Za-z][A-Za-z0-9_.\-]*$/;

const MONTHS = {
  jan: '01', feb: '02', mar: '03', apr: '04', may: '05', jun: '06',
  jul: '07', aug: '08', sep: '09', oct: '10', nov: '11', dec: '12',
};

const numberFormat = new Intl.NumberFormat('fr-FR');

export const fmtInt = (n) => numberFormat.format(n);

export function debounce(fn, delay = 220) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

/** Valeur d'une cellule, tolérante à un index absent (-1). */
export function get(row, index) {
  return index >= 0 && index < row.length ? row[index] : '';
}

function splitCells(line) {
  return line.replace(/^#\s?/, '').split('\t').map((cell) => cell.trim());
}

/**
 * Parse un TSV du GCAT : commentaires '#', ligne d'en-tête tabulée, puis données.
 * L'en-tête est la première ligne tabulée dont toutes les cellules sont des
 * identifiants. Les lignes de longueur différente sont complétées ou tronquées.
 */
export function parseGcatTsv(text) {
  const lines = text.split(/\r?\n/);
  let columns = null;
  let start = 0;

  for (let i = 0; i < Math.min(lines.length, 400); i += 1) {
    const line = lines[i];
    if (!line || line.indexOf('\t') === -1) continue;
    const cells = splitCells(line);
    if (cells.length >= 3 && cells.every((value) => IDENT.test(value))) {
      columns = cells;
      start = i + 1;
      break;
    }
  }

  if (!columns) throw new Error('En-tête TSV introuvable');

  const width = columns.length;
  const rows = [];

  for (let i = start; i < lines.length; i += 1) {
    const line = lines[i];
    if (!line) continue;
    if (line.startsWith('#') && line.indexOf('\t') === -1) continue; // commentaire
    const cells = splitCells(line);
    if (cells.length < 2) continue;
    if (cells.length < width) while (cells.length < width) cells.push('');
    else if (cells.length > width) cells.length = width;
    rows.push(cells);
  }

  const exact = new Map(columns.map((name, i) => [name, i]));
  const lower = new Map(columns.map((name, i) => [name.toLowerCase(), i]));

  return {
    columns,
    rows,
    /** Retourne l'index de la première colonne trouvée parmi les alias. */
    col(...aliases) {
      for (const alias of aliases) {
        if (exact.has(alias)) return exact.get(alias);
        const candidate = lower.get(String(alias).toLowerCase());
        if (candidate !== undefined) return candidate;
      }
      return -1;
    },
  };
}

/**
 * Charge le premier fichier disponible parmi une liste de noms.
 * Retourne null si aucun n'est présent (données pas encore récupérées).
 */
export async function loadDataset(names) {
  const candidates = Array.isArray(names) ? names : [names];

  for (const name of candidates) {
    try {
      const response = await fetch(`data/gcat/${name}`, { cache: 'no-cache' });
      if (!response.ok) continue;
      const text = await response.text();
      if (!text || text.trimStart().startsWith('<')) continue; // page d'erreur HTML
      const dataset = parseGcatTsv(text);
      dataset.file = name;
      return dataset;
    } catch (error) {
      // fichier absent ou illisible : on essaie le suivant
    }
  }

  return null;
}

/** Manifeste produit par scripts/fetch_gcat.py (peut être absent). */
export async function loadManifest() {
  try {
    const response = await fetch('data/gcat/MANIFEST.json', { cache: 'no-cache' });
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    return null;
  }
}

/** Affiche la date de synchronisation dans le pied de page si l'élément existe. */
export function setSyncDate(manifest) {
  const element = document.getElementById('sync-date');
  if (!element) return;
  if (!manifest || !manifest.generated_at) {
    element.textContent = 'non synchronisé';
    return;
  }
  const date = new Date(manifest.generated_at);
  element.textContent = Number.isNaN(date.getTime())
    ? manifest.generated_at
    : date.toLocaleString('fr-FR', { dateStyle: 'medium', timeStyle: 'short' });
}

/**
 * Analyse une date GCAT (`1957 Oct  4 1928:07`, `2026 Mar ??`, …).
 * Ne devine jamais une valeur manquante : les composantes absentes restent '00'.
 */
export function parseGcatDate(raw) {
  const source = String(raw ?? '').trim();

  if (!source || source === '-' || source === '?') {
    return { year: null, label: '—', key: '99999999' };
  }

  const match = /^(\d{4})(?:\s+([A-Za-z]{3}))?(?:\s+(\d{1,2}))?(?:\s+(\d{2})(\d{2}):(\d{2}))?/.exec(source);

  if (!match) {
    return { year: null, label: source, key: '99999999' };
  }

  const year = match[1];
  const month = match[2] ? MONTHS[match[2].toLowerCase()] || '00' : '00';
  const day = match[3] ? String(match[3]).padStart(2, '0') : '00';
  const hours = match[4] || '';
  const minutes = match[5] || '';
  const seconds = match[6] || '';

  const time = hours ? ` ${hours}:${minutes}` : '';

  return {
    year: Number(year),
    label: `${year}-${month}-${day}${time}`,
    key: `${year}${month}${day}${hours}${minutes}${seconds}`,
  };
}

/** Valeurs distinctes triées d'une colonne, sans vides. */
export function distinctValues(rows, index) {
  if (index < 0) return [];
  const values = new Set();
  for (const row of rows) {
    const value = row[index];
    if (value) values.add(value);
  }
  return [...values].sort((a, b) => a.localeCompare(b, 'fr'));
}

/** Remplit un <select> avec des valeurs distinctes. */
export function fillSelect(select, values, label = 'tous') {
  if (!select) return;
  select.innerHTML = '';
  select.append(new Option(label, ''));
  for (const value of values) select.append(new Option(value, value));
}

/** Remplit un <datalist> avec des valeurs distinctes. */
export function fillDatalist(datalist, values) {
  if (!datalist) return;
  datalist.innerHTML = '';
  for (const value of values) {
    const option = document.createElement('option');
    option.value = value;
    datalist.append(option);
  }
}

/** Pagination : ‹ 1 … 4 5 6 … 42 › */
export function renderPager(container, { page, pageSize, total, onPage }) {
  if (!container) return;

  const pages = Math.max(1, Math.ceil(total / pageSize));
  const current = Math.min(Math.max(1, page), pages);
  container.innerHTML = '';

  const button = (label, target, options = {}) => {
    const element = document.createElement('button');
    element.type = 'button';
    element.className = `pg${options.active ? ' is-active' : ''}${options.dots ? ' dots' : ''}`;
    element.textContent = label;
    if (options.active) element.setAttribute('aria-current', 'page');
    if (options.disabled || options.dots) element.disabled = true;
    else element.addEventListener('click', () => onPage(target));
    return element;
  };

  container.append(button('‹', current - 1, { disabled: current <= 1 }));

  const windowSize = 7;
  let start = Math.max(1, current - Math.floor(windowSize / 2));
  let end = Math.min(pages, start + windowSize - 1);
  start = Math.max(1, end - windowSize + 1);

  if (start > 1) {
    container.append(button('1', 1));
    if (start > 2) container.append(button('…', current, { dots: true }));
  }

  for (let index = start; index <= end; index += 1) {
    container.append(button(String(index), index, { active: index === current }));
  }

  if (end < pages) {
    if (end < pages - 1) container.append(button('…', current, { dots: true }));
    container.append(button(String(pages), pages));
  }

  container.append(button('›', current + 1, { disabled: current >= pages }));
}

/** Affiche proprement une erreur de chargement. */
export function showError(container, message) {
  if (!container) return;
  container.hidden = false;
  container.innerHTML = `<h2>Chargement impossible</h2><p>${message}</p>`;
}
