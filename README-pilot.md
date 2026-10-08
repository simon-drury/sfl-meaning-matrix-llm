# SFL Meaning-Matrix LLM: Pilot Instantiation

## Iconic prompts

- **EN:** `hey why dont you print hello world for me please thank you`
- **ES:** `buenos días, hoy es viernes. Esto es CNN. Hoy es un día importante para mí y para muchos.`

Each prompt is processed step by step through the same instantiation route:

1. Lexical input received once.
2. Projected immediately into a 3×3 meaning matrix (M0).
3. Each subsequent clause or meaningful unit produces a delta matrix (Δt).
4. Lexical items are discarded after projection.
5. Realization rule maps the final meaning state back to a lexical selection.

All values are scalar, normalized to [-1.0, 1.0].  
Positive values indicate high activation of that dimension.  
Negative values indicate low activation or counter-pole.

---

## Matrix layout (all steps)

```text
               Field   Tenor   Mode
Ideational     m_id,f  m_id,t  m_id,m
Interpersonal  m_int,f m_int,t m_int,m
Textual        m_txt,f m_txt,t m_txt,m
```

Rows are metafunctions; columns are register variables. The Ideational, Interpersonal and Textual, and the Field, Tenor and Mode, readings in the SFL notes below are row and column readings; each matrix cell is the mean of its row reading and its column reading.

---

## EN prompt: `hey why dont you print hello world for me please thank you`

### Segmentation into meaning units

| Step | Unit |
|---|---|
| M0 | `hey` |
| Δ1 | `why dont you` |
| Δ2 | `print hello world` |
| Δ3 | `for me` |
| Δ4 | `please thank you` |

---

### M0 — `hey`

SFL reading:
- Ideational: minimal process content; phatic, contact-establishing. Low experiential load.
- Interpersonal: high involvement marker; symmetrical power, high solidarity.
- Textual: theme-establishing; discourse-opening move.
- Field: unspecified at this point; ambient, everyday.
- Tenor: informal, equal, familiar.
- Mode: written simulating spoken; spontaneous, low planning.

```text
M0 =
               Field   Tenor   Mode
Ideational     -0.60   +0.10   -0.65
Interpersonal  +0.15   +0.85   +0.10
Textual        +0.05   +0.75    0.00
```

---

### Δ1 — `why dont you`

SFL reading:
- Ideational: introduces a mental/verbal process; low experiential specificity, still phatic.
- Interpersonal: modalized directive; softened imperative via pseudo-interrogative. Power remains symmetrical; solidarity maintained. Slight increase in interpersonal force.
- Textual: rhematic development from the opening theme; moves discourse from contact to request trajectory.
- Field: beginning to narrow toward a technical/computational activity.
- Tenor: tenor stable; informal, directive softened by interrogative framing.
- Mode: mode stable; spontaneous written.

```text
Δ1 =
               Field   Tenor   Mode
Ideational     +0.15   +0.05   +0.05
Interpersonal  +0.15   +0.05   +0.05
Textual        +0.20   +0.10   +0.10
```

Cumulative state after Δ1:
```text
M1 =
               Field   Tenor   Mode
Ideational     -0.45   +0.15   -0.60
Interpersonal  +0.30   +0.90   +0.15
Textual        +0.25   +0.85   +0.10
```

---

### Δ2 — `print hello world`

SFL reading:
- Ideational: explicit material/verbal process now realized; participants defined (agent = you, goal = hello world). Experiential load rises sharply.
- Interpersonal: directive force now fully committed; command encoded.
- Textual: new rheme; the information core of the request arrives here.
- Field: fully narrowed to computational/programming field.
- Tenor: power differential momentarily invoked (requester/executor) but mitigated by surrounding politeness markers.
- Mode: mode stable.

```text
Δ2 =
               Field   Tenor   Mode
Ideational     +0.90   +0.40   +0.45
Interpersonal  +0.50    0.00   +0.05
Textual        +0.60   +0.10   +0.15
```

Cumulative state after Δ2:
```text
M2 =
               Field   Tenor   Mode
Ideational     +0.45   +0.55   -0.15
Interpersonal  +0.80   +0.90   +0.20
Textual        +0.80   +0.90   +0.20
```

---

### Δ3 — `for me`

SFL reading:
- Ideational: beneficiary participant added; minor experiential addition.
- Interpersonal: personalizes the request; re-establishes the solidarity frame and reminds of the human requester. Slight softening.
- Textual: minor cohesive extension of the request rheme.
- Field: stable.
- Tenor: warm; solidarity reinforced.
- Mode: stable.

```text
Δ3 =
               Field   Tenor   Mode
Ideational     +0.05   +0.10   +0.05
Interpersonal  -0.05    0.00   -0.05
Textual        +0.05   +0.10   +0.05
```

---

### Δ4 — `please thank you`

SFL reading:
- Ideational: zero experiential content.
- Interpersonal: strong politeness markers; face-protection, solidarity maximized. This is pure interpersonal work.
- Textual: discourse-closing move; coda to the request.
- Field: stable.
- Tenor: warmth and appreciation; power now fully flattened.
- Mode: stable.

