from zhinst.toolkit import Session

DEVICE_ID = 'DEV12120'
SERVER_HOST = 'localhost'

# connect to data server
session = Session(SERVER_HOST)

# connect to device
device = session.connect_device(DEVICE_ID)

channel_1 = device.sgchannels[0]
channel_2 = device.sgchannels[1]

# setup channel 1
synth_1 = channel_1.synthesizer()
device.synthesizers[synth_1].centerfreq(1e9)
channel_1.output.on(1)
channel_1.output.range(10)
channel_1.output.rflfpath(1)
channel_1.synchronization.enable(True)
channel_1.marker.source("awg_trigger0")

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
channel_2.marker.source("awg_trigger0")

awg_2 = channel_2.awg
awg_2.outputamplitude(1)
awg_2.modulation.enable(0)

seqc_code_1 = """
wave padding = zeros(2000);
wave microwave = ones(8000);
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
"""

seqc_code_2 = """
wave read_out_delay = zeros(12000);
wave read_out_marker = zeros(10000);

playWave(1, read_out_delay);
waitWave();
setTrigger(1);
playWave(1, read_out_marker);
waitWave();
setTrigger(0);
"""

awg_1.load_sequencer_program(seqc_code_1)
awg_2.load_sequencer_program(seqc_code_2)

awg_1.enable_sequencer(single=False)
awg_2.enable_sequencer(single=False)