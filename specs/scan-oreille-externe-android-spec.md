# Spécification technique : scan de l'oreille externe par smartphone Android (Phase 1)

Version 0.1 (brouillon). Les valeurs chiffrées sont des cibles de départ à valider par les premiers essais.

**Décisions intégrées :** (1) solution développée en interne, sans API tierce (KIRI Engine, Polycam) ; (2) l'application mesure l'oreille **externe** (pavillon, conque, entrée du méat) ; le conduit reste mesuré par la sonde de `scanner-spec-prototype.md` ; (3) la précision visée est de l'ordre du millimètre, sans prétention métrologique.

## 1. Objectif et périmètre

**Objectif de la phase 1 (environ 12 semaines) :** démontrer qu'une application Android guide un utilisateur pour capturer l'oreille externe et que la chaîne de reconstruction produit un maillage à l'échelle réelle, avec un écart inférieur à 2 mm RMS sur fantômes.

**Rôle dans la chaîne :** forme extérieure et orientation de l'oreille, recalage éventuel avec le scan du conduit, pré-scan à bas coût.

**Inclus :** application de capture guidée, calcul de la reconstruction, export du maillage, banc de validation sur fantômes.
**Exclus (phases suivantes) :** conduit auditif, essais sur sujets humains, intégration à la CAO, réglementation, traitement entièrement embarqué.

## 2. Exigences de performance

| Réf. | Exigence | Cible phase 1 |
|---|---|---|
| E1 | Zone mesurée | Pavillon complet, conque, tragus, antitragus, entrée du méat |
| E2 | Justesse (écart maillage / référence, après alignement) | RMS ≤ 2 mm ; maximum ≤ 5 mm |
| E3 | Erreur d'échelle | ≤ 1 % sur les dimensions principales |
| E4 | Répétabilité (10 captures du même fantôme) | Écart type ≤ 1 mm |
| E5 | Durée de capture guidée | ≤ 60 s |
| E6 | Taux de captures exploitables au premier essai | ≥ 80 % |
| E7 | Sortie | Maillage étanche en mm, formats PLY et STL, repère standardisé |

## 3. Architecture

### 3.1 Application Android (Kotlin)

- Capture avec CameraX (ou ARCore pour récupérer les poses de la caméra en temps réel).
- Guidage à l'écran : couverture angulaire autour de l'oreille, netteté, exposition, vitesse de déplacement, alerte si les cheveux masquent le pavillon.
- Marqueur de référence imprimé (ArUco ou équivalent, côté connu) placé près de l'oreille pour fixer l'échelle.
- Enregistrement local des images, des poses et des métadonnées, puis envoi chiffré vers le backend.

### 3.2 Reconstruction

Deux voies à comparer sur les mêmes captures :

- **Voie A, photogrammétrie classique :** COLMAP et OpenMVS sur le backend. Segmentation de l'oreille pour masquer l'arrière-plan et les cheveux.
- **Voie B, modèle paramétrique d'oreille :** un modèle statistique ajusté sur les images par réseau de neurones. Plus robuste aux cheveux et aux zones cachées, mais produit une forme plausible et non mesurée : l'écart à la réalité est à quantifier.

Étapes communes : détection du marqueur, mise à l'échelle, nettoyage du maillage, fermeture, export.

### 3.3 Backend

Service de traitement hébergé par le projet. Le lieu d'hébergement et le cadre de données dépendent du point ouvert n° 3 de `DECISIONS.md` (les photos d'oreille sont des données biométriques).

## 4. Validation

- Fantômes d'oreille externe (silicone ou résine imprimée), 3 à 5 formes, avec référence mesurée par scanner de laboratoire.
- Mesures : RMS et maximum après alignement, erreur d'échelle, répétabilité, taux de réussite.
- Variables testées : éclairage, modèle de téléphone, présence de cheveux simulés, distance et vitesse de capture.
- Décision de passage : si E2 est tenu avec la voie A ou la voie B, on poursuit avec la meilleure ; sinon on revoit le périmètre avant la phase 2.

## 5. Risques

| Risque | Mitigation |
|---|---|
| Peau peu texturée, reconstruction bruitée | Éclairage uniforme, marqueurs ou motif temporaire, voie B |
| Cheveux et ombres | Segmentation, consigne de capture, voie B |
| Échelle incertaine | Marqueur de référence, poses ARCore |
| Variabilité des téléphones (optiques, stabilisation) | Liste de modèles de référence, étalonnage par modèle |
| Données biométriques | Chiffrement, durée de conservation courte, cadre de données fixé avant tout essai humain |

## 6. Livrables de la phase 1

1. Application Android de capture guidée (dossier `android/`).
2. Pipeline de reconstruction reproductible (voies A et B).
3. Banc de validation et rapport d'écarts sur fantômes.
4. Recommandation : voie retenue, précision réellement atteinte, périmètre de la phase 2.
