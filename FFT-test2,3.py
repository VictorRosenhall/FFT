import pyaudio
import numpy as np
import matplotlib.pyplot as plt

# === Inställningar ===
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

# === Användarinput ===
while True:
    try:
        max_freq = int(input("Hur högt ska programmet plotta frekvenser (Hz)?: "))
        if 0 < max_freq <= 20000:
            break
        print("Fel, skriv ett heltal mellan 1 och 20000.")
    except ValueError:
        print("Fel, skriv ett heltal mellan 1 och 20000.")

while True:
    lowpass_choice = input("Ska lågpassfiltret vara på? (ja/nej): ").lower()
    if lowpass_choice in ["ja", "nej"]:
        break
    print("Ogiltigt svar, skriv 'ja' eller 'nej'.")

# === Notnamn och konvertering ===
NOTNAMN = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def freq_to_note(freq):
    if freq <= 0:
        return "Ingen ton"
    midi = round(69 + 12 * np.log2(freq / 440.0))
    note = NOTNAMN[midi % 12]
    octave = (midi // 12) - 1
    return f"Ton: {note}{octave}"

def freq_to_note_transposed(freq):
    if freq <= 0:
        return ""
    midi = round(69 + 12 * np.log2(freq / 440.0) + 9)  # Transponering för altsax
    note = NOTNAMN[midi % 12]
    octave = (midi // 12) - 1
    return f"Transponerad ton: {note}{octave}"

# === Lågpassfilter ===
def lowpass(data, alpha=0.05):
    if lowpass_choice != "ja":
        return data
    filtered = np.zeros_like(data)
    filtered[0] = data[0]
    for i in range(1, len(data)):
        filtered[i] = alpha * data[i] + (1 - alpha) * filtered[i - 1]
    return filtered

# === PyAudio ===
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# === Plotsetup ===
plt.ion()
fig, ax = plt.subplots()
x = np.fft.rfftfreq(CHUNK, d=1/RATE)
line, = ax.plot(x, np.zeros_like(x))
ax.set_xlim(0, max_freq)
ax.set_ylim(-100, 0)
ax.set_xlabel("Frekvens (Hz)")
ax.set_ylabel("Amplitud (dBFS)")
ax.set_title("Frekvensspektrum (FFT)")
ton_text = ax.text(0.05, 0.9, "", transform=ax.transAxes, fontsize=12, color="black")

# === Realtidsanalys ===
try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)

        # Förbehandling
        audio_filtered = lowpass(audio_data)
        windowed = audio_filtered * np.hanning(len(audio_filtered))
        fft_result = np.fft.rfft(windowed)
        magnitude = np.abs(fft_result)

        # Normalisering till dBFS, begränsa till max 0
        magnitude_db = 20 * np.log10(np.clip(magnitude / 32768, 1e-6, 1.0))

        # Hitta dominerande frekvens
        idx = np.argmax(magnitude)
        dominant_freq = x[idx]
        note = freq_to_note(dominant_freq)
        transposed_note = freq_to_note_transposed(dominant_freq)

        # Uppdatera plot
        line.set_ydata(magnitude_db)
        ton_text.set_text(f"{note} | {transposed_note} ({int(dominant_freq)} Hz)")
        plt.draw()
        plt.pause(0.01)

except KeyboardInterrupt:
    print("Stänger av programmet...")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    plt.ioff()
    plt.show()
