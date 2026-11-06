# Conception du scanner : calculs et décisions de conception (v0.1)

Complète `specs/scanner-spec-prototype.md` (v0.2) et `docs/plan-developpement-scanner.md`. Les chiffres des sections 1 à 5 viennent du script `tools/simulation/conception_scanner_calculs.py` (sortie : `tools/simulation/resultats_calculs.txt`) ; ceux de la section 6 viennent du simulateur `tools/simulation/simulateur_scanner.py`. Les deux n'utilisent que numpy. Ce sont des **calculs d'ordre de grandeur sur des modèles simples**, pas des mesures : surface lisse, bruit indépendant de 0,02 mm par point, conduit modélisé par un cône légèrement elliptique. Ils servent à orienter la conception, pas à valider.

## 1. Quatre résultats qui changent la conception

### R1. Le recalage par surface (ICP) ne suffit pas pour la pose
Un anneau laser est recalé contre la surface déjà reconstruite. Calcul de l'incertitude sur la pose, rayon moyen 3,5 mm, 360 points par anneau, pas de 0,3 mm, 100 anneaux sur 30 mm :

| Cas | Axial par anneau | Axial cumulé sur 30 mm | Orientation seule par ICP |
|---|---|---|---|
| Cylindre parfait | non observable | non observable | non observable |
| Conicité 1° environ | 0,053 mm | 0,53 mm | non observable |
| Conicité 3° environ | 0,021 mm | 0,21 mm | non observable |
| Conicité 3° + ellipticité 5 % | 0,021 mm | 0,21 mm | inclinaison non observable ; décalage latéral 0,26 mm |
| Hypothèse : micro-relief de peau 0,03 mm / 1,5 mm | 0,007 mm | 0,07 mm | latéral 0,019 mm ; inclinaison 10° |

- La position axiale n'est contrainte que par la conicité (ou par un relief de paroi, hypothétique) : sur un conduit presque cylindrique elle est mal connue.
- L'**inclinaison de la sonde est confondue avec un décalage latéral** : un anneau incliné et un anneau décalé se ressemblent.
- Le **roulis** d'un conduit circulaire est inobservable.
- Conséquence : l'orientation doit venir d'ailleurs (gyroscope, texture vidéo, suivi externe). La phrase « fusion IMU + ICP » de la spécification (§4.2) n'est valable que si le gyroscope donne l'orientation et si une autre source donne l'axe.
- Nuance : une erreur axiale de 0,2 mm dans un conduit lisse change peu la forme (0,2 mm × conicité 0,05 = 0,01 mm de rayon). Elle affecte surtout la longueur et la position des coudes.

**Correction d'une affirmation antérieure :** j'avais écrit que le motif codé (tête B) donne des « morceaux de surface plus exploitables pour l'ICP ». Le calcul nuance cela : sur une paroi lisse, un morceau de surface a la même dégénérescence qu'un anneau ; il réduit le bruit, pas l'ambiguïté. L'avantage de la tête B tient à la tolérance au mouvement et à la mesure instantanée, pas à une pose mieux contrainte.

### R2. L'accéléromètre ne donne pas la position axiale
Double intégration : 1 mg de biais résiduel donne 1,2 mm d'erreur en 0,5 s et 4,9 mm en 1 s ; 0,1 mg donne encore 0,5 mm en 1 s. Il ne peut pas fournir l'axe à 0,1 mm. Le gyroscope reste utile pour l'orientation.

### R3. La géométrie de la tête A impose un grand champ, ou une base plus longue
Disposition retenue dans la spécification : caméra sur l'axe, anneau laser projeté dans un plan situé à la distance B devant la caméra. Un point de paroi de rayon ρ est vu à l'angle atan(ρ/B) de l'axe. Capteur de 400 px, objectif équidistant, rayon de paroi jusqu'à 6 mm (diamètre 12 mm) :

| Base B | Champ total requis | Résolution à r = 4 mm | Résolution à r = 6 mm |
|---|---|---|---|
| 1,5 mm | 152° | 0,081 mm/px | 0,169 mm/px |
| 2,0 mm (spécification) | 144° | 0,062 mm/px | 0,125 mm/px |
| 3,0 mm | 126° | 0,046 mm/px | 0,083 mm/px |
| 4,0 mm | 112° | 0,039 mm/px | 0,064 mm/px |
| 5,0 mm | 100° | 0,036 mm/px | 0,053 mm/px |

- **Incohérence dans la spécification v0.2 :** elle prévoit un champ de 100 à 120° et une base de 1,5 à 2 mm, ce qui ne permet de voir que des parois de rayon inférieur à environ 3,5 mm (diamètre 7 mm). Pour couvrir 12 mm, il faut soit B ≥ 3,5 mm (champ environ 120°), soit un champ de 145 à 150° (c'est le chiffre du brevet de l'Otoscan, objectif difficile).
- Une base plus longue améliore aussi la résolution, au prix d'une pointe plus longue (fenêtre transparente entre la caméra et le plan de l'anneau). La pointe doit rester atraumatique et passer le deuxième coude : à vérifier sur fantômes coudés.
- Avec un sous-pixel de 0,1 à 0,3 px, l'erreur de profondeur reste de l'ordre de 5 à 40 µm : compatible avec le budget scanner de 0,10 mm RMS, à confirmer après étalonnage.
- Autre levier à étudier : un cône laser dirigé vers l'avant (demi-angle inférieur à 90°) réduit l'angle de vue requis, mais l'anneau n'est plus plan et l'étalonnage se complique.

