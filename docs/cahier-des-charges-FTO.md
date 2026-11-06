# Cahier des charges – Étude FTO (Freedom To Operate)

> **Statut : étude lancée le 5 novembre 2026** (`DECISIONS.md`, décision 4 mise à jour). Prochaine étape : choisir le cabinet et signer le NDA. Les budgets et délais mentionnés ci-dessous sont indicatifs ; le budget de l'étude sera fixé sur devis. Développement localisé en Chine : le cabinet doit couvrir la CNIPA. Un criblage préliminaire (familles à examiner en priorité, limites) figure dans `docs/analyse-fto-preliminaire.md`.
**Projet** : scanner 3D intra-auriculaire + chaîne complète scan → CAO automatique → impression 3D continue
**Date** : 2026-11-04 | **Statut** : projet à envoyer au cabinet de conseil en PI

---

## 1. Objectif
Déterminer si la fabrication, l'utilisation et la vente du système décrit ci-dessous peuvent enfreindre des brevets en vigueur, et identifier les risques, les brevets bloquants et les contournements possibles. Le résultat doit permettre une décision go/no-go avant tout développement logiciel lourd.

## 2. Périmètre technique à analyser
| # | Bloc | Description | Priorité |
|---|------|-------------|----------|
| 1 | Sonde optique intra-conduit | Lumière structurée : anneau laser (A) ou motif codé monocoup (B), DOE, optique de sonde miniature, centrage/guidage | Haute |
| 2 | Suivi de pose / reconstruction | IMU + odométrie, ICP, fusion TSDF, filtrage par IA | Haute |
| 3 | Scan ultrasons (option) | Sonde type IVUS dans le conduit, couplant | Basse |
| 4 | CAO automatique de coque | Génération automatique de la coque/embout depuis le scan (découpe, évents, parois, prise d'empreinte virtuelle) | Haute |
| 5 | Chaîne intégrée | Scan → CAO → impression sans intervention, pièce finie en quelques minutes | Haute |
| 6 | Impression continue | Procédé continu (type DLP/CLIP) appliqué aux coques auditives, résines | Moyenne |
| 7 | Collecte de données / IA | Entraînement de modèles sur les scans (aspect données/vie privée à part) | Basse |

## 3. Juridictions
- **Chine** (CN) – fabrication et marché principal : prioritaire
- **Union européenne** (EP + DE, FR, NL, DK) – le Danemark et l'Allemagne concentrent les grands acteurs de l'audiologie
- **États-Unis** (US) – marché majeur
- Optionnel : JP, KR, famille PCT

## 4. Acteurs à examiner en priorité (portefeuilles connus)
Cible de la recherche sur les titulaires, à confirmer par le cabinet :
- Audiologie / aides auditives : Sonova, Demant, GN, WS Audiology, Starkey
- Scan 3D dentaire/auditif : 3Shape, Align, Dentsply Sirona, Carestream
- Impression 3D : Carbon, Formlabs, Stratasys, EnvisionTEC/Desktop Metal
- Scanners intra-auriculaires existants : Otoscan (Otometrics/Natus), Sonova (Phonak), Siemens/Sivantos
- Capteurs 3D industriels d'alésage et endoscopie 3D (brevets de sonde)
- Acteurs chinois : fabricants locaux d'aides auditives, de scanners 3D, de résines et imprimantes

## 4bis. Brevets prioritaires identifiés (étude de l'Otoscan)

Famille **United Sciences / 3DM Systems** (inventeur Karol Hatzilias, dépôts de 2012). Titulaire actuel, statut juridique, pays couverts et échéances **inconnus** : à vérifier en premier. Aucun de ces brevets ne cite Otometrics ni Natus comme titulaire ; leur lien avec l'Otoscan commercial est probable, non confirmé.

| Brevet | Objet | Intérêt pour nous |
|---|---|---|
| US 8,715,173 | Laser en anneau et en éventail | Architecture A (anneau laser) |
| US 8,900,125 | Otoscanning avec modélisation 3D | Chaîne scan → modèle |
| US 8,900,127 | Capteurs de pression, « compliance » du conduit | Force d'appui |
| US 8,900,128 | Caméra unique pour vidéo et mesure (laser pulsé une image sur deux) | Capteur partagé |
| US 8,900,129 | Otoscope vidéo | Sonde |
| US 8,900,130 | Alerte de sécurité (distance au tympan estimée par statistiques d'oreille) | Alerte de profondeur |

Éléments techniques à examiner contre nos choix : réflecteur conique et lentille diffractive pour l'anneau ; objectif grand angle (environ 150°) ; table de correspondance pixel → coordonnées ; suivi par rétroréflecteurs sur clip ou serre-tête ; suivi par caméras de sonde lisant un casque à repères (Otoscan, non décrit dans ces brevets) ; localisation du tympan par stéréo-mouvement ou point laser parallèle.

Demander au cabinet de comparer chacune des **options de suivi de pose** (T1 à T4 de `plan-developpement-scanner.md`) à ces brevets, et de proposer des contournements.

Titulaires à ajouter à la liste du §4 : Natus / Otometrics, United Sciences / 3DM Systems, PointClear Solutions (conception du logiciel de l'Otoscan).

## 5. Livrables attendus
1. **Stratégie de recherche** documentée (classes CPC, mots-clés, bases utilisées)
2. **Liste des brevets pertinents** en vigueur (statut juridique, pays, échéance)
3. **Analyse de chevauchement** (claim charts) pour les 10–15 brevets les plus proches
4. **Matrice de risque** par bloc technique × juridiction (faible / moyen / élevé)
5. **Options** : contournement de conception, licence, opposition/invalidation
6. **Opinion écrite** sur la liberté d'exploitation, avec limites et hypothèses
7. **Zones libres** pour dépôt de brevets propres (chaîne complète, CAO automatique)

## 6. Classes CPC / pistes de recherche (point de départ)
- A61B 1/227 et A61B 5/00, A61B 1/00 : endoscopes/otoscopes, mesure 3D intra-conduit
- G01B 11/25 : mesure par lumière structurée
- H04R 25/00 (en particulier 25/65 et 25/652) : aides auditives, coques sur mesure
- B33Y 10/00, 30/00, 50/02 et B29C 64/00 : fabrication additive
- G06T 17/00, G06T 7/00 : reconstruction 3D, ICP, fusion volumique
- G06F 30/00 : CAO automatique
- G02B 27/42 : éléments optiques diffractifs (DOE)

Mots-clés (EN/ZH/DE/FR) : ear canal scanner, in-ear 3D scan, structured light probe, laser ring, custom earmold, hearing aid shell, automated shell design, 耳道扫描, 助听器外壳, Ohrabdruck-Scanner, scanner conduit auditif.

## 7. Contraintes et hypothèses
- Budget cible : **10–40 k€**, délai : **4–8 semaines**
- Le cabinet doit avoir des compétences en **Chine** (ou un correspondant local) et en optique/dispositifs médicaux
- Confidentialité : accord de confidentialité (NDA) avant l'envoi de la description détaillée
- La description technique fournie reste au niveau **architecture**, sans les détails d'invention non déposée (brevets propres à déposer **avant** divulgation)
- L'étude ne couvre pas la réglementation (MDR/NMPA/FDA), traitée séparément

## 8. Sélection du cabinet – critères
| Critère | Poids |
|---------|-------|
| Expérience en dispositifs médicaux et optique | 25 % |
| Capacité en Chine (CNIPA) et en Europe (EPO) | 25 % |
| Références FTO de projets comparables | 20 % |
| Prix et clarté du devis (forfait) | 15 % |
| Délai et disponibilité | 10 % |
| Langues (FR/EN/ZH) | 5 % |

Demander des devis à 3 cabinets minimum. Demander s'ils proposent un **FTO en deux étapes** : (1) triage rapide à budget réduit pour écarter les risques majeurs, (2) analyse approfondie sur les brevets retenus.

## 9. Calendrier cible
| Semaine | Étape |
|---------|-------|
| S0 | Choix du cabinet, NDA, envoi de la description technique |
| S1–S2 | Stratégie de recherche validée avec vous |
| S3–S5 | Recherche et tri des brevets |
| S5–S7 | Claim charts et matrice de risque |
| S8 | Rapport final et réunion de restitution |

## 10. Questions à poser aux cabinets
1. Étude en une ou deux étapes ? Forfait ou régie ?
2. Qui réalise l'analyse en Chine, et en quelle langue sont rendus les claim charts ?
3. Que couvre l'opinion écrite en termes de responsabilité ?
4. Comment gérez-vous les demandes de brevets en cours (non encore délivrées) susceptibles de le devenir ?
5. Pouvez-vous coupler l'étude avec une analyse de brevetabilité de nos propres inventions ?

---
*Document de travail : à faire valider par un conseil en propriété industrielle avant envoi. Il ne constitue pas un avis juridique.*
