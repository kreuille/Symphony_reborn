# Spécification technique : extension de SprintRay Cloud pour l'auriculaire, orchestration et DHR (Phase 1)

Version 0.3 (brouillon). **SprintRay dispose déjà d'un cloud, avec un CAM intégré.** Cette spécification fixe les exigences du système pour les produits auriculaires ; chaque exigence est classée en phase 0 : déjà fournie, à configurer, à développer comme extension, ou à couvrir par un service complémentaire. Aucun budget n'est chiffré pour le moment. Les valeurs chiffrées sont des cibles de départ à valider par les premiers essais. Phase 1 : semaines 1 à 12, soit M0 à M2 du calendrier maître, avec Go / No-Go à la gate M2.

## 1. Objectif et périmètre

**Objectif de la phase 1 (environ 12 semaines) :**

1. Auditer SprintRay Cloud et son CAM intégré face aux exigences P1 à P9 : matrice d'écarts, avec l'équipe cloud de SprintRay.
2. Décider pour chaque écart : configurer, étendre l'existant, ou ajouter un service complémentaire.
3. Démontrer qu'une commande auriculaire traverse le système de bout en bout (identité droite/gauche, fichiers, jobs, recettes, contrôles, libération) avec un dossier numérique de lot (DHR) complet, résistant aux pannes et fonctionnant en mode dégradé hors ligne.

**Inclus :** audit de l'existant, extensions pour les objets auriculaires (identité, latéralité, produit), recettes auriculaires, DHR, droits d'accès, journal d'audit, sauvegardes, agent local (edge) avec mode hors ligne s'il n'existe pas déjà, mises à jour réversibles, interfaces avec le scanner et le CAD.
**Exclus (phases suivantes) :** multisite complet, intégration MES, facturation, application mobile, certification complète.

## 2. Exigences de performance

| Réf. | Exigence | Cible phase 1 |
|---|---|---|
| P1 | Identité : Case ID, Pair ID, latéralité, produit, matériau, site | 0 erreur d'identité sur 200 cas simulés |
| P2 | Fichiers : scan brut, maillage, design approuvé, fichier de fabrication | Hachés, versionnés, reliés au cas |
| P3 | Jobs idempotents, états durables, reprise après erreur | Aucun doublon après panne simulée |
| P4 | Recettes : machine, matériau, lot, version | Versionnées, application tracée |
| P5 | DHR : opérateurs, contrôles, dérogations, libération | 100 % complet pour les cas de test |
| P6 | Mode hors ligne (edge) | ≥ 8 h d'autonomie avec synchronisation sans perte |
| P7 | Journal d'audit | Toute modification de design, recette ou libération tracée, non modifiable |
| P8 | Sauvegarde et restauration | Restauration testée ; objectif de reprise ≤ 4 h |
| P9 | Mises à jour | Signées, avec retour arrière testé |

## 3. Sécurité et données

- Contrôle d'accès par rôle (opérateur, technicien, qualité, administrateur, support).
- Chiffrement en transit et au repos ; gestion des secrets.
- Pseudonymisation : séparation de l'identité commerciale et des données techniques.
- Responsable de traitement, finalités, durées et transferts éventuels vers la Chine à définir avant tout usage avec des données de sites réels.
- Journal d'audit signé ; revue d'accès périodique.
- Test d'intrusion avant le pilote.

## 4. Architecture

| Composant | Fonction |
|---|---|
| API et modèle de données | Commandes, cas, paires, fichiers, recettes (existant à auditer, extensions auriculaires) |
| Orchestrateur | Jobs idempotents, états, reprises, quarantaine |
| Agent local (edge) | Exécution locale, cache, mode hors ligne, synchronisation |
| Connecteurs | Scanner, CAD, machines, postes de contrôle |
| DHR | Dossier de lot, signatures, libération |
| Administration | Utilisateurs, rôles, recettes, versions |
| Observabilité | Journaux, alertes, diagnostic à distance |

### 4.1 Choix de départ

