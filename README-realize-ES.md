# sfl_realize.py — Realización Léxica (ES)

Mapea un estado de salida 9D $M_{\text{out}} \in [-1,1]^9$ al ítem léxico más próximo en el vocabulario empírico.

## Cómo funciona

$$w^* = \arg\min_{w \in \mathcal{V}} \|\hat{\mathbf{m}}_{\text{out}} - \mathbf{f}_w\|_2$$

donde $\mathbf{f}_w$ es el centroide 9D empírico del ítem léxico $w$.

- **Entrada**: vector 9D $\mathbf{m}_{\text{out}} \in [-1,1]^9$
- **Vocabulario**: `data/empirical_vocabulary_9d.json` — 32 580 ítems con centroides empíricos
- **Salida**: mejor coincidencia + candidatos clasificados con distancias euclídeas
- **Multilingüe**: mismo M_out presentado independientemente a vocabularios EN, ES, FR — sin traducción

## Ejecutar

```bash
python sfl_realize.py
```
