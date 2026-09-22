# sfl_visualise.py — Visualización de Trayectorias (ES)

Visualiza trayectorias de estados de significado semiótico en el manifold 9D.

## Ejecutar

```bash
python sfl_visualise.py --no-anim    # solo PNG estáticos
python sfl_visualise.py              # + animación MP4 (requiere ffmpeg)
```

Salidas escritas en `output/`.

## Archivos de salida

| Archivo | Lo que muestra |
|---------|----------------|
| `output/manifold_3d.png` | Trayectorias EN y ES como caminos en el subespacio ideacional×tenor×textual |
| `output/manifold_steps.png` | Desplazamiento y curvatura por paso, coloreados por dimensión conductora |
| `output/manifold_gaussians.png` | Perfiles gaussianos a lo largo de las 9 dimensiones en el estado final |
| `output/manifold_anim.mp4` | Trayectoria EN animada, un fotograma por unidad semiótica |
