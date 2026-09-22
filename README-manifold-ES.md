# sfl_manifold.py — Geometría del Manifold Semiótico (ES)

Implementa la geometría riemanniana del manifold semiótico continuo M.

## Cantidades

| Símbolo | Nombre | Lo que mide |
|---------|--------|-------------|
| $\Delta_t$ | desplazamiento | cuánto se movió el estado de significado en el paso t |
| $\kappa_t$ | curvatura | cuán bruscamente giró la trayectoria |
| $\phi_t$ | dimensión conductora | cuál de las 9 dimensiones impulsó el movimiento |
| $E(\gamma)$ | energía geodésica | distancia semántica total recorrida |

## El espacio de estados

$$\mathbf{m}_t = \operatorname{vec}(M_t) \in [-1.0, 1.0]^9$$

Filas: metafunciones Ideacional, Interpersonal, Textual.  
Columnas: dimensiones de registro Campo, Tenor, Modo.

## Ejecutar

```bash
python sfl_manifold.py
```

Ver `MANIFOLD.md` para la especificación formal completa.
