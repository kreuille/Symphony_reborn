# Plan de développement du scanner 3D intra-auriculaire

**Principe** : le scanner est la pièce maîtresse de la solution. Ce plan organise son développement de façon à lever d'abord le risque principal (le suivi de pose), à avancer sur le logiciel avant que le matériel existe, et à décider par critères chiffrés.

**Cohérence avec le dépôt** : ce plan complète `specs/scanner-spec-prototype.md` et `specs/scanner-plan-pilote.md` et respecte `DECISIONS.md` : budget d'erreur de la chaîne de 0,2 mm RMS (scanner : 0,10 nominal, seuil Go 0,15), impression sur machines à capsules SprintRay, étude FTO lancée le 5 novembre 2026 (décision 4 mise à jour), revue obligatoire à la gate M5, aucun budget chiffré avant la phase 0. Les durées et seuils ci-dessous sont des **hypothèses de travail** ; en cas de divergence, la spécification et le calendrier maître font foi.

## 1. Cibles de performance (hypothèses)

Les valeurs de l'Otoscan (voir `etude-otoscan.md`) servent de repère. **Attention : le budget d'erreur de notre chaîne (scanner 0,10 mm RMS nominal, seuil Go 0,15) est environ quatre fois plus strict que l'écart-type publié de l'Otoscan (0,415 mm, mesuré sur une méthode différente).** Il faut donc d'abord vérifier que les deux mesures sont comparables, et ne pas se contenter de « faire aussi bien que l'Otoscan ».

| Critère | Cible phase 1 (fantômes) | Référence |
|---|---|---|
| Erreur RMS du scanner vs référence | seuil Go 0,15 mm ; nominal 0,10 mm (`DECISIONS.md`) | Otoscan : écart-type 0,415 mm, biais -0,05 mm (méthode différente) |
| Durée de scan par oreille | ≤ 2 min (hypothèse) | Otoscan : 2 à 6 min |
| Couverture | jusqu'au 2ᵉ coude + 4-6 mm | Otoscan : même exigence |
| Scans complets du premier coup | ≥ 90 % (hypothèse) | Otoscan : 70 % (revendiqué) |
| Diamètre de pointe | à fixer d'après données anatomiques ; indicatif ≤ 4-5 mm | à valider |
| Sécurité | alerte de profondeur, arrêt automatique | brevet US 8,900,130 (à examiner à la revue M5) |

## 2. Décision structurante : comment connaître la position de la sonde

Un anneau laser ne donne qu'une tranche à la fois. Tout l'assemblage dépend de la pose de la sonde. Dans un conduit quasi cylindrique, le recalage par surface (ICP) est peu contraint le long de l'axe : le glissement n'est pas détecté. C'est pourquoi l'Otoscan s'appuie sur un suivi externe.

| Option | Principe | Atouts | Risques |
|---|---|---|---|
| **T1 – Repères sur la tête, caméras sur la sonde** | Approche Otoscan : casque à repères, caméras de suivi dans la sonde | Éprouvée, précise | Brevets probables (FTO), encombrement, sonde plus lourde |
| **T2 – Inertiel-visuel sans casque** | IMU + morceaux de surface (motif codé, architecture B) + recalage + IA | Léger, très différenciant, brevetable | Dérive, ambiguïté le long de l'axe : à prouver |
| **T3 – Suivi externe de la poignée** | Caméra(s) fixes voient des repères sur la poignée ; la sonde est rigide donc pointe = pose de la poignée × décalage connu ; clip léger sur l'oreille pour compenser la tête | Sonde simple et légère, matériel peu coûteux | Occultation de la poignée, étalonnage de l'ensemble |
| **T4 – Retrait motorisé** | Gaine souple, encodeur : mouvement 1D connu, comme un IVUS | Position axiale précise | Confort et sécurité, mécanique lourde ; non prioritaire |

