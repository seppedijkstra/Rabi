import os
from zhinst.toolkit import Session
import TimeTagger
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt


def create_seqc_code(pulse_length):
    return [r"""
        wave padding = zeros(2000);
        wave microwave = ones(""" + str(pulse_length * 2e9) + r""");
        wave read_out = zeros(10000);

        setTrigger(0);
        playWave(1, padding);
        waitWave();
        playWave(1, microwave);
        waitWave();
        playWave(1, padding);
        waitWave();
        setTrigger(1);
        playWave(1, read_out);
        """, r"""
        wave read_out_delay = zeros(""" + str((2e-6 + pulse_length) * 2e9) + r""");
        wave read_out_marker = ones(10000);

        playWave(1, read_out_delay);
        waitWave();
        setTrigger(1);
        playWave(1, read_out_marker);
        waitWave();
        setTrigger(0);
        """]

# setup output directory

save_dir = "/home/dl-lab-pc3/Documents/Nikolaj_Nitzsche/Rabi_bap"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Timestamped folder
save_path = os.path.join(save_dir, f"Rabi_{timestamp}")
os.makedirs(save_path, exist_ok=True)  # Create folder if it doesn't exist
print(f"Saving data to: {save_path}")

# shfsg setup

DEVICE_ID = 'DEV12120'
SERVER_HOST = 'localhost'

# connect to data server
session = Session(SERVER_HOST)

# connect to device
device = session.connect_device(DEVICE_ID)

channel_1 = device.sgchannels[0]
channel_2 = device.sgchannels[0]

# setup channel 1
synth_1 = channel_1.synthesizer()
device.synthesizers[synth_1].centerfreq(1e9)
channel_1.output.on(1)
channel_1.output.range(10)
channel_1.output.rflfpath(1)
channel_1.synchronization.enable(True)

awg_1 = channel_1.awg
awg_1.outputamplitude(1)
awg_1.modulation.enable(0)

# setup channel 2
synth_2 = channel_2.synthesizer()
device.synthesizers[synth_2].centerfreq(1e9)
channel_2.output.on(1)
channel_2.output.range(10)
channel_2.output.rflfpath(1)
channel_2.synchronization.enable(True)

awg_2 = channel_2.awg
awg_2.outputamplitude(1)
awg_2.modulation.enable(0)


# time tagger setup

counter_input = 1
gate_input = 2

timetagger = TimeTagger.createTimeTaggerNetwork('localhost:41101')

timetagger.setTriggerLevel(counter_input, 0.25)
timetagger.setInputDelay(counter_input, 0)

timetagger.setTriggerLevel(gate_input, 0.5)
timetagger.setInputDelay(gate_input, 0)


# experiment

pulse_lengths = np.arange(0.5e-6,4e-6,0.002e-6)
photon_counts = np.zeros((250, len(pulse_lengths)))

for i,pulse in enumerate(pulse_lengths):

    for repetition in range(250):
        seqc = create_seqc_code(pulse)
        awg_1.load_sequencer_program(seqc[0])
        awg_2.load_sequencer_program(seqc[1])

        counter = CountBetweenMarkers(tagger=timetagger,
                                      click_channel=counter_input,
                                      begin_channel=gate_input,
                                      end_channel=-gate_input,
                                      n_values=1,
                                      )

        awg_1.enable_sequencer(single=True)
        awg_2.enable_sequencer(single=True)

        pl_rate = counter.getData()[0]

        photon_counts[repetition, i] = pl_rate


avg_pl = np.mean(photon_counts, axis=0)  # Average over all measurements

# ======= SAVE DATA ===========
np.save(os.path.join(save_path, "PL_values.npy"), photon_counts)  # Save as .npy
np.savetxt(os.path.join(save_path, "PL_values.csv"), photon_counts, delimiter=",")  # Save as CSV
np.savetxt(os.path.join(save_path, "averaged_PL.csv"), np.column_stack((pulse_lengths, avg_pl)), delimiter=",",
           header="Driving Time (ms), PL (counts)")

# ======= PLOT & SAVE FIGURE ===========
plt.figure(figsize=(8, 6))
plt.plot(pulse_lengths, avg_pl, marker='o', linestyle='-', color='b', label="Averaged PL vs. Driving Time")
plt.xlabel('Driving Time (ms)')
plt.ylabel('PL (counts)')
plt.title('Average PL vs. Pulse Time (Rabi Oscillations)')
plt.grid(True)
plt.legend()
plt.savefig(os.path.join(save_path, "Rabi_Oscillations.png"))  # Save plot as PNG
plt.show()

print(f"Data and plot saved in: {save_path}")

