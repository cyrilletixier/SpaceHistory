"""Journal du build : orbites, statuts des charges utiles, masses, vols habités, codes."""

from __future__ import annotations

from collections import Counter

from .constants import CREWED_RANGE, ORBIT_ORDER
from .gcat import Dataset
from .payloads import (
    CORRECTION_CANDIDATES,
    ORBITAL_MASS_CORRECTIONS,
    PAYLOAD_FAILED,
    PAYLOAD_STATUS,
    orbital_mass_override,
)
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


def report_payload_status(payloads: list[dict]) -> None:
    """Trace les statuts des charges utiles et les codes `Status` non rangés.

    Même principe que `report_orbits` : un code inédit du GCAT doit se voir
dans le journal du build, pas seulement dans la colonne « Statut » du site.
    La répartition par famille est affichée en clair, parce qu'elle résume ce que
    la page des charges utiles montre : `en orbite` n'est pas la seule issue.
    """
    known = set(PAYLOAD_STATUS) | {PAYLOAD_FAILED}
    families = Counter(payload["status"] or "—" for payload in payloads)
    unmapped = Counter(
        payload["status_code"]
        for payload in payloads
        if payload["status"] and payload["status"] not in known
    )

    listed = ", ".join(f"{label}={count}" for label, count in families.most_common())
    print(f"statuts des charges utiles : {listed or 'aucun'}")
    if unmapped:
        top = ", ".join(f"{code}={count}" for code, count in unmapped.most_common(10))
        print(f"codes Status hors familles connues ({len(unmapped)}) : {top}")


def report_mass_corrections(payloads: list[dict]) -> None:
    """Trace les corrections de masse orbitale des premiers vols habités.

    La table `ORBITAL_MASS_CORRECTIONS` remplace la masse du GCAT par la masse
    orbitale NSSDCA pour 22 vaisseaux. Une substitution silencieuse serait
    invérifiable : on affiche donc combien de charges utiles elle touche, et
    deux anomalies possibles.

    - Une entrée de la table qui ne rencontre **aucune** charge utile est
      signalée : le GCAT a pu renommer l'objet, et la correction ne s'applique
      alors plus à rien (elle resterait écrite dans le code sans effet).
    - Une charge utile **habitée** dont le nom évoque une des familles visées
      (`CORRECTION_CANDIDATES`) sans entrée dans la table est signalée aussi :
      c'est la façon de voir un vol précoce oublié sans tenir de liste à part.
    """
    applied = [payload for payload in payloads if orbital_mass_override(payload["name"])]
    print(f"masses corrigées : {len(applied)} charge(s) utile(s)")

    names = {payload["name"] for payload in applied}
    unused = sorted(set(ORBITAL_MASS_CORRECTIONS) - names)
    if unused:
        print(
            f"::warning::corrections de masse sans charge utile correspondante "
            f"({len(unused)}/{len(ORBITAL_MASS_CORRECTIONS)}) : {', '.join(unused[:8])} "
            f"— nom renommé dans satcat.tsv ? clé à corriger ?"
        )

    uncovered = sorted(
        {
            payload["name"]
            for payload in payloads
            if payload["crewed"]
            and payload["name"]
            and CORRECTION_CANDIDATES.search(payload["name"])
            and not orbital_mass_override(payload["name"])
        }
    )
    if uncovered:
        print(
            f"vols habités précoces sans correction de masse ({len(uncovered)}) : "
            f"{', '.join(uncovered[:8])}"
        )


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
