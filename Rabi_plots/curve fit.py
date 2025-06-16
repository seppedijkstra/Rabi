import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import pearsonr

data = pd.read_csv("averaged_PL.csv")
data.columns = ['time', 'PL_counts']
data["PL_smooth"] = data["PL_counts"].rolling(window=5, center=True).mean()


bounds = ([0, 1e-7, 1e5, -2*np.pi], [20, 1e-3, 1e7, 2*np.pi])


clean_data = data.dropna()
time = clean_data["time"].values

signal = clean_data["PL_counts"].values

# Damping function that described the Rabi oscillations found in the literature
def damping_function(t,a,b,c,d):
    return a*(1-np.e**(-t/b)*np.cos(c*t + d))

initial_guess = [2, 25e-6, 6e6, 0]

data["PL_smooth"] = data["PL_counts"].rolling(window=5, center=True).mean()
smooth = clean_data["PL_smooth"].values

params, param_cov = curve_fit(damping_function, time, signal, p0=initial_guess,  bounds=bounds)
print(params)

fit_signal = damping_function(time, *params)

smooth_norm = (smooth - np.mean(smooth)) / np.std(smooth)
signal_norm = (signal - np.mean(signal)) / np.std(signal)
fit_norm = (fit_signal - np.mean(fit_signal)) / np.std(fit_signal)

smooth_coeff,_ = pearsonr(smooth_norm, fit_norm)
corr_coeff, _ = pearsonr(signal_norm, fit_norm)
similarity_percent = corr_coeff * 100

fitted_frequency = params[2]  # in Hz
print(f"Fitted frequency: {fitted_frequency:.2f} Hz")

print("Correlation: ", similarity_percent)
print("Smooth Correlation: ", smooth_coeff * 100)

plt.figure(figsize=(10, 5))
plt.plot(clean_data["time"] *1e6, signal, label='Original Data', alpha=0.5)
plt.plot(data["time"] *1e6, data["PL_smooth"], label='Smoothed Data', linewidth=2)
plt.plot(clean_data["time"]*1e6, fit_signal, '--r', label='Damped Cosine Fit')
plt.xlabel("RF Driving time (μs)")
plt.ylabel("PL Counts")
plt.title("Smoothed Data and Fit")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
