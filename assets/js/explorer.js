/* Explorateur des lancements.
   Ne lit plus les TSV : data/launches.json contient une entrée par lancement,
   déjà agrégée au build par Launch_Tag. Le navigateur ne filtre, trie et pagine. */

const fmt = new Intl.NumberFormat('fr-FR');

const state = {
  q: '', yMin: null, yMax: null, launcher: '', site: '',
  status: '', sort: 'date', dir: -1, page: 1, pageSize: 50,
};

let launches = [];
let view = [];

const $ = (id) => document.getElementById(id);

const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[char]));

function sortValue(item, key) {
  switch (key) {
    case 'tag': return item.t.toLowerCase();
    case 'launcher': return (item.lv || '').toLowerCase();
    case 'site': return (item.s || '').toLowerCase();
    case 'agency': return (item.a || '').toLowerCase();
    case 'objects': return item.o;
    case 'status': return item.st;
    default: return item.k;
  }
}

function matches(item) {
  if (state.yMin && (!item.y || item.y < state.yMin)) return false;
  if (state.yMax && (!item.y || item.y > state.yMax)) return false;
  if (state.site && item.s !== state.site) return false;
  if (state.status && item.st !== state.status) return false;

  if (state.launcher) {
    const needle = state.launcher.trim().toLowerCase();
    if (needle && !(item.lv || '').toLowerCase().includes(needle)) return false;
  }

  if (state.q) {
    const needle = state.q.trim().toLowerCase();
    if (needle) {
      const haystack = `${item.t} ${item.lv} ${item.s} ${item.a} ${item.n}`.toLowerCase();
      if (!haystack.includes(needle)) return false;
    }
  }

  return true;
}

function apply() {
  view = launches.filter(matches);
  const key = state.sort;

  view.sort((a, b) => {
    const left = sortValue(a, key);
    const right = sortValue(b, key);
    if (left < right) return -state.dir;
    if (left > right) return state.dir;
    return a.k < b.k ? -1 : 1;
  });

  const pages = Math.max(1, Math.ceil(view.length / state.pageSize));
  if (state.page > pages) state.page = pages;
  render();
}

