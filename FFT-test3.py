import pyaudio
import numpy as np
import matplotlib.pyplot as plt

# === Inställningar ===
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
THRESHOLD = 1000  # Tröskel för att ignorera svaga frekvenser

NOTNAMN = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# === Funktioner ===

def freq_to_note(frequency):
    if frequency <= 20 or frequency > 5000:
        return "Ingen ton"
    midi_number = round(69 + 12 * np.log2(frequency / 440.0))
    note = NOTNAMN[midi_number % 12]
    oktav = (midi_number // 12) - 1
    return f"{note}{oktav}"

def get_dominant_freq(audio_data, rate):
    window = np.hanning(len(audio_data))
    fft_data = np.fft.fft(audio_data * window)
    freqs = np.fft.fftfreq(len(fft_data), 1 / rate)
    magnitudes = np.abs(fft_data)

    # Fokusera bara på positiva frekvenser
    half_len = len(magnitudes) // 2
    magnitudes = magnitudes[:half_len]
    freqs = freqs[:half_len]

    # Ignorera svaga signaler
    magnitudes[magnitudes < THRESHOLD] = 0
    idx = np.argmax(magnitudes)
    return freqs[idx]

# === Initiera ljudström ===
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, frames_per_buffer=CHUNK)

# === Initiera plot ===
plt.ion()
fig, ax = plt.subplots()
x = np.arange(0, 2 * CHUNK, 2)
line, = ax.plot(x, np.random.rand(CHUNK))
ax.set_ylim(-10000, 10000)
ax.set_title("Realtids ljudanalys")
ax.set_xlabel("Tid")
ax.set_ylabel("Amplitud")

freq_text = ax.text(0.7, 0.9, "", transform=ax.transAxes, fontsize=12, color="black")

# === Huvudloop ===
try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)

        dominant_freq = get_dominant_freq(audio_data, RATE)
        note_name = freq_to_note(dominant_freq)
        amplitude = np.max(np.abs(audio_data))

        line.set_ydata(audio_data)
        freq_text.set_text(f"{note_name} ({int(dominant_freq)} Hz) Amp: {amplitude}")

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