**Mise à jour après calculs** (`conception-scanner.md`) : sur une paroi lisse, le recalage par surface ne contraint ni l'axe, ni l'inclinaison, ni le roulis, que ce soit avec un anneau ou avec un morceau de surface (tête B) ; l'accéléromètre ne peut pas fournir l'axe. L'orientation doit venir du gyroscope et l'axe d'une source à trancher par essais (odométrie visuelle, suivi externe de la poignée). La recommandation ci-dessous est à lire avec cette réserve. **Le simulateur de pose (`conception-scanner.md`, section 6) renforce T3 :** le suivi externe de la poignée est la seule option qui tient le budget d'erreur (0,075 mm RMS) dans tous les conduits simulés, alors qu'un recalage de surface avec axe parfait dérive de 0,2 mm (conduit droit) à 0,7 mm (coudes). Un estimateur qui suit le centre de la lumière avec la courbure du gyroscope ramène l'erreur à 0,25 mm avec coudes : mieux, mais au-dessus du seuil Go de 0,15 mm. La **fusion** du suivi externe, du gyroscope et du suivi du centre garde 0,08 mm en nominal et passe de 0,15 à 0,11 mm quand le suivi est masqué ou dégradé. Une latence du suivi de 30 ms non compensée coûte environ 0,015 mm avec un mouvement de main lisse (0,06 mm avec un mouvement saccadé pour le suivi seul, 0,013 mm pour la fusion) : la latence doit être mesurée, pas forcément supprimée. Un **retrait motorisé avec centrage mécanique** (option produit prioritaire depuis le 6 novembre 2026, décision 12, pour réduire l'erreur de manipulation) amène le suivi du centre à 0,10 mm sans suivi externe dans le simulateur (et à 0,06 à 0,10 mm combiné au suivi externe par fusion adaptative de type Kalman, sections 8.8 et 8.9), mais le gain vient du centrage, pas de la vitesse constante (`conception-scanner.md`, section 8) ; hypothèse à prouver sur banc ; avec un centrage au contact, la déformation de la paroi ramène le meilleur cas simulé à 0,14 mm (0,23 mm avec un tissu mou), au-dessus du nominal. **Le mouvement de la tête impose de suivre l'oreille** (clip rigide ou suivi sans clip) : sans cela le suivi externe seul est à 1,4 mm d'erreur ; avec un clip qui glisse de 0,1 mm, la fusion donne 0,12 mm, et 0,30 mm avec 0,3 mm de glissement.

**Recommandation** :
1. **Simuler d'abord T2** (semaines 1 à 4) : si la simulation montre une ambiguïté axiale non résoluble, on le sait avant d'avoir dépensé en matériel.
2. **Construire T3 comme référence de repli** : le plus rapide à rendre fonctionnel.
3. T1 sert seulement de comparaison ; son recours dépendra de la revue brevets de la gate M5 et des résultats de l'étude FTO. T4 est écarté de la phase 1.
4. Une combinaison T2 + repère externe léger est probablement la solution finale.

## 3. Lots de travail

| Lot | Contenu | Livrable |
|---|---|---|
| **WP1 Optique** | Tête de mesure : source laser (anneau via cône ou DOE), caméra miniature, objectif grand angle, filtre, mise au point ; budget optique et miniaturisation ; étude de la longueur d'onde (contraste sur peau, cérumen, sécurité) | Têtes optiques v0 (banc) puis v1 (pointe réelle) |
| **WP2 Électronique et embarqué** | Caméra, laser pulsé synchronisé à la cadence (alternance vidéo / mesure), IMU, interface USB, alimentation, sécurité laser (limiteur matériel) | Carte de contrôle et firmware |
| **WP3 Mécanique et ergonomie** | Sonde, poignée, gâchette, embouts jetables ou nettoyables, repères de suivi, support, clip d'oreille | Prototypes imprimés puis usinés |
| **WP4 Étalonnage** | Optique (distorsion), triangulation (table pixel → coordonnées), main-œil (pointe vs poignée), temps ; procédure automatisée en production | Banc et procédure d'étalonnage |
| **WP5 Reconstruction 3D** | Détection de la trace, nuage de points, pose, fusion (TSDF), détection des trous, maillage propre, contrôle de complétude, export STL | Bibliothèque et application de scan |
| **WP6 IA** | Filtrage des aberrations (reflets, cérumen, poils), estimation de pose assistée, estimation de profondeur et alerte tympan, modèle statistique d'oreille | Modèles entraînés sur simulation puis données réelles |
| **WP7 Validation** | Fantômes, banc de référence, protocole de mesure, critères Go/No-Go | Rapports de validation |
| **WP8 Qualité et réglementaire** | Dossier technique dès le départ : gestion des risques, sécurité laser, électrique, biocompatibilité, utilisabilité | Plan réglementaire et dossier évolutif |

Normes à examiner avec un expert (à confirmer selon le marché) : ISO 14971 (gestion des risques), IEC 60825-1 (laser), IEC 60601-1 (sécurité électrique), ISO 10993 (biocompatibilité), IEC 62366 (utilisabilité), IEC 62304 (logiciel).

## 4. Stratégie de développement

1. **Simulation d'abord.** Un simulateur (rendu d'une sonde virtuelle dans des conduits 3D) génère des images laser avec vérité terrain. On y développe et on compare les options de suivi, la reconstruction et l'IA **avant** le matériel. Source de formes : modèles de conduits publics ou générés, puis premiers scans réels.
2. **Fantômes imprimés dans vos imprimantes.** Conduits aux deux coudes, diamètres variés, surfaces de réflectance différente, versions souples (silicone). Un avantage direct de votre métier. La précision du fantôme lui-même doit être mesurée.
3. **Banc de référence.** Mesure du fantôme par un moyen métrologique (scanner de table, tomographie ou machine à mesurer) pour obtenir la vérité terrain.
4. **Itérations courtes.** Têtes optiques sur banc fixe (sans main) pour valider la triangulation, puis sonde manuelle avec suivi.
5. **Acheter avant de développer.** Modules de caméra miniature (classe 1 mm), diodes laser, IMU, éléments diffractifs, bibliothèques open source de traitement 3D. Candidats à vérifier avec les fournisseurs de Shenzhen ; ne rien figer avant les tests.
6. **Protéger au fil de l'eau.** Brevets sur ce qui nous distingue (par exemple fusion capteurs + pose sans casque, contrôle de complétude, lien avec la CAO) avant toute divulgation.

