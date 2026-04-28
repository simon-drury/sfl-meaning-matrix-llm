# Understanding Log

Permanent record of moments of understanding as they happen.

---

## Entry 1 — 28 April 2026, 21:42 CEST
### W, b, and the training algorithm

**What was understood:**

The Dense layer has two sets of parameters: the weight matrix W and the bias vector b. Neither is set by hand. Both are found entirely by the training algorithm — no human in the loop.

**How the algorithm finds W (and b):**

1. W starts randomly initialised. b starts at zero.
2. Forward pass — the current W multiplies the input, produces an output.
3. Loss — the distance between that output and the target is measured.
4. GradientTape — computes the gradient: the direction in which W is currently making the loss worse.
5. Optimiser — subtracts a small step in that direction: W ← W − η · ∂L/∂W
6. Repeat thousands of times. W and b drift toward values that make the loss small.

**Relation to the SFL architecture:**

The input x_i is one of the six meaning values: ideational, field, interpersonal, tenor, textual, mode.

W_ij is the weight connecting meaning dimension i to output position j.

The layer takes the 6D meaning coordinate, multiplies it through the weight matrix, adds bias, and produces the transformed semantic state.

The only thing that differs from the standard MIT lab is what the loss measures. The lab measures distance from an arbitrary placeholder target. The SFL architecture measures distance from the permanent context — the target register state. The mechanics of finding W are identical.

**This is the same algorithm as Ava Amini's lecture.** Same backpropagation, same GradientTape, same SGD update rule. The architecture wraps it — the engine underneath is unchanged.
