# Plan pilote du logiciel de design avec des techniciens

Version 0.2 (brouillon). Les chiffres sont des ordres de grandeur à ajuster avec les partenaires. Calendrier : les mois ci-dessous sont relatifs ; dans le calendrier maître, le mois 0 de ce pilote correspond à **M4** (accords et installation M4–M5, production shadow M6–M8, bilan M9). Ce plan suppose que la phase 1 (moteur déterministe validé sur corpus) est terminée avec un Go. Il se déroule en **mode shadow** : le logiciel propose, le technicien décide.

## 1. Objectifs

1. Mesurer sur des cas réels le taux d'acceptation des designs sans retouche significative.
2. Mesurer le temps de conception et le temps de correction par rapport au flux actuel.
3. Collecter les triplets (maillage, design automatique, design final corrigé) pour entraîner et valider les fonctions IA.
4. Recueillir l'avis des techniciens et mesurer l'intérêt commercial (remplacement ou complément du CAD actuel).

## 2. Partenaires

- **Nombre :** 2 à 3 laboratoires ou fabricants, profils différents.
- **Critères :** au moins 20 à 30 paires par mois, techniciens référents motivés, accord de partage des maillages et designs, outil CAD actuel connu.
- **Contrepartie :** accès gratuit pendant le pilote, formation, accès prioritaire à la version commerciale.
- Ces sites peuvent être les mêmes que ceux des pilotes scanner et cellule, pour mutualiser les données.

## 3. Cadre juridique

- **Accord de données :** propriété des données (propriété client, licence d'usage pour l'apprentissage), durée, anonymisation, droit de retrait.
- **Données personnelles :** pas de nom ni d'identité, identifiants pseudonymisés ; conformité locale (RGPD, loi chinoise si applicable).
- **Propriété intellectuelle :** les règles de design et modèles restent la propriété de la société ; les modifications du technicien restent confidentielles.
- **Statut du logiciel :** à confirmer avec le conseiller réglementaire avant tout usage au-delà de la phase pilote.

## 4. Protocole du pilote

### 4.1 Pour chaque cas

1. Le technicien reçoit le maillage et réalise son design habituel (référence), temps chronométré.
2. Le logiciel génère un design automatique sur le même maillage (en aveugle).
3. Le technicien relit le design automatique, le corrige si besoin ; chaque correction est journalisée.
4. Les deux designs sont comparés (écart de forme, paramètres, durée).
5. La pièce retenue est fabriquée selon le flux normal du site.

### 4.2 Taille de l'échantillon

- Pilote initial : 100 à 150 oreilles.
- Extension : 300 oreilles ou plus pour l'entraînement et la validation IA.

## 5. Mesures et indicateurs

| Indicateur | Définition | Cible indicative |
|---|---|---|
| Acceptation sans retouche | Designs auto validés sans correction significative (< 2 min) | ≥ 60 %, puis ≥ 80 % |
| Temps de correction | Minutes moyennes par design automatique | ≤ 30 % du temps de design manuel |
| Gain de temps global | Temps manuel vs temps auto + revue | ≥ 50 % |
| Écart de forme | Surface de contact du design auto vs maillage d'entrée, hors offsets (RMS) | ≤ 0,08 mm ; l'écart au design final du technicien est suivi à part |
| Taux d'exceptions signalées | Cas refusés ou alertés | Documenté, aucun cas silencieux erroné |
| Taux de refabrication | Pièces refaites pour cause de design | ≤ taux habituel du site |
| Satisfaction des techniciens | Questionnaire | ≥ 4/5 avec liste des irritants |
| Intention d'achat | Prix accepté, remplacement du CAD actuel | oui ou conditions précises |

## 6. Données collectées pour l'IA

Pour chaque oreille :

- maillage d'entrée et métadonnées (côté, produit, matériau) ;
- design automatique et ses paramètres ;
- design du technicien (référence) et design final corrigé ;
- historique des corrections ;
- temps par étape ; résultats de fabrication si disponibles.

Objectif : au moins 150 à 300 triplets avec droits d'usage clairs avant l'entraînement. Données versionnées, format ouvert (STL, PLY, JSON), stockage sécurisé.

## 7. Organisation

| Rôle | Responsabilité |
|---|---|
| Chef de projet | Planning, relation sites, rapports |
| Ingénieur logiciel / géométrie | Corrections, mises à jour, support |
| Ingénieur IA | Préparation des données, premiers modèles |
| Technicien référent (par site) | Cas, retours, relecture |
| Responsable qualité | Règles, traçabilité, versions |
| Conseiller réglementaire (externe) | Statut du logiciel |

Support : réponse sous 24 à 48 h ; mise à jour au plus toutes les deux semaines ; réunion hebdomadaire de 30 min.

## 8. Planning indicatif (6 mois, de M4 à M9)

| Période | Contenu |
|---|---|
| Mois 0–1 (M4) | Accords, droits de données (sites choisis dès M1–M3) |
| Mois 1–2 (M5) | Installation, formation, essais à blanc sur des cas anonymisés |
| Mois 2–5 (M6–M8) | Pilote shadow (100 à 150 oreilles), ajustements toutes les deux semaines |
| Mois 5–6 (M9) | Analyse, rapport, décision de la suite ; release du moteur pour le pilote G1 |
| M10–M15 (si Go) | Extension à 300 oreilles, premier entraînement IA, comparaison à la référence humaine |

## 9. Budget indicatif

| Poste | Ordre de grandeur |
|---|---|
| Équipe (logiciel, IA, support) | à chiffrer selon allocation réelle |
| Licences CAD de référence | à chiffrer |
| Conseil réglementaire et juridique | à chiffrer |
| Déplacements, formation, contreparties | à chiffrer |

Les montants seront estimés après la phase 0 ; aucun chiffre n'est avancé sans coûts réels.

## 10. Critères Go / No-Go

- **Go :** acceptation ≥ 60 %, gain de temps ≥ 50 %, zéro cas silencieux erroné, refabrication au plus égale à la référence, au moins un site prêt à adopter.
- **Go conditionnel :** un indicateur manqué avec cause identifiée et plan de correction chiffré.
- **No-Go :** acceptation faible sans amélioration plausible, ou refus des sites.

## 11. Risques et parades

| Risque | Parade |
|---|---|
| Techniciens peu disponibles | Référent désigné, sessions courtes |
| Données insuffisantes | Plusieurs sites, mutualisation avec les pilotes scanner et cellule |
| Variabilité entre techniciens | Protocole commun, plusieurs techniciens par site |
| Droits de données contestés | Accord écrit avant la collecte |
| Cas atypiques | Règle de refus, enregistrement des échecs |
| IA non reproductible | Versions de modèles figées, jeu de test séparé |

## 12. Points ouverts à décider

1. Sites et nombre de techniciens.
2. Régime des données (propriété, durée, usage pour l'IA).
3. Logiciel de référence et conditions de licence.
4. Seuil d'acceptation définitif.
