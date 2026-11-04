# symphony_reborn

Documentation du projet **scanner 3D intra-auriculaire** et de la chaîne complète **scan → CAO automatique → impression 3D continue**.

## Contenu

| Fichier | Description |
|---|---|
| `docs/presentation-projet-scanner-3D.docx` | Dossier de présentation détaillé (8 pages), base du script de présentation : contexte, choix technologique, chaîne complète, feuille de route, PI, réglementation, budget, risques, squelette de présentation, questions probables |
| `docs/cahier-des-charges-FTO.md` | Cahier des charges de l'étude de liberté d'exploitation (FTO) à confier à un cabinet de propriété industrielle |

## Synthèse du projet

- **Objectif** : numériser le conduit auditif sans empreinte silicone et produire la pièce finie (coque/embout) en quelques minutes.
- **Technologie retenue** : optique à lumière structurée (anneau laser ou motif codé monocoup) ; ultrasons (type IVUS) faisables mais plus complexes, photogrammétrie en complément.
- **Chaîne** : scan → reconstruction (IMU, ICP, TSDF, IA) → CAO automatique → impression continue.
- **Stratégie logicielle** : démarrer avec un logiciel existant (3Shape), puis internaliser.
- **Feuille de route** : FTO (4–8 semaines, 10–40 k€) → prototype sur fantômes (12 semaines, critères Go/No-Go) → pilote en 2–3 laboratoires (6–9 mois, 30–300 oreilles) → industrialisation.

## Points ouverts

- Commander l'étude FTO et choisir le cabinet
- Valider licence et API du partenaire logiciel
- Sélectionner 2 à 3 laboratoires pilotes
- Choix techniques : capteur de référence, fournisseurs, résine compatible
- Cadre réglementaire avant tout pilote sur patient
- Dépôt de brevets (chaîne complète, CAO automatique) avant divulgation détaillée

> Les spécifications détaillées du prototype (phase 1) et le plan pilote laboratoires, rédigés lors d'une session précédente, n'étaient plus disponibles et ne sont pas inclus.
