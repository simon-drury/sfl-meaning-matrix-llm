# SFL Meaning Matrix LLM

> **el lenguaje como semiótica social — halliday 1978**

Una arquitectura de investigación que fundamenta los modelos de lenguaje basados en transformers
en la Lingüística Sistémico-Funcional (LSF). En lugar de predecir el siguiente token
directamente, el sistema calcula una trayectoria a través de un *manifold semiótico*
de seis dimensiones — y luego realiza esa trayectoria como salida léxica
de forma independiente en cada lengua de destino.

El español y el inglés son lenguas primeras co-iguales. No existe ningún paso de traducción.

---

## La tesis central

Los LLM actuales mapean forma a forma: secuencia de tokens de entrada, secuencia de tokens de salida.
Esta arquitectura mapea forma → significado → forma:

```
prompt (cualquier modalidad)
     |
     v
MeaningTrajectory en M   <-- manifold semiótico, 6 dimensiones
     |
     v
W_adapt: R^6 -> R^d_model   <-- capa adaptadora
     |
     v
[paso forward del transformer]  <-- ciego a la modalidad
     |
     v
M_out en M               <-- estado de significado de salida
     |
     v
w* en V_L                <-- elemento más próximo en el espacio de realización para la modalidad L
```

El manifold codifica las seis metafunciones de la LSF:
**ideacional, campo, interpersonal, tenor, textual, modo.**
Cada estado de significado es un punto en este espacio. Cada enunciado es una trayectoria.

---

## Inicio rápido

```bash
git clone https://github.com/simon-drury/sfl-meaning-matrix-llm.git
cd sfl-meaning-matrix-llm
pip install -r requirements.txt

# Ejecutar el motor de geometría sobre los dos prompts piloto
python sfl_manifold.py

# Demo de desmatrición (realización co-igual EN + ES)
python sfl_realize.py

# Generar todos los gráficos de visualización
python sfl_visualise.py --no-anim       # PNG estáticos
python sfl_visualise.py                 # + animación MP4 (requiere ffmpeg)

# Ejecutar la API
uvicorn api:app --reload
# -> http://127.0.0.1:8000/docs
```

Los gráficos se escriben en `output/`.

---

## Mapa del repositorio

| Archivo | Etapa | Detalle |
|---|---|---|
| `MANIFOLD.md` | Teoría | Especificación formal completa con LaTeX |
| `sfl_matrix_engine.py` | Análisis | Prompt -> `MeaningTrajectory` |
| `sfl_manifold.py` | Geometría | delta_t, kappa_t, phi_t, L_sp |
| `sfl_attention.py` | Atención | Máscara de auto-atención ponderada por LSF |
| `sfl_adapter.py` | Adaptador | W_adapt: R^6 -> R^d_model |
| `sfl_realize.py` | Realización | M_out -> w* en V_L (EN y ES) |
| `sfl_visualise.py` | Visualización | Trayectoria 3D, geometría por pasos, gaussianas, animación |
| `api.py` | API | Wrapper FastAPI, modalidad primero, endpoint pipeline completo |
| `wadapt_lora_training_sketch.ipynb` | Investigación | Boceto Colab: entrenamiento del adaptador LoRA hacia Llama-3.2 |

Cada módulo tiene dos READMEs: inglés (`README-{módulo}.md`) y
español (`README-{módulo}-ES.md`).

---

## Los dos prompts piloto

Todos los datos piloto proceden de exactamente dos prompts icónicos, uno por lengua.

**EN** — una persona dando instrucciones a un LLM:
```
hey  /  why dont you  /  print hello world  /  for me  /  please thank you
```

**ES** — apertura de un informativo radiodifundido:
```
buenos días  /  hoy es viernes  /  Esto es CNN  /  día importante  /  y para muchos
```

Estos prompts se eligieron porque abarcan toda la extensión del manifold semiótico:
desde el registro interpersonal fático (baja carga ideacional, alto tenor) hasta
el registro institucional radiodifundido (campo alto, textual alto).

---

## Las seis dimensiones

| Dimensión | Lo que codifica | Rango |
|---|---|---|
| ideacional | contenido proposicional / experiencial | [-1, 1] |
| campo | especificidad del dominio / materia | [-1, 1] |
| interpersonal | relación hablante-oyente | [-1, 1] |
| tenor | formalidad y poder | [-1, 1] |
| textual | discurso / cohesión | [-1, 1] |
| modo | canal / continuo escrito-oral | [-1, 1] |

Un estado de significado M_t es un punto en [-1, 1]^6.
Una trayectoria de significado T es la secuencia ordenada M_0, M_1, ..., M_T.

---

## Cantidades geométricas clave

| Símbolo | Nombre | Lo que mide |
|---|---|---|
| delta_t | desplazamiento | cuánto se movió el significado en el paso t |
| kappa_t | curvatura | cuán bruscamente giró la trayectoria en el paso t |
| phi_t | dimensión conductora | qué dimensión impulsó el movimiento |
| L_sp | longitud del camino | distancia semántica total recorrida |

Una trayectoria recta = desarrollo de significado coherente y de baja energía.
Un pico pronunciado en kappa = evento semántico: cambio de registro, movimiento evaluativo, cambio de campo.

