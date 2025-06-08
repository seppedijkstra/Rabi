import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

ZL = 0.51 - 21.83j

Q = np.sqrt((50 / 0.51) - 1)
C = 1 / (2 * np.pi * 110e6 * Q * 0.51)
L = 50 / Q / (2 * np.pi * 110e6)

L_l = 21.83 / (2 * np.pi * 110e6)
print(L_l)

print(Q,C,L)

def calculate_impedance(f):

    w = 2 * np.pi * f


    Z_ll = 1j * w * L_l

    ZL2 = ZL + Z_ll

    Zc = -1j / (w * C)
    Z1 = ZL2 + Zc

    Zl = 1j * w * L
    Zin = 1 / (1 / Z1 + 1 / Zl)
    return Zin

Z0 = 50
Zin = calculate_impedance(110e6)

Gamma = (Zin - Z0) / (Zin + Z0)
VSWR = (1 + abs(Gamma)) / (1 - abs(Gamma))

print(Zin,Gamma,VSWR)

freqs = np.linspace(100e6, 120e6, 500)
Gamma_vals = []
Zin_vals = []

for f_test in freqs:
    Zin = calculate_impedance(f_test)
    Gamma = (Zin - Z0) / (Zin + Z0)
    Zin_vals.append(Zin)
    Gamma_vals.append(abs(Gamma))

plt.plot(freqs / 1e6, 20 * np.log10(Gamma_vals), color='seagreen')
plt.xlabel("Frequency (MHz)")
plt.ylabel("Return Loss (dB)")
plt.grid(True)
plt.tight_layout()
plt.show()


Zin_vals = np.array(Zin_vals)
Z_mag = 20 * np.log10(np.abs(Zin_vals))
Z_phase = np.angle(Zin_vals, deg=True)

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

lns1 = ax1.semilogx(freqs, Z_mag, color='teal', label = 'Magnitude')
ax1.set_ylabel("Magnitude (dBΩ)")
lns2 = ax2.semilogx(freqs, Z_phase, color='firebrick', label='Phase')
ax2.set_ylabel("Phase (degrees)")
ax1.set_xlabel("Frequency (Hz)")
lns = lns1+lns2
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc=0)
plt.grid(True)
plt.tight_layout()
plt.show()