# Spécification technique : logiciel de design auriculaire (Phase 1)

Version 0.2 (brouillon). Les valeurs chiffrées sont des cibles de départ à valider par les premiers essais.

## 1. Objectif et périmètre

**Objectif de la phase 1 (environ 12 semaines) :** démontrer qu'un moteur de design **déterministe** (règles explicites) génère, à partir d'un maillage de conduit, un embout ou une coque fabricable, avec un résultat comparable à celui d'un technicien sur un corpus de référence. Les fonctions IA sont limitées à de l'aide (détection de repères) en mode proposition.

**Inclus :** import de maillages, détection de repères, génération du design, contrôles de fabricabilité, interface de revue pour l'opérateur, journal des modifications, export.
**Exclus (phases suivantes) :** conception entièrement autonome sans revue, entraînement d'un modèle IA complet, intégration cloud complète, certification logicielle.

## 2. Exigences de performance

| Réf. | Exigence | Cible phase 1 |
|---|---|---|
| P1 | Entrée | STL/PLY étanche ou réparable, unités mm, côté connu |
| P2 | Détection des repères (méat, premier et second coude, point d'insertion…) | Écart ≤ 1 mm sur ≥ 90 % des cas du corpus |
| P3 | Temps de conception automatique | ≤ 60 s par oreille (hors revue) |
| P4 | Acceptation sans retouche (jugée par le technicien) | ≥ 60 % en phase 1, objectif ≥ 80 % à terme |
| P5 | Écart entre la surface de contact du design et le maillage d'entrée, hors offsets prescrits (RMS) | ≤ 0,08 mm (part « design » du budget d'erreur de 0,2 mm, voir README). L'écart au design du technicien est suivi comme indicateur d'acceptation, pas comme budget géométrique |
| P6 | Contrôles de fabricabilité | 0 pièce hors règles (épaisseur minimale, canaux, évents, rayons) |
| P7 | Journalisation | Chaque modification tracée (qui, quand, quoi, version) |
| P8 | Sortie | STL étanche en mm, repère standard, métadonnées (ID, côté, version, règles appliquées) |

## 3. Sécurité et qualité du logiciel

- Aucune sortie jugée « sûre » sans revue humaine en phase 1.
- Règles de design versionnées, testées et justifiées par produit.
- Classification du logiciel (aide à la conception d'un dispositif) à confirmer avec le conseiller réglementaire ; appliquer dès maintenant un cycle de vie documenté (exigences, tests, traçabilité).
- Aucun modèle IA mis en production sans benchmark validé.

## 4. Architecture

Deux couches séparées :

- **Base déterministe :** offsets, épaisseurs, canal acoustique, évents, logements de filtres, interfaces, marquages, contrôles de fabricabilité.
- **Aide IA (optionnelle) :** détection de repères, proposition de paramètres, détection d'exceptions. Toute proposition passe par la base déterministe puis par la revue.

### 4.1 Modules

| Module | Fonction |
|---|---|
| Import et réparation | Contrôle d'étanchéité, orientation, nettoyage du maillage |
| Repères | Détection automatique et correction manuelle |
| Design | Coque, canal, évent, filtre, marquage |
| Contrôle | Règles de fabricabilité, alertes |
| Revue | Interface opérateur, comparaison, validation |
| Journal | Historique des modifications et versions |
| Export | STL, métadonnées, lien avec la cellule de production |

### 4.2 Choix de départ

- Phase 1 s'appuie sur un CAD existant (par exemple 3Shape ou Cyfex) sous licence, en parallèle, pour servir de référence et de repli.
- Format interne ouvert (STL, PLY, JSON de paramètres).
- Plateforme : à choisir (moteur géométrique existant ou développement maison).

## 5. Validation

### 5.1 Corpus de référence

- 100 à 200 maillages sous droits d'utilisation clairs, avec côté, produit, et design final d'un technicien.
- Corpus séparé : apprentissage / validation / test (aucune oreille dans deux ensembles).
- Cas atypiques identifiés : conduits très coudés, sténoses, maillages incomplets.

### 5.2 Essais

| Essai | Description | Critère |
|---|---|---|
| T1 | Import, réparation, orientation sur tout le corpus | 100 % exploitables ou refusés avec motif |
| T2 | Détection des repères | P2 |
| T3 | Génération du design sur le corpus test | P3, P5 |
| T4 | Contrôles de fabricabilité | P6 |
| T5 | Revue par 3 techniciens : acceptation sans retouche | P4 |
| T6 | Cas atypiques : le système signale ou refuse | Aucune génération silencieuse erronée |
| T7 | Journal et reproductibilité : même entrée, même sortie | Résultat identique |
| T8 | Impression des designs sur la cellule G1 (capsules SprintRay), mesure de la pièce | Écart pièce / design ≤ 0,10 mm RMS |

## 6. Critères Go / No-Go de la phase 1

- **Go :** P2 à P6 et P8 atteints sur le corpus test, T6 et T7 validés, T8 conforme.
- **Go conditionnel :** acceptation entre 40 et 60 % avec cause identifiée et plan de correction.
- **No-Go :** acceptation < 40 % sans amélioration plausible, ou droits sur le corpus insuffisants.

## 7. Livrables

1. Moteur de design et interface de revue (code source).
2. Règles de design documentées par produit.
3. Corpus de référence, protocole et rapport de validation T1 à T8.
4. Comparatif avec le CAD de référence (qualité, temps, coût).
5. Note de conception pour la phase 2 (modèles IA, données à collecter).

## 8. Planning indicatif (12 semaines)

| Semaines | Contenu |
|---|---|
| 1–2 | Corpus, droits, choix de plateforme, règles de design avec les techniciens |
| 3–5 | Import, repères, base déterministe |
| 5–8 | Design, contrôles de fabricabilité, interface de revue |
| 8–10 | Campagne T1 à T7 |
| 10–11 | T8 avec la cellule G1 |
| 12 | Rapport et décision Go / No-Go |

**Budget indicatif :** coût principal en ingénierie (géométrie, logiciel) ; licences de CAD de repli à chiffrer.

## 9. Interfaces

- Entrée : maillage du scanner ou scan d'empreinte (STL/PLY).
- Sortie : STL de fabrication et fichier de paramètres vers la cellule et le cloud.
- Retour : corrections des techniciens, utilisées comme données d'apprentissage.

## 10. Risques et parades

| Risque | Parade |
|---|---|
| Droits sur le corpus ou le CAD insuffisants | Accords écrits en phase 0 ; CAD de repli |
| Règles de design non partagées entre techniciens | Ateliers de formalisation, versionnage, arbitrage |
| Cas atypiques mal gérés | Règle de refus, signalement obligatoire |
| Dépendance aux licences externes | Format ouvert, plan d'internalisation progressif |
| Surconfiance dans l'IA | Mode proposition, benchmark avant toute autonomie |

## 11. Points ouverts à décider

1. CAD de repli et conditions de licence (API, export, utilisation des données).
2. Source du corpus et droits d'utilisation pour l'entraînement.
3. Produits couverts en phase 1 (embout, protection, avec filtre).
4. Classification réglementaire du logiciel.
