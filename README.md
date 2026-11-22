# SpaceHistory

Exploration et classements sur l'histoire spatiale, à partir d'une source unique :
le **General Catalog of Artificial Space Objects (GCAT)** de Jonathan McDowell.

Site publié : **<https://cyrilletixier.github.io/SpaceHistory/>**

Le dépôt remplit deux rôles :

1. **entrepôt de données brutes** — `data/gcat/` contient les fichiers TSV du GCAT, tels que publiés,
   resynchronisés automatiquement chaque semaine ;
2. **site statique** (GitHub Pages) — trois pages qui rendent ces données consultables
   (présentation, lancements, objets mis en orbite), avec filtres et pagination.

## Le site

| Page | Contenu |
|---|---|
| `index.html` | présentation du projet, état de la base, méthode |
| `launches.html` | toutes les tentatives de lancement orbital depuis 1957 |
| `objects.html` | toutes les charges utiles mises en orbite |

Aucun build, aucune dépendance : les pages lisent directement les TSV de `data/gcat/`
dans le navigateur (agrégation et filtres côté client).

### Publication (GitHub Pages)

`.github/workflows/pages.yml` construit l'artefact et le déploie :

- **URL** : <https://cyrilletixier.github.io/SpaceHistory/>
- **déclencheurs** : push sur `main`, fin du workflow *Update GCAT data* (déclencheur
  `workflow_run` — indispensable car un commit poussé avec le `GITHUB_TOKEN` ne déclenche
  pas les workflows `push`), et lancement manuel ;
- **contenu publié** : `index.html`, `launches.html`, `objects.html`, `assets/`, `data/`,
  plus un `.nojekyll` et un `robots.txt` générés. Ni `.git`, ni `scripts/`, ni `.github/` ;
- **activation** : `actions/configure-pages` avec `enablement: true` crée le site en mode
  *GitHub Actions* s'il n'existe pas encore.

> Si le job de déploiement échoue avec « Pages site is not configured to use GitHub
> Actions », il faut basculer une fois le réglage :
> **Settings → Pages → *Source* : GitHub Actions**, puis relancer le workflow.

Le site est reconstruit à chaque modification du code **et** à chaque resynchronisation des
données : l'artefact embarqué contient les TSV, donc les pages servies sont toujours
alignées sur la dernière récupération.

## Les données

`data/gcat/` = copie **non transformée** des fichiers publiés sur
<https://planet4589.org/space/gcat/tsv/>.

| Fichier | Origine | Contenu |
|---|---|---|
| `launchlog.tsv` | `derived/` | journal des lancements orbitaux, une ligne par **objet** lancé |
| `active.tsv` | `derived/` | satellites actuellement actifs |
| `currentcat.tsv` | `derived/` | objets actuellement en orbite, débris compris |
| `geotab.tsv` | `derived/` | journal des satellites géostationnaires |
| `satcat.tsv` | `cat/` | catalogue complet de tous les objets spatiaux |
| `psatcat.tsv` | `cat/` | catalogue des charges utiles |
| `ftocat.tsv` | `cat/` | catalogue des échecs de mise en orbite |
| `deepcat.tsv` | `cat/` | catalogue de l'espace lointain |
| `MANIFEST.json` | généré | URL, taille, nombre de lignes, SHA-256 et date de récupération de chaque fichier |

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
- commit `data: GCAT refresh AAAA-MM-JJ` par le bot — puis republication du site via
  `workflow_run`.

Script sans dépendance externe (stdlib Python ≥ 3.9) :

```bash
python3 scripts/fetch_gcat.py --out data/gcat        # récupère / met à jour
python3 scripts/fetch_gcat.py --out data/gcat --check # vérifie sans écrire
```

> Le premier remplissage de `data/gcat/` se fait donc en lançant le workflow une fois
> (ou le script en local) : avant cela, les pages affichent leur état vide.

## Méthodologie des classements

- **Lancement** = tentative de lancement **orbital** (les échecs sont conservés, le
  suborbital est exclu — GCAT le publie séparément).
- **Unité de compte** : `launchlog.tsv` contient une ligne par *objet* lancé (colonne
  `Piece`). Le nombre de lancements = nombre de `Launch_Tag` distincts ; le site agrège
  donc à la volée et affiche séparément le nombre d'objets.
- **Statut** : dérivé des codes `LVState` / `SatState` (`OS` = succès orbital,
  `OF` = échec orbital). Le code brut reste visible à côté du statut déduit.
- **Dates** : jamais normalisées de force ; une date vague reste vague.
- **Pays / agence** : la valeur affichée est celle du champ `Agency` du GCAT, sans
  réécriture (URSS, Russie, Ukraine restent distincts).

Les règles détaillées et les sources alternatives (Space-Track, CelesTrak, UNOOSA…)
sont documentées dans [`SOURCES.md`](SOURCES.md).

## Structure du dépôt

```
.
├── index.html                  # page projet
├── launches.html               # page lancements
├── objects.html                # page objets mis en orbite
├── assets/
│   ├── css/style.css           # thème sombre inspiré de Rocket Lab
│   └── js/
│       ├── gcat.js             # parseur TSV GCAT, dates, pagination, utilitaires
│       ├── home.js             # page projet (lit MANIFEST.json)
│       ├── launches.js         # agrégation par Launch_Tag + filtres
│       └── objects.js          # charges utiles + filtres
├── data/gcat/                  # données brutes GCAT + MANIFEST.json
├── scripts/fetch_gcat.py       # récupération des TSV
└── .github/workflows/
    ├── update-gcat.yml         # récupération hebdomadaire des données
    └── pages.yml               # publication du site sur GitHub Pages
```

## Licences

- **Données** : © Jonathan McDowell, *General Catalog of Artificial Space Objects*,
  licence **CC BY 4.0**. Toute réutilisation doit créditer :
  > McDowell, J., 2020: General Catalog of Artificial Space Objects,
  > <https://planet4589.org/space/gcat>
- **Code** du dépôt : libre d'usage et de modification dans le cadre de ce projet.
