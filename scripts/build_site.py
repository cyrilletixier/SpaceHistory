#!/usr/bin/env python3
"""Construit le site pré-calculé dans _site/.

    python3 scripts/build_site.py --data data/gcat --out _site

Tout ce qui est calculable l'est ici : les pages HTML sortent finies, les
classements sont rendus au build. Le navigateur ne reçoit plus qu'un JSON
allégé (une entrée par lancement) pour l'explorateur des lancements, et un
second JSON (une entrée par charge utile) pour la page des charges utiles.

Les codes bruts du GCAT (sites, organisations, États) sont traduits via
sites.tsv et orgs.tsv ; les codes d'origine restent disponibles (infobulle,
JSON, journal du build) pour que rien ne devienne invérifiable.

Les charges utiles (`satcat.tsv`, complété par `ftocat.tsv` pour les échecs)
fournissent les colonnes ajoutées à l'explorateur : la **masse en orbite**
(somme des `Mass` des charges utiles réellement cataloguées en orbite, corrigée
pour les premiers vols habités — voir `ORBITAL_MASS_CORRECTIONS`), la
**destination** (famille d'orbite déduite de `OpOrbit`) et le caractère
**habité** du vol (marqueur d'équipage du champ `Type`). Ce sont elles aussi
qui alimentent `charges-utiles.html`, la page vers laquelle pointe chaque vol.

Aucune donnée n'est envoyée sur le réseau : le script lit data/gcat/*.tsv.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from sitebuild.constants import RANKINGS, REPO_ROOT, SITE_URL
from sitebuild.gcat import Translator, read_gcat_tsv
from sitebuild.launches import build_launches
from sitebuild.payloads import attach_payloads, read_payloads
from sitebuild.rendering import (
    format_int,
    format_mass,
    format_pct,
    format_sync,
    render,
    write_json,
)
from sitebuild.reports import (
    report_codes,
    report_crewed,
    report_mass_corrections,
    report_orbits,
)
from sitebuild.stats import (
    aggregate,
    build_highlights,
    build_objects_view,
    decade_of,
    launch_stats,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/gcat", help="dossier des TSV GCAT")
    parser.add_argument("--out", default="_site", help="dossier de sortie")
    parser.add_argument("--templates", default="templates", help="dossier des templates")
    args = parser.parse_args()

    data_dir = Path(args.data)
    out_dir = Path(args.out)
    templates_dir = Path(args.templates)
    if not templates_dir.is_absolute():
        templates_dir = REPO_ROOT / templates_dir

    launchlog = data_dir / "launchlog.tsv"
    if not launchlog.exists():
        print(f"fichier manquant : {launchlog}", file=sys.stderr)
        print("lancez d'abord : python3 scripts/fetch_gcat.py --out data/gcat", file=sys.stderr)
        return 1

    dataset = read_gcat_tsv(launchlog)
    translator = Translator(data_dir)
    launches = build_launches(dataset, translator)

    # Charges utiles : masses, orbites et équipage viennent de satcat.tsv
    # (objets catalogués) et de ftocat.tsv (charges perdues en échec).
    payloads = read_payloads(data_dir, translator)
    attach_payloads(launches, payloads)

    stats = launch_stats(launches)
    stats["payloads"] = len(payloads)

    print(
        f"statuts : succès {stats['successes']}, échec {stats['failures']}, "
        f"inconnu {stats['unknown']}"
    )
    report_codes(dataset, "Launch_Code")
    report_codes(dataset, "LVState")
    report_orbits(payloads)
    report_mass_corrections(payloads)
    report_crewed(launches)
    translator.report()

    manifest: dict = {}
    manifest_path = data_dir / "MANIFEST.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = {}

    sync_label = format_sync(manifest.get("generated_at"))

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["int_fr"] = format_int
    env.filters["pct"] = format_pct
    env.filters["mass"] = format_mass

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    base = {
        "stats": stats,
        "sync_label": sync_label,
        "site_url": SITE_URL,
        "source_rows": len(dataset.rows),
    }

    # Pages de premier niveau
    render(
        env, "home.html", out_dir / "index.html",
        root="", page_path="", active="home",
        rankings=RANKINGS, highlights=build_highlights(launches), **base,
    )
    render(
        env, "launches.html", out_dir / "launches.html",
        root="", page_path="launches.html", active="launches", **base,
    )
    render(
        env, "charges-utiles.html", out_dir / "charges-utiles.html",
        root="", page_path="charges-utiles.html", active="payloads", **base,
    )
    render(
        env, "objets.html", out_dir / "objets.html",
        root="", page_path="objets.html", active="objets",
        objects=build_objects_view(launches, data_dir, translator), **base,
    )
    render(
        env, "rankings_index.html", out_dir / "classements" / "index.html",
        root="../", page_path="classements/", active="rankings",
        rankings=RANKINGS, **base,
    )

    # Une page par classement : les libellés sont déjà humains, le nom complet
    # et le code GCAT d'origine accompagnent chaque ligne agrégée (infobulle).
    keys = {
        "decennies": {"key": lambda item: decade_of(item["year"])},
        "annees": {"key": lambda item: str(item["year"]) if item["year"] else ""},
        "lanceurs": {"key": lambda item: item["launcher"]},
        "sites": {
            "key": lambda item: item["site"],
            "code": lambda item: item["site_code"],
            "detail": lambda item: item["site_detail"],
        },
        "agences": {
            "key": lambda item: item["agency"],
            "code": lambda item: item["agency_code"],
            "detail": lambda item: item["agency_detail"],
        },
        "pays": {
            "key": lambda item: item["country"],
            "code": lambda item: item["country_code"],
            "detail": lambda item: item["country_detail"],
        },
    }
    for ranking in RANKINGS:
        spec = keys[ranking["slug"]]
        rows = aggregate(
            launches, spec["key"], ranking["order"], spec.get("code"), spec.get("detail")
        )
        limit = ranking.get("limit")
        render(
            env, "rankings.html", out_dir / "classements" / f"{ranking['slug']}.html",
            root="../", page_path=f"classements/{ranking['slug']}.html",
            active="rankings", rk=ranking, rows=rows[:limit] if limit else rows,
            hidden=max(0, len(rows) - (limit or len(rows))), **base,
        )

        # Les libellés sont des traductions : le journal montre, pour les
        # classements concernés, ce que chaque nom recouvre réellement.
        if spec.get("detail"):
            print(f"libellés {ranking['slug']} (10 premiers) :")
            for row in rows[:10]:
                print(f"  {row['name']} — {row['detail'] or 'sans nom long'} [{row['code']}]")

    # Explorateur : une entrée par lancement, colonnes utiles seulement.
    # `s` et `a` portent les libellés, `sc` et `ac` les codes GCAT d'origine.
    # `dc` garde les codes d'orbite bruts derrière `dd` (libellé de destination).
    # `cr` vaut 1 pour un vol habité, 0 sinon.
    payload = {
        "source": "GCAT — launchlog.tsv (Jonathan McDowell)",
        "generated": manifest.get("generated_at"),
        "source_rows": len(dataset.rows),
        "launches": [
            {
                "t": item["tag"],
                "d": item["date"],
                "k": item["sort"],
                "y": item["year"],
                "lv": item["launcher"],
                "s": item["site"],
                "sc": item["site_code"],
                "a": item["agency"],
                "ac": item["agency_code"],
                "o": item["objects"],
                "n": " · ".join(item["names"][:8])[:140],
                "pc": item["payload_count"],
                "pi": item["payloads_in_orbit"],
                "pm": item["payloads_with_mass"],
                "m": item["mass_kg"],
                "dd": item["destination"],
                "dc": item["destination_codes"],
                "cr": 1 if item["crewed"] else 0,
                "st": item["status"],
                "c": item["state"],
            }
            for item in launches
        ],
    }
    write_json(out_dir / "data" / "launches.json", payload)

    # Charges utiles : une entrée par charge utile, pour la page filtrée par vol.
    # `cr` vaut 1 quand la charge porte le marqueur d'équipage du vol ; `m` est la
    # masse retenue (`mass_corrected`), donc la masse orbitale NSSDCA pour les
    # vaisseaux habités précoces corrigés.
    write_json(
        out_dir / "data" / "charges-utiles.json",
        {
            "source": "GCAT — satcat.tsv + ftocat.tsv (Jonathan McDowell)",
            "generated": manifest.get("generated_at"),
            "payloads": [
                {
                    "t": item["launch"],
                    "n": item["name"],
                    "y": item["year"],
                    "m": item["mass_corrected"],
                    "o": item["orbit"],
                    "r": item["orbit_code"],
                    "ow": item["owner"],
                    "f": 1 if item["failed"] else 0,
                    "cr": 1 if item["crewed"] else 0,
                    "ty": item["type"],
                }
                for item in payloads
            ],
        },
    )

    # Ressources statiques
    assets = REPO_ROOT / "assets"
    if assets.exists():
        shutil.copytree(assets, out_dir / "assets")

    (out_dir / ".nojekyll").write_text("", encoding="utf-8")
    (out_dir / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: " + SITE_URL + "/sitemap.xml\n",
        encoding="utf-8",
    )

    pages = ["", "launches.html", "charges-utiles.html", "objets.html", "classements/index.html"]
    pages += [f"classements/{ranking['slug']}.html" for ranking in RANKINGS]
    urls = "".join(f"  <url><loc>{SITE_URL}/{page}</loc></url>\n" for page in pages)
    (out_dir / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}</urlset>\n",
        encoding="utf-8",
    )

    size = sum(path.stat().st_size for path in out_dir.rglob("*") if path.is_file())
    json_size = (out_dir / "data" / "launches.json").stat().st_size
    payload_size = (out_dir / "data" / "charges-utiles.json").stat().st_size
    print(f"{stats['launches']} lancements, {stats['objects']} objets, {len(pages)} page(s)")
    print(
        f"_site/ : {size / 1024:.0f} Ko ; explorateur : {json_size / 1024:.0f} Ko ; "
        f"charges utiles : {payload_size / 1024:.0f} Ko"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
