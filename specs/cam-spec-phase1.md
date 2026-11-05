# Spécification technique : logiciel CAM de préparation de fabrication (Phase 1)

Version 0.2 (brouillon). **SprintRay dispose déjà d'un CAM intégré à son cloud.** Le chantier consiste à l'auditer, le paramétrer et l'étendre pour l'auriculaire ; un moteur CAM propriétaire n'est envisagé que si l'extension est impossible. Aucun budget n'est chiffré pour le moment. Les valeurs chiffrées sont des cibles de départ à valider par les premiers essais. Décisions intégrées : impression sur machines à capsules SprintRay ; budget d'erreur total de la chaîne de 0,2 mm RMS, dont 0,10 mm pour l'impression ; la précision d'impression inférieure à 0,10 mm est annoncée pour le dentaire et reste à démontrer sur formes auriculaires.

## 1. Objectif et périmètre

Le CAM transforme un design approuvé (sortie du CAD) en fichier de fabrication prêt pour la machine : orientation de la pièce, supports, regroupement sur le plateau, compensation du retrait et de la polymérisation, génération du fichier machine selon la recette, identification et traçabilité. C'est le lien entre le design et l'imprimante : ses choix influencent directement la précision, l'ouverture des canaux, l'état des surfaces et le rendement.

**Objectif de la phase 1 (12 semaines, M0 à M2) :** auditer le CAM du cloud SprintRay (fonctions, paramètres accessibles, extensibilité, format du fichier machine) ; démontrer qu'il produit, avec des profils auriculaires, des paires avec des canaux ouverts et un écart conforme au budget d'erreur ; identifier les règles propres à l'auriculaire qui apportent un gain mesurable, et décider comment les intégrer (extension du CAM cloud ou service de préparation en amont) ; fixer les exigences du CAM de la machine intégrée G3.

**Inclus :** import du design, contrôles d'entrée, orientation, supports, regroupement et identité des pièces, compensation, génération du fichier machine, contrôles de simulation, journal, interface de revue opérateur.
**Exclus (phases suivantes) :** CAD (voir la spécification du logiciel de design), pilotage de la machine en temps réel, entraînement d'un modèle IA complet, certification logicielle.

## 2. Exigences de performance

| Réf. | Exigence | Cible de départ |
|---|---|---|
| C1 | Canaux ouverts et traversables après impression, supports et nettoyage | 100 % sur le corpus d'essai |
| C2 | Écart pièce imprimée / design après compensation | ≤ 0,10 mm RMS ; maximum ≤ 0,25 mm |
| C3 | Marques de supports sur les surfaces fonctionnelles (contact conduit, canaux) | Aucune marque visible ni mesurable |
| C4 | Temps de préparation automatique d'une paire (hors revue) | ≤ 60 s |
| C5 | Préparation acceptée par l'opérateur sans retouche | ≥ 80 % |
| C6 | Identité droite/gauche : aucune inversion, marquage physique et contrôle croisé | 0 erreur sur 200 cas simulés |
| C7 | Échecs d'impression attribuables au CAM (supports insuffisants, orientation) | ≤ 5 % des pièces |
| C8 | Reproductibilité : même entrée, mêmes paramètres, même fichier machine | Identique (empreinte numérique) |
| C9 | Traçabilité : paramètres, version des règles, version du fichier, rattachés au Pair ID | 100 % |

## 3. Qualité et sécurité du logiciel

- Aucune règle propriétaire mise en production sans comparaison à la préparation de référence de l'opérateur.
- Règles versionnées, testées et justifiées par produit et par matériau.
- Une préparation qui ne respecte pas les contrôles (canal bouché, surplomb non supporté, collision) est refusée et signalée, jamais corrigée silencieusement.
- Classification réglementaire du logiciel à confirmer avec le conseiller réglementaire ; cycle de vie documenté (exigences, tests, traçabilité) dès maintenant.

## 4. Architecture

Moteur déterministe à règles explicites, paramétré par le quadruplet (produit, matériau, machine, recette). Les fonctions fondées sur les données (compensation apprise, réglages optimisés) viennent en seconde marche, encadrées par la base déterministe et une revue humaine.

