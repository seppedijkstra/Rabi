from laboneq.simple import *


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
"""

device_setup = DeviceSetup.from_descriptor(
    yaml_text=descriptor,
    server_host="localhost",
    server_port='8004',
    setup_name='Rabi_Setup'
)

laser_lo = Oscillator(frequency=2.6e9)
rf_lo = Oscillator(frequency=2.6e9)
cal = Calibration()
cal["/logical_signal_groups/laser_out/drive"] = SignalCalibration(local_oscillator=laser_lo)
cal["/logical_signal_groups/rf_out/drive"] = SignalCalibration(local_oscillator=rf_lo)

device_setup.set_calibration(cal)


device_setup.logical_signal_groups["rf_out"].logical_signals["drive"].calibration = SignalCalibration(
        oscillator=Oscillator(
            uid="rf_out_osc", frequency=1.8e8, modulation_type=ModulationType.HARDWARE
        ),
    )


exp = Experiment(
    uid="rabi_measurement",
    signals=[
        ExperimentSignal("laser_signal"),
        ExperimentSignal("rf_signal")
    ]
)

laser_pulse_init = pulse_library.const(length=30e-6, amplitude=0.0, marker=1)
laser_pulse_readout = pulse_library.const(length=1e-6, amplitude=0.0, marker=1)
rf_pulse = pulse_library.const(length=4e-6, amplitude=1.0)

with exp.acquire_loop_rt(count=3):
    with exp.section(uid="init_section"):
        for _ in range(100):
            exp.play(signal="laser_signal", pulse=laser_pulse_init)
        exp.delay(signal="laser_signal", time=3000e-6)



exp.set_signal_map({
    "laser_signal": device_setup.logical_signal_groups["laser_out"].logical_signals["drive"],
    "rf_signal": device_setup.logical_signal_groups["rf_out"].logical_signals["drive"]
})


session = Session(device_setup)
session.connect(do_emulation=True)


session.run(exp)


compiled_exp = session.compile(exp)

show_pulse_sheet("Rabi", compiled_exp, interactive=False)