### R4. Cadence et synchronisation
- Le pas axial entre anneaux vaut vitesse / cadence : 0,33 mm à 10 mm/s et 30 mesures/s. La flèche d'interpolation sur un conduit lisse est négligeable (0,003 mm pour un rayon de courbure de 5 mm) : **la cadence n'est pas limitante** pour la justesse, contrairement à ce qu'on pourrait craindre avec P6 (10 mm/s) et P7 (pas de maillage 0,1 mm).
- Le flou de bouger est faible : 10 µm pour 10 mm/s et 1 ms d'exposition.
- Le point critique est la **datation** : une erreur de 1 ms à 50 mm/s de mouvement relatif donne 0,05 mm. Exigence proposée : horodatage matériel commun caméra, laser, gyroscope et suivi, avec un décalage résiduel ≤ 0,5 ms. **Le simulateur (section 6) relativise ce chiffre** : pour la forme et des vitesses de main de 5 à 10 mm/s, plusieurs millisecondes de désynchronisation sont tolérées si la latence est connue.

## 2. Architecture de pose proposée (à valider)

| Étape | Orientation | Position axiale | Latéral |
|---|---|---|---|
| **Phase 1, banc motorisé** (essais T2, T3, T5) | platine ou gyroscope | codeur linéaire du banc (déjà prévu) | ICP, anneau |
| **Phase 1, scan manuel** (essais T4, T6) | gyroscope 6 axes ≥ 200 Hz, horodaté | **à trancher par essais** entre trois sources (ci-dessous) | ICP, anneau |
| Produit | gyroscope + texture vidéo | source retenue | ICP |

Trois candidats pour l'axe en scan manuel, à comparer sur le même banc :
1. **Odométrie visuelle** sur les images vidéo (éclairage LED blanc, images entrelacées avec les images de mesure, comme dans les brevets de l'Otoscan). Hypothèse à tester : les images contiennent assez de texture (peau, poils) pour mesurer l'avance.
2. **Suivi externe de la poignée** (option T3 du plan de développement) : sonde rigide, caméra fixe, repères sur la poignée.
3. **Conicité et relief par ICP** : seulement comme contrainte faible, jamais seule.

Critère de choix proposé : erreur de longueur axiale ≤ 0,2 mm sur 25 mm, et RMS du maillage final dans le budget (seuil Go 0,15 mm, nominal 0,10 mm).

## 3. Paramètres proposés pour la tête A (v0.3, à confronter aux composants réels)

| Paramètre | Spécification v0.2 | Proposition v0.3 | Raison |
|---|---|---|---|
| Base de triangulation B | 1,5 à 2 mm | 3 à 4 mm (à ajuster selon la caméra) | Champ requis et résolution (R3) |
| Champ de vision | 100 à 120° | 115 à 130° | Couvre 12 mm avec B = 3 à 4 mm |
| Pointe | ≤ 4,5 mm de diamètre | idem, avec fenêtre transparente de longueur B | Caméra voit l'anneau à travers la fenêtre |
| Cadence | non précisée | caméra ≥ 60 images/s : 30 mesures + 30 vidéo par seconde | Entrelacement vidéo / mesure |
| Exposition laser | non précisée | impulsion ≤ 1 ms synchronisée | Flou de bouger et sécurité |
| Datation | non précisée | horodatage matériel commun, résiduel ≤ 0,5 ms | R4 |
| Orientation | IMU 6 axes ≥ 200 Hz | idem, gyroscope prioritaire | R1, R2 |
| Axe | ICP | codeur sur banc ; source à trancher en manuel | R1, R2 |

La spécification n'a pas été modifiée : ces valeurs sont des propositions à valider (l'essai T1 de la spécification, étalonnage et erreur de reprojection, est le premier test du banc).

## 4. Limites de ces calculs
- Surface supposée parfaitement connue, bruit indépendant : l'ICP réel sera moins bon.
- Conicité, ellipticité et relief de peau choisis par hypothèse : à remplacer par des mesures sur de vraies oreilles (scans publics ou issus du pilote).
- Pas de coudes, pas de mouvement de la mâchoire, pas de cérumen ni de reflets.
- Le champ requis suppose une caméra sur l'axe et un anneau plan à 90° ; un objectif annulaire panoramique (type endoscope industriel) est une autre disposition à comparer.

## 6. Résultats du simulateur de pose (v0.1)

Outil : `tools/simulation/simulateur_scanner.py` (numpy seul). Il génère un conduit synthétique, simule un retrait manuel de la sonde (vitesse variable, décalage latéral, inclinaison et roulis aléatoires, 30 mesures/s, anneau de 72 points, bruit de 0,02 mm), lance les rayons de l'anneau sur la paroi, puis reconstruit la pose avec cinq configurations. Résultats complets : `tools/simulation/resultats_simulateur.txt` (8 graines) et `resultats_simulateur_gyro_0.5.txt`.

