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
- Le point critique est la **datation** : une erreur de 1 ms à 50 mm/s de mouvement relatif donne 0,05 mm. Exigence proposée : horodatage matériel commun caméra, laser, gyroscope et suivi, avec un décalage résiduel ≤ 0,5 ms.

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

### Ce que ces résultats indiquent
1. **Le contrôle du simulateur est correct** : avec les poses vraies, l'erreur vaut le bruit de mesure (0,019 mm).
2. **Le recalage de surface seul ne donne pas la longueur** : l'axe dérive de 4 à 5 mm sur 24 mm (environ 18 %), conduit conique ou non. Confirme R1 pour l'axe.
3. **Une source d'axe suffit pour la longueur** : codeur (E) ou odométrie visuelle (V, sous mes hypothèses de bruit) ramènent l'erreur axiale à 0,1-0,5 mm.
4. **Mais l'axe n'est pas le principal problème.** Avec un axe parfait (E), l'estimation latérale par recalage de l'anneau dérive encore : 0,2 mm RMS sur conduit droit, **0,7 mm avec coudes**. Cela dépasse le budget scanner (0,10 mm nominal, seuil Go 0,15 mm). Correction de mon analyse R1, qui insistait sur l'axe : sur la forme, c'est la dérive latérale et celle de l'orientation dans les coudes qui domine.
5. **Le suivi externe (T) donne 0,075 mm dans tous les conduits, coudes compris**, sous des hypothèses d'étalonnage que le banc devra confirmer. C'est la seule configuration dans le budget.
6. **Sensibilités** : biais du gyroscope multiplié par 10 (0,5 °/s) : orientation finale 3,6° au lieu de 0,45°, surface 0,26 mm au lieu de 0,21 mm sur conduit droit (effet modéré, le recalage absorbe une partie). Inclinaison de la sonde de 0° à 2° : aucun effet notable sur la dérive.

### Limites importantes de ce simulateur
- **L'estimateur de E, V et I est simple** (recalage de chaque anneau sur la moyenne des quatre précédents). Les modèles qui extrapolent le long de l'axe (ordre 1 ou 2) sont instables dans mes essais. Une optimisation sur fenêtre glissante avec contraintes de lissage fera probablement mieux : **le résultat 0,7 mm avec coudes est une limite de cet estimateur, pas une limite démontrée de la méthode.**
- Conduit synthétique (coudes, conicité, ellipticité choisis par hypothèse), bruits gaussiens, pas de cérumen, de reflets, de mouvement de mâchoire ni d'occultation du suivi.
- Les valeurs de V (odométrie visuelle) et de T (suivi externe) sont des hypothèses de ma part ; la faisabilité réelle de V dépend de la texture des images, à tester.

### Conséquences pour la conception
- **La spécification (§4.2 « IMU + ICP ») est insuffisante** : à retenir pour la mise à jour de la spécification.
- **Le banc de la phase 1 ne peut pas se limiter à un codeur linéaire** si les fantômes ont des coudes : il faut une référence de pose en 6 degrés de liberté (bras motorisé, table à plusieurs axes ou suivi externe de référence).
- **Le suivi externe de la poignée (option T3 du plan) devient la base de référence** pour la phase 1 ; l'odométrie visuelle et un meilleur estimateur restent des pistes à comparer, avec comme question : quelle erreur latérale atteint-on dans des coudes ?
- Prochaines étapes pour le simulateur : estimateur par fenêtre glissante, coudes plus réalistes (rayon de courbure mesuré), mouvement de mâchoire, occultation du suivi, puis comparaison avec des données réelles du banc.

## 7. Prochaines étapes de conception
1. **Simulateur** : version 0.1 faite (section 6) ; à améliorer (estimateur par fenêtre glissante, coudes réalistes, mâchoire, occultation).
2. **Banc optique tête A** : choix du module caméra (résolution, cadence, champ), du laser vert 520 nm, du miroir conique, mesure de la résolution réelle.
3. **Nomenclature des composants et fournisseurs** (caméras 1 mm, lasers, cônes ou DOE, gyroscope), en tenant compte du lieu de développement (Chine).
4. **Mise à jour de la spécification** (§4.1 et §4.2) après validation des propositions de la section 3.
5. **Étude de la tête B** (motif codé) : mêmes calculs de géométrie et de précision.
