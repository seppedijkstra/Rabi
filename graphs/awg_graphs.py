import matplotlib.pyplot as plt
import csv
import numpy as np

offset = 72
time_offset = 0.748e-5

channel_1_x = []
channel_1_y = []
channel_2_x = []
channel_2_y = []

with open('./ALL0001/F0001CH1.CSV', 'r') as csvfile:
    plots = list(csv.reader(csvfile, delimiter = ','))
    #print(plots)

    for row in plots[18+offset:]:
        #print(row[3],row[4], row[3][:1] + row[3][2:])

        channel_1_x.append((float(row[3][:1] + row[3][2:])+time_offset) * 1e6)
        channel_1_y.append(float(row[4])+2.7)

with open('./ALL0001/F0001CH2.CSV', 'r') as csvfile:
    plots = list(csv.reader(csvfile, delimiter = ','))
    #print(plots)

    for row in plots[18+offset:]:
        #print(row[3],row[4], row[3][:1] + row[3][2:])

        channel_2_x.append((float(row[3][:1] + row[3][2:])+time_offset) * 1e6 )
        channel_2_y.append((float(row[4])-0.03) *1e3)



read_channel_1_x = []
read_channel_1_y = []
read_channel_2_x = []
read_channel_2_y = []

with open('./ALL0002/F0002CH1.CSV', 'r') as csvfile:
    plots = list(csv.reader(csvfile, delimiter = ','))
    #print(plots)

    for row in plots[18:-offset]:
        #print(row[3],row[4], row[3][:1] + row[3][2:])

        read_channel_1_x.append((float(row[3][:1] + row[3][2:])+time_offset) * 1e6)
        read_channel_1_y.append((float(row[4])+1.6))




fig, (ax1, ax3) = plt.subplots(2,1)

color = 'mediumseagreen'
ax1.plot(channel_1_x, channel_1_y, color=color, linewidth=0.8)
#ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()

color = 'goldenrod'
ax2.plot(channel_2_x, channel_2_y, color=color, linewidth=0.8)
#ax2.tick_params(axis='y', labelcolor=color)

color = 'steelblue'
ax3.plot(read_channel_1_x, read_channel_1_y, color=color, linewidth=0.8)
#ax3.tick_params(axis='y', labelcolor=color)

#ax4 = ax3.twinx()

#color = 'tab:blue'
#ax4.plot(read_channel_2_x, read_channel_2_y, color=color, linewidth=0.8, alpha=1)
#ax4.tick_params(axis='y', labelcolor=color)

# ax1.set_xticks(np.arange(-0.6e-5, 1.7e-5, 0.1e-5))
# ax3.set_xticks(np.arange(-0.6e-5, 1.7e-5, 0.1e-5))
ax1.tick_params(axis='x',labelsize=9)
ax2.tick_params(axis='x',labelsize=9)
ax3.tick_params(axis='x',labelsize=9)
ax1.set_xlabel('Time [μs]')
ax3.set_xlabel('Time [μs]')
ax1.set_ylabel('Channel 1 Marker [V]')
ax2.set_ylabel('Channel 1 Out [mV]')
ax3.set_ylabel('Channel 2 Marker [V]')
fig.tight_layout()
plt.show()
