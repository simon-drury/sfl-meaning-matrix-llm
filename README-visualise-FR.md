# sfl_visualise.py — Visualisation des Trajectoires (FR)

Visualise les trajectoires d’états de signification sémiotique dans le manifold 9D.

## Exécuter

```bash
python sfl_visualise.py --no-anim    # PNG statiques uniquement
python sfl_visualise.py              # + animation MP4 (nécessite ffmpeg)
```

Sorties écrites dans `output/`.

## Fichiers de sortie

| Fichier | Ce qu’il montre |
|---------|------------------|
| `output/manifold_3d.png` | Trajectoires EN et ES dans le sous-espace idéationnel×tenor×textuel |
| `output/manifold_steps.png` | Déplacement et courbure par étape, colorés par dimension motrice |
| `output/manifold_gaussians.png` | Profils gaussiens sur les 9 dimensions à l’état final |
| `output/manifold_anim.mp4` | Trajectoire EN animée, une image par unité sémiotique |
