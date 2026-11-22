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
dans `_site/`. Le seul calcul côté client est le filtrage de l'explorateur des lancements,
qui travaille sur un JSON allégé (une entrée par lancement, 10 champs au lieu de 20).

Conséquences directes :

- une visite ne télécharge plus les 5,3 Mo du journal brut (ni les 19,3 Mo de `satcat.tsv`) ;
- chaque classement a une **URL propre**, un `<title>` et une description — donc indexable et citable ;
- le header et le footer existent une seule fois, dans `templates/layout.html` ;
- l'artefact publié ne contient que du HTML, du CSS, du JS et un JSON dérivé.

## Le site

| Page | Contenu |
|---|---|
| `index.html` | présentation, état de la base, repères, méthode |
| `launches.html` | explorateur : toutes les tentatives orbitales depuis 1957 |
| `classements/index.html` | index des classements |
| `classements/decennies.html` | tentatives, issues et objets, décennie par décennie |
| `classements/annees.html` | le rythme annuel depuis 1957 |
| `classements/lanceurs.html` | familles et versions de lanceurs, avec taux de réussite |
| `classements/sites.html` | bases de tir les plus actives |
| `classements/agences.html` | agences et opérateurs, sans fusion d'entités |
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

`data/gcat/` = copie **non transformée** des fichiers publiés sur
<https://planet4589.org/space/gcat/tsv/>.

| Fichier | Origine | Contenu | Utilisé par |
|---|---|---|---|
| `launchlog.tsv` | `derived/` | journal des lancements orbitaux, une ligne par **objet** lancé | tout le site |
| `active.tsv` | `derived/` | satellites actuellement actifs | `objets.html` |
| `currentcat.tsv` | `derived/` | objets actuellement en orbite, débris compris | — (à venir) |
| `geotab.tsv` | `derived/` | journal des satellites géostationnaires | — (à venir) |
| `satcat.tsv` | `cat/` | catalogue complet de tous les objets spatiaux | — (à venir) |
| `psatcat.tsv` | `cat/` | catalogue des charges utiles | — (à venir) |
| `ftocat.tsv` | `cat/` | catalogue des échecs de mise en orbite | — (à venir) |
| `deepcat.tsv` | `cat/` | catalogue de l'espace lointain | — (à venir) |
| `MANIFEST.json` | généré | URL, taille, nombre de lignes, SHA-256 et date de récupération de chaque fichier | date de synchro affichée |

Format commun : un bloc de commentaires préfixé `#`, puis une ligne d'en-tête tabulée,
puis les données. Les champs sont complétés par des espaces ; les dates sont au format
`YYYY Mon DD HHMM:SS` (non ISO, parfois vagues).

## Resynchronisation hebdomadaire

`.github/workflows/update-gcat.yml` exécute `scripts/fetch_gcat.py` :

- **cron** chaque lundi à 05:17 UTC, plus déclenchement manuel (onglet *Actions* →
  *Update GCAT data* → *Run workflow*) ;
- téléchargement des 8 fichiers, comparaison par SHA-256, écriture **uniquement si le
  contenu a changé** ;
- `MANIFEST.json` n'est réécrit que si les données ont réellement bougé ;
- commit `data: GCAT refresh AAAA-MM-JJ` par le bot — puis reconstruction et republication
  du site via `workflow_run`.

Script sans dépendance externe (stdlib Python ≥ 3.9) :

```bash
python3 scripts/fetch_gcat.py --out data/gcat        # récupère / met à jour
python3 scripts/fetch_gcat.py --out data/gcat --check # vérifie sans écrire
```

## Méthodologie des classements

- **Lancement** = tentative de lancement **orbital** (les échecs sont conservés, le
  suborbital est exclu — GCAT le publie séparément).
- **Unité de compte** : `launchlog.tsv` contient une ligne par *objet* lancé (colonne
  `Piece`). Le nombre de lancements = nombre de `Launch_Tag` distincts ; le build agrège
  et conserve le nombre d'objets dans une colonne séparée.
- **Statut** : dérivé du code `LVState` (`OS` = succès orbital, `OF` = échec orbital, tout
  autre code = statut indéterminé). Le code brut reste visible dans l'explorateur.
- **Taux de réussite** : calculé sur les seules issues connues, les statuts indéterminés
  étant exclus du dénominateur.
- **Dates** : jamais normalisées de force ; une date vague reste vague (`1962-??`).
- **Pays / agence** : la valeur affichée est celle du champ `Agency` du GCAT, sans
  réécriture (URSS, Russie et Ukraine restent distincts), et les codes `SatOwner` ne sont
  pas traduits.

Les règles détaillées et les sources alternatives (Space-Track, CelesTrak, UNOOSA…)
sont documentées dans [`SOURCES.md`](SOURCES.md).

## Structure du dépôt

```
.
├── templates/                  # sources des pages (Jinja2)
│   ├── layout.html             # header, footer, canonical, sitemap
│   ├── home.html               # page projet
│   ├── launches.html           # explorateur des lancements
│   ├── objets.html             # vue objets
│   ├── rankings_index.html     # index des classements
│   └── rankings.html           # gabarit d'une page de classement
├── assets/
│   ├── css/style.css           # thème sombre inspiré de Rocket Lab
│   └── js/explorer.js          # filtres de l'explorateur (lit data/launches.json)
├── scripts/
│   ├── fetch_gcat.py           # récupération des TSV (stdlib)
│   └── build_site.py           # agrégation + rendu → _site/
├── data/gcat/                  # données brutes GCAT + MANIFEST.json
├── _site/                      # sortie du build, non versionnée
├── requirements.txt            # Jinja2 (build uniquement)
└── .github/workflows/
    ├── update-gcat.yml         # récupération hebdomadaire des données
    └── pages.yml               # build + publication sur GitHub Pages
```

## Licences

- **Données** : © Jonathan McDowell, *General Catalog of Artificial Space Objects*,
  licence **CC BY 4.0**. Toute réutilisation doit créditer :
  > McDowell, J., 2020: General Catalog of Artificial Space Objects,
  > <https://planet4589.org/space/gcat>
- **Code** du dépôt : libre d'usage et de modification dans le cadre de ce projet.