### 4.1 Fonctions

| Fonction | Contenu |
|---|---|
| Import et contrôle d'entrée | Design approuvé, métadonnées, étanchéité, unités, côté, cohérence avec la commande |
| Orientation | Choix de l'angle selon la précision, l'accumulation de résine, la surface de contact et les canaux |
| Supports | Positions, diamètres, points de contact évitant les surfaces fonctionnelles, accès au retrait |
| Regroupement et identité | Placement de la paire et de plusieurs cas sur le plateau, séparation, marquage, contrôle droite/gauche |
| Compensation | Correction du retrait et de la polymérisation par matériau, orientation et recette |
| Génération du fichier machine | Découpage en couches, paramètres de la recette, empreinte numérique, version |
| Simulation et contrôles | Détection de canaux bouchés, surplombs, accumulation, collisions, volume utile |
| Revue opérateur | Visualisation de l'orientation et des supports, validation ou correction journalisée |
| Journal | Toutes les décisions et modifications avec version des règles |

### 4.2 Les trois marches

| Marche | Période | Contenu | Gate |
|---|---|---|---|
| 1 | M0–M5 | CAM existant du cloud SprintRay, audité et paramétré par profils (machine, matériau, recette) ; collecte des réglages et des résultats | M5 |
| 2 | M6–M11 | Règles auriculaires en mode shadow (extension du CAM cloud ou service amont) : elles proposent orientation, supports et compensation, l'opérateur décide, le système compare | M11 |
| 3 | M12–M24 | Compensation et réglages pilotés par les données de production, via le CAM cloud ; fichiers machine natifs de la machine intégrée G3 | M18, M24 |

### 4.3 Choix de départ

- Phase 1 : le CAM du cloud SprintRay sert de base, de référence et de repli. Les paramètres accessibles, le format de fichier machine, l'extensibilité (règles, profils, appels externes) et la feuille de route de l'équipe qui le maintient sont à confirmer avant toute dépendance. Cet accès est interne au groupe, ce qui facilite l'accord mais ne dispense pas de le formaliser.
- Formats ouverts pour l'entrée (STL, PLY) et pour les paramètres (JSON) ; le format du fichier machine suit celui de la machine.
- La compensation commence par un modèle simple (facteurs par axe et par matériau) calibré sur des calibres étalons, puis affiné avec les données de production.

## 5. Validation

### 5.1 Corpus et références

- Corpus de 50 géométries auriculaires anonymisées, avec courbures en S, canaux et évents ; le même que celui de l'imprimante.
- Calibres étalons imprimés (cylindres de 6, 8 et 10 mm, tube coudé, canaux de diamètres décroissants).
- Référence de mesure : scanner de laboratoire ou machine de mesure sur les pièces imprimées, comparées au design.

### 5.2 Essais

| Essai | Description | Critère |
|---|---|---|
| T1 | Import et contrôles d'entrée sur tout le corpus | 100 % exploitables ou refusés avec motif |
| T2 | Orientation : plan d'expériences (en lien avec l'essai T5 de l'imprimante) | Réglage optimal documenté, C1, C2 |
| T3 | Supports : marques, canaux, surplombs, retrait | C1, C3 |
| T4 | Regroupement de la paire et de plusieurs cas : positions, identité, marquage | C6 |
| T5 | Compensation : calibres puis géométries réelles, avant et après correction | C2 |
| T6 | Simulation contre réalité : la détection de canaux bouchés et de défauts annonce-t-elle les échecs observés ? | Concordance mesurée, aucun échec non détecté sur les canaux |
| T7 | Reproductibilité et traçabilité | C8, C9 |
| T8 | Intégration : fichier accepté par la machine, échange avec le CAD et le cloud, DHR complété | Cycle complet sans intervention hors procédure |

## 6. Critères Go / No-Go de la phase 1

- **Go :** C1, C2, C3, C6, C8 et C9 atteints sur le corpus ; T8 validé ; paramètres de l'outil existant documentés ; exigences G3 du CAM rédigées.
- **Go conditionnel :** C2 entre 0,10 et 0,15 mm avec cause identifiée ; le budget d'erreur de la chaîne doit alors être renégocié avant la gate M2.
- **No-Go :** paramètres de l'outil existant inaccessibles et pas de repli, ou précision et canaux incompatibles sans amélioration plausible.

