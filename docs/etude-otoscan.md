# Étude de référence : conception et fonctionnement de l'Otoscan

**Statut** : synthèse de sources publiques fournie par le demandeur, non vérifiée de façon indépendante. Elle sert de référence concurrentielle et de point de départ pour l'étude FTO.

**Limite essentielle** : aucune documentation technique publique de Natus (ni fiche de spécifications, ni manuel) n'a été trouvée. Les sources se répartissent en deux familles :
- **Sur l'Otoscan lui-même** : Q&R de 2014 avec le chef de produit, cours de formation continue Otometrics (2019), articles sur la conception du casque et du logiciel.
- **Brevets de la famille United Sciences / 3DM Systems** (dépôts de 2012, inventeur Karol Hatzilias), que le cours de 2019 cite comme origine de la technologie. Aucun brevet ne nomme Otometrics ni Natus comme titulaire.

Les détails optiques viennent donc des brevets : ils décrivent très probablement la lignée technologique de l'Otoscan, sans que ce soit confirmé.

## 1. Architecture matérielle (établie pour l'Otoscan)

| Élément | Rôle |
|---|---|
| Sonde manuelle | Rangée dans un support, connectée en USB. Gâchette contextuelle : déclenche l'action suivante affichée à l'écran (jauge de profondeur, démarrage, pause) |
| Deux caméras de suivi | De chaque côté de la sonde ; doivent voir le casque en permanence |
| Laser en anneau | Émis depuis la pointe vers l'extérieur ; modes « Canal Ring » (conduit) et « Concha Ring » (parties courbes du pavillon) |
| Laser en ligne | Émis devant la pointe, comme un lecteur de code-barres ; mode « Pinna Line » (zones plates) |
| Mini-caméra dans la pointe | Filme la trace du laser sur la peau |
| Casque de suivi | Anneau de repères (points et tirets imprimés) autour de chaque oreille |
| PC dédié | Portable verrouillé, mono-application, forte charge GPU pendant le scan |
| Cloud (Otocloud) | Stockage et commande |

- **Casque** : doit rester fixe malgré les mouvements de tête et de mâchoire et s'adapter à toutes les têtes. Solution « flottante », découplée de la tête, posable d'une main.
- **Laser** : comparé à un pointeur (anneau) et à une caisse de supermarché (ligne). Classe laser non donnée ; déclaré sans danger, y compris avec un pacemaker.

## 2. Principe de mesure : triangulation laser (d'après les brevets)

1. **Projection** : anneau (parfois interrompu) ou éventail de lumière sur la paroi du conduit.
   - Anneau : réflecteur conique ; la rupture vient d'un masquage partiel du faisceau.
   - Éventail : lentille diffractive.
   - Laser amené par fibre optique ou diode montée dans la sonde.
2. **Capture** : objectif grand angle (environ 150° de champ dans le mode décrit).
   - Distance de mise au point conçue pour passer le deuxième coude ; lentille 60° → surface focale d'environ 6 mm.
   - Réglage par vis de mise au point.
   - Résolution visée : environ **50 µm par pixel** près de la surface focale.
3. **Du pixel au point 3D** : repérage de la crête de la trace (pixels les plus brillants : comparaison aux voisins, moyenne, image floutée, médiane à mi-hauteur) puis **table de correspondance** pixel → coordonnées, calculée une fois à l'étalonnage par triangulation (R = h·S/S′).
4. **Vidéo et laser sur le même capteur** : capteur à deux fois la cadence vidéo, laser pulsé une image sur deux (paires : vidéo en LED blanche ; impaires : mesure). Cadence de mesure de 25 à 30 images/s : déduction personnelle de l'auteur de la synthèse, non donnée par le brevet.

## 3. Suivi de position et assemblage

