# sfl_visualise.py — Visualización del Manifold Semiótico

## Propósito

Produce representaciones visuales de las trayectorias de significado calculadas por
`sfl_manifold.py`, usando los dos prompts icónicos como datos piloto.

---

## Requisitos

```bash
pip install matplotlib numpy
# Para exportar MP4:
brew install ffmpeg       # macOS
sudo apt install ffmpeg   # Linux/WSL
# Windows: descargar desde https://ffmpeg.org
```

---

## Uso

```bash
python sfl_visualise.py            # las cuatro salidas
python sfl_visualise.py --no-anim  # omitir MP4/GIF
```

---

## Cuatro salidas

| Archivo | Qué muestra |
|---|---|
| `output/manifold_3d.png` | Ambas trayectorias como caminos en el espacio ideacional / campo / textual |
| `output/manifold_steps.png` | \(\|\delta_t\|\) por paso (barra, coloreada por \(\phi_t\)) + \(\kappa_t\) superpuesta (blanco punteado) |
| `output/manifold_gaussians.png` | Los 6 perfiles Gaussianos en el estado final, EN sólido / ES discontinuo |
| `output/manifold_anim.mp4` | Trayectoria EN animada — un fotograma por unidad de significado, cámara rotatoria |

---

## Cómo leer los gráficos

**Trayectoria 3D** — cada punto es un estado de significado \(M_t\).
El camino que los conecta es la trayectoria \(\mathcal{T}\).
Camino recto = desarrollo de significado coherente y de baja energía.
Curva brusca = evento semántico (cambio de registro, movimiento evaluativo, cambio de campo).

**Geometría por paso** — la altura de la barra es la magnitud del desplazamiento \(\|\delta_t\|\).
El color de la barra es el driver metafuncional dominante \(\phi_t\) — el *por qué* del movimiento.
La línea blanca punteada es la curvatura \(\kappa_t\): los picos marcan eventos semánticos.

**Perfiles Gaussianos** — cada una de las seis dimensiones SFL se muestra como una
distribución de probabilidad centrada en su valor de estado final.
La dispersión (\(\sigma = 0.20\)) representa incertidumbre — un estado de significado
es una región, no un punto.

---

## Clave de colores

| Color | Dimensión |
|---|---|
| `#4f98a3` verde azulado | ideacional |
| `#da7101` naranja | campo |
| `#a12c7b` morado | interpersonal |
| `#437a22` verde | tenor |
| `#006494` azul | textual |
| `#7a39bb` violeta | modo |

---

## Próximo paso

`sfl_realize.py` — desmatrición: recuperación por vecino más cercano
en \(\mathcal{V}_L\) para producir salida léxica en el idioma \(L\).
