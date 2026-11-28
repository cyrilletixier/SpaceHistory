"""Charges utiles : masse en orbite, destination, vol habité, rattachement aux lancements."""

from __future__ import annotations

from pathlib import Path

from .constants import (
    CREW_MARK,
    CREW_MARK_INDEX,
    ORBIT_FAMILIES,
    ORBIT_ORDER,
    UNKNOWN_CODES,
)
from .gcat import Translator, parse_date, read_gcat_tsv


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