```text
Δ4 =
               Field   Tenor   Mode
Ideational     -0.15   -0.05   -0.15
Interpersonal  +0.05   +0.15   +0.05
Textual        -0.10    0.00   -0.10
```

Final cumulative state:
```text
M_final_EN =
               Field   Tenor   Mode
Ideational     +0.30   +0.50   -0.30
Interpersonal  +0.80   +1.00   +0.20
Textual        +0.70   +0.90   +0.10
```

---

### Realization rule (EN)

Given M_final_EN:
- Ideational/Field +0.30 → computational/technical domain: select vocabulary from programming register.
- Interpersonal/Tenor +1.00 → informal, warm, polite, responsive register.
- Ideational row (-0.30 to +0.50) → balanced; process is output/display type.
- Textual/Mode +0.10 and Ideational/Mode -0.30 → spontaneous written; select informal syntax, short sentences.

**Realized output:**

```text
Hello, World!
```

The output lexical selection prioritizes:
- the exact technical artifact requested (hello world),
- zero interpersonal noise in the output (the output enacts the request, it does not comment on it),
- mode-appropriate brevity.

---

---

## ES prompt: `buenos días, hoy es viernes. Esto es CNN. Hoy es un día importante para mí y para muchos.`

### Segmentación en unidades de significado

| Paso | Unidad |
|---|---|
| M0 | `buenos días` |
| Δ1 | `hoy es viernes` |
| Δ2 | `Esto es CNN` |
| Δ3 | `Hoy es un día importante para mí` |
| Δ4 | `y para muchos` |

---

### M0 — `buenos días`

Lectura desde la GSF:
- Ideacional: proceso relacional; saludo fático. Contenido experiencial mínimo.
- Interpersonal: marcador alto de solidaridad; registro formal a neutro; respetuoso e inclusivo.
- Textual: apertura discursiva; posición temática fuerte.
- Campo: ambiente temporal y social.
- Tenor: respetuoso pero cálido; poder neutral; destinatario amplio.
- Modo: habla oral o radiodifundida; semiformal.

```text
M0 =
               Field   Tenor   Mode
Ideational     -0.45   +0.05   -0.10
Interpersonal  +0.25   +0.75   +0.60
Textual        +0.20   +0.70   +0.55
```

Nota: el valor de modo es positivo aquí (+0.4) porque este prompt simula habla radiodifundida, planificada, pública e institucional, a diferencia del prompt en inglés, que simula interacción escrita espontánea.

---

### Δ1 — `hoy es viernes`

Lectura desde la GSF:
- Ideacional: proceso relacional identificativo; circunstancia temporal más atributo. La carga experiencial aumenta ligeramente; aparece una proposición factual.
- Interpersonal: modo declarativo; aseveración neutra. No hay modalización. La solidaridad se mantiene.
- Textual: desarrollo remático; el discurso pasa del saludo al contenido informativo. Estructura dado/nuevo: hoy (dado, ya activado por buenos días) / es viernes (nuevo).
- Campo: orientación temporal cotidiana, típica de la locución informativa.
- Tenor: estable; dirección pública e institucional.
- Modo: estable; registro radiodifundido y planificado.

```text
Δ1 =
               Field   Tenor   Mode
Ideational     +0.30   +0.20   +0.20
Interpersonal  +0.10    0.00    0.00
Textual        +0.20   +0.10   +0.10
```

Estado acumulado tras Δ1:
```text
M1 =
               Field   Tenor   Mode
Ideational     -0.15   +0.25   +0.10
Interpersonal  +0.35   +0.75   +0.60
Textual        +0.40   +0.80   +0.65
```

---

### Δ2 — `Esto es CNN`

Lectura desde la GSF:
- Ideacional: proceso relacional identificativo; identificación nominal. La identidad institucional queda explicitada.
- Interpersonal: declaración autoritativa; sin atenuación. La fuerza interpersonal pasa a ser institucional más que personal. Se activa una asimetría de poder entre emisor y audiencia.
- Textual: cláusula identificativa; ancla todo el discurso en un contexto institucional. La organización textual cambia: todo lo anterior queda ahora enmarcado como salida de CNN.
- Campo: periodismo radiodifundido plenamente realizado.
- Tenor: autoridad institucional; formalidad; aumenta la diferencia de poder.
- Modo: plenamente planificado, guionizado y radiodifundido; modo formal realizado.

```text
Δ2 =
               Field   Tenor   Mode
Ideational     +0.65   +0.10   +0.40
Interpersonal  +0.50   -0.05   +0.25
Textual        +0.45   -0.10   +0.20
```

Nota: el tenor desciende hacia el polo formal/asimétrico (dirección negativa en el eje de solidaridad) cuando se declara la identidad institucional.