| Config | Axe | Orientation | Latéral |
|---|---|---|---|
| poses vraies | vérité | vérité | vérité |
| E : codeur | codeur, bruit 5 µm | gyroscope | recalage de l'anneau sur un modèle local de surface |
| V : odométrie visuelle | bruit 10 µm/image + erreur d'échelle 0,3 % (**hypothèses**) | gyroscope | idem |
| T : suivi externe | pose absolue : bruit 0,04 mm, erreur d'étalonnage main-pointe 0,05 mm, dérive 0,03 mm, 0,1° (**hypothèses**) | suivi | suivi |
| I : recalage seul | aucune | gyroscope | idem, axe prédit à vitesse constante |

Erreur RMS du nuage reconstruit par rapport à la surface exacte (mm), moyenne sur 8 graines. Gyroscope : biais résiduel 0,05 °/s.

| Conduit | Poses vraies | E codeur | V odom. visuelle | T suivi externe | I recalage seul |
|---|---|---|---|---|---|
| Droit, conique, elliptique | 0,020 | 0,21 | 0,21 | **0,074** | 0,27 |
| Droit, presque cylindrique | 0,020 | 0,20 | 0,20 | **0,075** | 0,23 |
| Avec deux coudes | 0,019 | 0,71 | 0,71 | **0,075** | 0,74 |
| Avec deux coudes et micro-relief (hypothèse) | 0,019 | 0,71 | 0,71 | **0,075** | 0,74 |

Erreur de position axiale à la fin d'un retrait de 24 mm (mm) : E 0,08 à 0,45 ; V 0,10 à 0,46 ; T 0,06 ; **I 4,2 à 4,6**.

### Amélioration de l'estimateur : suivi du centre de la lumière (v0.2 du simulateur)
Le recalage de chaque anneau sur un modèle de surface (configs E et V ci-dessus) dérive dans les coudes. Diagnostic : l'anneau est situé à la distance B devant la sonde ; dans un coude, la tangente du conduit à cet endroit est tournée de (courbure × B) par rapport à l'axe de la sonde, soit environ 0,4 rad avec B = 3,5 mm et un coude serré. Un estimateur qui suppose que le centre de la lumière avance dans l'axe de la sonde se trompe donc d'environ 0,07 mm par image dans un coude.

Nouvel estimateur (configs « centre ») : la position latérale est déduite du centre de l'anneau mesuré (moyenne des points) et de sa progression le long de la tangente ; la courbure est estimée par le gyroscope (rotation mesurée par unité d'avance, filtrée). Pas de modèle de surface, pas de recalage.

| Conduit | Recalage de surface (E + ICP) | **Suivi du centre, axe par codeur** | **Suivi du centre, axe par odométrie visuelle** | Suivi externe (T) |
|---|---|---|---|---|
| Droit, conique | 0,21 | 0,25 | 0,26 | **0,074** |
| Droit, presque cylindrique | 0,20 | 0,26 | 0,26 | **0,075** |
| Avec deux coudes | 0,71 | **0,25** | **0,25** | **0,075** |
| Avec deux coudes et micro-relief (hypothèse) | 0,71 | **0,25** | **0,25** | **0,075** |

Erreur RMS du nuage (mm), 8 graines. Erreur latérale RMS du suivi du centre avec coudes : 0,35 mm (0,5 mm si le biais résiduel du gyroscope est dix fois plus fort, 0,5 °/s, avec une surface de 0,30 mm).

Lecture :
1. **Gain net dans les coudes** (0,71 → 0,25 mm) ; pas de gain sur conduit droit, où l'ancien estimateur est déjà à 0,2 mm. L'erreur reste **au-dessus du seuil Go de 0,15 mm** (et du nominal 0,10).
2. **L'axe par odométrie visuelle (V) donne presque le même résultat que le codeur** (0,25 contre 0,25 mm) sous mes hypothèses de bruit (10 µm par image, 0,3 % d'échelle). Elles restent à mesurer (protocole `protocole-experience-otoscope-colmap.md`).
3. **Limites de cet estimateur** : il suppose que la sonde reste alignée sur le conduit à quelques degrés près. Sensibilité à l'inclinaison de la sonde simulée : faible (0,21 à 0,25 mm de 0,5° à 2°). L'erreur restante vient surtout de l'estimation de la direction du conduit (gyroscope, filtre de courbure). Le coefficient de filtrage de la courbure a été choisi parmi trois valeurs sur les mêmes graines : léger réglage sur les données de test.
4. **Les coudes simulés sont des coudes que j'ai choisis** (deux coudes opposés de 29° et 26°, rayon de courbure minimal de l'ordre de 9 mm) : à remplacer par des courbures mesurées sur de vraies oreilles.

