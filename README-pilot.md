# SFL Meaning-Matrix LLM: Pilot Instantiation

## Iconic prompts

- **EN:** `hey why dont you print hello world for me please thank you`
- **ES:** `buenos días, hoy es viernes. Esto es CNN. Hoy es un día importante para mí y para muchos.`

Each prompt is processed step by step through the same instantiation route:

1. Lexical input received once.
2. Projected immediately into a 3×2 meaning matrix (M0).
3. Each subsequent clause or meaningful unit produces a delta matrix (Δt).
4. Lexical items are discarded after projection.
5. Realization rule maps the final meaning state back to a lexical selection.

All values are scalar, normalized to [-1.0, 1.0].  
Positive values indicate high activation of that dimension.  
Negative values indicate low activation or counter-pole.

---

## Matrix layout (all steps)

```
[ Ideational     Field  ]
[ Interpersonal  Tenor  ]
[ Textual        Mode   ]
```

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

```
M0 =
[ Ideational: -0.7    Field: -0.5 ]
[ Interpersonal: +0.8  Tenor: +0.9 ]
[ Textual: +0.6       Mode: -0.6  ]
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

```
Δ1 =
[ Ideational: +0.1    Field: +0.2 ]
[ Interpersonal: +0.1  Tenor:  0.0 ]
[ Textual: +0.2       Mode:  0.0  ]
```

Cumulative state after Δ1:
```
M1 =
[ Ideational: -0.6    Field: -0.3 ]
[ Interpersonal: +0.9  Tenor: +0.9 ]
[ Textual: +0.8       Mode: -0.6  ]
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

```
Δ2 =
[ Ideational: +0.9    Field: +0.9 ]
[ Interpersonal: +0.1  Tenor: -0.1 ]
[ Textual: +0.3       Mode:  0.0  ]
```

Cumulative state after Δ2:
```
M2 =
[ Ideational: +0.3    Field: +0.6 ]
[ Interpersonal: +1.0  Tenor: +0.8 ]
[ Textual: +1.0       Mode: -0.6  ]
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

```
Δ3 =
[ Ideational: +0.1    Field:  0.0 ]
[ Interpersonal: -0.1  Tenor: +0.1 ]
[ Textual: +0.1       Mode:  0.0  ]
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

```
Δ4 =
[ Ideational: -0.3    Field:  0.0 ]
[ Interpersonal: +0.1  Tenor: +0.2 ]
[ Textual: -0.2       Mode:  0.0  ]
```

Final cumulative state:
```
M_final_EN =
[ Ideational:  0.0    Field: +0.6 ]
[ Interpersonal: +1.0  Tenor: +1.0 ]
[ Textual: +0.8       Mode: -0.6  ]
```

---

### Realization rule (EN)

Given M_final_EN:
- Field +0.6 → computational/technical domain: select vocabulary from programming register.
- Interpersonal +1.0, Tenor +1.0 → informal, warm, polite, responsive register.
- Ideational 0.0 → balanced; process is output/display type.
- Mode -0.6 → spontaneous written; select informal syntax, short sentences.

**Realized output:**

```
Hello, World!
```

The output lexical selection prioritizes:
- the exact technical artifact requested (hello world),
- zero interpersonal noise in the output (the output enacts the request, it does not comment on it),
- mode-appropriate brevity.

---

---

## ES prompt: `buenos días, hoy es viernes. Esto es CNN. Hoy es un día importante para mí y para muchos.`

### Segmentation into meaning units

| Step | Unit |
|---|---|
| M0 | `buenos días` |
| Δ1 | `hoy es viernes` |
| Δ2 | `Esto es CNN` |
| Δ3 | `Hoy es un día importante para mí` |
| Δ4 | `y para muchos` |

---

### M0 — `buenos días`

SFL reading:
- Ideational: relational process; phatic greeting. Minimal experiential content.
- Interpersonal: high solidarity marker; formal-to-neutral register; respectful, inclusive.
- Textual: discourse-opening; strong theme position.
- Field: ambient; temporal/social.
- Tenor: respectful but warm; power neutral; broad address.
- Mode: spoken or scripted broadcast; semi-formal.

```
M0 =
[ Ideational: -0.6    Field: -0.3 ]
[ Interpersonal: +0.8  Tenor: +0.7 ]
[ Textual: +0.7       Mode: +0.4  ]
```

Note: Mode value is positive here (+0.4) because this prompt simulates broadcast speech (planned, public, institutional), unlike the EN prompt which simulates spontaneous written interaction.

---

### Δ1 — `hoy es viernes`

SFL reading:
- Ideational: relational identifying process; circumstance (time) + attribute. Experiential load rises slightly; factual proposition introduced.
- Interpersonal: declarative mood; neutral assertion. No modalization. Solidarity maintained.
- Textual: rhematic development; moves from greeting to informational content. Given/new structure: hoy (given: today, already established by buenos días) / es viernes (new: the specific day).
- Field: temporal; daily orientation function typical of broadcast journalism.
- Tenor: stable; institutional, public address.
- Mode: stable; planned broadcast register.

