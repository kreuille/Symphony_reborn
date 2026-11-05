# Protocole d'expérience : otoscope USB bas coût et photogrammétrie (COLMAP) sur fantômes

Version 0.1 (brouillon). Les seuils chiffrés sont des **hypothèses de départ** à confirmer ; aucun coût n'est chiffré (décision 7 de `DECISIONS.md`).

## 1. Objectif et question posée

**Question** : à partir de la vidéo d'un otoscope USB bas coût qui se retire d'un conduit, la photogrammétrie (COLMAP) reconstruit-elle assez bien le déplacement de la caméra pour servir de source d'axe (option « V », odométrie visuelle) au scanner à anneau laser ?

C'est l'hypothèse la plus incertaine de la configuration V du simulateur (`docs/conception-scanner.md`, section 6) : j'y ai supposé un bruit de 10 µm par image et une erreur d'échelle de 0,3 %, sans mesure. L'expérience sert à remplacer ces hypothèses par des valeurs mesurées.

**Ce que l'expérience ne teste pas** : l'anneau laser, la précision de la forme du conduit, les coudes réalistes en main libre, la peau réelle, le cérumen, la mâchoire. Elle ne mesure pas non plus un produit : l'otoscope sert d'instrument d'essai.

## 2. Hypothèses à tester

| # | Hypothèse | Mesure |
|---|---|---|
| H1 | COLMAP recale la grande majorité des images dans un conduit étroit | fraction d'images recalées |
| H2 | L'échelle globale (mm par unité COLMAP) est stable d'un essai à l'autre | écart-type / moyenne sur 3 répétitions |
| H3 | L'échelle ne dérive pas le long du retrait | dérive d'échelle locale sur 5 mm, erreur de longueur de bout en bout |
| H4 | Le bruit de position par image est de l'ordre de 10 µm (valeur du simulateur) | résidu axial entre images successives |
| H5 | La texture de paroi conditionne le résultat (lisse = pire cas) | comparaison lisse / mouchetée / teintée |

## 3. Matériel

### 3.1 Capteur d'image
- **2 otoscopes USB bas coût de modèles différents** (pour ne pas conclure sur un seul exemplaire). À relever sur chacun, car les fiches commerciales sont peu fiables : diamètre réel de la pointe, résolution et cadence réelles, plage de netteté (distances), champ de vue mesuré, éclairage réglable ou non, contrôle de l'exposition, format vidéo (MJPEG ou H.264).
- Cible d'étalonnage (damier ou grille de points) de petites dimensions, imprimée à l'échelle.

### 3.2 Banc de déplacement
- Axe linéaire motorisé (un axe de vos imprimantes, ou un rail à moteur pas à pas), vitesse constante réglable de 2,5 à 10 mm/s, course d'au moins 30 mm, résolution de position meilleure que 0,02 mm, otoscope fixé rigidement et aligné sur l'axe du fantôme.
- Repère visible au début du mouvement (LED ou marque) pour caler le temps de la vidéo sur celui du banc.
- Journal de position du banc (heure, mm) ou vitesse constante connue.

### 3.3 Fantômes
Générés par `tools/photogrammetrie/exporter_fantome.py` à partir des conduits du simulateur (STL étanche vérifié) :

| Fantôme | Commande | Rôle |
|---|---|---|
| P1 : presque cylindrique | `--conduit droit_cylindre --elargir 1.2` | cas le plus défavorable : peu de relief |
| P2 : conique elliptique | `--conduit droit_conique --elargir 1.2` | conduit droit plus réaliste |
| P3 : avec deux coudes | `--conduit realiste --elargir 1.2` | forme réaliste (étape 3) |

`--elargir` ajoute un rayon au conduit pour laisser passer la pointe de l'otoscope : **à adapter au diamètre mesuré de la pointe**. L'option `--noyau` exporte la lumière seule pour mouler du **silicone** autour d'un noyau imprimé (puis retirer le noyau).

Variantes de surface pour chaque fantôme :
- **S0 lisse** : résine poncée ou silicone lisse. Les stries de couches d'une impression brute sont une texture artificielle : à supprimer (ponçage, enduit) ou à signaler.
- **S1 mouchetée** : mouchetis noir et blanc, par exemple à la bombe, pour avoir une texture de référence.
- **S2 teintée** : silicone pigmenté (tons chair, veinules) pour se rapprocher d'une peau.

