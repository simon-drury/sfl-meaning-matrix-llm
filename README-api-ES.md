# api.py -- SFL Meaning Matrix: Wrapper FastAPI

## El transformer es ciego a la modalidad

La API aplica el principio arquitectonico central:
el transformer opera sobre estados de significado en M.
La modalidad se gestiona en los bordes -- por el parser (entrada)
y el realizador (salida).

```
prompt (cualquier modalidad)
     |
     v
[parser]              <- borde de entrada
     |
     v
MeaningTrajectory     <- el transformer solo ve esto
     |
     v
[transformer]
     |
     v
M_out en M
     |
     v
[realizador]          <- borde de salida, modalidad es un parametro
     |
     v
realizacion (texto hoy, audio manana, visual la semana siguiente)
```

---

## Ejecucion

```bash
pip install fastapi uvicorn numpy
uvicorn api:app --reload
```

Documentacion interactiva autogenerada en: `http://127.0.0.1:8000/docs`

---

## Endpoints

| Metodo | Endpoint | Que hace |
|---|---|---|
| `GET` | `/health` | Control de actividad |
| `GET` | `/dims` | Nombres y rangos de las dimensiones del manifold |
| `POST` | `/analyze` | Prompt -> MeaningTrajectory completa con geometria |
| `POST` | `/realize` | M_out + modalidad -> realizacion mas cercana |
| `POST` | `/pipeline` | Prompt + modalidad -> trayectoria + realizacion en una llamada |

---

## Ejemplo: pipeline completo

```bash
curl -X POST http://127.0.0.1:8000/pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "buenos dias hoy es viernes Esto es CNN",
    "lang_in": "ES",
    "modality": "text",
    "lang_out": "ES",
    "k": 3
  }'
```

---

## Realizacion multilingue: mismo M_out, dos vocabularios

```bash
# Realizacion EN
curl -X POST http://127.0.0.1:8000/realize \
  -d '{"M_out": [0.1, 0.6, 1.0, 1.0, 0.8, -0.6, 0.3, 0.2, 0.5], "modality": "text", "lang": "EN"}'
# -> "thank you"

# Realizacion ES -- mismo M_out
curl -X POST http://127.0.0.1:8000/realize \
  -d '{"M_out": [0.1, 0.6, 1.0, 1.0, 0.8, -0.6, 0.3, 0.2, 0.5], "modality": "text", "lang": "ES"}'
# -> "gracias"
```

Dos busquedas independientes en dos espacios de vocabulario.

---

## Anadir una nueva modalidad

Registrar un nuevo realizador en `api.py`:

```python
REALIZERS["audio:EN"] = AudioRealizerEN()   # misma interfaz .nearest()
REALIZERS["visual"]   = VisualRealizer()    # sin lang para algunas modalidades
```

Los endpoints `/realize` y `/pipeline` funcionan de inmediato.
El transformer no cambia.

---

## Alcance del piloto

- Vocabulario piloto con huellas codificadas manualmente
- Autenticacion, almacenamiento persistente, procesamiento por lotes y streaming son Nivel 2
