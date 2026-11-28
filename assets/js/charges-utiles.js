/* Catalogue des charges utiles.
   Lit data/charges-utiles.json : une entrée par charge utile — `satcat.tsv`
   pour les objets catalogués en orbite, `ftocat.tsv` pour les charges perdues
   lors d'un échec. `?vol=<Launch_Tag>` restreint la vue à un lancement : c'est
   la cible du lien de la colonne « objets / charges utiles » de l'explorateur.
   Le bandeau du vol affiche alors, quand le lancement est reconnu dans
   data/launches.json, combien d'objets du tir ne sont pas des charges utiles
   listées (étages, débris).

   `cr` vaut 1 quand le vol emportait un équipage (marqueur du GCAT, 2e
   caractère du champ `Type`), `ty` conserve le code `Type` brut pour que la
   règle reste vérifiable au survol.

   Statut : `f` vaut 1 pour une charge perdue lors d'un échec (`ftocat.tsv`).
   Sinon le statut actuel vient du code `Status` du GCAT (`sc`), traduit par la
   table `statuts` du JSON, calculée au build : une charge cataloguée a été mise
   en orbite, elle n'y est pas forcément restée (Sputnik 1 : `R`, rentré le
   4 janvier 1958). `fd` est la date de fin de phase (`DDate`), `a` les noms
   alternatifs du catalogue (`PLName`, nom d'usage de `psatcat.tsv`). */

const fmt = new Intl.NumberFormat('fr-FR');

const state = {
  q: '', vol: '', orbit: '', crewed: '', yMin: null, yMax: null, status: '',
  sort: 'year', dir: -1, page: 1, pageSize: 50,
};

let payloads = [];
let view = [];

/* Code `Status` du GCAT → statut lisible, écrit par le build. */
let statuses = {};

/* Lancement filtré, retrouvé dans data/launches.json quand `?vol=` désigne un
   tag exact : il fournit le nombre total d'objets du tir, donc le nombre
   d'objets qui ne sont pas des charges utiles listées ici. */
let launch = null;

const $ = (id) => document.getElementById(id);

/* Statut affiché : échec au lancement, sinon traduction du code `Status`.
   Un code que le build n'a pas rangé s'affiche tel quel. */
function statusOf(item) {
  if (item.f) return 'échec';
  if (!item.sc) return '';
  return statuses[item.sc] || item.sc;
}

const statusClass = (label) => {
  if (label === 'en orbite') return ' ok';
  if (label === 'échec' || label === 'détruit') return ' ko';
  return '';
};

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
    case 'crewed': return item.cr || 0;
    case 'status': return statusOf(item);
    default: return (item.n || '').toLowerCase();
  }
}

function matches(item) {
  if (state.yMin && (!item.y || item.y < state.yMin)) return false;
  if (state.yMax && (!item.y || item.y > state.yMax)) return false;
  if (state.orbit && item.o !== state.orbit) return false;
  if (state.crewed === '1' && !item.cr) return false;
  if (state.crewed === '0' && item.cr) return false;
  if (state.status && statusOf(item) !== state.status) return false;

  if (state.vol) {
    const needle = state.vol.trim().toLowerCase();
    if (needle && !(item.t || '').toLowerCase().includes(needle)) return false;
  }

  if (state.q) {
    const needle = state.q.trim().toLowerCase();
    if (needle) {
      const haystack = `${item.n} ${(item.a || []).join(' ')} ${item.t} ${item.ow}`.toLowerCase();
      if (!haystack.includes(needle)) return false;
    }
  }

  return true;
}

/* Bandeau de rappel : d'où l'on vient, et comment revenir à tout le catalogue.
   Quand le vol est reconnu, il dit aussi combien d'objets du tir ne sont pas
   des charges utiles : étages, débris, composants — tout ce que le catalogue
   ne range pas sous `Type` commençant par `P`. */
