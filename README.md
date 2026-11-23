# SpaceHistory

Exploration et classements sur l'histoire spatiale, à partir d'une source unique :
le **General Catalog of Artificial Space Objects (GCAT)** de Jonathan McDowell.

Site publié : **<https://cyrilletixier.github.io/SpaceHistory/>**

Le dépôt remplit trois rôles :

1. **entrepôt de données brutes** — `data/gcat/` contient les fichiers TSV du GCAT, tels que publiés,
   resynchronisés automatiquement chaque semaine ;
2. **code de calcul** — `scripts/build_site.py` agrège les TSV et produit les classements ;
3. **site statique pré-calculé** (GitHub Pages) — un simple tas de fichiers HTML servis par le CDN
   de GitHub, sans serveur applicatif.

## Principe : tout est pré-calculé au build

Le navigateur n'agrège plus rien. `scripts/build_site.py` lit `data/gcat/launchlog.tsv`,
regroupe les objets par `Launch_Tag`, calcule les classements et écrit des pages **finies**
dans `_site/`. Le seul calcul côté client est le filtrage des deux explorateurs, qui
travaillent sur des JSON allégés : une entrée par lancement (20 champs au lieu de 20 colonnes
brutes) et une entrée par charge utile.

Conséquences directes :

- une visite ne télécharge plus les 5,3 Mo du journal brut (ni les 19,3 Mo de `satcat.tsv`) ;
- chaque classement a une **URL propre**, un `<title>` et une description — donc indexable et citable ;
- le header et le footer existent une seule fois, dans `templates/layout.html` ;
- l'artefact publié ne contient que du HTML, du CSS, du JS et des JSON dérivés.

## Le site

| Page | Contenu |
|---|---|
| `index.html` | présentation, état de la base, repères, méthode |
| `launches.html` | explorateur : toutes les tentatives orbitales depuis 1957 |
| `charges-utiles.html` | catalogue des charges utiles, filtrable par vol (`?vol=`) |
| `classements/index.html` | index des classements |
| `classements/decennies.html` | tentatives, issues et objets, décennie par décennie |
| `classements/annees.html` | le rythme annuel depuis 1957 |
| `classements/lanceurs.html` | familles et versions de lanceurs, avec taux de réussite |
| `classements/sites.html` | bases de tir les plus actives |
| `classements/agences.html` | agences et opérateurs de lancement |
| `classements/pays.html` | pays de l'engin porteur (`LVState`) |
| `objets.html` | objets mis en orbite par décennie et par propriétaire |
| `sitemap.xml`, `robots.txt` | générés au build |

### Construire le site en local

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_site.py --data data/gcat --out _site
python3 -m http.server -d _site 8000   # http://localhost:8000
```

Le build échoue explicitement si `data/gcat/launchlog.tsv` est absent.

### Publication (GitHub Pages)

`.github/workflows/pages.yml` construit l'artefact puis le déploie :

- **URL** : <https://cyrilletixier.github.io/SpaceHistory/>
- **déclencheurs** : push sur `main`, fin du workflow *Update GCAT data* (déclencheur
  `workflow_run` — indispensable car un commit poussé avec le `GITHUB_TOKEN` ne déclenche
  pas les workflows `push`), et lancement manuel ;
- **étapes** : `setup-python` → `pip install -r requirements.txt` → `build_site.py`
  → `upload-pages-artifact` → `deploy-pages` ;
- **contenu publié** : `_site/` uniquement. Ni `data/gcat/`, ni `scripts/`, ni `.github/`,
  ni `.git` ;
- **activation** : `actions/configure-pages` avec `enablement: true` crée le site en mode
  *GitHub Actions* s'il n'existe pas encore.

> Si le job de déploiement échoue avec « Pages site is not configured to use GitHub
> Actions », il faut basculer une fois le réglage :
> **Settings → Pages → *Source* : GitHub Actions**, puis relancer le workflow.

## Les données

`data/gcat/` = copie **non transformée** des 11 fichiers publiés sur
<https://planet4589.org/space/gcat/tsv/> (8 catalogues, 3 tables de référence).

| Fichier | Origine | Contenu | Utilisé par |
|---|---|---|---|
| `launchlog.tsv` | `derived/` | journal des lancements orbitaux, une ligne par **objet** lancé | tout le site |
| `active.tsv` | `derived/` | satellites actuellement actifs | `objets.html` |
| `currentcat.tsv` | `derived/` | objets actuellement en orbite, débris compris | — (à venir) |
| `geotab.tsv` | `derived/` | journal des satellites géostationnaires | — (à venir) |
| `satcat.tsv` | `cat/` | catalogue complet de tous les objets spatiaux | **masse et orbite** des charges utiles |
| `psatcat.tsv` | `cat/` | catalogue des charges utiles (programme, catégorie, commentaire) | — (à venir) |
| `ftocat.tsv` | `cat/` | catalogue des échecs de mise en orbite | charges utiles perdues |
| `deepcat.tsv` | `cat/` | catalogue de l'espace lointain | — (à venir) |
| `sites.tsv` | `tables/` | **référence** : code de site → nom, coordonnées | libellés des sites |
| `orgs.tsv` | `tables/` | **référence** : code d'organisation ou d'État → nom | libellés des agences, des pays, des propriétaires |
| `lp.tsv` | `tables/` | **référence** : code de pas de tir → nom et site de rattachement | — (à venir) |
| `MANIFEST.json` | généré | URL, taille, nombre de lignes, SHA-256 et date de récupération de chaque fichier | date de synchro affichée |

Format commun : un bloc de commentaires préfixé `#`, puis une ligne d'en-tête tabulée,
puis les données. Les champs sont complétés par des espaces ; les dates sont au format
`YYYY Mon DD HHMM:SS` (non ISO, parfois vagues).

