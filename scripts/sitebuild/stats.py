"""Statistiques et agrégations : taux, classements, vue objets, faits marquants."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from .gcat import Translator, read_gcat_tsv
from .rendering import format_int


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
