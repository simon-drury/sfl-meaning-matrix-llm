# Abstract

> "Language arises in the life of the individual through an ongoing exchange of meanings with significant others."
> M.A.K. Halliday, Language as Social Semiotic (1978)

---

Current transformer architectures model probability distributions over token sequences. The results are often remarkable. They are also, by construction, probabilistic approximations of form. The social conditions under which language is produced, specifically field, tenor, and mode, are not represented in the model.

This paper presents an alternative input architecture. Rather than operating on token sequences, the system encodes each semiotic unit as a position in a nine-dimensional Riemannian manifold parameterised by the SFL metafunctions (ideational, interpersonal, textual) and register variables (field, tenor, mode). The transformer operates on these meaning states directly. Lexical output is realised independently per language at the output edge. The social context of the interaction is encoded once, in a reference state M0, and carried across the process without fine-tuning or persistent memory.

The architecture is evaluated against two iconic prompts in English and Spanish.