## Resynchronisation hebdomadaire

`.github/workflows/update-gcat.yml` exécute `scripts/fetch_gcat.py` :

- **cron** chaque lundi à 05:17 UTC, plus déclenchement manuel (onglet *Actions* →
  *Update GCAT data* → *Run workflow*) ;
- téléchargement des 11 fichiers (8 catalogues + 3 tables de référence), comparaison par
  SHA-256, écriture **uniquement si le contenu a changé** ;
- `MANIFEST.json` n'est réécrit que si les données ont réellement bougé ;
- commit `data: GCAT refresh AAAA-MM-JJ` par le bot — puis reconstruction et republication
  du site via `workflow_run`.

Script sans dépendance externe (stdlib Python ≥ 3.9) :

```bash
python3 scripts/fetch_gcat.py --out data/gcat        # récupère / met à jour
python3 scripts/fetch_gcat.py --out data/gcat --check # vérifie sans écrire
python3 scripts/fetch_gcat.py --out data/gcat --only tables  # tables de référence seules
```

## Méthodologie des classements

- **Lancement** = tentative de lancement **orbital** (les échecs sont conservés, le
  suborbital est exclu — GCAT le publie séparément).
- **Unité de compte** : `launchlog.tsv` contient une ligne par *objet* lancé (colonne
  `Piece`). Le nombre de lancements = nombre de `Launch_Tag` distincts ; le build agrège
  et conserve le nombre d'objets dans une colonne séparée.
- **Statut** : dérivé du code `Launch_Code` (`OS` = succès orbital, `OF` = échec orbital,
  `DS` = départ vers l'espace lointain), comparé **par préfixe** car le GCAT suffixe
  parfois le code (`OF40`, `OS89`). L'échec prime sur les autres pièces d'un même tir.
  Les codes `NS`, `NF` et `XS` ne sont pas des issues orbitales : ils restent
  « indéterminé » (26 lancements sur 7 460) plutôt que d'être rangés d'autorité.
  ⚠️ `LVState` et `SatState` ne sont **pas** des codes d'issue mais des codes de **pays** —
  piège de vocabulaire du GCAT.
- **Taux de réussite** : calculé sur les seules issues connues, les statuts indéterminés
  étant exclus du dénominateur.
- **Dates** : jamais normalisées de force ; une date vague reste vague (`1962-??`).
- **Libellés** : les codes de sites, d'organisations et d'États sont traduits par les
  **tables de référence du GCAT elles-mêmes** (`sites.tsv`, `orgs.tsv`), jamais par une
  liste écrite à la main. Le code brut reste accessible en infobulle, dans le JSON et dans
  le journal du build. Aucune entité n'est fusionnée : URSS, Russie et Ukraine restent
  distinctes, comme les codes d'agence du catalogue.
- **Pays** : les classements « agences » et « pays » ne portent pas sur le même champ —
  `Agency` (opérateur du lancement, 136 codes) et `LVState` (pays de l'engin porteur,
  20 codes). Ce ne sont donc pas deux vues du même palmarès.

### Charges utiles, masse en orbite et destination

L'explorateur des lancements porte deux colonnes calculées au build à partir de
`satcat.tsv` (et de `ftocat.tsv` pour les charges perdues) :

- **Charge utile** = ligne de catalogue dont le champ `Type` commence par `P` (le GCAT
  distingue les étages `R`, les débris `D`, les composants…). Chaque charge utile est
  rattachée à son vol par `Launch_Tag`.
- **Masse en orbite** = somme du champ `Mass` (kg) des charges utiles **cataloguées en
  orbite** pour ce vol. Le `0` que le GCAT écrit quand la masse est inconnue (plus de
  32 000 objets) est traité comme une absence, pas comme un zéro : ces charges utiles sont
  écartées de la somme, et le nombre de masses réellement additionnées est visible au
  survol. Un vol sans aucune masse connue affiche « — ». Une charge perdue lors d'un échec
  n'entre pas dans la somme (elle n'a pas été mise en orbite) : elle apparaît en revanche
  sur la page des charges utiles, avec le statut « échec ».
