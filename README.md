# symphony_reborn : AI Ear Microfactory

Dossier de développement du projet « AI Ear Microfactory » : chaîne complète Ear-to-Wear (scanner, logiciel CAD/CAM, cloud, imprimante, post-process) pour la fabrication d'embouts et de protections auditives sur mesure.

Statut : propositions de travail, version du 4 novembre 2026. Aucun budget n'est chiffré pour le moment.

## Contenu

| Dossier | Contenu |
|---|---|
| `docs/` | Documents à jour : dossier complet V3, plan de développement complet V2, présentation du scanner v2, calendrier maître (Excel) |
| `specs/` | Spécifications techniques de phase 1 et plans pilotes, par chantier (voir le tableau ci-dessous) |
| `sources/` | Documents d'origine fournis par Arnaud : stratégie V1, présentation scanner v1, spécification scanner v0.1, plan pilote laboratoires v0.1 |
| `archive/` | Versions précédentes des documents produits |
| `DECISIONS.md` | Décisions prises, hypothèses à valider, points ouverts |
| `docs/presentation-projet-scanner-3D.docx` | Première version de la présentation du scanner, déjà présente dans le dépôt ; remplacée par `docs/presentation-projet-scanner-3D-v2.docx` (capsules SprintRay, FTO alors différé, budget d'erreur 0,2 mm, aucun budget chiffré) |
| `docs/cahier-des-charges-FTO.md` | Cahier des charges de l'étude FTO, déjà présent dans le dépôt ; l'étude est lancée depuis le 5 novembre 2026 (voir `DECISIONS.md`, décision 4) ; son budget sera fixé sur devis et n'est pas repris dans les autres documents |
| `docs/plan-developpement-scanner.md` | Plan de développement du scanner : options de suivi de pose (T1 à T4), lots de travail, simulation d'abord, jalons, équipe, risques, 30 premiers jours ; aligné sur `DECISIONS.md` |
| `docs/conception-scanner.md` | Calculs de conception du scanner (observabilité de la pose, géométrie de la tête A, cadence et datation), résultats du simulateur de pose, architecture de pose proposée, paramètres v0.3 ; script, simulateur de pose et résultats dans `tools/simulation/` |
| `docs/protocole-experience-otoscope-colmap.md` | Protocole d'expérience : otoscope USB bas coût et photogrammétrie (COLMAP) sur fantômes, pour mesurer la faisabilité de l'odométrie visuelle ; outils dans `tools/photogrammetrie/` (export STL des fantômes, analyse des résultats COLMAP) |
| `docs/plan-banc-phase1.md` | Plan du banc de phase 1 : hypothèses du simulateur à mesurer, matériel (sans prix), ordre des essais T1 à T13, seuils de décision entre les options (a), (b) et (c), formats de données, risques, premiers 15 jours |
| `docs/analyse-fto-preliminaire.md` | Criblage préliminaire de brevets publics (familles à examiner en priorité, statuts indicatifs, limites, suite à donner) ; ne remplace pas un avis juridique |
| `docs/etude-otoscan.md` | Étude de référence sur l'Otoscan (Natus/Otometrics) et les brevets United Sciences : performances publiées, enseignements, brevets à examiner à la revue M5 |

## Spécifications et plans pilotes

| Chantier | Spécification phase 1 | Plan pilote |
|---|---|---|
| Scanner 3D intra-auriculaire (G2a) | `specs/scanner-spec-prototype.md` | `specs/scanner-plan-pilote.md` |
| Cellule de production G1 | `specs/g1-spec-cellule-production.md` | `specs/g1-plan-pilote-cellule.md` |
| Logiciel de design (G2b) | `specs/logiciel-spec-design-auriculaire.md` | `specs/logiciel-plan-pilote.md` |
| CAM (volet du logiciel) | `specs/cam-spec-phase1.md` | couvert par les plans pilotes du logiciel et de G1 |
| Extension de SprintRay Cloud, DHR | `specs/cloud-spec-orchestration-dhr.md` | `specs/cloud-plan-pilote.md` |
| Imprimante | `specs/imprimante-spec-phase1.md` | `specs/imprimante-plan-pilote.md` |
| Post-process | `specs/postprocess-spec-phase1.md` | `specs/postprocess-plan-pilote.md` |

## Calendrier

Les phases 1 des spécifications durent 12 semaines (M0 à M2). Le calendrier de tous les chantiers, les gates (M2, M5, M8, M10, M14, M18, M24, M30, M36), les dépendances et le budget d'erreur de la chaîne sont dans `docs/calendrier-maitre.xlsx`.
