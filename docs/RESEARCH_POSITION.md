# Research Position

## Purpose

This repository is an experimental implementation of an SFL-informed language-modelling architecture. It investigates whether an explicit representation of meaning as a structured semiotic state can supplement or, in defined experiments, replace purely token-derived input representations.

The work is organised around a 3 x 3 meaning-state matrix. Its rows represent the three metafunctions of systemic functional linguistics:

- ideational
- interpersonal
- textual

Its columns represent the contextual register variables:

- field
- tenor
- mode

These axes must remain distinct. Field, tenor, and mode are not metafunctions; they describe contextual variation. The matrix is therefore a representational device for modelling relations between metafunctional and register dimensions. Vectorisation or projection to another space is a downstream computational operation, not a redefinition of the linguistic categories.

## What Is Implemented

The repository contains working research components for parsing and encoding meaning states, manifold and trajectory operations, attention experiments, model adapters, realisation, visualisation, training, corpus ingestion, an API, and pipeline tests. The code and accompanying materials should be read as a research prototype and an evolving laboratory record, rather than as a finished general-purpose language model.

The current implementation provides a basis for investigating questions such as:

- Can structured meaning-state inputs improve control of register-sensitive generation?
- Can the representation provide useful interpretability beyond token-level features?
- What information is retained or lost when a 3 x 3 meaning-state is projected into model embedding spaces?
- How does the approach compare with token-only, embedding-only, and hybrid baselines?
- Can the architecture support multilingual or cross-linguistic experiments without treating subword segmentation as the primary semantic representation?

## Research Programme

The next research phase is empirical. It requires explicit task definitions, versioned annotation and corpus procedures, reproducible training configurations, baselines, ablation studies, quantitative metrics, qualitative linguistic analysis, and documented limitations.

The central claim under examination is deliberately modest: an SFL-informed, explicit meaning-state representation may offer a valuable inductive bias for selected language-modelling tasks. The repository does not claim to have demonstrated a replacement for contemporary token-based LLMs.

## Authorship and Curation

> **[sjd]** I have deliberately used generative AI throughout the development and documentation of this project, including for drafting, explanation, code exploration, and critique. The resulting material is nevertheless heavily curated: I select the research questions, linguistic commitments, architecture decisions, experimental priorities, source material, and final revisions. AI-generated text and code are treated as working material, not as unexamined authorship.

This note is included for transparency. The project remains accountable to normal standards of scholarly attribution, verification, reproducibility, and critical evaluation.

## How To Read This Repository

Start with `README.md` for the current architecture and entry points. The implementation files and notebooks document experiments at different stages of maturity. `RESEARCH-LOG.md` records the evolving rationale, while tests and scripts should be understood as evidence of prototyping activity rather than as a complete evaluation suite.
