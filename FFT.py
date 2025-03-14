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

# Skapa en Matplotlib-figur för att visa ljudvåg
plt.ion()
fig, ax = plt.subplots()
x = np.arange(0, 2 * CHUNK, 2)
line, = ax.plot(x, np.random.rand(CHUNK))
ax.set_ylim(-30000, 30000)

# Huvudloop för realtidsinspelning och visualisering
try:
    while True:
        # Läs data från mikrofonen
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)

        # Uppdatera grafen med den nya ljudvågen
        line.set_ydata(audio_data)
        plt.draw()
        plt.pause(0.01)  # Vänta lite för att uppdatera grafen

except KeyboardInterrupt:
    print("Programmet stängs av...")
finally:
    # Stäng av strömmen och figur
    stream.stop_stream()
    stream.close()
    p.terminate()
    plt.ioff()
    plt.show()