function renderPager() {
  const nav = $('pager');
  if (!nav) return;
  const pages = Math.max(1, Math.ceil(view.length / state.pageSize));
  nav.innerHTML = '';

  const add = (label, target, options = {}) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `pg${options.active ? ' is-active' : ''}${options.dots ? ' dots' : ''}`;
    button.textContent = label;
    if (options.active) button.setAttribute('aria-current', 'page');
    if (options.disabled || options.dots) button.disabled = true;
    else {
      button.addEventListener('click', () => {
        state.page = target;
        render();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }
    nav.append(button);
  };

  add('‹', state.page - 1, { disabled: state.page <= 1 });

  const size = 7;
  let start = Math.max(1, state.page - Math.floor(size / 2));
  let end = Math.min(pages, start + size - 1);
  start = Math.max(1, end - size + 1);

  if (start > 1) {
    add('1', 1);
    if (start > 2) add('…', state.page, { dots: true });
  }
  for (let index = start; index <= end; index += 1) {
    add(String(index), index, { active: index === state.page });
  }
  if (end < pages) {
    if (end < pages - 1) add('…', state.page, { dots: true });
    add(String(pages), pages);
  }

  add('›', state.page + 1, { disabled: state.page >= pages });
}

function render() {
  const tbody = $('tbody');
  const start = (state.page - 1) * state.pageSize;
  const slice = view.slice(start, start + state.pageSize);

  tbody.innerHTML = slice.map((item) => `
    <tr>
      <td class="mono">${esc(item.d)}</td>
      <td>${esc(item.t)}</td>
      <td>${esc(item.lv) || '—'}</td>
      <td>${esc(item.s) || '—'}</td>
      <td class="dim">${esc(item.a) || '—'}</td>
      <td class="num">${fmt.format(item.o)}</td>
      <td class="dim">${esc(item.n) || '—'}</td>
      <td>${esc(item.st)}${item.c ? ` <span class="mono dim">${esc(item.c)}</span>` : ''}</td>
    </tr>`).join('');

  $('count').textContent = `${fmt.format(view.length)} lancement${view.length > 1 ? 's' : ''}`;
  $('rows-info').textContent = view.length
    ? `${fmt.format(start + 1)}–${fmt.format(Math.min(start + state.pageSize, view.length))} sur ${fmt.format(view.length)}`
    : '';

  const empty = $('empty');
  if (view.length) {
    empty.hidden = true;
    empty.innerHTML = '';
  } else {
    empty.hidden = false;
    empty.innerHTML = '<h2>Aucun lancement</h2><p>Aucun enregistrement ne correspond à ces filtres.</p>';
  }

  renderPager();
}

function fillControls() {
  const launchers = [...new Set(launches.map((item) => item.lv).filter(Boolean))]
    .sort((a, b) => a.localeCompare(b, 'fr'));
  const datalist = $('launcher-list');
  datalist.innerHTML = '';
  for (const launcher of launchers) {
    const option = document.createElement('option');
    option.value = launcher;
    datalist.append(option);
  }

  const sites = [...new Set(launches.map((item) => item.s).filter(Boolean))]
    .sort((a, b) => a.localeCompare(b, 'fr'));
  const select = $('f-site');
  for (const site of sites) select.append(new Option(site, site));
}

function bind() {
  $('f-query').addEventListener('input', (event) => {
    state.q = event.target.value;
    state.page = 1;
    apply();
  });

  $('f-year-min').addEventListener('input', (event) => {
    state.yMin = Number(event.target.value) || null;
    state.page = 1;
    apply();
  });

  $('f-year-max').addEventListener('input', (event) => {
    state.yMax = Number(event.target.value) || null;
    state.page = 1;
    apply();
  });

  $('f-launcher').addEventListener('input', (event) => {
    state.launcher = event.target.value;
    state.page = 1;
    apply();
  });

  $('f-site').addEventListener('change', (event) => {
    state.site = event.target.value;
    state.page = 1;
    apply();
  });

  $('f-status').addEventListener('change', (event) => {
    state.status = event.target.value;
    state.page = 1;
    apply();
  });

  $('page-size').addEventListener('change', (event) => {
    state.pageSize = Number(event.target.value) || 50;
    state.page = 1;
    apply();
  });

  $('f-reset').addEventListener('click', () => {
    Object.assign(state, {
      q: '', yMin: null, yMax: null, launcher: '', site: '', status: '', page: 1,
    });
    $('f-query').value = '';
    $('f-year-min').value = '';
    $('f-year-max').value = '';
    $('f-launcher').value = '';
    $('f-site').value = '';
    $('f-status').value = '';
    apply();
  });

  for (const button of document.querySelectorAll('[data-sort]')) {
    button.addEventListener('click', () => {
      const key = button.dataset.sort;
      if (state.sort === key) state.dir = -state.dir;
      else {
        state.sort = key;
        state.dir = key === 'objects' ? -1 : (key === 'date' ? -1 : 1);
      }
      state.page = 1;
      apply();
    });
  }
}

async function boot() {
  try {
    const response = await fetch('data/launches.json', { cache: 'no-cache' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const payload = await response.json();
    launches = payload.launches || [];
    $('ds-rows')?.replaceChildren(document.createTextNode(fmt.format(payload.source_rows || 0)));

    fillControls();
    bind();
    apply();
  } catch (error) {
    $('count').textContent = 'indisponible';
    const empty = $('empty');
    empty.hidden = false;
    empty.innerHTML = '<h2>Données indisponibles</h2><p>Le fichier <code>data/launches.json</code> n\'a pas pu être chargé.</p>';
  }
}

boot();
