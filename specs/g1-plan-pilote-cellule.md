# Plan pilote de la cellule G1 chez des clients

Version 0.2 (brouillon). Les chiffres sont des ordres de grandeur à ajuster avec les partenaires. Calendrier : les mois ci-dessous sont relatifs ; dans le calendrier maître, le mois 0 de ce pilote correspond à **M9** (sélection des sites et cadrage réglementaire dès M3 ; finalisation des accords M9, installation et qualification locale M10, production M11–M13, bilan M14). Ce plan suppose que la phase 1 de la cellule (recettes validées en interne) est terminée avec un Go.

## 1. Objectifs

1. Vérifier en conditions réelles que la cellule produit des pièces utilisables par un fabricant ou un laboratoire.
2. Mesurer le temps complet Ear-to-Wear et le coût complet par paire par rapport au flux actuel du client.
3. Mesurer la charge opérateur, la fiabilité et les besoins de service.
4. Tester le modèle commercial : prix par paire, abonnement, consommables.

## 2. Partenaires

- **Nombre :** 2 à 3 sites : un fabricant de protections, un laboratoire d'embouts, éventuellement un audioprothésiste à volume.
- **Critères de choix :** au moins 20 à 30 paires par mois, techniciens CAD, processus documentés, accord pour partager les données de cycle, site accessible pour le support.
- **Contrepartie proposée :** matériel prêté ou tarif préférentiel, formation, consommables offerts pendant le pilote, accès prioritaire à l'offre commerciale.

## 3. Cadre juridique et réglementaire (à régler avant le premier produit remis)

- **Accord de pilote :** confidentialité, propriété intellectuelle (vous gardez les recettes et logiciels ; les données de production restent au client sous licence d'usage), responsabilité, durée.
- **Fabricant légal et usage prévu :** décider qui est le fabricant légal du produit fini, pour quels produits et quels pays. **À confirmer auprès d'un consultant réglementaire.**
- **Produits remis à des porteurs :** limiter le pilote au domaine qualifié ; ne pas présenter des coques destinées à recevoir de l'électronique comme des aides auditives finies.
- **Données :** pas de données personnelles inutiles ; pseudonymisation ; conformité locale (RGPD, loi chinoise si applicable).
- **Sécurité du site :** analyse de risques IPA et UV, formation, assurance responsabilité civile.

## 4. Protocole du pilote

### 4.1 Pour chaque commande

1. Commande créée avec Case ID, Pair ID, latéralité, produit, matériau.
2. Entrée du maillage (scan d'empreinte existant) ; contrôle d'identité.
3. Conception avec le CAD autorisé ; revue de l'opérateur.
4. Impression et post-traitement selon la recette qualifiée.
5. Contrôle qualité et décision de libération, avec dossier de lot (DHR).
6. Remise au client et retour d'usage.

**Comparaison de référence :** le délai et le taux de reprise habituels du client sur le même type de produit.

### 4.2 Taille de l'échantillon

- Pilote initial : 100 à 200 paires réparties entre les sites.
- Extension si résultats bons : 500 paires ou plus, avec ajout de produits.

## 5. Mesures et indicateurs

| Indicateur | Définition | Cible indicative |
|---|---|---|
| Temps Ear-to-Wear | Du début de la commande à la pièce libérée (p50 et p95) | À fixer avec le client : inférieur au flux actuel |
| Rendement du premier coup | Pièces libérées sans reprise / total | ≥ 90 % |
| Écart de forme | Pièce vs maillage cible (RMS) | ≤ 0,10 mm (budget d'erreur de la chaîne : 0,2 mm au total) |
| Taux de reprise client | Pièces refaites car mal ajustées | ≤ taux habituel du client |
| Temps opérateur | Minutes par paire | ≤ valeur de référence client |
| Complétude du DHR | Dossiers complets / paires | 100 % |
| Coût complet par paire | Consommables + main-d'œuvre + amortissement + service | Inférieur au prix actuel du client |
| Disponibilité de la cellule | Temps de fonctionnement | ≥ 95 % |
| Satisfaction opérateurs | Questionnaire | ≥ 4/5 avec liste des irritants |
| Intention d'achat | Prix accepté, nombre de cellules envisagées | oui ou conditions précises |

Les cibles sont à discuter avec les partenaires.

## 6. Données collectées

Pour chaque paire : identifiants, fichiers d'entrée et de design, recette, lot de résine, durées par étape, mesures QC, reprises avec cause, incidents, retours d'usage. Données versionnées, format ouvert, stockées de façon sécurisée.

## 7. Organisation

| Rôle | Responsabilité |
|---|---|
| Chef de projet pilote | Planning, relation client, rapports |
| Ingénieur process | Recettes, support technique, optimisation |
| Technicien de production (site) | Opération quotidienne |
| Référent client (par site) | Commandes, retours, accès aux données |
| Responsable qualité | Libération, non-conformités, dossier |
| Conseiller réglementaire (externe) | Fabricant légal, usage prévu |

Support : intervention sous 24 à 48 h, réunion hebdomadaire de 30 min avec chaque site.

## 8. Planning indicatif (6 mois, de M9 à M14)

| Période | Contenu |
|---|---|
| Mois 0–1 (M9) | Finalisation des accords et du cadre réglementaire (travaux lancés dès M3), analyse de risques site |
| Mois 1–2 (M10) | Installation, formation, qualification locale, répétition du support, réception technique |
| Mois 2–5 (M11–M13) | Production pilote, ajustements toutes les deux semaines |
| Mois 5–6 (M14) | Analyse, bilan, décision Go / réduction / arrêt de l'extension |

## 9. Budget indicatif

| Poste | Ordre de grandeur |
|---|---|
| Matériel et consommables | à chiffrer à partir du coût kit réel (voir phase 1) |
| Équipe pilote (ingénierie, support) | à chiffrer selon allocation réelle |
| Conseil réglementaire, assurance | à chiffrer |
| Déplacements, formation | à chiffrer |

Ce budget doit être calculé après la phase 0 ; aucun chiffre n'est avancé tant que le coût réel du kit n'est pas connu.

## 10. Critères Go / No-Go

- **Go :** rendement ≥ 90 %, reprises au plus égales à la référence client, coût complet inférieur au flux actuel, DHR complet, au moins un site prêt à acheter.
- **Go conditionnel :** un indicateur manqué avec cause identifiée et plan de correction chiffré.
- **No-Go :** coût ou qualité nettement moins bons que la référence sans amélioration plausible, ou refus des clients.

## 11. Risques et parades

| Risque | Parade |
|---|---|
| Site peu disponible | Référent désigné, contrepartie claire, réunions courtes |
| Panne de machine | Pièces de rechange, support rapide, procédure de reprise |
| Écart de qualité entre opérateurs | Formation commune, protocole standard |
| Produit hors domaine qualifié demandé | Périmètre écrit, refus documenté |
| Incident sécurité (IPA, UV) | Formation, consignes, ventilation, inspection |
| Délais réglementaires | Lancer le cadrage dès la phase 0 |

## 12. Points ouverts à décider

1. Sites et pays du pilote.
2. Fabricant légal et usage prévu.
3. Produits inclus dans le domaine qualifié.
4. Prix et contrepartie offerts.
5. Régime des données (propriété, durée).
