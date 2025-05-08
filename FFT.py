# Fil: FFT.py
# Programmerare: Victor Rosenhall TE23C
# Datum: 2025/05/08
# Beskrivning: Programmet använder datorns mikrofon för att göra en Fast Fourier Transform (FFT)
# och visualisera frekvensspektrumet i realtid. Det visar dessutom aktuell ton samt transponering för altsaxofon.

# Bibliotek
import pyaudio
import numpy as np
import matplotlib.pyplot as plt

# Inställningar
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

#Frågar användaren efter en maxfrekvens och validerar inmatningen.
#Programmet fortsätter att fråga tills användaren anger ett positivt heltal mellan 1 och 20000.
#Returnerar: Ett heltal (max_freq) som representerar den högsta frekvensen att plottas.
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

# Frågar användaren om lågpassfiltret ska vara aktiverat.
# Programmet accepterar endast 'ja' eller 'nej' och fortsätter att fråga vid ogiltig inmatning.
# Returnerar: En sträng ('ja' eller 'nej') som anger om lågpassfiltret ska användas.
while True:
    usr_input_2 = input("Ska lågpassfiltret vara på? ")
    try:
        lowpass_choice = str(usr_input_2)
        if lowpass_choice in ["ja", "nej"]:
           break
        else:   
            print("Ogiltigt svar, välj ja eller nej")
    except ValueError:
        print("Ogiltigt svar, välj ja eller nej")

# Array med notnamn
Notnamn = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Konverterar en frekvens till motsvarande tonnamn.
# Om frekvensen är 0 eller negativ returneras "Ingen ton".
# Returnerar: En sträng med tonens namn och oktav, t.ex. "Ton: A4".
#Parameter: frequency (float/int) – frekvensen i Hz som ska konverteras.
def freq_to_note(frequency):
    if frequency <= 0:
        return "Ingen ton"
    midi_number = round(69 + 12 * np.log2(frequency / 440.0))
    note = Notnamn[midi_number % 12]
    oktav = (midi_number // 12) - 1
    return f"Ton: {note}{oktav}, "

#Konverterar frekvens till en transponerad ton för altsaxofon.
#Transponeringen görs genom att höja tonen 9 halvtoner (en stor sext).
#Returnerar: En sträng med den transponerade tonens namn och oktav.
#Parameter: frequency (float/int) – frekvensen i Hz som ska konverteras.
def freq_to_note_transp(frequency):
    if frequency <= 0:
        return ""
    midi_number = round(69 + 12 * np.log2(frequency / 440.0) + 9) # + 9 gör transponeringen
    note = Notnamn[midi_number % 12]
    oktav = (midi_number // 12) - 1
    return f"Transponerad ton: {note}{oktav}"

#Tillämpas på ljudsignalen om lågpassfiltret är aktiverat av användaren.
#Filtrerar ut snabba förändringar i signalen för att göra analysen jämnare.
#Returnerar: Den filtrerade signalen om filtret är aktivt, annars originalsignalen.
#Parametrar:
    #data (np.ndarray) – array med ljuddata som ska filtreras.
    #alpha (float) – jämnhetsfaktor för filtret, standardvärde är 0.1.
def lowpass(data, alpha=0.1):
    if usr_input_2 == "ja":
        filtered = data
        filtered = np.zeros_like(data) # Initierar en array för det filtrerade ljudet
        filtered[0] = data[0] #Första värdet sätts till originalets första värde
        for i in range(1, len(data)): # Loopa genom resten av data
           filtered[i] = alpha * data[i] + (1 - alpha) * filtered[i - 1] # Blandar nuvarande värde med föregående filtrerade värde
        return filtered
    else:
        return data

# Startar PyAudio-strömmen (stream)
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, frames_per_buffer=CHUNK)

# Förbereder plot
plt.ion()
fig, ax = plt.subplots()
x = np.fft.rfftfreq(CHUNK, d=1/RATE) # Skapar en array med frekvenser för FFT baserat på chunkstorlek och samplingsfrekvens
line, = ax.plot(x, np.zeros_like(x))
ax.set_xlim(0, max_freq)
ax.set_ylim(-100, 100)  # dB-skala
ax.set_xlabel("Frekvens (Hz)")
ax.set_ylabel("Amplitud (dBFS)")
ax.set_title("Frekvensspektrum (FFT)")

# Textfält för tonen
ton_text = ax.text(0.05, 0.9, "", transform=ax.transAxes, fontsize=12, color="black")

#Loop som kör i realtid så länge programmet är aktivt.
#Läser in ljuddata, filtrerar signalen, beräknar FFT och uppdaterar grafen.
#Visar också aktuell ton och dess transponerade version i grafen.
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

        # Hitta den dominerande frekvensen
        idx = np.argmax(magnitude)
        dominant_freq = x[idx]
        note_name = freq_to_note(dominant_freq)
        note_name_transponerat = freq_to_note_transp(dominant_freq)

        # Uppdatera graf
        line.set_ydata(magnitude_db)
        ton_text.set_text(f"{note_name} {note_name_transponerat} ({int(dominant_freq)} Hz)")
        plt.draw()
        plt.pause(0.01)

#Avslutar programmet vid tangentbordsavbrott (Ctrl+C).
#Stänger ner ljudströmmen och PyAudio på ett säkert sätt.
#Stänger också plottfönstret och avslutar hela programmet.
except KeyboardInterrupt:
    print("Programmet stängs av...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    plt.ioff()
    plt.show()
