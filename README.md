# SpaceHistory

Exploration et classements sur l'histoire spatiale, à partir d'une source unique :
le **General Catalog of Artificial Space Objects (GCAT)** de Jonathan McDowell.

Site publié : **<https://cyrilletixier.github.io/SpaceHistory/>**

Le dépôt remplit trois rôles :

1. **entrepôt de données brutes** — `data/gcat/` contient les fichiers TSV du GCAT, tels que publiés,
   resynchronisés automatiquement chaque semaine ;
2. **code de calcul** — `scripts/build_site.py` (et ses modules `scripts/sitebuild/`) agrège les TSV et produit les classements ;
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
| `launches.html` | explorateur : toutes les tentatives orbitales depuis 1957, filtrables par vol habité |
| `charges-utiles.html` | catalogue des charges utiles, filtrable par vol (`?vol=`), par statut et par équipage |
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
| `satcat.tsv` | `cat/` | catalogue complet de tous les objets spatiaux | **masse, orbite et statut actuel** des charges utiles, **marqueur d'équipage** |
| `psatcat.tsv` | `cat/` | catalogue des charges utiles (programme, catégorie, commentaire) | **nom d'usage** des charges utiles |
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

L'explorateur des lancements porte des colonnes calculées au build à partir de
`satcat.tsv` (et de `ftocat.tsv` pour les charges perdues) :

- **Charge utile** = ligne de catalogue dont le champ `Type` commence par `P` (le GCAT
  distingue les étages `R`, les débris `D`, les composants…). Chaque charge utile est
  rattachée à son vol par `Launch_Tag`.
- **Masse en orbite** = somme du champ `Mass` (kg) des charges utiles **cataloguées en
  orbite** pour ce vol, après correction de la masse orbitale des premiers vaisseaux
  habités (voir *Correction des vaisseaux habités précoces*). Le `0` que le GCAT écrit
  quand la masse est inconnue (plus de 32 000 objets) est traité comme une absence, pas
  comme un zéro : ces charges utiles sont écartées de la somme, et le nombre de masses
  réellement additionnées est visible au survol. Un vol sans aucune masse connue affiche
  « — ». Une charge perdue lors d'un échec n'entre pas dans la somme (elle n'a pas été mise
  en orbite) : elle apparaît en revanche sur la page des charges utiles, avec le statut
  « échec ».
- **Destination** = famille d'orbite déduite de `OpOrbit` : `LLEO`/`LEO` → **LEO**,
  `MEO`, `GEO`/`GSO`, `HEO`, `LLO`/`LMO`/`LSO` → **Lunaire**, `EEO`/`HCO` →
  **Interplanétaire**. Le qualificatif après la barre oblique (`LLEO/I`, `GEO/T`) précise
  l'orbite sans en changer la famille. Un code inconnu n'est pas traduit : il s'affiche tel
  quel et le journal du build le signale, comme pour les codes d'agence.
- **Objets / charges utiles** : les deux colonnes sont fusionnées en une seule,
  cliquable — objets du tir, puis charges utiles après la barre oblique. Un clic renvoie
  vers `charges-utiles.html?vol=<Launch_Tag>`, dont le bandeau affiche combien d'objets
  du tir (étages, débris) ne sont pas des charges utiles listées. Les noms restent dans
  `launches.json` (champ `n`) pour que la recherche de l'explorateur continue de fonctionner.
- **Statut d'une charge utile** = état **actuel**, lu dans le champ `Status` de
  `satcat.tsv`, et non déduit de la table d'origine : figurer dans `satcat.tsv` veut
  seulement dire « a été mis en orbite » (Sputnik 1 y est, avec `R` : rentré le
  4 janvier 1958). Ce champ nomme l'événement qui clôt la phase en cours de l'objet, et
  `DDate` en donne la date (vide tant que la phase dure). Les codes sont regroupés selon la
  documentation du GCAT (*phases.html*) : `O`, `OX`, `AO`, `N`, `NA`, `LEASE` → **en
  orbite** ; `R`, `AR`, `D`, `AS`, `S` → **rentré** ; `L`, `AL`, `LF`, `TX`, `DEP` → **posé** ;
  `DSO`, `DSA`, `EO`, `EAO`, `EN` → **espace lointain** ; `DK`, `GRP`, `ATT`, `TFR`,
  `EVA DP`, `EVA RP` → **rattaché** à un autre objet ; `E`, `C`, `F`, `AF` → **détruit** ;
  les charges de `ftocat.tsv` restent en **échec**. Le suffixe `?` ne change pas la famille.
  Un code non rangé s'affiche tel quel et le journal du build le signale. Le code brut et
  `DDate` restent au survol ; la table code → statut est écrite une seule fois dans
  `charges-utiles.json` (champ `statuts`).
- **Noms** : le nom principal reste le `Name` du GCAT, tiré de l'opérateur (`1-y ISZ`).
  Dessous s'affichent les autres noms du catalogue quand ils diffèrent : `PLName` (nom
  constructeur, `PS-1`) et le `Name` de `psatcat.tsv` (nom d'usage, `First Sputnik`,
  crochets de nom non officiel retirés). La jointure se fait par `JCAT`, jamais par le nom ;
  la recherche de la page porte sur tous ces noms.

### Vols habités

Le caractère habité d'un vol n'est **pas** déduit du nom de la mission : les libellés du
GCAT sont hétérogènes et une même famille de véhicule couvre des vols habités et des vols
de test sans personne à bord. Il vient d'un attribut du catalogue, le champ `Type` des
charges utiles, qui encode trois choses sur ses premiers caractères :

| Position | Valeur | Signification |
|---|---|---|
| 1re lettre | `P` | classe d'objet : charge utile (`R` = étage, `D` = débris…) |
| **2e caractère** | **`H`** | **le vol emportait un équipage** |
| 4e caractère | `H` | le véhicule est *habitable*, quel que soit le vol |