### Fusion du suivi externe et du suivi du centre (v0.3 du simulateur)
Configuration F : le suivi du centre de la lumière (axe par odométrie visuelle, courbure par gyroscope) fournit la position image par image ; le suivi externe de la poignée la recale en douceur (gain 0,3 en position, 0,05 en orientation) quand il voit la poignée. Le calcul est causal (pas d'interpolation sur les images futures). Erreur RMS du nuage (mm) :

| Scénario | Suivi du centre seul (V) | Suivi externe seul (T) | **Fusion (F)** |
|---|---|---|---|
| Nominal (bruit 0,04 mm, erreur main-pointe 0,05 mm), avec coudes | 0,25 | **0,075** | 0,080 |
| Nominal, conduit droit | 0,26 | **0,074** | 0,079 |
| Deux occultations de 25 images (environ un tiers du retrait), avec coudes | 0,23 | 0,153 | **0,106** |
| Deux occultations, conduit droit | 0,23 | 0,148 | **0,103** |
| Suivi dégradé (bruit 0,1 mm, erreur main-pointe 0,1 mm), avec coudes | 0,23 | 0,140 | **0,111** |
| Suivi dégradé, conduit droit | 0,23 | 0,136 | **0,107** |
| Gyroscope 10 fois moins bon (0,5 °/s), avec coudes | 0,30 | **0,069** | 0,077 |

Lecture :
1. **Sans panne, la fusion n'améliore pas le suivi externe** (0,080 contre 0,075 mm) : le suivi externe domine, la fusion ne fait que le lisser.
2. **La fusion apporte de la robustesse** : avec occultations ou avec un suivi dégradé, l'erreur passe de 0,14-0,15 à 0,10-0,11 mm. Elle est causale, alors que le suivi seul est interpolé après coup : l'avantage est donc plutôt sous-estimé.
3. **Orientation** : 0,06° pour la fusion contre 0,18° pour le suivi externe seul (nominal) ; avec un gyroscope dix fois moins bon, 0,57° pour la fusion (le gyroscope pèse alors plus).
4. **Aucune configuration ne passe sous 0,10 mm quand le suivi est dégradé ou masqué** : le budget nominal de 0,10 mm RMS n'est tenu que sous les hypothèses nominales d'étalonnage du suivi externe. La qualité de ce suivi (erreur main-pointe, bruit, taux d'occultation) est donc le facteur dominant.
5. **Limites** : gain de fusion choisi parmi trois valeurs (0,1 ; 0,2 ; 0,3) sur 3 graines ; modèle de suivi simple (bruit, biais constant, dérive lente ; pas de latence, de désynchronisation, de valeurs aberrantes ni de mouvement de la tête au-delà de la dérive) ; occultations en rafales régulières.

### Latence et désynchronisation du suivi externe (v0.4 du simulateur)
Modèle : le suivi externe livre à l'image k la pose de l'instant k·dt moins une latence de 30 ms. L'algorithme compense la latence qu'il connaît ; la **désynchronisation** est la part non compensée (latence mal connue). Conduit avec coudes, 4 graines ; résultats complets : `tools/simulation/resultats_latence_suivi.txt`. Le mouvement de la main est ici **lissé** (option `--mouvement lisse`) ; les résultats précédents de cette section utilisent le mouvement **saccadé** par défaut, plus sévère (rotation et décalage latéral aléatoires à chaque image). Avec le mouvement lissé et sans latence, les conclusions précédentes ne changent pas (suivi externe 0,071 mm, fusion 0,066 à 0,068 mm, suivi du centre 0,27 à 0,28 mm, recalage de surface 0,73 mm avec coudes ; `resultats_simulateur_mouvement_lisse.txt`).

RMS du nuage (mm), mouvement lissé :

| Vitesse | Désynchronisation | Suivi externe T | Fusion F |
|---|---|---|---|
| 5 mm/s | 0 ms | 0,067 | 0,073 |
| 5 mm/s | 10 ms | 0,065 | 0,075 |
| 5 mm/s | 30 ms | 0,082 | 0,081 |
| 10 mm/s | 0 ms | 0,069 | 0,079 |
| 10 mm/s | 10 ms | 0,068 | 0,077 |
| 10 mm/s | 30 ms | 0,086 | 0,078 |

Mouvement saccadé (cas sévère), 5 mm/s : T de 0,069 (0 ms) à 0,071 (5 ms), 0,078 (10 ms) et **0,130 mm (30 ms)** ; F de 0,089 à 0,091, 0,093 et **0,102 mm**.

Erreur de pose de la fusion (axe final, orientation finale) : à 5 mm/s, 0,04 mm et 0,07° sans désynchronisation, 0,07 mm et 0,19° à 10 ms, 0,14 mm et 0,53° à 30 ms ; à 10 mm/s, 0,05 / 0,11 / 0,35 mm. L'erreur axiale vaut à peu près la vitesse multipliée par la désynchronisation. (Je ne reporte pas l'erreur finale du suivi externe seul : elle est faussée par l'effet de bord de l'interpolation différée en fin de série.)

Lecture :
1. **Avec une main qui bouge doucement, jusqu'à 10 ms de désynchronisation ne change presque rien à la forme** (écart inférieur à 0,003 mm), car un décalage le long de l'axe est presque invisible sur un conduit lisse. À 30 ms, le suivi externe seul perd environ 0,015 mm.
2. **La désynchronisation se voit dans la pose** (position axiale, orientation) : elle compte si l'on exploite la position le long du conduit (profondeur, longueur, position des coudes).
3. **Quand la main bouge de façon saccadée, la fusion encaisse mieux la latence** : à 30 ms de désynchronisation, 0,102 mm contre 0,130 mm pour le suivi seul.
4. **Conséquence sur l'exigence R4** (horodatage ≤ 0,5 ms, calculée pour un mouvement relatif de 100 mm/s) : pour la forme, des vitesses de main de 5 à 10 mm/s tolèrent plusieurs millisecondes, **à condition de connaître la latence** (à mesurer à ±5 ms environ) et d'horodater les images. L'exigence de 0,5 ms n'est utile que pour des mouvements rapides ou pour la précision de position axiale. À reconsidérer, elle n'est plus un critère dimensionnant dans mes hypothèses.
5. **Limites** : latence constante (pas de variation ni de pertes d'images), mouvement lissé choisi par moi (filtre passe-bas de l'ordre de 2 Hz), gain de fusion non réajusté, pas de mouvement de la tête ni de valeurs aberrantes.

### Mouvement de la tête et valeurs aberrantes du suivi (v0.5 du simulateur)
Modèle : la tête (donc l'oreille) bouge dans le repère du suivi externe (translation et rotation aléatoires lissées, corrélées sur environ 1 s). Le suivi externe mesure la pose de la sonde dans son propre repère. **Compensation** : un clip fixé sur l'oreille est suivi par le même capteur (bruit comme la poignée, plus un **glissement** lent du clip sur l'oreille) et sert à exprimer la sonde dans le repère de l'oreille ; un gyroscope sur la tête retire la rotation de la tête du gyroscope de la sonde. **Valeurs aberrantes** : avec une probabilité par image, la pose du suivi est décalée de 1 mm et 3° (marqueur mal détecté, reflet). La fusion rejette les corrections dont l'écart dépasse 0,5 mm ou 1,5° ; « T + médiane » est le suivi seul avec un filtre médian sur 5 images. Conduit avec coudes, mouvement de main lissé, 5 mm/s, 4 graines. RMS du nuage (mm), erreur latérale RMS entre parenthèses ; résultats : `tools/simulation/resultats_tete_aberrants.txt`.

| Scénario | Suivi du centre seul | Suivi externe T | T + médiane | **Fusion F** |
|---|---|---|---|---|
| Référence (tête immobile) | 0,254 | 0,067 | 0,061 | 0,062 |
| Tête 1,5 mm / 1,5°, **sans compensation** | 0,234 | **1,37** | 1,37 | 0,274 |
| Tête 1,5 mm / 1,5°, compensée (glissement du clip 0,1 mm) | 0,242 | 0,150 | 0,138 | **0,122** |
| Tête 1,5 mm / 1,5°, compensée (glissement 0,3 mm) | 0,242 | 0,367 | 0,359 | **0,304** |
| Tête 3 mm / 3°, compensée (glissement 0,1 mm) | 0,242 | 0,149 | 0,137 | **0,121** |
| Valeurs aberrantes 3 % (tête immobile) | 0,254 | **0,183** | 0,062 | 0,061 |
| Tête 1,5 mm / 1,5° compensée + aberrants 3 % | 0,242 | 0,252 | 0,148 | **0,128** |

Lecture :
1. **Sans compensation de la tête, le suivi externe seul est inutilisable** : le mouvement de la tête passe directement dans la mesure (1,37 mm). La fusion limite les dégâts (0,27 mm) parce que le suivi du centre de la lumière est relatif à l'oreille et que la porte de rejet écarte une partie des corrections incohérentes ; je n'ai pas isolé la part de chaque effet.
2. **La compensation par clip coûte de l'ordre de 0,06 à 0,09 mm** : de 0,062 à 0,122 mm pour la fusion (bruit du clip et glissement de 0,1 mm). Avec un clip qui glisse de 0,3 mm, l'erreur monte à 0,30-0,37 mm : **le glissement du clip sur l'oreille domine et il est lent, donc ni la fusion ni un filtre ne le corrigent**. Il faut un clip rigide (glissement de l'ordre de 0,05 à 0,1 mm), ou suivre l'oreille elle-même avec le capteur 3D externe, sans clip (idée de la section 7.2).
3. **L'amplitude du mouvement de la tête (1,5 ou 3 mm et degrés) n'a pas d'effet une fois compensée** : seule compte la qualité de la mesure du clip.
4. **Les valeurs aberrantes doivent être rejetées** : à 3 %, le suivi brut passe de 0,067 à 0,183 mm ; la médiane (0,062) et la fusion avec porte (0,061) rétablissent le niveau nominal.
5. **Budget** : avec la tête mobile et un clip qui glisse de 0,1 mm, la meilleure configuration (fusion) donne 0,12 mm, au-dessus du nominal de 0,10 mm et sous le seuil Go de 0,15 mm ; avec aberrants en plus, 0,13 mm.
6. **Limites** : mouvement de tête et glissement de clip modélisés par des processus lissés de mon choix ; gyroscope de tête supposé de même qualité que celui de la sonde ; valeurs aberrantes indépendantes d'une image à l'autre ; seuils de rejet fixés une fois (0,5 mm et 1,5°) sans réglage ; la **mâchoire**, qui déforme le conduit lui-même, n'est pas modélisée.

### Ce que ces résultats indiquent
1. **Le contrôle du simulateur est correct** : avec les poses vraies, l'erreur vaut le bruit de mesure (0,019 mm).
2. **Le recalage de surface seul ne donne pas la longueur** : l'axe dérive de 4 à 5 mm sur 24 mm (environ 18 %), conduit conique ou non. Confirme R1 pour l'axe.
3. **Une source d'axe suffit pour la longueur** : codeur (E) ou odométrie visuelle (V, sous mes hypothèses de bruit) ramènent l'erreur axiale à 0,1-0,5 mm.
4. **Mais l'axe n'est pas le principal problème.** Avec un axe parfait (E), l'estimation latérale par recalage de l'anneau dérive encore : 0,2 mm RMS sur conduit droit, **0,7 mm avec coudes**. Cela dépasse le budget scanner (0,10 mm nominal, seuil Go 0,15 mm). Correction de mon analyse R1, qui insistait sur l'axe : sur la forme, c'est la dérive latérale et celle de l'orientation dans les coudes qui domine.
5. **Le suivi externe (T) donne 0,075 mm dans tous les conduits, coudes compris**, sous des hypothèses d'étalonnage que le banc devra confirmer. C'est la seule configuration dans le budget ; le suivi du centre de la lumière arrive à 0,25 mm.
6. **Sensibilités** : biais du gyroscope multiplié par 10 (0,5 °/s) : orientation finale 3,6° au lieu de 0,45°, surface 0,26 mm au lieu de 0,21 mm sur conduit droit (effet modéré, le recalage absorbe une partie). Inclinaison de la sonde de 0° à 2° : aucun effet notable sur la dérive.

### Limites importantes de ce simulateur
- **L'estimateur de E, V et I est simple** (recalage de chaque anneau sur la moyenne des quatre précédents). Les modèles qui extrapolent le long de l'axe (ordre 1 ou 2) sont instables dans mes essais. Le résultat de 0,7 mm avec coudes était bien une limite de cet estimateur : le suivi du centre de la lumière (sous-section ci-dessus) le ramène à 0,25 mm. Une optimisation sur fenêtre glissante fera peut-être encore mieux ; l'objectif de 0,15 mm n'est pas atteint.
- Conduit synthétique (coudes, conicité, ellipticité choisis par hypothèse), bruits gaussiens, pas de cérumen, de reflets, de mouvement de mâchoire ni d'occultation du suivi.
- Les valeurs de V (odométrie visuelle) et de T (suivi externe) sont des hypothèses de ma part ; la faisabilité réelle de V dépend de la texture des images, à tester.

### Conséquences pour la conception
- **La spécification (§4.2 « IMU + ICP ») est insuffisante** : à retenir pour la mise à jour de la spécification.
- **Le banc de la phase 1 ne peut pas se limiter à un codeur linéaire** si les fantômes ont des coudes : il faut une référence de pose en 6 degrés de liberté (bras motorisé, table à plusieurs axes ou suivi externe de référence).
- **Le suivi externe de la poignée (option T3 du plan) reste la base de référence** pour la phase 1, **complété par le gyroscope et le suivi du centre de la lumière** (fusion F) pour tenir les occultations et un suivi imparfait. Le suivi du centre de la lumière avec gyroscope est la meilleure option sans suivi externe (0,25 mm avec coudes) mais ne tient pas encore le budget ; sa dérive restante est à comparer sur banc.
- **Le suivi de la tête est une exigence de conception à part entière** : fixation rigide du clip (glissement ≤ 0,1 mm) ou suivi de l'oreille sans clip ; rejet des valeurs aberrantes du suivi.
- Prochaines étapes pour le simulateur : latence variable et pertes d'images, déformation du conduit par la mâchoire, suivi de l'oreille sans clip, coudes réalistes (rayon de courbure mesuré), mouvement de mâchoire, occultation du suivi, puis comparaison avec des données réelles du banc.

## 7. Photogrammétrie, échelle et recalage sur la partie visible

### 7.1 Photogrammétrie seule : forme juste, échelle inconnue ?
Avec une seule caméra, la reconstruction est connue à un facteur d'échelle près : une seule longueur réelle suffit à fixer toutes les dimensions. Trois nuances pour le conduit auditif :
1. **La forme n'est pas forcément bonne** : la caméra avance le long de son axe de visée (profondeur mal triangulée), les parois sont peu texturées, humides et brillantes, l'objectif est grand angle, la mâchoire bouge.
2. **L'échelle peut dériver** le long de la séquence : ce n'est alors plus un seul facteur à corriger.
3. **La tolérance est serrée** : une erreur d'échelle de 1 % sur un rayon de 4 mm donne 0,04 mm, à comparer au budget de 0,10 mm RMS ; il faut tenir 1 à 2 %.

L'anneau laser fournit une mesure métrique à chaque image ; il lève donc l'ambiguïté d'échelle. Une base stéréo connue ou un suivi externe le font aussi ; un accéléromètre non (R2).

### 7.2 Idée : recaler le scan interne sur la partie du canal visible de l'extérieur
Proposition d'Arnaud : le début du canal est visible de l'extérieur ; un capteur 3D externe le scanne, et la superposition des deux scans corrige l'échelle.

**Essai dans le simulateur** (`python3 simulateur_scanner.py --test-externe`, résultats dans `tools/simulation/resultats_recalage_externe.txt`). Scan interne avec axe par codeur et erreur d'échelle ε, puis recalage par ICP sur 6 mm de conduit visible (50 % des points vus, bruit du capteur externe σ). Moyenne sur 6 graines :

| Conduit | ε | σ externe | Biais de rayon avant | Biais après (échelle seule) | Échelle retrouvée (1 = parfait) | RMS avant | RMS après recalage complet |
|---|---|---|---|---|---|---|---|
| Droit conique | 3 % | 0,1 mm | 0,103 mm | 0,030 mm | 1,007 | 0,305 | 0,398 |
| Droit conique | 3 % | 0,5 mm | 0,103 mm | 0,038 mm | 1,010 | 0,305 | 0,379 |
| Avec coudes | 3 % | 0,1 mm | 0,170 mm | 0,079 mm | 1,002 | 0,720 | 0,776 |
| Avec coudes | 3 % | 0,5 mm | 0,170 mm | 0,080 mm | 1,002 | 0,720 | 0,733 |

Lecture :
1. **L'échelle est retrouvée à 1 % près**, même avec 0,5 mm de bruit sur le capteur externe, parce que des centaines de points sont moyennés. L'erreur de rayon due à l'échelle est fortement réduite.
2. **Il faut n'appliquer que l'échelle** : le recalage complet (rotation et translation) dégrade la forme (RMS de 0,28 à 0,4-0,6 mm sur conduit droit), car la partie visible est courte et presque cylindrique, donc mal contrainte en roulis et en position axiale.
3. **La dérive n'est pas corrigée** : le RMS de base (0,28 mm droit, 0,72 mm avec coudes) ne bouge pas. Le recalage final ne règle que l'échelle.
4. **Réserve importante** : j'ai simulé un bruit aléatoire, pas un **biais systématique** du capteur externe (peau, concavités, multi-trajets d'un ToF). Un biais radial de 0,1 mm donnerait environ 2,5 % d'erreur d'échelle pour un rayon de 4 mm (estimation simple), soit l'ordre de grandeur de l'erreur qu'on veut corriger. La qualité réelle du capteur externe est le point à mesurer.

**Conclusion** : l'idée sert bien de contrôle d'échelle, à condition d'avoir un capteur externe précis. Son plus grand intérêt est un usage continu (capteur qui voit l'oreille et la poignée de la sonde) : c'est le suivi externe T3, seule configuration qui tient le budget en 6.

