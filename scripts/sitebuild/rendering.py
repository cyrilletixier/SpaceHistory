"""Formatage des nombres et dates, rendu des gabarits et écriture des JSON."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from jinja2 import Environment


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
