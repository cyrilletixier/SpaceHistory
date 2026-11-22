import { loadManifest, setSyncDate, fmtInt } from './gcat.js';

const byName = (manifest, name) =>
  manifest?.files?.find((file) => file.name === name) ?? null;

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = value;
}

async function init() {
  const manifest = await loadManifest();
  setSyncDate(manifest);

  if (!manifest) {
    setText('manifest-note', 'Aucun manifeste : lancer le workflow « Update GCAT data » pour récupérer les données.');
    return;
  }

  const launchlog = byName(manifest, 'launchlog.tsv');
  const psatcat = byName(manifest, 'psatcat.tsv');
  const satcat = byName(manifest, 'satcat.tsv');

  setText('kpi-launchlog', launchlog ? fmtInt(launchlog.rows) : '—');
  setText('kpi-psat', psatcat ? fmtInt(psatcat.rows) : '—');
  setText('kpi-satcat', satcat ? fmtInt(satcat.rows) : '—');

  const date = manifest.generated_at ? new Date(manifest.generated_at) : null;
  setText(
    'kpi-sync',
    date && !Number.isNaN(date.getTime())
      ? date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
      : '—'
  );

  const total = manifest.files.reduce((sum, file) => sum + file.rows, 0);
  setText(
    'manifest-note',
    `${fmtInt(manifest.files.length)} fichiers TSV · ${fmtInt(total)} enregistrements bruts · ${manifest.license} · source ${manifest.source}`
  );
}

init();
