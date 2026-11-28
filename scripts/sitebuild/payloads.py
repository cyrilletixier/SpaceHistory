"""Charges utiles : masse en orbite, destination, vol habité, rattachement aux lancements."""

from __future__ import annotations

import re
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


# --------------------------------------------------------------------------- #
# Corrections de masse orbitale (premiers vols habités)
# --------------------------------------------------------------------------- #

# Masse du vaisseau **placé en orbite**, publiée par la NASA (NSSDCA), pour les
# premiers vaisseaux habités dont le champ `Mass` du GCAT ne donne pas cette
# valeur. Chaque entrée cite sa fiche : la correction reste vérifiable une par
# une, sans faire confiance à une constante globale.
#
# La clé est le champ `Name` de `satcat.tsv`, à l'identique — pas de
# correspondance approximative, pas de fusion de vols (Vostok 1 et Vostok 2
# restent deux entrées, comme URSS et Russie restent deux États). Un nom absent
# de cette table garde la masse du GCAT ; une entrée qui ne rencontre aucune
# charge utile est signalée dans le journal du build plutôt que de dormir ici.
ORBITAL_MASS_CORRECTIONS: dict[str, dict] = {
    "Vostok 1": {"vehicle": "Vostok", "orbital_mass": 4725, "source": "NASA NSSDCA 1961-012A"},
    "Vostok 2": {"vehicle": "Vostok", "orbital_mass": 4730, "source": "NASA NSSDCA 1961-019A"},
    "Vostok 3": {"vehicle": "Vostok", "orbital_mass": 4730, "source": "NASA NSSDCA 1962-028A"},
    "Vostok 4": {"vehicle": "Vostok", "orbital_mass": 4730, "source": "NASA NSSDCA 1962-031A"},
    "Vostok 5": {"vehicle": "Vostok", "orbital_mass": 4730, "source": "NASA NSSDCA 1963-020A"},
    "Vostok 6": {"vehicle": "Vostok", "orbital_mass": 4730, "source": "NASA NSSDCA 1963-024A"},
    "Voskhod 1": {"vehicle": "Voskhod", "orbital_mass": 5320, "source": "NASA NSSDCA 1964-058A"},
    "Voskhod 2": {"vehicle": "Voskhod", "orbital_mass": 5682, "source": "NASA NSSDCA 1965-018A"},
    "Mercury 6": {
        "vehicle": "Mercury", "orbital_mass": 1355,
        "source": "NASA NSSDCA 1962-004A (Friendship 7)",
    },
    "Mercury 7": {
        "vehicle": "Mercury", "orbital_mass": 1355,
        "source": "NASA NSSDCA 1962-016A (Aurora 7)",
    },
    "Mercury 8": {
        "vehicle": "Mercury", "orbital_mass": 1355,
        "source": "NASA NSSDCA 1962-034A (Sigma 7)",
    },
    "Mercury 9": {
        "vehicle": "Mercury", "orbital_mass": 1355,
        "source": "NASA NSSDCA 1963-015A (Faith 7)",
    },
    "Gemini 3": {"vehicle": "Gemini", "orbital_mass": 3228, "source": "NASA NSSDCA 1965-020A (GT-3)"},
    "Gemini 4": {"vehicle": "Gemini", "orbital_mass": 3575, "source": "NASA NSSDCA 1965-023A (GT-4)"},
    "Gemini 5": {"vehicle": "Gemini", "orbital_mass": 3581, "source": "NASA NSSDCA 1965-057A (GT-5)"},
    "Gemini 6A": {
        "vehicle": "Gemini", "orbital_mass": 3514,
        "source": "NASA NSSDCA 1965-104A (GT-6A)",
    },
    "Gemini 7": {"vehicle": "Gemini", "orbital_mass": 3663, "source": "NASA NSSDCA 1965-096A (GT-7)"},
    "Gemini 8": {"vehicle": "Gemini", "orbital_mass": 3789, "source": "NASA NSSDCA 1966-024A (GT-8)"},
    "Gemini 9A": {
        "vehicle": "Gemini", "orbital_mass": 3800,
        "source": "NASA NSSDCA 1966-050A (GT-9A)",
    },
    "Gemini 10": {
        "vehicle": "Gemini", "orbital_mass": 3812,
        "source": "NASA NSSDCA 1966-066A (GT-10)",
    },
    "Gemini 11": {
        "vehicle": "Gemini", "orbital_mass": 3774,
        "source": "NASA NSSDCA 1966-075A (GT-11)",
    },
    "Gemini 12": {
        "vehicle": "Gemini", "orbital_mass": 3763,
        "source": "NASA NSSDCA 1966-097A (GT-12)",
    },
}

# Familles de véhicules couvertes par la table ci-dessus. Sert au journal du
# build : une charge utile habitée dont le nom évoque l'une d'elles sans entrée
# dans la table est signalée, pour qu'un vol oublié ne passe pas inaperçu.
CORRECTION_CANDIDATES = re.compile(r"vostok|voskhod|mercury|gemini", re.IGNORECASE)


def orbital_mass_override(name: str) -> dict | None:
    """Correction de masse orbitale pour un nom de charge utile, ou None.

    Correspondance **exacte** sur le champ `Name` du catalogue : ni recherche
    floue, ni expression régulière. Un nom qui ne figure pas dans la table garde
    la masse du GCAT, ce qui est le comportement par défaut pour les ~64 000
    autres charges utiles.
    """
    return ORBITAL_MASS_CORRECTIONS.get((name or "").strip())


def read_payloads(data_dir: Path, translator: Translator | None = None) -> list[dict]:
    """Une entrée par charge utile : `satcat.tsv` puis `ftocat.tsv`.

    `satcat.tsv` recense les objets catalogués, donc les charges utiles
    effectivement mises en orbite ; `ftocat.tsv` recense celles perdues lors
    d'un échec. Les deux alimentent la page des charges utiles (avec un statut
    distinct), mais **seule la première sert à la masse en orbite** : compter
    une charge perdue dans « masse en orbite » serait faux.

    Deux masses sont conservées : `mass_gcat`, celle du champ `Mass`, et
    `mass_corrected`, celle qui fait foi — la précédente, remplacée par la
    masse orbitale NSSDCA quand le nom figure dans `ORBITAL_MASS_CORRECTIONS`
    (premiers vols habités). Garder les deux rend la substitution vérifiable et
    permet au journal du build de dire sur combien de charges elle porte.

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

            mass_gcat = to_mass(table.cell(row, idx["Mass"]))
            override = orbital_mass_override(name)
            mass_corrected = override["orbital_mass"] if override else mass_gcat

            payloads[key] = {
                "jcat": jcat,
                "launch": tag,
                "name": name,
                "year": year,
                "mass_gcat": mass_gcat,
                "mass_corrected": mass_corrected,
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
      en orbite ; vide (None) si aucune n'a de masse, jamais zéro. La somme
      porte sur `mass_corrected`, donc sur la masse orbitale NSSDCA pour les
      vaisseaux corrigés — sans quoi un vol comme Vostok 1 contribuerait pour
      une valeur que la table vient précisément de rectifier ;
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
        masses = [
            payload["mass_corrected"]
            for payload in in_orbit
            if payload["mass_corrected"] is not None
        ]

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