```
Δ1 =
[ Ideational: +0.4    Field: +0.2 ]
[ Interpersonal:  0.0  Tenor:  0.0 ]
[ Textual: +0.2       Mode:  0.0  ]
```

Cumulative state after Δ1:
```
M1 =
[ Ideational: -0.2    Field: -0.1 ]
[ Interpersonal: +0.8  Tenor: +0.7 ]
[ Textual: +0.9       Mode: +0.4  ]
```

---

### Δ2 — `Esto es CNN`

SFL reading:
- Ideational: relational identifying process; nominal identification. Institutional identity explicitly realized.
- Interpersonal: authoritative declaration; no hedging. Interpersonal force is now institutional rather than personal. Power differential invoked: broadcaster over audience.
- Textual: identificatory clause; anchors the entire discourse in an institutional context. Textual organization shifts: everything said before is now framed as CNN output.
- Field: broadcast journalism fully realized.
- Tenor: institutional authority; formal; power differential increases.
- Mode: fully planned, scripted broadcast; formal mode realized.

```
Δ2 =
[ Ideational: +0.5    Field: +0.8 ]
[ Interpersonal: +0.2  Tenor: -0.3 ]
[ Textual: +0.1       Mode: +0.3  ]
```

Note: Tenor decreases toward the formal/asymmetric pole (negative direction on solidarity axis) as institutional identity is declared.

Cumulative state after Δ2:
```
M2 =
[ Ideational: +0.3    Field: +0.7 ]
[ Interpersonal: +1.0  Tenor: +0.4 ]
[ Textual: +1.0       Mode: +0.7  ]
```

---

### Δ3 — `Hoy es un día importante para mí`

SFL reading:
- Ideational: relational attributive process; experiential evaluation introduced (importante = attribute). Personal participant (mí) reintroduces the speaker as an individual within the institutional frame.
- Interpersonal: evaluative assertion; appraisal (attitude: appreciation/affect). Personal voice reasserts within institutional register; unusual move in broadcast journalism — marks the day as personally significant. Slight vulnerability or gravitas introduced.
- Textual: thematic restart (Hoy re-thematized); creates a new clause complex within the same move. Contrast between institutional identification (Δ2) and personal significance (Δ3).
- Field: evaluative; affective; significance-marking.
- Tenor: momentary shift from institutional authority to personal voice; solidarity with audience increased through personal disclosure.
- Mode: stable; still planned, but personal affect introduced.

```
Δ3 =
[ Ideational: +0.2    Field: -0.1 ]
[ Interpersonal: -0.1  Tenor: +0.3 ]
[ Textual: +0.1       Mode: -0.1  ]
```

---

### Δ4 — `y para muchos`

SFL reading:
- Ideational: extension of participant range; muchos = generalized beneficiary/experiencer. Broadens the significance from personal to collective.
- Interpersonal: solidarity maximized; the speaker aligns with a collective; shared experience invoked. Appraisal broadens from individual to social.
- Textual: additive cohesive conjunction (y); extends the previous clause. Minimal new textual organization.
- Field: collective significance; historical or social moment implied.
- Tenor: solidarity maximized; power differential dissolved in shared significance.
- Mode: stable; brief, rhetorically weighted.

```
Δ4 =
[ Ideational: +0.2    Field: +0.1 ]
[ Interpersonal: +0.1  Tenor: +0.2 ]
[ Textual: +0.0       Mode:  0.0  ]
```

Final cumulative state:
```
M_final_ES =
[ Ideational: +0.7    Field: +0.8 ]
[ Interpersonal: +1.0  Tenor: +0.9 ]
[ Textual: +1.0       Mode: +0.6  ]
```

---

### Realization rule (ES)

Given M_final_ES:
- Field +0.8 → broadcast journalism; institutional, public, Spanish-language.
- Interpersonal +1.0, Tenor +0.9 → warm collective solidarity within formal institutional frame.
- Ideational +0.7 → evaluative relational process; significance-marking content.
- Mode +0.6 → planned, semi-formal broadcast speech; complete clause structures, measured pace.

**Realized output (ES):**

```
Buenos días. Hoy es un día importante para todos. Seguimos en CNN.
```

Realization selects:
- greeting appropriate to field and tenor,
- collective solidarity (todos rather than muchos — realizes the broadening move of Δ4),
- institutional identification re-anchored at close (Seguimos en CNN — maintains field and mode),
- declarative mood throughout (interpersonal: authoritative but warm),
- register-appropriate brevity and cadence.

---

**Post-render EN translation of ES output:**

```
Good morning. Today is an important day for everyone. We continue on CNN.
```

---

## Summary: meaning trajectories compared

| Dimension | M_final_EN | M_final_ES |
|---|---|---|
| Ideational | 0.0 | +0.7 |
| Field | +0.6 | +0.8 |
| Interpersonal | +1.0 | +1.0 |
| Tenor | +1.0 | +0.9 |
| Textual | +0.8 | +1.0 |
| Mode | -0.6 | +0.6 |

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
