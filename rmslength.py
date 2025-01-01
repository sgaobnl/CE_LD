import pickle
import math
import matplotlib.pyplot as plt
import numpy as np 
from scipy.optimize import curve_fit

def model(x, a, b):
    return a * x + b


lengthfile = "./sbndwireends.txt"
lengthmap = {}

with open(lengthfile, 'r') as file: 
    for line in file: 
        # Split the line into individual elements and convert them to float 
        elements = list(map(float, line.split()))
        x0 = elements[5]
        y0 = elements[6]
        z0 = elements[7]
        x1 = elements[8]
        y1 = elements[9]
        z1 = elements[10]
        length = math.sqrt((x0-x1)**2+(y0-y1)**2+(z0-z1)**2)
        lengthmap[int(elements[0])] = length
print(len(lengthmap))
length = []
rms = []
length_eu = []
length_ev = []
length_ey = []
rms_eu = []
rms_ev = []
rms_ey = []
length_wu = []
length_wv = []
length_wy = []
rms_wu = []
rms_wv = []
rms_wy = []
with open('/scratch_local/SBND_Installation/data/commissioning/LD_result/LD_2024_12_23_09_26_24.ld', 'rb') as f:
    result = pickle.load(f)
print(result[-1])

for i in result:
    ch = int(i[10])
    if 'W' in i[0]:
        ch += 5632
    if 'V' in i[9]:
        ch += 1984
    if 'Y' in i[9]:
        ch += 1984*2
    this_length = lengthmap[ch-1]
    this_rms = min(max(i[16],0.1),100)
    length.append(this_length)
    rms.append(this_rms)

    if 'E' in i[0] and 'U' in i[9]:
        length_eu.append(this_length)
        rms_eu.append(this_rms)
    elif 'E' in i[0] and 'V' in i[9]:
        length_ev.append(this_length)
        rms_ev.append(this_rms)
    elif 'E' in i[0] and 'Y' in i[9]:
        length_ey.append(this_length)
        rms_ey.append(this_rms)
    elif 'W' in i[0] and 'U' in i[9]:
        length_wu.append(this_length)
        rms_wu.append(this_rms)
    elif 'W' in i[0] and 'V' in i[9]:
        length_wv.append(this_length)
        rms_wv.append(this_rms)
    elif 'W' in i[0] and 'Y' in i[9]:
        length_wy.append(this_length)
        rms_wy.append(this_rms)

    #rms.append(i[12])

print(length[:10])
print(rms[:10])
# Create the plot 
plt.scatter(length, rms, marker='.') 
# Add labels and title 
plt.xlabel('Wire length (cm)') 
plt.ylabel('RMS') 
plt.title('RMS vs wire length') 
plt.ylim(0.1, 100)
plt.yscale('log')
popt, pcov = curve_fit(model, length, np.log(rms))
a, b = popt 
print(f"Fitted parameters: a = {a}, b = {b}")
fitted_log_y = model(np.array(length), a, b) 
fitted_y = np.exp(fitted_log_y)
plt.plot(length, fitted_y, label=f'Fit: log(y) = {a:.2e}x + {b:.4f}', color='red')
plt.legend()
# Save the plot as a PNG file 
plt.savefig('plot.png')

plt.clf()
fig, axs = plt.subplots(1, 2, figsize=(12, 4))

axs[0].scatter(length_eu, rms_eu, marker='.', color='r', label='East U')
axs[0].scatter(length_ev, rms_ev, marker='.', color='b', label='East V')
axs[0].scatter(length_ey, rms_ey, marker='.', color='g', label='East Y')
axs[0].set_yscale('log')
axs[0].set_title('East')
axs[0].set_xlabel('Wire length (cm)')
axs[0].set_ylabel('RMS/bit')
axs[0].set_ylim(0.1,100)
axs[0].legend()

axs[1].scatter(length_wu, rms_wu, marker='.', color='r', label='West U')
axs[1].scatter(length_wv, rms_wv, marker='.', color='b', label='West V')
axs[1].scatter(length_wy, rms_wy, marker='.', color='g', label='West Y')
axs[1].set_yscale('log')
axs[1].set_title('West')
axs[1].set_xlabel('Wire length (cm)')
axs[1].set_ylabel('RMS/bit')
axs[1].set_ylim(0.1,100)
axs[1].legend()

plt.savefig('rms.png')

drms_u = []
drms_v = []
drms_y = []

for i in result:
    ch = int(i[10])
    if 'W' in i[0]:
        ch += 5632
    if 'V' in i[9]:
        ch += 1984
    if 'Y' in i[9]:
        ch += 1984*2
    this_length = lengthmap[ch-1]
    this_rms = i[16]
    logy = model(this_length,a,b)
    y = math.exp(logy)
    if 'U' in i[9]:
        drms_u.append(this_rms-y)
    elif 'V' in i[9]:
        drms_v.append(this_rms-y)
    else:
        drms_y.append(this_rms-y)

plt.clf()

# Create a figure and a set of subplots
fig, axs = plt.subplots(1, 3, figsize=(12, 4))

# First plot
axs[0].hist(drms_u, bins=np.linspace(-2.5, 2.5, 100 + 1), edgecolor='black', alpha=0.7, label='U')
axs[0].set_yscale('log')
axs[0].set_title('U')
axs[0].set_xlabel('delta rms')
axs[0].set_ylabel('channels')
axs[0].legend()

axs[1].hist(drms_v, bins=np.linspace(-2.5, 2.5, 100 + 1), edgecolor='black', alpha=0.7, label='V')
axs[1].set_yscale('log')
axs[1].set_title('V')
axs[1].set_xlabel('delta rms')
axs[1].set_ylabel('channels')
axs[1].legend()

axs[2].hist(drms_y, bins=np.linspace(-2.5, 2.5, 100 + 1), edgecolor='black', alpha=0.7, label='Y')
axs[2].set_yscale('log')
axs[2].set_title('Y')
axs[2].set_xlabel('delta rms')
axs[2].set_ylabel('channels')
axs[2].legend()


# Adjust layout
plt.tight_layout()

# Save the plot as a PNG file
plt.savefig('drms.png')

