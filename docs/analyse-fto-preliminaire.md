# Analyse FTO préliminaire (criblage de brevets publics)

Version 0.1 du 6 novembre 2026. Réalisée par Claude à la demande d'Arnaud (décision 4 de `DECISIONS.md` : FTO lancé, sans cabinet pour le moment).

**Ce document n'est pas un avis juridique et ne conclut à aucune liberté d'exploitation.** Il dresse une première carte des brevets publics à examiner et indique ce qui reste à faire.

## 1. Limites de cette analyse
- Outil : quelques recherches web (moteur limité aux États-Unis) ; **les revendications n'ont pas été lues**, seulement des titres, résumés et indications de statut.
- **Statuts** : ceux de Google Patents (« Expired - Fee Related ») sont une hypothèse automatique, pas une conclusion juridique. Les dates de dépôt, les échéances, les pays validés et les titulaires actuels n'ont pas été vérifiés dans les registres (USPTO Patent Center, Registre européen, CNIPA).
- **Chine** : aucune recherche de brevets chinois n'a pu être faite avec cet outil, alors que le développement se fait en Chine. À confier à un conseil local.
- Une seule passe de recherche : des familles importantes ont pu m'échapper.

## 2. Familles de brevets repérées

| # | Famille | Objet (d'après titres et résumés) | Statut indiqué | Priorité d'examen |
|---|---|---|---|---|
| 1 | **United Sciences / 3DM Systems** : US 8,715,173 (anneau et éventail laser), 8,900,125 (modélisation 3D), 8,900,127, 8,900,128 (caméra unique vidéo + mesure), 8,900,129, 8,900,130 (alerte de sécurité) ; EP 2825087 B1 (« Otoscanner ») ; demandes US 2013/0237754 à 237758 | Otoscope avec laser en anneau ou en éventail, caméra grand angle, suivi de la pose ; famille d'origine de l'Otoscan (lien probable, non confirmé) | « Expired - Fee Related » indiqué par Google pour **US 8,715,173 et US 8,900,128** ; statut non retrouvé pour 8,900,125, 8,900,129 et 8,900,130 ; titulaire actuel indiqué : Ethos United I LLC (titulaire d'origine : United Sciences LLC) ; **statut de EP 2825087 B1 non vérifié** | Haute pour vérifier : si l'expiration est confirmée, le risque sur la tête A (anneau laser) baisse nettement ; un brevet européen peut rester en vigueur |
| 2 | **Famille « Intraoral scanning apparatus »** (titre indiqué ; décrit un scanner pour l'oreille avec une partie extérieure et une sonde amovible, lumière structurée à franges mobiles, caméra et optique de mise au point hors du conduit) : US 11,368,667, 11,539,937, 11,622,102, 11,671,582, 11,831,815, 12,155,812, 12,335,456, 12,355,936, 12,375,638 | Sonde à lumière structurée pour l'oreille, numérisation directe pour coques sur mesure | Délivrés récemment (numéros jusqu'à 12,3xx,xxx) : **vraisemblablement en vigueur**, non vérifié | **Très haute** : proche de notre tête B (lumière structurée) ; revendications à lire |
| 3 | **EP 3403568 B1** (délivré le 1er novembre 2023) | Scanner en forme de sonde avec source de lumière structurée et caméra pour surfaces intérieures ; revendications générales (surfaces intérieures), pas propres à l'oreille | Délivré en 2023 ; demande déposée en 2011 d'après le document ; pays validés et échéance **à vérifier** | **Très haute** : revendications potentiellement larges sur une sonde à lumière structurée |
| 4 | **US 7,625,335** (3Shape AS) | Balayage optique tridimensionnel de surfaces intérieures, y compris l'oreille | Ancien ; statut non vérifié | Moyenne (probablement ancien) |
| 5 | US 8,135,453 ; US 7,961,981 ; US 8,437,009 ; US 7,961,300 | Modélisation du conduit par tomographie par cohérence optique ; image 3D du conduit externe ; reconstruction 3D d'une empreinte ; scanner à point unique | Non vérifiés | Basse à moyenne |
| 6 | **US 12,678,069** (« mesures tridimensionnelles de la forme de l'oreille externe ») | Mesure 3D du pavillon | Très récent, non vérifié | Moyenne : concerne le scan externe de l'oreille (suivi de l'oreille sans clip, contrôle d'échelle) |
| 7 | **US 11,451,912** (« fabrication assistée par ordinateur 3D d'une protection auditive ou d'un appareil de réduction de bruit ») | Chaîne CAO/FAO pour protections auditives | Non vérifié | **Haute** : concerne notre chaîne scan → CAO → impression |

## 3. Lecture par bloc technique (hypothèses de travail)

| Bloc | Observations | Niveau d'attention |
|---|---|---|
| Tête A (anneau laser) | Brevets les plus proches (famille 1) apparemment expirés aux États-Unis d'après Google, à confirmer ; état en Europe et en Chine à vérifier | Moyen, en baisse si l'expiration est confirmée |
| Tête B (motif codé, lumière structurée) | Familles 2 et 3 à lire en priorité | **Élevé** |
| Suivi de pose, clip, fusion, gyroscopes | **Aucun brevet repéré** dans cette passe sur le suivi de la sonde par rapport à la tête ou sur un clip ; la recherche ciblée reste à faire | Inconnu |
| CAO automatique et chaîne de bout en bout | Famille 7 à lire ; autres familles probables chez les fabricants d'aides auditives (non cherchées) | **Élevé** |
| Impression | Machines à capsules SprintRay : droits liés à l'équipement et à la résine, à clarifier avec le fournisseur | À cadrer |
| Scanners intra-oraux dentaires | Non étudiés (piste abandonnée) | Hors périmètre |

## 4. Ce qu'il reste à faire (par ordre de priorité)
1. **Lire les revendications indépendantes** des familles 2, 3 et 7 (Google Patents, Registre européen) et vérifier leur statut, leur titulaire et les pays couverts. C'est le point qui peut changer le choix entre tête A et tête B.
2. **Confirmer l'expiration** de la famille 1 dans les registres (États-Unis, EP 2825087 B1 et ses validations, équivalents chinois éventuels).
3. **Recherches ciblées** (classes CPC de `docs/cahier-des-charges-FTO.md`) sur : suivi de la pose d'une sonde auriculaire par rapport à la tête, clip ou support sur l'oreille, fusion de gyroscopes et de suivi externe, retrait motorisé et centrage d'une sonde auriculaire, CAO automatique de coques.
4. **Recherche de brevets chinois** par un conseil local (CNIPA), puis européens et américains.
5. **Brevets propres** à déposer avant toute divulgation détaillée (suivi de la pose avec clip et fusion, CAO automatique, chaîne complète) : à confirmer par un conseil.
6. Décider, après lecture des revendications, de la suite : contournement de conception, licence, ou changement d'architecture. Revue obligatoire à la gate M5.

## 5. Sources consultées (recherche web, pas de lecture des revendications)
- Google Patents : [US 8,900,128 B2](https://patents.google.com/patent/US8900128), [US 8,715,173 B2](https://www.google.com.au/patents/US8715173), [EP 2825087 B1](https://patents.google.com/patent/EP2825087B1/da), [US 7,625,335](https://patents.google.com/patent/US7625335)
- USPTO (documents) : [US 8,900,125](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8900125), [US 8,900,130](https://insight.rpxcorp.com/pat/US8900130B2), [US 12,678,069](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12678069), [US 11,451,912](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11451912), [US 11,368,667](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11368667), [US 12,375,638](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12375638)
- Registre européen : [EP 3403568 B1](https://data.epo.org/publication-server/rest/v1.2/patents/EP3403568NWB1/document.html)
