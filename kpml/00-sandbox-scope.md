# KPML sandbox scope

## Core position

The SFL Meaning Matrix model remains the project core.

## Purpose of this sandbox

This branch evaluates KPML/Nigel as one possible realisation adapter: a route for mapping a core meaning state into grammatical language.

KPML/Nigel is not adopted as the project's sole or permanent output layer.

## Architectural rule

The core should expose a stable, realiser-neutral meaning-state interface. Each external grammar, corpus method, decoder, or retrieval system receives its own adapter.

## Consequence

A KPML/Nigel result is evidence about one adapter path. It does not commit the project to KPML, prevent comparison with other SFL resources, or require changes to the trained core model.

## Experiment sequence

1. Establish KPML/Nigel's native semantic-input contract.
2. Run one native example unchanged.
3. Record source, environment, input, procedure, output, and limitations.
4. Compare that contract with one exported core meaning state.
5. Build a minimal adapter only if the comparison supports it.

## Documentation rule

Record decisions, sources, environments, inputs, outputs, limitations, and negative results in the repository rather than leaving them only in chat.
