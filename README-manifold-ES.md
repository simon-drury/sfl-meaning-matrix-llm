# sfl_manifold.py — Motor de Geometría de Trayectoria Semiótica

## Propósito

Toma una `MeaningTrajectory` — la salida de `sfl_matrix_engine.py` — y calcula
la **geometría del camino** a través del manifold semiótico \(\mathcal{M}\).

El vocabulario permanece aparcado. Este módulo opera exclusivamente sobre estados de significado.

---

## Cinco salidas por paso de trayectoria

| Símbolo | Nombre | Definición | Qué nos dice |
|---|---|---|---|
| \(\|\delta_t\|\) | Magnitud de desplazamiento | \(\|M_t - M_{t-1}\|_2\) | Cuánto se movió el significado en un paso |
| \(\kappa_t\) | Curvatura local | \(\arccos\!\left(\frac{\delta_t \cdot \delta_{t+1}}{\|\delta_t\|\,\|\delta_{t+1}\|}\right)\) | Si el camino giró — \(\kappa\) alto marca un evento semántico |
| \(\mathbf{v}_t\) | Vector de momento | \(\alpha\,\delta_t + (1-\alpha)\,\mathbf{v}_{t-1}\) | En qué dirección se dirige el camino |
| \(\mathcal{L}_{\text{sp}}\) | Pérdida de trayectoria semiótica | \(\sum_t \left(\lambda_1\|\delta_t\|^2 + \lambda_2\,\kappa_t^2\right)\) | Coherencia geométrica total de la trayectoria |
| \(\phi_t\) | Driver dominante | \(\arg\max_i |\delta_t^{(i)}|\) | **Por qué** se movió el camino — qué dimensión metafuncional impulsó el paso |

---

## El driver dominante \(\phi_t\)

Los transformadores estándar ponderan posiciones en una secuencia de tokens.
Esta arquitectura identifica la **fuente metafuncional** de cada desplazamiento de significado.
En cada paso, se nombra la dimensión con el mayor desplazamiento absoluto.

Esto no está disponible en arquitecturas basadas en tokens. Es una consecuencia directa
de operar sobre un manifold semánticamente etiquetado, en lugar de un espacio de embeddings léxicos.

---

## Pérdida de Trayectoria Semiótica \(\mathcal{L}_{\text{sp}}\)

\[
\mathcal{L}_{\text{sp}} = \sum_{t=1}^{n}
\left( \lambda_1 \|\delta_t\|^2 + \lambda_2\,\kappa_t^2 \right)
\]

Mientras que el entrenamiento estándar de modelos de lenguaje minimiza la entropía cruzada
sobre predicciones de tokens, esta arquitectura minimiza la **incoherencia geométrica
a lo largo de un camino de significado**. La pérdida penaliza tanto los grandes
desplazamientos como los giros bruscos — ambos indican una trayectoria semánticamente forzada.

La retropropagación se aplica normalmente: ambos términos son suaves y diferenciables
con respecto a los valores de la matriz.

---

## Resultados piloto — prompts icónicos

### EN: `hey why dont you print hello world for me please thank you`

| Paso | Unidad | \(\|\delta\|\) | \(\kappa\) | Driver \(\phi\) |
|---|---|---|---|---|
| 1 | why dont you | 0.316 | — | textual |
| 2 | print hello world | 1.296 | 0.675 | field |
| 3 | for me | 0.173 | 1.254 | ideational |
| 4 | please thank you | 0.387 | 2.034 | ideational |

\(\mathcal{L}_{\text{sp}} = 4.063\)

El gran desplazamiento en el paso 2 refleja la activación brusca del campo
ideacional cuando la solicitud se vuelve concreta. La alta curvatura en el paso 4
marca el retorno hacia el trabajo interpersonal tras el núcleo instrumental del prompt.

---

### ES: `buenos días — hoy es viernes. Esto es CNN. Hoy es un día importante para mí y para muchos.`

| Paso | Unidad | \(\|\delta\|\) | \(\kappa\) | Driver \(\phi\) |
|---|---|---|---|---|
| 1 | hoy es viernes | 0.490 | — | ideacional |
| 2 | Esto es CNN | 1.058 | 0.748 | campo |
| 3 | día importante para mí | 0.400 | 1.858 | tenor |
| 4 | y para muchos | 0.316 | 0.886 | ideacional |

\(\mathcal{L}_{\text{sp}} = 3.209\)

El gran desplazamiento en el paso 2 (`Esto es CNN`) refleja la activación
institucional del campo. La alta curvatura en el paso 3 marca el giro
desde la autoridad institucional hacia la voz personal — el momento
evaluativo y afectivo del prompt.

---

## Nota sobre escalabilidad

`compute_manifold()` es una función pura sobre una `MeaningTrajectory`.
Sin efectos secundarios, sin llamadas a modelos, sin I/O.
Escalable horizontalmente en los tres niveles de despliegue:
Nivel 1 (local), Nivel 2 (API), Nivel 3 (distribuido).

---

## Próximo paso

`sfl_adapter.py` — proyecta el vector de significado de 6 dimensiones en la
dimensión de embedding de un transformador local (Llama 3.2 3B / DeepSeek 1.5B)
mediante una capa lineal aprendida \(W_{\text{adapt}} \in \mathbb{R}^{d_{\text{model}} \times 6}\).