### 7.3 Otoscopes USB bas coût et photogrammétrie libre (type OpenScan)
- **OpenScan** est un projet libre de numérisation par photogrammétrie d'**objets posés sur un plateau tournant**, la caméra tournant autour. C'est une vue de l'extérieur : il ne convient pas à l'intérieur d'un conduit. Il pourrait servir pour scanner le **pavillon** de l'oreille avec plusieurs caméras, en pratique difficile sur un patient (mouvement, durée).
- Les logiciels de photogrammétrie libres (COLMAP, Meshroom, OpenSfM) peuvent traiter des images d'otoscope.
- **Otoscopes USB bas coût** : utiles pour une **expérience rapide**, pas comme base du produit. Caractéristiques habituelles à vérifier sur le modèle choisi : pointe de 4 à 6 mm, vidéo 720p à 1080p, mise au point fixe, auto-exposition, éclairage LED non réglable, pas d'horodatage matériel, champ souvent étroit (vers l'avant, pas panoramique). Ils ne permettent ni l'anneau laser, ni la synchronisation à 0,5 ms exigée en R4, ni un étalonnage fiable sans travail.
- **Protocole détaillé** : `docs/protocole-experience-otoscope-colmap.md` (fantômes générés par `tools/photogrammetrie/exporter_fantome.py`, analyse par `tools/photogrammetrie/analyse_colmap.py`).
- **Expérience proposée** : filmer un fantôme d'oreille en silicone de géométrie connue avec un otoscope bas coût, traiter la vidéo avec COLMAP, et mesurer (a) si la reconstruction fonctionne dans ce milieu peu texturé, (b) la forme et la dérive d'échelle par rapport au fantôme. Cela teste directement l'hypothèse de l'odométrie visuelle (option V), à faible coût. Fantômes d'abord ; tout essai sur une personne demande consentement et cadre éthique.

