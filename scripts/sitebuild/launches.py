"""Lancements : issue (succès/échec), code représentatif et construction de la liste."""

from __future__ import annotations

from collections import Counter

from .gcat import Dataset, Translator, parse_date


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
