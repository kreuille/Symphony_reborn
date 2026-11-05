# Spécification technique : cellule de production G1 sur matériel existant (Phase 1)

Version 0.2 (brouillon). Les valeurs chiffrées sont des cibles de départ à valider par les premiers essais. Décision intégrée : l'impression se fait sur les machines à capsules SprintRay ; le temps de cycle capsule est à mesurer (essai T9) et sert de référence aux autres projets.

## 1. Objectif et périmètre

**Objectif de la phase 1 (environ 12 semaines) :** démontrer qu'un embout ou une protection auditive imprimé sur les machines et le post-traitement SprintRay existants, à partir d'un maillage de conduit, est dimensionnellement conforme, sûr à manipuler et reproductible.

**Inclus :** impression, lavage, séchage, cure, finition, contrôle qualité, recettes, matériaux rigide et souple, évaluation de la route silicone.
**Exclus (phases suivantes) :** scanner direct, CAO propriétaire, cloud complet, essais sur personnes, industrialisation, machine intégrée G3.

## 2. Exigences de performance

| Réf. | Exigence | Cible phase 1 |
|---|---|---|
| P1 | Domaine produit | Embouts et protections rigides ; route souple évaluée ; silicone décidé séparément |
| P2 | Écart pièce imprimée / maillage cible (après alignement) | RMS ≤ 0,10 mm (part « impression » du budget d'erreur de 0,2 mm, voir README) ; maximum ≤ 0,25 mm. Attention : la précision < 0,10 mm est celle annoncée pour le dentaire ; elle n'est pas démontrée sur des formes auriculaires |
| P3 | Rendement du premier coup (30 pièces consécutives) | ≥ 90 % de pièces conformes |
| P4 | Canaux et évents : écart de diamètre | ≤ 0,10 mm |
| P5 | Résidus de résine et état de surface | Aucun résidu visible ; rugosité acceptée par les techniciens |
| P6 | Temps de la pièce lancée à la pièce finie | À mesurer, objectif ≤ 60 min pour une paire |
| P7 | Matériau | Résine avec déclaration de biocompatibilité adaptée au contact conduit/peau, ou plan d'essais |
| P8 | Traçabilité | Chaque pièce rattachée à : Case ID, Pair ID, latéralité, lot, machine, recette |

## 3. Sécurité

- Analyse de risques écrite : UV, IPA (inflammable, ventilation, stockage), résine non polymérisée, pièces chaudes.
- Usage de la cellule limité aux opérateurs formés ; équipements de protection définis.
- Aucune pièce portée par une personne en phase 1.
- Pièces d'essai non remises à des tiers.

## 4. Architecture de la cellule

Imprimante et post-traitement existants + poste de contrôle + poste de travail avec CAD. Trois routes de matériaux évaluées indépendamment.

| Route | Procédé | Question à trancher |
|---|---|---|
| Rigide | Impression, lavage, séchage, cure, finition | Précision sur formes auriculaires, orientation, supports |
| Souple / semi-rigide | Idem, résine souple | Dureté après post-process, résidus, vieillissement |
| Silicone | Moule, dosage, mélange, réticulation | Cellule dédiée, partenaire, ou hors périmètre |

Paramètres à optimiser : orientation et supports, épaisseur de couche, temps de lavage, séchage, dose de cure, retrait de supports.

## 5. Validation

### 5.1 Références et échantillons

- 10 à 20 géométries réelles anonymisées (conduits variés, courbure en S, diamètres 5 à 12 mm).
- Calibres étalons imprimés (cylindres 6, 8, 10 mm, tube coudé).
- Mesure : scanner de laboratoire ou MMT sur la pièce imprimée, comparée au maillage cible.

### 5.2 Essais

| Essai | Description | Critère |
|---|---|---|
| T1 | Compatibilité équipement : la forme tient dans le volume, supports | Pièce imprimable sans défaut |
| T2 | Précision sur calibres | P4 |
| T3 | Précision sur géométries réelles | P2 |
| T4 | Répétabilité : 30 pièces consécutives | P3 |
| T5 | Lavage et séchage : résidus, canaux bouchés | P5 |
| T6 | Cure et propriétés mécaniques : dureté, flexion | Fiche matériau respectée |
| T7 | Vieillissement accéléré simple (chaleur, humidité, nettoyage) | Pas de déformation notable |
| T8 | Essais biocompatibilité ou vérification des attestations fournisseur | Dossier matériau complet |
| T9 | Mesure du temps complet et du temps opérateur | P6 |

## 6. Critères Go / No-Go de la phase 1

- **Go :** P2 (≤ 0,10 mm), P3, P4, P5 atteints sur la route rigide ; dossier matériau complet ; analyse de risques sécurité signée.
- **Go conditionnel :** un indicateur manqué avec cause identifiée et plan de correction chiffré (par exemple, un seul type de produit retenu). Pour P2, aucun dépassement de 0,10 mm RMS n'est toléré : toute marge perdue ici fait dépasser le budget de 0,2 mm de la chaîne. Si T2 et T3 montrent un écart supérieur sur formes auriculaires, le budget doit être renégocié (seuils scanner et design, ou limite totale) avant la gate M2.
- **No-Go :** précision ou rendement nettement insuffisants sans amélioration plausible, ou aucune résine utilisable en contact.

## 7. Livrables

1. Recettes qualifiées par route (paramètres, durées, doses).
2. Rapport de validation T1 à T9, données brutes.
3. Dossier matériaux (fiches, attestations, plan d'essais).
4. Coût réel du kit et du coût installé (avec et sans scanner).
5. Procédure de contrôle qualité et critères de libération.
6. Analyse de risques et consignes de sécurité.

## 8. Planning indicatif (12 semaines)

| Semaines | Contenu |
|---|---|
| 1–2 | Inventaire du matériel, choix des résines, préparation des échantillons et de la référence de mesure |
| 3–5 | T1 à T3 route rigide, premières recettes |
| 5–8 | T4 à T6, optimisation, route souple |
| 8–10 | T7, T8, évaluation silicone, mesure des temps |
| 10–11 | Chiffrage du kit installé, procédure QC |
| 12 | Rapport et décision Go / No-Go |

**Budget :** non chiffré à ce stade ; il dépendra du coût réel du kit et des allocations d'équipe.

## 9. Interface avec les autres projets

- Entrée : maillage STL/PLY étanche en mm, repère standard (voir spec scanner section 9 et spec logiciel).
- Sortie vers le cloud : paramètres de recette, lot, mesures QC, résultat de libération.

## 10. Risques et parades

| Risque | Parade |
|---|---|
| Machine conçue pour le dentaire, volumes ou précision inadaptés | Test T1 au plus tôt ; évaluer un autre équipement si nécessaire |
| Résidus dans les canaux fins | Recette de lavage dédiée, essais avec solvant et durée variables |
| Résine non qualifiée pour le contact | Choisir une résine avec dossier existant ; lancer essais en parallèle |
| Marché majoritairement silicone | Décision précoce sur la route silicone ; entretiens clients en phase 0 |
| Sécurité IPA et UV | Analyse de risques, ventilation, formation |

## 11. Points ouverts à décider

1. Résine et référence de mesure (scanner de laboratoire ou MMT, interne ou sous-traitance).
2. Produits retenus pour le pilote (embout, protection, avec filtre ou non).
3. Route silicone : cellule dédiée, partenaire ou hors périmètre.
4. Seuils de tolérance définitifs, à confirmer avec les clients.
