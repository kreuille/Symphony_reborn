# legokit — kit de briques LEGO-compatibles imprimables en 3D, à partir d'un modèle

Équivalent open-source minimaliste de Brickalike : modèle 3D → voxels → briques → fichiers d'impression + notice.
Python 3 + numpy, un seul fichier (`legokit.py`).

## Utilisation

```bash
python3 legokit.py mon_modele.stl --width 32 --out kit/      # STL ou OBJ, axe Z = haut
python3 legokit.py --shape sphere --width 20 --out demo/     # formes de test : sphere, cone, torus, pyramid
python3 legokit.py mon_modele.stl --width 32 --hollow        # coque épaisse de 2 briques (moins de pièces)
```

Options : `--width` (plots sur le plus grand côté), `--bed X Y` (plateau, défaut 220 220 mm),
`--tol` (jeu par côté : 0,1 mm FDM ; 0,05 mm résine), `--keep-floating`.

## Sorties (`--out`)

| Fichier | Contenu |
|---|---|
| `plateaux/plateau_NN.stl` | pièces rangées sur des plateaux d'impression, plots vers le haut, sans supports |
| `parts.csv` | liste de pièces et quantités |
| `notice.html` | notice couche par couche (couche précédente en gris) |
| `assemble_apercu.stl` | modèle assemblé pour visualiser le résultat |

## Pièces

Briques creuses 1x1 à 2x6 : plafond 1 mm, parois 1,5 mm, tubes sous les briques ≥ 2x2, pions sous les 1xN,
plots Ø4,8 × 1,8, pas 8 mm, hauteur 9,6 mm. Chaque pièce est une union de volumes fermés qui se chevauchent
(les trancheurs les fusionnent). Le jeu `--tol` est à calibrer : imprimez d'abord une 2x4 et testez-la sur une vraie brique.

## Principe

1. **Voxelisation** : un rayon vertical par colonne, remplissage par parité (le maillage doit être fermé).
2. **Découpage** : glouton, plus grande brique d'abord ; les couches impaires sont packées sur le plan transposé
   pour décaler les joints.
3. **Élagage** : les briques qui ne touchent le bloc principal que par une arête (marches d'escalier en diagonale)
   sont retirées, sinon le modèle ne tiendrait pas ensemble. Le nombre retiré est affiché.
4. **Plateaux** : rangement en étagères sur le plateau indiqué.

## Limites actuelles

Une seule couleur (pas d'attribution par texture), pas de plaques/pentes/tuiles, glouton non optimal
(pas de minimisation du nombre de pièces ni de la solidité). Pistes : couleurs via texture OBJ, pièces 1/3 hauteur
(plates) pour plus de résolution verticale, optimisation du découpage (ILP).
