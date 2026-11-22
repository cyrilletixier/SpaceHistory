#!/usr/bin/env python3
"""Télécharge les tables TSV brutes du GCAT dans data/gcat/.

Aucune dépendance externe (stdlib uniquement).

    python3 scripts/fetch_gcat.py --out data/gcat
    python3 scripts/fetch_gcat.py --out data/gcat --check
    python3 scripts/fetch_gcat.py --out data/gcat --only tables

Les fichiers ne sont réécrits que si leur empreinte SHA-256 a changé ;
MANIFEST.json n'est réécrit que si les données ont réellement évolué, afin que
le workflow ne produise aucun commit inutile.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://planet4589.org/space/gcat/tsv"

FILES: list[tuple[str, str]] = [
    ("derived/launchlog.tsv", "Journal des lancements orbitaux (une ligne par objet lancé)"),
    ("derived/active.tsv", "Satellites actuellement actifs"),
    ("derived/currentcat.tsv", "Objets actuellement en orbite, débris compris"),
    ("derived/geotab.tsv", "Journal des satellites géostationnaires"),
    ("cat/satcat.tsv", "Catalogue complet des objets spatiaux"),
    ("cat/psatcat.tsv", "Catalogue des charges utiles"),
    ("cat/ftocat.tsv", "Catalogue des échecs de mise en orbite"),
    ("cat/deepcat.tsv", "Catalogue de l'espace lointain"),
    # Tables de référence : elles traduisent les codes employés par le reste du
    # catalogue (agences, sites, pas de tir) en noms lisibles.
    ("tables/orgs.tsv", "Organisations : code d'agence ou de propriétaire → nom"),
    ("tables/sites.tsv", "Sites de lancement : code → nom et coordonnées"),
    ("tables/lp.tsv", "Pas de tir : code → nom et site de rattachement"),
]

USER_AGENT = "SpaceHistory-gcat-fetcher/1.0 (+https://github.com/cyrilletixier/SpaceHistory)"


def fetch(url: str, retries: int = 3, timeout: int = 180) -> bytes:
    """Télécharge une URL avec quelques tentatives en cas d'erreur réseau."""
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": USER_AGENT, "Cache-Control": "no-cache"}
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt < retries:
                delay = 2**attempt
                print(f"  ! {exc} → nouvelle tentative dans {delay}s", file=sys.stderr)
                time.sleep(delay)
    raise RuntimeError(f"échec du téléchargement de {url} : {last_error}")


def inspect(data: bytes) -> tuple[int, int]:
    """Retourne (nombre de lignes de données, nombre de colonnes).

    Heuristique adaptée au format GCAT : commentaires préfixés '#', puis une
    ligne d'en-tête tabulée, puis les données.
    """
    rows = 0
    columns = 0
    header_seen = False
    for raw in data.decode("utf-8", "replace").splitlines():
        line = raw.rstrip("\r")
        if not line.strip():
            continue
        if not header_seen:
            if "\t" in line:
                columns = len(line.lstrip("#").split("\t"))
                header_seen = True
            continue
        if line.startswith("#") and "\t" not in line:
            continue
        rows += 1
    return rows, columns


def selected_files(only: str) -> list[tuple[str, str]]:
    """Filtre FILES sur des fragments de chemin (« tables », « orgs »…)."""
    tokens = [token.strip() for token in only.split(",") if token.strip()]
    if not tokens:
        return FILES
    return [entry for entry in FILES if any(token in entry[0] for token in tokens)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="data/gcat", help="dossier de destination")
    parser.add_argument(
        "--check", action="store_true", help="télécharge et compare sans rien écrire"
    )
    parser.add_argument(
        "--only",
        default="",
        help="ne récupérer que les fichiers dont le chemin contient un de ces "
             "fragments (séparés par des virgules), ex. : --only tables",
    )
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    updated = 0

    for relpath, description in selected_files(args.only):
        url = f"{BASE}/{relpath}"
        name = Path(relpath).name
        target = out / name
        print(f"→ {name}")
        try:
            data = fetch(url)
        except RuntimeError as exc:
            # Un fichier manquant ne doit pas invalider la récupération des autres.
            print(f"  x {exc}", file=sys.stderr)
            continue

        digest = hashlib.sha256(data).hexdigest()
        previous = target.read_bytes() if target.exists() else None
        changed = previous is None or hashlib.sha256(previous).hexdigest() != digest

        if changed and not args.check:
            target.write_bytes(data)
            updated += 1
            print(f"  ✓ mis à jour — {len(data):,} octets".replace(",", " "))
        elif changed:
            print(f"  ~ différent — {len(data):,} octets".replace(",", " "))
        else:
            print("  = inchangé")

        rows, columns = inspect(data)
        entries.append(
            {
                "name": name,
                "path": f"{args.out.rstrip('/')}/{name}",
                "url": url,
                "source_path": relpath,
                "description": description,
                "bytes": len(data),
                "rows": rows,
                "columns": columns,
                "sha256": digest,
            }
        )

    if not entries:
        print("Aucun fichier récupéré.", file=sys.stderr)
        return 1

    if not args.check:
        manifest_path = out / "MANIFEST.json"
        unchanged = False
        if manifest_path.exists():
            try:
                previous_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                unchanged = previous_manifest.get("files") == entries
            except (json.JSONDecodeError, OSError):
                unchanged = False

        if unchanged and updated == 0:
            print("\nManifeste inchangé.")
        else:
            manifest = {
                "source": "Jonathan McDowell — General Catalog of Artificial Space Objects",
                "source_url": "https://planet4589.org/space/gcat/",
                "license": "CC BY 4.0",
                "citation": "McDowell, J., 2020: General Catalog of Artificial Space Objects, https://planet4589.org/space/gcat",
                "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "files": entries,
            }
            manifest_path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            print("\nManifeste réécrit.")

    total = sum(entry["rows"] for entry in entries)
    print(f"\n{len(entries)} fichier(s), {total:,} ligne(s), {updated} mis à jour".replace(",", " "))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
