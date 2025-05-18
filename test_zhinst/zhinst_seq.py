from zhinst.toolkit import Session

DEVICE_ID = 'DEV12120'
SERVER_HOST = 'localhost'

### connect to data server
session = Session(SERVER_HOST)

### connect to device
device = session.connect_device(DEVICE_ID)

channel = device.sgchannels[0]

synth = channel.synthesizer()
device.synthesizers[synth].centerfreq(1e9)
channel.output.on(1)
channel.output.range(10)
channel.output.rflfpath(1)
channel.marker[0].source("awgTrigger1")

awg = channel.awg
awg.outputamplitude(1)
awg.modulation.enable(0)

seqc_code = """
wave w_gauss = gauss(8000, 4000, 1000);

setTrigger(1);
playWave(1, w_gauss);
waitWave();
setTrigger(0);
"""

awg.load_sequencer_program(seqc_code)

awg.enable_sequencer(single=False)