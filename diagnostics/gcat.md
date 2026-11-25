# Diagnostic GCAT

Rapport généré automatiquement : valeurs réellement présentes dans
les TSV, colonne par colonne. Il existe pour vérifier le vocabulaire
des codes d'issue, pas pour publier quoi que ce soit.

## `launchlog.tsv`

- colonnes : **20**
- lignes de données : **32258**
- largeurs rencontrées : [20]

Deux premières lignes brutes (onglets visibles, tronquées) :

```
'# Updated 2026 Nov 23 0024:13'
'1957 ALP  \t1957 Oct  4 1928:34\t1957 ALP 2\tP           \t1-y ISZ\tPS-1\tS00002    \tOKB1\tSU\tSputnik 8K71PS\tM1-PS\t-\tNIIP-5\tLC1\t-\t-\tMVS\tSU\tOS  \tEnergiya'
```

### Valeurs réelles par colonne

| # | colonne | non vides | OS | OF | commence par O | valeurs les plus fréquentes |
|---|---|---|---|---|---|---|
| 0 | `Launch_Tag` | 32258 | 0 | 0 | 0 | `2021-006`×145, `2025-276`×130, `2025-009`×116, `2024-149`×115, `2026-227`×115, `2023-001`×114 |
| 1 | `Launch_Date` | 32258 | 0 | 0 | 0 | `2021 Jan 24 1500`×145, `2025 Nov 28 1844:30`×130, `2025 Jan 14 1909:00`×116, `2024 Aug 16 1856:00`×115, `2026 Oct  1 1832:00`×115, `2023 Jan  3 1455:56`×114 |
| 2 | `Piece` | 32258 | 0 | 0 | 0 | `2026-F07`×40, `2014-F02`×30, `1982-F01`×25, `1983-F01`×25, `1991-F02`×25, `1985-089`×24 |
| 3 | `Type` | 32258 | 0 | 0 | 0 | `P      O  M`×10527, `P`×8494, `P      R  M`×1643, `P   G`×1011, `P      L  M`×910, `PX-RT--`×732 |
| 4 | `Name` | 32258 | 25 | 1 | 1329 | `Spuskaemaya Kapsula`×368, `Molniya-1`×86, `Molniya-3`×53, `Kosmos`×50, `[Kosmos]`×45, `Raduga`×35 |
| 5 | `PLName` | 32258 | 25 | 0 | 1418 | `ESO`×766, `SpK`×215, `Strela-3`×118, `SRV`×108, `-`×85, `Qianfan`×72 |
| 6 | `JCAT` | 32258 | 0 | 0 | 0 | `S00002`×1, `S00003`×1, `F00002`×1, `S00004`×1, `F00004`×1, `F00006`×1 |
| 7 | `SatOwner` | 32258 | 17 | 0 | 1165 | `SPXS`×13182, `PVO`×1017, `PLAN`×572, `GUKOSR`×543, `ONEWEBN`×526, `KUIP`×438 |
| 8 | `SatState` | 32258 | 0 | 0 | 3 | `US`×20332, `SU`×4052, `CN`×2316, `RU`×1417, `UK`×849, `J`×483 |
| 9 | `LV_Type` | 32258 | 1 | 0 | 1 | `Falcon 9`×16443, `Kosmos 11K65M`×1480, `Soyuz-U`×901, `Soyuz-2-1B`×834, `Space Shuttle`×493, `Tsiklon-3`×349 |
| 10 | `Flight_ID` | 32258 | 1 | 0 | 4 | `-`×238, `Y1`×164, `Y2`×158, `107/B1058.5  F107`×145, `564/B1071.30 F570`×130, `Y7`×116 |
| 11 | `Platform` | 32258 | 0 | 0 | 36 | `-`×31435, `MLP1`×174, `MLP2`×141, `DFHT`×118, `MLP3`×93, `L-1011`×82 |
| 12 | `Launch_Site` | 32258 | 0 | 0 | 0 | `CC`×9239, `VSFBS`×6283, `KSC`×2770, `NIIP-53`×2513, `GIK-5`×1382, `NIIP-5`×1113 |
| 13 | `Launch_Pad` | 32258 | 0 | 0 | 155 | `LC40`×7923, `SLC4E`×6642, `LC39A`×2553, `LC31`×924, `LC1`×798, `LC132/2`×585 |
| 14 | `Ascent_Site` | 32258 | 0 | 0 | 0 | `-`×32111, `WTR`×82, `WI`×34, `ETR`×15, `CELS`×9, `KMR`×5 |
| 15 | `Ascent_Pad` | 32258 | 0 | 0 | 0 | `-`×32111, `PAWA`×41, `LP3`×35, `MFWA`×15, `LP15`×14, `LP1`×12 |
| 16 | `Agency` | 32258 | 259 | 0 | 273 | `SPX`×16658, `RVSN`×2162, `UNKS`×1854, `AE`×781, `SAST`×763, `CALT`×751 |
| 17 | `LVState` | 32258 | 0 | 0 | 0 | `US`×21037, `SU`×4029, `CN`×2417, `RU`×2093, `F`×1260, `IN`×593 |
| 18 | `Launch_Code` | 32258 | 30708 | 1076 | 31784 | `OS`×30505, `OF`×937, `DS`×446, `OF40`×117, `OS89`×73, `OS95`×52 |
| 19 | `LTCite` | 32258 | 0 | 0 | 10 | `Wire`×12692, `nasaspaceflight.com`×4908, `SpaceX`×4332, `AK15/RAEX`×2422, `spaceflightnow.com`×1417, `VCR`×474 |

