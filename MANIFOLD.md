# SFL Meaning-Matrix LLM: Semiotic Manifold Architecture

## 1. The meaning space

Let \(\mathcal{M}\) be a 6-dimensional Riemannian manifold. Each point
\(\mathbf{m} \in \mathcal{M}\) is a vector

\[
\mathbf{m} = (m_1, m_2, m_3, m_4, m_5, m_6) \in [-1, 1]^6
\]

whose components correspond, in order, to:
\(m_1\) ideational, \(m_2\) field, \(m_3\) interpersonal,
\(m_4\) tenor, \(m_5\) textual, \(m_6\) mode.

Each dimension is not a discrete value but a **Gaussian distribution**
centred on the parsed value \(\mu_i\) with variance \(\sigma_i^2\):

\[
p(m_i) = \mathcal{N}(\mu_i,\, \sigma_i^2)
\]

A meaning state is therefore a **region** of \(\mathcal{M}\), not a point.

---

## 2. Parsing a prompt: the meaning trajectory

A prompt \(P\) in language \(L\) is segmented into \(n\) meaning units
\(u_1, \ldots, u_n\). Vocabulary is **parked** after this step.

Each unit \(u_t\) produces a delta matrix \(\Delta_t \in \mathbb{R}^{3 \times 2}\).
The cumulative meaning state at step \(t\) is

\[
M_t = \text{clip}\!\left(\sum_{k=0}^{t} \Delta_k,\; -1,\; 1\right)
\]

where \(M_0\) is the initial state encoding the opening unit, and
\(\text{clip}\) keeps all values within \([-1, 1]\).

The result is a **meaning trajectory**

\[
\mathcal{T} = \langle M_0,\, M_1,\, \ldots,\, M_n \rangle \subset \mathcal{M}
\]

a sequence of regions tracing a **path through the semiotic manifold**.

---

## 3. Path geometry: curvature and momentum

Between consecutive states, the displacement vector is

\[
\delta_t = M_t - M_{t-1} \in \mathbb{R}^6
\]

The **local curvature** of the path at step \(t\) is the angle between
successive displacement vectors:

\[
\kappa_t = \arccos\!\left(\frac{\delta_t \cdot \delta_{t+1}}
                              {\|\delta_t\|\,\|\delta_{t+1}\|}\right)
\]

Low \(\kappa_t\) means the path is continuing smoothly in the same
direction — the meaning is developing coherently. High \(\kappa_t\)
indicates a register shift, a change of field, or a sudden evaluative move.

The **path momentum** at step \(t\) is the exponentially weighted
mean of recent displacements:

\[
\mathbf{v}_t = \alpha\,\delta_t + (1 - \alpha)\,\mathbf{v}_{t-1},
\quad \alpha \in (0, 1)
\]

The transformer uses \(\mathbf{v}_t\) to bias the search for the next
coherent region — paths with momentum tend to continue; sharp curvature
signals a genuine semantic event.

---

## 4. The transformer input

The transformer receives \(\mathcal{T}\) as a sequence of 6-dimensional
float vectors. No token IDs. No positional embeddings in the lexical sense.
Position is encoded as **semiotic distance** along the path:

\[
d(M_s, M_t) = \left\| M_t - M_s \right\|_2
\]

The model is not predicting the next token over a vocabulary distribution.
It is finding the next region \(M_{n+1} \in \mathcal{M}\) such that the
extended path \(\langle \mathcal{T},\, M_{n+1} \rangle\) is **geodesically
coherent** with the trajectory so far.

---

## 5. Geodesic coherence and the role of probability

The most coherent continuation is the region that minimises the total
path energy:

\[
M_{n+1}^* = \arg\min_{M \in \mathcal{M}}\;
E\!\left(\langle \mathcal{T},\, M \rangle\right)
\]

where the path energy \(E\) penalises both large displacements and
high curvature:

\[
E(\mathcal{T}) = \sum_{t=1}^{n} \left( \lambda_1 \|\delta_t\|^2
                 + \lambda_2\,\kappa_t^2 \right)
\]

Probability enters not as a distribution over vocabulary but as
**uncertainty on the manifold**: where the local curvature is high
or the Gaussian spread \(\sigma_i\) is large, multiple continuation
regions are plausible. The transformer samples from those; where the
path is smooth and well-constrained, the continuation is near-deterministic.

This is not stochastic token prediction. It is **geodesic search with
bounded uncertainty**.

---

## 6. Post-transformer: de-matrixising

The output of the transformer is a meaning state \(M_{\text{out}} \in \mathcal{M}\).

Lexical items are retrieved by finding the vocabulary elements whose own
semiotic fingerprints \(\mathbf{f}_w \in \mathcal{M}\) minimise distance
to \(M_{\text{out}}\), within language \(L\):

\[
w^* = \arg\min_{w \in \mathcal{V}_L}\;
      \left\| \mathbf{f}_w - M_{\text{out}} \right\|_2
\]

Each language \(L\) has its own vocabulary space \(\mathcal{V}_L\).
There is no translation step. The same \(M_{\text{out}}\) presented
to \(\mathcal{V}_{\text{EN}}\) and \(\mathcal{V}_{\text{ES}}\) produces
two independent, co-equal realizations in their respective languages.

---

## Status

Manifold geometry formalised.  
Next step: implement \(\kappa_t\), \(\mathbf{v}_t\), and path energy \(E\)
as `sfl_manifold.py`.
