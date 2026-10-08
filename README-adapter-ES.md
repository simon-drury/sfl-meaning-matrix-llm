# sfl_adapter.py — Capa de Proyección: Significado a Embedding

## Propósito

Conecta el motor del manifold semiótico con el modelo transformer.
Toma el vector de significado de 9 dimensiones producido por
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
| \(\mathbf{m}_t\) | \((9,)\) | Vector de significado en el paso \(t\) |
| \(W_{\text{adapt}}\) | \((d_{\text{model}} \times 9)\) | Matriz de proyección aprendida |
| \(\mathbf{b}\) | \((d_{\text{model}},)\) | Sesgo aprendido |
| \(\mathbf{e}_t\) | \((d_{\text{model}},)\) | Vector de embedding, listo para el transformer |

Solo se entrenan \(W_{\text{adapt}}\) y \(\mathbf{b}\).
Todos los pesos del transformer permanecen congelados en la Etapa 1.

---

## Modelos locales compatibles

| Modelo | \(d_{\text{model}}\) | Parámetros entrenables (\(n_{\text{dim}}=9\)) |
|---|---|---|
| DeepSeek-R1-Distill-Qwen-1.5B | 2048 | 20,480 |
| Llama 3.2 3B Instruct | 3072 | 30,720 |

Ambos modelos están instalados localmente mediante GPT4All v3.10.0.

---

## Salida de validación

```
AdapterConfig(deepseek-r1-distill-qwen-1.5b | d_model=2048 | n_dim=9 | parámetros entrenables=20,480)
  Forma entrada : (5, 9)
  Forma salida  : (5, 2048)  OK
  Todo finito   : True
  Estado        : PASS

AdapterConfig(llama-3.2-3b-instruct | d_model=3072 | n_dim=9 | parámetros entrenables=30,720)
  Forma entrada : (5, 9)
  Forma salida  : (5, 3072)  OK
  Todo finito   : True
  Estado        : PASS
```

---

## Próximo paso

`sfl_realize.py` — desmatrición: mapea el estado de salida del transformer
\(M_{\text{out}} \in \mathcal{M}\) de vuelta a elementos léxicos en el idioma \(L\)
mediante recuperación por vecino más cercano en \(\mathcal{V}_L\).
