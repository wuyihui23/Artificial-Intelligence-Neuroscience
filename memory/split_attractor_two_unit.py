"""Two-unit reduction of the h∆K–PFG model (Lanz et al., Nature 2026, Methods eqs 12–13).

U' = a_exc * (F_exc(W_EE*U - W_IE*V + I) - U)
V' = a_inh * (F_inh(U) - V)

Scans W_EE at fixed W_IE and reports the decay time after a 2 s input pulse,
for slow (a = 0.64) and fast (a = 4.63) excitation. Prediction: tau ≈ 1/(a_exc*(1-g)), g = W_EE - W_IE.
"""
import numpy as np

def f_exc(x):
    return np.clip(x, 0, 1)

def f_inh(x):
    return max(x, 0.0)

def decay_time(a_exc, a_inh, w_ee, w_ie, t_in=2.0, t_max=60.0, dt=1e-3):
    u = v = 0.0
    for _ in range(int(t_in / dt)):
        u, v = u + dt * a_exc * (f_exc(w_ee * u - w_ie * v + 1) - u), v + dt * a_inh * (f_inh(u) - v)
    u0 = u
    for k in range(int(t_max / dt)):
        u, v = u + dt * a_exc * (f_exc(w_ee * u - w_ie * v) - u), v + dt * a_inh * (f_inh(u) - v)
        if u < u0 / np.e:
            return k * dt
    return np.inf  # latched

if __name__ == "__main__":
    w_ie = 2.0
    for label, a in [("slow", 0.64), ("fast", 4.63)]:
        print(f"{label} excitation (a_exc = {a})")
        for w_ee in np.arange(2.5, 3.05, 0.05):
            tau = decay_time(a, 4.63, w_ee, w_ie)
            print(f"  W_EE = {w_ee:.2f}  g = {w_ee - w_ie:.2f}  tau = {tau:.2f} s")