### Colonnes à codes courts

- `LVState` (#17, 100% de codes courts) : `US`×21037, `SU`×4029, `CN`×2417, `RU`×2093, `F`×1260, `IN`×593, `J`×336, `NZ`×291
- `SatState` (#8, 99% de codes courts) : `US`×20332, `SU`×4052, `CN`×2316, `RU`×1417, `UK`×849, `J`×483, `F`×216, `D`×209
- `Launch_Code` (#18, 99% de codes courts) : `OS`×30505, `OF`×937, `DS`×446, `OF40`×117, `OS89`×73, `OS95`×52, `OS75`×46, `OS85`×19
- `Agency` (#16, 58% de codes courts) : `SPX`×16658, `RVSN`×2162, `UNKS`×1854, `AE`×781, `SAST`×763, `CALT`×751, `AFSSD`×695, `ULAL`×517
- `Launch_Site` (#12, 52% de codes courts) : `CC`×9239, `VSFBS`×6283, `KSC`×2770, `NIIP-53`×2513, `GIK-5`×1382, `NIIP-5`×1113, `VS`×1014, `CSG`×864

### Échantillons par `Launch_Code`

- `OS` (30505 pièces)
  - 1957 Oct  4 1928:34 · Sputnik 8K71PS · 1-y ISZ
  - 1957 Nov  3 0230:42 · Sputnik 8K71PS · 2-y ISZ
  - 1958 Feb  1 0347:56 · Jupiter C · Explorer I
  - 1958 Mar 17 1215:41 · Vanguard · Vanguard I
- `OF` (937 pièces)
  - 1957 Dec  6 1644:35 · Vanguard · Vanguard
  - 1958 Feb  5 0733 · Vanguard · Vanguard
  - 1958 Mar  5 1827:57 · Jupiter C · Explorer II
  - 1958 Apr 27 0901 · Sputnik 8A91 · ISZ
- `DS` (446 pièces)
  - 1959 Jan  2 1641:21 · Vostok-L 8K72 · AMS Luna-1
  - 1959 Mar  3 0510:56 · Juno II · Pioneer IV
  - 1959 Sep 12 0639:42 · Vostok-L 8K72 · AMS Luna-2
  - 1959 Oct  4 0043:39 · Vostok-L 8K72 · AMS Luna-3
- `OF40` (117 pièces)
  - 1961 Feb  4 0118:03 · Molniya 8K78 · Tyazholiy Sputnik
  - 1961 Aug 23 1004:10 · Atlas Agena B · Ranger 1
  - 1961 Nov 18 0812:21 · Atlas Agena B · Ranger 2
  - 1962 Aug 25 0218:45 · Molniya 8K78 · AMS
- `OS89` (73 pièces)
  - 2017 Jul 14 0636:49 · Soyuz-2-1A · Kanopus-V-IK No. 2
  - 2017 Jul 14 0636:49 · Soyuz-2-1A · NORSAT-1
  - 2017 Jul 14 0636:49 · Soyuz-2-1A · Iskra-MAI-85
  - 2017 Jul 14 0636:49 · Soyuz-2-1A · NORSAT-2
- `OS95` (52 pièces)
  - 2025 Dec 28 1318:05 · Soyuz-2-1B · Marafon No. 1
  - 2025 Dec 28 1318:05 · Soyuz-2-1B · Marafon No. 2 GMM?
  - 2025 Dec 28 1318:05 · Soyuz-2-1B · Zorkiy-2M VPE
  - 2025 Dec 28 1318:05 · Soyuz-2-1B · Aist-2T No. 1
- `OS75` (46 pièces)
  - 1958 Oct 11 0842:13 · Thor Able I · Pioneer I
  - 1965 Jan 22 0752:00 · Thor Delta C · Tiros 9
  - 1969 Jun 21 0847:58 · Thor Delta E1 · IMP 5
  - 1971 Sep 29 0945:00 · Thor Delta N · OSO 7
- `OS85` (19 pièces)
  - 1997 Jul  9 1304 · Delta 7920-10C · Iridium 15
  - 1997 Jul  9 1304 · Delta 7920-10C · Iridium 17
  - 1997 Jul  9 1304 · Delta 7920-10C · Iridium 20
  - 1997 Jul  9 1304 · Delta 7920-10C · Iridium 18
- `NS` (13 pièces)
  - 1965 Jan 19 1404:00 · Titan II GLV · Gemini II
  - 1965 Dec 16 1409:22 · R-36O 8K69 · OGCh No. 01L
  - 1966 Feb  5 1219:49 · R-36O 8K69 · OGCh No. 02L
  - 1966 Feb 26 1612:01 · Saturn IB · Apollo AS-201
- `XS` (11 pièces)
  - 1969 Jul 21 1754:01 · LM AS · Eagle
  - 1969 Nov 20 1425:56 · LM AS · Intrepid
  - 1970 Sep 21 0743 · E-8-5 VA · Luna-16 VA
  - 1971 Feb  6 1848 · LM AS · Antares
- `OF50` (6 pièces)
  - 1966 Jul 14 0210:02 · Atlas D · OV1-8
  - 1966 Jul 14 0210:02 · Atlas D · OV1-7
  - 1993 Mar 25 2138:02 · Atlas I · UHF F/O F1
  - 2001 Jul 12 2158 · Ariane 5G · Artemis
- `OF25` (6 pièces)
  - 1979 Feb  6 0846 · N-1 · Ayame
  - 1981 Aug  6 0816:00 · Atlas SLV-3D Centaur · FLTSATCOM F5
  - 1990 Mar 14 1152:31 · Commercial Titan 3 · INTELSAT 603
  - 1993 Apr 27 1035:00 · Soyuz-U · Kosmos-2243

## `active.tsv`

- colonnes : **21**
- lignes de données : **17324**
- largeurs rencontrées : [21]

### Valeurs réelles par colonne

| # | colonne | non vides | OS | OF | commence par O | valeurs les plus fréquentes |
|---|---|---|---|---|---|---|
| 0 | `JCAT` | 17324 | 0 | 0 | 0 | `S00965`×1, `S01002`×1, `S01291`×1, `S01315`×1 |
| 1 | `Piece` | 17324 | 0 | 0 | 0 | `2026-227`×11, `1998-069F`×3, `2026-254`×3, `1998-067`×3 |
| 2 | `Name` | 17324 | 2 | 0 | 766 | `CSTP`×6, `Cartosat-2 Series Sat…`×4, `Digui Tongxin Shiyan …`×3, `Daqi Huanjing Jiance …`×2 |
| 3 | `LaunchDate` | 17324 | 0 | 0 | 0 | `2025 Nov 28 1844:30`×124, `2026 Oct  1 1832:00`×109, `2026 Mar 30 1102:00`×100, `2025 Jan 14 1909:00`×95 |
| 4 | `LState` | 17324 | 0 | 0 | 0 | `US`×13945, `CN`×1565, `F`×811, `RU`×571 |
| 5 | `Owner` | 17324 | 0 | 0 | 768 | `SPXS`×11187, `ONEWEBN`×523, `KUIP`×392, `NROC`×302 |
| 6 | `OwnState` | 17324 | 0 | 0 | 1 | `US`×13265, `CN`×1524, `UK`×761, `RU`×388 |
| 7 | `UNState` | 17324 | 0 | 0 | 0 | `US`×8209, `[US]`×5009, `[CN]`×1076, `UK`×695 |
| 8 | `Manu` | 17324 | 45 | 0 | 863 | `SPXS`×11612, `ONEWUS`×646, `KUIP`×392, `SECM`×293 |
| 9 | `ManuState` | 17324 | 0 | 0 | 0 | `US`×13873, `CN`×1547, `RU`×368, `F`×180 |
| 10 | `LaunchMass` | 17324 | 0 | 0 | 0 | `575.000`×5019, `730.000`×2554, `305.000`×1293, `297.000`×921 |
| 11 | `DryMass` | 17324 | 0 | 0 | 0 | `530.000`×5019, `700.000`×2823, `290.000`×1413, `275.000`×908 |
| 12 | `Class` | 17324 | 0 | 0 | 0 | `B`×14683, `D`×1334, `C`×970, `A`×316 |
| 13 | `Category` | 17324 | 0 | 0 | 0 | `COM`×14144, `IMG`×1020, `TECH`×589, `IMG-R`×267 |
| 14 | `TF` | 17324 | 0 | 0 | 0 | `-`×17245, `Z`×32, `E`×31, `U`×16 |
| 15 | `MVR` | 17324 | 0 | 0 | 0 | `M`×14988, `-`×2335, `N`×1 |
| 16 | `Perigee` | 17324 | 0 | 0 | 0 | `284`×889, `283`×603, `285`×373, `264`×345 |
| 17 | `Apogee` | 17324 | 0 | 0 | 0 | `292`×933, `291`×412, `279`×321, `337`×274 |
| 18 | `Inc` | 17324 | 0 | 0 | 0 | `53.16`×2188, `43.00`×1827, `43.01`×1727, `53.22`×984 |
| 19 | `GeoLong` | 17324 | 0 | 0 | 0 | `-`×16696, `166.7E`×4, `3.9W`×4, `112.9E`×4 |
| 20 | `OpOrbit` | 17324 | 0 | 0 | 0 | `LLEO/I`×10898, `LLEO/S`×3260, `LLEO/P`×637, `LEO/I`×606 |

### Colonnes à codes courts

- `ManuState` (#9, 100% de codes courts) : `US`×13873, `CN`×1547, `RU`×368, `F`×180, `UK`×160, `I`×143, `D`×138, `J`×132
- `Class` (#12, 100% de codes courts) : `B`×14683, `D`×1334, `C`×970, `A`×316, `-`×7, `BD`×5, `CD`×5, `CB`×4
- `LState` (#4, 100% de codes courts) : `US`×13945, `CN`×1565, `F`×811, `RU`×571, `IN`×173, `NZ`×124, `J`×65, `KR`×38
- `OwnState` (#6, 99% de codes courts) : `US`×13265, `CN`×1524, `UK`×761, `RU`×388, `J`×144, `F`×102, `I`×91, `D`×82
- `Category` (#13, 92% de codes courts) : `COM`×14144, `IMG`×1020, `TECH`×589, `IMG-R`×267, `NAV`×253, `SIG`×236, `MET`×111, `SCI`×96
- `MVR` (#15, 87% de codes courts) : `M`×14988, `-`×2335, `N`×1
- `UNState` (#7, 59% de codes courts) : `US`×8209, `[US]`×5009, `[CN]`×1076, `UK`×695, `CN`×459, `RU`×305, `[RU]`×83, `J`×79

## `satcat.tsv`

- colonnes : **42**
- lignes de données : **69999**
- largeurs rencontrées : [42]

### Valeurs réelles par colonne

| # | colonne | non vides | OS | OF | commence par O | valeurs les plus fréquentes |
|---|---|---|---|---|---|---|
| 0 | `JCAT` | 69999 | 0 | 0 | 0 | `S00001`×1, `S00002`×1, `S00003`×1, `S00004`×1 |
| 1 | `Satcat` | 69999 | 0 | 0 | 0 | `NNA`×562, `00001`×1, `00002`×1, `00003`×1 |
| 2 | `Launch_Tag` | 69999 | 0 | 0 | 0 | `1999-025`×3537, `1982-092`×1808, `1993-036`×1718, `2022-151`×802 |
| 3 | `Piece` | 69999 | 0 | 0 | 0 | `1957 ALP 1`×1, `1957 ALP 2`×1, `1957 BET 1`×1, `1958 ALP`×1 |
| 4 | `Type` | 69999 | 0 | 0 | 0 | `D  P`×12361, `P      O  M`×10068, `P`×8091, `D  W`×6728 |
| 5 | `Name` | 69999 | 19 | 3 | 1331 | `deb FY-1C`×3494, `deb Kosmos-1408`×1806, `deb Kosmos-2251`×1716, `deb CZ-6A Y2`×800 |
| 6 | `PLName` | 69999 | 19 | 0 | 1495 | `-`×30344, `11S510`×1208, `KDU part`×733, `ESO`×569 |
| 7 | `LDate` | 69999 | 0 | 0 | 0 | `1999 May 10`×3537, `1982 Sep 16`×1814, `1993 Jun 16`×1718, `2022 Nov 11`×802 |
| 8 | `Parent` | 69999 | 0 | 0 | 0 | `S25730`×3533, `S13552`×1806, `S22675`×1716, `S54236`×801 |
| 9 | `SDate` | 69999 | 0 | 0 | 0 | `2007 Jan 11 2228`×3533, `2009 Feb 10 1656`×2370, `2021 Nov 15 0250?`×1805, `2022 Nov 12 0525?`×800 |
| 10 | `Primary` | 69999 | 0 | 0 | 0 | `Earth`×69999 |
| 11 | `DDate` | 69999 | 0 | 0 | 0 | `-`×33309, `1976 Aug  2`×150, `1973 May  7`×92, `1975 Sep  9`×74 |
| 12 | `Status` | 69999 | 0 | 0 | 33261 | `R`×33477, `O`×32085, `OX`×1176, `L`×1074 |
| 13 | `Dest` | 69999 | 0 | 0 | 4 | `-`×66150, `LEO`×130, `A06581`×70, `S26400`×63 |
| 14 | `Owner` | 69999 | 840 | 0 | 2283 | `SPXS`×12805, `CASC`×4384, `RVSN`×4067, `KVR`×3116 |
| 15 | `State` | 69999 | 0 | 0 | 1 | `US`×28857, `SU`×16148, `CN`×9319, `RU`×9183 |
| 16 | `Manufacturer` | 69999 | 191 | 0 | 1999 | `-`×23667, `SPXS`×13047, `TSSKB`×2659, `YUZHUA`×2150 |
| 17 | `Bus` | 69999 | 37 | 2 | 545 | `-`×31660, `Starlink`×4684, `Starlink V2MO`×4341, `Starlink V2M`×2760 |
| 18 | `Motor` | 69999 | 0 | 0 | 28 | `-`×67133, `AOCS`×352, `S400`×105, `11D428A`×92 |
| 19 | `Mass` | 69999 | 0 | 0 | 0 | `0`×32053, `575`×4320, `730`×2764, `260`×1685 |
| 20 | `MassFlag` | 7741 | 0 | 0 | 0 | `?`×7741 |
| 21 | `DryMass` | 69999 | 0 | 0 | 0 | `0`×32054, `530`×4321, `700`×3003, `248`×1679 |
| 22 | `DryFlag` | 22356 | 0 | 0 | 0 | `?`×22356 |
| 23 | `TotMass` | 69999 | 0 | 0 | 0 | `0`×34260, `575`×4324, `730`×2765, `260`×1685 |
| 24 | `TotFlag` | 6128 | 0 | 0 | 0 | `?`×6128 |
| 25 | `Length` | 69999 | 0 | 0 | 0 | `0.0`×32223, `0.3`×10496, `0.2`×5899, `1.0`×1987 |
| 26 | `LFlag` | 18601 | 0 | 0 | 0 | `?`×18601 |
| 27 | `Diameter` | 69999 | 0 | 0 | 0 | `0.0`×32122, `4.1`×8041, `2.8`×4832, `0.1`×2455 |
| 28 | `DFlag` | 5085 | 0 | 0 | 0 | `?`×5085 |
| 29 | `Span` | 69999 | 0 | 0 | 0 | `0.0`×32014, `29.0`×8013, `9.0`×4823, `1.0`×1996 |
| 30 | `SpanFlag` | 19923 | 0 | 0 | 0 | `?`×19923 |
| 31 | `Shape` | 69999 | 0 | 0 | 184 | `-`×32028, `Box + pan`×12825, `Cyl`×7543, `Box`×2803 |
| 32 | `ODate` | 69999 | 0 | 0 | 0 | `2007 Jan 27`×289, `1992 Feb  6`×248, `1976 Jul 31`×200, `1992 Feb  5`×178 |
| 33 | `Perigee` | 69999 | 0 | 0 | 0 | `284`×981, `283`×676, `231`×436, `285`×424 |
| 34 | `PF` | 508 | 0 | 0 | 0 | `?`×508 |
| 35 | `Apogee` | 69999 | 0 | 0 | 0 | `292`×1056, `291`×491, `279`×410, `337`×363 |
| 36 | `AF` | 529 | 0 | 0 | 0 | `?`×529 |
| 37 | `Inc` | 69999 | 0 | 0 | 0 | `53.16`×2092, `43.00`×1929, `43.01`×1885, `53.22`×1213 |
| 38 | `IF` | 251 | 0 | 0 | 0 | `?`×251 |
| 39 | `OpOrbit` | 69999 | 0 | 0 | 0 | `LLEO/I`×29480, `LEO/I`×10756, `LEO/S`×10384, `LLEO/S`×7056 |
| 40 | `OQUAL` | 69999 | 0 | 0 | 22 | `-`×69636, `S`×222, `SSR`×29, `K`×29 |
| 41 | `AltNames` | 69999 | 1 | 1 | 74 | `-`×65498, `Delta 7925`×68, `:U`×36, `Delta 2914`×29 |

### Colonnes à codes courts

- `Status` (#12, 100% de codes courts) : `R`×33477, `O`×32085, `OX`×1176, `L`×1074, `DK`×473, `DSO`×461, `N`×337, `AR`×296
- `State` (#15, 99% de codes courts) : `US`×28857, `SU`×16148, `CN`×9319, `RU`×9183, `F`×1495, `J`×933, `UK`×835, `IN`×775

## Schémas de tous les fichiers

### `active.tsv`

- colonnes (21) : `JCAT`, `Piece`, `Name`, `LaunchDate`, `LState`, `Owner`, `OwnState`, `UNState`, `Manu`, `ManuState`, `LaunchMass`, `DryMass`, `Class`, `Category`, `TF`, `MVR`, `Perigee`, `Apogee`, `Inc`, `GeoLong`, `OpOrbit`
- lignes de données : 17324

- S00965 · 1964-083D · NNS 30020 · 1964 Dec 13 0008:10 · US · BUWEPS · US · US · NAFI · US · 54.000 · 54.000 · D · NAV · Z · - · 1027 · 1084 · 89.98 · - · LEO/P
- S01002 · 1965-008C · LES 1 · 1965 Feb 11 1519:05 · US · AFSSD · US · US · MITLL · US · 158.000 · 31.000 · D · COM · Z · - · 2782 · 2805 · 32.14 · - · MEO
- S01291 · 1965-016D · SR 7B · 1965 Mar  9 1829:47 · US · NRO/NRL · US · US · NRL · US · 47.000 · 47.000 · D · SIG · Z · - · 909 · 938 · 70.09 · - · LEO/I

### `currentcat.tsv`

- colonnes (23) : `JCAT`, `DeepCat`, `Satcat`, `Piece`, `Active`, `Type`, `Name`, `LDate`, `Parent`, `Owner`, `State`, `SDate`, `ExpandedStatus`, `DDate`, `ODate`, `Period`, `Perigee`, `PF`, `Apogee`, `AF`, `Inc`, `IF`, `OpOrbit`
- lignes de données : 83858

- S00001 · - · 00001 · 1957 ALP 1 · R · R2 · 8K71PS No. M1-10 Stage 2 · 1957 Oct  4 · - · RKKE · SU · 1957 Oct  4 1933 · Reentered Earth atmosphere · 1957 Dec  1 1000? · - · - · - · - · - · - · - · - · -
- S00002 · - · 00002 · 1957 ALP 2 · P · P · 1-y ISZ · 1957 Oct  4 · S00001 · RKKE · SU · 1957 Oct  4 1933 · Reentered Earth atmosphere · 1958 Jan  4? · - · - · - · - · - · - · - · - · -
- S00003 · - · 00003 · 1957 BET 1 · P · P A · 2-y ISZ · 1957 Nov  3 · A00002 · RKKE · SU · 1957 Nov  3 0235 · Reentered attached to A00… · 1958 Apr 14 0200? · - · - · - · - · - · - · - · - · -

### `deepcat.tsv`

- colonnes (42) : `JCAT`, `Satcat`, `Launch_Tag`, `Piece`, `Type`, `Name`, `PLName`, `LDate`, `Parent`, `SDate`, `Primary`, `DDate`, `Status`, `Dest`, `Owner`, `State`, `Manufacturer`, `Bus`, `Motor`, `Mass`, `MassFlag`, `DryMass`, `DryFlag`, `TotMass`, `TotFlag`, `Length`, `LFlag`, `Diameter`, `DFlag`, `Span`, `SpanFlag`, `Shape`, `ODate`, `Perigee`, `PF`, `Apogee`, `AF`, `Inc`, `IF`, `OpOrbit`, `OQUAL`, `AltNames`
- lignes de données : 1244

- D00001 · NNA · 1959 MU · 1959 MU · R3  D · 8K72E No. B1-6 · 8K72E · 1959 Jan  2 · - · 1959 Jan  3 0349? · Earth · 1959 Jan  3 1956? · EO · Luna · RVSN · RU · OKB1 · Blok-E · - · 1472 ·  · 1472 ·  · 1472 ·  · 5.0 ·  · 2.7 ·  · 5.0 ·  · Cyl · 1959 Jan  3 · -370 · ? · -242160 · ? · 65.00 ·  · EEO · - · -
- D00002 · 00112 · 1959 MU · 1959 MU 1 · P   D · AMS Luna-1 · E-1 No. 4 · 1959 Jan  2 · - · 1959 Jan  3 0349? · Earth · 1959 Jan  3 1956? · EO · Luna · OKB1 · SU · OKB1 · E-1 · - · 205 ·  · 205 ·  · 205 ·  · 0.8 ·  · 0.8 ·  · 2.0 ·  · Sphere + Ant · 1959 Jan  3 · -370 · ? · -242160 · ? · 65.00 ·  · EEO · - · -
- D00003 · 00113 · 1959 NU · 1959 NU 1 · P   D · Pioneer 4 · Pioneer 4 · 1959 Mar  3 · - · 1959 Mar  3 1654 · Earth · 1959 Mar  4 2000? · EO · Luna · ABMA · US · JPL · Juno II Probe · - · 7 ·  · 7 ·  · 7 ·  · 0.6 ·  · 0.2 ·  · 0.6 ·  · Cone · 1959 Mar  3 · -45 ·  · -393400 ·  · 29.00 ·  · EEO · - · -

### `ftocat.tsv`

- colonnes (42) : `JCAT`, `Satcat`, `Launch_Tag`, `Piece`, `Type`, `Name`, `PLName`, `LDate`, `Parent`, `SDate`, `Primary`, `DDate`, `Status`, `Dest`, `Owner`, `State`, `Manufacturer`, `Bus`, `Motor`, `Mass`, `MassFlag`, `DryMass`, `DryFlag`, `TotMass`, `TotFlag`, `Length`, `LFlag`, `Diameter`, `DFlag`, `Span`, `SpanFlag`, `Shape`, `ODate`, `Perigee`, `PF`, `Apogee`, `AF`, `Inc`, `IF`, `OpOrbit`, `OQUAL`, `AltNames`
- lignes de données : 1845

- F00001 · NSO · 1957-F01 · 1957-F01 · R3  F · Vanguard TV-3 Stage 3 · GRC 33-KS-2800 · 1957 Dec  6 · L04718 · 1957 Dec  6 1645 · Earth · 1957 Dec  6 · S · - · NRL · US · GCR · 33-KS-2800 · - · 198 ·  · 22 ·  · 22 ·  · 1.5 ·  · 0.7 ·  · 1.5 ·  · Cyl · 1957 Dec  6 · -6378 ·  · 0 ·  · 33.00 ·  · ATM · - · -
- F00002 · NSO · 1957-F01 · 1957-F01 · P   F · Vanguard · Vanguard Test Satellite F · 1957 Dec  6 · F00001 · 1957 Dec  6 1645 · Earth · 1957 Dec  6 · S · - · NRL · US · NRL · NRL 6" · - · 2 ·  · 2 ·  · 2 ·  · 0.1 ·  · 0.1 ·  · 0.1 ·  · Sphere · 1957 Dec  6 · -6378 ·  · 0 ·  · 33.00 ·  · ATM · - · -
- F00003 · NSO · 1958-F01 · 1958-F01 · R3  F · Vanguard TV-3BU Stage 3 · GRC 33-KS-2800 · 1958 Feb  5 · L04809 · 1958 Feb  5 0734 · Earth · 1958 Feb  5 · S · - · NRL · US · GCR · 33-KS-2800 · - · 196 ·  · 22 ·  · 22 ·  · 1.5 ·  · 0.7 ·  · 1.5 ·  · Cyl · 1958 Feb  5 · -6378 ·  · 1 ·  · 33.00 ·  · ATM · - · -

### `geotab.tsv`

- colonnes (19) : `JCAT`, `Piece`, `Name`, `LDate`, `GDate`, `ODate`, `Period`, `Perigee`, `PF`, `Apogee`, `AF`, `Inc`, `IF`, `OType`, `Longitude`, `DriftRate`, `TDate`, `TF`, `Flags`
- lignes de données : 1969

- S00553 · 1963-004A · Syncom 1 · 1963 Feb 14 · 1963 Feb 14 · 2026 Nov 20 2021 · 1236.219 · 28691.5 ·  · 34863.2 ·  · 26.38 ·  · MEO · 95.85W · - · 1963 Feb 14 · P · -
- S00634 · 1963-031A · Syncom 2 · 1963 Jul 26 · 1963 Jul 26 · 2026 Nov 16 2025 · 1435.886 · 35756.6 ·  · 35808.3 ·  · 29.66 ·  · GEO/T · 71.04E · +   0.046E · 1969 Apr · P · -
- S00858 · 1964-047A · Syncom 3 · 1964 Aug 19 · 1964 Aug 20 · 2026 Nov 21 1352 · 1435.259 · 35748.6 ·  · 35791.8 ·  · 7.35 ·  · GEO/ID · 135.62E · +   0.203E · 1974 Dec 29 · P · -

### `launchlog.tsv`

- colonnes (20) : `Launch_Tag`, `Launch_Date`, `Piece`, `Type`, `Name`, `PLName`, `JCAT`, `SatOwner`, `SatState`, `LV_Type`, `Flight_ID`, `Platform`, `Launch_Site`, `Launch_Pad`, `Ascent_Site`, `Ascent_Pad`, `Agency`, `LVState`, `Launch_Code`, `LTCite`
- lignes de données : 32258

- 1957 ALP · 1957 Oct  4 1928:34 · 1957 ALP 2 · P · 1-y ISZ · PS-1 · S00002 · OKB1 · SU · Sputnik 8K71PS · M1-PS · - · NIIP-5 · LC1 · - · - · MVS · SU · OS · Energiya
- 1957 BET · 1957 Nov  3 0230:42 · 1957 BET 1 · P A · 2-y ISZ · PS-2 · S00003 · OKB1 · SU · Sputnik 8K71PS · M1-2PS · - · NIIP-5 · LC1 · - · - · MVS · SU · OS · Grahn-WWW
- 1957-F01 · 1957 Dec  6 1644:35 · 1957-F01 · P   F · Vanguard · Vanguard Test Satellite F · F00002 · NRL · US · Vanguard · TV-3 · - · CC · LC18A · - · - · NRL · US · OF · Vang-ER9948

### `lp.tsv`

- colonnes (17) : `Site`, `Code`, `UCode`, `Type`, `StateCode`, `TStart`, `TStop`, `ShortName`, `Name`, `Location`, `Longitude`, `Latitude`, `Error`, `Parent`, `ShortEName`, `EName`, `UName`
- lignes de données : 2807

- A51 · RW14/32 · - · LP · - · 1955 · * · Area 51 RW14/32 · Runway 14/32, Groom Lake … · Groom Lake, Nevada · -115.8020 · 37.2375 · 0.0001 · NRO · - · - · -
- A51 · X1 · - · LP · - · 1967 Sep 28 · 1967 Sep 28 · Drone 501 Drop · Accidental Drop Location,… · Groom Lake, Nevada · -115.8000 · 38.1000 · 0.2000 · NRO · - · - · -
- ABER · A · - · LP · - · - · - · Launch Site A · Skylark Tower, Apron A, R… · Aberporth · -4.5734 · 52.1415 · 0.0001 · RAE · - · - · -

### `orgs.tsv`

- colonnes (17) : `Code`, `UCode`, `StateCode`, `Type`, `Class`, `TStart`, `TStop`, `ShortName`, `Name`, `Location`, `Longitude`, `Latitude`, `Error`, `Parent`, `ShortEName`, `EName`, `UName`
- lignes de données : 4147

- EARTH · EARTH · EARTH · AP · C · - · - · Earth · Earth · Earth · - · - · 0.0200 · - · Earth (Terra) · Earth · Earth
- LUNA · LUNA · LUNA · AP · C · - · - · Luna · Luna · Luna · - · - · 0.0200 · - · Moon · Moon · Luna
- SSYS · SSYS · SSYS · AP · C · - · - · Solar System · Solar System natural cele… · Sol · - · - · 0.0200 · - · Solar System · Solar System natural cele… · Solar System

### `psatcat.tsv`

- colonnes (28) : `JCAT`, `Piece`, `Name`, `LDate`, `TLast`, `TOp`, `TDate`, `TF`, `Program`, `Plane`, `Att`, `Mvr`, `Class`, `Category`, `Result`, `Control`, `Discipline`, `UNState`, `UNReg`, `UNPeriod`, `UNPerigee`, `UNApogee`, `UNInc`, `DispEpoch`, `DispPeri`, `DispApo`, `DispInc`, `Comment`
- lignes de données : 27940

- S00002 · 1957 ALP 2 · First Sputnik · 1957 Oct  4 · 1957 Oct 27 · 1957 Oct 27 · 1957 Oct 27 · - · Sputnik · - · - · - · C · TECH · S · - · ENV* · SU · A/AC.105/INF.002 · - · 227 · 947 · 65.1 · - · 0 · 0 · 0.00 · First Earth satellite
- S00003 · 1957 BET 1 · Second Sputnik · 1957 Nov  3 · 1957 Nov  9 · 1957 Nov  9 · 1957 Nov  9 · - · Sputnik · - · - · - · C · BIO · S · - · BIO · SU · A/AC.105/INF.002 · - · 225 · 1671 · 65.3 · - · 0 · 0 · 0.00 · First animal payload
- S00004 · 1958 ALP · Explorer 1 · 1958 Feb  1 · 1958 Apr  1 · 1958 Apr  1 · 1958 Apr  1 · - · Explorer ABMA · - · - · - · C · SCI · S · JPL · P* · US · A/AC.105/INF.001 · - · - · - · - · - · 0 · 0 · 0.00 · Discovered trapped radiat…

### `satcat.tsv`

- colonnes (42) : `JCAT`, `Satcat`, `Launch_Tag`, `Piece`, `Type`, `Name`, `PLName`, `LDate`, `Parent`, `SDate`, `Primary`, `DDate`, `Status`, `Dest`, `Owner`, `State`, `Manufacturer`, `Bus`, `Motor`, `Mass`, `MassFlag`, `DryMass`, `DryFlag`, `TotMass`, `TotFlag`, `Length`, `LFlag`, `Diameter`, `DFlag`, `Span`, `SpanFlag`, `Shape`, `ODate`, `Perigee`, `PF`, `Apogee`, `AF`, `Inc`, `IF`, `OpOrbit`, `OQUAL`, `AltNames`
- lignes de données : 69999

- S00001 · 00001 · 1957 ALP · 1957 ALP 1 · R2 · 8K71PS No. M1-10 Stage 2 · 8K71A M1-10 (M1-1PS) · 1957 Oct  4 · - · 1957 Oct  4 1933 · Earth · 1957 Dec  1 1000? · R · - · OKB1 · SU · OKB1 · Blok-A · - · 7790 ·  · 7790 ·  · 7800 · ? · 28.0 ·  · 2.6 ·  · 28.0 ·  · Cyl · 1957 Oct  4 · 214 ·  · 938 ·  · 65.10 ·  · LLEO/I · - · -
- S00002 · 00002 · 1957 ALP · 1957 ALP 2 · P · 1-y ISZ · PS-1 · 1957 Oct  4 · S00001 · 1957 Oct  4 1933 · Earth · 1958 Jan  4? · R · - · OKB1 · SU · OKB1 · PS · - · 84 ·  · 84 ·  · 84 ·  · 0.6 ·  · 0.6 ·  · 2.9 ·  · Sphere + Ant · 1957 Oct  4 · 214 ·  · 938 ·  · 65.10 ·  · LLEO/I · - · :RE,:RC
- S00003 · 00003 · 1957 BET · 1957 BET 1 · P A · 2-y ISZ · PS-2 · 1957 Nov  3 · A00002 · 1957 Nov  3 0235 · Earth · 1958 Apr 14 0200? · AR · - · OKB1 · SU · OKB1 · PS · - · 508 ·  · 508 ·  · 8298 · ? · 2.0 ·  · 1.0 ·  · 2.0 ·  · Cone · 1957 Nov  3 · 211 ·  · 1659 ·  · 65.33 ·  · LEO/I · - · :RE,:RC

### `sites.tsv`

- colonnes (18) : `Site`, `Code`, `UCode`, `Type`, `StateCode`, `TStart`, `TStop`, `ShortName`, `Name`, `Location`, `Longitude`, `Latitude`, `Error`, `Parent`, `ShortEName`, `EName`, `Group`, `UName`
- lignes de données : 712

- OCEAN · - · OCEAN · LS · EARTH · - · - · Ocean · Ocean launch sites · - · - · - · 0.0000 · - · Ocean · - · - · Ocean launch sites
- A51 · - · A51 · LS · US · 1968 · 1972 · Area 51 · Groom Lake Air Force Base… · Groom Lake, Nevada · -115.8000 · 37.2300 · 0.1000 · NRO · - · - · - · Groom Lake Air Force Base…
- AAAF · - · HADC · LS · US · 1941 Apr 13 · 1949 Dec  2 · Alamagordo · Alamagordo Army Air Field · - · -106.1030 · 32.8496 · 0.0001 · USAF · - · - · WS · Alamagordo Army Air Field