Seul le 2e caractère répond à la question posée ; le 4e décrit le matériel. Les cas de
contrôle du catalogue séparent nettement les deux :

| Vol | `Type` | Équipage | Lecture |
|---|---|---|---|
| Shenzhou 1 à 4 | `PP-H` | non | véhicule habitable, vol de test |
| Crew Dragon Demo-1 | `PP-H-V-` | non | idem |
| Apollo 6 | `PP-H` | non | idem (premier vol de la Saturn V avec un CSM) |
| Buran OK-1K | `P` | non | ni l'un ni l'autre marqueur |
| Shenzhou 5 | `PH-H` | **oui** | premier vol habité chinois |
| Soyouz TM-2 | `PH H V` | **oui** | |
| Apollo 7 | `PH-H` | **oui** | |

La règle retenue lit donc le 2e caractère. Sur le millésime courant du catalogue elle
désigne **360 vols**, ce qui recoupe le décompte des vols habités établi indépendamment — un
total qui serait très différent si la règle visait le véhicule ou les noms de mission.

Deux précautions d'agrégation :

- **Par vol, pas par objet** : une mission navette compte pour un lancement, pas pour ses
  sept astronautes ni pour ses trois pièces. Un vol est habité dès qu'**une** de ses charges
  utiles porte le marqueur.
- **Échecs compris** : le marqueur est lu dans `satcat.tsv` *et* dans `ftocat.tsv`, car un
  vol habité qui échoue reste un vol habité (Soyouz MS-10, navette Challenger). Ces lignes
  ne pèsent pas sur la masse en orbite, mais comptent pour l'équipage.

`.github/workflows/check-build.yml` verrouille le résultat : le total doit rester dans la
fourchette 340–400, et sept vols de référence (Apollo 6 et 7, Buran, Shenzhou 1 et 5, Crew
Dragon Demo-1, Shenzhou 12) doivent être marqués dans le bon sens. Un déplacement de
l'encodage rendrait ces contrôles rouges plutôt que de vider silencieusement le filtre.

### Correction des vaisseaux habités précoces

Pour les 22 premiers vaisseaux habités, le champ `Mass` du GCAT ne donne pas la masse du
vaisseau **placé en orbite**. La table `ORBITAL_MASS_CORRECTIONS`
(`scripts/sitebuild/payloads.py`) lui substitue la valeur publiée par la NASA (NSSDCA),
fiche par fiche :

| Véhicule | Vols couverts | Masse orbitale retenue |
|---|---|---|
| Vostok | Vostok 1 à 6 | 4 725 kg (Vostok 1), 4 730 kg (Vostok 2 à 6) |
| Voskhod | Voskhod 1 et 2 | 5 320 kg, 5 682 kg |
| Mercury | Mercury 6 à 9 | 1 355 kg |
| Gemini | Gemini 3 à 12 | de 3 228 à 3 812 kg selon le vol |

Règles de la correction :

- **correspondance exacte** sur le champ `Name` de `satcat.tsv` : ni recherche floue, ni nom
  recomposé — la même exigence que pour les libellés, qui ne sont jamais réécrits à la main ;
- **une entrée par vol** : Vostok 1 et Vostok 2 sont deux lignes distinctes, comme URSS et
  Russie restent deux États ; aucune entrée ne regroupe plusieurs missions ;
- **deux masses conservées** : `mass_gcat` (la valeur du catalogue) et `mass_corrected`
  (la valeur retenue). C'est la seconde qui alimente la colonne « Masse » du catalogue des
  charges utiles *et* la masse en orbite de l'explorateur, donc les sommes par vol, par
  décennie et par année ;
- **la source est dans la table**, à côté de la masse (`NASA NSSDCA 1961-012A`…) : une
  correction non sourcée n'a pas sa place ici ;
- **une masse inconnue reste une absence** : la correction rectifie une valeur existante,
  elle ne remplit jamais un trou.

Le journal du build verrouille l'application de la table :

```
masses corrigées : 22 charge(s) utile(s)
```

Il signale en plus deux anomalies possibles — une entrée de la table qui ne rencontre
**aucune** charge utile du catalogue (nom renommé côté GCAT : la correction ne s'applique
plus à rien) et un vol habité dont le nom évoque `vostok|voskhod|mercury|gemini` sans
correction associée (un vol précoce oublié). Les deux sortent en `::warning::` plutôt que
de rester silencieuses.

Vérification locale :

```bash
python3 scripts/build_site.py --data data/gcat --out _site
python3 - <<'PY'
import json
from pathlib import Path

payloads = json.loads(
    Path("_site/data/charges-utiles.json").read_text(encoding="utf-8")
)["payloads"]
print({item["n"]: item["m"] for item in payloads if item["n"] == "Vostok 1"})
PY
# attendu : {'Vostok 1': 4725}
```

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
│   ├── build_site.py           # point d'entrée du build : orchestration + rendu → _site/
│   ├── sitebuild/              # modules du build (chacun < 300 lignes)
│   │   ├── constants.py        # chemins, familles d'orbites, définition des classements
│   │   ├── gcat.py             # lecture des TSV, traduction des codes, dates
│   │   ├── launches.py         # lancements : issue, code représentatif
│   │   ├── payloads.py         # charges utiles : masse (corrections NSSDCA), statut, noms,
│   │   │                       # destination, vol habité
│   │   ├── stats.py            # agrégations, classements, faits marquants
│   │   ├── rendering.py        # formatage, gabarits, écriture des JSON
│   │   └── reports.py          # journal du build (orbites, statuts, masses corrigées,
│   │                           # vols habités, codes)
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
