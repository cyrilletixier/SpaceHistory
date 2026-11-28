"""Constantes du build : chemins, expressions régulières, familles d'orbites, classements."""

from __future__ import annotations

import re
from pathlib import Path


# scripts/sitebuild/constants.py → racine du dépôt (trois niveaux au-dessus).
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
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
