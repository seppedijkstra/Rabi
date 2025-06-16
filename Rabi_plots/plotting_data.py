import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv("averaged_PL.csv")

# Clean and rename columns
df.columns = df.columns.str.strip()
df.rename(columns={"# Driving Time (ms)": "Time_ms", "PL (counts)": "PL_counts"}, inplace=True)

# Convert time from ms to µs
df["Time_us"] = df["Time_ms"] * 1e6
df["Time_ns"] = df["Time_ms"] * 1e9

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(df["Time_us"], df["PL_counts"], marker='o', linestyle='-', color='orange', alpha=0.7)
plt.title("Rabi Oscillations (Raw Data)")
plt.xlabel("Driving Time (µs)")
plt.ylabel("Photoluminescence (counts)")
plt.grid(True)
plt.tight_layout()
plt.show()


# Apply rolling average smoothing
df["PL_smooth"] = df["PL_counts"].rolling(window=5, center=True).mean()

# Plot with smoothing
plt.figure(figsize=(10, 6))
plt.plot(df["Time_us"], df["PL_counts"], 'o', alpha=0.3, label='Raw')
plt.plot(df["Time_us"], df["PL_smooth"], '-', linewidth=2, label='Smoothed')
plt.title("Rabi Oscillations (Smoothed)")
plt.xlabel("RF Driving Time (μs)")
plt.ylabel("Photoluminescence (counts)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

