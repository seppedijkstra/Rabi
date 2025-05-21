import TimeTagger

save_dir = "/home/dl-lab-pc3/Documents/Nikolaj_Nitzsche/Rabi_bap"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
save_path = os.path.join(save_dir, f"Taggercalibration_{timestamp}")
os.makedirs(save_path, exist_ok=True)
print(f"Saving data to: {save_path}")

# time tagger setup
counter_channel = 1
trigger_channel = 2

timetagger = TimeTagger.createTimeTaggerNetwork('localhost:41101')
countrate = TimeTagger.Countrate(tagger=tagger, channels=[1])

timetagger.setTriggerLevel(trigger_channel, 0.5)
timetagger.setInputDelay(trigger_channel, 0)
timetagger.setInputDelay(counter_channel, 0)

trigger_levels = np.arange(0.1,4,0.05)

x = trigger_levels.values
y = []
for level in trigger_levels:
    timetagger.setTriggerLevel(counter_channel, level)
    countrate.startFor(2e11)
    countrate.waitUntilFinished()
    y.append(countrate.getData()[0])

np.savetxt(os.path.join(save_path, "taggercalibration.csv"), y, delimiter=",")

# plotting the two using matplotlib
plt.plot(x, y, 'o-')
plt.title("calibration results of time tagger")
plt.xlabel("trigger levels")
plt.ylabel("detected counts")
plt.savefig(os.path.join(save_path, "Timetaggercalibration.png"))  # Save plot as PNG