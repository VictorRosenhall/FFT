import pyaudio
import numpy as np
import matplotlib.pyplot as plt

# Inställningar
FORMAT = pyaudio.paInt16  
CHANNELS = 1  
RATE = 44100  
CHUNK = 1024  

# Skapa PyAudio-instans och starta mikrofon
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, frames_per_buffer=CHUNK)

# Lista med notnamn
Notnamn = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Skapa Matplotlib-plot
plt.ion()
fig, ax = plt.subplots()
x = np.arange(0, 2 * CHUNK, 2)  
line, = ax.plot(x, np.random.rand(CHUNK))  
ax.set_ylim(-10000, 10000)

# Lägg till text för att visa frekvens ocg ton
freq_text = ax.text(0.7, 0.9, "", transform=ax.transAxes, fontsize=12, color="black")

# Funktion för att konvertera frekvens till notnamn
def freq_to_note(frequency):
    if frequency <= 0:
        return "Ingen ton"

    # Beräkna MIDI-nummer
    midi_number = round(69 + 12 * np.log2(frequency / 440.0))

    # Hitta notnamn och oktav
    note = Notnamn[midi_number % 12]  # Notnamn (ex: A, C#, G)
    oktav = (midi_number // 12) - 1  # Oktavnummer

    return f"{note}{oktav}"

# Realtidsloop
try:
    while True:
        # Läs in ljuddata
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)

        # FFT för att analysera frekvens
        fft_data = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(fft_data), 1/RATE)
        magnitudes = np.abs(fft_data)

        # Hitta den dominerande frekvensen
        idx = np.argmax(magnitudes[:CHUNK // 2])  
        dominant_freq = freqs[idx]  

        # Konvertera frekvens till notnamn
        note_name = freq_to_note(dominant_freq)

        # Uppdatera grafen
        line.set_ydata(audio_data)
        freq_text.set_text(f"{note_name} ({int(dominant_freq)} Hz)")
        
        plt.draw()
        plt.pause(0.01)

except KeyboardInterrupt:
    print("Programmet stängs av...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    plt.ioff()
    plt.show()
