# Spécification technique : prototype de scanner 3D du conduit auditif (Phase 1)

Version 0.2 (brouillon). Les valeurs chiffrées sont des cibles de départ à valider par les premiers essais.

**Décisions intégrées en v0.2 :** (1) l'impression se fait sur les machines à capsules SprintRay (route G1), pas en impression continue ; (2) le scanner contribue au budget d'erreur total de la chaîne de 0,2 mm avec 0,10 mm RMS (voir README) ; (3) pas d'étude FTO pour le moment : le choix des têtes A et B se fait sur des critères techniques, le risque est accepté et à revoir à la gate M5 du calendrier maître.

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

## 3. Sécurité du prototype

- Source laser de **classe 1** (IEC 60825-1), à vérifier avec la fiche technique du composant.
- Pointe de sonde **atraumatique**, diamètre ≤ 4,5 mm, avec **butée mécanique** empêchant tout contact avec le tympan, y compris sur fantôme.
- Température de la pointe ≤ 41 °C (mesure par capteur, coupure automatique).
- Usage limité aux fantômes en phase 1 ; aucun essai sur personne avant évaluation réglementaire et éthique.

## 4. Architecture

**Poignée commune + deux têtes interchangeables**, pour comparer les approches sur le même banc.

- **Tête A : anneau laser panoramique** (miroir conique ou DOE annulaire). Référence métrologique : simple et précise.
- **Tête B : motif codé monocoup** (VCSEL + DOE, lignes ou points codés). Candidate pour le produit : tolérante au mouvement.

### 4.1 Optique (valeurs de départ)

| Paramètre | Valeur de départ |
|---|---|
| Caméra | puce-au-bout, ≤ 1 mm, 400×400 px minimum (module à sélectionner) |
| Champ de vision | 100–120° |
| Longueur d'onde laser | vert 520 nm (essai bleu 450 nm), réduit la diffusion sous la peau |
| Base de triangulation | 1,5–2 mm |
| Distance de travail | 2–10 mm |
| Filtre | passe-bande étroit sur la longueur d'onde du laser ; polarisation croisée en option |

Estimation de précision (théorique, avant étalonnage) : avec z = 5 mm, base 1,5 mm, focale ≈ 170 px, l'erreur de profondeur est d'environ 0,1 mm par pixel d'erreur de détection, soit **environ 10 µm avec une détection sous-pixel à 0,1 px**. À z = 8 mm, environ 25 µm. En pratique, prévoir 3 à 5 fois plus, d'où la cible de 0,1 mm.

### 4.2 Pose de la sonde

- IMU 6 axes (accéléromètre + gyroscope), fréquence ≥ 200 Hz, synchronisée avec l'exposition de la caméra.
- Fusion IMU + ICP entre relevés successifs ; avec la tête A, un codeur linéaire sur le banc pour fixer le décalage axial.

### 4.3 Électronique

- Microcontrôleur ou FPGA pour la synchronisation caméra / laser / IMU.
- Liaison USB 3 vers le PC (flux vidéo type UVC + canal de données IMU).
- Pilote laser avec modulation synchronisée à l'exposition, protection contre la surintensité.

### 4.4 Logiciel

1. Acquisition synchronisée (images, IMU, codeur).
2. Étalonnage caméra, puis caméra-projecteur, sur cible de géométrie connue.
3. Détection de la raie ou du motif (sous-pixel), triangulation.
4. Filtrage des points aberrants (reflets, cérumen simulé).
5. Estimation de pose (IMU + ICP), fusion TSDF (voxel 0,1 mm).
6. Extraction du maillage (marching cubes), fermeture et export STL/PLY.
7. Script de mesure d'erreur par rapport à la référence.

## 5. Validation

### 5.1 Fantômes et références

- 3 à 5 **fantômes d'oreille** (silicone ou résine imprimée) de formes et diamètres variés, avec courbure en S.
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

**Mesure de l'erreur :** distance point-surface entre le maillage et la référence après alignement optimal (RMS, 95e centile, maximum), avec cartographie des écarts.

## 6. Critères Go / No-Go de la phase 1

- **Go :** P2, P3, P4 et P5 atteints sur au moins 3 fantômes, avec au moins une des deux têtes ; T8 validé.
- **Go conditionnel :** précision comprise entre 0,1 et 0,15 mm avec une cause identifiée et corrigeable.
- **No-Go :** précision > 0,15 mm sans amélioration plausible ; ou impossibilité de tenir le diamètre de pointe ≤ 4,5 mm.

## 7. Livrables

1. Prototype fonctionnel (poignée et deux têtes) et plans.
2. Logiciel d'acquisition et de reconstruction (code source).
3. Données brutes et rapport de validation (T1–T8).
4. Nomenclature (BOM) et fournisseurs.
5. Note de conception pour la phase 2.

## 8. Planning indicatif (12 semaines)

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
| Ambiguïté de pose dans un conduit cylindrique | IMU, codeur, texture de l'image, motif dense (tête B) |
| Reflets sur surface humide | Filtrage, polarisation, seuils adaptatifs |
| Dérive de l'étalonnage | Étalonnage de contrôle avant chaque session |

## 11. Points ouverts à décider

1. Capteur de référence disponible en interne ou en sous-traitance (micro-CT, scanner industriel) ?
2. Résine pour l'essai T8 : à choisir avec le projet G1 (imprimante : machine à capsules SprintRay, décidé).
3. Fournisseurs pour la micro-caméra, le VCSEL et le DOE.
4. FTO différé (décision actuelle : pas d'étude pour le moment). Le choix de la tête A ou B repose sur les résultats de phase 1. Revoir cette décision au plus tard à la gate M5, avant la fabrication des prototypes destinés à des sites tiers et avant toute divulgation détaillée.