## 7. Validation en mode shadow (M6 à M11)

Les règles auriculaires du CAM sont évaluées sans risque : pour chaque pièce, l'opérateur prépare comme d'habitude, le moteur propose en aveugle, et les deux préparations sont comparées.

| Indicateur | Définition | Cible indicative |
|---|---|---|
| Acceptation | Propositions du moteur acceptées sans retouche significative | ≥ 80 % |
| Échecs d'impression | Pièces échouées pour cause de préparation, moteur contre opérateur | Inférieur ou égal à l'opérateur |
| Canaux ouverts | Pièces dont les canaux sont ouverts | 100 % |
| Précision | Écart pièce / design, moteur contre opérateur | Inférieur ou égal à l'opérateur |
| Temps de préparation | Moteur contre opérateur | Gain d'au moins 50 % |
| Exceptions | Cas signalés ou refusés | Documentés, aucun cas silencieux erroné |

Échantillon : au moins 100 paires, collectées dans le pilote du logiciel de design et dans la qualification de G1. La décision de mise en production du CAM propriétaire est prise à M11 ; elle conditionne son usage dans le pilote G1.

## 8. Livrables

1. Rapport d'audit du CAM cloud, profils auriculaires et règles d'extension (code source si développées), interface de revue.
2. Règles de préparation documentées par produit et par matériau.
3. Rapport de validation T1 à T8, données brutes, corpus.
4. Comparaison avec l'outil CAM de référence (précision, canaux, temps, rendement).
5. Exigences du CAM de la machine intégrée G3, version 1, et note de conception de la marche 2.

## 9. Planning indicatif (12 semaines)

| Semaines | Contenu |
|---|---|
| 1–2 | Accès à l'outil et aux paramètres, droits, corpus, règles avec les opérateurs |
| 3–5 | T1 à T3 : import, orientation, supports (en lien avec les essais de l'imprimante) |
| 5–8 | T4 et T5 : regroupement, identité, compensation |
| 8–10 | T6 et T7 : simulation, reproductibilité |
| 10–11 | T8 : intégration avec le CAD, le cloud et la machine |
| 12 | Rapport et décision Go / No-Go |

**Budget :** non chiffré à ce stade ; il dépendra du périmètre d'extension issu de l'audit.

## 10. Interfaces

- Entrée : design approuvé et métadonnées du CAD, commande et recette du cloud (le CAM est intégré au cloud SprintRay).
- Sortie : fichier machine, paramètres et empreinte numérique vers la machine et le DHR.
- Retour : résultats de contrôle et d'impression, utilisés pour la compensation et les règles.

## 11. Risques et parades

| Risque | Parade |
|---|---|
| CAM cloud non extensible ou paramètres inaccessibles | Accord interne dès la phase 0 ; service de préparation en amont ; moteur CAM propriétaire en dernier recours |
| Dépendance à la feuille de route de l'équipe cloud de SprintRay | Accord de priorités, interfaces ouvertes |
| Canaux bouchés ou déformés malgré les supports | Plan d'expériences, simulation, règles par produit |
| Marques de supports sur les surfaces fonctionnelles | Règles de points de contact, orientation, finition |
| Inversion droite/gauche | Marquage physique, contrôle croisé, essais d'inversion |
| Compensation qui dérive d'une résine ou d'un lot à l'autre | Étalonnage par lot, suivi des données, limites de correction |
| Dépendance au format propriétaire de la machine | Format d'échange ouvert en amont, couche d'adaptation |
| Règles non partagées entre opérateurs | Ateliers de formalisation, versionnage, arbitrage |

## 12. Points ouverts à décider

1. Accès aux paramètres, au format de fichier machine et à l'extensibilité du CAM du cloud SprintRay, et feuille de route de l'équipe qui le maintient.
2. Propriété et protection de la base de règles.
3. Politique de marquage et d'identification physique des pièces.
4. Format du fichier machine de la machine intégrée G3, à décider avec le chantier imprimante.
5. Classification réglementaire du logiciel.