- Chaque image ne donne qu'une tranche annulaire en coordonnées sonde ; il faut la position de la sonde par rapport à l'oreille à chaque instant.
- **Otoscan** : les caméras de la sonde lisent l'anneau de repères du casque.
- **Brevets** : rétroréflecteurs sur clip d'oreille ou serre-tête, éclairés en infrarouge, lus par photodétecteurs sur la sonde. L'anneau imprimé et les caméras de l'Otoscan sont une variante non décrite dans ces brevets.
- **Assemblage** : transformation rigide (rotation + translation, « Tensor 1 ») du repère sonde au repère oreille, puis sommation des points en un nuage unique. **Aucun recalage de type ICP n'est décrit** : la précision dépend surtout de celle du suivi. Algorithme de calcul de pose non décrit.
- **Mouvements** : le casque suit la tête. La mâchoire est traitée par deux scans (bouche ouverte, fermée), sans correction automatique.

## 4. Complétude, profondeur, sécurité

- **Complétude** : modèle comparé aux exigences du type d'appareil (BTE : conque ; ITE : plus de conduit ; IIC : encore plus). Contour noir si données suffisantes, jaune si insuffisantes ; trous visibles.
- **Jauge de profondeur** : bleu (trop superficiel), vert (cible), rouge (alerte). Cible 16-18 mm (hommes), 14-16 mm (femmes), d'après la littérature et les recommandations HIMS. Un opérateur récemment formé dépasse le deuxième coude de 4 à 6 mm.
- **US 8,900,130 (sécurité)** : estimation de la distance sonde-tympan par statistiques de taille d'oreille ; alerte sonore ou visuelle. Ne prouve pas que l'Otoscan fait exactement cela.
- **US 8,900,127 (conformité)** : capteurs de pression entre châssis flottant et boîtier → force d'appui, puis « compliance » du conduit. Rien ne dit que l'Otoscan l'intègre.
- **Localisation du tympan** : stéréo-mouvement ou point laser parallèle à l'axe de l'objectif.

## 5. Logiciel, données, flux

- Scan guidé : jauge de profondeur, anneau dans le conduit, ligne sur le pavillon, anneau dans la conque ; reprise manuelle des zones manquantes.
- **Format** : STL seul mentionné. Question des fabricants : le scan nécessite-t-il des corrections ? (les empreintes silicone dilatent le conduit et sont corrigées, pas les scans laser.)
- **Cloud** : envoi automatique, conservation jusqu'à 5 ans, réutilisable pour plusieurs fabricants ; commande avec notes sur le portail.
- **Partenaires 2019** : ReSound, Westone, Emtech, Microsonic, Dreve, Widex (Royaume-Uni).
- **Artefacts** : poils et cérumen raisonnable ignorés ; cérumen excessif = contre-indication.

## 6. Formation, contre-indications, performances déclarées