## 8. Retrait motorisé et sonde auto-centrée

### 8.1 Idée
Automatiser le retrait : l'opérateur place la sonde à la profondeur voulue (insertion manuelle), puis un moteur la retire à vitesse constante pendant le scan, avec arrêt automatique. Comparaison avec un retrait IVUS (« pullback »). Le moteur ne fait que **retirer** (jamais pousser vers le tympan) : c'est le sens le plus sûr.

### 8.2 Ce que le simulateur indique
Le simulateur ne modélise pas la mécanique : j'ai représenté une sonde motorisée **auto-centrée** par un décentrage latéral de 0,05 mm (au lieu de 0,3 mm), une inclinaison de 0,3° (au lieu de 2°) et une vitesse constante de 3 mm/s. Tête mobile (1,5 mm et 1,5°), compensée par un gyroscope sur la tête (pas de clip ni de suivi externe). Conduit avec coudes, 4 graines. Résultats : `tools/simulation/resultats_sonde_motorisee.txt`.

| Cas | Suivi du centre, axe par codeur (RMS, mm) | Fusion avec suivi externe et clip (mm) |
|---|---|---|
| Main libre | 0,246 | 0,122 |
| **Sonde motorisée auto-centrée** | **0,100** | 0,119 |
| Idem, gyroscope 10 fois meilleur | 0,094 | 0,119 |