---

## Realización multilingüe co-igual

El mismo M_out presentado de forma independiente a V_EN y V_ES:

```
Estado final EN (please thank you):
  mejor coincidencia EN : thank you
  mejor coincidencia ES : gracias
  (mismo M_out, distinto V_L -- sin traducción)
```

El estado de significado codifica *gratitud + cierre interpersonal*.
Cada vocabulario lo realiza en su propia lengua desde el mismo punto geométrico.

---

## Determinismo y probabilidad

El sistema es deliberadamente agnóstico en esta cuestión en la fase actual.
Un estado de significado se modela como una región gaussiana en el manifold
(sigma = 0,20 en el piloto), no como un punto. Esto implica:

- Los desplazamientos pequeños (delta_t < 0,3) se tratan como movimiento dentro de la región
- Los desplazamientos grandes señalan eventos semánticos genuinos
- La recuperación por vecino más próximo en sfl_realize.py puede extenderse a
  muestreo estocástico top-k desde la gaussiana en cualquier momento

Si la trayectoria es determinista (dado contexto suficiente) o
irreduciblemente probabilística es una pregunta de investigación abierta.

---

## Salidas de visualización

Ejecutar `sfl_visualise.py` produce:

| Archivo | Lo que muestra |
|---|---|
| `output/manifold_3d.png` | Trayectorias EN y ES como caminos en el espacio ideacional/campo/textual |
| `output/manifold_steps.png` | Desplazamiento y curvatura por paso, coloreados por dimensión conductora |
| `output/manifold_gaussians.png` | Perfiles gaussianos para las 6 dimensiones en el estado final |
| `output/manifold_anim.mp4` | Trayectoria EN animada, un fotograma por unidad de significado |

---

## API

Véase [`README-api-ES.md`](README-api-ES.md) para la documentación completa de los endpoints.

```bash
uvicorn api:app --reload
# Documentación interactiva en http://127.0.0.1:8000/docs
```

| Endpoint | Lo que hace |
|---|---|
| `GET /health` | Comprobación de disponibilidad |
| `GET /dims` | Nombres y rangos de las dimensiones del manifold |
| `POST /analyze` | Prompt -> MeaningTrajectory completa con geometría |
| `POST /realize` | M_out + modalidad -> realización más próxima |
| `POST /pipeline` | Prompt + modalidad -> trayectoria + realización |

---

## Teoría formal

Véase [`MANIFOLD.md`](MANIFOLD.md) para la especificación matemática completa,
que incluye la definición de M como manifold riemanniano liso, el
funcional de camino geodésico, la proyección del adaptador y el criterio de
recuperación en la realización.

---

## Estado de implementación

**Fase 1 — pipeline del manifold de significado: completo y ejecutable.**

| Componente | Archivo | Estado |
|---|---|---|
| Analizador semántico (motor de matrices) | `sfl_matrix_engine.py` | ✅ Operativo |
| Geometría del manifold | `sfl_manifold.py` | ✅ Operativo |
| Capa de atención LSF | `sfl_attention.py` | ✅ Operativo |
| Realización léxica (EN/ES/PT/IT/ZH) | `sfl_realize.py` | ✅ Operativo |
| Visualización de trayectorias | `sfl_visualise.py` | ✅ Operativo |
| Wrapper API FastAPI | `api.py` | ✅ Operativo |
| Boceto adaptador LoRA (Colab) | `wadapt_lora_training_sketch.ipynb` | ✅ Ejecutable en Colab |

**Fase 2 — integración con el transformer: arquitectura especificada, implementación en curso.**

| Componente | Archivo | Estado | Requiere |
|---|---|---|---|
| Proyección adaptadora W_adapt | `sfl_adapter.py` | 🔧 Integración pendiente | Instalación local de GPT4All |
| Puente GPT4All | `sfl_gpt4all.py` | 🔧 Integración pendiente | Instalación local de GPT4All + modelo (~4 GB) |
| Entrenamiento LoRA Wadapt | `wadapt_lora_training_sketch.ipynb` | 🔧 Objetivos de entrenamiento pendientes | Estados ocultos de Llama-3.2 |

Los componentes de la Fase 1 se ejecutan con `pip install -r requirements.txt` — sin GPU, sin descarga de modelos, menos de 50 MB en total.
Los componentes de la Fase 2 requieren una instalación local de transformer y son objeto de investigación en curso.

---

## Fundamentación teórica

- Halliday, M.A.K. (1985). *An Introduction to Functional Grammar*. Arnold.
- Halliday, M.A.K. & Matthiessen, C. (2014). *Halliday's Introduction to Functional Grammar* (4ª ed.). Routledge.
- Martin, J.R. (1992). *English Text: System and Structure*. Benjamins.

Las metafunciones de la LSF (ideacional, interpersonal, textual) y las
variables de registro (campo, tenor, modo) constituyen la base teórica de
las seis dimensiones del manifold.

---

## Política lingüística

Todos los READMEs de módulo se mantienen en paralelo:
inglés (`README-{módulo}.md`) y español (`README-{módulo}-ES.md`).
Ambos son primarios. Ninguno es una traducción del otro.
