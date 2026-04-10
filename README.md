# SFL-first LLM: Meaning-Matrix Architecture

## Purpose
This project proposes a language model architecture in which lexical tokenization is not the primary computational substrate. Instead, lexical input is immediately compiled into a sequence of meaning-making matrices grounded in Systemic Functional Linguistics (SFL), and subsequent computation proceeds entirely in meaning space.

The goal is not to predict a lexical path but to compute a meaning path. Neural networks are used as calculators over meaning states, not as the theory of meaning itself.

## Core claim
A prompt should be processed as a trajectory through a functional-semantic manifold rather than as a sequence of vocabulary items. The model begins with lexical surface form only long enough to project it into meaning space, then discards lexical items. Internal computation is performed only over meaning states and their deltas.

## Initial pilot representation
The pilot uses a sequence of 3×2 matrices. These are also interpretable as 6-point vectors.

| Metafunction / context pairing | Variable |
|---|---|
| Ideational | Ideational |
| Field | Field |
| Interpersonal | Interpersonal |
| Tenor | Tenor |
| Textual | Textual |
| Mode | Mode |

A convenient matrix layout for the first pilot is:

```text
[ Ideational     Field ]
[ Interpersonal  Tenor ]
[ Textual        Mode  ]
```

This format is not intended as a rigid categorical box model. The six values are treated as free-floating, overlapping, and continuous rather than mutually exclusive. The underlying geometry is better understood as a semantic manifold with six primary regions or nodes.

## Geometric intuition
The first working intuition is a continuous semantic space with six primary nodes:

1. Ideational
2. Interpersonal
3. Textual
4. Field
5. Tenor
6. Mode

These nodes are not discrete compartments. They are better imagined as overlapping Gaussian regions in a shared space, possibly on or within a sphere-like manifold. A single meaning state is therefore a weighted position across all six regions rather than a discrete choice among them.

This means the model processes a meaning trajectory, not a token stream.

## Matrix engine
The matrix engine replaces conventional tokenization.

### What a standard tokenizer does
A standard tokenizer:
- splits text into subword or wordpiece units,
- maps them to vocabulary IDs,
- passes lexical embeddings forward.

In this setup, lexical form is primary and meaning is inferred indirectly.

### What the matrix engine does
The matrix engine:
- receives lexical input once,
- projects it immediately into a sequence of meaning-making matrices,
- assigns values over Ideational, Interpersonal, Textual, Field, Tenor, and Mode,
- discards lexical items after projection,
- sends only matrices and matrix deltas downstream.

So the downstream model never processes token IDs as its main substrate. It processes meaning states.

## Delta principle
The sequence is expected to be mostly delta-carrying rather than full-state repetition.

- The initial state may be a fuller matrix.
- Subsequent matrices primarily encode how meaning has shifted.
- A matrix therefore represents a local semantic update, not a lexical event.

This can be written schematically as:

```text
M0, Δ1, Δ2, Δ3, ... Δt
```

where each delta records changes in the six-dimensional meaning state.

The aim is to reduce redundancy and keep the computation focused on semantic movement rather than on repeating a full lexical or semantic frame at every step.

## Transformer stage
After encoding, the matrices are passed to transformer-like mechanisms, but these are reconceived as attention clusters over meaning dimensions.

The first pilot assumption is six attention heads or six primary attention clusters corresponding to:

1. Ideational
2. Interpersonal
3. Textual
4. Field
5. Tenor
6. Mode

These heads do not attend over lexical tokens as primary units. They attend over sequences of meaning states and deltas. Their task is to locate, compare, and propagate meaningful contextual change within the semantic manifold.

## The role of neural networks
Neural networks are retained, but only as computational instruments.

They are not taken to define meaning. The representational theory comes from SFL. The neural network is the numerical machinery that:
- helps map text into meaning space,
- computes over trajectories and deltas,
- supports communication among functional/contextual attention clusters,
- assists realization back into lexical output.

In short, the neural network is the tool for the calculation, not the calculation itself.

## Internal ontology
This architecture changes the ontology of the model.

### Standard LLM ontology
- Internal state is primarily lexical/sublexical.
- Meaning is an emergent by-product of token prediction.
- Syntax and distribution dominate the computation.

### Proposed ontology
- Internal state is functional-semantic and contextual.
- Meaning is explicit and primary.
- Lexis is only an input/output realization layer.
- Computation proceeds in meaning space.

## Output stage
Outputs are also represented first as meaning-making matrices.

Only after the semantic trajectory has been computed does the system realize lexical output by selecting vocabulary items that best correspond to the computed meaning states. In this sense, lexical items are realizational selections from an already-computed semantic configuration.

## Theoretical stance
This design is grounded in Systemic Functional Linguistics rather than in a purely NLP-first view of language.

Key commitments:
- Meaning is function in context.
- The three metafunctions and the contextual variables are not rigidly discrete.
- The architecture is concerned with instantiation dynamics, not preserving lexical chains.
- The system computes over contextualized meaning movement.

## Working analogies
Two analogies were identified as productive for later development.

### 1. Lorenz / three-body style dynamics
Meaning trajectories may behave like continuous, sensitive flows through a structured state space:
- small changes in initial conditions can produce major trajectory shifts,
- trajectories may orbit, bend, fold, or move between attractor-like regions,
- discourse can be interpreted as a path through a dynamic semantic field.

### 2. Quantum maze analogy
The internal computation may be usefully imagined not as many lexical walkers exploring separate paths, but as one instantiated meaning-state distributed across a structured possibility space. Attention then acts more like coordinated projection across dimensions than serial token stepping.

These are analogies, not final mathematical commitments, but they help clarify the intended non-lexical computational picture.

## Near-term design questions
The following questions remain open and should guide the next design phase:

1. What exact topology should the meaning space have: plane, sphere, manifold, Gaussian mixture, or another form?
2. What is the primitive numeric status of each value: scalar, vector, distribution, or hybrid?
3. What exactly is a delta: displacement, reweighting, or constrained update?
4. What composition operator combines successive meaning states?
5. How should realization from meaning states back into lexical output be scored?
6. How should the six primary heads communicate when dimensions overlap strongly?

## Immediate next implementation step
The best next move is not to build the full architecture at once, but to formalize one minimal pilot slice:

- one compact state specification,
- one delta/update rule,
- one tiny example domain,
- one toy realization procedure.

That will allow the meaning-engine hypothesis to be tested before scaling.

## Status
This README records the first-pass conceptual architecture without loss, ready to be pushed to GitHub as the initial project description.
