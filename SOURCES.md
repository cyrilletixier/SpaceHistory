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
| `launchlog.tsv` | `…/tsv/derived/launchlog.tsv` | page **Lancements** (agrégé par `Launch_Tag`) et tous les classements |
| `psatcat.tsv` | `…/tsv/cat/psatcat.tsv` | explorateur objet par objet (à venir) |
| `satcat.tsv` | `…/tsv/cat/satcat.tsv` | analyses à venir (masse, orbite) |
| `active.tsv` | `…/tsv/derived/active.tsv` | satellites actifs (`objets.html`) |
| `currentcat.tsv` | `…/tsv/derived/currentcat.tsv` | objets en orbite, débris compris |
| `geotab.tsv` | `…/tsv/derived/geotab.tsv` | journal GEO |
| `ftocat.tsv` | `…/tsv/cat/ftocat.tsv` | échecs de mise en orbite |
| `deepcat.tsv` | `…/tsv/cat/deepcat.tsv` | espace lointain |
| `sites.tsv` | `…/tsv/tables/sites.tsv` | **table de référence** : code de site → nom |
| `orgs.tsv` | `…/tsv/tables/orgs.tsv` | **table de référence** : code d'organisation ou d'État → nom |
| `lp.tsv` | `…/tsv/tables/lp.tsv` | **table de référence** : code de pas de tir → nom |

Base des URL : `https://planet4589.org/space/gcat/tsv/`.

### Pièges connus du format

1. **Une ligne = un objet, pas un lancement** (`Piece`). Compter les lignes de
   `launchlog.tsv` donne un nombre d'objets ; le nombre de lancements est le nombre de
   `Launch_Tag` distincts.
2. **Dates non ISO** : `1957 Oct  4 1928:07`, parfois vagues (`?` sur le jour, absence
   d'heure). Un parseur strict les perd ou les invente.
3. **Lignes de commentaires** préfixées `#` et champs complétés par des espaces.
4. **Codes abrégés** (`SPXS`, `GIK-1`, `RVSN`, `SU`…) : lisibles uniquement via les tables
   de référence du GCAT (`orgs.tsv`, `sites.tsv`) — voir la section 4.
5. **Homonymes de vocabulaire** : `Launch_Code` porte l'**issue** du tir, tandis que
   `LVState` et `SatState` portent des codes de **pays**. Confondre les deux produit des
   taux de réussite absurdes (c'est le bug corrigé en amont de la v1 du site).
6. **Pas de clé étrangère explicite** entre lancements et objets au-delà de `Launch_Tag` /
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
- **Statut** : dérivé de `Launch_Code`, comparé par préfixe (`OF40`, `OS89` sont des
  variantes suffixées). `OF*` = échec, `OS*` et `DS*` = succès, tout le reste =
  indéterminé. **L'échec prime** : un seul `OF` suffit à qualifier le tir, même si une
  autre pièce porte `OS`.
- **Statuts indéterminés** : `NS` (13), `XS` (11), `NF` (2) sur 32 246 lignes — soit 26
  des 7 460 lancements. Ce ne sont pas des issues orbitales ; ils sont exclus du
  dénominateur des taux plutôt que classés d'autorité.
- **Objets** : nombre de lignes rattachées au `Launch_Tag`.
- **Pays de l'engin** (`LVState`) : champ **par pièce**, renseigné sur la totalité des
  32 246 lignes. Le pays du lanceur est constant au sein d'un tir ; le build retient la
  première valeur non vide de chaque `Launch_Tag`. Contrôle de vraisemblance : le palmarès
  obtenu (États-Unis, URSS, Russie, Chine, France, Japon, Inde…) suit l'histoire des
  lancements — c'est ce qui valide l'hypothèse.

### Points à trancher pour les classements à venir

- Faut-il classer les **lancements** ou les **objets** ? Le rideshare et les méga-constellations
  rendent les deux palmarès très différents.
- Faut-il compter la **masse** mise en orbite plutôt que le nombre d'objets ? `satcat.tsv`
  fournit `Mass` pour la majorité des charges utiles récentes.
- Un lanceur **réutilisé** compte comme un lancement (oui), mais pas comme un exemplaire neuf.
- Les **pas de tir** (`lp.tsv`) existent comme table de référence mais ne sont pas encore
  agrégés : un classement par rampe serait le prolongement naturel du classement par site.

## 4. Traduction des codes en libellés

Le GCAT publie ses propres tables de référence. Ce sont elles qui servent de dictionnaire :
**aucune liste de correspondance n'est écrite à la main**, ce qui garantit que chaque
libellé affiché reste vérifiable à la source.

| Champ lu | Table | Clé | Exemple |
|---|---|---|---|
| `Launch_Site` | `sites.tsv` | `Site` | `GIK-1` → Plesetsk |
| `Agency` | `orgs.tsv` | `Code` | `RVSN` → *Rakentiye Voiska Strategicheskogo Naznacheniye* |
| `LVState` | `orgs.tsv` | `Code` | `SU` → SSSR |
| `SatOwner` | `orgs.tsv` | `Code` | `SPXS` → SpaceX |

Règles de résolution, dans l'ordre :

1. correspondance exacte du code ;
2. si le code se termine par `?` (rattachement douteux chez le GCAT : `TYSC?`, `KVR?`),
   on réessaie sans le `?` — mieux vaut un nom assorti d'un doute qu'un code nu ;
3. code composite (`NASA/USAF`, `CGWIC/SAST`) : chaque composante est traduite séparément
   puis jointe par ` / ` ;
4. sinon le code brut est affiché tel quel — jamais inventé, jamais deviné.

Le libellé affiché suit la chaîne `ShortName` → `ShortEName` → `Name` → code brut. Le nom
complet (`Name`) sert d'infobulle et, pour les agences, de seconde ligne sous le sigle :
`RVSN` seul ne dit rien, son nom développé si.

### Couverture constatée

Sur la synchronisation de référence (32 246 objets, 7 460 lancements) :

- **sites** : 712 entrées, **aucun** code de site non résolu ;
- **organisations et États** : 4 087 entrées, **4** codes non résolus — `10ADS`, `2SLS`,
  `3SLS`, `4SLS`, des escadrons de lancement de l'US Air Force absents d'`orgs.tsv`
  (54 lancements à eux quatre), affichés tels quels ;
- **États** : 20 valeurs distinctes — `US`, `SU`, `CN`, `RU`, `F`, `IN`, `J`, `NZ`,
  `I-ESA`, `KR`, `IR`, `IL`, `I`, `KP`, `D`, `I-ELDO`, `CYM`, `UK`, `BR`, `AU`. Les préfixes
  `I-` (`I-ESA`, `I-ELDO`, `I-INT`, `I-EU`…) désignent des organisations internationales,
  pas des États : le classement « pays » les laisse en lignes distinctes plutôt que de les
  rattacher arbitrairement à un pays hôte.

Le journal du build imprime cette couverture à chaque exécution : vocabulaire complet de
`Launch_Code` et `LVState`, codes non résolus et leur poids, dix premières lignes de chaque
classement traduit. Une dérive du catalogue se voit donc dans le journal, jamais dans les
chiffres publiés sans trace.

## 5. Citation

> McDowell, J., 2020: General Catalog of Artificial Space Objects,
> <https://planet4589.org/space/gcat> (CC BY 4.0)