- **Destination** = famille d'orbite déduite de `OpOrbit` : `LLEO`/`LEO` → **LEO**,
  `MEO`, `GEO`/`GSO`, `HEO`, `LLO`/`LMO`/`LSO` → **Lunaire**, `EEO`/`HCO` →
  **Interplanétaire**. Le qualificatif après la barre oblique (`LLEO/I`, `GEO/T`) précise
  l'orbite sans en changer la famille. Un code inconnu n'est pas traduit : il s'affiche tel
  quel et le journal du build le signale, comme pour les codes d'agence.
- **Lien vers le vol** : la colonne « charges utiles » ne recopie plus les noms ; elle
  affiche le nombre de charges utiles et renvoie vers
  `charges-utiles.html?vol=<Launch_Tag>`. Les noms restent dans `launches.json` (champ `n`)
  pour que la recherche de l'explorateur continue de fonctionner.

Les règles détaillées, la couverture des tables de référence et les sources alternatives
(Space-Track, CelesTrak, UNOOSA…) sont documentées dans [`SOURCES.md`](SOURCES.md).

## Structure du dépôt

```
.
├── templates/                  # sources des pages (Jinja2)
│   ├── layout.html             # header, footer, canonical, sitemap
│   ├── home.html               # page projet
│   ├── launches.html           # explorateur des lancements
│   ├── charges-utiles.html     # catalogue des charges utiles
│   ├── objets.html             # vue objets
│   ├── rankings_index.html     # index des classements
│   └── rankings.html           # gabarit d'une page de classement
├── assets/
│   ├── css/style.css           # thème sombre inspiré de Rocket Lab
│   ├── js/explorer.js          # filtres de l'explorateur (lit data/launches.json)
│   └── js/charges-utiles.js    # filtres du catalogue (lit data/charges-utiles.json)
├── scripts/
│   ├── fetch_gcat.py           # récupération des TSV (stdlib)
│   ├── build_site.py           # agrégation + rendu → _site/
│   ├── diagnose_gcat.py        # rapport de vocabulaire sur les données brutes
│   └── diagnose_codes.py       # inventaire des codes à traduire
├── data/gcat/                  # données brutes GCAT + MANIFEST.json
├── _site/                      # sortie du build, non versionnée
├── requirements.txt            # Jinja2 (build uniquement)
└── .github/workflows/
    ├── update-gcat.yml         # récupération hebdomadaire des données
    ├── pages.yml               # build + publication sur GitHub Pages
    ├── check-build.yml         # build de contrôle sur chaque PR
    └── diagnose-gcat.yml       # rapports de vocabulaire, publiés sur une branche dédiée
```

## Licences

- **Données** : © Jonathan McDowell, *General Catalog of Artificial Space Objects*,
  licence **CC BY 4.0**. Toute réutilisation doit créditer :
  > McDowell, J., 2020: General Catalog of Artificial Space Objects,
  > <https://planet4589.org/space/gcat>
- **Code** du dépôt : libre d'usage et de modification dans le cadre de ce projet.
