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
(somme des `Mass` des charges utiles réellement cataloguées en orbite), la
**destination** (famille d'orbite déduite de `OpOrbit`) et le caractère
**habité** du vol (marqueur d'équipage du champ `Type`). Ce sont elles aussi
qui alimentent `charges-utiles.html`, la page vers laquelle pointe chaque vol.

Aucune donnée n'est envoyée sur le réseau : le script lit data/gcat/*.tsv.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://cyrilletixier.github.io/SpaceHistory"

IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_.\-]*$")
DATE_RE = re.compile(
    r"^(\d{4})(?:\s+([A-Za-z]{3}))?(?:\s+(\d{1,2}))?(?:\s+(\d{2})(\d{2}):(\d{2}))?"
)
MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# Valeurs de remplissage du GCAT : elles ne désignent aucun lieu, aucune
# organisation, aucun État ; on ne les traduit donc pas.
UNKNOWN_CODES = {"", "-", "?", "*", "UNK", "X"}

# Familles d'orbite affichées dans la colonne « Destination ». La clé est le
# code `OpOrbit` du GCAT, qualificatif retiré : `LLEO/I` → `LLEO`, `GEO/T` →
# `GEO`. Le qualificatif (inclinaison, héliosynchrone, polaire…) précise
# l'orbite, il n'en change pas la famille.
#
# Un code absent de cette table n'est pas traduit : il s'affiche tel quel et le
# journal du build le signale. Aucune orbite n'est donc rangée d'office dans une
# famille, comme aucun code d'agence n'est inventé.
ORBIT_FAMILIES = {
    "LLEO": "LEO",
    "LEO": "LEO",
    "MEO": "MEO",
    "GEO": "GEO",
    "GSO": "GEO",
    "HEO": "HEO",
    "EEO": "Interplanétaire",
    "HCO": "Interplanétaire",
    "LLO": "Lunaire",
    "LMO": "Lunaire",
    "LSO": "Lunaire",
}

# Ordre d'affichage quand un vol dépose ses charges utiles sur plusieurs
# orbites : du plus proche de la Terre au plus lointain.
ORBIT_ORDER = ["LEO", "MEO", "GEO", "HEO", "Lunaire", "Interplanétaire"]

# Marqueur d'équipage du champ `Type` d'une charge utile. Ce champ encode
# plusieurs attributs sur ses premiers caractères :
#
#   1re lettre   : classe d'objet — `P` charge utile, `R` étage, `D` débris ;
#   2e caractère : `H` si **le vol emportait un équipage**, `P` sinon ;
#   4e caractère : `H` si **le véhicule est habitable**, quel que soit le vol.
#
# Les deux `H` ne disent pas la même chose, et seul le second caractère répond
# à la question « vol habité ? ». Les cas de contrôle du catalogue le montrent :
#
#   Shenzhou 1 à 4    `PP-H`      véhicule habitable, vol sans personne
#   Crew Dragon DM-1  `PP-H-V-`   idem
#   Shenzhou 5        `PH-H`      vol habité
#   Soyouz TM-2       `PH H V`    vol habité
#   Buran OK-1K       `P`         ni l'un ni l'autre (lancé sans équipage)
#   Apollo 6 / 7      `PP-H` / `PH-H`  le couple non habité / habité
#
# Se fier au 4e caractère produirait donc la liste fausse des véhicules
# habitables jamais habités ; se fier au nom de la charge utile raterait les
# mêmes vols. La règle retenue désigne 360 vols sur le millésime courant, ce qui
# recoupe le décompte des vols habités établi indépendamment.
CREW_MARK = "H"
CREW_MARK_INDEX = 1

# Fourchette de contrôle des vols habités. Elle n'impose rien au rendu : elle
# sert au journal du build à signaler un changement d'encodage côté GCAT, qui
# viderait sinon le filtre « habité » sans bruit.
CREWED_RANGE = (300, 420)

# Colonnes de libellés des tables de référence (sites.tsv et orgs.tsv ont le
# même jeu de colonnes).
SHORT_COLUMNS = ("ShortName", "ShortEName")
LONG_COLUMNS = ("Name", "EName", "UName")

RANKINGS = [
    {
        "slug": "decennies",
        "nav": "Décennies",
        "title": "Les décennies spatiales",
        "sub": "Tentatives de lancement orbital, succès, échecs et objets mis en "
               "orbite, décennie par décennie, depuis 1957.",
        "name_label": "Décennie",
        "order": "source",
        "show_period": False,
    },
    {
        "slug": "annees",
        "nav": "Années",
        "title": "Le rythme annuel des lancements",
        "sub": "Chaque année depuis 1957, du premier Spoutnik aux cadences "
               "actuelles : tentatives, issues et objets mis en orbite.",
        "name_label": "Année",
        "order": "source",
        "show_period": False,
    },
    {
        "slug": "lanceurs",
        "nav": "Lanceurs",
        "title": "Les lanceurs les plus utilisés",
        "sub": "Classement des familles et versions de lanceurs par nombre de "
               "tentatives orbitales, avec leur taux de réussite.",
        "name_label": "Lanceur",
        "order": "attempts",
        "show_period": True,
        "limit": 200,
    },
    {
        "slug": "sites",
        "nav": "Sites",
        "title": "Les sites de lancement",
        "sub": "Les bases de tir les plus actives de l'histoire spatiale, "
               "toutes époques confondues.",
        "name_label": "Site",
        "order": "attempts",
        "show_period": True,
        "limit": 120,
        "source_hint": "Les noms de sites viennent de <code>sites.tsv</code>, la table "
                       "de référence du GCAT. Un même nom peut recouvrir plusieurs "
                       "codes de sites ; le nom complet et les codes bruts "
                       "s'affichent au survol.",
    },
    {
        "slug": "agences",
        "nav": "Agences",
        "title": "Les agences et opérateurs",
        "sub": "Répartition des tentatives orbitales par agence de lancement, "
               "sans fusion des entités historiques : URSS, Russie et Ukraine "
               "restent des lignes distinctes.",
        "name_label": "Agence",
        "order": "attempts",
        "show_period": True,
        "show_detail_line": True,
        "limit": 200,
        "source_hint": "Les noms d'organisations viennent de <code>orgs.tsv</code>, la "
                       "table de référence du GCAT. Beaucoup d'agences n'ont qu'un "
                       "sigle : le nom développé donné par le catalogue s'affiche "
                       "sous le sigle, et le code brut au survol.",
    },
    {
        "slug": "pays",
        "nav": "Pays",
        "title": "Les pays lanceurs",
        "sub": "Tentatives de lancement orbital par pays de l'engin porteur, "
               "d'après le champ LVState du GCAT. Les États restent ceux du "
               "catalogue : URSS, Russie et Ukraine sont des lignes distinctes.",
        "name_label": "Pays",
        "order": "attempts",
        "show_period": True,
        "limit": 120,
        "source_hint": "Le pays est celui de l'engin lanceur (<code>LVState</code>), pas "
                       "celui du propriétaire du satellite (<code>SatState</code>). Les "
                       "noms d'États viennent de <code>orgs.tsv</code> ; le code brut "
                       "s'affiche au survol.",
    },
]


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


def launch_outcome(codes: list[str]) -> str:
    """Qualifie un lancement d'après les codes d'issue de ses pièces.

    Le GCAT range l'issue dans `Launch_Code` : une lettre de destination suivie
    d'une lettre d'issue. `OS` = mise en orbite réussie, `OF` = échec orbital,
    `DS` = départ vers l'espace lointain réussi. Le code est parfois suffixé
    (`OF40`, `OS89`), d'où la comparaison par préfixe.

    L'échec prime : un seul « OF » suffit à qualifier le lancement, même si
    d'autres pièces portent « OS » — un lancement qui perd sa charge utile
    reste un échec.

    Les rares codes hors de ce trio (`NS`, `NF`, `XS`) ne sont pas des issues
    orbitales : ils restent « inconnu » plutôt que d'être rangés d'office dans
    une colonne.

    Attention au piège de vocabulaire : dans ce fichier, `LVState` et `SatState`
    ne sont *pas* des codes d'issue mais des codes de **pays** (US, SU, CN…).
    """
    upper = [code.upper() for code in codes]

    if any(code.startswith("OF") for code in upper):
        return "échec"
    if any(code.startswith(("OS", "DS")) for code in upper):
        return "succès"
    return "inconnu"


def representative_code(codes: list[str], status: str) -> str:
    """Code le plus parlant à afficher à côté du statut."""
    if status == "échec":
        for code in codes:
            if code.upper().startswith("OF"):
                return code
    elif status == "succès":
        for code in codes:
            if code.upper().startswith(("OS", "DS")):
                return code
    return codes[0] if codes else ""


def build_launches(dataset: Dataset, translator: Translator | None = None) -> list[dict]:
    """Agrège launchlog.tsv par Launch_Tag : une entrée = un lancement."""
    idx = {
        name: dataset.col(name)
        for name in (
            "Launch_Tag", "Launch_Date", "PLName", "Name", "LV_Type",
            "Launch_Site", "Launch_Pad", "Agency", "LVState", "Launch_Code",
            "SatOwner",
        )
    }
    cell = dataset.cell
    groups: dict[str, dict] = {}

    for row in dataset.rows:
        tag = cell(row, idx["Launch_Tag"]) or "?"
        group = groups.get(tag)
        if group is None:
            year, label, sort_key = parse_date(cell(row, idx["Launch_Date"]))
            group = {
                "tag": tag, "year": year, "date": label, "sort": sort_key,
                "launcher": "", "site": "", "pad": "", "agency": "",
                "country": "", "codes": [], "objects": 0, "names": [],
                "owners": Counter(), "_seen": set(),
            }
            groups[tag] = group

        group["objects"] += 1

        for field, column in (
            ("launcher", "LV_Type"),
            ("site", "Launch_Site"),
            ("pad", "Launch_Pad"),
            ("agency", "Agency"),
            ("country", "LVState"),
        ):
            if not group[field]:
                group[field] = cell(row, idx[column])

        # L'issue est portée par chaque pièce : on collecte les codes du
        # lancement, puis on tranche une fois le lancement complet.
        code = cell(row, idx["Launch_Code"])
        if code and code not in group["codes"]:
            group["codes"].append(code)

        owner = cell(row, idx["SatOwner"])
        if owner:
            group["owners"][owner] += 1

        name = cell(row, idx["PLName"]) or cell(row, idx["Name"])
        if name and name not in group["_seen"]:
            group["_seen"].add(name)
            group["names"].append(name)

    launches: list[dict] = []
    for group in groups.values():
        codes = group.pop("codes")
        group.pop("_seen")

        # On garde le code brut (et le nom complet GCAT) à côté du libellé :
        # c'est ce qui reste vérifiable dans le catalogue, et c'est ce qu'on
        # affiche au survol.
        group["site_code"] = group["site"]
        group["agency_code"] = group["agency"]
        group["country_code"] = group["country"]
        if translator is not None:
            group["site"] = translator.site(group["site_code"])
            group["site_detail"] = translator.site_detail(group["site_code"])
            group["agency"] = translator.org(group["agency_code"])
            group["agency_detail"] = translator.org_detail(group["agency_code"])
            group["country"] = translator.state(group["country_code"])
            group["country_detail"] = translator.state_detail(group["country_code"])
        else:
            group["site_detail"] = ""
            group["agency_detail"] = ""
            group["country_detail"] = ""

        status = launch_outcome(codes)
        group["status"] = status
        group["state"] = representative_code(codes, status)
        launches.append(group)

    launches.sort(key=lambda item: (item["sort"], item["tag"]))
    return launches


# --------------------------------------------------------------------------- #
# Charges utiles : masse en orbite, destination, vol habité
# --------------------------------------------------------------------------- #


def to_mass(raw: str) -> int | None:
    """Masse en kg d'une ligne de catalogue, ou None si elle n'est pas connue.

    Le GCAT écrit `0` (parfois `-`) quand la masse est inconnue : c'est une
    valeur de remplissage, pas un objet de masse nulle. Ces lignes sont donc
    écartées de la somme plutôt que de la tirer vers zéro — 32 000 objets du
    catalogue portent ce zéro.
    """
    value = (raw or "").strip().replace(" ", "")
    if not value or value in {"-", "?", "*"}:
        return None
    try:
        mass = float(value)
    except ValueError:
        return None
    return int(round(mass)) if mass > 0 else None


def orbit_label(raw: str) -> str:
    """Famille d'orbite d'un code `OpOrbit` : `LLEO/I` → `LEO`.

    Le qualificatif après la barre oblique (héliosynchrone, polaire, inclinée…)
    précise l'orbite, il ne la change pas. Un code inconnu est rendu tel quel :
    il vaut mieux afficher `XYZ` que de ranger l'objet dans une famille fausse.
    """
    base = (raw or "").strip().upper().split("/")[0]
    return ORBIT_FAMILIES.get(base, base)


def orbit_rank(label: str) -> tuple[int, str]:
    """Clé de tri des destinations : du plus proche au plus lointain."""
    if label in ORBIT_ORDER:
        return (ORBIT_ORDER.index(label), label)
    return (len(ORBIT_ORDER), label)


def is_crewed(kind: str) -> bool:
    """Le vol emportait-il un équipage ? Voir `CREW_MARK`.

    On lit le **2e** caractère de `Type`, celui du vol, et non le 4e, qui
    signale un véhicule habitable : Shenzhou 1 à 4 et Crew Dragon Demo-1
    portent le second sans avoir eu personne à bord.
    """
    marker = (kind or "").strip().upper()
    return len(marker) > CREW_MARK_INDEX and marker[CREW_MARK_INDEX] == CREW_MARK


def read_payloads(data_dir: Path, translator: Translator | None = None) -> list[dict]:
    """Une entrée par charge utile : `satcat.tsv` puis `ftocat.tsv`.

    `satcat.tsv` recense les objets catalogués, donc les charges utiles
    effectivement mises en orbite ; `ftocat.tsv` recense celles perdues lors
    d'un échec. Les deux alimentent la page des charges utiles (avec un statut
    distinct), mais **seule la première sert à la masse en orbite** : compter
    une charge perdue dans « masse en orbite » serait faux.

    En revanche, le marqueur d'équipage est lu dans les deux tables : un vol
    habité qui échoue (Soyouz MS-10, navette Challenger) reste un vol habité, et
    sa charge utile n'existe que dans `ftocat.tsv`.

    Une charge utile est une ligne dont le champ `Type` commence par `P` (le
    catalogue distingue les étages `R`, les débris `D`, les composants…).
    """
    payloads: dict[tuple[str, str], dict] = {}

    for filename, failed in (("satcat.tsv", False), ("ftocat.tsv", True)):
        path = data_dir / filename
        if not path.exists():
            continue

        table = read_gcat_tsv(path)
        idx = {
            name: table.col(name)
            for name in (
                "JCAT", "Launch_Tag", "Name", "PLName", "Type", "Mass",
                "OpOrbit", "Owner", "LDate",
            )
        }
        if idx["Type"] < 0 or idx["Launch_Tag"] < 0:
            continue

        for row in table.rows:
            kind = table.cell(row, idx["Type"]).strip().upper()
            if not kind.startswith("P"):
                continue

            tag = table.cell(row, idx["Launch_Tag"]).strip()
            if not tag or tag in UNKNOWN_CODES:
                continue

            name = table.cell(row, idx["Name"]) or table.cell(row, idx["PLName"])
            orbit_code = table.cell(row, idx["OpOrbit"]).strip()
            owner_code = table.cell(row, idx["Owner"]).strip()
            year, _, _ = parse_date(table.cell(row, idx["LDate"]))
            jcat = table.cell(row, idx["JCAT"]).strip()

            key = (tag, jcat or f"{name}|{year}")
            if key in payloads:
                continue

            payloads[key] = {
                "jcat": jcat,
                "launch": tag,
                "name": name,
                "year": year,
                "mass": to_mass(table.cell(row, idx["Mass"])),
                "orbit": orbit_label(orbit_code),
                "orbit_code": orbit_code,
                "owner": translator.org(owner_code) if translator else owner_code,
                "failed": failed,
                "crewed": is_crewed(kind),
                "type": kind,
            }

    return sorted(
        payloads.values(),
        key=lambda item: (item["launch"], (item["name"] or "").lower()),
    )


def attach_payloads(launches: list[dict], payloads: list[dict]) -> None:
    """Ajoute à chaque lancement sa masse en orbite, sa destination et son équipage.

    - `mass_kg` : somme des masses **connues** des charges utiles cataloguées
      en orbite ; vide (None) si aucune n'a de masse, jamais zéro ;
    - `payloads_with_mass` : sur combien de charges utiles la somme porte ;
    - `destination` : familles d'orbite de ces charges utiles, du plus proche au
      plus lointain (`LEO · GEO` pour un vol à destination mixte) ;
    - `destination_codes` : les codes `OpOrbit` bruts, pour l'infobulle ;
    - `crewed` : le vol emportait un équipage, c'est-à-dire qu'au moins une de
      ses charges utiles porte le marqueur d'équipage. L'agrégation par vol est
      ce qui empêche de compter sept fois une mission navette ; et l'on regarde
      **toutes** les charges du vol, échecs compris, parce qu'un vol habité qui
      échoue reste un vol habité.

    Un lancement en échec n'a, par construction, aucune charge utile dans
    `satcat.tsv` : sa masse en orbite reste vide, ce qui est le résultat exact.
    """
    by_tag: dict[str, list[dict]] = {}
    for payload in payloads:
        by_tag.setdefault(payload["launch"], []).append(payload)

    for item in launches:
        group = by_tag.get(item["tag"], [])
        in_orbit = [payload for payload in group if not payload["failed"]]
        masses = [payload["mass"] for payload in in_orbit if payload["mass"]]

        families: list[str] = []
        for payload in in_orbit:
            label = payload["orbit"]
            if label and label not in families:
                families.append(label)
        families.sort(key=orbit_rank)

        item["payload_count"] = len(group)
        item["payloads_in_orbit"] = len(in_orbit)
        item["payloads_with_mass"] = len(masses)
        item["mass_kg"] = sum(masses) if masses else None
        item["destination"] = " · ".join(families)
        item["destination_codes"] = " · ".join(
            sorted({payload["orbit_code"] for payload in in_orbit if payload["orbit_code"]})
        )
        item["crewed"] = any(payload["crewed"] for payload in group)


def report_orbits(payloads: list[dict]) -> None:
    """Trace le vocabulaire des orbites : familles obtenues, codes non traduits.

    Même principe que `report_codes` : si le GCAT introduit une orbite inédite,
    ça doit apparaître dans le journal du build, pas silencieusement dans une
    colonne.
    """
    families = Counter(payload["orbit"] for payload in payloads if payload["orbit"])
    unmapped = Counter(
        payload["orbit_code"].strip().upper().split("/")[0]
        for payload in payloads
        if payload["orbit_code"] and payload["orbit"] not in ORBIT_ORDER
    )

    listed = ", ".join(f"{label}={count}" for label, count in families.most_common(12))
    print(f"destinations ({len(payloads)} charges utiles) : {listed or 'aucune'}")
    if unmapped:
        top = ", ".join(f"{code}={count}" for code, count in unmapped.most_common(10))
        print(f"orbites hors familles connues ({len(unmapped)}) : {top}")


def report_crewed(launches: list[dict]) -> None:
    """Trace les vols habités et alerte si le marqueur d'équipage se dérobe.

    Le total est le garde-fou de la règle `is_crewed` : si le GCAT change
    l'encodage de `Type`, le filtre « habité » se viderait sans que rien ne le
    dise. On affiche donc le total, sa répartition par décennie et les vols
    habités en échec, et on sort de la fourchette attendue en annotation.
    """
    crewed = [item for item in launches if item["crewed"]]
    decades = Counter(decade_of(item["year"]) for item in crewed)
    failed = [item["tag"] for item in crewed if item["status"] == "échec"]

    listed = ", ".join(f"{name}={count}" for name, count in sorted(decades.items()))
    print(f"vols habités : {len(crewed)} — {listed or 'aucun'}")
    if failed:
        print(f"vols habités en échec : {len(failed)} — {', '.join(failed[:8])}")

    low, high = CREWED_RANGE
    if not low <= len(crewed) <= high:
        print(
            f"::warning::vols habités hors de la fourchette {low}-{high} : {len(crewed)} "
            f"— vérifier l'encodage de Type (2e caractère = marqueur d'équipage)"
        )


def launch_stats(launches: list[dict]) -> dict:
    counts = Counter(item["status"] for item in launches)
    years = [item["year"] for item in launches if item["year"]]
    first = min(years) if years else None
    last = max(years) if years else None
    successes = counts.get("succès", 0)
    failures = counts.get("échec", 0)
    known = successes + failures

    return {
        "launches": len(launches),
        "successes": successes,
        "failures": failures,
        "unknown": counts.get("inconnu", 0),
        "objects": sum(item["objects"] for item in launches),
        "crewed": sum(1 for item in launches if item["crewed"]),
        "first_year": first,
        "last_year": last,
        "period": f"{first} → {last}" if first else "—",
        "success_rate": (100 * successes / known) if known else None,
    }


def aggregate(
    launches: list[dict],
    key_func,
    order: str = "attempts",
    code_func=None,
    detail_func=None,
) -> list[dict]:
    """Agrège les lancements selon une clé, avec taux et part du total.

    `code_func` et `detail_func` collectent les codes GCAT d'origine et les noms
    complets d'une ligne agrégée : ils forment l'infobulle, pour qu'un libellé
    traduit ne cache jamais sa source.
    """
    buckets: dict[str, dict] = {}

    for item in launches:
        name = (key_func(item) or "").strip()
        if not name:
            continue
        bucket = buckets.get(name)
        if bucket is None:
            bucket = {
                "name": name, "attempts": 0, "successes": 0,
                "failures": 0, "objects": 0, "years": [],
                "codes": set(), "details": [],
            }
            buckets[name] = bucket
        bucket["attempts"] += 1
        bucket["objects"] += item["objects"]
        if item["status"] == "succès":
            bucket["successes"] += 1
        elif item["status"] == "échec":
            bucket["failures"] += 1
        if item["year"]:
            bucket["years"].append(item["year"])
        if code_func is not None:
            code = (code_func(item) or "").strip()
            if code:
                bucket["codes"].add(code)
        if detail_func is not None:
            detail = (detail_func(item) or "").strip()
            if detail and detail not in bucket["details"]:
                bucket["details"].append(detail)

    rows = list(buckets.values())
    for row in rows:
        years = row.pop("years")
        row["first"] = min(years) if years else None
        row["last"] = max(years) if years else None
        row["code"] = ", ".join(sorted(row.pop("codes")))
        details = row.pop("details")
        # Un nom agrégé peut recouvrir plusieurs entités (les codes de site de
        # Plesetsk) : l'infobulle les énumère, la colonne n'en montre qu'un.
        row["detail"] = " · ".join(details[:3])
        row["detail_one"] = details[0] if details else ""
        tip = []
        if row["detail"]:
            tip.append(f"GCAT : {row['detail']}")
        if row["code"]:
            tip.append(f"code {row['code']}")
        row["tip"] = " · ".join(tip)
        known = row["successes"] + row["failures"]
        row["rate"] = (100 * row["successes"] / known) if known else None

    if order == "attempts":
        rows.sort(key=lambda row: (-row["attempts"], row["name"].lower()))

    total = sum(row["attempts"] for row in rows) or 1
    for row in rows:
        row["share"] = 100 * row["attempts"] / total
    return rows


# --------------------------------------------------------------------------- #
# Formatage
# --------------------------------------------------------------------------- #


def format_int(value) -> str:
    if value is None:
        return "—"
    return f"{int(value):,}".replace(",", "\u202f")


def format_pct(value) -> str:
    if value is None:
        return "—"
    return f"{value:.1f}\u202f%".replace(".", ",")


def format_mass(value) -> str:
    """Masse en kg, ou tiret cadratin : une somme inconnue n'est pas zéro."""
    if not value:
        return "—"
    return f"{format_int(value)}\u202fkg"


def format_sync(raw: str | None) -> str:
    if not raw:
        return "inconnue"
    try:
        moment = datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return raw
    return moment.strftime("%d/%m/%Y")


# --------------------------------------------------------------------------- #
# Rendu
# --------------------------------------------------------------------------- #


def render(env: Environment, template: str, target: Path, **context) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(env.get_template(template).render(**context), encoding="utf-8")
    return target


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def decade_of(year: int | None) -> str:
    return f"{year // 10 * 10}s" if year else "inconnue"


def build_objects_view(
    launches: list[dict], data_dir: Path, translator: Translator | None = None
) -> dict:
    """Vue « objets » : objets mis en orbite par décennie et par propriétaire."""
    decades: dict[str, dict] = {}
    owners: Counter = Counter()

    for item in launches:
        name = decade_of(item["year"])
        entry = decades.get(name)
        if entry is None:
            entry = {"name": name, "launches": 0, "objects": 0}
            decades[name] = entry
        entry["launches"] += 1
        entry["objects"] += item["objects"]
        owners.update(item["owners"])

    def describe(counter: Counter, limit: int) -> list[dict]:
        """Code -> libellé, en gardant code et nom complet pour l'infobulle."""
        rows = []
        for code, count in counter.most_common(limit):
            detail = translator.org_detail(code) if translator else ""
            tip = []
            if detail:
                tip.append(f"GCAT : {detail}")
            tip.append(f"code {code}")
            rows.append(
                {
                    "name": translator.org(code) if translator else code,
                    "code": code,
                    "detail": detail,
                    "tip": " · ".join(tip),
                    "count": count,
                }
            )
        return rows

    active_total = None
    active_owners: list[dict] = []
    active_path = data_dir / "active.tsv"
    if active_path.exists():
        active = read_gcat_tsv(active_path)
        index = active.col("Owner")
        if index >= 0:
            counts = Counter(
                value for value in (active.cell(row, index) for row in active.rows) if value
            )
            active_total = len(active.rows)
            active_owners = describe(counts, 15)

    return {
        "decades": list(decades.values()),
        "owners": describe(owners, 25),
        "active_total": active_total,
        "active_owners": active_owners,
    }


def build_highlights(launches: list[dict]) -> list[dict]:
    """Quelques repères factuels pour la page d'accueil."""
    by_launcher = aggregate(launches, lambda item: item["launcher"])
    by_site = aggregate(launches, lambda item: item["site"])
    by_year = aggregate(launches, lambda item: str(item["year"]) if item["year"] else "", "source")
    by_decade = aggregate(launches, lambda item: decade_of(item["year"]), "source")

    def top(rows: list[dict]) -> dict | None:
        return max(rows, key=lambda row: row["attempts"]) if rows else None

    highlights = []
    launcher, site = top(by_launcher), top(by_site)
    year, decade = top(by_year), top(by_decade)
    if launcher:
        highlights.append({
            "label": "Lanceur le plus utilisé",
            "value": launcher["name"],
            "detail": f"{format_int(launcher['attempts'])} tentatives",
        })
    if site:
        highlights.append({
            "label": "Site le plus actif",
            "value": site["name"],
            "detail": f"{format_int(site['attempts'])} tentatives",
        })
    if year:
        highlights.append({
            "label": "Année la plus chargée",
            "value": year["name"],
            "detail": f"{format_int(year['attempts'])} tentatives",
        })
    if decade:
        highlights.append({
            "label": "Décennie la plus chargée",
            "value": decade["name"],
            "detail": f"{format_int(decade['attempts'])} tentatives",
        })
    return highlights


def report_codes(dataset: Dataset, column: str) -> None:
    """Trace le vocabulaire complet d'une colonne.

    Un changement de codes côté GCAT doit se voir dans le journal du build, pas
    dans les taux affichés : on liste donc toutes les valeurs distinctes.
    """
    index = dataset.col(column)
    if index < 0:
        print(f"codes {column} : colonne absente")
        return
    counts = Counter(
        value for value in (dataset.cell(row, index) for row in dataset.rows) if value
    )
    listed = ", ".join(f"{code}={count}" for code, count in counts.most_common(40))
    print(f"codes {column} : {len(counts)} valeurs distinctes — {listed or 'aucune'}")


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
    # `cr` vaut 1 quand la charge porte le marqueur d'équipage du vol.
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
                    "m": item["mass"],
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