Attribution (suivi du centre seul, même conduit et même tête mobile) :

| Changement par rapport à la main libre | RMS (mm) |
|---|---|
| Vitesse constante de 3 mm/s seule | 0,269 (aucun gain) |
| Inclinaison 0,3° seule | 0,214 |
| Décentrage 0,05 mm seul | 0,164 |
| Décentrage 0,05 mm + inclinaison 0,3° (vitesse libre, 5 mm/s) | 0,104 |

Lecture :
1. **Ce qui fait gagner de la précision, c'est que la sonde reste centrée et alignée sur le conduit, pas que sa vitesse soit constante.** Le moteur seul ne change rien ; il n'est utile que s'il s'accompagne d'un guidage ou d'un centrage mécanique.
2. Avec ce centrage, le suivi du centre de la lumière **atteint le budget nominal (0,10 mm) sans suivi externe ni clip**, la tête étant compensée par un simple gyroscope sur la base. C'est le seul cas simulé sans suivi externe qui y parvient.
3. Le centrage peut se faire **sans moteur** (collerette ou structure auto-centrante) : le moteur apporte surtout la reproductibilité, la protection (arrêt, limite de force) et les mains libres.
4. **Hypothèse non démontrée** : j'ai supposé qu'on obtient 0,05 mm de décentrage et 0,3° d'inclinaison. Aucune conception mécanique ne le garantit ; c'est le point à prouver sur banc.
5. **Non modélisé** : la **déformation du conduit par le contact** (le conduit est souple ; une collerette ou une gaine en contact peut le dilater de plusieurs dixièmes de millimètre, comme le fait une empreinte au silicone, que l'Otoscan évite en restant sans contact), le confort et l'hygiène (gaine à usage unique), les frottements dans les coudes, la mâchoire.

### 8.3 Avantages et inconvénients

| | Avantages | Inconvénients |
|---|---|---|
| Moteur de retrait | Reproductible, mains libres, retrait seul (sens sûr), arrêt automatique et limite de force, durée courte et constante | Dispositif actif au contact du patient (dossier de sécurité plus lourd), coût et complexité, risques d'accrochage |
| Centrage mécanique | Alignement sur le conduit (gain principal), suivi plus simple | Risque de contact et de déformation de la paroi, adaptation aux tailles, usage unique |
| Ancrage de la base dans la concha | Repère lié à l'oreille : moins besoin de clip et de suivi externe | Fixation rigide à prouver (le glissement du clip dominait l'erreur) |

