# Plan pilote de la machine intégrée (imprimante) chez des clients

Version 0.1 (brouillon). Les chiffres sont des ordres de grandeur à ajuster avec les partenaires. Ce plan est **conditionnel** : il suppose que la gate M18 a décidé l'EVT, que la gate M24 a décidé le DVT et que les machines de pré-série issues du DVT respectent les exigences de sécurité. Calendrier : le mois 0 de ce pilote est **M26** dans le calendrier maître.

Le pilote de l'imprimante est mené **avec** celui du post-process (étape B) : les deux chantiers sont intégrés dans la même machine.

## 1. Objectifs

1. Vérifier en conditions réelles que la machine intégrée produit des pièces conformes (précision, rendement) avec des opérateurs non développeurs.
2. Mesurer la fiabilité, la maintenance, le temps de cycle complet et le coût réel.
3. Recueillir les exigences de service et de support pour la montée en cadence.
4. Mesurer l'intérêt commercial : prix accepté, nombre de machines envisagées.

## 2. Partenaires

- **Nombre :** 2 à 3 sites, de préférence ceux qui ont déjà participé au pilote G1.
- **Critères :** production d'au moins 20 à 30 paires par mois, opérateurs formés, local conforme (ventilation, alimentation), accord de partage des données.
- **Contrepartie :** machine prêtée ou tarif préférentiel, consommables offerts, formation, accès prioritaire à l'offre.

## 3. Cadre juridique et sécurité (à régler avant toute installation)

- **Conformité de la machine :** sécurité électrique, UV, IPA, parties mobiles, compatibilité électromagnétique. Le cadre applicable est à définir par des spécialistes et à vérifier avant d'installer une machine chez un tiers.
- **Fabricant légal et usage prévu :** décidés avec le pilote G1 (à confirmer auprès d'un consultant réglementaire).
- **Accord de pilote :** confidentialité, propriété intellectuelle, responsabilité, assurance, durée, conditions de reprise de la machine.
- **Données :** pseudonymisation, accès par rôle, hébergement et transferts conformes (voir le plan pilote cloud).
- **Formation et consignes :** opérateurs formés, consignes affichées, registre d'incidents.

## 4. Protocole du pilote

### 4.1 Déroulement par site

1. Installation de la machine, qualification locale (réception technique, mesures étalons).
2. Formation des opérateurs et de l'administrateur du site.
3. Production en parallèle du flux habituel pendant 2 semaines (mode shadow).
4. Production réelle limitée au domaine qualifié, avec support renforcé.
5. Exercices planifiés : panne, remplacement d'un consommable, mise à jour à distance, retour arrière.

### 4.2 Taille de l'échantillon

- 3 machines pendant 3 mois de production.
- Au moins 500 paires au total (hypothèse à ajuster selon les volumes des sites).

## 5. Mesures et indicateurs

| Indicateur | Définition | Cible indicative |
|---|---|---|
| Écart de forme | Pièce vs maillage cible (RMS) | ≤ 0,10 mm |
| Rendement du premier coup | Pièces libérées sans reprise / total | ≥ 90 % |
| Temps de cycle complet | De la mise en machine à la pièce libérée (p50 et p95) | À fixer d'après les mesures G1 |
| Disponibilité | Temps de fonctionnement | ≥ 95 % |
| Fiabilité | Cycles entre deux pannes | À fixer à partir des essais de fiabilité du DVT |
| Délai de résolution des pannes | Temps médian | ≤ 48 h ouvrées |
| Incidents de sécurité | Nombre et gravité | 0 incident grave |
| Coût réel par paire | Consommables, maintenance, amortissement | Inférieur au flux actuel du client |
| Écart entre coût réel et coût cible (BOM) | Mesure du coût de série | Documenté |
| Satisfaction des opérateurs | Questionnaire | ≥ 4/5 avec liste des irritants |
| Intention d'achat | Prix accepté, nombre de machines | Oui, ou conditions précises |

## 6. Données collectées

Pour chaque cycle : paramètres de la machine, capteurs, lot de résine, durées, alertes, résultats de contrôle, reprises avec cause, interventions de maintenance. Données transmises au cloud, versionnées et stockées de façon sécurisée.

## 7. Organisation

| Rôle | Responsabilité |
|---|---|
| Chef de projet pilote | Planning, relation avec les sites, rapports |
| Ingénieur imprimante | Support, corrections, analyse des défauts |
| Ingénieur post-process | Modules de lavage, séchage et cure |
| Ingénieur sécurité et qualité | Conformité, incidents, libération |
| Support terrain | Installation, formation, maintenance |
| Référent client (par site) | Opérations et retours |

Support : intervention sous 24 à 48 h, mises à jour à distance au plus toutes les deux semaines avec retour arrière prévu, réunion hebdomadaire de 30 min.

## 8. Planning indicatif (6 mois, de M26 à M31)

| Période | Contenu |
|---|---|
| Mois 0–1 (M26) | Accords, conformité de la machine, local, formation |
| Mois 1–2 (M27) | Installation, qualification locale, mode shadow |
| Mois 2–5 (M28–M30) | Production pilote, exercices de panne ; le bilan intermédiaire alimente la gate M30 |
| Mois 5–6 (M31) | Bilan final et décision de la montée en cadence |

## 9. Budget indicatif

| Poste | Ordre de grandeur |
|---|---|
| Machines de pré-série (3 exemplaires) | À chiffrer après les devis fournisseurs (gate M18) |
| Équipe pilote, support et maintenance | À chiffrer selon l'effectif retenu |
| Conformité, assurance, conseil | À chiffrer |
| Consommables, déplacements, formation | À chiffrer |

Aucun chiffre n'est avancé : ces coûts dépendent des devis fournisseurs et de l'effectif décidé.

## 10. Critères Go / No-Go de la montée en cadence

- **Go :** écart de forme ≤ 0,10 mm RMS, rendement ≥ 90 %, disponibilité ≥ 95 %, aucun incident de sécurité grave, coût réel proche de la cible, au moins un site prêt à acheter.
- **Go conditionnel :** un indicateur manqué avec cause identifiée et plan de correction chiffré.
- **No-Go :** incident de sécurité grave, fiabilité insuffisante sans amélioration plausible, ou coût très supérieur à l'objectif.

## 11. Risques et parades

| Risque | Parade |
|---|---|
| Machine non conforme aux exigences de sécurité | Vérification préalable par des spécialistes, aucune installation sans conformité |
| Pannes fréquentes | Essais de fiabilité au DVT, pièces de rechange, support rapide |
| Coût de série supérieur à la cible | Devis, révision du périmètre, décision de gate |
| Variabilité entre machines | Calibration en fin de ligne, suivi par numéro de série |
| Réseau instable | Mode local, synchronisation contrôlée |
| Opérateurs mal formés | Formation, consignes, support renforcé |

## 12. Points ouverts à décider

1. Sites et pays du pilote.
2. Cadre de conformité de la machine et organisme éventuel.
3. Contrepartie offerte aux sites.
4. Modèle de maintenance : par l'équipe, par un partenaire local.
