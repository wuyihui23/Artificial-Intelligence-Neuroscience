# Artificial-Intelligence-Neuroscience
paper review/discussion about AI structure with interdisciplinary neuroscience 

# memory
Lanz, A.J., Kathman, N.D., Hao, E. et al. A split attractor design for rapidly writing a navigational goal. Nature (2026). https://doi.org/10.1038/s41586-026-11144-9

## Update 2026-11-05: study guide and simulation

Added to `memory/`:

- `study-guide.md`: summary of the circuit (h∆K, PFG, FB5V, FB6M), the rate-model equations, the two-variable derivation τ ≈ 1/(a_exc·(1 − g)), the disinhibition gate (follow vs store mode), a glossary and self-test questions.
- `split-attractor-lab.html`: interactive simulation, open in a browser. Rig 1 compares slow and fast excitation; Rig 2 toggles FB5V inhibition on the h∆K–PFG ring to show the bump following or locking the heading.
- `split_attractor_two_unit.py`: reproduces the decay-time scan of the two-unit model (slow vs fast excitation).

Key idea: slow recurrent excitation makes persistence robust and tuneable; splitting the attractor into two populations lets inhibition of h∆K act as a write gate for the heading carried by PFG.
