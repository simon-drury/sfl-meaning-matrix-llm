# Abstract

> "Language arises in the life of the individual through an ongoing exchange of meanings with significant others."
> M.A.K. Halliday, Language as Social Semiotic (1978)

---

Language is produced under social conditions, specifically field, tenor, and mode.

This paper presents an input architecture. The system encodes each semiotic unit as a position in a nine-dimensional Riemannian manifold (a 3x3 matrix: rows the SFL metafunctions, columns the register variables field, tenor and mode). The transformer operates on these meaning states directly. Lexical output is realised independently per language at the output edge. The social context of the interaction is encoded once, in a reference state M0, and carried across the process.

The architecture is evaluated against two iconic prompts in English and Spanish.
