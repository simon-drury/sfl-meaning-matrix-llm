# api.py — LASSM : Wrapper FastAPI (FR)

## Le transformer est aveugle à la modalité

L’API fait respecter le principe architectural central :
le transformer opère sur des états de signification dans M.
Il n’a aucune connaissance de la modalité d’entrée ou de sortie.
La modalité est gérée aux bords — par l’analyseur (entrée) et le réalisateur (sortie).

## Exécuter

```bash
pip install fastapi uvicorn numpy
uvicorn api:app --reload
# http://127.0.0.1:8000/docs
```

## Endpoints

| Méthode | Endpoint | Ce qu’il fait |
|---------|----------|-----------------|
| `GET`   | `/health` | Vérification de disponibilité |
| `GET`   | `/dims` | Noms et plages des dimensions du manifold |
| `POST`  | `/analyze` | Prompt → MeaningTrajectory complète avec géométrie |
| `POST`  | `/realize` | M_out + modalité → réalisation la plus proche |
| `POST`  | `/pipeline` | Prompt + modalité → trajectoire + réalisation |

Voir `README-api.md` pour la documentation complète.