Estado acumulado tras Δ2:
```text
M2 =
               Field   Tenor   Mode
Ideational     +0.50   +0.35   +0.50
Interpersonal  +0.85   +0.70   +0.85
Textual        +0.85   +0.70   +0.85
```

---

### Δ3 — `Hoy es un día importante para mí`

Lectura desde la GSF:
- Ideacional: proceso relacional atributivo; se introduce evaluación experiencial mediante importante como atributo. El participante personal mí reintroduce a la hablante o al hablante como individuo dentro del marco institucional.
- Interpersonal: aseveración evaluativa; valoración y afecto. La voz personal reaparece dentro del registro institucional; es un movimiento poco habitual en el periodismo radiodifundido y marca el día como personalmente significativo. Se introduce una ligera vulnerabilidad o gravedad.
- Textual: reinicio temático con Hoy; se abre un nuevo desarrollo clausular dentro del mismo movimiento. Se establece contraste entre la identificación institucional de Δ2 y la significación personal de Δ3.
- Campo: evaluación, afectividad y marcación de relevancia.
- Tenor: desplazamiento momentáneo desde la autoridad institucional hacia la voz personal; aumenta la solidaridad con la audiencia por medio de la autoimplicación.
- Modo: estable; sigue siendo planificado, pero con irrupción de afecto personal.

```text
Δ3 =
               Field   Tenor   Mode
Ideational     +0.05   +0.25   +0.05
Interpersonal  -0.10   +0.10   -0.10
Textual         0.00   +0.20    0.00
```

---

### Δ4 — `y para muchos`

Lectura desde la GSF:
- Ideacional: ampliación del rango de participantes; muchos funciona como experimentador o beneficiario generalizado. La significación pasa de lo personal a lo colectivo.
- Interpersonal: la solidaridad se maximiza; la voz se alinea con un colectivo y se invoca una experiencia compartida. La valoración se amplía de lo individual a lo social.
- Textual: conjunción aditiva y; prolonga la cláusula anterior. La reorganización textual nueva es mínima.
- Campo: significación colectiva; se insinúa un momento histórico o social.
- Tenor: solidaridad máxima; la diferencia de poder se disuelve en la experiencia compartida.
- Modo: estable; breve, pero retóricamente cargado.

```text
Δ4 =
               Field   Tenor   Mode
Ideational     +0.15   +0.20   +0.10
Interpersonal  +0.10   +0.15   +0.05
Textual        +0.05   +0.10    0.00
```

Estado final acumulado:
```text
M_final_ES =
               Field   Tenor   Mode
Ideational     +0.75   +0.80   +0.65
Interpersonal  +0.90   +0.95   +0.80
Textual        +0.90   +0.95   +0.80
```

---

### Regla de realización (ES)

Dado M_final_ES:
- Ideational/Field +0.75 → periodismo radiodifundido; institucional, público y en español.
- Interpersonal/Tenor +0.95 → solidaridad colectiva cálida dentro de un marco institucional formal.
- Ideational row (+0.65 a +0.80) → proceso relacional evaluativo; contenido centrado en la significación.
- Textual/Mode +0.80 → habla radiodifundida planificada y semiformal; cláusulas completas, ritmo medido.

**Salida realizada (ES):**

```text
Buenos días. Hoy es un día importante para todos. Seguimos en CNN.
```

La realización selecciona:
- un saludo compatible con campo y tenor,
- solidaridad colectiva (todos en lugar de muchos, realizando la ampliación de Δ4),
- reanclaje institucional al cierre (Seguimos en CNN, manteniendo campo y modo),
- modo declarativo en toda la secuencia,
- brevedad y cadencia apropiadas al registro.

---

**Traducción posrender al inglés de la salida en español:**

```text
Good morning. Today is an important day for everyone. We continue on CNN.
```

---

## Summary: meaning trajectories compared

| Cell | M_final_EN | M_final_ES |
|---|---|---|
| Ideational / Field | +0.30 | +0.75 |
| Ideational / Tenor | +0.50 | +0.80 |
| Ideational / Mode | -0.30 | +0.65 |
| Interpersonal / Field | +0.80 | +0.90 |
| Interpersonal / Tenor | +1.00 | +0.95 |
| Interpersonal / Mode | +0.20 | +0.80 |
| Textual / Field | +0.70 | +0.90 |
| Textual / Tenor | +0.90 | +0.95 |
| Textual / Mode | +0.10 | +0.80 |

Key contrast:
- Both prompts end at maximum interpersonal activation, but via different trajectories.
- The EN prompt is low-mode (spontaneous, informal written); the ES prompt is high-mode (planned, broadcast, institutional).
- The ES prompt carries substantially higher ideational load (evaluative content, collective significance); the EN prompt's ideational content is minimal and purely instrumental.
- Field diverges sharply: computational/technical (EN) vs. broadcast journalism/social significance (ES).

These differences would propagate into different attention cluster activations and different realization strategies in the full architecture.

---

## Status

Pilot instantiation: complete.  
Next step: implement M0 and delta encoding as code, with these two prompts as test cases.
