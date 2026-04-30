# API FastAPI : Pipeline Sémantique

Wrapper stateless exposant la pipeline complète via HTTP.

## Endpoints

### POST /analyze
Analyse un prompt, retourne trajectoire.

### POST /realize  
Donne un état M, retourne réalisations lexique.

### POST /pipeline
End-to-end : prompt → trajectory → realization.

### GET /health
Retourne statut ok.

### GET /dims
Retourne noms et plages des 6 dimensions.