## 5. Calendrier par jalons

| Période | Contenu | Porte de décision |
|---|---|---|
| **Mois 0** | Recrutement ou contractualisation de l'équipe ; achat du matériel de base ; veille brevets légère (les brevets de `etude-otoscan.md`), et suivi de l'étude FTO (lancée) | — |
| **M0-M3 (phase 1)** | Simulateur ; banc optique (WP1, WP4) ; fantômes ; comparaison T2 / T3 ; premier maillage de fantôme | **Porte 1** : erreur RMS sur fantômes ; choix du suivi |
| **M3-M9** (à caler sur la gate M5 : revue brevets obligatoire avant tout prototype chez un tiers) | Sonde manuelle v1 ; firmware ; reconstruction temps réel ; IA v1 ; complétude et profondeur ; fantômes souples | **Porte 2** : cibles du §1 atteintes ; mesures répétables par plusieurs opérateurs |
| **M9-M15** | Pilote laboratoires (30 à 300 oreilles) avec cadre réglementaire défini ; collecte pour l'IA ; interface avec la CAO automatique | **Porte 3** : comparaison au silicone ; taux de remake |
| **M15-M24** | Version industrialisable ; étalonnage de production ; dossier réglementaire | **Porte 4** : décision de lancement industriel |

Le calendrier est indicatif : les gates du calendrier maître (`docs/calendrier-maitre.xlsx`) font foi ; les portes ci-dessus sont des jalons internes au scanner.

## 6. Équipe (hypothèse)

