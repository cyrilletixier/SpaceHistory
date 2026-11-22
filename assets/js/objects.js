import {
  loadDataset,
  loadManifest,
  setSyncDate,
  parseGcatDate,
  fmtInt,
  get,
  debounce,
  distinctValues,
  fillSelect,
  renderPager,
  showError,
} from './gcat.js';

const PAGE_SIZES = [50, 100, 250, 500];

const state = {
  query: '',
  yearMin: '',
  yearMax: '',
  category: '',
  klass: '',
  stateCode: '',
  sort: 'date',
  direction: -1,
  page: 1,
  pageSize: 100,
};

let objects = [];
let filtered = [];

const nodes = {
  tableWrap: document.getElementById('table-wrap'),
  tbody: document.getElementById('tbody'),
  pager: document.getElementById('pager'),
  count: document.getElementById('count'),
  rowsInfo: document.getElementById('rows-info'),
  empty: document.getElementById('empty'),
};

function build(dataset) {
  const c = {
    name: dataset.col('Name', 'PLName'),
    date: dataset.col('LDate', 'Launch_Date', 'LDate_UTC'),
    klass: dataset.col('Class'),
    category: dataset.col('Category', 'Dest', 'OpOrbit'),
    stateCode: dataset.col('UNState', 'State', 'Owner'),
    program: dataset.col('Program', 'Programme'),
    jcat: dataset.col('JCAT', 'Satcat'),
    owner: dataset.col('Owner'),
  };

  const rows = dataset.rows.map((row) => {
    const parsed = parseGcatDate(get(row, c.date));
    const name = get(row, c.name);
    return {
      name,
      dateLabel: parsed.label,
      dateKey: parsed.key,
      year: parsed.year,
      klass: get(row, c.klass),
      category: get(row, c.category),
      stateCode: get(row, c.stateCode),
      program: get(row, c.program),
      jcat: get(row, c.jcat),
      owner: get(row, c.owner),
      searchIndex: `${name} ${get(row, c.program)} ${get(row, c.jcat)} ${name ? '' : 'sans nom'}`.toLowerCase(),
    };
  });

  return { rows, columns: c };
}

function matches(entry) {
  if (state.query && !entry.searchIndex.includes(state.query.toLowerCase())) return false;
  if (state.yearMin && (!entry.year || entry.year < Number(state.yearMin))) return false;
  if (state.yearMax && (!entry.year || entry.year > Number(state.yearMax))) return false;
  if (state.category && entry.category !== state.category) return false;
  if (state.klass && entry.klass !== state.klass) return false;
  if (state.stateCode && entry.stateCode !== state.stateCode) return false;
  return true;
}

