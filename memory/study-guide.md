# Study guide: A split attractor design for rapidly writing a navigational goal

Lanz, Kathman, Hao, Ermentrout & Nagel, *Nature* (2026). https://doi.org/10.1038/s41586-026-11144-9
Interactive simulation: [`split-attractor-lab.html`](split-attractor-lab.html) (open in a browser).

## The paper in one paragraph

How can a working-memory attractor be both **stable** and **rapidly switchable**? In the fly fan-shaped body (FB), **h∆K** (30 neurons) and **PFG** (18 neurons) excite each other around a ring and share a persistent "goal bump" that turns on with odour and holds the fly's heading during a goal-directed run.

The paper has **two separate ideas**:

1. **Slow excitation + fast inhibition → robust, tuneable persistence.** PFG → h∆K excitation is slow (peptides/modulators); global inhibition (FB5V, FB6M, GABA) is fast and depresses over time. Slow excitation makes persistence possible over a *wide* range of synaptic strengths instead of a knife-edge.
2. **The "split" design → disinhibition is a write gate.** PFG receives the compass (content); h∆K receives FB5V inhibition (timing). Inhibit h∆K → loop open, PFG *follows* heading. Release → loop closes and *locks* the current heading, like a latch.

"Split" in the title refers to idea 2 (two populations). The "depression" is short-term depression of the inhibitory synapses seen in recordings; the model does not include it.

## Biology

| Element | Inputs / outputs | Role |
| --- | --- | --- |
| **h∆K** (~30) | excites PFG; slow excitation from PFG; inhibited by FB5V and FB6M | carries the goal bump; the gated half |
| **PFG** (18) | compass input (EPG, ∆7); excites h∆K; inhibited by FB6M | carries the content (heading) |
| **FB6A/D, ExR3** | broad excitation onto h∆K (cholinergic / serotonergic) | trigger slow persistent excitation |
| **FB5V** (9/side) | GABAergic, inhibits **h∆K only** | the write gate: high during turns, suppressed by odour |
| **FB6M** (2/side) | GABAergic, inhibits h∆K and PFG | global inhibition, permissive for both |

Key findings:

1. Shared persistent bump in h∆K and PFG; bump offset coincides with the end of the goal run (Fig. 1).
2. No intrinsic persistence: current injection gives only fast responses (Fig. 2a).
3. Persistence needs recurrence: blocked by nicotinic antagonists and by tetanus toxin in h∆K (Fig. 2c–f).
4. Excitation is slow; PFG expresses no fast transmitter (Fig. 2g–i).
5. Inhibition is fast and depresses; picrotoxin converts it to excitation (Fig. 2j–m).
6. The halves decouple: during turns/rest PFG has a weak bump that follows heading, h∆K is silent (Fig. 4).
7. FB5V is tonic, suppressed by odour, rises during turns and goal deviations (Fig. 6).

## Idea 1 — the maths of persistence

**Full model (Methods eqs 1–6).** Rate model, 30 h∆K + 18 PFG + 1 inhibitory unit; τ = 1, leak α = 10 (membrane time constant 0.1 s). Gaussian ring weights, σ = 0.25 rad.

```
τ du_h∆K/dt = −α u_h∆K + exc·W·U_PFG − W_inh·U_inh + I_h∆K
τ du_PFG/dt = −α u_PFG + exc·W·U_h∆K − W_inh·U_inh + I_PFG
τ du_inh/dt = −α u_inh + inh·(ΣU_h∆K + ΣU_PFG) + I_inh
U'' = −(a+b)·U' + a·b·(F(u) − U)        (alpha-function synapse)
```

| Synapse | a (decay rate) | decay 1/a | b (rise rate) |
| --- | --- | --- | --- |
| slow excitation | 0.64 s⁻¹ | ≈ 1.6 s | 25 s⁻¹ |
| fast synapse | 4.63 s⁻¹ | ≈ 0.22 s | 25 s⁻¹ |

**Two-variable reduction (eqs 12–13).** Lump h∆K + PFG into one excitatory unit; membranes ≫ synapses, decay ≪ rise:

```
U' = a_exc·(F_exc(W_EE·U − W_IE·V + I) − U)
V' = a_inh·(F_inh(U) − V)
```

If inhibition tracks excitation (V ≈ U), the loop is one leaky unit with gain g = W_EE − W_IE:

```
U' ≈ −a_exc·(1 − g)·U   ⇒   τ_decay ≈ 1 / (a_exc·(1 − g))
```

- g < 1 decays; g → 1 decay time diverges; g ≥ 1 latches at saturation.
- τ ∝ 1/a_exc, so slow excitation gives ~7× longer decays and a ~7× wider band of weights with finite long persistence.
- Simulation (W_IE = 2, `split_attractor_two_unit.py`): slow excitation τ = 2.3 s at W_EE = 2.5 → 23 s at 2.95; fast excitation τ ≤ 0.5 s, then jumps to latched.
- With fast excitation inhibition lags and the loop overshoots, narrowing the band further; hence sensitivity to excitatory but not inhibitory speed (Ext. Data Fig. 7).

## Idea 2 — split design and disinhibition gate

| | Follow mode (FB5V active) | Store mode (FB5V suppressed) |
| --- | --- | --- |
| Input to h∆K | strong inhibition (−5 in paper) | 0 |
| h∆K | silent | high bump |
| Loop | open | closed → attractor |
| PFG bump | weak, follows heading (rotational gain ≈ 1) | strong, fixed (gain ≈ 0) |

- Compass input is 1/6 of recurrent strength; recurrence must dominate for the bump to lock.
- At release, the weak PFG bump at the current heading is amplified by h∆K feedback until it saturates; the moving compass is then too weak to drag it.
- The rectifier F makes the gate work: with strong negative input F(u_h∆K) = 0, so loop gain is 0.
- Inhibiting both populations (like FB6M) only shuts everything off; decoupling needs inhibition of the half without the input.
- Causal tests still needed: FB5V activation/silencing; optogenetic writing of a bump.

## Glossary

| Term | Meaning |
| --- | --- |
| Ring attractor | network whose stable states are bumps at any angle around a ring |
| Persistent activity | activity outlasting its input by much more than the membrane time constant |
| Alpha function | synaptic response rising with 1/b, decaying with 1/a |
| Loop gain g | net excitation minus inhibition; g = 1 is the integrator edge |
| Disinhibition | removing inhibition to enable a circuit |
| Latch | follows input while open, holds last value when closed |
| Rotational gain | bump movement ÷ heading change |
| Short-term depression | synapse weakens with repeated activation |

## Self-test

1. Why can't h∆K's membrane produce the seconds-long bump? Which experiment shows this?
2. Which two experiments show persistence depends on recurrent signalling?
3. Derive τ_decay ≈ 1/(a_exc(1 − g)) from the two-variable model. Which assumption is needed?
4. Why does slow excitation widen the range of weights giving long but finite persistence?
5. Why is the regime sensitive to excitatory but not inhibitory speed?
6. What does "split" mean, and which population carries content vs timing?
7. Explain how releasing h∆K from inhibition locks the current heading.
8. Why must recurrence be much stronger than the compass input?
9. Why does inhibiting both h∆K and PFG not produce follow-vs-store switching?
10. Name three properties of FB5V that fit a gate, and one causal experiment to test it.