| Rôle | Charge |
|---|---|
| Ingénieur optique (triangulation, miniaturisation) | 1 |
| Ingénieur électronique / embarqué | 1 |
| Ingénieur vision 3D / reconstruction | 1 à 2 |
| Ingénieur IA (simulation, modèles) | 1 |
| Ingénieur mécanique / design industriel | 1 |
| Responsable qualité et réglementaire (temps partiel au début) | 0,5 |
| Chef de projet technique (vous, ou à nommer) | 1 |

Environ 6 à 8 personnes à pleine charge. Les ingénieurs en Chine réduisent fortement le coût ; un expert extérieur en optique ou en vision 3D médicale peut accélérer la phase 1.

**Budget** : non chiffré à ce stade (décision 7 de `DECISIONS.md`) ; montants à remettre après la phase 0, à partir de coûts réels. L'effectif ci-dessus est une hypothèse à rapprocher des 17 à 25 ETP du plan complet.

## 7. Risques principaux

| Risque | Réponse |
|---|---|
| Suivi de pose imprécis ou dérivant | Simulation en premier ; T3 en repli ; critères de porte 1 |
| Brevets bloquants (anneau laser, suivi, caméra grand angle) | Étude FTO lancée (décision 4) ; revue obligatoire à la gate M5 ; contournement de conception ; veille |
| Miniaturisation (capteur, optique, laser dans une pointe fine) | Banc d'abord, pointe réelle ensuite ; plusieurs fournisseurs de modules |
| Reflets, cérumen, poils, humidité | Longueur d'onde et filtrage ; IA ; contre-indications ; scénarios dans les fantômes |
| Mouvement du patient (tête, mâchoire) | Clip de compensation ; scans mâchoire ouverte et fermée au début |
| Sécurité (profondeur, laser, force d'appui) | Alerte et arrêt automatiques ; limiteur matériel ; analyse de risques dès le départ |
| Données insuffisantes pour l'IA | Simulation massive ; collecte planifiée dans le pilote |
| Réglementaire | Expert dès la phase 1 ; dispositif de référence à identifier |

## 8. Premiers 30 jours

1. Commander l'étude FTO (cahier des charges prêt, brevets de `etude-otoscan.md` en tête de liste) : choisir le cabinet, signer le NDA, envoyer l'architecture sans détails d'invention non déposée.
2. Définir précisément la cible (cahier des charges produit : taille de pointe, type d'appareils visés, utilisateur).
3. Construire le simulateur minimal : sonde virtuelle, conduit 3D, image laser, vérité terrain.
4. Commander le matériel du banc : modules caméra, diodes laser, éléments diffractifs ou cônes, IMU, platines de translation et rotation.
5. Imprimer les premiers fantômes (3 formes anatomiques) et les mesurer.
6. Chercher l'ingénieur optique et l'ingénieur vision 3D (ou un bureau d'études partenaire).
7. Valider avec un expert en dispositifs médicaux le statut réglementaire probable.

## 9. Décisions prises le 5 novembre 2026 et suites

| Question | Réponse | Conséquence pour le plan |
|---|---|---|
| Équipe | Mixte : interne et externe | Garder en interne ce qui fait la différence (reconstruction 3D, IA, intégration) ; externaliser l'optique miniature, l'électronique et la mécanique si le recrutement est lent ; fixer les rôles |
| Lieu | Chine | Fournisseurs de modules caméra, diodes laser, optique et prototypage en local ; recrutement local ; vigilance sur la propriété intellectuelle et sur le cadre de données |
| Pièces visées | Toutes | Cible de couverture jusqu'au 2ᵉ coude (ITE/IIC) à tenir dès la phase 1 |
| Enveloppe phase 1 | Pas définie | Pas de chiffre ; à établir après la phase 0 sur devis réels |
| FTO | Go | Lancer maintenant (voir §8, étape 1) |

Restent à décider : le cabinet FTO (compétence en Chine, UE et US), le bureau d'études externe pour l'optique, la répartition précise interne / externe, et la liste des pièces à valider en premier au pilote.
