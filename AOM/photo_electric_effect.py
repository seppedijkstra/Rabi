import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Reading file
file_path = "data/F0000CH1.CSV"  # Update path if needed
df = pd.read_csv(file_path, skiprows=2, header=None)
df.dropna(axis=1, how='all', inplace=True)

# Third column can be seen as timing and the 4th as data
df_signal = df[[3, 4]].copy()
df_signal.columns = ['Time (s)', 'Voltage (V)']
df_signal.dropna(inplace=True)

df_signal['Time (ms)'] = df_signal['Time (s)'] * 1000  # To miliseconds
df_signal['Voltage (mV)'] = df_signal['Voltage (V)'] * 1000  # To millivolts

plt.figure(figsize=(14, 6))
plt.plot(df_signal['Time (ms)'], df_signal['Voltage (mV)'], label='Channel 1 (TeO₂)', linewidth=1.2, color='orange')

plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

plt.title('Piezoelectric Signal from TeO₂ Crystal (Channel 1)', fontsize=25)
plt.xlabel('Time (ms)', fontsize=20)
plt.ylabel('Voltage (mV)', fontsize=20)
plt.grid(True)
plt.legend(prop={'size': 20})
plt.tight_layout()
plt.savefig("data/piezoelectric_signal.png", dpi=800)
plt.show()
