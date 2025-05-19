import os
from zhinst.toolkit import Session
import TimeTagger
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import time
from rtcs.devices.zurichinstruments.shfsg_rtcs import ShfsgRtcs

# ======= CONSTANTS ===========
START = 2.85e9
END = 2.89e9
STEP = 1e5
REPETITIONS = 10

# ======= SETUP OUTPUT DIRECTORY ===========
save_dir = "/home/dl-lab-pc3/Documents/Nikolaj_Nitzsche/Rabi_bap"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
save_path = os.path.join(save_dir, f"ESR_{timestamp}")
os.makedirs(save_path, exist_ok=True)
print(f"Saving data to: {save_path}")

# ======= SETUP TIME TAGGER ===========
tagger = TimeTagger.createTimeTaggerNetwork('localhost:41101')
countrate = TimeTagger.Countrate(tagger=tagger, channels=[1])

# ======= SETUP Zurich SHFSG-RTCS ===========
sh = ShfsgRtcs(serial_number='DEV12120')
sh.open()
sh.set_marker_state(0, 1)

DEVICE_ID = 'DEV12120'
SERVER_HOST = 'localhost'
session = Session(SERVER_HOST)
device = session.connect_device(DEVICE_ID)
channel_1 = device.sgchannels[0]

# Configure channel 1
center_frequency = 2.8e9  # 2.8 GHz
synth_1 = channel_1.synthesizer()
device.synthesizers[synth_1].centerfreq(center_frequency)
channel_1.output.on(1)
channel_1.output.range(0)
channel_1.output.rflfpath(1)
channel_1.sines[0].i.enable(1)
channel_1.sines[0].q.enable(1)
awg_1 = channel_1.awg
awg_1.outputamplitude(1)
awg_1.modulation.enable(0)

# ======= SWEEP PARAMETERS ===========
RF_frequencies = np.arange(START, END, STEP)  # 2.85 → 2.89 GHz in 100 kHz steps
PL_values = np.zeros((REPETITIONS, len(RF_frequencies)))

# ======= ACQUIRE PHOTOLUMINESCENCE ===========
for rep in range(REPETITIONS):
    for idx, RF_freq in enumerate(RF_frequencies):
        channel_1.oscs[0].freq(RF_freq - center_frequency)
        countrate.startFor(2e11)
        countrate.waitUntilFinished()
        pl_rate = countrate.getData()[0]
        print(f"[Rep {rep+1}/{REPETITIONS}] {RF_freq / 1e9:.6f} GHz → {pl_rate:.0f} counts/s")
        PL_values[rep, idx] = pl_rate

# ======= AVERAGE PL VALUES ===========
avg_pl = PL_values.mean(axis=0)

# ======= NORMALIZE PL (divide by max) ===========
normalized_PL = avg_pl / np.max(avg_pl)

# ======= SAVE DATA ===========
# Raw repeats
np.save(os.path.join(save_path, "PL_values_ESR.npy"), PL_values)
np.savetxt(
    os.path.join(save_path, "PL_values_ESR.csv"),
    PL_values,
    delimiter=",",
    header=",".join(f"{f/1e9:.6f}GHz" for f in RF_frequencies),
    comments=''
)

# Averaged
np.savetxt(
    os.path.join(save_path, "averaged_PL_ESR.csv"),
    np.column_stack((RF_frequencies, avg_pl)),
    delimiter=",",
    header="Frequency (Hz),PL (counts)",
    comments=''
)

# ======= PLOT: Raw Average PL vs. Frequency ===========
plt.figure(figsize=(8,6))
plt.plot(RF_frequencies/1e9, avg_pl,
         'o-', label="Average PL")
plt.xlabel("Microwave Frequency (GHz)")
plt.ylabel("PL (counts/s)")
plt.title("Average PL vs. Microwave Frequency")
plt.grid(True)
plt.legend()
plt.savefig(os.path.join(save_path, "Average_PL_vs_Frequency.png"),
            dpi=300, bbox_inches='tight')
plt.show()

# ======= PLOT: Normalized PL vs. Frequency ===========
plt.figure(figsize=(8,6))
plt.plot(RF_frequencies/1e9, normalized_PL,
         's-', color='tab:orange', label="Normalized PL")
plt.xlabel("Microwave Frequency (GHz)")
plt.ylabel("PL (normalized)")
plt.title("Normalized PL vs. Microwave Frequency")
plt.grid(True)
plt.legend()
plt.savefig(os.path.join(save_path, "Normalized_PL_vs_Frequency.png"),
            dpi=300, bbox_inches='tight')
plt.show()

print(f"All data and plots saved in: {save_path}")

# ======= CLEANUP ===========
del tagger
sh.close()
session.disconnect_device(DEVICE_ID)