function renderBanner() {
  const banner = $('vol-banner');
  if (!banner) return;

  if (!state.vol) {
    banner.hidden = true;
    banner.innerHTML = '';
    return;
  }

  let extra = '';
  const needle = state.vol.trim().toLowerCase();
  if (launch && (launch.t || '').toLowerCase() === needle) {
    const objects = launch.o || 0;
    const listed = launch.pc || 0;
    const unlisted = Math.max(0, objects - listed);
    extra = ` — ${fmt.format(objects)} objet(s) au lancement, dont ${fmt.format(listed)} charge(s) utile(s)`
      + (unlisted > 0
        ? ` ; ${fmt.format(unlisted)} objet(s) non listé(s) ici (étages, débris)`
        : ' ; aucun objet non listé');
  }

  banner.hidden = false;
  banner.innerHTML = 'Vol filtré : <span class="pill mono">' + esc(state.vol) + '</span>'
    + extra
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

/* Pastille d'équipage : elle qualifie le vol qui a emporté cette charge utile.
   Le code `Type` brut reste dans l'infobulle du nom, ce qui rend la règle
   vérifiable sans quitter la page. */
function crewBadge(item) {
  if (!item.cr) return '';
  const tip = `Vol habité — Type GCAT : ${item.ty || 'PH…'}`;
  return ` <span class="pill" title="${esc(tip)}">habité</span>`;
}

/* Noms alternatifs du catalogue, sous le nom principal du GCAT : `1-y ISZ`
   devient reconnaissable comme `PS-1 · First Sputnik`. */
function aliasLine(item) {
  if (!item.a || !item.a.length) return '';
  return `<span class="alias">${esc(item.a.join(' · '))}</span>`;
}

/* Pastille de statut. Le code `Status` brut et la date de fin de phase
   (`DDate`, gardée vague quand le GCAT l'est) restent au survol. */
function statusCell(item) {
  const label = statusOf(item);
  if (!label) return '<span class="dim">—</span>';
  const tip = item.f
    ? 'Charge perdue lors du lancement (ftocat.tsv)'
    : `Code GCAT : ${item.sc}${item.fd ? ` — fin de phase : ${item.fd}` : ''}`;
  return `<span class="pill${statusClass(label)}" title="${esc(tip)}">${esc(label)}</span>`;
}

function render() {
  const tbody = $('tbody');
  const start = (state.page - 1) * state.pageSize;
  const slice = view.slice(start, start + state.pageSize);

  tbody.innerHTML = slice.map((item) => `
    <tr>
      <td class="name"${item.ty ? ` title="Type GCAT : ${esc(item.ty)}"` : ''}>${esc(item.n) || '<span class="dim">sans nom</span>'}${crewBadge(item)}${aliasLine(item)}</td>
      <td><a class="pill mono" href="charges-utiles.html?vol=${encodeURIComponent(item.t)}"
             title="Voir les charges utiles de ce vol">${esc(item.t)}</a></td>
      <td class="num">${item.y ? fmt.format(item.y) : '<span class="dim">—</span>'}</td>
      <td class="num">${item.m ? `${fmt.format(item.m)}\u00a0kg` : '<span class="dim">—</span>'}</td>
      <td${item.r ? ` title="Code GCAT : ${esc(item.r)}"` : ''}>${esc(item.o) || '<span class="dim">—</span>'}</td>
      <td class="dim">${esc(item.ow) || '—'}</td>
      <td>${statusCell(item)}</td>
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
      q: '', vol: '', orbit: '', crewed: '', yMin: null, yMax: null, status: '', page: 1,
    });
    $('f-query').value = '';
    $('f-vol').value = '';
    $('f-orbit').value = '';
    $('f-year-min').value = '';
    $('f-year-max').value = '';
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
        state.dir = ['year', 'mass', 'crewed'].includes(key) ? -1 : 1;
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
    statuses = payload.statuts || {};

    /* Le lancement filtré, pour le décompte des objets non listés : il est
       cherché dans data/launches.json, uniquement quand un vol est demandé.
       Un échec de chargement ne casse rien : le bandeau se contente de ne pas
       afficher le décompte. */
    if (state.vol) {
      try {
        const launchResponse = await fetch('data/launches.json', { cache: 'no-cache' });
        if (launchResponse.ok) {
          const all = (await launchResponse.json()).launches || [];
          launch = all.find((item) => item.t === state.vol)
            || all.find((item) => (item.t || '').toLowerCase() === state.vol.toLowerCase())
            || null;
        }
      } catch (error) {
        launch = null;
      }
    }

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
