# earscan : pipeline serveur de reconstruction de l'oreille externe

Backend de l'application Android décrite dans `specs/scan-oreille-externe-android-spec.md` (voie A, photogrammétrie). Entrée : images de capture contenant un marqueur ArUco de côté connu. Sortie : maillage en millimètres (PLY et STL) et `report.json`.

## Étapes

1. **COLMAP** : extraction de points, appariement, reconstruction éparse (poses des caméras), puis densification et maillage de Poisson.
2. **Échelle** (`scale.py`) : détection du marqueur dans chaque image, triangulation de ses 4 coins avec les poses COLMAP, côté mesuré comparé au côté réel. Le calcul est refusé si le marqueur est vu dans moins de 2 images ou si les 4 côtés diffèrent de plus de 5 %.
3. **Nettoyage** (`clean.py`, voir plus bas) : mise à l'échelle, retrait du plan de support et du fond, plus grande composante, lissage, fermeture, export.
4. **Évaluation** (`evaluate.py`) : recalage rigide ICP sur un maillage de référence en mm, puis écart point-surface (RMS, moyenne, p95, maximum) et erreur d'échelle. Cela couvre les exigences E2 à E4 de la spécification.

## Détourer l'oreille et nettoyer le maillage

Le maillage brut de COLMAP contient toute la scène (table, fond, support) et une peau un peu bruitée. Deux niveaux d'action, cumulables :

**1. Dans les photos (avant la reconstruction).** Poser l'oreille sur un **fond uni mat** (papier bleu ou vert, sans pli ni ombre) puis détourer :

```bash
python -m earscan masks captures/ --out masques/ --method background --marker-id 7   # contrôler masques/preview/
python -m earscan reconstruct captures/ --out sortie/ --marker-id 7 --marker-size-mm 20 --mask background
```

COLMAP n'extrait alors de points que sur l'oreille et le marqueur : moins de bruit, recalage plus propre. `--method grabcut` est peu fiable (voir le lot synthétique plus bas) : à éviter. **Toujours regarder les aperçus** avant de lancer.

**2. Sur le maillage (après la reconstruction).** Fait automatiquement par `reconstruct` (désactivable par `--no-crop`) :

1. coupe au-dessus du plan du marqueur (retire la table et le fond) ;
2. garde la plus grande composante (retire les îlots et débris) ;
3. option `--roi-radius-mm 60` : ne garde que le disque de ce rayon autour du marqueur ;
4. lissage de Taubin (`--smooth 10`, 0 pour désactiver), qui enlève le bruit sans rétrécir l'objet ;
5. fermeture du contour de coupe pour obtenir un maillage étanche.

Pour retravailler un maillage déjà reconstruit, sans relancer COLMAP :

```bash
python -m earscan clean sortie/scene_mm.ply --report sortie/report.json --out sortie/ear_clean.ply --roi-radius-mm 60
python -m earscan clean ancien.ply --out propre.ply      # sans report : plan dominant cherché automatiquement
```

`scene_mm.ply` est le maillage brut mis à l'échelle ; `ear_mm.ply` est le résultat nettoyé. Pour une surface plus nette dès COLMAP, augmenter `--poisson-trim` (par exemple 9 à 10) retire davantage de surface extrapolée par le maillage de Poisson.

La surface reste limitée par les photos : plus de recouvrement, une mise au point nette et un éclairage uniforme améliorent le résultat bien plus que le lissage.

## Lot d'images synthétiques (avec cheveux)

`earscan/synth.py` génère des photos simulées d'une oreille stylisée, avec cheveux, marqueur ArUco, fond bleu uni, ombrage, bruit et poses de caméra connues. Il sert à tester le détourage et l'échelle en connaissant la bonne réponse. Un exemple de 24 vues (cheveux moyens) est dans `earscan/exemples/oreille_cheveux_medium/` (aperçu : `apercu.jpg`).

