# Spécification technique : post-process (Phase 1 : qualification des équipements existants et exigences G3)

Version 0.1 (brouillon). Les valeurs chiffrées sont des cibles de départ à valider par les premiers essais. Le post-process regroupe le lavage, le séchage, la cure, la finition, le transfert et le contrôle.

## 1. Objectif et périmètre

**Objectif de la phase 1 (12 semaines, M0 à M2) :**

1. Qualifier les équipements existants de lavage, séchage et cure pour des pièces auriculaires : résidus, canaux ouverts, déformation, propriétés après cure.
2. Établir les recettes de G1 pour les routes rigide et souple, et évaluer la route silicone séparément.
3. Poser l'analyse de risques (IPA inflammable, UV) et les exigences G3 des modules intégrés.

**Inclus :** recettes, mesures, analyse de risques, contrôle qualité et critères de libération, exigences des modules G3, plan des preuves de sous-ensembles (M6 à M11).
**Exclus :** conception détaillée des modules, prototypes (EVT), essais sur personnes. Le vrai silicone (moule, dosage, réticulation) est évalué séparément : il ne s'agit pas d'un post-traitement de résine.

## 2. Exigences de performance

| Réf. | Exigence | Cible de départ |
|---|---|---|
| Q1 | Résidus de résine sur la pièce et dans les canaux | Aucun résidu visible ; méthode de mesure à définir avec la qualité |
| Q2 | Canaux fins ouverts et traversables | 100 % |
| Q3 | Variation dimensionnelle due au post-process (sortie d'impression vs pièce finie) | ≤ 0,05 mm RMS, à valider par T5 |
| Q4 | Dose de cure mesurée et tracée par pièce (énergie, durée, température) | 100 % des pièces |
| Q5 | Propriétés après cure (dureté, flexibilité) | Fiche matériau respectée |
| Q6 | Fin de séchage vérifiée | Critère mesurable à définir (par exemple masse stable) |
| Q7 | Sécurité IPA et UV | Analyse de risques signée, consignes affichées |
| Q8 | Rendement du premier coup | ≥ 90 % sur 30 pièces |
| Q9 | Traçabilité : recette, durées, dose, opérateur, rattachés au Pair ID | 100 % |
| Q10 | Écart pièce finale vs maillage cible (impression et post-process) | ≤ 0,10 mm RMS, cohérent avec le budget d'erreur de la chaîne |

## 3. Sécurité

- **IPA :** liquide inflammable (point éclair et limites d'inflammabilité publiés par NIOSH). Ventilation, stockage conforme, quantité limitée, absence de source d'inflammation, plan en cas de fuite ou d'incendie.
- **UV :** protection des yeux et de la peau, capots, arrêt à l'ouverture.
- **Résine :** gants, manipulation, déchets.
- Analyse de risques signée avant les essais.
- Pour les modules intégrés G3 : interlocks UV et IPA, ventilation et détection, à concevoir et à faire valider par des spécialistes.

## 4. Architecture

| Fonction | G1 : équipement existant | G3 : module intégré |
|---|---|---|
| Lavage | Équipement de lavage SprintRay, recette qualifiée | Module fluidique : circuit, filtration, gestion du solvant |
| Séchage | Séchage existant ou manuel guidé | Module de séchage : flux, durée, détection de fin |
| Cure | Équipement de cure existant, recette | Module de cure : dose UV, température, uniformité |
| Finition | Manuelle guidée | Retrait des supports et finition, automatisation partielle à évaluer |
| Transfert | Manuel entre équipements | Mécanisme de transfert entre modules |
| Contrôle | Inspection et mesures manuelles | Contrôle intégré : mesure, aspect, marquage |
| Sécurité | Consignes et ventilation | Interlocks, détection, capots |

## 5. Validation

### 5.1 Références et échantillons

- Pièces imprimées issues du corpus de l'imprimante (géométries auriculaires, calibres, canaux fins).
- Résines : rigide et souple retenues avec le chantier imprimante.
- Références de mesure : scanner de laboratoire ou machine de mesure, duromètre, balance, inspection optique.

### 5.2 Essais

| Essai | Description | Critère |
|---|---|---|
| T1 | Analyse de risques et inventaire des équipements, consignes | Q7 |
| T2 | Lavage : durée, solvant, agitation ; résidus et canaux | Q1, Q2 |
| T3 | Séchage : durée et critère de fin | Q6 |
| T4 | Cure : dose, température ; propriétés mécaniques | Q4, Q5 |
| T5 | Variation dimensionnelle avant et après post-process | Q3, Q10 |
| T6 | Répétabilité : 30 pièces consécutives | Q8 |
| T7 | Vieillissement et nettoyage simple (chaleur, humidité, désinfection) | Pas de déformation notable |
| T8 | Biocompatibilité : attestations du fournisseur, plan d'essais après cure | Dossier complet, plan arrêté |
| T9 | Temps par étape et temps opérateur | Cycle de référence pour les autres projets |

## 6. Critères Go / No-Go de la phase 1

- **Go :** Q1 à Q5, Q7, Q8 et Q10 atteints sur la route rigide ; dossier matériau complet ; analyse de risques signée.
- **Go conditionnel :** un indicateur manqué avec cause identifiée et plan de correction chiffré (par exemple, un seul type de produit retenu).
- **No-Go :** résidus ou déformation incompatibles, sans amélioration plausible, ou absence de résine utilisable en contact.

## 7. Livrables

1. Recettes qualifiées par route (durées, solvant, doses).
2. Rapport de validation T1 à T9 et données brutes.
3. Dossier matériaux et plan de biocompatibilité.
4. Analyse de risques, consignes et procédure en cas d'incident.
5. Procédure de contrôle qualité et critères de libération.
6. Exigences G3 des modules, version 1 (gel à M5) et plan des preuves de sous-ensembles.

## 8. Planning indicatif (12 semaines, puis jusqu'à M8)

| Semaines | Contenu |
|---|---|
| 1–2 | Inventaire, analyse de risques, choix des résines, préparation des échantillons |
| 3–5 | T2 et T3 : lavage et séchage |
| 5–8 | T4 et T5 : cure et variation dimensionnelle |
| 8–10 | T6 à T9 : répétabilité, vieillissement, biocompatibilité, temps |
| 10–12 | Rapport, exigences G3, décision Go / No-Go |
| M3–M8 | Recettes de G1 stabilisées, route souple, décision silicone à M8 |

## 9. Preuves de sous-ensembles (M6 à M11)

| Module | Preuve attendue sur banc | Décision |
|---|---|---|
| Lavage fluidique | Résidus et canaux conformes, gestion du solvant, filtration | Poursuivre, remplacer ou abandonner |
| Séchage | Détection de fin de séchage, durée stable | Idem |
| Cure | Dose et température mesurées, uniformité, propriétés conformes | Idem |
| Transfert | Transfert répétable sans endommager la pièce | Idem |
| Interlocks et sécurité | Arrêt à l'ouverture, détection, ventilation conformes à l'analyse de risques | Idem |
| Contrôle intégré | Corrélation avec la mesure de référence | Idem |

Cibles chiffrées de chaque banc : à fixer avec les exigences G3 à M5.

## 10. Risques et parades

| Risque | Parade |
|---|---|
| Résidus dans les canaux fins | Recette de lavage dédiée, essais de durée et d'agitation |
| Déformation à la cure | Réglage de la dose, de la température et du support, plan d'expériences |
| Incident de sécurité (IPA, UV) | Analyse de risques, ventilation, interlocks, formation |
| Résine non qualifiée pour le contact | Choisir une résine avec dossier existant, plan de biocompatibilité en parallèle |
| Route silicone confondue avec une résine | Évaluation séparée, cellule dédiée ou partenaire |
| Modules G3 trop coûteux | Devis avant la gate M18, décision de périmètre |

## 11. Points ouverts à décider

1. Résines et fournisseurs.
2. Méthodes de mesure des résidus et de fin de séchage.
3. Route silicone : cellule dédiée, partenaire ou hors périmètre.
4. Exigences de biocompatibilité selon l'usage prévu (à confirmer avec le conseiller réglementaire).
5. Cadre de sécurité des modules intégrés.
