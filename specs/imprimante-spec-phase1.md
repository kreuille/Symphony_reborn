# Spécification technique : imprimante (Phase 1 : qualification de la machine existante et exigences G3)

Version 0.1 (brouillon). Les valeurs chiffrées sont des cibles de départ à valider par les premiers essais. Décisions intégrées : l'impression se fait sur machines à capsules SprintRay ; budget d'erreur total de la chaîne de 0,2 mm RMS, dont 0,10 mm pour l'impression ; la précision inférieure à 0,10 mm est celle annoncée pour le dentaire, non démontrée sur formes auriculaires.

## 1. Objectif et périmètre

**Objectif de la phase 1 (12 semaines, M0 à M2) :**

1. Mesurer ce que la machine à capsules existante sait faire sur des formes auriculaires : précision, volume utile, canaux fins, répétabilité, temps d'impression.
2. En déduire les exigences chiffrées de l'imprimante intégrée G3 (version 1, gel à M5).
3. Instruire la décision « réutiliser une plateforme SprintRay » ou « concevoir un moteur dédié », à trancher à la gate M5.

**Inclus :** essais d'impression, plan d'expériences sur l'orientation et les supports, mesures, exigences G3, revue des plateformes réutilisables, plan des preuves de sous-ensembles (M6 à M11).
**Exclus :** conception détaillée de la machine, prototypes matériels (EVT), post-processing (voir spécification post-process), essais sur personnes.

## 2. Exigences de performance

| Réf. | Exigence | Cible de départ |
|---|---|---|
| I1 | Capacité : paire (droite et gauche) imprimée en un cycle | Enveloppe du corpus de 50 géométries plus 20 % de marge (à mesurer) |
| I2 | Précision : écart pièce / maillage cible (après alignement) | RMS ≤ 0,10 mm ; maximum ≤ 0,25 mm |
| I3 | Canaux fins : écart de diamètre d'un canal ouvert | ≤ 0,10 mm ; diamètre minimal fiable à déterminer |
| I4 | Rendement du premier coup (30 pièces consécutives) | ≥ 90 % |
| I5 | Répétabilité entre plateaux et positions sur le plateau | Écart type ≤ 0,05 mm |
| I6 | Temps d'impression d'une paire | À mesurer ; objectif fixé après la mesure |
| I7 | Traçabilité : lot de résine ou de capsule, machine, recette, rattachés au Pair ID | 100 % |
| I8 | Interfaces : réception du fichier machine du CAM, état et télémétrie vers le cloud | Droits d'accès à confirmer (API, format de fichier) |

## 3. Sécurité

- Résine non polymérisée, UV, pièces mobiles et surfaces chaudes : analyse de risques écrite avant les essais.
- Opérateurs formés, équipements de protection définis.
- Aucune pièce portée par une personne en phase 1.
- Pour la machine intégrée : le cadre de sécurité des machines (électrique, UV, parties mobiles) est à cadrer par des spécialistes avant l'EVT.

## 4. Architecture de référence de l'imprimante intégrée (G3)

Sous-systèmes à instruire ; les choix make, buy ou partner sont provisoires et seront décidés à la gate M18.

| Sous-système | Fonction | Orientation provisoire |
|---|---|---|
| Source lumineuse et optique | Projection de la couche, uniformité, résolution | À instruire (réutilisation ou achat) |
| Plateforme et axe vertical | Positionnement, planéité, asservissement | À instruire |
| Interface capsule ou cuve et résine | Alimentation, étanchéité, identification du lot | Réutilisation SprintRay à étudier |
| Gestion thermique | Stabilité de température de la résine et du moteur | À instruire |
| Électronique et firmware | Pilotage, capteurs, sécurité, communication | Développement interne ou partenaire |
| Interface de transfert | Passage de la pièce vers le post-process | À concevoir avec le post-process |
| Sécurité | Capots, interlocks, détection | À concevoir |

## 5. Validation

### 5.1 Références et échantillons

- Corpus de 50 géométries auriculaires anonymisées, avec courbures en S et diamètres de 5 à 12 mm.
- Calibres étalons imprimés (cylindres de 6, 8 et 10 mm, tube coudé, canaux de diamètres décroissants).
- Référence de mesure : scanner de laboratoire ou machine à mesurer tridimensionnelle sur les pièces imprimées, comparées au maillage cible.

### 5.2 Essais

