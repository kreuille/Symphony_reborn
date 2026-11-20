# legokit — kit de briques LEGO-compatibles imprimables en 3D, à partir d'un modèle

**Application web :** `python3 legoweb.py` puis http://127.0.0.1:8000 — voir [Application web](#application-web-legowebpy).

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
Sont marquées « imprimable » les pièces nommées exactement « Brick / Plate / Tile N x M » (jusqu'à 12), générées en paramétrique ; `legoprint.py` couvre le reste via LDraw.
Exemples : set 10698 → 790 pièces, 33 couleurs, 51 % générables ; set 11011 → 1500 pièces, 39 couleurs, 47 %.
Les figurines complètes et sous-ensembles de l'inventaire Rebrickable ne sont pas inclus.

## Numéro de set → STL et 3MF par couleur (`legoprint.py`)

```bash
python3 legoprint.py 40468 --out kit_40468/                      # plateau 256x256 (X1, P1, A1)
python3 legoprint.py 10698 --bed 180 180 --colors "Red,Black"    # A1 mini, seulement certaines couleurs
python3 legoprint.py 10698 --no-ldraw                            # briques/plaques/tuiles paramétriques seulement (rapide, sans LDraw)
```

Couvre **tout le set**, par deux voies :
- **Briques, plaques, tuiles N x M** (« Brick/Plate/Tile N x M ») : formes paramétriques de `legokit.py`, creuses, tubes et plots calibrés pour l'impression.
- **Toutes les autres pièces** (pentes, supports, jantes, pneus, fenêtres, minifigs...) : géométrie de la bibliothèque LDraw (`legopart.py`) :
  faces orientées vers l'extérieur (BFC), conversion LDU → mm, **plots vers le haut** sauf si l'appui est quasi nul (un pneu se couche),
  retrait de 0,2 mm du pied des pièces qui s'emboîtent. Les références Rebrickable sont reliées aux fichiers LDraw (variantes, impressions).
  Seuls les autocollants et le papier ne sont pas imprimés ; ils sont listés dans `non_generees.csv` avec la raison.

Pour chaque couleur : `kit/<Couleur>/<Couleur>_NN.3mf` et `.stl`, un fichier par plateau (marge 5 mm, écart 3 mm), plus `resume.csv`.
Le 3MF contient un objet par type de pièce et la couleur Rebrickable (`basematerials`) ; le STL contient le même plateau sans couleur.
La bibliothèque LDraw (~150 Mo) est téléchargée une fois dans le cache (`--ldraw complete.zip` pour en indiquer une locale).

Résultats : 10698 → 790/790 pièces sur 33 plateaux ; 11011 → 1 500/1 500 sur 39 ; 40468 (Yellow Taxi) → 123/124 sur 9 (planche d'autocollants exclue).

**Images des plateaux :** `--preview` (ou `python3 legopreview.py kit_40468/`) écrit dans `apercus/` une image PNG par plateau (pièces en couleur, vue de dessus inclinée,
plateau dessiné dessous) et `apercu_plateaux.png`, planche d'ensemble de tous les plateaux. Rendu WebGL dans Chrome/Chromium/Edge sans interface (variable `CHROME`).

**À savoir avant d'imprimer les pièces LDraw :**
- La géométrie LDraw est fidèle à la forme extérieure, pas optimisée pour l'impression : 3 à 13 % d'arêtes non appariées (jonctions en T) que les trancheurs réparent à l'import, pas de supports ajoutés (pentes inversées, arches, supports : à supporter dans le trancheur).
- Le jeu d'emboîtement des pièces spéciales est celui de LDraw moins 0,2 mm sur l'emprise ; à calibrer sur un premier essai (même démarche que la 2x4).
- Les pneus sont en caoutchouc : les imprimer en TPU, ou accepter une pièce rigide. Les 3MF et STL n'ont pas été ouverts dans Bambu Studio.

## Notice de montage LDraw (`legonotice.py`)

```bash
python3 legonotice.py --set 1069-1 --out notice.html                       # modèle officiel du dépôt OMR LDraw
python3 legonotice.py --model mon_modele.mpd --out notice.html             # votre propre fichier .mpd / .ldr
python3 legonotice.py --model m.mpd --ldraw complete.zip --title "Mon set" # bibliothèque LDraw déjà téléchargée
```

Produit un fichier HTML **autonome** (aucune dépendance, fonctionne hors ligne, WebGL2) : une étape à la fois, flèches gauche/droite,
souris pour tourner, molette pour zoomer, pièces de l'étape listées avec couleur, quantité, référence et nom. Les pièces de l'étape sont en couleur, les
précédentes atténuées (case à décocher). Les pièces que `legoprint.py` sait imprimer sont marquées **imprimable**.

- **Sources :** le modèle vient de l'OMR (`--set`, ~1 470 sets) ou d'un fichier ; les formes viennent de la bibliothèque LDraw
  (`complete.zip`, ~150 Mo, téléchargée une fois dans `~/.cache/legokit/`). Hôtes à autoriser : `library.ldraw.org`, `www.ldraw.org`.
- **Étapes :** celles du fichier (`0 STEP`). Les sous-modèles passent avant l'étape qui les pose ; un sous-modèle sans `STEP` forme une seule étape.
  Les pièces définies dans le MPD (`0 FILE parts/...`) sont gérées.
- **Tous les sets n'ont pas de modèle LDraw :** 10698 et 11011 (utilisés plus haut) n'y sont pas, `--set` le dit ; il faut alors un fichier `--model`
  (créé avec LDraw/Bricklink Studio exporté en .ldr, ou trouvé en ligne). Les fichiers `.io` de Studio ne sont pas lus.
- **Vérifié :** tests hors ligne (`test_legonotice.py`) et rendu contrôlé dans Chromium sur trois modèles OMR, de 28 à 2 320 pièces.
  Limites : pas de multiplicateur « ×4 » pour un sous-assemblage répété (il est répété étape par étape), pas de pièces en rotation animée.

### Export PDF

```bash
python3 legonotice.py --model mon_modele.mpd --out notice.html --pdf notice.pdf
```

PDF A4, **2 étapes par page** : image de l'étape (caméra recadrée sur ce qui est déjà monté, pièces nouvelles en couleur) et liste des pièces avec le tag « imprimable ».
`--pdf` pilote Chrome, Chromium ou Edge sans interface (variable `CHROME` pour indiquer le binaire). Sans navigateur en ligne de commande :
ouvrez `notice.html` et cliquez sur **PDF** (impression du navigateur, « Enregistrer au format PDF »). Exemple : 16 étapes → 8 pages, 0,7 Mo.
Au-delà de ~300 étapes (gros modèles), le PDF devient lourd et lent à produire : un avertissement s'affiche.

## Modèle construit avec les pièces d'un set (`legobuild.py`)

Pour les boîtes de briques en vrac sans modèle LDraw (ex. 10698) : on choisit une forme, l'outil construit **uniquement avec les briques et couleurs de l'inventaire**.

```bash
python3 legobuild.py 10698 --shape sphere --out build_10698/ --pdf
python3 legobuild.py 10698 --model ma_forme.stl --max-colors 12 --colors "Red,Blue,White"
```

1. Prend les briques « Brick N x M » de l'inventaire (plaques, tuiles, pièces spéciales et couleurs transparentes exclues par défaut ; `--trans` pour les transparentes).
2. Garde les `--max-colors` couleurs les plus abondantes (8 par défaut ; 0 = toutes) ou celles de `--colors`.
3. Cherche la plus grande taille de la forme (formes : sphere, cone, cylinder, torus, pyramid, ou STL/OBJ) qui se monte avec les stocks réels,
   joints décalés d'une rangée à l'autre, briques flottantes retirées.
4. Répartit les couleurs en dégradé vertical (teintes puis neutres), en respectant le stock par taille et par couleur.

Sorties : `modele.ldr` (une étape par paquet de 10 briques), `notice.html` (+ `notice.pdf` avec `--pdf`), `pieces_utilisees.csv`, `pieces_restantes.csv`
et `kit/<Couleur>/*.3mf|stl` pour imprimer **seulement** les pièces utilisées.
Exemple : set 10698, sphère → 10×10×8, 72 briques sur 164 disponibles avec 8 couleurs (14×14×12, 285 briques avec 27 couleurs).
La notice demande la bibliothèque LDraw (`--ldraw complete.zip` ou téléchargement dans le cache) ; `--no-notice` / `--no-print` pour s'en passer.
Les codes couleur LDraw reprennent l'id Rebrickable quand la teinte correspond, sinon une couleur directe RVB.

## Application web (`legoweb.py`)

```bash
python3 legoweb.py                          # http://127.0.0.1:8000
python3 legoweb.py --port 9000 --ldraw complete.zip --cache ~/.cache/legokit
```

Serveur Python standard (aucune dépendance), interface dans `web/index.html`, trois onglets :

- **Kit à imprimer** : numéro de set, imprimante (plateau 180 à 350 mm) et jeu → photo du set, taux de couverture, **plateaux 3D interactifs** par couleur
  (rotation, zoom, vue de dessus), téléchargement 3MF/STL par plateau ou **ZIP** complet, liste des pièces avec **photos**, filtres par couleur et par source.
- **Modèle avec les pièces du set** : forme, nombre de couleurs → modèle construit avec les seules briques du set, notice 3D intégrée, plateaux, `.ldr`, CSV, ZIP.
- **Notice de montage** : numéro de set de l'OMR LDraw, ou envoi d'un fichier `.ldr` / `.mpd` → notice 3D étape par étape (bouton PDF dans la notice).

Fonctionnement : les calculs tournent en tâche de fond (une à la fois, avec le journal affiché), les résultats sont conservés 24 h dans `~/.cache/legokit/web/`.
Premier lancement : téléchargement des données Rebrickable (~15 Mo) et de la bibliothèque LDraw (~150 Mo). Les photos des pièces sont chargées par votre navigateur depuis le CDN Rebrickable.

**Sécurité :** le serveur écoute sur `127.0.0.1` par défaut et n'a pas d'authentification ; il télécharge et écrit des fichiers. Ne l'exposez pas sur Internet sans reverse proxy authentifié.
Les entrées sont validées (numéro de set, bornes numériques, extensions `.ldr`/`.mpd`, 40 Mo max), les chemins de fichiers sont confinés au dossier de la tâche et les notices générées sont affichées dans un `iframe` isolé (`sandbox`), avec échappement des noms venant d'un fichier envoyé.
Tests : `python3 test_legoweb.py` (serveur complet, sans réseau).
