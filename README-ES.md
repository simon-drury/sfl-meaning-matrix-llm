# Modelo Semiótico Social (LASSM) — ES

> **el lenguaje como semiótica social — halliday 1978**

**Language As Social Semiotic Model (LASSM)**: modelización neuronal continua del lenguaje, fundamentada en la Lingüística Sistémico-Funcional de Halliday, que opera sobre matrices de estado semiótico 3×3 y trayectorias continuas en 9 dimensiones.

El español y el inglés son lenguas primeras co-iguales. No existe ningún paso de traducción.

---

## La tesis central

LASSM mapea forma → significado → forma:

```
prompt (cualquier modalidad)
     |
     v
proyección M₀ (adaptador SFL)
     |
     v
trayectoria en M (SFLMeaningTransformer, espacio 9D)
     |
     v
M_out ∈ [-1,1]^{3×3}   ←− estado de significado de salida
     |
     v
w* ∈ V_L   ←− elemento más próximo en el vocabulario empírico 9D
```

El transformer es un **calculador de trayectoria**. La teoría es SFL.

---

## La matriz de estado $M_t$

$$
M_t = \begin{bmatrix}
m_{\text{id, campo}} & m_{\text{id, tenor}} & m_{\text{id, modo}} \\
m_{\text{int, campo}} & m_{\text{int, tenor}} & m_{\text{int, modo}} \\
m_{\text{txt, campo}} & m_{\text{txt, tenor}} & m_{\text{txt, modo}}
\end{bmatrix}_t \in [-1.0, 1.0]^{3 \times 3}
$$

- **Filas (estratos metafuncionales)**: ideacional, interpersonal, textual
- **Columnas (dimensiones de registro)**: campo, tenor, modo

Desplegada: vector 9D $\mathbf{m}_t = \operatorname{vec}(M_t) \in [-1.0, 1.0]^9$.

---

## Las nueve dimensiones

| Dimensión | Rango | Significado LSF |
|-----------|-------|------------------|
| ideacional × campo | [-1, +1] | tipo de proceso en el dominio de actividad |
| ideacional × tenor | [-1, +1] | carga experiencial según el rol social |
| ideacional × modo | [-1, +1] | estructuración de la experiencia según el canal |
| interpersonal × campo | [-1, +1] | modalidad y apreciación en el dominio |
| interpersonal × tenor | [-1, +1] | distancia social, solidaridad, jerarquía |
| interpersonal × modo | [-1, +1] | postura interaccional según el medio |
| textual × campo | [-1, +1] | organización de la información en el dominio |
| textual × tenor | [-1, +1] | cohesión y tema según los roles sociales |
| textual × modo | [-1, +1] | estructura tema–rema, oralidad vs planificación |

---

## Inicio rápido

```bash
git clone https://github.com/simon-drury/sfl-meaning-matrix-llm.git
cd sfl-meaning-matrix-llm
pip install -r requirements.txt

python sfl_manifold.py       # geometría del manifold
python sfl_realize.py        # realización co-igual EN + ES
python sfl_visualise.py      # visualizaciones
uvicorn api:app --reload     # API en http://127.0.0.1:8000/docs
```

---

## Mapa del repositorio

| Archivo | Etapa | Detalle |
|---------|-------|---------|
| `traincore.py` | Entrenamiento | SFLMeaningTransformer 2,37M parámetros |
| `sfl_matrix_engine_v3.py` | Análisis | Motor matricial 3×3, operadores de covarianza |
| `sfl_manifold.py` | Geometría | Δt, κ, energía geodésica |
| `sfl_realize.py` | Realización | k-NN en vocabulario empírico 9D (EN/ES) |
| `sfl_visualise.py` | Visualización | Trayectoria 3D, geometría por pasos, animación |
| `api.py` | API | FastAPI, endpoints /analyze /pipeline /realize |
| `data/empirical_vocabulary_9d.json` | Datos | 32 580 ítems léxicos, centroides 9D empíricos |
| `data/empirical_trajectories.jsonl` | Datos | 500 trayectorias continuas parseadas |

---

## Cantidades geométricas clave

| Símbolo | Nombre | Lo que mide |
|---------|--------|-------------|
| $\Delta_t$ | desplazamiento | cuánto se movió el significado en el paso t |
| $\kappa_t$ | curvatura | cuán bruscamente giró la trayectoria |
| $\phi_t$ | dimensión conductora | qué dimensión impulsó el movimiento |
| $L_{\text{sp}}$ | energía geodésica | distancia semántica total recorrida |

---

## Realización multilingüe co-igual

El mismo $M_{\text{out}}$ presentado de forma independiente a $V_{\text{EN}}$ y $V_{\text{ES}}$:

```
Estado final (please thank you):
  mejor coincidencia EN : thank you
  mejor coincidencia ES : gracias
  (mismo M_out, distinto V_L — sin traducción)
```

El estado de significado codifica *gratitud + cierre interpersonal*. Cada vocabulario lo realiza en su propia lengua desde el mismo punto geométrico.

---

## Estado de implementación

| Componente | Archivo | Estado |
|------------|---------|--------|
| Motor matricial 3×3 | `sfl_matrix_engine_v3.py` | ✅ Operativo |
| Transformer (2,37M parámetros) | `traincore.py` | ✅ Entrenado |
| Vocabulario empírico 9D | `data/empirical_vocabulary_9d.json` | ✅ 32 580 ítems |
| Trayectorias empíricas | `data/empirical_trajectories.jsonl` | ✅ 500 frases |
| Realización léxica | `sfl_realize.py` | ✅ Operativo |
| API FastAPI | `api.py` | ✅ Operativo |
| Visualización | `sfl_visualise.py` | ✅ Operativo |

---

## Fundamentación teórica

- Halliday, M.A.K. (1985). *An Introduction to Functional Grammar*. Arnold.
- Halliday, M.A.K. & Matthiessen, C. (2014). *Halliday’s Introduction to Functional Grammar* (4ª ed.). Routledge.
- Martin, J.R. (1992). *English Text: System and Structure*. Benjamins.

---

## Política lingüística

Todos los READMEs de módulo se mantienen en paralelo: inglés (`README-{módulo}.md`) y español (`README-{módulo}-ES.md`). Ambos son primarios. Ninguno es una traducción del otro.

---

**Repo**: https://github.com/simon-drury/sfl-meaning-matrix-llm
