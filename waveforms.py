from zhinst.toolkit import Session


# ======= SETUP DEVICE SESSION OF AWG ===========
session = Session("localhost")
device = session.connect_device("DEV12120")

# ======= SETUP THE LASER AND MW DEVICES ===========

LASER_CHANNEL = 1
MW_CHANNEL = 2

awg_node_laser = device.sgchannels[LASER_CHANNEL].awg
awg_node_mw = device.sgchannels[MW_CHANNEL].awg

SEQUENCER_CODE_LASER = r"""
// Define timing and waveform parameters (fill these in with your values)
const t_first_pulse = 1;    // Duration of first block pulse in seconds 
const t_delay = 1;          // Delay between pulses in seconds

// Define sample rate
const s_rate = 2.0e9;            // 2 GSa/s, 0.5 ns resolution

// Convert to samples and round to next multiple of 16 for hardware compliance
const s_first_pulse = round(t_first_pulse * s_rate / 16) * 16;
const s_delay = round(t_delay * s_rate / 16) * 16;

// Generate block pulses (amplitude = 1.0 for full scale, adjust as needed)
wave first_pulse = ones(s_first_pulse, 1.0);
wave second_pulse = ones(s_second_pulse, 1.0);

// Sequence: play first pulse, delay, play second pulse
playWave(1, first_pulse);          // Play first block wave on output channel 1
playZero(s_delay);                 // Insert silent delay
"""
while 1:
    awg_node_laser.load_sequencer_program(SEQUENCER_CODE_LASER)
    awg_node_laser.enable_sequencer(single=True)
    awg_node_laser.wait_done()