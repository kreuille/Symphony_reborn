# Plan pilote avec laboratoires partenaires

Version 0.1 (brouillon). Les chiffres sont des ordres de grandeur à ajuster avec les partenaires. Ce plan suppose que la phase 1 (prototype validé sur fantômes) est terminée avec un Go.

## 1. Objectifs

1. Vérifier sur de vraies oreilles que le scanner donne des pièces utilisables sans retouche majeure.
2. Mesurer le temps réel du scan jusqu'à la pièce finie, avec impression continue.
3. Collecter des données (scan brut, conception automatique, conception corrigée par le technicien) pour entraîner votre propre CAO.
4. Recueillir l'avis des techniciens et mesurer l'intérêt commercial (prix acceptable, remplacement du scanner actuel).

## 2. Partenaires

- **Nombre :** 2 à 3 laboratoires ou audioprothésistes, de profils différents (un grand laboratoire, un petit, un spécialisé en protection auditive ou en écouteurs sur mesure si possible).
- **Critères de choix :** volume de pièces suffisant (au moins 20 à 30 paires par mois), technicien référent motivé, utilisation de 3Shape ou équivalent, accord pour partager les données, disponibilité géographique pour le support.
- **Contrepartie proposée :** équipement prêté ou tarif préférentiel, formation, pièces imprimées gratuitement pendant le pilote, accès prioritaire à la version commerciale.

## 3. Cadre juridique et éthique (à régler avant le premier patient)

- **Accord de partenariat :** confidentialité, propriété de la propriété intellectuelle générée (conseil : vous gardez celle de la sonde et des algorithmes ; les données restent au laboratoire sous licence d'usage pour l'apprentissage), exclusivité éventuelle limitée dans le temps, responsabilité.
- **Données personnelles :** formulaire de consentement éclairé pour chaque personne scannée, pseudonymisation (identifiant à la place du nom), stockage sécurisé, durée de conservation, conformité avec les lois locales (RGPD en Europe, loi chinoise sur la protection des informations personnelles si le pilote est en Chine).
- **Statut du dispositif :** un scanner utilisé sur des personnes, même en pilote, relève probablement d'une procédure d'investigation ou d'un avis du comité d'éthique, selon le pays. **À confirmer auprès d'un consultant réglementaire avant de commencer.** Le choix du pays du pilote peut simplifier la démarche.
- **Sécurité :** laser classe 1 vérifié, butée mécanique, protocole d'arrêt en cas d'inconfort, assurance responsabilité civile couvrant les essais.
- **Hygiène :** embouts de sonde jetables ou stérilisables, procédure de nettoyage documentée.

## 4. Protocole du pilote

### 4.1 Pour chaque personne participante

1. Consentement et vérification de l'absence de contre-indication (infection, douleur, perforation du tympan connue).
2. Inspection et nettoyage du conduit si nécessaire (pratique courante du laboratoire).
3. **Scan de référence :** le procédé habituel du laboratoire (empreinte en silicone puis numérisation, ou scanner existant).
4. **Scan avec votre prototype**, deux fois par oreille (pour la répétabilité).
5. Conception : d'abord avec le logiciel existant (3Shape ou autre) sur votre scan, puis conception de référence du technicien.
6. Impression de la pièce sur votre imprimante continue et finition.
7. **Essai de port** par la personne : confort, étanchéité, retour verbal.
8. Pour la protection auditive : mesure de l'atténuation si le laboratoire dispose du matériel (par exemple mesure in situ), sinon test d'étanchéité simple.

### 4.2 Taille de l'échantillon

- Pilote initial : 30 à 50 personnes (60 à 100 oreilles) réparties entre les laboratoires.
- Extension si les résultats sont bons : 150 à 300 oreilles pour entraîner et valider l'IA de CAO.

## 5. Mesures et indicateurs

| Indicateur | Définition | Cible indicative |
|---|---|---|
| Écart de forme | Distance entre votre maillage et le scan de référence, après alignement (RMS, 95e centile) | RMS ≤ 0,15 mm sur oreilles réelles |
| Taux de scan réussi du premier coup | Scans exploitables sans reprise / total | ≥ 85 % |
| Temps de scan | Durée par oreille | ≤ 60 s |
| Temps total jusqu'à la pièce finie | Du début du scan à la pièce prête | ≤ 60 min (objectif 30 min) |
| Taux de retouche par le technicien | Pièces nécessitant plus de 5 min de retouche | ≤ 20 % |
| Taux de refabrication | Pièces refaites car mal ajustées | ≤ taux habituel du laboratoire |
| Confort et étanchéité | Note de la personne (1 à 5) et test d'étanchéité | ≥ 4/5, étanche dans ≥ 90 % des cas |
| Satisfaction du technicien | Questionnaire | ≥ 4/5, avec liste des irritants |
| Intention d'achat | Prix accepté, remplacement de l'équipement actuel | oui, ou conditions précises |

