import os
from datetime import datetime
import TimeTagger
from zhinst.toolkit import Session
import numpy as np
import matplotlib.pyplot as plt
from zhinst.toolkit import Waveforms


def create_mw_sequence(pulse_length):
     return r"""
    // Define timing and waveform parameters (fill these in with your values)
    const t_first_pulse = """ + str(pulse_length) + r""";    // Duration of first block pulse in seconds 

    // Define sample rate
    const s_rate = 2.0e9;            // 2 GSa/s, 0.5 ns resolution

    // Convert to samplefs and round to next multiple of 16 for hardware compliance
    const s_pulse = round(t_first_pulse * s_rate / 16) * 16;

    wave pulse = ones(s_pulse, 1.0);
    playWave(1, pulse);        
    """
# ======= EXPERIMENT PARAMETERS ===========
num_pulse_trains = 1750
start_time_ms = 0.0005  # Start driving time in ms
end_time_ms = 0.004  # End driving time in ms
mw_sweep = np.linspace(start_time_ms, end_time_ms, num_pulse_trains)

# ======= SETUP OUTPUT DIRECTORY ===========
save_dir = "/home/dl-lab-pc3/Documents/Nikolaj_Nitzsche/Cryo/Rabi"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Timestamped folder
save_path = os.path.join(save_dir, f"Rabi_{timestamp}")
os.makedirs(save_path, exist_ok=True)  # Create folder if it doesn't exist
print(f"Saving data to: {save_path}")


# ======= SETUP DEVICE SESSION OF AWG ===========
session = Session("localhost")
device = session.connect_device("DEV12120")

# ======= SETUP THE LASER AND MW DEVICES ===========

LASER_CHANNEL = 1
MW_CHANNEL = 2

awg_node_laser = device.sgchannels[LASER_CHANNEL].awg
awg_node_mw = device.sgchannels[MW_CHANNEL].awg

# ======= SETUP TIMETAGGER FOR PL MEASUREMENT ===========
tagger = TimeTagger.createTimeTaggerNetwork('localhost:41101')
countrate = TimeTagger.Countrate(tagger=tagger, channels=[1])

# ======= CREATE SEQUENCER CODE ===========

SEQUENCER_CODE_LASER_PULSE_1 = r"""
// Define timing and waveform parameters (fill these in with your values)
const t_first_pulse = 300e-6;    // Duration of first block pulse in seconds 

// Define sample rate
const s_rate = 2.0e9;            // 2 GSa/s, 0.5 ns resolution

// Convert to samples and round to next multiple of 16 for hardware compliance
const s_pulse = round(t_pulse * s_rate / 16) * 16;

wave pulse = ones(s_first_pulse, 1.0);
playWave(1, pulse);        
"""

SEQUENCER_CODE_LASER_PULSE_2= r"""
// Define timing and waveform parameters (fill these in with your values)
const t_first_pulse = 10e-6;    // Duration of first block pulse in seconds 

// Define sample rate
const s_rate = 2.0e9;            // 2 GSa/s, 0.5 ns resolution

// Convert to samples and round to next multiple of 16 for hardware compliance
const s_pulse = round(t_first_pulse * s_rate / 16) * 16;

wave pulse = ones(s_pulse, 1.0);
playWave(1, pulse);        
"""

num_measurements = 250  # Number of train sequences  #100 trains with 20 points ~8 min
PL_values = np.zeros((num_measurements, num_pulse_trains))

for repetition in range(num_measurements):
    print(f"------------------ Measurement {repetition + 1} of {num_measurements} ----------------")
    for index, mw_time in enumerate(mw_sweep):

        SEQUENCER_CODE_MW_PULSE = create_mw_sequence(mw_time)

        awg_node_laser.load_sequencer_program(SEQUENCER_CODE_LASER_PULSE_1)
        awg_node_laser.load_sequencer_program(SEQUENCER_CODE_MW_PULSE)

        awg_node_laser.load_sequencer_program(SEQUENCER_CODE_LASER_PULSE_2)
        awg_node_laser.enable_sequencer(single=True)


        # For the measurement
        countrate.startFor(10e6)
        countrate.waitUntilFinished()
        pl_rate = countrate.getData()[0]
        print(f"PL Measurement after pulse {mw_time} us, repetition {repetition}")
        # Store PL data
        PL_values[repetition, index] = pl_rate


# ======= AVERAGE PL VALUES ===========
avg_pl = np.mean(PL_values, axis=0)  # Average over all measurements

# ======= SAVE DATA ===========
np.save(os.path.join(save_path, "PL_values.npy"), PL_values)  # Save as .npy
np.savetxt(os.path.join(save_path, "PL_values.csv"), PL_values, delimiter=",")  # Save as CSV
np.savetxt(os.path.join(save_path, "averaged_PL.csv"), np.column_stack((num_measurements, avg_pl)), delimiter=",",
           header="Driving Time (ms), PL (counts)")

# ======= PLOT & SAVE FIGURE ===========
plt.figure(figsize=(8, 6))
plt.plot(num_measurements, avg_pl, marker='o', linestyle='-', color='b', label="Averaged PL vs. Driving Time")
plt.xlabel('Driving Time (ms)')
plt.ylabel('PL (counts)')
plt.title('Average PL vs. Pulse Time (Rabi Oscillations)')
plt.grid(True)
plt.legend()
plt.savefig(os.path.join(save_path, "Rabi_Oscillations.png"))  # Save plot as PNG
plt.show()

print(f"Data and plot saved in: {save_path}")