function sortRows() {
  const { sort, direction } = state;
  filtered.sort((a, b) => {
    switch (sort) {
      case 'name':
        return a.name.localeCompare(b.name, 'fr') * direction;
      case 'klass':
        return a.klass.localeCompare(b.klass, 'fr') * direction;
      case 'category':
        return a.category.localeCompare(b.category, 'fr') * direction;
      case 'stateCode':
        return a.stateCode.localeCompare(b.stateCode, 'fr') * direction;
      case 'date':
      default:
        return a.dateKey.localeCompare(b.dateKey) * direction;
    }
  });
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function render() {
  filtered = objects.filter(matches);
  sortRows();

  const total = filtered.length;
  const pages = Math.max(1, Math.ceil(total / state.pageSize));
  if (state.page > pages) state.page = pages;

  const start = (state.page - 1) * state.pageSize;
  const slice = filtered.slice(start, start + state.pageSize);

  const fragment = document.createDocumentFragment();
  for (const entry of slice) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="mono">${entry.dateLabel}</td>
      <td class="key name">${escapeHtml(entry.name) || '<span class="dim">—</span>'}</td>
      <td class="muted">${escapeHtml(entry.klass) || '—'}</td>
      <td class="muted">${escapeHtml(entry.category) || '—'}</td>
      <td class="muted">${escapeHtml(entry.stateCode) || '—'}</td>
      <td class="muted">${escapeHtml(entry.program) || '—'}</td>
      <td class="mono muted">${escapeHtml(entry.jcat) || '—'}</td>
    `;
    fragment.append(tr);
  }

  nodes.tbody.innerHTML = '';
  nodes.tbody.append(fragment);

  nodes.count.textContent = `${fmtInt(total)} objet${total > 1 ? 's' : ''}`;
  nodes.rowsInfo.textContent = total
    ? `lignes ${fmtInt(start + 1)}–${fmtInt(Math.min(start + state.pageSize, total))} sur ${fmtInt(total)}`
    : '';

  renderPager(nodes.pager, {
    page: state.page,
    pageSize: state.pageSize,
    total,
    onPage: (page) => {
      state.page = page;
      render();
      nodes.tableWrap.scrollIntoView({ block: 'start', behavior: 'smooth' });
    },
  });
}

function bindControls() {
  const query = document.getElementById('f-query');
  const yearMin = document.getElementById('f-year-min');
  const yearMax = document.getElementById('f-year-max');
  const category = document.getElementById('f-category');
  const klass = document.getElementById('f-class');
  const stateCode = document.getElementById('f-state');
  const pageSize = document.getElementById('page-size');
  const reset = document.getElementById('f-reset');

  query?.addEventListener(
    'input',
    debounce((event) => {
      state.query = event.target.value.trim();
      state.page = 1;
      render();
    })
  );

  const onYear = debounce(() => {
    state.yearMin = yearMin?.value.trim() ?? '';
    state.yearMax = yearMax?.value.trim() ?? '';
    state.page = 1;
    render();
  });
  yearMin?.addEventListener('input', onYear);
  yearMax?.addEventListener('input', onYear);

  category?.addEventListener('change', () => {
    state.category = category.value;
    state.page = 1;
    render();
  });

  klass?.addEventListener('change', () => {
    state.klass = klass.value;
    state.page = 1;
    render();
  });

  stateCode?.addEventListener('change', () => {
    state.stateCode = stateCode.value;
    state.page = 1;
    render();
  });

  pageSize?.addEventListener('change', () => {
    state.pageSize = Number(pageSize.value) || 100;
    state.page = 1;
    render();
  });

  reset?.addEventListener('click', () => {
    state.query = '';
    state.yearMin = '';
    state.yearMax = '';
    state.category = '';
    state.klass = '';
    state.stateCode = '';
    state.page = 1;
    if (query) query.value = '';
    if (yearMin) yearMin.value = '';
    if (yearMax) yearMax.value = '';
    if (category) category.value = '';
    if (klass) klass.value = '';
    if (stateCode) stateCode.value = '';
    render();
  });

  for (const button of document.querySelectorAll('[data-sort]')) {
    button.addEventListener('click', () => {
      const key = button.dataset.sort;
      if (state.sort === key) state.direction *= -1;
      else {
        state.sort = key;
        state.direction = key === 'date' ? -1 : 1;
      }
      state.page = 1;
      for (const other of document.querySelectorAll('[data-sort]')) {
        other.closest('th')?.removeAttribute('aria-sort');
      }
      button.closest('th')?.setAttribute('aria-sort', state.direction === 1 ? 'ascending' : 'descending');
      render();
    });
  }
}

async function init() {
  setSyncDate(await loadManifest());
  bindControls();

  const pageSizeSelect = document.getElementById('page-size');
  if (pageSizeSelect) {
    pageSizeSelect.innerHTML = '';
    for (const size of PAGE_SIZES) pageSizeSelect.append(new Option(size, String(size), false, size === state.pageSize));
  }

  const dataset = await loadDataset(['psatcat.tsv', 'satcat.tsv']);

  if (!dataset) {
    nodes.tableWrap.hidden = true;
    nodes.empty.hidden = false;
    showError(
      nodes.empty,
      'Les fichiers <code>data/gcat/psatcat.tsv</code> et <code>satcat.tsv</code> sont absents. Lancez le workflow <strong>Update GCAT data</strong> (onglet Actions) ou <code>python3 scripts/fetch_gcat.py</code> en local.'
    );
    return;
  }

  const built = build(dataset);
  objects = built.rows;

  document.getElementById('ds-file').textContent = dataset.file;
  document.getElementById('ds-rows').textContent = fmtInt(dataset.rows);

  fillSelect(document.getElementById('f-category'), distinctValues(dataset.rows, built.columns.category));
  fillSelect(document.getElementById('f-class'), distinctValues(dataset.rows, built.columns.klass));
  fillSelect(document.getElementById('f-state'), distinctValues(dataset.rows, built.columns.stateCode));

  render();
}

init();
