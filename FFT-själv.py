import pyaudio
import numpy as np
import matplotlib.pyplot as plt

# Inställningar
FORMAT = pyaudio.paInt16  # Format för ljuddata
CHANNELS = 1              # En kanal (mono)
RATE = 44100              # Samplingsfrekvens (Hz)
CHUNK = 1024              # Storlek på varje ljudblock

# Skapa PyAudio instans
p = pyaudio.PyAudio()

# Öppna ström från mikrofonen
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, frames_per_buffer=CHUNK)

#omvandlar från tid till frekvens
ljud = stream.read(CHUNK) #läser av ljudet från mikrofonen
ljud_np = np.frombuffer(ljud, dtype=np.int16) # omvandlar inputen till en numpy array
ljud_fft = np.fft.fft(ljud_np) # gör en fft-omvandling med 


x_axel = np.zeros(ljud_fft, dtype=int)
y = [1, 2, 3, 4]
print("innan funk")
def graf():
    plt.plot(x_axel, y)
    plt.label("Hertz")
    plt.ylabel("Amplitud")
    plt.show()

print("efter funk")
graf()

    