- Formation : 27 modules en ligne (2,5 à 3 h) ; environ 5-7 patients pour être à l'aise, environ 15 pour être sûr.
- Durée : 2-3 min/oreille (2014) ; en 2019 environ 6 min pour un débutant, moins de 2 min avec l'expérience, contre environ 10 min pour le silicone.
- Contre-indications : cérumen excessif, chirurgie récente, écoulement ou infection, patient immobile impossible, toux réflexe persistante, antécédents de crises, migraines ou sensibilité aux lumières stroboscopiques.
- Population : adultes ≥ 18 ans (FDA 2019) ; pédiatrie en cours.
- **Résultats déclarés par le fabricant (2019, sans méthode ni taille d'échantillon)** : 92 % de confort bon/excellent ; 74 % préfèrent l'Otoscan au silicone ; 70 % des opérateurs atteignent la profondeur cible sans trou ; environ 8 % de remakes contre 15-20 % annoncés pour l'industrie.
- **Prix (2019)** : 12 500 $ le système, 1 250 $/an de cloud (première année offerte).
- Hygiène : « pas de consommables », « contrôle d'infection facile » ; nettoyage non détaillé.

## 7. Précision (littérature indépendante)

Étude comparant l'Otoscan (logiciel 1.7.12883.0) à deux matériaux d'empreinte :
- déviation moyenne **-0,052 mm** (scanner) contre -0,136 et -0,118 mm (matériaux, qui rétrécissent) ;
- écart-type **0,415 mm** (scanner) contre 0,496 à 0,546 mm.

Précision globale jugée comparable. Essai randomisé sur 76 adultes : pas de différence de satisfaction à 1 et 6 mois entre embouts issus d'un scan et d'une empreinte ; le scanner n'est pas nommé dans le résumé.

## 8. Inconnues

Longueur d'onde, puissance et classe des lasers ; précision du suivi et nombre de repères ; dimensions et poids de la sonde, résolution du capteur ; algorithme exact de recalage ; autres formats d'export que STL ; procédure de nettoyage ; « Otoscan Link » (aucune source).

Pour aller plus loin : étude de cas PointClear (conception du logiciel), manuel utilisateur Natus, brevet US 8,715,173 (laser en anneau et en éventail), non lus.

## 9. Enseignements pour notre projet

1. L'architecture A (anneau laser) est validée par un produit approuvé FDA, mais elle repose sur un **suivi externe** (casque + caméras).
2. Sans ICP dans leurs brevets : un anneau laser ne donne pas de relief le long de l'axe, donc le recalage par surface est peu contraint dans un conduit quasi cylindrique. Notre hypothèse « IMU + ICP + TSDF sans casque » est plus risquée qu'envisagé au départ (voir `plan-developpement-scanner.md`).
3. Les brevets US 8,900,125 à 130 et 8,715,173 (dépôts 2012) sont à placer en tête du FTO ; statut juridique et titulaire actuel à vérifier.
4. L'Otoscan livre un STL et passe par un fabricant tiers : notre différenciation est la chaîne scan → CAO automatique → impression en quelques minutes.
5. À reprendre : contrôle de complétude, jauge de profondeur, alerte tympan, contre-indications, formation opérateur.
6. Repères de performance pour nos critères Go/No-Go : écart-type ≈ 0,4 mm, biais ≈ 0,05 mm, scan ≤ 2 min, 70 % de scans complets du premier coup (revendiqué).
7. Piste réglementaire : l'Otoscan, déjà approuvé par la FDA, pourrait servir de dispositif de référence (à confirmer par un expert).

## Sources

- AudiologyOnline : Otoscan, 3D Ear Scanning (2019) – https://www.audiologyonline.com/articles/otoscan-3d-ear-scanning-future-24421
- ENT & Audiology News : Leaving an impression (2014) – https://entandaudiologynews.com/development/spotlight-on-innovation/post/leaving-an-impression-otoscan-ear-scanning-solution
- Delve : Otoscan finaliste MDEA (2019) – https://delve.com/news/otoscan-a-finalist-in-mdea-awards
- PointClear Solutions : étude de cas – https://www.casestudies.com/company/pointclear-solutions/case-study/innovative-design-and-development-make-the-first-3d-digital-ear-scanning-solution-a-reality
- US 8,900,125 (otoscanning with 3D modeling) – https://patents.google.com/patent/US8900125B2/en
- US 8,900,127 (capteur de pression) – https://patents.google.com/patent/US8900127B2/en
- US 8,900,128 (caméra vidéo + scan) – https://patents.google.com/patent/US8900128B2/en
- US 8,900,129 (otoscanner vidéo) – https://patents.google.com/patent/US8900129B2/en
- US 8,900,130 (alerte de sécurité) – https://patents.google.com/patent/US8900130B2/en
- Étude de précision, scanner manuel vs matériaux d'empreinte (GMS Z Audiol) – https://journals.publisso.de/en/journals/zaud/volume8/zaud000093
- Essai randomisé scan 3D vs moule conventionnel (PubMed) – https://pubmed.ncbi.nlm.nih.gov/41704209/
