from laboneq.simple import *
import numpy as np
import TimeTagger

# ================= Initialize the trigger =================
tagger = TimeTagger.createTimeTagger()
trigger_channel = 2
tagger.setTriggerLevel(trigger_channel, 3.3)  # We assume that the trigger voltage will be 3.3 V
data_channel = 1
begin_channel = trigger_channel  # Rising edge
end_channel = -trigger_channel  # Falling edge
measurement = TimeTagger.CountBetweenMarkers(tagger, data_channel, begin_channel, end_channel,
                                             1)  # We will perform this trigger only for 1 cycle, so one long pulse will be send as a trigger.

# ================= Setup sweep times =================
num_pulse_trains = 1750
start_time_ms = 0.0005  # Start driving time in ms
end_time_ms = 0.004  # End driving time in ms
rf_sweep = np.linspace(start_time_ms, end_time_ms, num_pulse_trains)

# ================= Initialize the AWG =================
descriptor = """
instruments:
    SHFSG:
        - address: DEV12120
          uid: device_shfsg
          interface: 1GbE

connections:
  device_shfsg:
    - iq_signal: laser_out/drive
      ports: [SGCHANNELS/0/OUTPUT]

    - iq_signal: rf_out/drive
      ports: [SGCHANNELS/1/OUTPUT]

    - iq_signal: trigger_out/drive
      ports: [SGCHANNELS/2/OUTPUT]
"""

device_setup = DeviceSetup.from_descriptor(
    yaml_text=descriptor,
    server_host="localhost",
    server_port='8004',
    setup_name='Rabi_Setup'
)

# ================= Setup the frequencies for the RF signal and laser pulse =================
laser_lo = Oscillator(frequency=2.8e9)
rf_lo = Oscillator(frequency=2.8e9)
trigger_lo = Oscillator(frequency=2.8e9)
cal = Calibration()
cal["/logical_signal_groups/laser_out/drive"] = SignalCalibration(local_oscillator=laser_lo)
cal["/logical_signal_groups/rf_out/drive"] = SignalCalibration(local_oscillator=rf_lo)
cal["/logical_signal_groups/trigger_out/drive"] = SignalCalibration(local_oscillator=trigger_lo)

device_setup.set_calibration(cal)

device_setup.logical_signal_groups["rf_out"].logical_signals["drive"].calibration = SignalCalibration(
    oscillator=Oscillator(
        uid="rf_out_osc", frequency=7e7, modulation_type=ModulationType.HARDWARE
    ),
)

# ================= Setting up experiments with the constant times =================

exps = [Experiment(
    uid="rabi_measurement",
    signals=[
        ExperimentSignal("laser_signal"),
        ExperimentSignal("rf_signal"),
        ExperimentSignal("trigger_signal")
    ]
) for i in range(1750)]

laser_pulse_init = pulse_library.const(length=3e-6, amplitude=0.0, marker=1)
laser_pulse_readout = pulse_library.const(length=1e-6, amplitude=0.0, marker=1)
trigger_pulse = pulse_library.const(length=1e-6, amplitude=0.0, marker=1)

# ================= The following times will change due to sweep =================

num_measurements = 250  # Number of train sequences  #100 trains with 20 points ~8 min
PL_values = np.zeros((num_measurements, num_pulse_trains))
for repetition in range(num_measurements):
    print(f"------------------ Measurement {repetition + 1} of {num_measurements} ----------------")
    for index, rf_time in enumerate(rf_sweep):
        rf_pulse = pulse_library.const(length=rf_time, amplitude=1.0)

        with exps[index].acquire_loop_rt(count=2):
            with exps[index].section(uid="init_section"):
                for _ in range(100):
                    exps[index].play(signal="laser_signal", pulse=laser_pulse_init)
                exps[index].delay(signal="laser_signal", time=1e-6)

            with exps[index].section(uid="rf_section", play_after="init_section"):
                exps[index].delay(signal="rf_signal", time=1e-6 + max(rf_sweep) - rf_time)
                exps[index].play(signal="rf_signal", pulse=rf_pulse)
                exps[index].delay(signal="rf_signal", time=1e-6)

            with exps[index].section(uid="read_out_section", play_after="rf_section"):
                exps[index].play(signal="laser_signal", pulse=laser_pulse_readout)
                exps[index].play(signal="trigger_signal", pulse=trigger_pulse)

        exps[index].set_signal_map({
            "laser_signal": device_setup.logical_signal_groups["laser_out"].logical_signals["drive"],
            "rf_signal": device_setup.logical_signal_groups["rf_out"].logical_signals["drive"]
            "trigger_signal": device_setup.logical_signal_groups["trigger_out"].logical_signals["drive"]
        })

session = Session(device_setup)
session.connect(do_emulation=True)

session.run(exp)

compiled_exp = session.compile(exp)

show_pulse_sheet("Rabi", compiled_exp, interactive=False)