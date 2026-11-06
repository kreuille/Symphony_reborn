# Spécification technique : prototype de scanner 3D du conduit auditif (Phase 1)

Version 0.4 (brouillon). Les valeurs chiffrées sont des cibles de départ à valider par les premiers essais.

**Mise à jour v0.4 (6 novembre 2026) :** le **retrait motorisé** devient l'option produit prioritaire (décision 12 de `DECISIONS.md`) pour réduire l'erreur de manipulation et automatiser le scan ; ajout de l'exigence P9, de l'essai T13 et d'un critère Go (indépendance de l'opérateur), et révision de 4.2 et 3.

**Mise à jour v0.3 (6 novembre 2026) :** intègre les calculs et simulations de `docs/conception-scanner.md` (géométrie de la tête A, architecture de pose, suivi de la tête, latence, retrait motorisé) et les décisions du 5 novembre. Les modifications portent sur §2 (note), §4.1, §4.2, §4.3, §4.4, §5, §6, §10 et §11. Les résultats de simulation sont des ordres de grandeur sur un conduit synthétique : ils orientent la conception, ils ne valident rien.

**Décisions intégrées en v0.2 :** (1) l'impression se fait sur les machines à capsules SprintRay (route G1), pas en impression continue ; (2) le scanner contribue au budget d'erreur total de la chaîne de 0,2 mm avec 0,10 mm RMS (voir README) ; (3) étude FTO lancée le 5 novembre 2026 (décision 4 de `DECISIONS.md` mise à jour) : le choix des têtes A et B tient compte de ses résultats, avec revue à la gate M5 du calendrier maître.

## 1. Objectif et périmètre

**Objectif de la phase 1 (environ 12 semaines) :** démontrer qu'une sonde optique miniature à lumière structurée mesure la forme du conduit auditif avec une erreur inférieure à 0,1 mm, sur fantômes, et produit un maillage STL directement imprimable.

**Inclus :** sonde, électronique, logiciel d'acquisition et de reconstruction, banc de validation, fantômes.
**Exclus (phases suivantes) :** essais sur sujets humains, CAO automatique, réglementation, industrialisation.

## 2. Exigences de performance

| Réf. | Exigence | Cible phase 1 |
|---|---|---|
| P1 | Zone mesurée | Du méat jusqu'à 3–5 mm du tympan (profondeur 25–30 mm), diamètres 5–12 mm |
| P2 | Justesse (écart maillage / référence, après alignement) | RMS ≤ 0,10 mm ; maximum ≤ 0,25 mm |
| P3 | Répétabilité (10 scans du même fantôme) | Écart type ≤ 0,05 mm |
| P4 | Erreur de diamètre sur calibres étalons (6, 8, 10 mm) | ≤ 0,05 mm |
| P5 | Durée de scan par oreille | ≤ 60 s (objectif 30 s) |
| P6 | Vitesse de retrait manuelle tolérée | jusqu'à 10 mm/s |
| P7 | Résolution du maillage final | pas de 0,1 mm |
| P8 | Sortie | STL étanche (watertight), unités mm, repère standardisé |
| P9 | Indépendance de l'opérateur (v0.4) | taux de scans complets du premier coup ≥ 90 % ; écart du RMS entre opérateurs ≤ 0,03 mm (hypothèse) ; écart de durée entre opérateurs à relever |

