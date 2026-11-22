#!/usr/bin/env python3
"""Rapport de diagnostic des TSV GCAT.

Écrit un Markdown qui montre, colonne par colonne, les valeurs réellement
présentes dans les fichiers. Sert à vérifier deux choses qu'on ne peut pas
déduire de la documentation :

  - l'alignement des colonnes (en-tête vs lignes de données) ;
  - le vocabulaire exact des codes d'issue (OS, OF, DS…).

    python3 scripts/diagnose_gcat.py --data data/gcat --out diagnostics/gcat.md

Aucune dépendance : ni Jinja, ni le reste du build.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_.\-]*$")

# Un code d'issue GCAT ressemble à « OS », « OF », « DS », « O », « D »…
SHORT_CODE = re.compile(r"^[A-Za-z]{1,3}$")

DETAILED = ("launchlog.tsv",)
COMPACT = ("active.tsv", "satcat.tsv")


def read_tsv(path: Path):
    """Retourne (colonnes, lignes, lignes brutes après l'en-tête)."""
    text = path.read_text(encoding="utf-8", errors="replace").lstrip("\ufeff")
    lines = text.splitlines()

    columns: list[str] | None = None
    start = 0
    for index, line in enumerate(lines[:400]):
        if "\t" not in line:
            continue
        cells = [cell.strip() for cell in re.sub(r"^#\s?", "", line).split("\t")]
        if len(cells) >= 3 and all(IDENT.match(cell) for cell in cells):
            columns = cells
            start = index + 1
            break

    if columns is None:
        return None, [], lines[:3]

    width = len(columns)
    rows: list[list[str]] = []
    for line in lines[start:]:
        if not line or (line.startswith("#") and "\t" not in line):
            continue
        cells = [cell.strip() for cell in re.sub(r"^#\s?", "", line).split("\t")]
        if len(cells) < 2:
            continue
        if len(cells) != width:
            cells = (cells + [""] * width)[:width]
        rows.append(cells)

    return columns, rows, lines[start:start + 2]


def shorten(value: str, limit: int = 22) -> str:
    value = value.replace("|", "\\|").replace("\t", " ")
    return value if len(value) <= limit else value[: limit - 1] + "…"


def describe(path: Path, limit: int, sample_lines: bool) -> list[str]:
    out: list[str] = []
    columns, rows, raw = read_tsv(path)
    out.append(f"## `{path.name}`")
    out.append("")

    if columns is None:
        out.append("**En-tête introuvable.** Début du fichier :")
        out.append("")
        out.append("```")
        out.extend(line[:200] for line in raw)
        out.append("```")
        out.append("")
        return out

    out.append(f"- colonnes : **{len(columns)}**")
    out.append(f"- lignes de données : **{len(rows)}**")
    out.append(f"- largeurs rencontrées : {sorted({len(row) for row in rows})}")
    out.append("")

    if sample_lines and raw:
        out.append("Deux premières lignes brutes (onglets visibles, tronquées) :")
        out.append("")
        out.append("```")
        out.extend(repr(line[:400]) for line in raw)
        out.append("```")
        out.append("")

    out.append("### Valeurs réelles par colonne")
    out.append("")
    out.append("| # | colonne | non vides | OS | OF | commence par O | valeurs les plus fréquentes |")
    out.append("|---|---|---|---|---|---|---|")

    for index, name in enumerate(columns):
        values = [row[index] for row in rows if index < len(row) and row[index]]
        if not values:
            out.append(f"| {index} | `{name}` | 0 | 0 | 0 | 0 | *(colonne vide)* |")
            continue
        counts = Counter(values)
        os_count = sum(count for value, count in counts.items() if value.upper().startswith("OS"))
        of_count = sum(count for value, count in counts.items() if value.upper().startswith("OF"))
        o_count = sum(count for value, count in counts.items() if value.upper().startswith("O"))
        top = ", ".join(
            f"`{shorten(value)}`×{count}" for value, count in counts.most_common(limit)
        )
        out.append(
            f"| {index} | `{name}` | {len(values)} | {os_count} | {of_count} | {o_count} | {top} |"
        )

    out.append("")

    # Colonnes dont les valeurs ressemblent à des codes courts : candidates
    # pour porter l'issue d'un lancement.
    candidates = []
    for index, name in enumerate(columns):
        values = [row[index] for row in rows if index < len(row) and row[index]]
        if not values:
            continue
        short = sum(1 for value in values if SHORT_CODE.match(value))
        if short / len(values) >= 0.5:
            counts = Counter(values)
            top = ", ".join(
                f"`{shorten(value, 8)}`×{count}" for value, count in counts.most_common(8)
            )
            candidates.append((short / len(values), name, index, top))

    if candidates:
        candidates.sort(reverse=True)
        out.append("### Colonnes à codes courts")
        out.append("")
        for share, name, index, top in candidates:
            out.append(f"- `{name}` (#{index}, {share:.0%} de codes courts) : {top}")
        out.append("")

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/gcat")
    parser.add_argument("--out", default="diagnostics/gcat.md")
    args = parser.parse_args()

    data_dir = Path(args.data)
    out_path = Path(args.out)

    report: list[str] = [
        "# Diagnostic GCAT",
        "",
        "Rapport généré automatiquement : valeurs réellement présentes dans",
        "les TSV, colonne par colonne. Il existe pour vérifier le vocabulaire",
        "des codes d'issue, pas pour publier quoi que ce soit.",
        "",
    ]

    for name in DETAILED:
        path = data_dir / name
        if path.exists():
            report += describe(path, limit=6, sample_lines=True)

    for name in COMPACT:
        path = data_dir / name
        if path.exists():
            report += describe(path, limit=4, sample_lines=False)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"rapport écrit : {out_path} ({out_path.stat().st_size} o)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
