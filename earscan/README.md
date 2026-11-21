# earscan : pipeline serveur de reconstruction de l'oreille externe

Backend de l'application Android décrite dans `specs/scan-oreille-externe-android-spec.md` (voie A, photogrammétrie). Entrée : images de capture contenant un marqueur ArUco de côté connu. Sortie : maillage en millimètres (PLY et STL) et `report.json`.

## Étapes

1. **COLMAP** : extraction de points, appariement, reconstruction éparse (poses des caméras), puis densification et maillage de Poisson.
2. **Échelle** (`scale.py`) : détection du marqueur dans chaque image, triangulation de ses 4 coins avec les poses COLMAP, côté mesuré comparé au côté réel. Le calcul est refusé si le marqueur est vu dans moins de 2 images ou si les 4 côtés diffèrent de plus de 5 %.
3. **Nettoyage** : plus grande composante connexe, mise à l'échelle, export.
4. **Évaluation** (`evaluate.py`) : recalage rigide ICP sur un maillage de référence en mm, puis écart point-surface (RMS, moyenne, p95, maximum) et erreur d'échelle. Cela couvre les exigences E2 à E4 de la spécification.

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
- **Non traité** : segmentation de l'oreille (cheveux, fond), voie B (modèle paramétrique), précision réelle sur fantômes. La précision de 2 mm RMS visée par la spécification reste à mesurer.
