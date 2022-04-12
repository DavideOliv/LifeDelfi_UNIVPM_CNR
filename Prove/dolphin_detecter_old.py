from subprocess import Popen, PIPE
import sys
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
from scipy import signal as sg
import numpy as np

FREQUENCY = 192000
SECONDS   = 1

N_BYTES = FREQUENCY * 2 * SECONDS

MIN_CLICK_FREQ = 5

MIN_SHAPE_DETECT = SECONDS * MIN_CLICK_FREQ


low_band = 35e3
high_band = 50e3
filter = sg.butter(4, [low_band, high_band], btype='bandpass', analog=False, output='sos', fs=FREQUENCY)
res = np.empty(FREQUENCY * SECONDS, dtype=np.int16)


def check(wav):
    wav = sg.sosfilt(filter, res)
    _, _, Sxx = sg.spectrogram(wav, FREQUENCY)
    
    onda_tot = np.sum(Sxx, axis=0)
    peaks, props = sg.find_peaks(onda_tot, height=np.mean(onda_tot)*3, distance=50)

    if peaks.shape[0] >= (MIN_SHAPE_DETECT):
        return True
    else:
        return False

def main():
    line = p.stdout.read(N_BYTES)
    while line:
        residx = 0
        for idx in range(0, len(line), 2):
            val = int.from_bytes(line[idx:idx+2], "little", signed=True)
			
            res[residx] = val
            residx += 1    
        
        dolphin = check(res)
        if dolphin:
            print("DELFINO SI")
        else:
            print("DELFINO NO")

        line = p.stdout.read(N_BYTES)
        
if __name__ == "__main__":
    p = Popen(f'arecord -f S16_LE -r {FREQUENCY} -c 1 -t raw', stdout=PIPE, shell=True)
    try:
        main()
    except KeyboardInterrupt:
        print("Keybord Interrupt")
    finally:
        p.terminate()
        print("arecord subprocess terminated")
    
