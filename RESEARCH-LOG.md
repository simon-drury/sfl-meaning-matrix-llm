# Research Log

Timestamped record of decisions, insights, and directions.
Code does not belong here. This is the jotter.

---

## 2026-10-20

### Versioning and debug report — data coverage and coordinate order

Commits on builders-yard:

0. Commit 4b0a0ec adds two new files and modifies no existing file:
   data_audit.py and train_sfl_pi_windows.py.
1. This commit changes RESEARCH-LOG.md and adds a cross-reference and
   coordinate-order note to the docstrings of the two new files.

Debug finding (repository evidence). data/empirical_trajectories.jsonl
stores 500 meaning states as one uninterrupted sequence with no document
boundaries. The TrajectoryDataset loader in train_sfl_pi.py groups
consecutive vector_9d records into a single trajectory and truncates it
to max_seq_len = 64. The default configuration therefore trains on one
64-state trajectory and leaves 436 records unused.

Candidate material. The recorded historical run reports 25 epochs over
500 records. Under the current loader the file yields one 64-state
trajectory. The historical configuration is not reproduced by the current
default code path and requires verification of the loader or data version
used before the historical metrics are cited.

Repairs. data_audit.py reports record count, per-coordinate variation,
zero-delta steps and the no-change baseline MSE for the data file.
train_sfl_pi_windows.py trains the SFL-pi next-state objective on sliding
windows over all records, holds out the final 20 per cent of records, and
records one-step error, recursive rollout error and the no-change
baseline for the held-out records.

Evaluation rule. A trained model is informative only if its held-out
error is lower than the no-change baseline that repeats the previous
state. Most coordinates vary little in the present data, so this
comparison is mandatory in every run report.

### Coordinate order contract (repository evidence)

The data file and download_and_ingest_treebank.py store the meaning-state
matrix with metafunctions as rows and contextual variables as columns:

M_t = [ m_ID,FL  m_ID,TN  m_ID,MD ]
      [ m_IP,FL  m_IP,TN  m_IP,MD ]
      [ m_TX,FL  m_TX,TN  m_TX,MD ]

Row-major flattening gives:

z_t = (m_ID,FL, m_ID,TN, m_ID,MD, m_IP,FL, m_IP,TN, m_IP,MD,
       m_TX,FL, m_TX,TN, m_TX,MD)

The 16-element v7 document specifies the transpose: rows field, tenor,
mode; columns ideational, interpersonal, textual. Under that convention:

z'_t = (m_FL,ID, m_FL,IP, m_FL,TX, m_TN,ID, m_TN,IP, m_TN,TX,
        m_MD,ID, m_MD,IP, m_MD,TX)

Every coordinate swaps its row and column index, so z'_t = P z_t for the
9-element permutation P that exchanges (i,j) with (j,i). Code that assumes
one convention and reads data stored in the other misreads every cell.
The data is the contract. The v7 document is the item to correct, not the
data. The register-major order already present in the olmo repository
adapter comment (olmo/sfl/trainer_integration.py) is the likely source of
the v7 order.

### Why metafunctions dominate (direct specification)

All meaning is simultaneously ideational, interpersonal and textual. The
metafunctions are the substrate of the meaning state. Field, tenor and
mode are contextual configuration. The diagonal correlations (field with
ideational, tenor with interpersonal, mode with textual) are typical
correlations, resonance after Hasan, not exclusive pairings; the six
off-diagonal readings remain under investigation (decision D001,
answers pending). Metafunctions are therefore rows, the dominant
substrate; contextual variables are columns.

### Research note — configuration choice in the meaning matrix: Halliday or Martin

Research question. Does the meaning matrix allow an analyst to operate
the architecture under a Hallidayan or a Martinian organization of
context, as an explicit configuration choice?

Finding. Yes, at the level of the meaning state. The nine cells are the
Cartesian product of the metafunctions and the contextual variables.
Both positions accept the projection of experiential meaning onto field,
interpersonal meaning onto tenor and textual meaning onto mode (Martin
1992, p. 494-496, as quoted in Matthiessen 2015). The interaction surface
is shared ground; the disagreement is the organizing priority.

0. Metafunction-dominant configuration (recorded contract). Rows are
   the metafunctions, the substrate; contextual variables are columns.
   Substrate covariance is M M^T, metafunction by metafunction. This
   expresses Halliday's account: register is a semantic variety of
   language, the meanings at risk, a linguistic category rather than a
   contextual one (Halliday 1978, p. 111, as quoted in Matthiessen 2015).
1. Register-dominant configuration. Rows are field, tenor and mode.
   Substrate covariance is M^T M, register by register. This expresses
   Martin's account: register is the semiotic system constituted in the
   contextual variables field, tenor and mode, the metafunctionally
   organised connotative semiotic between language and genre, a semiotic
   system in its own right (Martin 1992, p. 501-502, as quoted in
   Matthiessen 2015).

Formal statement. The configurations are transposes: z' = pi(M^T) = P z_t
for the 9-element permutation P exchanging (i,j) with (j,i).
Permutation-indifferent operations (uniform coordinate-wise error) are
invariant under the choice; the configurations differ only where the
architecture privileges an axis: the flattening contract, covariance
primacy, and row-allocated attention.

Scope. The claim is bounded. The architecture hosts both readings at the
level of the meaning state. It implements neither scholar's full model of
context. Martin's stratified context (ideology, genre, register; Martin
1992, p. 496) and Halliday's cline of instantiation (Halliday 1991) are
not represented by the nine cells. The configuration choice does not
resolve decision D001: both positions theorize the diagonal projection,
and the six off-diagonal readings remain open under either
configuration.

Recorded detail. Martin's endnote 7 records that the divergence
originated as a misunderstanding of Halliday's model that was extended
rather than undone (Martin 1992, p. 589, as quoted in Matthiessen 2015).

Research consequence. The disagreement has been argued on paper since
the 1980s. The matrix makes the organizing-priority divergence
operational: a two-configuration comparison under the same data and
objective is a defined experiment. Matthiessen (2015) notes that
computational SFL work is important work that has sometimes been
overlooked by researchers concerned mainly with manual discourse
analysis; the experiment gives the divergence a measurable form.

Source verification. Quotations from Martin (1992) are quoted as given
in Matthiessen (2015). Direct verification against Martin (1992) at the
cited pages remains open and is required before publication of the
accompanying paper.

References. Halliday, M.A.K. (1978). Language as Social Semiotic.
Edward Arnold. Martin, J.R. (1992). English Text: System and Structure.
John Benjamins. Matthiessen, C.M.I.M. (2015). Modelling context and
register: the long-term project of registerial cartography. Letras,
Santa Maria 25(50), 15-90.

---

## 2026-04-27

### NLP retained at the output edge — architectural decision

The realizer (`sfl_realize.py`) uses k-nearest-neighbour retrieval (k-NN)
to map a meaning state M_out to a lexical item in V_L. This is standard NLP.

This is not a compromise. It is a deliberate boundary decision:

- The architecture does not discard NLP. It relocates it.
- NLP operates at the output edge only, after meaning has been computed.
- The transformer (Pathformer) never sees token sequences or lexical embeddings.
  It operates on meaning states in M throughout.
- k-NN at the output edge can use GPU-accelerated vector search (FAISS) at scale.
  It is hardware-compatible and well-understood.
- The realizer is modular and swappable: k-NN now (mv0), learned decoder later (mv1+).
  The architecture does not change when the realizer is upgraded.

The key distinction: NLP does the retrieval. SFL does the reasoning.
The decoder is not corrupt — it is correctly scoped.

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
2. Assign 9-dim (3x3) meaning state to each unit
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
