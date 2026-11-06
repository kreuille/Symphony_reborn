# Plan du banc de phase 1 : du simulateur à la mesure

Version 0.1 (brouillon, 6 novembre 2026). Complète `specs/scanner-spec-prototype.md` (v0.4), qui fait foi pour les exigences, et `docs/conception-scanner.md` (calculs et simulations). **Aucun coût n'est chiffré** (décision 7 de `DECISIONS.md`) ; les valeurs numériques ci-dessous sont des cibles de départ issues des simulations, à confirmer par les mesures.

## 1. Objectif
Remplacer les **hypothèses** du simulateur par des **mesures**, afin de choisir l'architecture de pose et de centrage avant le pilote. En 12 semaines, sur fantômes uniquement, décider entre :
- **(a)** suivi externe + gyroscopes + fusion en main libre (référence et repli) ;
- **(b)** retrait motorisé centré sans suivi externe ;
- **(c)** retrait motorisé centré + suivi externe en fusion adaptative (option produit prioritaire, décision 12).

## 2. Hypothèses du simulateur à mesurer

| Hypothèse (valeur simulée) | Où elle pèse | Essai qui la mesure |
|---|---|---|
| Bruit du suivi externe 0,04 mm par image ; erreur main-pointe 0,05 mm ; dérive 0,03 mm | Suivi externe (0,075 mm tête immobile) | T9 |
| Latence du suivi de 30 ms, connue à ±5 ms | Désynchronisation | T9 |
| Glissement du clip sur l'oreille 0,1 mm (0,3 mm dégrade fortement) | Tête mobile | T10 |
| Biais du gyroscope 0,05 °/s | Orientation, courbure | T1 (banc gyroscope, voir 4) |
| Dérive du suivi du centre (0,01 à 0,03 mm par image) | Fusion adaptative | T4, T5 sur fantôme à coudes |
| Décentrage 0,05 mm et inclinaison 0,3° d'un retrait centré | Option (b) et (c) | T11 |
| Raideur radiale du conduit k_t (0,5 à 2 N/mm, non mesurée) | Centrage au contact | T11 (fantômes souples) |
| Odométrie visuelle : 10 µm par image, 0,3 % d'échelle | Axe en main libre | T12 |
| Indépendance de l'opérateur (P9) | Valeur de l'automatisation | T13 |

## 3. Matériel du banc (sans prix)

