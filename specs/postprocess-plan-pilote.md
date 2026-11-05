# Plan pilote du post-process

Version 0.1 (brouillon). Les chiffres sont des ordres de grandeur à ajuster avec les partenaires. Le pilote du post-process se déroule en **deux étapes** : l'étape A avec les équipements existants, dans le pilote G1 ; l'étape B avec les modules intégrés, dans le pilote de la machine intégrée (conditionnel).

| Étape | Équipements | Mois 0 dans le calendrier maître | Période |
|---|---|---|---|
| A | Équipements SprintRay existants chez les sites G1 | M9 | M9 à M14 |
| B | Modules intégrés de la machine G3 | M26 | M26 à M31 |

## 1. Objectifs

1. Vérifier en conditions réelles que les recettes de lavage, séchage et cure sont tenues par des opérateurs du site : résidus, canaux ouverts, dose de cure, déformation.
2. Mesurer le temps par étape, la charge opérateur et les incidents de sécurité.
3. Étape B : vérifier la fiabilité, la sécurité et la maintenance des modules intégrés.
4. Recueillir les exigences de service (consommables, maintenance, solvant, UV).

## 2. Partenaires

- Étape A : les 2 à 3 sites du pilote G1 (voir le plan pilote de la cellule G1).
- Étape B : les sites du pilote de la machine intégrée (voir le plan pilote de l'imprimante).
- **Critères :** local ventilé, opérateurs formés, consignes de sécurité acceptées, accord de partage des données de cycle.

## 3. Cadre juridique et sécurité

- **Sécurité des sites :** analyse de risques IPA et UV signée, ventilation, stockage du solvant, consignes affichées, assurance.
- **Équipements intégrés (étape B) :** conformité de la machine vérifiée par des spécialistes avant installation.
- **Biocompatibilité :** attestations et essais après cure conformes à l'usage prévu, à confirmer avec le conseiller réglementaire avant de remettre des pièces à des porteurs.
- **Données :** pseudonymisation, accès par rôle, conformité locale (voir le plan pilote cloud).
- **Déchets :** gestion du solvant et de la résine usagés conforme aux règles locales.

## 4. Protocole du pilote

### 4.1 Pour chaque cycle

1. Pièce reçue de l'imprimante avec Pair ID et recette.
2. Lavage selon la recette ; relevé de la durée et du solvant utilisé.
3. Séchage jusqu'au critère de fin ; relevé de la durée.
4. Cure avec enregistrement de la dose, de la durée et de la température.
5. Finition (retrait des supports) et inspection : aspect, canaux ouverts, marquage.
6. Mesure dimensionnelle d'un échantillon de pièces (au minimum une pièce par lot) ; libération ou rejet avec cause.

### 4.2 Taille de l'échantillon

- Étape A : 100 à 200 paires avec relevé complet, dont 30 paires mesurées dimensionnellement.
- Étape B : au moins 500 paires sur 3 machines, avec les mesures de fiabilité des modules.

## 5. Mesures et indicateurs

| Indicateur | Définition | Cible indicative |
|---|---|---|
| Résidus | Pièces sans résidu visible / total | ≥ 98 % |
| Canaux ouverts | Pièces dont les canaux sont ouverts / total | 100 % |
| Variation dimensionnelle | Avant et après post-process (RMS) | ≤ 0,05 mm |
| Dose de cure tracée | Pièces avec dose enregistrée / total | 100 % |
| Rendement du premier coup | Pièces libérées sans reprise / total | ≥ 90 % |
| Temps par étape | Lavage, séchage, cure, finition (p50 et p95) | Inférieur au temps de référence du site |
| Temps opérateur | Minutes par paire | Inférieur à la référence du site |
| Incidents de sécurité | Nombre et gravité | 0 incident grave |
| Disponibilité des modules (étape B) | Temps de fonctionnement | ≥ 95 % |
| Consommation de solvant et de consommables | Par paire | Documentée |
| Satisfaction des opérateurs | Questionnaire | ≥ 4/5 avec liste des irritants |

## 6. Données collectées

Pour chaque pièce : recette, durées, solvant, dose et température de cure, résultats d'inspection, mesures dimensionnelles, reprises avec cause, incidents. Données versionnées et transmises au cloud (DHR).

## 7. Organisation

| Rôle | Responsabilité |
|---|---|
| Chef de projet pilote | Planning, relation avec les sites, rapports |
| Ingénieur process | Recettes, analyse des défauts, support |
| Ingénieur sécurité et qualité | Consignes, incidents, libération |
| Technicien de site | Opérations quotidiennes |
| Support terrain | Maintenance, consommables, formation |

Support : intervention sous 24 à 48 h ; réunion hebdomadaire de 30 min avec chaque site.

## 8. Planning indicatif

| Étape A (M9 à M14) | Contenu |
|---|---|
| M9 | Finalisation des consignes de sécurité et des recettes |
| M10 | Installation, formation, qualification locale |
| M11–M13 | Production pilote, relevé complet des cycles |
| M14 | Bilan et décision |

| Étape B (M26 à M31, conditionnelle) | Contenu |
|---|---|
| M26 | Conformité de la machine, local, formation |
| M27 | Installation, mode shadow |
| M28–M30 | Production pilote, exercices de panne |
| M31 | Bilan et décision de la montée en cadence |

## 9. Budget indicatif

| Poste | Ordre de grandeur |
|---|---|
| Étape A : mesures, consommables, support | À chiffrer après la phase 0 (inclus dans le budget du pilote G1) |
| Étape B : modules de pré-série | À chiffrer après les devis fournisseurs (gate M18) |
| Sécurité, conformité, assurance | À chiffrer |

Aucun chiffre n'est avancé tant que le coût réel du kit et les devis fournisseurs ne sont pas connus.

## 10. Critères Go / No-Go

- **Go :** résidus et canaux conformes, variation ≤ 0,05 mm, dose tracée à 100 %, rendement ≥ 90 %, aucun incident de sécurité grave, au moins un site prêt à poursuivre.
- **Go conditionnel :** un indicateur manqué avec cause identifiée et plan de correction chiffré.
- **No-Go :** incident de sécurité grave, déformation ou résidus incompatibles sans amélioration plausible, ou refus des sites.

## 11. Risques et parades

| Risque | Parade |
|---|---|
| Incident IPA ou UV | Formation, ventilation, consignes, interlocks, assurance |
| Résidus ou canaux bouchés | Recette dédiée, contrôle systématique |
| Dispersion entre opérateurs | Procédure standard, formation, plusieurs techniciens par site |
| Fuites ou consommation excessive de solvant | Suivi, maintenance préventive |
| Pannes des modules intégrés (étape B) | Pièces de rechange, support rapide, essais de fiabilité au DVT |
| Documentation de biocompatibilité incomplète | Dossier matériau complet avant toute remise à un porteur |

## 12. Points ouverts à décider

1. Sites et pays du pilote.
2. Méthodes de mesure des résidus et de fin de séchage.
3. Gestion et élimination des solvants et résines usagés.
4. Maintenance : par l'équipe ou par un partenaire local.
