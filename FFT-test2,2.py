import pyaudio
import numpy as np
import matplotlib.pyplot as plt

# Inställningar
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

# Användarinput
while True:
    usr_input = input("Hur högt ska programmet plotta frekvenser?: ")
    try:
        max_freq = int(usr_input)
        if max_freq > 0 and max_freq < 20001:
            break
        else:
            print("Fel, skriv ett positivt heltal mellan 1 och 20000")
    except ValueError:
        print("Fel, skriv ett positivt heltal mellan 1 och 20000")

while True:
    usr_input_2 = input("Ska lågpassfiltret vara på?")
    try:
        lowpass_choice = str(usr_input_2)
        if lowpass_choice == "ja" or "nej":
           break
        else:   
            print("Ogiltigt svar, välj ja eller nej")
    except ValueError:
        print("Ogiltigt svar, välj ja eller nej")

# Lista med notnamn
Notnamn = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Konvertera frekvens till notnamn
def freq_to_note(frequency):
    if frequency <= 0:
        return "Ingen ton"
    midi_number = round(69 + 12 * np.log2(frequency / 440.0))
    note = Notnamn[midi_number % 12]
    oktav = (midi_number // 12) - 1
    return f"Ton: {note}{oktav}, "

# Transponerad version av freq_to_note för alto saxofon
def freq_to_note_transp(frequency):
    if frequency <= 0:
        return ""
    midi_number = round(69 + 12 * np.log2(frequency / 440.0) + 9) # + 9 gör transponeringen
    note = Notnamn[midi_number % 12]
    oktav = (midi_number // 12) - 1
    return f"Transponerad ton: {note}{oktav}"

# low-pass
def lowpass(data, alpha=0.05):
    if usr_input_2 == "ja":
        filtered = data
        filtered = np.zeros_like(data)
        filtered[0] = data[0]
        for i in range(1, len(data)):
           filtered[i] = alpha * data[i] + (1 - alpha) * filtered[i - 1]
        return filtered
    else:
        return data

# Starta PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, frames_per_buffer=CHUNK)

# Förbereda plot
plt.ion()
fig, ax = plt.subplots()
x = np.fft.rfftfreq(CHUNK, d=1/RATE)
line, = ax.plot(x, np.zeros_like(x))
ax.set_xlim(0, max_freq)
ax.set_ylim(-100, 100)  # dB-skala
ax.set_xlabel("Frekvens (Hz)")
ax.set_ylabel("Amplitud (dBFS)")
ax.set_title("Frekvensspektrum (FFT)")

# Textfält för tonen
ton_text = ax.text(0.05, 0.9, "", transform=ax.transAxes, fontsize=12, color="black")

# Realtidsloop
try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)

        # Använd low-pass-filter
        filtered_audio = lowpass(audio_data, alpha=0.05)

        # FFT och dBFS
        fft_data = np.fft.rfft(filtered_audio)
        magnitude = np.abs(fft_data)
        magnitude_db = 20 * np.log10((magnitude / 32768) + 1e-6)  # dBFS

        # Hitta dominerande frekvens
        idx = np.argmax(magnitude)
        dominant_freq = x[idx]
        note_name = freq_to_note(dominant_freq)
        note_name_transponerat = freq_to_note_transp(dominant_freq)

        # Uppdatera graf
        line.set_ydata(magnitude_db)
        ton_text.set_text(f"{note_name} {note_name_transponerat} ({int(dominant_freq)} Hz)")
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
