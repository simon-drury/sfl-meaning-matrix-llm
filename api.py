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
  POST /realize         M_out + modality + lang -> realization (EN,ES,PT,IT,ZH)
  POST /pipeline        lang_in + modality + lang_out -> trajectory + realization

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
    build_pilot_pt,
    build_pilot_it,
    build_pilot_zh,
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

# Pilot encoders: lang code -> encoder function
ENCODERS = {
    "EN": encode_en,
    "ES": encode_es,
}

# Realization registry: "modality:lang" -> VocabularySpace
# Add new languages or modalities here. The pipeline does not change.
REALIZERS: dict = {
    "text:EN": build_pilot_en(),
    "text:ES": build_pilot_es(),
    "text:PT": build_pilot_pt(),
    "text:IT": build_pilot_it(),
    "text:ZH": build_pilot_zh(),
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
    return np.array([s.to_vector() for s in traj.states])


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    lang: str = Field("EN", description="Pilot input language: EN or ES")


class StepOut(BaseModel):
    t:             int
    label:         str
    state:         List[float]
    displacement:  Optional[float] = None
    curvature:     Optional[float] = None
    driver:        Optional[str]   = None


class AnalyzeResponse(BaseModel):
    lang:         str
    steps:        List[StepOut]
    geodesic_energy: float


class RealizeRequest(BaseModel):
    M_out:    List[float]   = Field(..., description="Meaning state vector, length 6")
    modality: str           = Field("text", description="Output modality")
    lang:     Optional[str] = Field("EN",   description="Output language: EN, ES, PT, IT, ZH")
    k:        int           = Field(5,      description="Number of candidates")


class Candidate(BaseModel):
    form:     str
    distance: float


class RealizeResponse(BaseModel):
    modality:   str
    lang:       Optional[str]
    best:       str
    candidates: List[Candidate]


class PipelineRequest(BaseModel):
    lang_in:  str           = Field("EN",   description="Input pilot language: EN or ES")
    modality: str           = Field("text",  description="Output modality")
    lang_out: Optional[str] = Field("EN",   description="Output language: EN, ES, PT, IT, ZH")
    k:        int           = Field(5)


class PipelineResponse(BaseModel):
    lang_in:         str
    modality:        str
    lang_out:        Optional[str]
    steps:           List[StepOut]
    geodesic_energy: float
    realization:     RealizeResponse


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SFL Meaning Matrix",
    description=(
        "Meaning before form. Language after meaning. "
        "The transformer operates on meaning states in the semiotic manifold M. "
        "Modality and language are edge parameters only. "
        "Realization languages: EN, ES, PT, IT, ZH."
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
        geodesic_energy=round(analysis.path_loss, 4),
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


@app.get("/langs")
def langs():
    """Return available input encoders and output realization languages."""
    return {
        "input_langs":  list(ENCODERS.keys()),
        "output_langs": list({k.split(":")[1] for k in REALIZERS.keys()}),
        "modalities":   list({k.split(":")[0] for k in REALIZERS.keys()}),
    }


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    """Run the pilot encoder and return the full MeaningTrajectory with geodesic geometry."""
    return _run_analyze(req.lang)


@app.post("/realize", response_model=RealizeResponse)
def realize(req: RealizeRequest):
    """
    Given a meaning state M_out, return the nearest semiotic unit
    in the requested language vocabulary. Output edge only.
    Languages: EN, ES, PT, IT, ZH.
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
    lang_in drives the trajectory. lang_out drives the realization.
    The two are independent. No translation step.
    Input langs: EN, ES. Output langs: EN, ES, PT, IT, ZH.
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
        geodesic_energy=analyze_resp.geodesic_energy,
        realization=realize_resp,
    )
