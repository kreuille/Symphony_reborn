# Plan pilote du cloud et du DHR sur site client

Version 0.3 (brouillon). Le pilote porte sur SprintRay Cloud étendu pour l'auriculaire (le cloud existe déjà ; seules les extensions et la configuration sont évaluées). Les chiffres sont des ordres de grandeur à ajuster avec les partenaires. Calendrier : les mois ci-dessous sont relatifs ; dans le calendrier maître, le mois 0 de ce pilote correspond à **M9** (accords de données et test d'intrusion M6–M8, installation M10, production M11–M13, bilan M14). Ce plan suppose que la phase 1 (plateforme validée en environnement de test) est terminée avec un Go. Il se déroule en parallèle du pilote de la cellule G1, dont il constitue le support numérique.

## 1. Objectifs

1. Vérifier en conditions réelles que chaque paire conserve son identité, sa latéralité, ses fichiers, ses lots, ses recettes et ses contrôles.
2. Mesurer la fiabilité (disponibilité, reprises, mode hors ligne) et la charge de support.
3. Mesurer l'adoption par les opérateurs et le temps de saisie.
4. Tester la valeur du modèle commercial (abonnement, traçabilité à la paire).

## 2. Partenaires

- **Nombre :** les 2 à 3 sites du pilote G1, plus un site test interne.
- **Critères :** réseau fiable ou mode hors ligne acceptable, interlocuteur informatique identifié, accord de traitement des données.
- **Contrepartie :** accès gratuit pendant le pilote, support renforcé, accès prioritaire à l'offre.

## 3. Cadre juridique et sécurité (à régler avant le premier cas réel)

- **Accord de traitement des données :** responsable de traitement, finalités, durées, sous-traitants, transferts vers la Chine, droits des personnes.
- **Conformité :** RGPD en Europe, loi chinoise sur la protection des informations personnelles si applicable, analyse d'impact si nécessaire.
- **Sécurité :** test d'intrusion réalisé, droits par rôle, chiffrement, sauvegardes testées, procédure d'incident.
- **Statut :** le DHR numérique sert de dossier de lot pour le pilote ; son usage réglementaire dépend du fabricant légal (à confirmer).

## 4. Protocole du pilote

### 4.1 Déploiement par site

1. Installation de l'agent local, configuration des rôles et des recettes.
2. Formation des opérateurs et de l'administrateur du site.
3. Mode shadow pendant 2 semaines : saisie parallèle avec le flux habituel du site.
4. Passage en production sur le domaine qualifié, avec support renforcé.
5. Exercice de panne planifié : coupure réseau, restauration, retour arrière de mise à jour.

### 4.2 Taille de l'échantillon

- Pilote initial : 100 à 200 paires sur l'ensemble des sites.
- Au moins un exercice de panne et une restauration par site.

## 5. Mesures et indicateurs

| Indicateur | Définition | Cible indicative |
|---|---|---|
| Erreurs d'identité ou de latéralité | Cas détectés après libération | 0 |
| Complétude du DHR | Dossiers complets / paires libérées | 100 % |
| Disponibilité | Temps de fonctionnement des services | ≥ 99 % |
| Fonctionnement hors ligne | Pannes réseau gérées sans perte | 100 % |
| Délai de résolution des incidents | Temps médian | ≤ 24 h ouvrées |
| Temps de saisie opérateur | Minutes par paire pour le suivi | ≤ valeur de référence du site |
| Satisfaction des opérateurs | Questionnaire | ≥ 4/5 avec liste des irritants |
| Restauration | Test de restauration réussi dans le délai visé | oui, ≤ 4 h |
| Intention d'achat | Abonnement et prix acceptés | oui ou conditions précises |

## 6. Données collectées

Données techniques et d'usage : événements de jobs, erreurs, durées, incidents, temps de réponse, retours des opérateurs. Données de production pseudonymisées, stockées de façon sécurisée, durée de conservation définie. Les données servent à améliorer la plateforme et alimentent les autres projets (recettes, design, scanner) selon les accords.

## 7. Organisation

| Rôle | Responsabilité |
|---|---|
| Chef de projet pilote | Planning, relation sites, rapports |
| Ingénieur plateforme | Déploiement, corrections, supervision |
| Ingénieur sécurité | Revue d'accès, incidents, tests |
| Support terrain | Formation, assistance, diagnostic à distance |
| Référent informatique (par site) | Réseau, accès, sauvegardes locales |
| Responsable données / juridique | Accords, registre des traitements |

Support : intervention sous 24 à 48 h ; mise à jour au plus toutes les deux semaines avec retour arrière prévu ; réunion hebdomadaire de 30 min.

## 8. Planning indicatif (6 mois, de M9 à M14)

| Période | Contenu |
|---|---|
| Mois 0–1 (M9) | Configuration finale (accords de données, hébergement et test d'intrusion faits M6–M8) |
| Mois 1–2 (M10) | Installation, formation, mode shadow de 2 semaines |
| Mois 2–5 (M11–M13) | Production pilote, exercices de panne, ajustements |
| Mois 5–6 (M14) | Analyse, rapport, décision Go / réduction / arrêt de l'extension |

## 9. Budget indicatif

| Poste | Ordre de grandeur |
|---|---|
| Équipe (plateforme, sécurité, support) | à chiffrer selon allocation réelle |
| Hébergement et outils | à chiffrer |
| Test d'intrusion, conseil juridique et données | à chiffrer |
| Déplacements, formation | à chiffrer |

Les montants seront estimés après la phase 0.

## 10. Critères Go / No-Go

- **Go :** aucune erreur d'identité, DHR 100 % complet, disponibilité ≥ 99 %, restauration réussie, aucun incident de sécurité majeur, au moins un site prêt à souscrire.
- **Go conditionnel :** un indicateur manqué avec cause identifiée et plan de correction chiffré.
- **No-Go :** erreur d'identité non expliquée, perte de données, ou cadre de données non respecté.

## 11. Risques et parades

| Risque | Parade |
|---|---|
| Réseau instable sur site | Agent local, mode hors ligne testé |
| Résistance des opérateurs à la saisie | Interface simple, mode shadow, intégration aux postes |
| Incident de sécurité | RBAC, journal, procédure d'incident, assurance |
| Cadre de données non conforme | Décision juridique avant le pilote |
| Mise à jour défectueuse | Retour arrière testé, déploiement progressif |
| Charge de support sous-estimée | Mesure en pilote, rebudgétisation |

## 12. Points ouverts à décider

1. Hébergement et région.
2. Transferts de données vers la Chine et leur cadre.
3. Valeur légale du DHR numérique pour chaque site.
4. Contrepartie offerte aux sites.
