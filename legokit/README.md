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

## Numéro de set → liste de pièces par couleur (`legoset.py`)

```bash
python3 legoset.py 10698 --out set_10698/
```

Télécharge une fois les CSV publics de Rebrickable (cache `~/.cache/legokit/rebrickable`, ou `--cache`, ou `LEGOKIT_CACHE`),
puis écrit `pieces_par_couleur.csv` (couleur, code RVB, pièce, quantité, `imprimable` oui/non) et affiche le détail par couleur.
Sont marquées imprimables les pièces nommées exactement « Brick / Plate / Tile N x M » (jusqu'à 12), que `legokit.brick_mesh` sait générer.
Exemples : set 10698 → 790 pièces, 33 couleurs, 51 % générables ; set 11011 → 1500 pièces, 39 couleurs, 47 %.
Pas encore fait : STL/3MF par couleur, pièces spéciales (pentes, arches, figurines), sous-ensembles et figurines de l'inventaire.

## Numéro de set → STL et 3MF par couleur (`legoprint.py`)

```bash
python3 legoprint.py 10698 --out kit_10698/                 # plateau 256x256 (X1, P1, A1)
python3 legoprint.py 10698 --bed 180 180 --colors "Red,Black"   # A1 mini, seulement certaines couleurs
```

Pour chaque couleur : `kit_10698/<Couleur>/<Couleur>_NN.3mf` et `.stl`, un fichier par plateau d'impression (pièces rangées dans le plateau,
marge 5 mm, écart 3 mm, plots vers le haut, sans supports), plus `resume.csv`. Le 3MF contient un objet par type de pièce et la couleur Rebrickable
(`basematerials`) ; le STL contient le même plateau sans couleur.
Dimensions : brique 9,6 mm, plaque et tuile 3,2 mm (+ plots 1,8 mm), jeu `--tol` 0,1 mm par côté.
Exemple : set 10698 → 424 pièces sur 29 plateaux (une trentaine de couleurs), 366 pièces non gérées.

Les 3MF sont relus et vérifiés par `test_legoprint.py` (XML, dimensions, pièces dans le plateau, sans chevauchement),
mais pas encore ouverts dans Bambu Studio : la couleur du filament est à choisir dans le trancheur si elle n'est pas reprise.
