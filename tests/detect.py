import scipy.io.wavfile as wavutils
import numpy as np
import matplotlib.pyplot as plt
import note
import wavgen
import windows

THRESHOLD = 10
MISMATCHES = 10

WLEN = 1500
WOVERLAP = 1000

test_dir = 'resources/tests/'
test_filename = 'amazing_grace.wav'

srate, data = wavutils.read(test_dir + test_filename)

print(f'Testing for: {test_filename}')

slen = len(data)

i = 0
spect = list()

while i + WLEN <= slen:
    t = data[i:(i+WLEN)]
    f = np.fft.fft(t * windows.sinusoidal(WLEN), WLEN)

    spect.append(np.abs(f[0:round(WLEN/2)]))

    i += WLEN - WOVERLAP


freqs = np.fft.fftfreq(WLEN, 1.0/srate)
freqs = freqs[0:round(len(freqs)/2)]

# plt.imshow(np.transpose(np.fliplr(np.log(spect))), aspect='auto', extent=[0, slen/srate,
#    0, freqs[len(freqs) - 1]])

plt.plot(freqs, spect[1])

# plt.xlabel('Time (s)')
# plt.ylabel('Frequency (Hz)')

base_freqs = list()
for fbin in spect:
    base_freqs.append(np.argmax(fbin))

collapsed_freqs = list()
counts = list()

i = 0
while i < len(base_freqs):
    j = i + 1
    mis = 0
    while j < len(base_freqs) and mis < MISMATCHES:
        if base_freqs[i] == base_freqs[j]:
            mis = 0
        else:
            mis += 1
        j += 1
    
    last_pos = j
    if mis >= MISMATCHES:
        last_pos = j - mis - 1

    if last_pos - i > THRESHOLD:
        collapsed_freqs.append(base_freqs[i])
        counts.append(last_pos - i)
    i = last_pos + 1

print(np.array(base_freqs) * srate/WLEN)

notes = [note.closest_note(freqs[i]) for i in collapsed_freqs]

print(notes)

song = np.array([])
for i in range(len(notes)):
    freq = note.freq_by_note(notes[i][0], notes[i][1])
    song = np.append(song[0:-WOVERLAP], wavgen.sine_wave(freq, counts[i] * WLEN
        - (counts[i] - 1) * WOVERLAP, srate))

wavutils.write('result.wav', srate, song)

plt.show()