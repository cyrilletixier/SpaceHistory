"""Journal du build : vocabulaire des orbites, vols habités et codes rencontrés."""

from __future__ import annotations

from collections import Counter

from .constants import CREWED_RANGE, ORBIT_ORDER
from .gcat import Dataset
from .stats import decade_of


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
