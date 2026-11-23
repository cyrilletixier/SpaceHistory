/* Catalogue des charges utiles.
   Lit data/charges-utiles.json : une entrée par charge utile — `satcat.tsv`
   pour les objets catalogués en orbite, `ftocat.tsv` pour les charges perdues
   lors d'un échec. `?vol=<Launch_Tag>` restreint la vue à un lancement : c'est
   la cible du lien de la colonne « charges utiles » de l'explorateur. */

const fmt = new Intl.NumberFormat('fr-FR');

const state = {
  q: '', vol: '', orbit: '', yMin: null, yMax: null, status: '',
  sort: 'year', dir: -1, page: 1, pageSize: 50,
};

let payloads = [];
let view = [];

const $ = (id) => document.getElementById(id);

const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[char]));

function sortValue(item, key) {
  switch (key) {
    case 'vol': return (item.t || '').toLowerCase();
    case 'year': return item.y || 0;
    case 'mass': return item.m || -1;
    case 'orbit': return (item.o || '').toLowerCase();
    case 'owner': return (item.ow || '').toLowerCase();
    case 'status': return item.f ? 'échec' : 'en orbite';
    default: return (item.n || '').toLowerCase();
  }
}

function matches(item) {
  if (state.yMin && (!item.y || item.y < state.yMin)) return false;
  if (state.yMax && (!item.y || item.y > state.yMax)) return false;
  if (state.orbit && item.o !== state.orbit) return false;
  if (state.status === 'orbite' && item.f) return false;
  if (state.status === 'echec' && !item.f) return false;

  if (state.vol) {
    const needle = state.vol.trim().toLowerCase();
    if (needle && !(item.t || '').toLowerCase().includes(needle)) return false;
  }

  if (state.q) {
    const needle = state.q.trim().toLowerCase();
    if (needle) {
      const haystack = `${item.n} ${item.t} ${item.ow}`.toLowerCase();
      if (!haystack.includes(needle)) return false;
    }
  }

  return true;
}

/* Bandeau de rappel : d'où l'on vient, et comment revenir à tout le catalogue. */
function renderBanner() {
  const banner = $('vol-banner');
  if (!banner) return;

  if (!state.vol) {
    banner.hidden = true;
    banner.innerHTML = '';
    return;
  }

  banner.hidden = false;
  banner.innerHTML = 'Vol filtré : <span class="pill mono">' + esc(state.vol) + '</span>'
    + ' — <a href="launches.html">explorateur des lancements</a>'
    + ' · <a href="charges-utiles.html">voir tous les vols</a>';
}

function apply() {
  view = payloads.filter(matches);
  const key = state.sort;

  view.sort((a, b) => {
    const left = sortValue(a, key);
    const right = sortValue(b, key);
    if (left < right) return -state.dir;
    if (left > right) return state.dir;
    return (a.n || '').localeCompare(b.n || '', 'fr');
  });

  const pages = Math.max(1, Math.ceil(view.length / state.pageSize));
  if (state.page > pages) state.page = pages;
  renderBanner();
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
      <td class="name">${esc(item.n) || '<span class="dim">sans nom</span>'}</td>
      <td><a class="pill mono" href="charges-utiles.html?vol=${encodeURIComponent(item.t)}"
             title="Voir les charges utiles de ce vol">${esc(item.t)}</a></td>
      <td class="num">${item.y ? fmt.format(item.y) : '<span class="dim">—</span>'}</td>
      <td class="num">${item.m ? `${fmt.format(item.m)}\u00a0kg` : '<span class="dim">—</span>'}</td>
      <td${item.r ? ` title="Code GCAT : ${esc(item.r)}"` : ''}>${esc(item.o) || '<span class="dim">—</span>'}</td>
      <td class="dim">${esc(item.ow) || '—'}</td>
      <td>${item.f ? '<span class="pill ko">échec</span>' : '<span class="pill ok">en orbite</span>'}</td>
    </tr>`).join('');

  $('count').textContent = `${fmt.format(view.length)} charge${view.length > 1 ? 's' : ''} utile${view.length > 1 ? 's' : ''}`;
  $('rows-info').textContent = view.length
    ? `${fmt.format(start + 1)}–${fmt.format(Math.min(start + state.pageSize, view.length))} sur ${fmt.format(view.length)}`
    : '';

  const empty = $('empty');
  if (view.length) {
    empty.hidden = true;
    empty.innerHTML = '';
  } else {
    empty.hidden = false;
    empty.innerHTML = '<h2>Aucune charge utile</h2><p>Aucun enregistrement ne correspond à ces filtres.</p>';
  }

  renderPager();
}

function fillControls() {
  const orbits = [...new Set(payloads.map((item) => item.o).filter(Boolean))]
    .sort((a, b) => a.localeCompare(b, 'fr'));
  const select = $('f-orbit');
  for (const orbit of orbits) select.append(new Option(orbit, orbit));
}

function bind() {
  $('f-query').addEventListener('input', (event) => {
    state.q = event.target.value;
    state.page = 1;
    apply();
  });

  $('f-vol').addEventListener('input', (event) => {
    state.vol = event.target.value;
    state.page = 1;
    apply();
  });

  $('f-orbit').addEventListener('change', (event) => {
    state.orbit = event.target.value;
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
      q: '', vol: '', orbit: '', yMin: null, yMax: null, status: '', page: 1,
    });
    $('f-query').value = '';
    $('f-vol').value = '';
    $('f-orbit').value = '';
    $('f-year-min').value = '';
    $('f-year-max').value = '';
    $('f-status').value = '';
    apply();
  });

  for (const button of document.querySelectorAll('[data-sort]')) {
    button.addEventListener('click', () => {
      const key = button.dataset.sort;
      if (state.sort === key) state.dir = -state.dir;
      else {
        state.sort = key;
        state.dir = ['year', 'mass'].includes(key) ? -1 : 1;
      }
      state.page = 1;
      apply();
    });
  }
}

async function boot() {
  /* `?vol=` : le vol transmis par l'explorateur des lancements. */
  const params = new URLSearchParams(window.location.search);
  const vol = (params.get('vol') || '').trim();
  if (vol) {
    state.vol = vol;
    $('f-vol').value = vol;
  }

  try {
    const response = await fetch('data/charges-utiles.json', { cache: 'no-cache' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const payload = await response.json();
    payloads = payload.payloads || [];

    fillControls();
    bind();
    apply();
  } catch (error) {
    $('count').textContent = 'indisponible';
    const empty = $('empty');
    empty.hidden = false;
    empty.innerHTML = '<h2>Données indisponibles</h2><p>Le fichier <code>data/charges-utiles.json</code> n\'a pas pu être chargé.</p>';
  }
}

boot();
