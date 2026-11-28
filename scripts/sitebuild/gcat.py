"""Lecture des TSV du GCAT, tables de traduction des codes et analyse des dates."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from .constants import (
    DATE_RE,
    IDENT,
    LONG_COLUMNS,
    MONTHS,
    SHORT_COLUMNS,
    UNKNOWN_CODES,
)


# --------------------------------------------------------------------------- #
# Lecture des TSV GCAT
# --------------------------------------------------------------------------- #


class Dataset:
    """Table TSV GCAT : en-tête, lignes, accès par nom de colonne."""

    def __init__(self, name: str, columns: list[str], rows: list[list[str]]):
        self.name = name
        self.columns = columns
        self.rows = rows
        self._exact = {column: index for index, column in enumerate(columns)}
        self._lower = {column.lower(): index for index, column in enumerate(columns)}

    def col(self, *aliases: str) -> int:
        """Index de la première colonne trouvée parmi les alias, sinon -1."""
        for alias in aliases:
            if alias in self._exact:
                return self._exact[alias]
            index = self._lower.get(str(alias).lower())
            if index is not None:
                return index
        return -1

    @staticmethod
    def cell(row: list[str], index: int) -> str:
        return row[index] if 0 <= index < len(row) else ""


def read_gcat_tsv(path: Path) -> Dataset:
    """Parse un TSV GCAT : commentaires '#', ligne d'en-tête tabulée, données."""
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
        raise SystemExit(f"en-tête TSV introuvable dans {path}")

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

    return Dataset(path.name, columns, rows)


# --------------------------------------------------------------------------- #
# Codes GCAT → libellés humains
# --------------------------------------------------------------------------- #


def read_codebook(path: Path, code_column: str) -> dict[str, dict[str, str]]:
    """Lit une table de référence GCAT : code -> {nom court, nom complet}.

    Sert pour sites.tsv et orgs.tsv, qui partagent le même jeu de colonnes de
    libellés. C'est le GCAT lui-même qui nomme ses entités : aucun libellé n'est
    réécrit à la main, ce qui garantit qu'une traduction reste vérifiable à la
    source.
    """
    if not path.exists():
        return {}

    table = read_gcat_tsv(path)
    code_at = table.col(code_column)
    if code_at < 0:
        return {}

    short_at = [index for index in (table.col(name) for name in SHORT_COLUMNS) if index >= 0]
    long_at = [index for index in (table.col(name) for name in LONG_COLUMNS) if index >= 0]

    def first(row: list[str], indexes: list[int]) -> str:
        for index in indexes:
            label = table.cell(row, index)
            if label and label not in UNKNOWN_CODES:
                return label
        return ""

    book: dict[str, dict[str, str]] = {}
    for row in table.rows:
        code = table.cell(row, code_at)
        if not code or not IDENT.match(code):
            continue
        long = first(row, long_at)
        short = first(row, short_at) or long or code
        book.setdefault(code, {"short": short, "long": long})
    return book


class Translator:
    """Traduit les codes GCAT en libellés lisibles, sans jamais inventer.

    Un code absent des tables de référence est rendu tel quel et compté : le
    journal du build dit combien de codes restent à couvrir, et lesquels pèsent
    le plus.
    """

    def __init__(self, data_dir: Path):
        self.sites = read_codebook(data_dir / "sites.tsv", "Site")
        self.orgs = read_codebook(data_dir / "orgs.tsv", "Code")
        self.unknown_sites: Counter = Counter()
        self.unknown_orgs: Counter = Counter()

    @staticmethod
    def _entry(book: dict[str, dict[str, str]], raw: str) -> dict[str, str] | None:
        """Entrée de la table de référence, avec repli sur le code sans « ? ».

        Le GCAT suffixe certains codes d'un « ? » quand le rattachement est
        douteux (TYSC?, KVR?). Le code connu reste alors la meilleure clé : on
        préfère le nom assorti d'un point d'interrogation plutôt qu'un code nu.
        """
        entry = book.get(raw)
        if entry is None and raw.endswith("?"):
            entry = book.get(raw.rstrip("?"))
        return entry

    def site(self, code: str) -> str:
        raw = (code or "").strip()
        if raw in UNKNOWN_CODES:
            return ""
        entry = self._entry(self.sites, raw)
        if entry is None:
            self.unknown_sites[raw] += 1
            return raw
        return entry["short"]

    def site_detail(self, code: str) -> str:
        entry = self._entry(self.sites, (code or "").strip())
        return entry["long"] if entry else ""

    def org(self, code: str) -> str:
        raw = (code or "").strip()
        if raw in UNKNOWN_CODES:
            return ""

        entry = self._entry(self.orgs, raw)
        if entry is not None:
            return entry["short"]

        # Un code d'agence peut être composite (« NASA/USAF ») : on traduit
        # chaque composante séparément plutôt que de laisser un code brut.
        parts = [part.strip() for part in raw.split("/") if part.strip()]
        if len(parts) > 1:
            return " / ".join(self.org(part) or part for part in parts)

        self.unknown_orgs[raw] += 1
        return raw

    def org_detail(self, code: str) -> str:
        raw = (code or "").strip()
        if raw in UNKNOWN_CODES:
            return ""

        entry = self._entry(self.orgs, raw)
        if entry is not None:
            return entry["long"]

        parts = [part.strip() for part in raw.split("/") if part.strip()]
        if len(parts) > 1:
            return " / ".join(self.org_detail(part) or part for part in parts)
        return ""

    def state(self, code: str) -> str:
        """État / pays : mêmes tables de référence que les organisations.

        `LVState` et `SatState` portent des codes d'État (US, SU, RU, CN…)
        présents dans orgs.tsv au même titre que les agences.
        """
        return self.org(code)

    def state_detail(self, code: str) -> str:
        return self.org_detail(code)

    def report(self) -> None:
        """Trace la couverture des tables de référence, code par code."""

        def summary(counter: Counter) -> str:
            if not counter:
                return "aucun"
            top = ", ".join(f"{code}={count}" for code, count in counter.most_common(8))
            return f"{len(counter)} code(s) — {top}"

        print(f"libellés sites : {len(self.sites)} entrées ; non résolus : {summary(self.unknown_sites)}")
        print(f"libellés organisations : {len(self.orgs)} entrées ; non résolus : {summary(self.unknown_orgs)}")


# --------------------------------------------------------------------------- #
# Dates et agrégation
# --------------------------------------------------------------------------- #


def parse_date(raw: str) -> tuple[int | None, str, str]:
    """Retourne (année, libellé lisible, clé de tri).

    Une date vague reste vague : les composantes absentes ne sont jamais
    inventées (elles restent '??' dans le libellé).
    """
    source = (raw or "").strip()
    if not source or source in {"-", "?"}:
        return None, "—", "99999999"

    match = DATE_RE.match(source)
    if not match:
        return None, source, "99999999"

    year = int(match.group(1))
    month = MONTHS.get((match.group(2) or "").lower())
    day = int(match.group(3)) if match.group(3) else None
    hour, minute, second = match.group(4), match.group(5), match.group(6)

    label = str(year)
    if month:
        label += f"-{month:02d}"
        if day:
            label += f"-{day:02d}"
    elif day:
        label += f"-??-{day:02d}"
    if hour:
        label += f" {hour}:{minute}"

    key = (
        f"{year:04d}{month or 0:02d}{day or 0:02d}"
        f"{hour or '00'}{minute or '00'}{second or '00'}"
    )
    return year, label, key