```bash
python -m earscan.synth --out synth/ --views 48 --hair medium --seed 1      # none | light | medium | heavy
python -m earscan masks synth/images --out synth/masques --method background --marker-id 7
```

Contenu : `images/` (photos), `truth/ear_silhouette|ear_visible|hair/` (masques de vérité), `model/` (poses exactes au format COLMAP, en mm x `--model-unit`, donc échelle à retrouver = 1/`--model-unit`), `reference_ear_mm.ply` (surface de référence étanche en mm), `params.json`.

Résultats mesurés sur ce lot (8 vues, 960x720) :

| Cheveux | Détourage `background`, IoU avec l'oreille visible | Cheveux restés dans le masque |
|---|---|---|
| aucun | 0,99 | 0 % |
| légers | 0,50 | 99 % |
| moyens | 0,32 | 99 % |
| épais | 0,22 | 100 % |

- L'échelle par marqueur est retrouvée à 0,2 % près (10,02 pour 10,00 attendu), avec 8 vues du marqueur sur 8.
- **Le détourage par fond uni ne retire pas les cheveux** : ils diffèrent du fond, donc ils sont gardés. Un essai de séparation par couleur de peau a échoué (77 à 85 % des cheveux conservés, oreille dégradée), il n'a pas été gardé. GrabCut est inutilisable ici (IoU d'environ 0,2).
- Pour de vraies photos avec cheveux : dégager l'oreille (cheveux attachés ou plaqués), ou un modèle de segmentation appris, non traité.
- Limites du lot : forme d'oreille stylisée, cheveux en traits de couleur unie, éclairage simple. La reconstruction COLMAP complète n'a pas été lancée sur ce lot.

## Utilisation

```bash
pip install -r earscan/requirements.txt          # depuis la racine du dépôt

# Reconstruction (COLMAP requis ; la densification demande CUDA)
python -m earscan reconstruct captures/ --out sortie/ --marker-id 7 --marker-size-mm 20
python -m earscan reconstruct captures/ --out sortie/ --marker-id 7 --marker-size-mm 20 --sparse-only --cpu

# Écart à une référence (maillage de référence en mm ; --trim 0.9 pour un scan partiel)
python -m earscan evaluate sortie/ear_mm.ply reference.stl

python -m pytest earscan -q                      # tests
```

Le marqueur se génère avec `python -m earscan.make_marker --id 7 --size-mm 20 --out marqueur.svg` (exemple prêt à imprimer : `marker_7_20mm.svg`) ; le protocole de capture est dans `PROTOCOLE_CAPTURE.md`.

Le marqueur (dictionnaire `DICT_4X4_50` par défaut) s'imprime à une taille connue ; `--marker-size-mm` est le côté du carré noir. Le placer à côté de l'oreille, dans le même plan que la zone à mesurer, bien à plat.

## État de la validation

- **Testé** : lecture du modèle COLMAP, détection du marqueur et échelle (images synthétiques à échelle connue, écart inférieur à 1 %), évaluation (mouvement rigide, bruit, erreur d'échelle), nettoyage du maillage, ordre des commandes.
- **Non testé** : l'exécution de COLMAP lui-même, absent de l'environnement de développement. Les commandes sont dans `pipeline.build_commands`. Les options `--cpu` (`SiftExtraction.use_gpu`, `SiftMatching.use_gpu`) sont celles de COLMAP ≤ 3.11 et ont été renommées ensuite : à vérifier selon la version installée.
- **Testé aussi** : retrait du plan et du fond, composantes, fermeture, lissage (scènes synthétiques), détourage par fond uni et GrabCut (images synthétiques), masques au format COLMAP. Sur de vraies photos, le détourage et le nettoyage restent à juger à l'œil.
- **Non traité** : détourage par modèle appris (cheveux sur sujet réel), voie B (modèle paramétrique), précision réelle sur fantômes. La précision de 2 mm RMS visée par la spécification reste à mesurer.
