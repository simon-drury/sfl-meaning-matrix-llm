# api.py — LASSM: Wrapper FastAPI (ES)

## El transformer es ciego a la modalidad

La API hace cumplir el principio arquitectónico central:
el transformer opera sobre estados de significado en M.
No tiene conocimiento de la modalidad de entrada o salida.
La modalidad se gestiona en los bordes — por el analizador (entrada)
y el realizador (salida).

```
prompt (cualquier modalidad)
     |
     v
[analizador]          <- borde de entrada
     |
     v
MeaningTrajectory     <- el transformer sólo ve esto (estados 9D)
     |
     v
[SFLMeaningTransformer]
     |
     v
M_out ∈ [-1,1]^{3×3}
     |
     v
[realizador]          <- borde de salida
     |
     v
realización
```

## Ejecutar

```bash
pip install fastapi uvicorn numpy
uvicorn api:app --reload
# http://127.0.0.1:8000/docs
```

## Endpoints

| Método | Endpoint | Qué hace |
|--------|----------|-----------|
| `GET`  | `/health` | Comprobación de disponibilidad |
| `GET`  | `/dims` | Nombres y rangos de dimensiones |
| `POST` | `/analyze` | Prompt → MeaningTrajectory con geometría |
| `POST` | `/realize` | M_out + modalidad → realización más próxima |
| `POST` | `/pipeline` | Prompt + modalidad → trayectoria + realización |

## Lo que no es

Sin autenticación, sin almacenamiento persistente, sin lotes, vocabulario piloto únicamente. Todo eso es Tier 2.
