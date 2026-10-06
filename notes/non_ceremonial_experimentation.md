# Non-Ceremonial Experimentation Directive

## Audience

This note is for automated contributors, agentic coding systems, and human collaborators working on the SFL Meaning Matrix LLM.

## Directive

Do not introduce testing, validation, or process whose primary value is ceremonial: a small proof that a narrow command can run, a toy demonstration that does not interrogate the actual model, or an abstract checklist detached from a live architectural question. Such work can produce briefly satisfying proofs of concept while yielding little durable knowledge about the system.

The repository should be developed through substantive, inspectable experiments:

- Build the actual capability under investigation.
- Run it on the real empirical data and at a scale sufficient to expose its behaviour and limits.
- Preserve the configuration, data assumptions, outputs, failures, and diagnostic traces needed to inspect and reproduce what happened.
- Use observed failure modes to determine the next repair or architectural change.

## What counts as useful testing

Testing is justified when it directly protects or reveals the working system: for example, when it prevents a known regression in a relied-upon path, captures a real failure mode, or instruments a substantive training run so that model behaviour can be inspected.

A minimal smoke check may be added later as quiet maintenance infrastructure if it protects an established workflow. It must not be treated as the research result, a gate that displaces real experiments, or an end in itself.

## SFL-pi application

For SFL-pi, the immediate work is to train the real causal 9D trajectory model on the empirical trajectories, inspect predictions and rollouts, preserve evidence of its failure boundaries, and then modify the architecture in response to those observations. Do not substitute toy runs, ceremonial validation, or generic engineering ritual for that loop.