Contrôle du fantôme : mesurer le diamètre intérieur à plusieurs profondeurs avec des jauges ou calibres étalons ; l'incertitude de fabrication est à relever (c'est la vérité terrain de la forme).

## 4. Étalonnage de l'otoscope (avant les essais)
1. Fixer l'exposition, le gain et la balance des blancs si l'appareil le permet (sinon noter le comportement automatique).
2. Prendre 30 à 50 images de la cible à plusieurs distances et inclinaisons, dans la plage de netteté.
3. Estimer les paramètres de la caméra (modèle de distorsion à choisir selon le champ : modèle standard ou fisheye) et les conserver pour fixer les paramètres intrinsèques dans COLMAP.
4. Mesurer la distance minimale nette et le champ réel avec la cible.

## 5. Acquisition
- Éclairage : LED de l'otoscope seule, intensité fixe pendant chaque essai ; pièce sombre.
- Vidéo à la résolution et au débit les plus élevés, compression la plus faible possible (la compression efface la texture fine).
- Retrait de la pointe depuis le fond du fantôme (ou entrée jusqu'au fond), vitesse constante sur au moins 25 mm.
- Nommer chaque essai : `fantome_surface_vitesse_lumiere_rep` (ex. `P2_S1_5mm_L100_r1`).
- Garder : vidéo brute, journal du banc, paramètres du banc et de l'otoscope, notes (incident, ré-éclairage, buée).

## 6. Traitement (COLMAP)
Les noms d'options peuvent changer selon la version de COLMAP : à vérifier avec `colmap -h`.

```bash
ffmpeg -i essai.mp4 -vf fps=10 -start_number 0 frames/frame_%06d.png
colmap feature_extractor --database_path db.db --image_path frames \
       --ImageReader.single_camera 1 --ImageReader.camera_model OPENCV
colmap sequential_matcher --database_path db.db
colmap mapper --database_path db.db --image_path frames --output_path sparse
colmap model_converter --input_path sparse/0 --output_path txt --output_type TXT
```

- Fixer les paramètres intrinsèques issus de l'étalonnage quand ils sont fiables ; sinon laisser COLMAP les estimer et le noter.
- La cadence d'extraction (ici 10 images/s) doit être celle donnée à l'analyse (`--fps`).
- Lancer deux fois les cas limites (graine différente) pour voir si le résultat est stable.

## 7. Analyse
Script : `tools/photogrammetrie/analyse_colmap.py` (numpy seul ; test intégré : `--demo`).

```bash
python3 tools/photogrammetrie/analyse_colmap.py --images txt/images.txt --vitesse 5 --fps 10 --longueur 25
```

Il recale la trajectoire de caméra de COLMAP sur la trajectoire du banc par une transformation avec facteur d'échelle, puis donne : fraction d'images recalées, échelle (mm par unité COLMAP), erreur RMS (3D, axiale, latérale), erreur de longueur de bout en bout, dérive d'échelle locale (rapport des cordes sur 5 mm). Pour le fantôme P3 ou un trajet non rectiligne, fournir `--verite` (CSV `image,x,y,z` en mm).

Mesures complémentaires :
- **Forme** : comparer le nuage de points dense de COLMAP à la surface du fantôme avec un logiciel libre de comparaison nuage-maillage (par exemple CloudCompare), après recalage avec échelle ; relever l'erreur de rayon.
- **Bruit par image (H4)** : écart-type du résidu axial entre images successives, à comparer à 10 µm.
- **Décalage temporel** : décaler les indices d'image de quelques positions pour vérifier que le meilleur ajustement correspond bien au repère de départ ; reporter le décalage retenu.

## 8. Plan d'essais

| Étape | Contenu | Essais |
|---|---|---|
| 0. Préparation | Réception du matériel, mesures de l'otoscope, étalonnage, impression et contrôle des fantômes, validation du script d'analyse sur le test `--demo` | — |
| 1. Essai de fumée | P2 lisse (S0) et mouchetée (S1), 5 mm/s, 1 essai chacun | 2 |
| 2. Matrice principale | P1 et P2 × S0, S1 × 2,5 et 5 mm/s × 3 répétitions | 24 |
| 3. Lumière et vitesse | P2 S1, LED au maximum et réduite, 10 mm/s | environ 6 |
| 4. Surface teintée | P2 et P1 en S2 (silicone), 5 mm/s, 3 répétitions | 6 |
| 5. Fantôme coudé | P3 mouchetée, passage manuel guidé, comparaison nuage-maillage | 3 à 6 |

Répéter le plan sur le second modèle d'otoscope à partir de l'étape 2 (au moins P2, S1).

## 9. Critères de décision (hypothèses à valider)

| Mesure | Seuil de départ | Origine |
|---|---|---|
| Images recalées sur surface mouchetée | ≥ 90 % | continuité du suivi |
| Erreur de longueur de bout en bout | ≤ 0,8 % (0,2 mm sur 25 mm) | critère de la section 2 de `conception-scanner.md` |
| Dérive d'échelle locale, maximum sur 5 mm | ≤ 1 % | tolérance d'échelle de 1 à 2 % (section 7.1) |
| Répétabilité de l'échelle (3 essais) | ≤ 1 à 2 % | idem |
| RMS latéral après recalage | ≤ 0,2 mm | budget scanner 0,10 mm nominal |

- **Go pour l'option V** : seuils tenus sur surface mouchetée à 5 mm/s sur les deux otoscopes.
- **Go conditionnel** : seuils tenus seulement à 2,5 mm/s ou sur un seul modèle ; limiter la vitesse de retrait ou améliorer l'éclairage.
- **No-Go pour V seule** : moins de 70 % d'images recalées sur surface mouchetée, ou erreur de longueur supérieure à 2 % ; s'appuyer alors sur le suivi externe (option T3) et utiliser la vidéo en complément.
- **Résultat sur surface lisse** : informatif (pire cas), pas un critère d'arrêt ; la peau réelle a une texture inconnue à mesurer ensuite.

## 10. Retour dans la conception
1. Remplacer dans `tools/simulation/simulateur_scanner.py` les paramètres `vo_sigma` (bruit par image) et `vo_scale` (erreur d'échelle) par les valeurs mesurées, puis relancer la comparaison des configurations.
2. Mettre à jour la section 6 de `docs/conception-scanner.md` et la recommandation du plan de développement.
3. Décider si l'otoscope bas coût reste un outil d'essai ou si l'on spécifie une caméra miniature dédiée.

## 11. Risques et parades

| Risque | Parade |
|---|---|
| Exposition et balance des blancs automatiques qui varient | Verrouiller si possible ; sinon éclairage de référence et notes |
| Compression vidéo qui efface la texture | Débit maximal, format le moins compressé disponible |
| Mise au point fixe : paroi trop proche ou trop lointaine | Choisir le diamètre du fantôme pour rester dans la plage nette (mesurée à l'étape 0) |
| Vue vers l'avant : peu de parallaxe, triangulation de profondeur médiocre | C'est précisément le cas à tester ; noter les images perdues |
| Obturateur à balayage ligne par ligne (déformation en mouvement) | Vitesses limitées ; comparer 2,5 et 5 mm/s |
| Fantôme imprimé : stries de couches qui servent de fausse texture | Surface lisse poncée pour S0 ; signaler les stries |
| Décalage temporel entre la vidéo et le banc | Repère visible au départ ; balayage du décalage dans l'analyse |
| Trop de variantes | Suivre l'ordre des étapes ; s'arrêter si l'essai de fumée échoue |

## 12. Sécurité et éthique
- Fantômes uniquement. Les otoscopes grand public ne sont pas conçus pour un usage de recherche.
- Tout essai sur une personne exige un consentement et le cadre éthique et réglementaire approprié, à définir avant (points ouverts 2 et 3 de `DECISIONS.md`).
- Éclairage LED : sans risque particulier sur fantôme ; à revoir si l'otoscope est utilisé sur une personne.

## 13. Livrables
1. Jeu de données : vidéos brutes, étalonnages, journaux du banc, conditions de chaque essai.
2. Tableau récapitulatif des mesures de la section 7 pour chaque essai.
3. Rapport de 3 à 4 pages : réponse aux hypothèses H1 à H5, décision Go / Go conditionnel / No-Go, paramètres mesurés pour le simulateur.
4. Fichiers STL des fantômes et notes de fabrication.

## 14. Planning indicatif
Environ 3 semaines : semaine 1 (achat, mesures, étalonnage, fantômes), semaine 2 (essais des étapes 1 à 4), semaine 3 (étape 5, analyse, rapport, mise à jour du simulateur). À ajuster selon les délais de livraison et de moulage.
