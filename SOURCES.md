# Sources et méthode

Document de référence : d'où viennent les données, pourquoi cette source, et quelles
règles sont appliquées pour produire des classements défendables.

## 1. Source retenue : GCAT

**General Catalog of Artificial Space Objects** — Jonathan McDowell (Harvard-Smithsonian
Center for Astrophysics), <https://planet4589.org/space/gcat/>.

C'est le catalogue de référence derrière *Jonathan's Space Report*. Il est :

- **complet historiquement** : 1957 → aujourd'hui, y compris les échecs de mise en orbite ;
- **structuré** : lancements, objets, sites, véhicules, opérateurs, orbites dans des tables
  relationnelles en TSV ;
- **réutilisable** : licence CC BY 4.0, contrairement aux catalogues officiels restrictifs ;
- **mis à jour en continu** : d'où la resynchronisation hebdomadaire de ce dépôt.

Fichiers utilisés (copie brute dans `data/gcat/`) :

| Fichier | URL source | Usage dans ce dépôt |
|---|---|---|
| `launchlog.tsv` | `…/tsv/derived/launchlog.tsv` | page **Lancements** (agrégé par `Launch_Tag`) |
| `psatcat.tsv` | `…/tsv/cat/psatcat.tsv` | page **Objets** (charges utiles) |
| `satcat.tsv` | `…/tsv/cat/satcat.tsv` | repli pour la page Objets + analyses à venir |
| `active.tsv` | `…/tsv/derived/active.tsv` | satellites actifs |
| `currentcat.tsv` | `…/tsv/derived/currentcat.tsv` | objets en orbite, débris compris |
| `geotab.tsv` | `…/tsv/derived/geotab.tsv` | journal GEO |
| `ftocat.tsv` | `…/tsv/cat/ftocat.tsv` | échecs de mise en orbite |
| `deepcat.tsv` | `…/tsv/cat/deepcat.tsv` | espace lointain |

Base des URL : `https://planet4589.org/space/gcat/tsv/`.

### Pièges connus du format

1. **Une ligne = un objet, pas un lancement** (`Piece`). Compter les lignes de
   `launchlog.tsv` donne un nombre d'objets ; le nombre de lancements est le nombre de
   `Launch_Tag` distincts.
2. **Dates non ISO** : `1957 Oct  4 1928:07`, parfois vagues (`?` sur le jour, absence
   d'heure). Un parseur strict les perd ou les invente.
3. **Lignes de commentaires** préfixées `#` et champs complétés par des espaces.
4. **Codes propriétaires / agences** abrégés (`SPXS`, `ONEWEBN`, `PLAN`…) : nécessitent une
   table de correspondance pour un affichage lisible.
5. **Pas de clé étrangère explicite** entre lancements et objets au-delà de `Launch_Tag` /
   `JCAT`.

## 2. Sources écartées ou complémentaires

| Source | Statut | Raison |
|---|---|---|
| **Space-Track.org** (US Space Force) | écartée du dépôt | conditions d'utilisation interdisant la redistribution — utilisable en local seulement |
| **CelesTrak** (`celestrak.org/pub/satcat.csv`) | contrôle croisé | accessible sans compte, mais ne contient que les objets catalogués (aucun échec de lancement) |
| **UNOOSA — Online Index of Objects Launched into Outer Space** | contrôle croisé | registre officiel ONU, uniquement les succès enregistrés, publication tardive |
| **Launch Library 2 / The Space Devs** | complément possible | API pratique pour l'actualité et l'à-venir ; licence et quotas à vérifier avant intégration |
| **Wikipédia — listes de lancements orbitaux** | contrôle croisé | CC BY-SA, structuration faible, mais utile pour arbitrer un cas douteux |
| **JSR Launch Vehicle Database** (prédécesseur du GCAT) | historique | figé, remplacé par le GCAT |
| **FAA / AST** | périmètre restreint | lancements autorisés aux États-Unis uniquement |

## 3. Règles de comptage

- **Lancement** : tentative de lancement **orbital**, échecs inclus, suborbital exclu.
- **Identifiant** : `Launch_Tag`. Les objets d'un même tir sont agrégés.
- **Statut** : `echec` si un code `LVState`/`SatState` vaut `OF`, sinon `succes` si `OS`,
  sinon `inconnu`. Le code brut est affiché à côté pour audit.
- **Objets** : nombre de lignes rattachées au `Launch_Tag` ; les charges utiles sont
  distinguées par `Type` commençant par `P`.
- **Pays** : champ `Agency` du GCAT, non retraité (URSS / Russie / Ukraine séparés).

### Points à trancher pour les classements à venir

- Faut-il classer les **lancements** ou les **objets** ? Le rideshare et les méga-constellations
  rendent les deux palmarès très différents.
- Faut-il compter la **masse** mise en orbite plutôt que le nombre d'objets ? `satcat.tsv`
  fournit `Mass` pour la majorité des charges utiles récentes.
- Un lanceur **réutilisé** compte comme un lancement (oui), mais pas comme un exemplaire neuf.

## 4. Citation

> McDowell, J., 2020: General Catalog of Artificial Space Objects,
> <https://planet4589.org/space/gcat> (CC BY 4.0)
