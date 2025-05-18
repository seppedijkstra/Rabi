import os
from datetime import datetime
import TimeTagger
from laboneq.data.calibration import PortMode
from laboneq.data.calibration import SignalCalibration, Oscillator
from laboneq.dsl import LinearSweepParameter, Session
from laboneq.dsl.device import DeviceSetup, create_connection
from laboneq.dsl.device.instruments import SHFSG
from laboneq.dsl.experiment import Experiment, ExperimentSignal, pulse_library
import numpy as np
import matplotlib.pyplot as plt
from zhinst.toolkit import Waveforms

setup = DeviceSetup("TimeTagger_setup")
timetagger_server = "localhost"
timetagger_port = 41101


# function to set timetagger at a specific level
def settimetagger(session: Session,
                  trigger_level,
                  ):
    timetagger.setTriggerLevel(counter_input, trigger_level)



def simulatepulses(
        pulse_count: int,
        timetagger_trigger_sweep,
        click_up_length=13e-9,
        click_down_length=10e-9,
        click_amplitude=1.,
):
    exp = Experiment(
        uid="testtrigger",
        signals=[ExperimentSignal("apd", map_to=apd_lsg)],
    )

    # define what a click is
    click = pulse_library.const("click", length=click_up_length,
                                amplitude=click_amplitude)

    # call trigger level settings inside the sweep
    with exp.sweep(parameter=timetagger_trigger_sweep):
        exp.call("trigger_sweep", trigger_level=timetagger_trigger_sweep)
        with exp.acquire_loop_rt(uid="counts",
                                 count=1,
                                 ):
            # send fixed number of pulses
            with exp.section(uid="readout",
                             trigger={"apd": {"state": True}},
                             ):
                for i in range(pulse_count):
                    exp.delay(signal="apd", time=click_down_length)
                    exp.play(signal="apd", pulse=click)
    return exp

# add a dataserver
setup.add_dataserver(host="localhost", port=8004)

# add an SHFSG
setup.add_instruments(SHFSG(uid="device_shfsg",
    address="DEV12120", device_options="SHFSG8"))

# add connections
setup.add_connections(
    "device_shfsg",
    create_connection(to_signal="q0/drive_line",
        ports=f"SGCHANNELS/{0}/OUTPUT"),
    create_connection(to_signal="q0/apd_line",
        ports=f"SGCHANNELS/{1}/OUTPUT"),
)


# shortcut to connections
drive_lsg = setup.logical_signal_groups["q0"].logical_signals["drive_line"]
apd_lsg   = setup.logical_signal_groups["q0"].logical_signals["apd_line"]

session = Session(device_setup=setup)

# simple NV center drive
drive_lsg.calibration      = SignalCalibration()
drive_lsg.local_oscillator = Oscillator("NV_lo_osc", frequency=2.8e9)
drive_lsg.oscillator       = Oscillator("NV_osc",    frequency=-13e6)
drive_lsg.port_mode        = PortMode.RF
drive_lsg.range            = 10 #dBm

# APD simulation
apd_lsg.port_mode        = PortMode.LF
apd_lsg.range            = 10 #dBm
apd_lsg.local_oscillator = Oscillator(uid="apd_lo", frequency=0)
apd_lsg.oscillator       = Oscillator(uid="apd_osc", frequency=0)

address = f'{timetagger_server}:{timetagger_port}'

# Connect to the server
timetagger = Timetagger.createTimeTaggerNetwork(address)
# for the input connection of the time tagger,
# we set an initial trigger level and delay
timetagger.setTriggerLevel(counter_input, 0.25)
timetagger.setInputDelay(counter_input, 0)

# for the gate connection of the time tagger,
# we set an initial trigger level and delay
timetagger.setTriggerLevel(gate_start_input, 0.5)
timetagger.setInputDelay(gate_start_input, 0)

# register it to session
session.register_neartime_callback(settimetagger, "trigger_sweep")

# define a sweep with trigger levels
trigger_levels = LinearSweepParameter(uid="tlevel", start=0.1, stop=1,
                                      count=30, axis_name="trigger level [V]")

# create an experiment to perform the calibration
timetagger_calibration_experiment = simulatepulses(100, trigger_levels)

# compile experiment
cexp = session.compile(timetagger_calibration_experiment)