Les cibles sont à discuter avec les partenaires. Le taux de refabrication de référence est celui qu'ils connaissent déjà.

## 6. Données collectées pour l'IA

Pour chaque oreille :

- scan brut (images, nuage de points, données IMU) et maillage reconstruit ;
- scan de référence du laboratoire ;
- conception automatique du logiciel existant ;
- **conception finale corrigée par le technicien**, avec l'historique des modifications si le logiciel le permet ;
- paramètres d'impression et pièce finale mesurée (écart de forme) ;
- métadonnées : côté, âge et sexe (si consentement), type de pièce, retours de confort.

Objectif : au moins 150 à 300 triplets (scan, conception automatique, conception finale) avant d'entraîner votre propre CAO. Les données sont versionnées et stockées de façon sécurisée, avec un format ouvert (STL, PLY, JSON).

## 7. Organisation

| Rôle | Responsabilité |
|---|---|
| Chef de projet pilote | Planning, relation avec les laboratoires, rapports |
| Ingénieur logiciel / vision | Support du scanner, correction des bogues, collecte des données |
| Technicien d'impression | Impression, finition, mesure des pièces |
| Référent laboratoire (par site) | Recrutement des personnes, protocole, retours |
| Conseiller réglementaire (externe) | Cadre éthique et réglementaire |
| Ingénieur IA | Préparation des données, premiers entraînements |

Support : intervention sous 24 à 48 h en cas de panne, mise à jour logicielle toutes les deux semaines au maximum, réunion hebdomadaire de 30 min avec chaque laboratoire.

## 8. Planning indicatif (6 à 9 mois)

| Période | Contenu |
|---|---|
| Mois 0–1 | Sélection des partenaires, accords, avis éthique ou réglementaire, formation |
| Mois 1–2 | Installation, essais à blanc sur fantômes dans chaque laboratoire |
| Mois 2–5 | Pilote sur personnes (30 à 50), ajustements logiciels toutes les deux semaines |
| Mois 5–6 | Analyse des résultats, rapport, décision Go / No-Go de la phase suivante |
| Mois 6–9 (si Go) | Extension de l'échantillon, premier entraînement de la CAO automatique, tests de comparaison |

## 9. Budget indicatif

| Poste | Ordre de grandeur |
|---|---|
| Matériel (3 scanners prototypes, imprimantes ou accès à vos machines, consommables) | 15 000 à 60 000 € |
| Équipe du pilote (temps d'ingénierie et d'impression) | 80 000 à 200 000 € |
| Conseil éthique et réglementaire, assurance | 10 000 à 40 000 € |
| Déplacements, formation, indemnités éventuelles des laboratoires | 10 000 à 30 000 € |
| **Total** | **environ 115 000 à 330 000 €** |

Ce budget est une estimation qui dépend fortement du lieu, de la taille de l'équipe et du cadre réglementaire.

## 10. Critères Go / No-Go de la phase suivante

- **Go :** écart de forme RMS ≤ 0,15 mm, taux de scan réussi ≥ 85 %, taux de refabrication au plus égal à la référence du laboratoire, temps total ≤ 60 min, satisfaction ≥ 4/5 et au moins un laboratoire prêt à acheter.
- **Go conditionnel :** un indicateur manqué avec une cause identifiée et un plan de correction chiffré.
- **No-Go :** précision ou taux de refabrication nettement moins bons que la référence, sans amélioration plausible, ou refus des laboratoires.

## 11. Risques et parades

| Risque | Parade |
|---|---|
| Retards de l'avis éthique ou réglementaire | Lancer les démarches dès la phase 1 ; choisir un pays ou un cadre plus simple |
| Participation insuffisante des laboratoires | Technicien référent désigné, contrepartie claire, réunions courtes et régulières |
| Cérumen, poils, conduits très coudés | Nettoyage préalable, enregistrer les échecs pour améliorer le filtrage |
| Panne du prototype chez un partenaire | Pièces de rechange, support rapide, deuxième sonde par site |
| Licence du logiciel tiers (3Shape ou autre) | Vérifier d'avance les conditions d'intégration et d'utilisation des données |
| Fuite ou mauvaise gestion des données | Pseudonymisation, chiffrement, accès restreint, accord écrit |
| Résultats trop dépendants du technicien | Protocole standardisé, formation commune, plusieurs techniciens par site |

## 12. Points ouverts à décider

1. Pays et laboratoires du pilote.
2. Cadre éthique et réglementaire retenu, après avis d'un consultant.
3. Logiciel de CAO de départ et conditions de licence.
4. Régime des données (propriété, durée, usage pour l'IA).
5. Contrepartie offerte aux laboratoires.
6. Équipement de mesure d'atténuation pour la protection auditive.