| Essai | Description | Critère |
|---|---|---|
| T1 | Capacité : volume utile et positions sur le plateau | I1 |
| T2 | Précision sur calibres étalons | I2 |
| T3 | Précision sur géométries réelles (RMS, 95e centile, maximum, cartographie) | I2 |
| T4 | Canaux fins : diamètres décroissants, ouverture, écart | I3 |
| T5 | Plan d'expériences : orientation, supports, épaisseur de couche contre précision et rendement | Réglage optimal documenté |
| T6 | Répétabilité : 30 pièces consécutives, plusieurs plateaux | I4, I5 |
| T7 | Compatibilité de résines (rigide, souple) : propriétés mesurées avec les équipements de post-process existants | Fiche matériau respectée |
| T8 | Temps d'impression d'une paire, temps d'attente et de préparation | I6 |

## 6. Critères Go / No-Go de la phase 1

- **Go :** I2 (≤ 0,10 mm RMS sur formes auriculaires), I3, I4 et I5 atteints ; exigences G3 V1 documentées ; analyse de risques signée.
- **Go conditionnel :** RMS entre 0,10 et 0,15 mm avec cause identifiée et corrigeable ; le budget d'erreur de la chaîne doit alors être renégocié (seuils scanner et design, ou limite totale) avant la gate M2.
- **No-Go :** RMS supérieur à 0,15 mm sans amélioration plausible : rechercher un autre équipement pour G1 et réexaminer l'ambition G3.

## 7. Livrables

1. Rapport de validation T1 à T8 et données brutes.
2. Réglages d'orientation et de supports qualifiés par produit.
3. Exigences G3 de l'imprimante, version 1 (gel à M5).
4. Revue des plateformes SprintRay réutilisables et recommandation.
5. Plan des preuves de sous-ensembles (M6 à M11) avec cibles et bancs d'essai.
6. Analyse de risques et consignes de sécurité.

## 8. Planning indicatif (12 semaines, puis jusqu'à M5)

| Semaines | Contenu |
|---|---|
| 1–2 | Inventaire des machines, choix des résines, préparation du corpus et de la référence de mesure |
| 3–5 | T1 à T3 : **première mesure de précision sur formes auriculaires** |
| 5–8 | T4 à T6 : canaux, plan d'expériences, répétabilité |
| 8–10 | T7 et T8 : résines et temps |
| 10–12 | Rapport, exigences G3 V1, décision Go / No-Go |
| M3–M5 | Gel des exigences G3 ; revue des plateformes ; plan des preuves de sous-ensembles |

## 9. Preuves de sous-ensembles (M6 à M11)

| Sous-système | Preuve attendue sur banc | Décision |
|---|---|---|
| Source lumineuse et optique | Uniformité et résolution tenant la cible I2 | Poursuivre, remplacer ou abandonner |
| Plateforme et axe vertical | Planéité et répétabilité tenant I5 | Idem |
| Interface capsule ou cuve | Étanchéité, identification de lot, absence de contamination | Idem |
| Gestion thermique | Stabilité de température sur un cycle complet | Idem |
| Électronique et firmware | Pilotage des capteurs, arrêt de sécurité, communication avec le cloud | Idem |
| Interface de transfert | Transfert répétable vers le post-process | Idem |

Cibles chiffrées de chaque banc : à fixer avec les exigences G3 à M5.

## 10. Risques et parades

| Risque | Parade |
|---|---|
| Précision insuffisante sur formes auriculaires | Mesure dès la semaine 5 ; renégociation du budget d'erreur ; autre équipement |
| Canaux fins bouchés ou déformés | Réglages de supports, orientation, plan d'expériences |
| Accès limité aux paramètres et au format de fichier de la machine existante | Accord interne SprintRay dès la phase 0 |
| Plateforme réutilisable inadaptée à la paire auriculaire | Conception dédiée de repli, coût plus élevé |
| Coût de la machine supérieur à l'objectif de 2 000 USD | Devis fournisseurs avant la gate M18, décision de périmètre |
| Résines non qualifiées pour le contact | Choisir une résine avec dossier existant, essais en parallèle |

## 11. Points ouverts à décider

1. Accès aux plateformes, plans et paramètres des machines SprintRay existantes.
2. Référence de mesure : interne ou sous-traitance.
3. Résines pour les essais, avec le chantier post-process.
4. Seuils définitifs de précision et de rendement, à confirmer avec les clients.
5. Décision de réutilisation ou de conception dédiée, à la gate M5.
