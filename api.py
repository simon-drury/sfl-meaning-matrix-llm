#!/usr/bin/env python3
"""
api.py
FastAPI wrapper for the SFL Meaning Matrix pipeline.

The transformer is modality-blind.
It operates on meaning states in M -- nothing else.
Modality of input and output is handled at the edges.

Endpoints
---------
  GET  /health          liveness check
  GET  /dims            manifold dimension names and ranges
  POST /analyze         lang -> MeaningTrajectory geometry (EN or ES pilot)
  POST /realize         M_out + modality -> realization in output space
  POST /pipeline        lang + modality -> trajectory + realization

Run
---
  uvicorn api:app --reload
  # -> http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import math
import numpy as np
from typing import List, Optional, Tuple
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from sfl_matrix_engine import MeaningTrajectory, encode_en, encode_es
from sfl_manifold import compute_manifold, ManifoldAnalysis
from sfl_realize import (
    VocabularySpace,
    build_pilot_en,
    build_pilot_es,
    realize_trajectory,
)

# ---------------------------------------------------------------------------
# Manifold constants
# ---------------------------------------------------------------------------

DIMS = [
    {"name": "ideational",    "range": [-1.0, 1.0]},
    {"name": "field",         "range": [-1.0, 1.0]},
    {"name": "interpersonal", "range": [-1.0, 1.0]},
    {"name": "tenor",         "range": [-1.0, 1.0]},
    {"name": "textual",       "range": [-1.0, 1.0]},
    {"name": "mode",          "range": [-1.0, 1.0]},
]

N_DIM = len(DIMS)

# Pilot encoders: maps lang code -> encoder function
ENCODERS = {
    "EN": encode_en,
    "ES": encode_es,
}

# Realization registry: modality:lang -> VocabularySpace
REALIZERS: dict = {
    "text:EN": build_pilot_en(),
    "text:ES": build_pilot_es(),
}


def get_realizer(modality: str, lang: Optional[str]) -> VocabularySpace:
    key = f"{modality}:{lang}" if lang else modality
    if key not in REALIZERS:
        raise HTTPException(
            status_code=404,
            detail=f"No realizer for '{key}'. Available: {list(REALIZERS.keys())}",
        )
    return REALIZERS[key]


def trajectory_to_states(traj: MeaningTrajectory) -> np.ndarray:
    """Extract ordered state vectors from a MeaningTrajectory."""
    return np.array([s.to_vector() for s in traj.states])


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    lang: str = Field("EN", description="Pilot language: EN or ES")


class StepOut(BaseModel):
    t:             int
    label:         str
    state:         List[float]
    displacement:  Optional[float] = None
    curvature:     Optional[float] = None
    driver:        Optional[str]   = None


class AnalyzeResponse(BaseModel):
    lang:       str
    steps:      List[StepOut]
    path_loss:  float


class RealizeRequest(BaseModel):
    M_out:    List[float]       = Field(..., description="Meaning state, length 6")
    modality: str               = Field("text")
    lang:     Optional[str]     = Field("EN")
    k:        int               = Field(5)


class Candidate(BaseModel):
    form:     str
    distance: float


class RealizeResponse(BaseModel):
    modality:   str
    lang:       Optional[str]
    best:       str
    candidates: List[Candidate]


class PipelineRequest(BaseModel):
    lang_in:  str           = Field("EN",   description="Pilot language: EN or ES")
    modality: str           = Field("text")
    lang_out: Optional[str] = Field("EN")
    k:        int           = Field(5)


class PipelineResponse(BaseModel):
    lang_in:     str
    modality:    str
    lang_out:    Optional[str]
    steps:       List[StepOut]
    path_loss:   float
    realization: RealizeResponse


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SFL Meaning Matrix",
    description=(
        "Meaning before form. Language after meaning. "
        "The transformer operates on meaning states in the semiotic manifold M. "
        "Modality is handled at the edges only."
    ),
    version="0.1.0",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_analyze(lang: str) -> AnalyzeResponse:
    lang = lang.upper()
    if lang not in ENCODERS:
        raise HTTPException(
            status_code=404,
            detail=f"No pilot encoder for lang='{lang}'. Available: {list(ENCODERS.keys())}",
        )
    traj: MeaningTrajectory = ENCODERS[lang]()
    analysis: ManifoldAnalysis = compute_manifold(traj)

    states = trajectory_to_states(traj)
    labels = [s.label for s in traj.states]

    # Build step list: step 0 has no geometry (it is M0)
    geo_by_t = {sg.t: sg for sg in analysis.steps}

    steps = []
    for t, (state, label) in enumerate(zip(states, labels)):
        sg = geo_by_t.get(t)
        steps.append(StepOut(
            t=t,
            label=label,
            state=state.tolist(),
            displacement=round(sg.displacement, 4) if sg else None,
            curvature=(
                round(sg.curvature, 4)
                if sg and not math.isnan(sg.curvature)
                else None
            ),
            driver=sg.dominant_driver if sg else None,
        ))

    return AnalyzeResponse(
        lang=lang,
        steps=steps,
        path_loss=round(analysis.path_loss, 4),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/dims")
def dims():
    return {"n_dim": N_DIM, "dims": DIMS}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    """
    Run the pilot encoder for the requested language and return
    the full MeaningTrajectory with path geometry.
    """
    return _run_analyze(req.lang)


@app.post("/realize", response_model=RealizeResponse)
def realize(req: RealizeRequest):
    """
    Given a meaning state M_out and an output modality,
    return the nearest realization in that modality space.
    This endpoint is the output edge. The transformer is not involved.
    """
    if len(req.M_out) != N_DIM:
        raise HTTPException(
            status_code=422,
            detail=f"M_out must have {N_DIM} dimensions, got {len(req.M_out)}.",
        )
    vocab = get_realizer(req.modality, req.lang)
    M_out = np.array(req.M_out)
    candidates_raw: List[Tuple[str, float]] = vocab.nearest(M_out, k=req.k)

    return RealizeResponse(
        modality=req.modality,
        lang=req.lang,
        best=candidates_raw[0][0],
        candidates=[
            Candidate(form=w, distance=round(d, 4))
            for w, d in candidates_raw
        ],
    )


@app.post("/pipeline", response_model=PipelineResponse)
def pipeline(req: PipelineRequest):
    """
    Full pipeline: pilot encoder -> MeaningTrajectory -> realization.
    The transformer is modality-blind throughout.
    lang_in and lang_out are edge parameters only.
    """
    analyze_resp = _run_analyze(req.lang_in)
    M_out_list = analyze_resp.steps[-1].state

    realize_resp = realize(RealizeRequest(
        M_out=M_out_list,
        modality=req.modality,
        lang=req.lang_out,
        k=req.k,
    ))

    return PipelineResponse(
        lang_in=req.lang_in,
        modality=req.modality,
        lang_out=req.lang_out,
        steps=analyze_resp.steps,
        path_loss=analyze_resp.path_loss,
        realization=realize_resp,
    )