| Poste | Fonction | Exigence de départ |
|---|---|---|
| **Référence de pose à 6 degrés de liberté** (bras robotisé, table multi-axes ou suivi de référence) | Vérité terrain de la position et de l'orientation de la sonde, y compris dans des fantômes à coudes | résolution de position ≤ 0,02 mm, répétabilité à mesurer ; interface d'horodatage |
| **Retrait motorisé** (axe linéaire, éventuellement un axe de vos imprimantes) | Retrait à vitesse constante de 2,5 à 10 mm/s sur au moins 30 mm, arrêt automatique, mesure de la force | course ≥ 30 mm ; mesure de force ; position codée |
| **Suivi externe** (caméras fixes avec repères, ou capteur 3D) et **clip** à plusieurs versions | Pose de la poignée et de l'oreille | à qualifier en T9 ; au moins deux variantes de clip |
| **Gyroscopes** (sonde et tête) et centrale d'horodatage | Orientation, courbure | 6 axes ≥ 200 Hz, horodatés ; caractérisation de dérive |
| **Têtes optiques A et B** (caméra miniature, laser 520 nm et option 450 nm, cône ou DOE, fenêtre transparente) | Mesure du conduit | base B de 3 à 4 mm, champ de 115 à 130°, cadence ≥ 60 images/s |
| **Fantômes** (`tools/photogrammetrie/exporter_fantome.py`) : droit conique, presque cylindrique, avec deux coudes ; versions rigides et **souples** (silicone, noyau moulé) ; calibres de 6, 8 et 10 mm | Mesures de forme, de centrage et de raideur | surfaces lisse, mouchetée et teintée ; diamètres contrôlés aux jauges |
| **Support de fantôme mobile** | Simuler le mouvement de la tête (T10) | amplitude réglable de 1,5 à 3 mm et degrés |
| **Référence de mesure de forme** (tomographie, scanner industriel ou machine à mesurer) | Vérité terrain de la forme | incertitude ≤ 0,02 mm sur le fantôme |
| **Mesure de raideur** (indentation avec capteur de force sur fantômes souples, puis méthode adaptée sur sujets avec cadre éthique) | k_t et déformation de la paroi | à définir |
| **Otoscope USB bas coût** (2 modèles) et logiciel de photogrammétrie libre | T12 | selon `docs/protocole-experience-otoscope-colmap.md` |
| **Poste de calcul** et chaîne logicielle (acquisition, simulateur, scripts d'analyse du dépôt) | Acquisition et analyse | horodatage commun |

## 4. Ordre des essais et dépendances

| Semaine | Essais | Pourquoi à ce moment |
|---|---|---|
| 1–2 | Réception du matériel, impression et contrôle des fantômes, mise en place de la **référence de pose** et de l'horodatage commun ; **T1** (étalonnage de la tête A) en préparation | Tout le reste dépend de la référence et du temps commun |
| 2–4 | **T12** (otoscope USB et photogrammétrie, bon marché, rapide) ; caractérisation des gyroscopes (dérive, biais) | Informe tôt l'option « odométrie visuelle » |
| 3–5 | Tête A : montage, **T1, T2, T3** (justesse sur calibres et fantômes, sonde sur banc motorisé) ; **T9** (qualité du suivi externe) | Valide la mesure de forme avant la pose |
| 4–7 | Tête B : montage, motif et décodage | En parallèle |
| 5–9 | **T11** (décentrage, inclinaison et déformation avec retrait motorisé et centrage ; mesure de k_t sur fantômes souples) | Décide de l'option (b) ou (c) |
| 6–8 | **T10** (mouvement de la tête, clip) ; **T4, T5** (scan manuel puis répétabilité, avec référence de pose) | Mesure la dérive du suivi du centre et le glissement du clip |
| 6–9 | Logiciel : pose, fusion (gain fixe puis filtre adaptatif), TSDF, export ; remise à jour du simulateur avec les valeurs mesurées | Calcule le résultat final avec des valeurs réelles |
| 9–11 | **T6** (conditions difficiles), **T7** (tête A contre tête B), **T8** (impression sur machine à capsules), **T13** (indépendance de l'opérateur, retrait manuel contre motorisé) | Campagne finale |
| 12 | Rapport, décision Go / No-Go de phase 1 | Fin de phase |

## 5. Mesures et décisions

| Essai | Mesure | Seuil de départ | Si le seuil est tenu | Sinon |
|---|---|---|---|---|
| T9 | Bruit, erreur main-pointe, dérive, latence du suivi externe | bruit ≤ 0,04 mm ; main-pointe ≤ 0,05 mm ; latence connue à ±5 ms | Suivi externe retenu (options a et c) | Changer de capteur ou de repères ; sinon option (b) seule |
| T10 | Glissement du clip, erreur de pose tête mobile | glissement ≤ 0,1 mm ; erreur ≤ 0,15 mm RMS | Clip retenu | Suivi de l'oreille sans clip, ou option (b) |
| T11 | Décentrage, inclinaison, déformation de la paroi, k_t | décentrage ≤ 0,05 mm ; inclinaison ≤ 0,5° ; déformation ≤ 0,05 mm | Options (b) et (c) viables | Option (a) seule ; revoir le centrage actif |
| T12 | Recalage d'images, dérive d'échelle de l'odométrie visuelle | critères du protocole | Axe en main libre par odométrie visuelle | Axe par suivi externe |
| T13 | Taux de scans complets du premier coup, écart du RMS entre opérateurs | ≥ 90 % ; ≤ 0,03 mm | Valeur de l'automatisation démontrée | Revoir le geste ou le guidage |
| T3, T4, T5 | Justesse (RMS), répétabilité, scan manuel | P2 ≤ 0,10 mm ; Go ≤ 0,15 mm | Voir la spécification | Voir la spécification |

**Lecture finale** : avec les valeurs mesurées, relancer `tools/simulation/` (suivi seul, centre seul, fusion adaptative, hybride) et trancher entre (a), (b) et (c). Le rapport de fin de phase donne une valeur mesurée pour chaque ligne de la section 2.

## 6. Formats et traçabilité des données
- Horodatage commun de tous les flux (images, gyroscopes, suivi externe, banc, force) et latence mesurée à chaque session.
- Un dossier par essai : données brutes, paramètres du banc, étalonnage, conditions, incident éventuel ; format ouvert (CSV, PLY, STL, JSON).
- Scripts d'analyse versionnés dans le dépôt (`tools/`), résultats dans `docs/` et `tools/simulation/`.
- Contrôle d'étalonnage au début de chaque session.

## 7. Risques propres au banc

| Risque | Parade |
|---|---|
| La référence de pose n'est pas assez précise ou pas assez rapide | La qualifier d'abord (répétabilité, latence) ; sinon passer à un moyen plus précis |
| Fantômes imprimés imprécis ou à stries qui servent de fausse texture | Contrôle aux jauges, ponçage, silicone moulé pour les versions souples |
| Désynchronisation entre flux | Horodatage matériel commun, test de synchronisation en début de session |
| La sonde ne passe pas les coudes des fantômes | Essais préalables sur fantôme rigide transparent, longueur de la fenêtre transparente |
| Le centrage au contact déforme les fantômes souples d'une façon qui ne représente pas le conduit réel | Ne tirer de conclusion sur k_t qu'avec une mesure sur tissu réel, dans un cadre éthique adapté |
| Trop d'options en parallèle | Respecter l'ordre du tableau ; décider de laisser tomber une option dès qu'un seuil est manqué |

## 8. Livrables
1. Banc opérationnel et documenté (plans, étalonnages, procédures).
2. Jeu de données de tous les essais, avec métadonnées.
3. Rapport de phase 1 : une valeur mesurée pour chaque hypothèse de la section 2 et la décision (a), (b) ou (c).
4. Simulateur recalé sur les valeurs mesurées.
5. Spécification du scanner mise à jour (v0.5) pour la phase 2.

## 9. Premiers 15 jours
1. Fixer l'équipe (mixte, interne et externe, développement en Chine) et le responsable du banc.
2. Choisir et commander la référence de pose, le suivi externe, les gyroscopes, le retrait motorisé et les têtes optiques.
3. Imprimer les premiers fantômes (rigides) et lancer le moulage de fantômes souples.
4. Lancer **T12** (otoscope USB, quelques jours) pour avoir très tôt une première valeur sur l'odométrie visuelle.
5. Établir l'horodatage commun et qualifier la référence de pose.
6. Prévoir dès maintenant le cadre éthique de toute mesure de raideur sur sujets (points ouverts de `DECISIONS.md`).
