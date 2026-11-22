# data/gcat — données brutes GCAT

Ce dossier contient une copie **non transformée** des tables TSV publiées par
Jonathan McDowell (GCAT), plus un manifeste généré.

- Source : <https://planet4589.org/space/gcat/tsv/>
- Licence : CC BY 4.0 — © Jonathan McDowell
- **Ne pas éditer les fichiers à la main** : ils sont réécrits par
  `scripts/fetch_gcat.py` (workflow `.github/workflows/update-gcat.yml`, chaque lundi).

| Fichier | Origine | Contenu |
|---|---|---|
| `launchlog.tsv` | `derived/` | journal des lancements orbitaux, une ligne par objet lancé |
| `active.tsv` | `derived/` | satellites actuellement actifs |
| `currentcat.tsv` | `derived/` | objets actuellement en orbite, débris compris |
| `geotab.tsv` | `derived/` | journal des satellites géostationnaires |
| `satcat.tsv` | `cat/` | catalogue complet de tous les objets spatiaux |
| `psatcat.tsv` | `cat/` | catalogue des charges utiles |
| `ftocat.tsv` | `cat/` | catalogue des échecs de mise en orbite |
| `deepcat.tsv` | `cat/` | catalogue de l'espace lointain |
| `MANIFEST.json` | généré | URL, taille, lignes, SHA-256, date de récupération |

## Rafraîchir en local

```bash
python3 scripts/fetch_gcat.py --out data/gcat
```

## Format

Bloc de commentaires `#`, ligne d'en-ête tabulée, puis une ligne par enregistrement.
Dates au format `YYYY Mon DD HHMM:SS`, parfois vagues (`?`). Champs complétés par des espaces.
