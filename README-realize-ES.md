# sfl_realize.py — Desmatriciacion: Estado de Significado a Salida Lexica

## Proposito

La etapa final del pipeline. El transformer produce un estado de significado
\(M_{\text{out}} \in \mathcal{M}\). Este modulo recupera los elementos lexicos
cuyas huellas semioticas \(\mathbf{f}_w\) son mas cercanas a \(M_{\text{out}}\)
dentro del espacio de vocabulario \(\mathcal{V}_L\) del idioma objetivo \(L\).

\[
w^* = \arg\min_{w \in \mathcal{V}_L}\; \left\| \mathbf{f}_w - M_{\text{out}} \right\|_2
\]

---

## Realizacion multilingue co-igual

El mismo \(M_{\text{out}}\) presentado a \(\mathcal{V}_{\text{EN}}\) y
\(\mathcal{V}_{\text{ES}}\) produce dos realizaciones independientes en sus
respectivos idiomas. No hay paso de traduccion. Ambas salidas son
realizaciones co-iguales del mismo estado de significado.

Mientras que la traduccion automatica mapea forma a forma entre idiomas,
esta arquitectura mapea significado a forma de forma independiente dentro
de cada idioma.

---

## Huellas semioticas

Cada elemento lexico \(w \in \mathcal{V}_L\) lleva una huella
\(\mathbf{f}_w \in [-1, 1]^6\) que codifica su posicion metafuncional
en el manifold semiotico. En produccion, las huellas se aprenden de
corpora anotados con SFL. Los vocabularios piloto estan codificados
manualmente a partir del analisis de los dos prompts iconicos.

Como en todos los componentes, la dimensionalidad \(n_{\text{dim}}\)
es un parametro. Los vocabularios crecen con el manifold.

---

## Posicion en el pipeline

```
sfl_matrix_engine.py   parsear prompt -> MeaningTrajectory
       |
sfl_manifold.py        geometria del camino -> kappa, delta, phi, L_sp
       |
sfl_adapter.py         W_adapt: R^6 -> R^d_model
       |
[transformer]          paso hacia adelante sobre embeddings de significado
       |
sfl_realize.py         M_out -> w* en V_L
```

---

## Resultados piloto

### Realizacion de la trayectoria EN

| Paso | Unidad fuente | Mejor coincidencia | Principales candidatos |
|---|---|---|---|
| 0 | hey | hey | hey(0.00)  hello(0.22)  sorry(0.79) |
| 1 | why dont you | hello | hello(0.42)  hey(0.49)  sorry(0.78) |
| 2 | print hello world | hello world | hello world(0.37)  print(0.55)  code(0.72) |
| 3 | for me | for me | for me(0.00)  print(0.55)  show(0.62) |
| 4 | please thank you | thank you | thank you(0.26)  please(0.37)  sorry(0.63) |

### Demo multilingue: estado final EN -> ambos vocabularios

```
Mejor coincidencia EN : thank you
Mejor coincidencia ES : gracias
(mismo M_out, diferente V_L -- sin traduccion)
```

El estado de significado codifica *gratitud + cierre interpersonal*.
El vocabulario EN lo realiza como `thank you`; el vocabulario ES
lo realiza como `gracias`. Un significado, dos formas co-iguales.

---

## Escalabilidad

`VocabularySpace` es una estructura de datos pura. Puede respaldarse con:
- Un array numpy en memoria (piloto actual)
- Un indice FAISS para vocabularios a escala de millones
- Un almacen de vectores distribuido para corpora multilingues y multi-registro

La interfaz `nearest()` es identica en todos los casos.

---

## Proximo paso

`api.py` — wrapper FastAPI que expone el pipeline completo como un
servicio HTTP sin estado, escalable horizontalmente en el Nivel 2.
