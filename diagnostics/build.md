# Journal du build

Exécution de `scripts/build_site.py` sur les données du dépôt.

```
statuts : succès 6927, échec 508, inconnu 26
codes Launch_Code : 25 valeurs distinctes — OS=30505, OF=937, DS=446, OF40=117, OS89=73, OS95=52, OS75=46, OS85=19, NS=13, XS=11, OF50=6, OF25=6, OS80=6, OS66=3, OF45=3, OF44=2, OF20=2, OS65=2, NF=2, DS75=2, OF70=1, OS60=1, OS90=1, OF60=1, OF30=1
codes LVState : 20 valeurs distinctes — US=21037, SU=4029, CN=2417, RU=2093, F=1260, IN=593, J=336, NZ=291, I-ESA=68, KR=54, IR=24, IL=13, I=12, KP=9, D=7, I-ELDO=5, CYM=4, UK=3, BR=2, AU=1
destinations (28787 charges utiles) : LEO=25220, GEO=1356, SO=529, MEO=482, ATM=399, HEO=334, Interplanétaire=136, CLO=127, GTO=88, VHEO=67, DSO=37, TA=7
orbites hors familles connues (8) : SO=529, ATM=399, CLO=127, GTO=88, VHEO=67, DSO=37, TA=7, -=5
vols habités : 364 — 1960s=35, 1970s=34, 1980s=60, 1990s=85, 2000s=58, 2010s=48, 2020s=44
vols habités en échec : 4 — 1975-F02, 1983-F02, 1986-F01, 2018-F01
libellés sites : 712 entrées ; non résolus : aucun
libellés organisations : 4088 entrées ; non résolus : 6 code(s) — 10ADS=22, 3SLS=16, 2SLS=10, 4SLS=6, 21AT=6, 19SOG=1
libellés sites (10 premiers) :
  Plesetsk — 53-y Nauchno-Issledovatelskiy Ispitatelniy Poligon, · GNIIP, VKS section, Plesetsk, Rossiya · GNIIP, Plesetsk, Rossiya [GIK-1, GNIIP, GNIIPV, NIIP-53]
  Baykonur — NIIP-5, Baykonur, Kazakstan · GIK-5, Baykonur, Kazakstan [GIK-5, NIIP-5]
  Canaveral — Cape Canaveral Air Station, Florida · Space Florida, Cape Canaveral [CC, SPFLA]
  Vandenberg — Vandenberg AFB, California · South Vandenberg AFB, California · Vandenberg Space Force Base, California [V, VS, VSFB, VSFBS]
  Kourou — Centre Spatial Guyanais, Kourou, Guyane Francaise [CSG]
  Jiuquan — Jiuquan Space Center, Nei Monggol Zizhiqu, China [JQ]
  Kennedy — NASA John F. Kennedy Space Center, Florida [KSC]
  Xichang — Xichang Space Center (Songlin), Sichuan, China [XSC]
  Taiyuan — Taiyuan weixing fashe zhongxin [TYSC, TYSC?]
  Sriharikota — Satish Dhawan Space Ctr, Sriharikota, Andhra Pradesh, India [SDSC, SHAR]
libellés agences (10 premiers) :
  RVSN — Rakentiye Voiska Strategicheskogo Naznacheniye [RVSN]
  UNKS — Upravleniye Nachalnika Kosmicheskikh Sredstv [UNKS]
  SpaceX — SpaceX [SPX]
  CALT — Zhongguo yunzaihuojian jishu yanjiu yuan [CALT]
  Arianespace — Arianespace, Inc. [AE]
  SAST — Shanghai hangtian jishu yanjiuyuan [SAST]
  USAF SSD — US Air Force Space Systems Division [AFSSD, AFSSD2]
  VKS RVSN — Voenno-Kosmicheskiye Sili (Military Space Forces), RVSN [VKSR]
  Roskosmos — Federal'noe kosmicheskoe agentstvo Rossii (Roskosmos) [FKA]
  GSFC — NASA Goddard Space Flight Center [GSFC]
libellés pays (10 premiers) :
  USA — United States of America [US]
  SSSR — Soyuz Sovetskikh Sotsialisticheskikh Respublik [SU]
  Rossiya — Rossiyskaya Federatsiya [RU]
  Zhongguo — Zhonghua Renmin Gongheguo [CN]
  France — Republique Francaise [F]
  Nippon — Nippon-koku [J]
  India — Republic of India [IN]
  New Zealand — New Zealand [NZ]
  Iran — Jomhuri-ye Eslami-ye Iran [IR]
  ESA — European Space Agency [I-ESA]
7461 lancements, 32258 objets, 11 page(s)
_site/ : 5738 Ko ; explorateur : 1977 Ko ; charges utiles : 3453 Ko
```

## Poids des sorties

```
5.7M	_site
2.0M	_site/data/launches.json
80K	_site/classements/agences.html
28K	_site/classements/annees.html
8.0K	_site/classements/decennies.html
8.0K	_site/classements/index.html
76K	_site/classements/lanceurs.html
12K	_site/classements/pays.html
32K	_site/classements/sites.html
20K	_site/assets/css
8.0K	_site/assets/img
28K	_site/assets/js
```

## Quelques lignes des classements

### `classements/sites.html`

```
 
 
 
 Plesetsk
 
 1 688 
 22,6 % 
 1 619 
 68 
 96,0 % 
 3 102 
 1966–2026 
 
 
 
 Baykonur
 
 1 564 
 21,0 % 
 1 435 
 123 
 92,1 % 
 2 495 
 1957–2026 
 
 
 
 Canaveral
 
 1 112 
 14,9 % 
 1 032 
 78 
 93,0 % 
 9 249 
 1957–2026 
 
 
 
 Vandenberg
```

### `classements/agences.html`

```
 
 
 
 RVSN
 Rakentiye Voiska Strategicheskogo Naznacheniye 
 
 1 538 
 20,6 % 
 1 406 
 127 
 91,7 % 
 2 162 
 1960–1981 
 
 
 
 UNKS
 Upravleniye Nachalnika Kosmicheskikh Sredstv 
 
 906 
 12,1 % 
 869 
 36 
 96,0 % 
 1 854 
 1982–2026 
 
 
 
 SpaceX
 
 737 
 9,9 % 
 727 
 7 
 99,0 % 
 16 658 
 2006–2026 
 
 
```

### `classements/pays.html`

```
 
 
 
 USA
 
 2 493 
 33,4 % 
 2 304 
 175 
 92,9 % 
 21 037 
 1957–2026 
 
 
 
 SSSR
 
 2 457 
 32,9 % 
 2 281 
 168 
 93,1 % 
 4 029 
 1957–1991 
 
 
 
 Rossiya
 
 902 
 12,1 % 
 859 
 41 
 95,4 % 
 2 093 
 1992–2026 
 
 
 
 Zhongguo
```

