import TimeTagger

# 1. Initialize the Time Tagger (connects to the hardware).
tagger = TimeTagger.createTimeTagger()
# This auto-detects a connected Time Tagger device:contentReference[oaicite:12]{index=12}.
# If multiple devices or specific settings are needed, refer to Time Tagger docs for options.

# 2. Configure the trigger input channel.
trigger_channel = 1  # Physical channel receiving the block pulse trigger.
tagger.setTriggerLevel(trigger_channel, 1)
# Set trigger threshold to 0.5 V (adjust based on actual signal):contentReference[oaicite:13]{index=13}.
# This ensures the Time Tagger registers a time-tag when the pulse crosses 0.5 V.
# (For a TTL, rising through 0.5 V creates a rising-edge event, falling through 0.5 V creates a falling-edge event.)

# Optional: If the trigger pulses are very short or if you want to avoid multiple edges due to noise,
# you could set a dead-time on the trigger channel to ignore rapid successive events:
# tagger.setDeadtime(trigger_channel, 10000)  # e.g., 10,000 ps (10 ns) dead time (if needed).

# 3. Configure the data channel(s) (the channel whose events we want to record during the gate).
data_channel = 2  # Example data input channel.
# (You may also adjust its trigger level or other settings if needed, e.g., tagger.setTriggerLevel(data_channel, ...))

# 4. Set up a measurement that uses the trigger to define start and stop of acquisition.
# We'll use CountBetweenMarkers to count events on data_channel between start and stop triggers.

# Create a delayed virtual channel for the 5 µs gate duration.
# This will generate a "stop" event 5,000,000 ps after each falling edge on channel 1.
gate_stop = TimeTagger.DelayedChannel(tagger,               # the Time Tagger instance
                                      -1,                   # input channel: -1 = channel 1 falling edge:contentReference[oaicite:10]{index=10}
                                      5000000)              # delay in ps (5 µs = 5,000,000 ps)

begin_chan   = -1        # Rising edge of trigger_channel -> start
num_cycles   = 1                      # Number of trigger cycles to record (1 start-stop pair)
measurement = TimeTagger.CountBetweenMarkers(tagger, data_channel, begin_chan, gate_stop, n_values=num_cycles)
# This measurement will wait for a rising edge on channel 1, start counting channel 2 events,
# then wait for the next falling edge on channel 1 to stop counting:contentReference[oaicite:14]{index=14}:contentReference[oaicite:15]{index=15}.
# n_values=1 means it will store one count value (then stop after one start->stop cycle).

# 5. Start the measurement.
measurement.start()
# Immediately after starting, synchronize the Time Tagger to ensure a clean start:
tagger.sync()
# tagger.sync() flushes any previous time-tags and ensures the trigger configuration is applied:contentReference[oaicite:16]{index=16}.
# All time-tags following this call will be truly after the measurement start (so we ignore any prior spurious triggers).

# 6. Wait for the measurement to complete.
# The measurement will finish once a rising + falling trigger pair has been observed (one cycle).
measurement.waitUntilFinished()
# Alternatively, you could poll measurement.ready() in a loop until it's True.

# 7. Retrieve and print the result.
result_array = measurement.getData()      # getData() returns an array of length num_cycles with the counts.
counts_during_pulse = result_array[0]     # Since n_values=1, take the first (only) element.
print(f"Counts detected on channel {data_channel} during trigger pulse: {counts_during_pulse}")
