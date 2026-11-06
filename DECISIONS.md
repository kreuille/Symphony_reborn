# Journal des décisions et points ouverts

Dernière mise à jour : 6 novembre 2026. Les décisions ci-dessous viennent d'Arnaud ; les hypothèses sont signalées comme telles.

## Décisions prises

| # | Décision | Conséquence |
|---|---|---|
| 1 | Le projet complet couvre scanner, logiciel CAD/CAM, cloud, imprimante et post-process, pas seulement le scanner | Six chantiers dans le plan de développement V2 |
| 2 | Impression sur machines à capsules SprintRay (pas d'impression continue) | Objectif de 30 min scan-à-pièce suspendu jusqu'à la mesure du temps de cycle (essai T9 de G1) |
| 3 | Budget d'erreur total de la chaîne scan, design, impression : 0,2 mm RMS | Répartition nominale : scanner 0,10, design 0,08, impression 0,10 |
| 4 | **FTO : go du 5 novembre 2026 (remplace « pas d'étude pour le moment »). Pas de cabinet pour le moment : Claude réalise une analyse préliminaire** | Analyse non juridique (recherche de brevets publics, statut, revendications) ; elle ne remplace pas un avis de conseil en propriété industrielle ; cahier des charges de la future étude : `docs/cahier-des-charges-FTO.md` ; état : criblage préliminaire réalisé le 6 novembre 2026 (`docs/analyse-fto-preliminaire.md`, sans lecture des revendications ni recherche chinoise), lecture des revendications des familles prioritaires à faire ; revue obligatoire à la gate M5 |
| 8 | Développement du scanner confié à une équipe mixte, interne et externe | Détail des rôles à fixer dans le plan scanner (`docs/plan-developpement-scanner.md`) |
| 9 | Développement localisé en Chine | Coûts, fournisseurs et recrutement à raisonner en contexte chinois ; point ouvert : conformité des données et du dispositif (marché visé) |
| 10 | Tous les types de pièces visés : embouts, coques ITE, et les autres | Le scanner doit couvrir la profondeur du 2ᵉ coude (ITE/IIC) ; la CAO et l'impression à confirmer pour chaque type |
| 11 | Enveloppe de la phase 1 : 200 000 (devise à confirmer) | Première enveloppe donnée le 5 novembre 2026 ; à rapprocher de la décision 7 (pas de budget détaillé avant la phase 0) : l'enveloppe est un plafond, pas un budget chiffré |
| 12 | **Retrait motorisé du scan : option produit prioritaire** (insertion manuelle, moteur uniquement en retrait, arrêt automatique et limite de force), pour réduire l'erreur de manipulation et automatiser la partie scan | À valider sur banc en phase 1 avec un critère d'indépendance de l'opérateur (P9, T13 de la spécification scanner) ; le centrage (passif, actif) et le dossier de sécurité d'un dispositif actif restent à résoudre ; le suivi externe reste l'architecture de référence et le repli |
| 5 | Précision d'impression inférieure à 0,10 mm : valeur annoncée pour le dentaire | Non démontrée sur formes auriculaires ; première mesure à faire en semaine 5 |
| 6 | SprintRay a déjà un cloud et un CAM intégré au cloud | Cloud et CAM : audit, paramétrage et extension de l'existant, pas de développement de zéro |
| 7 | Aucun chiffre de budget pour le moment | Montants à remettre après la phase 0, à partir de coûts réels |

## Hypothèses à valider

- Effectif : 17 à 25 ETP selon la phase, contre 16 ETP nominaux dans le modèle financier V1. Décision d'enveloppe ou de phasage de G3 à prendre à la gate M2.
- Cibles chiffrées des spécifications (seuils, rendements, durées) : points de départ à confirmer par les essais et avec les clients.
- Aux seuils Go (scanner 0,15, design 0,08, impression 0,10), la chaîne donne 0,197 mm en quadrature : marge d'environ 0,003 mm ; la somme linéaire dépasse 0,2 mm.
- Objectif de coût de la machine intégrée G3 : 2 000 USD hors scanner, exigence du document de stratégie, non démontrée. Conservée car c'est une exigence produit, pas un budget.

## Points ouverts

1. Périmètre exact de SprintRay Cloud et de son CAM (API, extensibilité, mode hors ligne, feuille de route de l'équipe cloud).
2. Fabricant légal, usage prévu et pays du pilote.
3. Cadre de données : hébergement, transferts éventuels vers la Chine, responsable de traitement.
4. Droits CAD (3Shape, Cyfex ou alternatives).
5. Route silicone : cellule dédiée, partenaire ou hors périmètre.
6. Sites pilotes et accords de partenariat et de données.
7. Réutilisation d'une plateforme SprintRay pour la machine intégrée, ou conception dédiée (gate M5).
8. Mise à jour de la présentation scanner si de nouvelles décisions sont prises.
