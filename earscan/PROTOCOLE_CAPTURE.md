# Protocole de capture d'un fantôme d'oreille externe

Objectif : produire un jeu d'images exploitable par `python -m earscan reconstruct` et le comparer au scan de référence.

## Matériel

- Fantôme d'oreille (silicone ou résine) posé sur un support fixe, à hauteur d'œil.
- Marqueur `earscan/marker_7_20mm.svg` imprimé **à 100 % (sans mise à l'échelle)** sur papier mat, puis **mesuré à la règle** : le côté du carré noir doit faire 20 mm (si l'impression dévie, noter la vraie valeur et la donner à `--marker-size-mm`). Coller bien à plat à côté de l'oreille, dans le même plan que la zone à mesurer.
- Téléphone Android sur la même focale pendant toute la capture (pas de zoom, pas de changement d'objectif), mise au point verrouillée si possible.
- Éclairage doux et uniforme (lumière du jour indirecte ou deux sources diffuses), sans reflet ni ombre portée marquée.

## Capture

1. Nettoyer le fantôme (pas de poussière ni de reflets) ; éviter les surfaces brillantes (poudre mate si besoin).
2. Prendre **40 à 60 photos** en arc de cercle autour de l'oreille, de face à profil, à 15 à 25 cm, avec **au moins 70 % de recouvrement** entre deux images consécutives.
3. Faire deux arcs à des hauteurs différentes (un légèrement au-dessus, un au niveau de l'oreille).
4. Le marqueur doit être **entièrement visible et net dans au moins 10 images** réparties sur l'arc.
5. Images nettes (pas de flou de bougé), format JPEG pleine résolution, sans filtre ni retouche.

## Référence

Scanner le même fantôme avec un scanner de laboratoire (ou la sonde si elle mesure l'extérieur), exporter en STL en millimètres, sans mise à l'échelle.

## Traitement et mesure

```bash
python -m earscan reconstruct captures/ --out sortie/ --marker-id 7 --marker-size-mm 20
python -m earscan evaluate sortie/ear_mm.ply reference.stl
```

Noter pour chaque essai : modèle de téléphone, nombre d'images, éclairage, `marker_views` et `marker_spread` de `report.json`, puis RMS, p95, maximum et erreur d'échelle. Répéter 10 fois sur le même fantôme pour mesurer la répétabilité (E4).
