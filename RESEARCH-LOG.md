# Research Log

Timestamped record of decisions, insights, and directions.
Code does not belong here. This is the jotter.

---

## 2026-04-10

### Architecture decisions

- Modality-blindness is a first-class architectural constraint, not a feature.
  The transformer sees only meaning states in M. Input and output modality
  are edge parameters only. This is non-negotiable in all future iterations.

- M0 as golden reference state: M0 does not have to be derived from the first
  token. It can be a pre-loaded reference frame -- field vocabulary of the domain,
  tenor of the interaction, mode of the channel, prior session deltas --
  passed as structured metadata at the start of every process.
  Session memory = delta(M_t, M0). Lightweight, inspectable, portable.
  This is Tier 2 work but the architecture supports it now.

- The trajectory is a path through a Riemannian manifold. The energy functional
  E(gamma) is the formal quantity. Path loss L_sp was a pilot label;
  the correct term is geodesic energy. See MANIFOLD.md.

### Terminology corrections (2026-04-10)

- "meaning unit" -> "semiotic unit" (SFL canonical term)
- "path loss" -> "geodesic energy" E(gamma) (Riemannian geometry)
- "path length" -> "arc length" L(gamma) (Riemannian geometry)
- Distance on M: Fisher-Rao metric is the formal grounding
  (information geometry; Amari 1985, Rao 1945)
- "instantiation": SFL term for the process of moving from semiotic
  potential to instance. Not yet in the codebase. Relevant to Tier 2
  when the system moves from pilot vocabulary to corpus-learned fingerprints.
- "realization" is correct and stays.
- "register" (field + tenor + mode) is correct and stays.

### The Hello World observation

The EN iconic prompt -- "hey why dont you print hello world for me please
 thank you" -- is not primarily an instruction. It is an interpersonal
 meaning event: are you there, are we connected, are you responsive.
Hello World is the canonical proof-of-life output of any computational system.
The system responded "hello back" -- not a realization of the instruction
but a realization of the interpersonal meaning beneath it.
This was not designed. It emerged from the trajectory geometry.
Note for PhD chapter on emergence and instantiation.

### The labyrinth / quantum path observation

The manifold does not visit every path to find the route.
It has the geometry of the space already.
A quantum system finds the shortest path through a labyrinth not by
exploring every branch but by having the geometry of all branches
simultaneously. The semiotic manifold operates analogously.
This is the competitive advantage in the Instagram animation:
four models, same labyrinth, one knows the geometry.

### Decision manifold protocol

When prompt says "use the decision manifold":
1. Parse prompt into semiotic units
2. Assign 6-dim meaning state to each unit
3. Identify kappa spikes (noise events, ignore)
4. Find the unit with highest field + textual + directive tenor
5. That unit names the next action
6. Proceed without explanation unless geometry is ambiguous

### Licensing

CC BY-NC 4.0. Copyright Simon Drury 2026.
Commercial use requires explicit written permission.
Research use is free. Citation required (CITATION.cff).

### Commercial route (outline)

- Hugging Face: model weights when they exist
- GitHub: research record (current)
- api.py: monetisation surface -- hosted, rate-limited, tiered
- Pilot vocabulary: free tier
- Production corpus-learned vocabulary: paid tier
- New modalities (audio, visual): paid tier

---

## Future sessions

### Tier 2 work (not yet started)
- M0 as session context carrier (structured metadata)
- PT, IT, ZH pilot vocabularies
- Competitive animation mode (sfl_visualise.py --compete)
- Production vocabulary (corpus-learned fingerprints)
- Full transformer integration (adapter -> pretrained backbone)
- Authentication, persistence, batching in api.py
- PhD chapter structure