*Note v0.3 sur P6 et P7 :* avec 30 mesures par seconde et un retrait à 10 mm/s, le pas axial entre anneaux est de 0,33 mm ; l'erreur d'interpolation sur un conduit lisse est négligeable (de l'ordre de 0,003 mm), donc **le pas de maillage de 0,1 mm (P7) n'impose pas une cadence de 100 mesures/s**. Le flou de bouger est de 10 µm pour 10 mm/s et 1 ms d'exposition.

## 3. Sécurité du prototype

- Source laser de **classe 1** (IEC 60825-1), à vérifier avec la fiche technique du composant.
- Pointe de sonde **atraumatique**, diamètre ≤ 4,5 mm, avec **butée mécanique** empêchant tout contact avec le tympan, y compris sur fantôme.
- Température de la pointe ≤ 41 °C (mesure par capteur, coupure automatique).
- **Retrait motorisé (v0.4)** : insertion toujours manuelle ; le moteur ne fait que retirer la sonde, avec arrêt automatique, limite de force, butée de profondeur et arrêt à la moindre alarme ; dossier de sécurité d'un dispositif actif à constituer dès la phase 1.
- Usage limité aux fantômes en phase 1 ; aucun essai sur personne avant évaluation réglementaire et éthique.

## 4. Architecture

**Poignée commune + deux têtes interchangeables**, pour comparer les approches sur le même banc.

- **Tête A : anneau laser panoramique** (miroir conique ou DOE annulaire). Référence métrologique : simple et précise.
- **Tête B : motif codé monocoup** (VCSEL + DOE, lignes ou points codés). Candidate pour le produit : tolérante au mouvement.

### 4.1 Optique (valeurs de départ)

| Paramètre | Valeur de départ |
|---|---|
| Caméra | puce-au-bout, ≤ 1 mm, 400×400 px minimum (module à sélectionner) |
| Champ de vision | 115–130° (selon la base B ; 145–150° si B = 2 mm, objectif difficile) |
| Longueur d'onde laser | vert 520 nm (essai bleu 450 nm), réduit la diffusion sous la peau |
| Base de triangulation B (caméra – plan de l'anneau) | **3–4 mm** (v0.2 : 1,5–2 mm, incompatible avec un champ de 120° pour des diamètres jusqu'à 12 mm) |
| Distance de travail | 2–10 mm |
| Filtre | passe-bande étroit sur la longueur d'onde du laser ; polarisation croisée en option |
| Cadence | caméra ≥ 60 images/s : 30 mesures (laser pulsé, impulsion ≤ 1 ms) + 30 images vidéo (LED blanche) par seconde, entrelacées |

Estimation de précision (théorique, avant étalonnage), capteur de 400 px, objectif équidistant, rayon de paroi jusqu'à 6 mm : résolution de profondeur de 0,046 mm/px à r = 4 mm et 0,083 mm/px à r = 6 mm pour B = 3 mm (0,039 et 0,064 pour B = 4 mm). Avec une détection sous-pixel de 0,1 à 0,3 px, l'erreur de profondeur est de l'ordre de 5 à 25 µm ; en pratique prévoir 3 à 5 fois plus, d'où la cible de 0,1 mm. Détail et tableau complet : `docs/conception-scanner.md`, section 1 (R3). La pointe comporte une **fenêtre cylindrique transparente** de longueur B entre la caméra et le plan de l'anneau ; à vérifier : passage du deuxième coude avec une pointe plus longue.

### 4.2 Pose de la sonde (v0.3)

**Constat des calculs et simulations** (`docs/conception-scanner.md`, sections 1 et 6 à 8) : l'anneau laser ne contraint pas la pose ; le recalage de surface (ICP) ne donne ni l'axe, ni l'inclinaison, ni le roulis ; l'accéléromètre ne peut pas fournir l'axe (1 mg de biais = 4,9 mm en 1 s). La formule « IMU + ICP » de la v0.2 est abandonnée.

**Capteurs de pose :**
- **Gyroscope 6 axes** sur la sonde, fréquence ≥ 200 Hz, horodaté ; **second gyroscope sur la tête** (ou la base) pour retirer la rotation de la tête.
- **Suivi du centre de la lumière** : le centre de l'anneau mesuré fait avancer la pose le long de la tangente du conduit (courbure estimée par le gyroscope). Simulé à 0,25 mm RMS avec coudes en main libre (insuffisant seul).
- **Suivi externe de la poignée** (caméra fixe, repères sur la poignée, sonde rigide) **avec suivi d'un clip rigide sur l'oreille** (glissement visé ≤ 0,1 mm), ou suivi de l'oreille sans clip (à étudier). Simulé à 0,075 mm RMS tête immobile, 0,15 mm tête mobile.
- **Fusion** du suivi du centre, du gyroscope et du suivi externe (correction en douceur, rejet des mesures aberrantes par porte à 0,5 mm / 1,5° ou filtre médian) : simulée à 0,06 à 0,13 mm selon les perturbations (occultation, latence, tête mobile, aberrants).
- **Axe** : codeur sur le banc ; en manuel, source à trancher par essais (odométrie visuelle des images vidéo, protocole `docs/protocole-experience-otoscope-colmap.md`, ou suivi externe).

**Options à comparer en phase 1 sur le même banc :** (a) suivi externe + gyroscopes + fusion en main libre (référence et repli, voie la moins risquée) ; (b) **retrait motorisé avec centrage de la sonde, option produit prioritaire (v0.4)** : sans suivi externe, simulé à 0,106 mm au mieux avec centrage actif sans contact et à 0,14 mm au mieux avec un centrage au contact, **sous des hypothèses de centrage et d'alignement non démontrées** (sections 8.2, 8.5, 8.6) ; (c) **retrait motorisé combiné au suivi externe** (hybride) : sonde centrée et alignée par la mécanique, pose absolue fournie par le suivi, avec fusion adaptative (filtre de Kalman à deux états par axe) ; simulé à 0,06 à 0,10 mm selon les perturbations (tête mobile, clip glissant de 0,1 à 0,3 mm, occultations, aberrants), sous l'hypothèse de centrage non démontrée (sections 8.8 et 8.9 de `docs/conception-scanner.md`). La dérive supposée de l'estime est un paramètre à mesurer sur banc. Le moteur apporte surtout la reproductibilité du geste, pas un gain de précision à lui seul (vitesse constante seule : aucun gain en simulation).

### 4.3 Électronique

- Microcontrôleur ou FPGA pour la synchronisation caméra / laser / IMU.
- **Datation (v0.3)** : horodatage commun des images, du laser, des gyroscopes et du suivi externe. La **latence du suivi externe doit être mesurée** (à ±5 ms près) et compensée ; pour des vitesses de main de 5 à 10 mm/s, plusieurs millisecondes de désynchronisation résiduelle sont tolérées pour la forme (écart < 0,003 mm jusqu'à 10 ms, simulation), mais l'erreur de position axiale vaut environ la vitesse × la désynchronisation. L'exigence de 0,5 ms de la v0.2 n'est plus retenue comme critère de forme ; elle reste utile si l'on exploite la position axiale.
- Liaison USB 3 vers le PC (flux vidéo type UVC + canal de données IMU).
- Pilote laser avec modulation synchronisée à l'exposition, protection contre la surintensité.

### 4.4 Logiciel

1. Acquisition synchronisée (images, IMU, codeur).
2. Étalonnage caméra, puis caméra-projecteur, sur cible de géométrie connue.
3. Détection de la raie ou du motif (sous-pixel), triangulation.
4. Filtrage des points aberrants (reflets, cérumen simulé).
5. Estimation de pose (gyroscopes, suivi du centre de la lumière, recalage sur le suivi externe, rejet des aberrants, voir 4.2), puis fusion TSDF (voxel 0,1 mm).
6. Extraction du maillage (marching cubes), fermeture et export STL/PLY.
7. Script de mesure d'erreur par rapport à la référence.

## 5. Validation

### 5.1 Fantômes et références

- 3 à 5 **fantômes d'oreille** (silicone ou résine imprimée) de formes et diamètres variés, avec courbure en S (générables avec `tools/photogrammetrie/exporter_fantome.py`). Pour les fantômes à coudes, une **référence de pose en 6 degrés de liberté** est nécessaire (bras robotisé, table multi-axes ou suivi de référence) : un codeur linéaire ne suffit pas (v0.3). Prévoir aussi des fantômes **souples** pour les essais de centrage.
- **Calibres étalons** (cylindres de 6, 8, 10 mm) et un tube coudé de géométrie connue.
- **Référence de mesure :** scan micro-CT ou scanner industriel de haute précision (incertitude ≤ 0,02 mm), ou à défaut MMT sur gabarits.

### 5.2 Essais

| Essai | Description | Critère |
|---|---|---|
| T1 | Étalonnage et erreur de reprojection | < 0,3 px |
| T2 | Justesse statique sur calibres | P4 |
| T3 | Justesse sur fantômes d'oreille (sonde sur banc motorisé) | P2 |
| T4 | Scan manuel, vitesse de retrait variable | P2 et P6 |
| T5 | Répétabilité (10 scans) | P3 |
| T6 | Conditions difficiles : surface humide, cérumen simulé, poils | perte de données < 10 % de la surface |
| T7 | Comparaison tête A / tête B | rapport de synthèse |
| T8 | Impression du maillage sur une machine à capsules SprintRay avec la recette rigide de G1, mesure de la pièce | écart pièce / maillage ≤ 0,10 mm RMS (part « impression » du budget d'erreur) |
| T9 | Qualité du suivi externe : erreur main-pointe, bruit, dérive, **latence**, occultations | erreur main-pointe ≤ 0,05 mm, bruit ≤ 0,04 mm par image, latence mesurée à ±5 ms (valeurs supposées par les simulations) |
| T10 | Mouvement de la tête sur fantôme monté sur un support mobile : compensation par clip et gyroscope de tête, glissement du clip | glissement ≤ 0,1 mm ; erreur de pose avec tête mobile ≤ 0,15 mm RMS |
| T11 | Si l'option sans suivi externe est étudiée : décentrage et inclinaison obtenus par le retrait motorisé et le centrage, déformation de la paroi (fantôme souple) | décentrage ≤ 0,05 mm, inclinaison ≤ 0,5°, déformation ≤ 0,05 mm (valeurs supposées par les simulations) |
| T12 | Odométrie visuelle (protocole `docs/protocole-experience-otoscope-colmap.md`) | critères du protocole |
| T13 | **Indépendance de l'opérateur (v0.4)** : au moins 3 opérateurs de niveaux différents (dont un novice), plusieurs fantômes, 5 scans chacun, en retrait manuel puis en retrait motorisé | P9 : taux de scans complets du premier coup ≥ 90 % ; écart du RMS entre opérateurs ≤ 0,03 mm ; gain du retrait motorisé sur l'écart entre opérateurs mesuré |

**Mesure de l'erreur :** distance point-surface entre le maillage et la référence après alignement optimal (RMS, 95e centile, maximum), avec cartographie des écarts.

## 6. Critères Go / No-Go de la phase 1

- **Go :** P2, P3, P4 et P5 atteints sur au moins 3 fantômes, avec au moins une des deux têtes ; T8 validé.
- **Indépendance de l'opérateur (v0.4)** : P9 atteint avec le retrait motorisé (T13), le retrait manuel servant de comparaison.
- **Précision de pose (v0.3)** : le critère P2 est évalué aussi en **scan manuel sur un fantôme à coudes**, avec l'architecture de pose retenue en 4.2. Les simulations donnent 0,06 à 0,13 mm avec suivi externe et fusion (selon les perturbations) et 0,25 mm sans suivi externe en main libre : la tenue du seuil de 0,15 mm sans suivi externe n'est pas acquise.
- **Go conditionnel :** précision comprise entre 0,1 et 0,15 mm avec une cause identifiée et corrigeable.
- **No-Go :** précision > 0,15 mm sans amélioration plausible ; ou impossibilité de tenir le diamètre de pointe ≤ 4,5 mm.

## 7. Livrables

1. Prototype fonctionnel (poignée et deux têtes) et plans.
2. Logiciel d'acquisition et de reconstruction (code source).
3. Données brutes et rapport de validation (T1–T8).
4. Nomenclature (BOM) et fournisseurs.
5. Note de conception pour la phase 2.

## 8. Planning indicatif (12 semaines)

Ordre détaillé des essais, matériel du banc et seuils de décision : `docs/plan-banc-phase1.md`.

| Semaines | Contenu |
|---|---|
| 1–2 | Choix des composants, commande des fantômes et des calibres, mise en place de la référence |
| 3–5 | Tête A : montage, étalonnage, premiers scans |
| 4–7 | Tête B : montage, motif et décodage |
| 6–9 | Logiciel : pose, TSDF, export, scripts de mesure |
| 9–11 | Campagne d'essais T1–T8 |
| 12 | Rapport et décision Go / No-Go |

**Budget :** non chiffré à ce stade.

## 9. Interface avec l'imprimante

- Fichier STL étanche, unités en mm, orientation et origine définies par le repère du conduit (axe du conduit, point du méat).
- Métadonnées : identifiant, côté (gauche/droit), date, version de l'étalonnage, indicateurs de qualité.

## 10. Risques et parades

| Risque | Parade |
|---|---|
| Caméra miniature de résolution insuffisante | Tester deux modules ; sinon, caméra plus grande dans la poignée avec relais optique |
| Diffusion du laser sous la peau | Longueur d'onde verte ou bleue, polarisation, calibrage sur matériaux réalistes |
| Dérive de pose (axe, inclinaison, roulis, coudes) | Suivi externe + gyroscopes + suivi du centre + fusion (4.2) ; l'accéléromètre n'est pas utilisable pour l'axe |
| Mouvement de la tête, glissement du clip sur l'oreille (0,3 mm de glissement donne 0,3 mm d'erreur) | Clip rigide ≤ 0,1 mm ou suivi de l'oreille sans clip ; gyroscope sur la tête |
| Latence et désynchronisation du suivi externe | Mesure de la latence, horodatage commun, compensation |
| Valeurs aberrantes du suivi | Rejet par porte ou filtre médian |
| Centrage au contact qui déforme le conduit (meilleur cas simulé 0,14 mm, 0,23 mm si tissu mou) | Centrage actif sans contact ou suivi externe ; mesurer la raideur du conduit |
| Reflets sur surface humide | Filtrage, polarisation, seuils adaptatifs |
| Dérive de l'étalonnage | Étalonnage de contrôle avant chaque session |

## 11. Points ouverts à décider

1. Capteur de référence disponible en interne ou en sous-traitance (micro-CT, scanner industriel) ?
2. Résine pour l'essai T8 : à choisir avec le projet G1 (imprimante : machine à capsules SprintRay, décidé).
3. Fournisseurs pour la micro-caméra, le VCSEL et le DOE.
4. FTO lancé (5 novembre 2026). Le choix de la tête A ou B repose sur les résultats de phase 1 et sur ceux de l'étude FTO. Revue obligatoire au plus tard à la gate M5, avant la fabrication des prototypes destinés à des sites tiers et avant toute divulgation détaillée.
5. Banc de référence de pose en 6 degrés de liberté (bras robotisé, table multi-axes) disponible en interne ou en sous-traitance ?
6. Choix du suivi externe (capteur 3D, caméras à repères) et du clip, ou suivi de l'oreille sans clip ; précision mesurée en T9 et T10.
7. Odométrie visuelle : faisable ou non avec une caméra miniature (expérience T12).
8. Retrait motorisé (option produit prioritaire, décision 12) : centrage passif, actif, ou hybride avec suivi externe (T11, T13) ; raideur du conduit à mesurer ; dossier de sécurité d'un dispositif actif.
