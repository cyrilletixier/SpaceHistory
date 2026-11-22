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
  fillDatalist,
  renderPager,
  showError,
} from './gcat.js';

const PAGE_SIZES = [25, 50, 100, 250];

const state = {
  query: '',
  yearMin: '',
  yearMax: '',
  launcher: '',
  site: '',
  status: '',
  sort: 'date',
  direction: -1,
  page: 1,
  pageSize: 50,
};

let launches = [];
let filtered = [];

const nodes = {
  tableWrap: document.getElementById('table-wrap'),
  tbody: document.getElementById('tbody'),
  pager: document.getElementById('pager'),
  count: document.getElementById('count'),
  rowsInfo: document.getElementById('rows-info'),
  empty: document.getElementById('empty'),
};

const STATUS_LABEL = { succes: 'succès', echec: 'échec', inconnu: 'inconnu' };
const STATUS_CLASS = { succes: 'ok', echec: 'ko', inconnu: '' };

function outcomeOf(entry) {
  const lvStates = [...entry.lvStates];
  const satStates = [...entry.satStates];

  if (lvStates.some((code) => /^OF/i.test(code))) return 'echec';
  if (lvStates.some((code) => /^OS/i.test(code))) return 'succes';
  if (satStates.some((code) => /^OF/i.test(code))) return 'echec';
  if (satStates.some((code) => /^O/i.test(code))) return 'succes';
  return 'inconnu';
}

function aggregate(dataset) {
  const c = {
    tag: dataset.col('Launch_Tag', 'LaunchTag', 'Tag'),
    date: dataset.col('Launch_Date', 'LDate', 'Date'),
    launcher: dataset.col('LV_Type', 'LV', 'Launcher'),
    site: dataset.col('Launch_Site', 'Site', 'Platform'),
    pad: dataset.col('Launch_Pad', 'Pad'),
    agency: dataset.col('Agency', 'State', 'Owner'),
    type: dataset.col('Type'),
    name: dataset.col('Name', 'PLName'),
    satState: dataset.col('SatState', 'Sat_State'),
    lvState: dataset.col('LVState', 'LV_State'),
    orbit: dataset.col('OpOrbit', 'Dest', 'Orbit'),
  };

  const map = new Map();

  for (const row of dataset.rows) {
    const rawDate = get(row, c.date);
    const launcher = get(row, c.launcher);
    const tag = get(row, c.tag) || `${rawDate}|${launcher}`;

    let entry = map.get(tag);
    if (!entry) {
      entry = {
        tag,
        rawDate,
        parsed: parseGcatDate(rawDate),
        launcher,
        site: get(row, c.site),
        pad: get(row, c.pad),
        agency: get(row, c.agency),
        orbit: get(row, c.orbit),
        objects: 0,
        payloads: [],
        lvStates: new Set(),
        satStates: new Set(),
      };
      map.set(tag, entry);
    }

    entry.objects += 1;

    const lvState = get(row, c.lvState);
    if (lvState) entry.lvStates.add(lvState);

    const satState = get(row, c.satState);
    if (satState) entry.satStates.add(satState);

    if (!entry.site) entry.site = get(row, c.site);
    if (!entry.agency) entry.agency = get(row, c.agency);
    if (!entry.orbit) entry.orbit = get(row, c.orbit);

    const type = get(row, c.type);
    const name = get(row, c.name);
    if (name && /^P/i.test(type)) entry.payloads.push(name);
  }

  const result = [...map.values()];
  for (const entry of result) {
    entry.status = outcomeOf(entry);
    entry.code = [...entry.lvStates][0] || [...entry.satStates][0] || '';
    entry.year = entry.parsed.year;
    entry.searchIndex = [
      entry.tag,
      entry.launcher,
      entry.site,
      entry.agency,
      entry.payloads.slice(0, 6).join(' '),
    ]
      .join(' ')
      .toLowerCase();
  }
  return result;
}

function matches(entry) {
  if (state.query && !entry.searchIndex.includes(state.query.toLowerCase())) return false;
  if (state.yearMin && (!entry.year || entry.year < Number(state.yearMin))) return false;
  if (state.yearMax && (!entry.year || entry.year > Number(state.yearMax))) return false;
  if (state.launcher && entry.launcher !== state.launcher) return false;
  if (state.site && entry.site !== state.site) return false;
  if (state.status && entry.status !== state.status) return false;
  return true;
}

