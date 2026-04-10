# sfl_adapter.py — Capa de Proyección: Significado a Embedding

## Propósito

Conecta el motor del manifold semiótico con el modelo transformer.
Toma el vector de significado de \(n_{\text{dim}}\) dimensiones producido por
`sfl_manifold.py` y lo proyecta en el espacio de embedding de un transformer
local, de modo que la maquinaria de atención del transformer pueda operar
sobre estados de significado en lugar de embeddings de tokens.

---

## La proyección

\[
\mathbf{e}_t = W_{\text{adapt}}\,\mathbf{m}_t + \mathbf{b}
\]

| Símbolo | Forma | Descripción |
|---|---|---|
| \(\mathbf{m}_t\) | \((n_{\text{dim}},)\) | Vector de significado en el paso \(t\) |
| \(W_{\text{adapt}}\) | \((d_{\text{model}} \times n_{\text{dim}})\) | Matriz de proyección aprendida |
| \(\mathbf{b}\) | \((d_{\text{model}},)\) | Sesgo aprendido |
| \(\mathbf{e}_t\) | \((d_{\text{model}},)\) | Vector de embedding, listo para el transformer |

Solo se entrenan \(W_{\text{adapt}}\) y \(\mathbf{b}\).
Todos los pesos del transformer permanecen congelados en la Etapa 1.

---

## Modelos locales compatibles

| Modelo | \(d_{\text{model}}\) | Parámetros entrenables (\(n_{\text{dim}}=6\)) |
|---|---|---|
| DeepSeek-R1-Distill-Qwen-1.5B | 2048 | 14,336 |
| Llama 3.2 3B Instruct | 3072 | 21,504 |

Ambos modelos están instalados localmente mediante GPT4All v3.10.0.

---

## Escalabilidad

\(n_{\text{dim}} = 6\) es la dimensionalidad mínima viable actual.
Es un **parámetro**, no una constante.

Cada dimensión podría convertirse en un polinomio, una distribución
con momentos superiores, o un sub-vector. El número de dimensiones
crecerá según lo demande la teoría. `AdapterConfig` acepta cualquier
\(n_{\text{dim}}\) sin cambios en el transformer posterior.

---

## Salida de validación

```
AdapterConfig(deepseek-r1-distill-qwen-1.5b | d_model=2048 | n_dim=6 | parámetros entrenables=14,336)
  Forma entrada : (5, 6)
  Forma salida  : (5, 2048)  OK
  Todo finito   : True
  Estado        : PASS

AdapterConfig(llama-3.2-3b-instruct | d_model=3072 | n_dim=6 | parámetros entrenables=21,504)
  Forma entrada : (5, 6)
  Forma salida  : (5, 3072)  OK
  Todo finito   : True
  Estado        : PASS
```

---

## Próximo paso

`sfl_realize.py` — desmatrición: mapea el estado de salida del transformer
\(M_{\text{out}} \in \mathcal{M}\) de vuelta a elementos léxicos en el idioma \(L\)
mediante recuperación por vecino más cercano en \(\mathcal{V}_L\).
