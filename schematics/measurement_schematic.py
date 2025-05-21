import matplotlib.pyplot as plt
import numpy as np
import scipy

# the timing will be in ns so the init pulse is for 300 microseconds, but we will short it
# the readout pulse is only 5 microseconds 500 ns

svg_size = (26,30)


def make_pulse(start, duration, addzeros = True):
    """
    Create a pulse with a given start time and duration.
    """
    length = int(start + duration)
    if(addzeros): pulse = np.zeros(length + 1000)
    else: pulse = np.zeros(length)
    pulse[int(start):length] = 1
    return pulse


def make_sin(start, duration):
    """
    Create a sine wave with a given start time and duration.
    """
    length = int(start + duration)
    sin = np.zeros(length)
    t = np.linspace(0, duration, num=int(duration))  # Corrected to match the duration
    sin[int(start):int(start) + len(t)] = np.sin(2.87 * np.pi * 1e9 * t)  # 2.87 GHz sine wave
    return np.abs(sin)



padding = 1000
readout_time = 500
init_time = 2000
pulse_time = np.linspace(500, 4000, num=10)
start = 0

init_pulse1 = make_pulse(0, init_time)
start += init_time + padding
rf_first = make_sin(start, pulse_time[0])
start += pulse_time[0] + padding
readout_pulse1 = make_pulse(start, readout_time, False)
start += readout_time

mid_segment = start + 1000

start = mid_segment + 1500

init_pulse2 = make_pulse(start, init_time)
start += init_time + padding
rf_last = make_sin(start, pulse_time[-1])
start += pulse_time[-1] + padding
readout_pulse2 = make_pulse(start, readout_time, False)
start += readout_time

# Figures

# figure = drawing area
fig = plt.figure(figsize=(svg_size), tight_layout=True)

# Adjusted figure size for better proportions
fig = plt.figure(figsize=(20, 12), tight_layout=True)

# 6 subplots, one for each curve
channel1 = fig.add_subplot(211)  # 2 rows, 1 col, fig1
channel2 = fig.add_subplot(212)  # 2 rows, 1 col, fig2

# Channel 1
channel1.set_title('Channel 1 Outputs', fontsize=16, fontweight="bold", verticalalignment='baseline')
channel1.grid(True, which='both', linestyle='--', alpha=0.7)
channel1.set_xlabel("Time (ps)", fontsize=14)
channel1.set_ylabel("Voltage (V)", fontsize=14)
channel1.set_xlim(0, start + padding)
channel1.set_ylim(0.02, 1.2)  # Adjusted for consistent height
channel1.plot(rf_first, color='orange', linewidth=8, label='RF Wave')
channel1.plot(rf_last, color='orange', linewidth=8)
channel1.plot(init_pulse1, color='red', linewidth=8, label='Init Pulse')
channel1.plot(init_pulse2, color='red', linewidth=8)
channel1.scatter([mid_segment, mid_segment + 300, mid_segment + 600], [0.5, 0.5, 0.5], color='black', s=300)
channel1.legend(fontsize=12, loc='upper right')

# Channel 2
channel2.set_title('Channel 2 Outputs', fontsize=16, fontweight="bold", verticalalignment='baseline')
channel2.grid(True, which='both', linestyle='--', alpha=0.7)
channel2.set_xlabel("Time (ps)", fontsize=14)
channel2.set_ylabel("Voltage (V)", fontsize=14)
channel2.set_xlim(0, start + padding)
channel2.set_ylim(0.02, 1.2)  # Adjusted for consistent height
channel2.plot(readout_pulse1, color='purple', linewidth=8, label='Readout Pulse')
channel2.plot(readout_pulse2, color='purple', linewidth=8)
channel2.scatter([mid_segment, mid_segment + 300, mid_segment + 600], [0.5, 0.5, 0.5], color='black', s=300)
channel2.legend(fontsize=12, loc='upper right')

# Show the plot
plt.show()


plt.show()