import pyaudio
import numpy as np
import matplotlib.pyplot as plt

# Inställningar
FORMAT = pyaudio.paInt16  # 16-bitars ljudformat
CHANNELS = 1  # Mono
RATE = 44100  # Samplingsfrekvens (Hz)
CHUNK = 4096  # Antal samplingspunkter per frame

# Lista med notnamn
Notnamn = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def freq_to_note(frequency):
    if frequency <= 0:
        return "Ingen ton"
    midi_number = round(69 + 12 * np.log2(frequency / 440.0))
    print(midi_number)
    note = Notnamn[midi_number % 12]  # Hitta notnamn
    oktav = (midi_number // 12) - 1  # Beräkna oktavnummer
    return f"{note}{oktav}"

# Skapa PyAudio-instans och starta mikrofon
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, frames_per_buffer=CHUNK)

# Skapa Matplotlib-plot
plt.ion()
fig, ax = plt.subplots()
x = np.fft.rfftfreq(CHUNK, d=1/RATE)  # Skapa frekvensaxel för FFT
line, = ax.plot(x, np.zeros_like(x))  # Skapa en tom linje som uppdateras
ax.set_xlim(0, RATE / 2)  # Begränsa x-axeln till Nyquist-frekvensen (hälften av samplingsfrekvensen)
ax.set_ylim(0, 5000)  # Amplitudgränser (kan justeras beroende på mikrofonkänslighet)
ax.set_xlabel("Frekvens (Hz)")
ax.set_ylabel("Amplitud")
ax.set_title("Frekvensspektrum i realtid")

# Lägg till textfält för tonen
ton_text = ax.text(0.7, 0.9, "", transform=ax.transAxes, fontsize=12, color="black")

# Realtidsloop
try:
    while True:
        # Läs in ljuddata
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # Utför FFT
        fft_data = np.fft.rfft(audio_data)  # Använder rfft eftersom signalen är verklig (ej komplex)
        magnitude = np.abs(fft_data)  # Ta absolutbeloppet för att få amplituder
        
        # Hitta den dominerande frekvensen
        idx = np.argmax(magnitude)
        dominant_freq = x[idx]
        note_name = freq_to_note(dominant_freq)
        
        # Uppdatera grafen
        line.set_ydata(magnitude)
        ton_text.set_text(f"{note_name} ({int(dominant_freq)} Hz)")
        plt.draw()
        plt.pause(0.5)

except KeyboardInterrupt:
    print("Programmet stängs av...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    plt.ioff()
    plt.show()