- Modèle d'événements : chaque changement d'état est un événement horodaté et relié à un utilisateur ou un système.
- États d'un job : créé, en cours, bloqué, en erreur, en quarantaine, terminé, annulé.
- Contrats de données entre scanner, CAD, cloud et machines, documentés et versionnés.
- Stratégie de déploiement : l'infrastructure existante de SprintRay Cloud est réutilisée ; agent local par site si le mode hors ligne n'existe pas ; hébergement et transferts de données à aligner avec l'existant et le cadre juridique.
- Rien n'est supposé sur le périmètre actuel de SprintRay Cloud : l'audit de phase 0 le décrit.

## 5. Validation

### 5.1 Environnement et jeux de test

- Environnement de test isolé, jeux de 200 cas synthétiques avec scénarios d'erreur.
- Simulateurs de machines et de scanners.
- Cas réels anonymisés issus des phases 1 des autres projets.

### 5.2 Essais

| Essai | Description | Critère |
|---|---|---|
| T1 | Identité et latéralité sur 200 cas, y compris tentatives d'inversion | P1 |
| T2 | Cycle complet : commande, scan, design, fabrication, contrôle, libération | DHR complet (P5) |
| T3 | Pannes : coupure réseau, redémarrage, doublons de messages | P3 |
| T4 | Mode hors ligne 8 h et resynchronisation | P6 |
| T5 | Contrôle d'accès et journal d'audit | P7, aucun accès hors rôle |
| T6 | Sauvegarde, restauration, retour arrière de mise à jour | P8, P9 |
| T7 | Test d'intrusion et revue de sécurité | Aucun défaut critique ouvert |
| T8 | Charge : plusieurs cellules, plusieurs sites simulés | Pas de perte, latence acceptable |

## 6. Critères Go / No-Go de la phase 1

- **Go :** P1 à P9 atteints sur les essais, aucun défaut critique ouvert, décision prise sur l'hébergement et les transferts de données.
- **Go conditionnel :** défauts non critiques avec plan de correction daté.
- **No-Go :** identité ou traçabilité non fiables, ou impossibilité de respecter le cadre de données.

## 7. Livrables

1. Plateforme, agent local et API documentés (code source).
2. Contrats de données entre composants.
3. Rapport de validation T1 à T8 et rapport de sécurité.
4. Procédures de sauvegarde, restauration, mise à jour et support.
5. Registre des traitements de données et analyse d'impact.
6. Note de conception pour la phase 2 (multisite, MES).

## 8. Planning indicatif (12 semaines)

| Semaines | Contenu |
|---|---|
| 1–2 | Audit de SprintRay Cloud et de son CAM, matrice d'écarts, contrats de données, cadre de données |
| 3–5 | Extensions auriculaires, premiers jobs et recettes |
| 5–8 | DHR, droits, journal, agent local, mode hors ligne |
| 8–10 | Campagne T1 à T6 |
| 10–11 | Test d'intrusion, correction, charge |
| 12 | Rapport et décision Go / No-Go |

**Budget :** non chiffré à ce stade ; il dépendra du périmètre d'extension issu de l'audit.

## 9. Interfaces

- Scanner : maillage et métadonnées (voir spec scanner section 9).
- Logiciel de design : maillage en entrée, design et journal en sortie.
- Cellule G1 : paramètres de recette, mesures QC, résultat de libération.
- Utilisateurs : interface web pour commande, suivi, libération.

## 10. Risques et parades

| Risque | Parade |
|---|---|
| Erreur d'identité ou de latéralité | Contrôles croisés, essais d'inversion, double validation |
| Cloud indisponible | Agent local, mode hors ligne, resynchronisation contrôlée |
| Cadre de données (transferts vers la Chine) mal défini | Décision juridique en phase 0, hébergement adapté |
| Dérive de périmètre | Périmètre minimal en phase 1, backlog contrôlé |
| Faille de sécurité | Test d'intrusion, revue de code, droits minimaux |
| Perte de données | Sauvegardes testées, journaux d'audit |

## 11. Points ouverts à décider

1. Hébergement, région et responsable de traitement.
2. Transferts de données vers la Chine et mesures associées.
3. Niveau de signature électronique requis pour la libération.
4. Priorité des connecteurs (machines, scanner, CAD).