function sortEntries() {
  const { sort, direction } = state;
  filtered.sort((a, b) => {
    switch (sort) {
      case 'launcher':
        return a.launcher.localeCompare(b.launcher, 'fr') * direction;
      case 'site':
        return a.site.localeCompare(b.site, 'fr') * direction;
      case 'agency':
        return a.agency.localeCompare(b.agency, 'fr') * direction;
      case 'objects':
        return (a.objects - b.objects) * direction;
      case 'status':
        return a.status.localeCompare(b.status) * direction;
      case 'tag':
        return a.tag.localeCompare(b.tag) * direction;
      case 'date':
      default:
        return a.parsed.key.localeCompare(b.parsed.key) * direction;
    }
  });
}

function render() {
  filtered = launches.filter(matches);
  sortEntries();

  const total = filtered.length;
  const pages = Math.max(1, Math.ceil(total / state.pageSize));
  if (state.page > pages) state.page = pages;

  const start = (state.page - 1) * state.pageSize;
  const slice = filtered.slice(start, start + state.pageSize);

  nodes.tbody.innerHTML = '';
  const fragment = document.createDocumentFragment();

  for (const entry of slice) {
    const tr = document.createElement('tr');

    const payloads = entry.payloads.slice(0, 3).join(', ');
    const extra = entry.payloads.length > 3 ? ` +${entry.payloads.length - 3}` : '';

    tr.innerHTML = `
      <td class="mono">${entry.parsed.label}</td>
      <td class="key">${escapeHtml(entry.tag)}</td>
      <td>${escapeHtml(entry.launcher) || '<span class="dim">—</span>'}</td>
      <td class="muted">${escapeHtml(entry.site) || '—'}</td>
      <td class="muted">${escapeHtml(entry.agency) || '—'}</td>
      <td class="num">${fmtInt(entry.objects)}</td>
      <td class="name muted">${escapeHtml(payloads) || '—'}${extra}</td>
      <td><span class="pill ${STATUS_CLASS[entry.status]}">${STATUS_LABEL[entry.status]}${entry.code ? ` · ${escapeHtml(entry.code)}` : ''}</span></td>
    `;
    fragment.append(tr);
  }

  nodes.tbody.append(fragment);

  nodes.count.textContent = `${fmtInt(total)} lancement${total > 1 ? 's' : ''}`;
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

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function bindControls() {
  const query = document.getElementById('f-query');
  const yearMin = document.getElementById('f-year-min');
  const yearMax = document.getElementById('f-year-max');
  const launcher = document.getElementById('f-launcher');
  const site = document.getElementById('f-site');
  const status = document.getElementById('f-status');
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

  launcher?.addEventListener('input', () => {
    state.launcher = launcher.value.trim();
    state.page = 1;
    render();
  });

  site?.addEventListener('change', () => {
    state.site = site.value;
    state.page = 1;
    render();
  });

  status?.addEventListener('change', () => {
    state.status = status.value;
    state.page = 1;
    render();
  });

  pageSize?.addEventListener('change', () => {
    state.pageSize = Number(pageSize.value) || 50;
    state.page = 1;
    render();
  });

  reset?.addEventListener('click', () => {
    state.query = '';
    state.yearMin = '';
    state.yearMax = '';
    state.launcher = '';
    state.site = '';
    state.status = '';
    state.page = 1;
    if (query) query.value = '';
    if (yearMin) yearMin.value = '';
    if (yearMax) yearMax.value = '';
    if (launcher) launcher.value = '';
    if (site) site.value = '';
    if (status) status.value = '';
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

  const dataset = await loadDataset('launchlog.tsv');

  if (!dataset) {
    nodes.tableWrap.hidden = true;
    nodes.empty.hidden = false;
    showError(
      nodes.empty,
      'Le fichier <code>data/gcat/launchlog.tsv</code> est absent. Lancez le workflow <strong>Update GCAT data</strong> (onglet Actions) ou <code>python3 scripts/fetch_gcat.py</code> en local.'
    );
    return;
  }

  launches = aggregate(dataset);
  document.getElementById('ds-file').textContent = dataset.file;
  document.getElementById('ds-rows').textContent = fmtInt(dataset.rows);
  render();
}

init();
