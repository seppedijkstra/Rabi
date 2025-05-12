import os
from datetime import datetime
import TimeTagger
from zhinst.toolkit import Session
import numpy as np
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



awg_node_laser.load_sequencer_program(SEQUENCER_CODE_LASER_PULSE_1)
awg_node_laser.load_sequencer_program(SEQUENCER_CODE_MW_PULSE)
awg_node_laser.load_sequencer_program(SEQUENCER_CODE_LASER_PULSE_2)
awg_node_laser.enable_sequencer(single=True)
awg_node_laser.wait_done()