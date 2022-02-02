from scipy import signal as sg
import numpy as np
from scipy.io import wavfile
import sys

if len(sys.argv)>1:
    file = sys.argv[1]
else:
    print("Error : Wave file argument missing", file=sys.stderr)
    sys.exit(1)

sr,wav = wavfile.read(file)
N = wav.shape[0]
t = np.arange(N) / sr

low_band = 35e3
high_band = 50e3
filter = sg.butter(4, [low_band, high_band], btype='bandpass', analog=False, output='sos', fs=sr)
wav = sg.sosfilt(filter, wav)

f, t, Sxx = sg.spectrogram(wav, sr)

onda_tot = np.sum(Sxx, axis=0)
peaks, props = sg.find_peaks(onda_tot, height=np.mean(onda_tot)*3, distance=50)

click_freq_min = 5
if peaks.shape[0]>=(N/sr*click_freq_min):
    print("DELFINO SI")
else:
    print("DELFINO NO")