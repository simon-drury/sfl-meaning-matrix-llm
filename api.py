#!/usr/bin/env python3
"""
api.py
FastAPI wrapper for the SFL Meaning Matrix pipeline.

The transformer is modality-blind.
It operates on meaning states in M -- nothing else.
The modality of input and output is handled at the edges.

Endpoints
---------
  GET  /health          liveness check
  GET  /dims            manifold dimension names and ranges
  POST /analyze         prompt -> MeaningTrajectory (geometry only)
  POST /realize         M_out + modality -> realization in output space
  POST /pipeline        prompt + modality -> trajectory + realization

Run
---
  pip install fastapi uvicorn numpy
  uvicorn api:app --reload
  # -> http://127.0.0.1:8000
  # -> http://127.0.0.1:8000/docs  (auto-generated interactive docs)
"""

from __future__ import annotations

import numpy as np
from typing import List, Optional, Tuple
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from sfl_matrix_engine import MeaningUnit, MeaningTrajectory, parse_prompt
from sfl_manifold import compute_path_geometry
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

# ---------------------------------------------------------------------------
# Realization registry
# Modality -> realization function.
# Add new modalities here without touching the pipeline.
# ---------------------------------------------------------------------------

REALIZERS: dict = {}


def _register_text_realizers():
    REALIZERS["text:EN"] = build_pilot_en()
    REALIZERS["text:ES"] = build_pilot_es()


_register_text_realizers()


def get_realizer(modality: str, lang: Optional[str]) -> VocabularySpace:
    """
    Retrieve the realizer for a given modality and language.
    Returns the VocabularySpace (or future modality equivalent).
    Raises 404 if not registered.
    """
    key = f"{modality}:{lang}" if lang else modality
    if key not in REALIZERS:
        available = list(REALIZERS.keys())
        raise HTTPException(
            status_code=404,
            detail=f"No realizer registered for '{key}'. "
                   f"Available: {available}",
        )
    return REALIZERS[key]


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    prompt: str = Field(..., description="Input prompt in any language")
    lang: str   = Field("EN", description="ISO 639-1 language code of the prompt")


class StepGeometry(BaseModel):
    t:     int
    state: List[float]
    label: Optional[str]  = None
    delta: Optional[float] = None   # displacement magnitude ||delta_t||
    kappa: Optional[float] = None   # curvature
    phi:   Optional[str]   = None   # dominant driver (dimension name)


class AnalyzeResponse(BaseModel):
    lang:        str
    steps:       List[StepGeometry]
    path_length: float


class RealizeRequest(BaseModel):
    M_out:    List[float] = Field(..., description="Meaning state, length n_dim")
    modality: str         = Field("text",  description="Output modality")
    lang:     Optional[str] = Field("EN", description="Target language (for text modality)")
    k:        int           = Field(5,    description="Number of candidates to return")


class Candidate(BaseModel):
    form:     str
    distance: float


class RealizeResponse(BaseModel):
    modality:   str
    lang:       Optional[str]
    best:       str
    candidates: List[Candidate]


class PipelineRequest(BaseModel):
    prompt:   str           = Field(..., description="Input prompt")
    lang_in:  str           = Field("EN",  description="Input language")
    modality: str           = Field("text", description="Output modality")
    lang_out: Optional[str] = Field("EN",  description="Output language (text modality)")
    k:        int           = Field(5,     description="Realization candidates")


class PipelineResponse(BaseModel):
    lang_in:     str
    modality:    str
    lang_out:    Optional[str]
    trajectory:  List[StepGeometry]
    path_length: float
    realization: RealizeResponse


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SFL Meaning Matrix",
    description=(
        "Meaning before form. Language after meaning. "
        "The transformer is modality-blind: it operates on meaning states "
        "in the semiotic manifold M. Realization is a pluggable edge process."
    ),
    version="0.1.0",
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/dims")
def dims():
    """Return the manifold dimension names and ranges."""
    return {"n_dim": N_DIM, "dims": DIMS}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    """
    Parse a prompt into a MeaningTrajectory and compute path geometry.
    Returns the full trajectory with delta, kappa, phi per step.
    """
    try:
        trajectory: MeaningTrajectory = parse_prompt(req.prompt, lang=req.lang)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    states = np.array([u.state for u in trajectory.units])
    labels = [u.label for u in trajectory.units]

    geometry = compute_path_geometry(states)
    # geometry keys: deltas, magnitudes, kappas, drivers, path_length

    steps = []
    for t, (state, label) in enumerate(zip(states, labels)):
        step = StepGeometry(
            t=t,
            state=state.tolist(),
            label=label,
        )
        if t > 0:
            step.delta = float(geometry["magnitudes"][t - 1])
            step.kappa = (
                float(geometry["kappas"][t])
                if not np.isnan(geometry["kappas"][t])
                else None
            )
            step.phi = DIMS[geometry["drivers"][t - 1]]["name"]
        steps.append(step)

    return AnalyzeResponse(
        lang=req.lang,
        steps=steps,
        path_length=float(geometry["path_length"]),
    )


@app.post("/realize", response_model=RealizeResponse)
def realize(req: RealizeRequest):
    """
    Given a meaning state M_out and an output modality,
    return the nearest realization in that modality space.

    The transformer has no knowledge of the modality.
    This endpoint is the output edge.
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
    Full pipeline: prompt -> MeaningTrajectory -> realization.

    The transformer is modality-blind throughout.
    lang_in and lang_out are edge parameters only.
    """
    # 1. Parse and compute geometry
    analyze_resp = analyze(AnalyzeRequest(prompt=req.prompt, lang=req.lang_in))

    # 2. Take final meaning state as M_out
    M_out_list = analyze_resp.steps[-1].state

    # 3. Realize
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
        trajectory=analyze_resp.steps,
        path_length=analyze_resp.path_length,
        realization=realize_resp,
    )
