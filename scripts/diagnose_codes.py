#!/usr/bin/env python3
"""Inventaire des codes GCAT à traduire.

Écrit, pour chaque colonne codée, les valeurs réellement présentes avec leur
fréquence. Sert à remplir data/lookups/codes.tsv : on traduit ce qui existe,
par ordre de poids, au lieu de deviner un vocabulaire.

    python3 scripts/diagnose_codes.py --data data/gcat --out diagnostics/codes.md
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from diagnose_gcat import read_tsv  # noqa: E402  (script voisin, même dossier)

# (fichier, colonne, seuil) — le seuil évite de noyer le rapport dans la queue
# de distribution : en dessous, le code reste affiché brut sur le site.
TARGETS = [
    ("launchlog.tsv", "Launch_Code", 1),
    ("launchlog.tsv", "LVState", 1),
    ("launchlog.tsv", "SatState", 1),
    ("launchlog.tsv", "Agency", 20),
    ("launchlog.tsv", "Launch_Site", 20),
    ("launchlog.tsv", "SatOwner", 40),
    ("active.tsv", "Owner", 20),
    ("active.tsv", "Category", 1),
    ("active.tsv", "Class", 1),
    ("active.tsv", "MVR", 1),
    ("active.tsv", "OpOrbit", 1),
    ("satcat.tsv", "Status", 1),
    ("satcat.tsv", "State", 1),
    ("satcat.tsv", "OpOrbit", 1),
]


def inventory(path: Path, column: str, threshold: int) -> list[str]:
    columns, rows, _ = read_tsv(path)
    if not columns or column not in columns:
        return [f"## `{path.name}` / `{column}`", "", "*colonne absente*", ""]

    index = columns.index(column)
    values = [row[index] for row in rows if index < len(row) and row[index]]
    counts = Counter(values)

    listed = [(value, count) for value, count in counts.most_common() if count >= threshold]
    covered = sum(count for _, count in listed)
    total = len(values)

    out = [
        f"## `{path.name}` / `{column}`",
        "",
        f"- valeurs distinctes : **{len(counts)}** sur **{total}** lignes",
        f"- listées ci-dessous (seuil {threshold}) : **{len(listed)}** codes, "
        f"soit **{100 * covered / total:.1f} %** des lignes" if total else "- aucune ligne",
        "",
        "```",
    ]
    out.extend(f"{value}\t{count}" for value, count in listed)
    out.append("```")
    out.append("")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/gcat")
    parser.add_argument("--out", default="diagnostics/codes.md")
    args = parser.parse_args()

    data_dir = Path(args.data)
    out_path = Path(args.out)

    report: list[str] = [
        "# Codes GCAT à traduire",
        "",
        "Inventaire des valeurs réellement présentes, par ordre de fréquence.",
        "Sert de base à `data/lookups/codes.tsv`.",
        "",
    ]

    for filename, column, threshold in TARGETS:
        path = data_dir / filename
        if path.exists():
            report += inventory(path, column, threshold)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"inventaire écrit : {out_path} ({out_path.stat().st_size} o)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