### 8.4 Avis
Intéressant, mais **ce n'est pas le moteur qui compte, c'est le centrage et l'ancrage**. Proposition :
1. **Phase 1 : un retrait motorisé sur banc**, comme instrument de référence pour les fantômes (il en faut un de toute façon pour valider), sans en faire encore un choix de produit.
2. **Concevoir et tester des centrages passifs** (collerette souple, trois points de contact, gaine) sur fantômes souples : mesurer le décentrage et l'inclinaison obtenus, et la déformation de la paroi.
3. **Décider du moteur plus tard**, selon les gains réels et le surcoût réglementaire d'un dispositif actif.
4. Étudier un **ancrage de la base sur l'oreille** (type bouchon de concha) pour un repère mécanique, en comparaison du suivi externe avec clip.

## 9. Prochaines étapes de conception
1. **Simulateur** : version 0.1 faite (sections 6 et 7.2) ; à améliorer (estimateur par fenêtre glissante, coudes réalistes, mâchoire, occultation, biais systématique du capteur externe).
1bis. **Expériences bas coût** : otoscope USB et COLMAP sur fantôme (7.3) ; mesure de la précision d'un capteur 3D externe candidat sur fantôme d'oreille.
2. **Banc optique tête A** : choix du module caméra (résolution, cadence, champ), du laser vert 520 nm, du miroir conique, mesure de la résolution réelle.
3. **Nomenclature des composants et fournisseurs** (caméras 1 mm, lasers, cônes ou DOE, gyroscope), en tenant compte du lieu de développement (Chine).
4. **Mise à jour de la spécification** (§4.1 et §4.2) après validation des propositions de la section 3.
5. **Étude de la tête B** (motif codé) : mêmes calculs de géométrie et de précision.
