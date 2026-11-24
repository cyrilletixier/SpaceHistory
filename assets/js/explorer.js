/* Explorateur des lancements.
   Ne lit plus les TSV : data/launches.json contient une entrée par lancement,
   déjà agrégée au build par Launch_Tag. Le navigateur ne filtre, trie et pagine.
   Les colonnes `s`/`a` portent des libellés lisibles, `sc`/`ac` les codes GCAT,
   `dc` les codes d'orbite bruts derrière le libellé de destination `dd`.

   La colonne « charges utiles » ne liste plus les noms (ils restent dans `n`,
   pour la recherche) : elle renvoie vers charges-utiles.html?vol=<tag>.

   `cr` vaut 1 pour un vol habité. Le marqueur vient du GCAT (2e caractère du
   champ `Type` des charges utiles), pas d'une liste tenue à la main : le build
   l'a déjà agrégé au vol, le navigateur se contente de filtrer et d'afficher.
   Il dispose pour cela de sa propre colonne « Habité », triable, plutôt qu'une
   pastille noyée dans la colonne des missions : un lecteur qui cherche à savoir
   si un tir était habité ne devrait pas avoir à déchiffrer un tag. */

const fmt = new Intl.NumberFormat('fr-FR');

const state = {
  q: '', yMin: null, yMax: null, launcher: '', site: '', destination: '',
  crewed: '', status: '', sort: 'date', dir: -1, page: 1, pageSize: 50,
};

let launches = [];
let view = [];

const $ = (id) => document.getElementById(id);

const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[char]));

/* Familles d'orbite d'un lancement : `dd` peut en contenir plusieurs. */
const destinationsOf = (item) => (item.dd || '').split(' · ').filter(Boolean);

function sortValue(item, key) {
  switch (key) {
    case 'tag': return item.t.toLowerCase();
    case 'launcher': return (item.lv || '').toLowerCase();
    case 'site': return (item.s || '').toLowerCase();
    case 'agency': return (item.a || '').toLowerCase();
    case 'objects': return item.o;
    case 'payloads': return item.pc || 0;
    case 'mass': return item.m || -1;
    case 'destination': return (item.dd || '').toLowerCase();
    case 'crewed': return item.cr || 0;
    case 'status': return item.st;
    default: return item.k;
  }
}

function matches(item) {
  if (state.yMin && (!item.y || item.y < state.yMin)) return false;
  if (state.yMax && (!item.y || item.y > state.yMax)) return false;
  if (state.site && item.s !== state.site) return false;
  if (state.status && item.st !== state.status) return false;
  if (state.destination && !destinationsOf(item).includes(state.destination)) return false;
  if (state.crewed === '1' && !item.cr) return false;
  if (state.crewed === '0' && item.cr) return false;

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

/* Cellule « Habité » : la colonne qui porte l'information, au lieu d'une
   pastille collée au tag de mission. Un vol non habité affiche « — » et non un
   « non » explicite : la colonne est faite pour repérer les vols habités, et
   l'immense majorité des 5 000 lignes ne l'est pas.
   Le survol rappelle d'où vient le marqueur : il est lu dans le catalogue, pas
   saisi à la main — la règle reste donc vérifiable à la source. */
function crewedCell(item) {
  if (!item.cr) return '<span class="dim">—</span>';
  const tip = 'Vol habité — GCAT : 2e caractère du champ Type des charges utiles';
  return `<span class="pill ok" title="${esc(tip)}">habité</span>`;
}

/* Cellule « charges utiles » : compteur cliquable vers la page filtrée.
   Le survol rappelle combien de charges sont cataloguées en orbite. */
function payloadCell(item) {
  if (!item.pc) return '<span class="dim">—</span>';

  const url = `charges-utiles.html?vol=${encodeURIComponent(item.t)}`;
  const tip = item.pi && item.pi !== item.pc
    ? `${fmt.format(item.pi)} en orbite sur ${fmt.format(item.pc)} cataloguée(s) — voir le détail`
    : `${fmt.format(item.pc)} charge(s) utile(s) — voir le détail`;

  return `<a class="pill" href="${url}" title="${esc(tip)}">${fmt.format(item.pc)}</a>`;
}

/* Cellule « masse en orbite » : une somme inconnue s'affiche « — », pas « 0 ». */
function massCell(item) {
  if (!item.m) return '<span class="dim">—</span>';

  const missing = (item.pi || 0) - (item.pm || 0);
  const tip = `somme des masses connues de ${fmt.format(item.pm || 0)} charge(s) utile(s)`
    + (missing > 0 ? ` ; ${fmt.format(missing)} sans masse au catalogue` : '');

  return `<span title="${esc(tip)}">${fmt.format(item.m)}\u00a0kg</span>`;
}

function destinationCell(item) {
  if (!item.dd) return '<span class="dim">—</span>';
  const tip = item.dc ? `codes GCAT : ${item.dc}` : '';
  return `<span${tip ? ` title="${esc(tip)}"` : ''}>${esc(item.dd)}</span>`;
}

function render() {
  const tbody = $('tbody');
  const start = (state.page - 1) * state.pageSize;
  const slice = view.slice(start, start + state.pageSize);

  tbody.innerHTML = slice.map((item) => `
    <tr>
      <td class="mono">${esc(item.d)}</td>
      <td>${esc(item.t)}</td>
      <td>${crewedCell(item)}</td>
      <td>${esc(item.lv) || '—'}</td>
      <td${item.sc ? ` title="Code GCAT : ${esc(item.sc)}"` : ''}>${esc(item.s) || '—'}</td>
      <td class="dim"${item.ac ? ` title="Code GCAT : ${esc(item.ac)}"` : ''}>${esc(item.a) || '—'}</td>
      <td class="num">${fmt.format(item.o)}</td>
      <td class="num">${payloadCell(item)}</td>
      <td class="num">${massCell(item)}</td>
      <td>${destinationCell(item)}</td>
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

  const destinations = [...new Set(launches.flatMap(destinationsOf))]
    .sort((a, b) => a.localeCompare(b, 'fr'));
  const destinationSelect = $('f-destination');
  for (const destination of destinations) {
    destinationSelect.append(new Option(destination, destination));
  }
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

  $('f-destination').addEventListener('change', (event) => {
    state.destination = event.target.value;
    state.page = 1;
    apply();
  });

  $('f-crewed').addEventListener('change', (event) => {
    state.crewed = event.target.value;
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
      q: '', yMin: null, yMax: null, launcher: '', site: '', destination: '',
      crewed: '', status: '', page: 1,
    });
    $('f-query').value = '';
    $('f-year-min').value = '';
    $('f-year-max').value = '';
    $('f-launcher').value = '';
    $('f-site').value = '';
    $('f-destination').value = '';
    $('f-crewed').value = '';
    $('f-status').value = '';
    apply();
  });

  for (const button of document.querySelectorAll('[data-sort]')) {
    button.addEventListener('click', () => {
      const key = button.dataset.sort;
      if (state.sort === key) state.dir = -state.dir;
      else {
        state.sort = key;
        state.dir = ['objects', 'payloads', 'mass', 'date', 'crewed'].includes(key) ? -1 : 1;
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
